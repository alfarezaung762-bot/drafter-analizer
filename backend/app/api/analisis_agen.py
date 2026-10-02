"""Endpoint Fase 4 — agen penuh dengan skills.

    GET  /analisis/daftar                 saklar alur + daftar pemeriksaan untuk panel,
                                          dibaca dari analisis.md dan analisisformat.md
    POST /analisis/agen                   mulai — balas nomor pekerjaan, tidak menunggu
    GET  /analisis/agen/{nomor}           kemajuan per putaran + temuan
    POST /analisis/agen/{nomor}/batal     tombol Batal: berhenti mengirim request baru
    POST /analisis/agen/ekspor1 … 3       ekspor alat pengembang: bahan, jejak agen, gerbang

Handler setipis mungkin: parse input → panggil `telaah/alur.jalankan_agen` →
kembalikan JSON. Seluruh logikanya bisa dites tanpa server.

Formulir analisis dibaca SAAT BACKEND MENYALA (`muat_katalog` di bawah):
formulir yang cacat membuat backend menolak menyala dan menyebut
analisisnya — tidak pernah dilewati diam-diam.
"""

from __future__ import annotations

import threading
from typing import Optional

from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from app.core.config import settings
from app.db import simpanan
from app.models.pekerjaan import StatusPekerjaan
from app.models.temuan import FormatHalaman, KerangkaTabel, ParagrafInput, Temuan
from app.telaah.tahap2_agen.langkah1_pilih_analisis import (
    JENIS_PANEL,
    Prasyarat,
    daftar_panel,
    muat_katalog,
)

router = APIRouter(prefix="/analisis", tags=["analisis agen (Fase 4)"])

# Dibaca sekali saat modul dimuat — FormulirCacat menghentikan backend menyala.
KATALOG = muat_katalog()


def _korpus_terkonfigurasi() -> bool:
    """Hanya setelan — tidak menyentuh jaringan."""
    return bool(settings.opensearch_url and (settings.OPENSEARCH_INDEX or settings.OPENSEARCH_EMBEDDING_INDEX))


class DaftarResponse(BaseModel):
    alur: str = Field(..., description="'lama' atau 'agen' — saklar FASE2_ALUR di .env.")
    jenis: str
    analisis: list[dict] = Field(default_factory=list)


@router.get("/daftar", response_model=DaftarResponse)
def daftar(jenis: str = "PMK") -> DaftarResponse:
    """Daftar pemeriksaan untuk panel Pengaturan, dari analisis.md dan analisisformat.md."""
    folder = JENIS_PANEL.get(jenis, jenis.lower())
    prasyarat = Prasyarat(
        korpus=_korpus_terkonfigurasi(),
        alasan_korpus="korpus tidak terhubung — OpenSearch belum diatur",
        bacaan_format=True,
    )
    return DaftarResponse(
        alur=settings.FASE2_ALUR.strip().lower() or "lama",
        jenis=jenis,
        analisis=daftar_panel(KATALOG, folder, prasyarat),
    )


class AnalisisAgenRequest(BaseModel):
    paragraf: list[ParagrafInput]
    halaman: list[FormatHalaman] = Field(default_factory=list)
    tabel_raksasa: list[KerangkaTabel] = Field(default_factory=list)
    dokumen: str = ""
    jenis_dokumen: str = "PMK"
    aturan_aktif: Optional[list[str]] = Field(
        default=None, description="Kode analisis yang dicentang penelaah. None = semua."
    )
    mulai_nomor: int = 1
    ambang: Optional[float] = None
    temuan_lama: list[Temuan] = Field(
        default_factory=list,
        description=(
            "Periksa ulang: temuan analisis sebelumnya beserta keputusan penelaah, "
            "dari daftar yang tersimpan di berkas. Dibaca agen; gerbang membuang "
            "calon yang bertindihan dengannya."
        ),
    )
    lanjutkan: Optional[int] = Field(
        default=None,
        description="Nomor pekerjaan lama yang jawabannya dipakai ulang — request yang sama tidak dibayar dua kali.",
    )


