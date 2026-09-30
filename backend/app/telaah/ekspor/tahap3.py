"""Ekspor Tahap 3 — ALAT PENGEMBANG: pesan cari dugaan, PERSIS seperti dikirim ke AI.

Isinya pesan system dan user tiap panggilan tahap 3 — per kelompok pasal,
lintas naskah, lampiran, dan tanya ulang — urut seperti dikirim, dipisah satu
baris garis. Tanpa kepala, ringkasan, atau penjelasan: ditetapkan penelaah
27 Sep 2026, supaya penyusunan bahan diperiksa dari apa yang benar-benar
dibaca model.

Yang ditulis percakapan yang DISIMPAN saat analisis berjalan, tidak disusun
ulang: naskah di Word sudah berubah sesudah ditandai, jadi menyusunnya ulang
dari naskah sekarang bisa berbeda dari yang dulu dikirim. Tidak memanggil AI.
"""

from __future__ import annotations

from typing import Optional

from app.bersama.llm import Blok


def tulis_percakapan(judul: str, blok: list[Blok]) -> list[str]:
    """Satu panggilan: tiap blok (system, user, alat, hasil alat) apa adanya."""
    baris: list[str] = []
    for siapa, isi in blok:
        baris += [f"===== {judul} · {siapa} =====", isi]
    return baris


def tulis_semua(rekaman: list[tuple[str, list[Blok]]]) -> str:
    baris: list[str] = []
    for judul, blok in rekaman:
        if baris:
            baris.append("")
        baris += tulis_percakapan(judul, blok)
    return "\n".join(baris) + "\n"


def susun_ekspor_tahap3(rekaman: Optional[list[tuple[str, list[Blok]]]]) -> str:
    """Pesan tahap 3 yang tersimpan, atau satu kalimat kenapa tidak ada."""
    if rekaman is None:
        return (
            "Pesan tahap 3 tidak tercatat — analisis dengan AI belum berjalan pada "
            "dokumen ini, atau backend sudah dimulai ulang sejak itu.\n"
        )
    if not rekaman:
        return (
            "Tahap 3 tidak mengirim apa pun — tidak ada pemeriksaan AI yang "
            "dinyalakan di panel Pengaturan.\n"
        )
    return tulis_semua(rekaman)
