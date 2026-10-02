"""TAHAP 1 · LANGKAH 8 — bahan korpus: peraturan yang disebut naskah, dari korpus.

Disusun HANYA bila ada analisis terpilih ber-`Butuh: bahan korpus`. Kode
mengumpulkan semua peraturan yang disebut naskah — butir Mengingat, dan
rujukan pasal ke peraturan lain ("sebagaimana dimaksud dalam Pasal 25 ayat
(1) Undang-Undang Nomor …") — lalu mengambil statusnya dari korpus.
Hasilnya pembanding, bukan temuan; teks korpus hasil pemindaian, jadi
berpenanda "belum diverifikasi visual". Korpus dibaca saat analisis
berjalan, jadi selalu mutakhir.
"""

from __future__ import annotations

import re
from typing import Optional

from app.bersama.opensearch import PencariPeraturan, baca_kutipan
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import ParagrafInput

# "Undang-Undang Nomor 17 Tahun 2006", "Peraturan Pemerintah Nomor 1 Tahun 2020",
# "Peraturan Menteri Keuangan Nomor 246/PMK.06/2014"
_SEBUTAN = re.compile(
    r"(Undang-Undang|Peraturan Pemerintah(?: Pengganti Undang-Undang)?|Peraturan Presiden|"
    r"Keputusan Presiden|Peraturan Menteri Keuangan|Keputusan Menteri Keuangan)"
    r"\s+Nomor\s+[\w./-]+(?:\s+Tahun\s+\d{4})?",
    re.IGNORECASE,
)
_BATAS = 40


def kumpulkan_sebutan(pohon: PohonSatuan, paragraf: list[ParagrafInput]) -> list[str]:
    """Sebutan peraturan yang disebut naskah, urut kemunculan, tanpa kembar."""
    hasil: list[str] = []
    for s in pohon.semua(JenisSatuan.MENGINGAT):
        m = _SEBUTAN.search(s.teks)
        if m and m.group(0) not in hasil:
            hasil.append(m.group(0))
    for p in paragraf:
        for m in _SEBUTAN.finditer(p.utuh):
            if m.group(0) not in hasil:
                hasil.append(m.group(0))
    return hasil[:_BATAS]


def susun_bahan_korpus(
    pohon: PohonSatuan,
    paragraf: list[ParagrafInput],
    pencari: Optional[PencariPeraturan],
) -> str:
    """Blok BAHAN KORPUS, atau keterangan kenapa tidak ada."""
    if pencari is None:
        return "== BAHAN KORPUS ==\nKorpus tidak terhubung — bahan korpus tidak disusun."
    baris = [
        "== BAHAN KORPUS (dari korpus JDIH — pembanding, bukan temuan; teksnya hasil",
        "pemindaian, belum diverifikasi visual) ==",
    ]
    for sebutan in kumpulkan_sebutan(pohon, paragraf):
        kutipan = baca_kutipan(sebutan)
        if kutipan is None:
            baris.append(f"- {sebutan}: bentuknya tidak dikenali, tidak dicari")
            continue
        s = pencari.status_peraturan(kutipan)
        if s.berlaku is None:
            baris.append(f"- {sebutan}: status tidak diketahui ({s.alasan})")
        else:
            baris.append(
                f"- {sebutan}: {'Berlaku' if s.berlaku else 'Tidak Berlaku'} menurut korpus"
                + (f" — {s.judul}" if s.judul else "")
            )
    if len(baris) == 2:
        baris.append("(tidak ada peraturan lain yang disebut naskah)")
    return "\n".join(baris)
