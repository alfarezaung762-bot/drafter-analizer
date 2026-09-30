"""Ekspor Tahap 4 — ALAT PENGEMBANG: pesan memastikan, PERSIS seperti dibaca AI.

Tahap 4 tempat temuan LAHIR: tiap dugaan tahap 3 diuji dengan naskah utuh.
Tiap panggilan ditulis lengkap — system, user, lalu tiap alat yang dipanggil
model berikut HASILNYA, karena hasil alat itu juga dibaca model sebelum
menjawab (bug 7). Urut seperti dikirim; jalurnya tertulis di judul tiap
panggilan.

Yang ditulis percakapan yang disimpan saat analisis berjalan, bukan susunan
ulang. Tidak memanggil AI.
"""

from __future__ import annotations

from typing import Optional

from app.bersama.llm import Blok
from app.telaah.ekspor.tahap3 import tulis_semua


def susun_ekspor_tahap4(rekaman: Optional[list[tuple[str, list[Blok]]]]) -> str:
    """Percakapan tahap 4 yang tersimpan, atau satu kalimat kenapa tidak ada."""
    if rekaman is None:
        return (
            "Pesan tahap 4 tidak tercatat — analisis dengan AI belum berjalan pada "
            "dokumen ini, atau backend sudah dimulai ulang sejak itu.\n"
        )
    if not rekaman:
        return "Tahap 4 tidak mengirim apa pun — tahap 3 tidak menghasilkan dugaan.\n"
    return tulis_semua(rekaman)
