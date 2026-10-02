"""Ekspor Tahap 1 (Fase 4) — ALAT PENGEMBANG: label dan bahan PERSIS yang dibaca agen.

Isinya: label AI berikut hasil buktinya dan bedanya dengan parser, lalu
naskah berlabel, naskah berformat, dan bahan korpus persis seperti di depan
pesan tiap putaran. Sesudah analisis berjalan, yang ditulis bahan yang
BENAR-BENAR dikirim; sebelum itu, susunan dari naskah saat ini dengan label
parser — gratis, tanpa AI.
"""

from __future__ import annotations

from typing import Optional

from app.models.temuan import FormatHalaman, KerangkaTabel, ParagrafInput
from app.telaah.tahap1_bahan.langkah2_bukti_label import peta_letak
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import susun_naskah_berlabel
from app.telaah.tahap1_bahan.langkah7_naskah_berformat import susun_naskah_berformat
from app.telaah.tahap2_persiapan.bahan import angka


def _label(hasil) -> list[str]:
    baris = ["===== TAHAP 1 · LABEL SATUAN ====="]
    if hasil.label is None:
        baris.append("Label AI tidak diminta — peta letak dari parser cadangan.")
    else:
        baris.append(
            f"Jenis menurut AI: {hasil.label.jenis or '(tidak terbaca)'} · "
            f"label diusulkan: {len(hasil.label.label)} · jawaban terbaca: {'ya' if hasil.label.terbaca else 'tidak'}"
        )
    peta = hasil.peta
    if peta is None:
        return baris
    baris.append(f"Peta letak dipakai: {peta.sumber} · {len(peta.pohon.satuan)} satuan")
    baris += [f"  {c}" for c in peta.catatan]
    if peta.bukti is not None:
        for p, lab, alasan in peta.bukti.gagal:
            baris.append(f"  GAGAL BUKTI ¶{p} {lab!r}: {alasan}")
        for p in peta.bukti.tanpa_label:
            baris.append(f"  TANPA LABEL ¶{p} (paragraf berpenanda di batang tubuh)")
    if peta.beda_parser:
        baris.append(f"Beda dengan label parser ({len(peta.beda_parser)}) — kunci jawaban peralihan:")
        baris += [f"  ¶{p}: AI {a!r} · parser {b!r}" for p, a, b in peta.beda_parser]
    else:
        baris.append("Label AI sama persis dengan label parser.")
    return baris


def susun_ekspor_tahap1_bahan(
    hasil=None,
    paragraf: Optional[list[ParagrafInput]] = None,
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    halaman: Optional[list[FormatHalaman]] = None,
    anggaran: int = 100_000,
) -> str:
    """Dari hasil analisis yang berjalan, atau — bila None — dari naskah saat ini (gratis)."""
    if hasil is None:
        if not paragraf:
            return "Tidak ada paragraf untuk disusun.\n"
        peta = peta_letak(None, paragraf)
        if peta.pohon.gagal:
            return f"Tidak ada yang dikirim ke agen — peta letak tidak terbaca: {peta.pohon.gagal}\n"
        berlabel = susun_naskah_berlabel(paragraf, peta.pohon, tabel_raksasa, anggaran)
        berformat = susun_naskah_berformat(paragraf, peta.pohon, halaman)
        baris = [
            "===== TAHAP 1 · LABEL SATUAN =====",
            "Belum ada analisis yang berjalan — label dari parser cadangan (tanpa AI).",
            f"{len(peta.pohon.satuan)} satuan.",
        ]
        teks_korpus = ""
    else:
        if not hasil.berjalan and hasil.berlabel is None:
            return f"Analisis tidak sampai tahap bahan: {hasil.tidak_dijalankan}\n"
        baris = _label(hasil)
        berlabel, berformat, teks_korpus = hasil.berlabel, hasil.berformat, hasil.bahan_korpus
    baris += [
        "",
        f"===== TAHAP 1 · NASKAH BERLABEL — persis, di depan pesan tiap putaran isi "
        f"(±{angka(berlabel.token)} token) =====",
    ]
    if berlabel.kerangka:
        baris += [f"Kerangka: {k}" for k in berlabel.kerangka]
    baris.append(berlabel.teks)
    if berformat is not None:
        baris += [
            "",
            f"===== TAHAP 1 · NASKAH BERFORMAT — persis, putaran format (±{angka(berformat.token)} token) =====",
            berformat.teks,
        ]
    if teks_korpus:
        baris += ["", "===== TAHAP 1 · BAHAN KORPUS =====", teks_korpus]
    return "\n".join(baris) + "\n"
