"""Endpoint analisis lanjut — Fase 2 dan 3.

Dipisah dari `analisis.py` karena sifatnya memang berbeda, bukan karena
kerapian. Fase 1 selesai dalam hitungan detik dan boleh dijawab langsung;
Fase 2 berjalan menit, jadi permintaannya dijawab SEGERA dengan nomor
pekerjaan, dan hasilnya diambil panel secara berkala.

    POST /analisis/lanjut          mulai — balas nomor pekerjaan, tidak menunggu
    GET  /analisis/lanjut/{nomor}  kemajuan + temuan yang sudah ada

Kenapa tidak menunggu: panel yang menunggu satu permintaan selama tiga menit
akan dianggap macet oleh Word, dan penelaah tidak bisa membaca temuan Fase 1
sementara Fase 2 berjalan. Brief 8.7 mencatat persis kegagalan itu di Law
Analyzer.

Handler tetap setipis Fase 1: parse input → panggil fungsi → kembalikan JSON.
Seluruh logikanya di `fase2/alur.py`, yang bisa dites tanpa server.
"""

from __future__ import annotations

import threading
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.bersama.llm import KlienAzure, PerapalAzure
from app.bersama.opensearch import KorpusOpenSearch
from app.core.config import settings
from app.db import simpanan
from app.fase2.alur import jalankan_lanjut
from app.models.pekerjaan import BarisPeta, StatusPekerjaan
from app.models.temuan import ParagrafInput, Temuan

router = APIRouter(prefix="/analisis", tags=["analisis lanjut"])


class AnalisisLanjutRequest(BaseModel):
    paragraf: list[ParagrafInput]
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
        description="Cari pembanding di korpus peraturan. Butuh OpenSearch dan deployment embedding.",
    )
    lanjutkan: Optional[int] = Field(
        default=None,
        description=(
            "Nomor pekerjaan lama yang petanya mau dipakai ulang. Satuan yang "
            "sudah pernah dibaca tidak dibayar dua kali."
        ),
    )


class MulaiResponse(BaseModel):
    pekerjaan: int
    status: str
    pesan: str = ""


class KemajuanResponse(BaseModel):
    pekerjaan: int
    status: str
    satuan_total: int = 0
    satuan_selesai: int = 0
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = ""
    temuan: list[Temuan] = Field(default_factory=list)


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

        korpus = perapal = None
        if req.fase3:
            k, p = KorpusOpenSearch(), PerapalAzure()
            if k.siap and p.siap:
                korpus, perapal = k, p

        def lapor(selesai: int, total: int, baru: list[BarisPeta]) -> None:
            simpanan.simpan_peta(nomor, baru)
            simpanan.perbarui(nomor, satuan_total=total, satuan_selesai=selesai)

        lama = simpanan.ambil_peta(req.lanjutkan) if req.lanjutkan else None

        hasil = jalankan_lanjut(
            req.paragraf,
            klien=klien,
            korpus=korpus,
            perapal=perapal,
            aturan_aktif=req.aturan_aktif,
            ambang=req.ambang if req.ambang is not None else settings.FASE2_AMBANG_SKOR,
            per_panggilan=settings.FASE2_SATUAN_PER_PANGGILAN,
            mulai_nomor=req.mulai_nomor,
            batas_temuan=req.batas_temuan,
            lapor=lapor,
            peta_tersimpan=lama,
        )

        simpanan.tambah_temuan(nomor, hasil.temuan)
        simpanan.perbarui(
            nomor,
            status=StatusPekerjaan.SELESAI,
            satuan_selesai=len(hasil.peta),
            panggilan=hasil.ongkos.panggilan,
            token_masuk=hasil.ongkos.token_masuk,
            token_keluar=hasil.ongkos.token_keluar,
            pesan=hasil.tidak_dijalankan,
        )
    except Exception as e:  # noqa: BLE001
        simpanan.perbarui(
            nomor, status=StatusPekerjaan.GAGAL, pesan=f"{type(e).__name__}: {e}"
        )


@router.post("/lanjut", response_model=MulaiResponse)
async def mulai(request: AnalisisLanjutRequest) -> MulaiResponse:
    """Mulai analisis Fase 2/3. Membalas segera, tidak menunggu selesai."""
    nomor = simpanan.buat(request.dokumen, satuan_total=0)
    utas = threading.Thread(target=_jalankan, args=(nomor, request), daemon=True)
    utas.start()
    return MulaiResponse(pekerjaan=nomor, status=StatusPekerjaan.BERJALAN.value)


@router.get("/lanjut/{nomor}", response_model=KemajuanResponse)
async def kemajuan(nomor: int) -> KemajuanResponse:
    """Kemajuan dan temuan yang sudah ada. Boleh dipanggil berkali-kali."""
    p = simpanan.ambil(nomor)
    if p is None:
        raise HTTPException(status_code=404, detail=f"Pekerjaan {nomor} tidak ditemukan")
    return KemajuanResponse(
        pekerjaan=nomor,
        status=p.status.value,
        satuan_total=p.satuan_total,
        satuan_selesai=p.satuan_selesai,
        panggilan=p.panggilan,
        token_masuk=p.token_masuk,
        token_keluar=p.token_keluar,
        pesan=p.pesan,
        temuan=simpanan.ambil_temuan(nomor),
    )
