"""TAHAP 1 · LANGKAH 1 — AI memberi label tiap paragraf pembuka satuan.

SATU panggilan, sebelum putaran agen. Masuknya seluruh paragraf bernomor ¶
TANPA label, ditambah `label/SKILL.md` jenis naskahnya; keluarnya daftar
{¶, label} dan jenis naskah menurut AI. Label belum dipercaya di sini —
langkah 2 yang membuktikannya dengan kode.

Kenapa AI, padahal parser PMK biasa sudah ada: menambah jenis naskah — KMK,
PMK perubahan — cukup menambah skill label, tanpa parser baru. Diuji 2 Okt
2026: PMK 45 353/353 label sama dengan parser; PMK 4/2025 (perubahan) 330/330
lolos bukti kode.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.bersama.llm import Blok, Klien, Ongkos, baca_json
from app.models.temuan import ParagrafInput

PERAN_LABEL = """Kamu membaca SUSUNAN naskah peraturan perundang-undangan Indonesia —
pasal, ayat, huruf, angka — untuk memberi label letak. Kamu tidak menilai isinya."""

TUGAS_LABEL = """Tentukan dulu jenisnya — PMK biasa atau PMK perubahan — lalu beri label
setiap paragraf pembuka satuan, menurut ATURAN LABEL di atas.

Jawab HANYA dengan JSON:
{"jenis": "pmk biasa" | "pmk perubahan",
 "label": [{"p": <angka ¶>, "label": "<label>"}]}"""


@dataclass
class UsulanLabel:
    """Jawaban AI, belum dibuktikan."""

    jenis: str = ""
    label: dict[int, str] = field(default_factory=dict)
    terbaca: bool = False
    percakapan: list[Blok] = field(default_factory=list)
    jawaban: str = ""


def _rapat(t: str) -> str:
    return " ".join(t.split())


def naskah_bernomor(paragraf: list[ParagrafInput]) -> str:
    """Paragraf bernomor ¶ tanpa label — bentuk yang sama dengan uji 2 Okt 2026."""
    baris = ["== NASKAH, satu baris per paragraf: ¶nomor, lalu teks. [tabel] = isi sel tabel. =="]
    for p in paragraf:
        t = _rapat(p.utuh)
        if t:
            baris.append(f"¶{p.index}{' [tabel]' if p.tabel >= 0 else ''} {t}")
    return "\n".join(baris)


def pesan_label(paragraf: list[ParagrafInput], skill_label: str) -> str:
    return "ATURAN LABEL\n\n" + skill_label.strip() + "\n\n---\n\n" + naskah_bernomor(paragraf) + "\n\n---\n\n" + TUGAS_LABEL


def baca_label(teks: str) -> tuple[str, dict[int, str], bool]:
    """(jenis, {¶: label}, terbaca) dari jawaban AI. Entri rusak dilewati."""
    isi = baca_json(teks)
    if not isi:
        return "", {}, False
    keluar: dict[int, str] = {}
    for e in isi.get("label") or []:
        if not isinstance(e, dict):
            continue
        try:
            p = int(str(e.get("p")).strip().lstrip("¶"))
        except (TypeError, ValueError):
            continue
        lab = re.sub(r"\s+", "", str(e.get("label") or "")).strip().lower()
        if lab:
            keluar[p] = lab
    jenis = str(isi.get("jenis") or "").strip().lower()
    return jenis, keluar, True


def minta_label(
    paragraf: list[ParagrafInput],
    skill_label: str,
    klien: Klien,
    ongkos: Ongkos,
    tersimpan: Optional[dict[str, str]] = None,
    simpan=None,
) -> UsulanLabel:
    """Satu panggilan AI. Jawaban tersimpan untuk pesan yang SAMA dipakai ulang."""
    import hashlib

    pesan = pesan_label(paragraf, skill_label)
    kunci = "label:" + hashlib.sha1((PERAN_LABEL + "\n" + pesan).encode("utf-8")).hexdigest()
    if tersimpan and kunci in tersimpan:
        teks = tersimpan[kunci]
    else:
        jawab = klien.tanya(PERAN_LABEL, pesan)
        ongkos.catat(jawab)
        teks = jawab.teks
    jenis, label, terbaca = baca_label(teks)
    if terbaca and simpan is not None:
        simpan(kunci, teks)
    return UsulanLabel(
        jenis=jenis,
        label=label,
        terbaca=terbaca,
        percakapan=[("system", PERAN_LABEL), ("user", pesan), ("jawaban AI", teks)],
        jawaban=teks,
    )
