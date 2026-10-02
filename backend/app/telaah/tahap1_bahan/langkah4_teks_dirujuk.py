"""TAHAP 1 · LANGKAH 4 — teks yang dirujuk "sebagaimana dimaksud …".

CLAUDE.md butir 14: teks satuan yang dirujuk, sampai tingkat huruf/angka,
wajib ikut di SETIAP tahap yang menilai. Di Fase 4 agenlah yang menilai,
jadi tiap putaran per kelompok pasal menerima blok SATUAN YANG DIRUJUK untuk
pasal fokusnya — dicari KODE, dengan pernyataan terang-terangan untuk alamat
yang tidak ada. Pembacanya `tahap1_parser/rujukan.py`, dipakai apa adanya.
"""

from __future__ import annotations

from app.models.satuan import PohonSatuan
from app.telaah.tahap1_parser.rujukan import (  # noqa: F401
    blok_dirujuk,
    frasa_rujukan_saja,
    rujukan_satuan,
)


def blok_dirujuk_pasal(pohon: PohonSatuan, fokus: list[str]) -> list[str]:
    """Blok SATUAN YANG DIRUJUK untuk sekelompok pasal fokus. Kosong bila tidak ada."""
    satuan = [s for s in (pohon.cari(f) for f in fokus) if s is not None]
    return blok_dirujuk(satuan, pohon) if satuan else []
