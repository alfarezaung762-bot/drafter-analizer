"""Endpoint analisis lanjut — Fase 2 dan 3.

Dipisah dari `analisis.py` karena sifatnya memang berbeda, bukan karena
kerapian. Fase 1 selesai dalam hitungan detik dan boleh dijawab langsung;
Fase 2 berjalan menit, jadi permintaannya dijawab SEGERA dengan nomor
pekerjaan, dan hasilnya diambil panel secara berkala.

    POST /analisis/lanjut          mulai — balas nomor pekerjaan, tidak menunggu
    GET  /analisis/lanjut/{nomor}  kemajuan per tahap + temuan yang sudah ada
    POST /analisis/tahap1 … tahap5 ekspor alat pengembang

Kenapa tidak menunggu: panel yang menunggu satu permintaan selama tiga menit
akan dianggap macet oleh Word, dan penelaah tidak bisa membaca temuan Fase 1
sementara Fase 2 berjalan. Brief 8.7 mencatat persis kegagalan itu di Law
Analyzer.

Handler tetap setipis Fase 1: parse input → panggil fungsi → kembalikan JSON.
Seluruh logikanya di `telaah/alur.py`, yang bisa dites tanpa server.
"""

from __future__ import annotations

import threading
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.bersama.llm import KlienAzure, PerapalAzure
from app.bersama.opensearch import KorpusOpenSearch, PencariOpenSearch
from app.core.config import settings
from app.db import simpanan
from app.models.pekerjaan import StatusPekerjaan
from app.models.temuan import KerangkaTabel, ParagrafInput, Temuan
from app.telaah.alur import jalankan_lanjut
from app.telaah.ekspor.tahap1 import susun_ekspor_tahap1
from app.telaah.ekspor.tahap2 import susun_ekspor_tahap2
from app.telaah.ekspor.tahap3 import susun_ekspor_tahap3
from app.telaah.ekspor.tahap4 import susun_ekspor_tahap4
from app.telaah.ekspor.tahap5 import susun_ekspor_tahap5

router = APIRouter(prefix="/analisis", tags=["analisis lanjut"])


class AnalisisLanjutRequest(BaseModel):
    paragraf: list[ParagrafInput]
    tabel_raksasa: list[KerangkaTabel] = Field(
        default_factory=list,
        description=(
            "Kerangka tabel di atas 1.000 baris yang tidak dibaca panel per "
            "paragraf — PMK 108/2024 memuat 228 ribu baris tabel."
        ),
    )
    dokumen: str = Field(default="", description="Nama berkas, untuk catatan pekerjaan")
    aturan_aktif: Optional[list[str]] = Field(
        default=None,
        description="Kode aturan yang dicentang penelaah di panel Pengaturan. None berarti semua.",
    )
    mulai_nomor: int = Field(
        default=1,
        description=(
            "Nomor temuan pertama Fase 2 — melanjutkan nomor terakhir Fase 1. "
            "Nomor tidak pernah diurutkan ulang: (T3) sudah tertulis di komentar Word."
        ),
    )
    batas_temuan: int = Field(
        default=50,
        description="Batas ATAS jumlah temuan. Bukan target — model tidak diminta mencari sebanyak ini.",
    )
    ambang: Optional[float] = Field(default=None, description="Ambang skor. None memakai setelan backend.")
    fase3: bool = Field(
        default=False,
        description=(
            "Nyalakan korpus OpenSearch. F3-001 (pembanding) butuh OpenSearch dan "
            "deployment embedding; F3-002 (dasar hukum dicabut) cuma butuh "
            "OpenSearch dan tidak memanggil model sama sekali."
        ),
    )
    temuan_fase1: list[Temuan] = Field(
        default_factory=list,
        description=(
            "Temuan Fase 1 yang SUDAH terpasang di naskah. Dipakai dua kali: "
            "dilampirkan ke model supaya ia tidak mengulangnya, dan dipakai kode "
            "di tahap 5 untuk membuang calon yang rentangnya bertindihan. Model "
            "boleh menempelkan keberatan pada temuan ini, tetapi TIDAK PERNAH "
            "menghapusnya."
        ),
    )
    lanjutkan: Optional[int] = Field(
        default=None,
        description=(
            "Nomor pekerjaan lama yang jawabannya mau dipakai ulang. Panggilan "
            "tahap 3 yang pesannya sama persis tidak dibayar dua kali."
        ),
    )


class MulaiResponse(BaseModel):
    pekerjaan: int
    status: str
    pesan: str = ""


