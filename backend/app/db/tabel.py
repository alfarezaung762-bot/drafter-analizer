"""Dua tabel, dan cuma dua.

    PekerjaanDB        satu baris per analisis. Yang dibaca panel untuk
                       menampilkan kemajuan "Tahap 3 · 4/12" dan untuk tahu
                       analisisnya masih hidup.
    HasilPanggilanDB   satu baris per panggilan tahap 3 yang sudah dijawab —
                       jawaban mentahnya, dikunci sidik pesannya.

KENAPA PERLU BASIS DATA SAMA SEKALI. Analisis Fase 2 berjalan menit, bukan
detik. Selama menit itu tiga hal bisa terjadi dan ketiganya pernah terjadi:
backend di-restart, Word ditutup, panel dimuat ulang. Kalau jawabannya cuma
ada di memori proses, ketiganya menghanguskan pekerjaan yang sudah dibayar.

Sampai bug 7 (29 Sep 2026) yang disimpan PETA per satuan (`da_hasil_satuan`).
Petanya sudah tidak ada — model membaca naskah utuh — jadi yang disimpan kini
jawaban tiap panggilan tahap 3. Kuncinya sidik PESAN, bukan id satuan: jawaban
lama hanya dipakai ulang untuk pesan yang sama persis, jadi naskah yang sudah
diubah tidak pernah menerima jawaban atas naskah lamanya. Tabel lama dibiarkan
di basis data, tidak dipakai lagi.

Kolom `satuan_total`/`satuan_selesai` di tabel pekerjaan sengaja TIDAK diganti
nama walau isinya kini kemajuan per tahap: mengganti nama kolom menuntut
migrasi di basis data yang sudah berjalan.

TIDAK ADA TABEL TEMUAN. Temuan lahir di tahap 5 dan langsung dikirim ke
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
    satuan_total: int = 0  # kemajuan: total langkah tahap yang berjalan
    satuan_selesai: int = 0  # kemajuan: yang sudah selesai
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = ""
    dibuat: datetime = Field(default_factory=_sekarang)
    diperbarui: datetime = Field(default_factory=_sekarang)


class HasilPanggilanDB(SQLModel, table=True):
    """Jawaban satu panggilan tahap 3 yang sudah dibayar.

    Kunci uniknya (pekerjaan_id, kunci): pesan yang sama tidak pernah dibayar
    dua kali dalam satu pekerjaan.
    """

    __tablename__ = "da_hasil_panggilan"

    id: Optional[int] = Field(default=None, primary_key=True)
    pekerjaan_id: int = Field(index=True)
    kunci: str = Field(index=True, description="Sidik SHA-1 pesan system + user.")
    jawaban: str = ""
    dibuat: datetime = Field(default_factory=_sekarang)
