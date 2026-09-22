"""Dua tabel, dan cuma dua.

    PekerjaanDB   satu baris per analisis. Yang dibaca panel untuk menampilkan
                  kemajuan "82/175" dan untuk tahu analisisnya masih hidup.
    HasilSatuanDB satu baris per satuan yang sudah selesai dibaca — INILAH
                  PETA. Bukan konsep tambahan: peta memang tinggal di tabel
                  ini, dan Langkah 3 membacanya dari sini.

KENAPA PERLU BASIS DATA SAMA SEKALI. Analisis Fase 2 berjalan menit, bukan
detik. Selama menit itu tiga hal bisa terjadi dan ketiganya pernah terjadi:
backend di-restart, Word ditutup, panel dimuat ulang. Kalau petanya cuma ada
di memori proses, ketiganya menghanguskan seluruh pekerjaan yang sudah
dibayar — dan pekerjaan Fase 2 dibayar per token.

Brief 8.7 mencatat Law Analyzer berhenti di 68/175 satuan. Dengan tabel ini,
berhenti di 68 berarti 68 satuan sudah tersimpan dan yang perlu diulang
tinggal sisanya.

TIDAK ADA TABEL TEMUAN. Temuan lahir di Langkah 5 dan langsung dikirim ke
panel; yang perlu bertahan justru bahan bakunya, karena itu yang mahal.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import Field, SQLModel


def _sekarang() -> datetime:
    return datetime.now(timezone.utc)


class PekerjaanDB(SQLModel, table=True):
    """Satu kali analisis panjang."""

    __tablename__ = "da_pekerjaan"

    id: Optional[int] = Field(default=None, primary_key=True)
    dokumen: str = Field(default="", index=True)
    status: str = Field(default="menunggu", index=True)
    satuan_total: int = 0
    satuan_selesai: int = 0
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = ""
    dibuat: datetime = Field(default_factory=_sekarang)
    diperbarui: datetime = Field(default_factory=_sekarang)


class HasilSatuanDB(SQLModel, table=True):
    """Satu baris peta yang sudah selesai dibaca.

    Kunci uniknya (pekerjaan_id, satuan_id): satuan yang sama tidak pernah
    dibayar dua kali dalam satu pekerjaan.
    """

    __tablename__ = "da_hasil_satuan"

    id: Optional[int] = Field(default=None, primary_key=True)
    pekerjaan_id: int = Field(index=True)
    satuan_id: str = Field(index=True)
    ringkasan: str = ""
    memuat_norma: bool = False
    # Disimpan sebagai teks dipisah koma, bukan tabel sendiri. Isinya cuma
    # dibaca utuh lalu dikirim ke model, tidak pernah dicari per istilah, jadi
    # tabel penghubung cuma menambah kerumitan tanpa menambah kemampuan.
    istilah_dipakai: str = ""
    merujuk: str = ""
    dugaan: str = ""
    dibuat: datetime = Field(default_factory=_sekarang)
