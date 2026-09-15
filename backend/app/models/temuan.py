"""Skema data Temuan — kontrak final antara backend dan frontend.

Lihat docs/kontrak-data.md untuk penjelasan lengkap tiap field.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class TingkatKeparahan(str, Enum):
    TINGGI = "tinggi"
    SEDANG = "sedang"
    RENDAH = "rendah"


class StatusTemuan(str, Enum):
    BELUM_DITINJAU = "belum_ditinjau"
    DITERIMA = "diterima"
    DITOLAK = "ditolak"


# ---------------------------------------------------------------------------
# Bagian-bagian Temuan
# ---------------------------------------------------------------------------

class LokasiTemuan(BaseModel):
    """Posisi temuan di dalam dokumen."""

    paragraf_index: int = Field(
        ..., description="Indeks paragraf dalam daftar yang dikirim"
    )
    offset_mulai: int = Field(
        ..., description="Posisi karakter awal di dalam paragraf"
    )
    panjang: int = Field(
        ..., description="Panjang karakter yang disorot"
    )
    teks_asli: str = Field(
        ..., description="Teks asli yang bermasalah"
    )


class RujukanTemuan(BaseModel):
    """Rujukan ke butir KMK 527."""

    sumber: str = Field(
        ..., description="Nama peraturan sumber"
    )
    butir: str = Field(
        ..., description="Nomor butir spesifik"
    )
    kutipan: str = Field(
        ..., description="Kutipan isi butir"
    )
    pdf_url: str = Field(
        ..., description="URL PDF di JDIH"
    )


# ---------------------------------------------------------------------------
# Temuan — objek utama
# ---------------------------------------------------------------------------

class Temuan(BaseModel):
    """Satu temuan hasil pemeriksaan."""

    id: str = Field(
        ..., description="Identifier unik temuan dalam satu sesi analisis"
    )
    aturan_id: str = Field(
        ..., description="Kunci ke tabel rujukan (F1-001, dst.)"
    )
    fase: int = Field(
        default=1, description="Fase pemeriksaan, selalu 1 untuk Fase 1"
    )
    tingkat_keparahan: TingkatKeparahan
    lokasi: LokasiTemuan
    catatan: str = Field(
        ..., description="Penjelasan temuan untuk penelaah"
    )
    usulan_rumusan: Optional[str] = Field(
        default=None, description="Saran perbaikan (opsional)"
    )
    rujukan: RujukanTemuan
    status: StatusTemuan = Field(
        default=StatusTemuan.BELUM_DITINJAU
    )


# ---------------------------------------------------------------------------
# Request / Response untuk endpoint analisis
# ---------------------------------------------------------------------------

class ParagrafInput(BaseModel):
    """Satu paragraf yang dikirim dari frontend."""

    index: int = Field(..., description="Indeks paragraf di dokumen")
    teks: str = Field(..., description="Isi teks paragraf")


class AnalisisRequest(BaseModel):
    """Request body untuk POST /analisis/jalankan."""

    paragraf: list[ParagrafInput] = Field(
        ..., description="Daftar paragraf dari dokumen"
    )


class AnalisisResponse(BaseModel):
    """Response body dari POST /analisis/jalankan."""

    temuan: list[Temuan] = Field(
        default_factory=list, description="Daftar temuan hasil pemeriksaan"
    )
    jumlah_paragraf: int = Field(
        ..., description="Jumlah paragraf yang diperiksa"
    )