class KemajuanResponse(BaseModel):
    pekerjaan: int
    status: str
    tahap: str = Field(default="", description="Tahap yang sedang berjalan, mis. '3 cari dugaan'.")
    selesai: int = 0
    total: int = 0
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = ""
    temuan: list[Temuan] = Field(default_factory=list)
    keberatan: list[Temuan] = Field(
        default_factory=list,
        description=(
            "Temuan Fase 1 yang dapat catatan keberatan dari model. Panel "
            "memperbarui komentarnya; temuannya sendiri TIDAK dihapus."
        ),
    )


def _jalankan(nomor: int, req: AnalisisLanjutRequest) -> None:
    """Dijalankan di utas terpisah. Tidak boleh melempar ke luar.

    Apa pun yang gagal di sini berakhir jadi status "gagal" berikut
    alasannya — pekerjaan yang berhenti diam-diam tidak bisa dibedakan dari
    pekerjaan yang masih berjalan, dan penelaah akan menunggu selamanya.
    """
    try:
        klien = KlienAzure()
        if not klien.siap:
            simpanan.perbarui(
                nomor,
                status=StatusPekerjaan.GAGAL,
                pesan="Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env.",
            )
            return

        korpus = perapal = pencari = None
        if req.fase3:
            k, p = KorpusOpenSearch(), PerapalAzure()
            if k.siap and p.siap:
                korpus, perapal = k, p
            # F3-002 cuma butuh korpus, tidak butuh embedding maupun model.
            # Dipisah supaya ia tetap jalan walau deployment embedding mati.
            cari = PencariOpenSearch()
            if cari.siap:
                pencari = cari

        def lapor(tahap: str, selesai: int, total: int) -> None:
            simpanan.perbarui(nomor, tahap=tahap, selesai=selesai, total=total)

        def simpan(kunci: str, jawaban: str) -> None:
            simpanan.simpan_jawaban(nomor, kunci, jawaban)

        tersimpan = simpanan.ambil_jawaban(req.lanjutkan) if req.lanjutkan else {}

        hasil = jalankan_lanjut(
            req.paragraf,
            klien=klien,
            korpus=korpus,
            perapal=perapal,
            pencari=pencari,
            aturan_aktif=req.aturan_aktif,
            ambang=req.ambang if req.ambang is not None else settings.FASE2_AMBANG_SKOR,
            mulai_nomor=req.mulai_nomor,
            batas_temuan=req.batas_temuan,
            lapor=lapor,
            jawaban_tersimpan=tersimpan,
            simpan_jawaban=simpan,
            temuan_fase1=req.temuan_fase1,
            tabel_raksasa=req.tabel_raksasa,
            anggaran=settings.FASE2_ANGGARAN_TOKEN,
            pasal_per_fokus=settings.FASE2_PASAL_PER_FOKUS,
            berbarengan=settings.FASE2_PANGGILAN_BERBARENGAN,
        )

        # Temuan Fase 1 yang dapat keberatan model ikut dikembalikan, supaya
        # panel bisa memperbarui komentarnya. Yang tanpa keberatan tidak ikut:
        # panel sudah memegangnya, dan mengirim ulang cuma menggandakan.
        berkeberatan = [t for t in req.temuan_fase1 if t.catatan_ai]
        simpanan.tambah_temuan(nomor, hasil.temuan)
        # Dicatat SELALU, termasuk saat kosong: "tidak mengirim apa-apa" dan
        # "belum pernah jalan" adalah dua hal berbeda, dan ekspornya harus
        # bisa membedakannya.
        if hasil.pesan_tahap3 is not None:
            simpanan.simpan_pesan_tahap3(nomor, hasil.pesan_tahap3)
        if hasil.pesan_tahap4 is not None:
            simpanan.simpan_pesan_tahap4(nomor, hasil.pesan_tahap4)
        simpanan.simpan_ekspor_tahap5(nomor, susun_ekspor_tahap5(hasil))
        if berkeberatan:
            simpanan.tambah_keberatan(nomor, berkeberatan)
        simpanan.perbarui(
            nomor,
            status=StatusPekerjaan.SELESAI,
            tahap="5 verifikasi",
            panggilan=hasil.ongkos.panggilan,
            token_masuk=hasil.ongkos.token_masuk,
            token_keluar=hasil.ongkos.token_keluar,
            pesan=hasil.tidak_dijalankan,
        )
    except Exception as e:  # noqa: BLE001
        simpanan.perbarui(
            nomor, status=StatusPekerjaan.GAGAL, pesan=f"{type(e).__name__}: {e}"
        )