class MulaiResponse(BaseModel):
    pekerjaan: int
    status: str


class KemajuanAgenResponse(BaseModel):
    pekerjaan: int
    status: str
    tahap: str = ""
    putaran: list[dict] = Field(default_factory=list)
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = ""
    peringatan: list[str] = Field(default_factory=list)
    temuan: list[Temuan] = Field(default_factory=list)


def _jalankan(nomor: int, req: AnalisisAgenRequest) -> None:
    """Utas analisis. Tidak pernah melempar ke luar — kegagalan jadi status 'gagal'."""
    from app.bersama.llm import KlienAzure, PerapalAzure
    from app.bersama.opensearch import KorpusOpenSearch, PencariOpenSearch
    from app.telaah.alur import jalankan_agen
    from app.telaah.tahap2_agen.langkah3_jalankan_agen import Setelan

    try:
        klien = KlienAzure()
        if not klien.siap:
            simpanan.perbarui(
                nomor, status=StatusPekerjaan.GAGAL,
                pesan="Azure OpenAI belum terkonfigurasi. Periksa lewat GET /cek-env.",
            )
            return
        korpus = perapal = pencari = None
        dipilih = set(req.aturan_aktif or [a.kode for a in KATALOG.analisis])
        butuh_korpus = any("korpus" in a.butuh for a in KATALOG.analisis if a.kode in dipilih)
        if butuh_korpus:
            k, p = KorpusOpenSearch(), PerapalAzure()
            if k.siap and p.siap:
                korpus, perapal = k, p
            c = PencariOpenSearch()
            if c.siap:
                pencari = c

        def lapor(tahap: str, selesai: int, total: int) -> None:
            simpanan.perbarui(nomor, tahap=tahap, selesai=selesai, total=total)

        def lapor_putaran(kode: str, keadaan: dict) -> None:
            simpanan.catat_putaran(nomor, kode, keadaan)

        def simpan(kunci: str, jawaban: str) -> None:
            simpanan.simpan_jawaban(nomor, kunci, jawaban)

        tersimpan = simpanan.ambil_jawaban(req.lanjutkan) if req.lanjutkan else {}
        hasil = jalankan_agen(
            req.paragraf,
            jenis_panel=req.jenis_dokumen,
            klien=klien,
            katalog=KATALOG,
            kode_dipilih=req.aturan_aktif,
            korpus=korpus,
            perapal=perapal,
            pencari=pencari,
            halaman=req.halaman,
            tabel_raksasa=req.tabel_raksasa,
            ambang=req.ambang if req.ambang is not None else settings.FASE2_AMBANG_SKOR,
            mulai_nomor=req.mulai_nomor,
            temuan_lama=req.temuan_lama,
            tersimpan=tersimpan,
            simpan=simpan,
            batal=simpanan.tanda_batal(nomor),
            lapor=lapor,
            lapor_putaran=lapor_putaran,
            setelan=Setelan(
                macet_ulang=settings.FASE4_MACET_ULANG,
                macet_langkah=settings.FASE4_MACET_LANGKAH,
                tunggu_429=settings.FASE4_TUNGGU_429,
            ),
            anggaran=settings.FASE2_ANGGARAN_TOKEN,
            per_fokus=settings.FASE2_PASAL_PER_FOKUS,
            token_per_fokus=settings.FASE2_TOKEN_PER_FOKUS,
            berbarengan=settings.FASE2_PANGGILAN_BERBARENGAN,
        )
        simpanan.simpan_hasil_agen(nomor, hasil)
        simpanan.simpan_peringatan(nomor, hasil.peringatan)
        simpanan.tambah_temuan(nomor, hasil.temuan)
        simpanan.perbarui(
            nomor,
            status=StatusPekerjaan.SELESAI,
            tahap="dibatalkan" if hasil.dibatalkan else "selesai",
            panggilan=hasil.ongkos.panggilan,
            token_masuk=hasil.ongkos.token_masuk,
            token_keluar=hasil.ongkos.token_keluar,
            pesan=hasil.tidak_dijalankan,
        )
    except Exception as e:  # noqa: BLE001
        simpanan.perbarui(nomor, status=StatusPekerjaan.GAGAL, pesan=f"{type(e).__name__}: {e}")