# Seluruhnya `def`, BUKAN `async def`, dan itu disengaja.
#
# Ada yang memanggil Postgres secara memblokir lewat `simpanan`, dan ekspor
# tahap 1–2 menyusun bahan naskah utuh. Di dalam `async def`, pekerjaan
# memblokir menahan seluruh event loop — satu panel yang bertanya kemajuan
# tiap dua detik ikut menahan permintaan Fase 1 penelaah lain. Ditulis `def`,
# FastAPI menjalankannya di threadpool dan event loop-nya bebas.
@router.post("/lanjut", response_model=MulaiResponse)
def mulai(request: AnalisisLanjutRequest) -> MulaiResponse:
    """Mulai analisis Fase 2/3. Membalas segera, tidak menunggu selesai."""
    nomor = simpanan.buat(request.dokumen)
    utas = threading.Thread(target=_jalankan, args=(nomor, request), daemon=True)
    utas.start()
    return MulaiResponse(pekerjaan=nomor, status=StatusPekerjaan.BERJALAN.value)


class NaskahRequest(BaseModel):
    """Permintaan ekspor tahap 1 dan 2 — disusun dari naskah saat ini, gratis."""

    paragraf: list[ParagrafInput]
    tabel_raksasa: list[KerangkaTabel] = Field(default_factory=list)
    dokumen: str = ""
    temuan_fase1: list[Temuan] = Field(default_factory=list)
    aturan_aktif: Optional[list[str]] = None


@router.post("/tahap1", response_class=PlainTextResponse)
def ekspor_tahap1(request: NaskahRequest) -> str:
    """ALAT PENGEMBANG — hasil parser: pohon satuan, definisi, lampiran. Gratis."""
    return susun_ekspor_tahap1(request.paragraf, request.tabel_raksasa)


@router.post("/tahap2", response_class=PlainTextResponse)
def ekspor_tahap2(request: NaskahRequest) -> str:
    """ALAT PENGEMBANG — perkiraan token, lalu bahan persis untuk AI. Gratis."""
    return susun_ekspor_tahap2(
        request.paragraf,
        request.tabel_raksasa,
        request.temuan_fase1,
        anggaran=settings.FASE2_ANGGARAN_TOKEN,
        aturan_aktif=request.aturan_aktif,
        pasal_per_fokus=settings.FASE2_PASAL_PER_FOKUS,
    )


class TersimpanRequest(BaseModel):
    dokumen: str = ""
    pekerjaan: Optional[int] = Field(
        default=None,
        description=(
            "Pekerjaan yang diekspor. None berarti pakai yang TERBARU untuk "
            "dokumen ini — supaya panel yang baru dimuat ulang, dan karena itu "
            "lupa nomornya, tetap bisa mengekspor."
        ),
    )


def _nomor(request: TersimpanRequest) -> Optional[int]:
    return request.pekerjaan or simpanan.pekerjaan_terakhir(request.dokumen)


@router.post("/tahap3", response_class=PlainTextResponse)
def ekspor_tahap3(request: TersimpanRequest) -> str:
    """ALAT PENGEMBANG — pesan tahap 3 (cari dugaan) persis seperti dikirim. Gratis."""
    nomor = _nomor(request)
    return susun_ekspor_tahap3(simpanan.ambil_pesan_tahap3(nomor) if nomor is not None else None)


@router.post("/tahap4", response_class=PlainTextResponse)
def ekspor_tahap4(request: TersimpanRequest) -> str:
    """ALAT PENGEMBANG — pesan tahap 4 berikut hasil alat, persis seperti dibaca AI."""
    nomor = _nomor(request)
    return susun_ekspor_tahap4(simpanan.ambil_pesan_tahap4(nomor) if nomor is not None else None)


@router.post("/tahap5", response_class=PlainTextResponse)
def ekspor_tahap5(request: TersimpanRequest) -> str:
    """ALAT PENGEMBANG — nasib tiap dugaan: lolos atau gugur, berikut alasannya."""
    nomor = _nomor(request)
    teks = simpanan.ambil_ekspor_tahap5(nomor) if nomor is not None else None
    return teks or (
        "Hasil tahap 5 tidak tercatat — analisis dengan AI belum berjalan pada "
        "dokumen ini, atau backend sudah dimulai ulang sejak itu.\n"
    )


@router.get("/lanjut/{nomor}", response_model=KemajuanResponse)
def kemajuan(nomor: int) -> KemajuanResponse:
    """Kemajuan dan temuan yang sudah ada. Boleh dipanggil berkali-kali."""
    p = simpanan.ambil(nomor)
    if p is None:
        raise HTTPException(status_code=404, detail=f"Pekerjaan {nomor} tidak ditemukan")
    return KemajuanResponse(
        pekerjaan=nomor,
        status=p.status.value,
        tahap=p.tahap,
        selesai=p.selesai,
        total=p.total,
        panggilan=p.panggilan,
        token_masuk=p.token_masuk,
        token_keluar=p.token_keluar,
        pesan=p.pesan,
        temuan=simpanan.ambil_temuan(nomor),
        keberatan=simpanan.ambil_keberatan(nomor),
    )