@router.post("/agen", response_model=MulaiResponse)
def mulai(request: AnalisisAgenRequest) -> MulaiResponse:
    """Mulai analisis Fase 4. Membalas segera, tidak menunggu selesai."""
    nomor = simpanan.buat(request.dokumen)
    simpanan.tanda_batal(nomor)
    threading.Thread(target=_jalankan, args=(nomor, request), daemon=True).start()
    return MulaiResponse(pekerjaan=nomor, status=StatusPekerjaan.BERJALAN.value)


@router.get("/agen/{nomor}", response_model=KemajuanAgenResponse)
def kemajuan(nomor: int) -> KemajuanAgenResponse:
    p = simpanan.ambil(nomor)
    if p is None:
        raise HTTPException(status_code=404, detail=f"Pekerjaan {nomor} tidak ditemukan")
    return KemajuanAgenResponse(
        pekerjaan=nomor,
        status=p.status.value,
        tahap=p.tahap,
        putaran=simpanan.ambil_putaran(nomor),
        panggilan=p.panggilan,
        token_masuk=p.token_masuk,
        token_keluar=p.token_keluar,
        pesan=p.pesan,
        peringatan=simpanan.ambil_peringatan(nomor),
        temuan=simpanan.ambil_temuan(nomor),
    )


@router.post("/agen/{nomor}/batal")
def batal(nomor: int) -> dict:
    """Tombol Batal. Request yang sedang berjalan selesai dulu; tidak ada request baru."""
    if not simpanan.batalkan(nomor):
        raise HTTPException(status_code=404, detail=f"Pekerjaan {nomor} tidak sedang berjalan di backend ini")
    return {"pekerjaan": nomor, "batal": True}


class EksporRequest(BaseModel):
    dokumen: str = ""
    pekerjaan: Optional[int] = None
    paragraf: list[ParagrafInput] = Field(default_factory=list)
    halaman: list[FormatHalaman] = Field(default_factory=list)
    tabel_raksasa: list[KerangkaTabel] = Field(default_factory=list)


def _hasil(req: EksporRequest):
    nomor = req.pekerjaan or simpanan.pekerjaan_terakhir(req.dokumen)
    return simpanan.ambil_hasil_agen(nomor) if nomor is not None else None


@router.post("/agen/ekspor1", response_class=PlainTextResponse)
def ekspor1(request: EksporRequest) -> str:
    """ALAT PENGEMBANG — label dan bahan persis yang dibaca agen."""
    from app.telaah.ekspor.tahap1_bahan import susun_ekspor_tahap1_bahan

    hasil = _hasil(request)
    if hasil is None:
        return susun_ekspor_tahap1_bahan(
            None, request.paragraf, request.tabel_raksasa, request.halaman, settings.FASE2_ANGGARAN_TOKEN
        )
    return susun_ekspor_tahap1_bahan(hasil)


@router.post("/agen/ekspor2", response_class=PlainTextResponse)
def ekspor2(request: EksporRequest) -> str:
    """ALAT PENGEMBANG — jejak agen per putaran: tiap request, alat, token."""
    from app.telaah.ekspor.tahap2_jejak_agen import susun_ekspor_tahap2_jejak

    return susun_ekspor_tahap2_jejak(_hasil(request))


@router.post("/agen/ekspor3", response_class=PlainTextResponse)
def ekspor3(request: EksporRequest) -> str:
    """ALAT PENGEMBANG — lolos/gugur di gerbang, dan kunci jawaban peralihan."""
    from app.telaah.ekspor.tahap3_verifikasi import susun_ekspor_tahap3_verifikasi

    return susun_ekspor_tahap3_verifikasi(_hasil(request))
