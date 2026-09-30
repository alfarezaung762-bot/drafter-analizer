"""Ekspor Tahap 1 — ALAT PENGEMBANG: hasil parser, persis seperti dibaca kode.

Empat bagian: pohon satuan (id, jenis, rentang paragraf, teks berlabel),
definisi Pasal 1, paragraf yang teksnya tidak masuk satuan mana pun, dan
lampiran berikut jenis fisik tiap bloknya.

Paragraf yang tidak masuk satuan TETAP dikirim ke AI apa adanya (tahap 2
menyusun bahan dari seluruh paragraf) — daftarnya di sini supaya kegagalan
parser kelihatan, bukan supaya dibuang. Bug 11: pada PMK 119 daftar ini dulu
memuat 79 paragraf, termasuk seluruh definisi Pasal 1.

Tidak memanggil AI, tidak berbiaya.
"""

from __future__ import annotations

import re
from typing import Optional

from app.models.satuan import JenisSatuan, PohonSatuan, label_satuan
from app.models.temuan import KerangkaTabel, ParagrafInput
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.lampiran import baca_lampiran
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import angka

_LABEL_DEPAN = re.compile(r"^(?:\(\d+\)|[a-z]\.|\d+\.|[a-z]\)|\d+\))\s*")
_PENANDA_SAJA = re.compile(
    r"^(Pasal\s+\d+[A-Z]?|BAB\s+[IVXLC]+|Bagian\s+\w+|Paragraf\s+\d+|\(\d+\)|[a-z]\.|\d+\.)$",
    re.IGNORECASE,
)


def _rapat(teks: str) -> str:
    return re.sub(r"\s+", "", teks).lower()


def _rapi(teks: str) -> str:
    return re.sub(r"\s+", " ", teks).strip()


def _kedalaman(pohon: PohonSatuan) -> dict[str, int]:
    dalam: dict[str, int] = {}
    for s in pohon.satuan:
        dalam[s.id] = dalam.get(s.induk, -1) + 1 if s.induk else 0
    return dalam


def teks_di_luar_satuan(paragraf: list[ParagrafInput], pohon: PohonSatuan) -> list[ParagrafInput]:
    """Paragraf batang tubuh yang teksnya tidak termuat di teks satuan mana pun."""
    pasal = pohon.semua(JenisSatuan.PASAL)
    if not pasal:
        return []
    awal = pasal[0].paragraf_mulai
    # Batang tubuh berakhir di penutup ("Ditetapkan di …") atau di lampiran.
    batas = [s.paragraf_mulai for s in (pohon.cari("penutup"), pohon.cari("lampiran")) if s]
    akhir = min(batas) if batas else paragraf[-1].index + 1
    semua = _rapat(" ".join(s.teks for s in pohon.satuan))
    hasil = []
    for p in paragraf:
        if not (awal <= p.index < akhir):
            continue
        teks = _rapi(p.utuh)
        if not teks or _PENANDA_SAJA.match(teks):
            continue
        if _rapat(_LABEL_DEPAN.sub("", teks)) not in semua:
            hasil.append(p)
    return hasil


def susun_ekspor_tahap1(
    paragraf: list[ParagrafInput], tabel_raksasa: Optional[list[KerangkaTabel]] = None
) -> str:
    """Hasil parser naskah ini. Fungsi murni."""
    pohon = bangun_pohon(paragraf)
    baris = [f"===== TAHAP 1 · POHON SATUAN ({len(pohon.satuan)}) ====="]
    if pohon.gagal:
        baris.append(f"PARSER MENYERAH — Fase 2 tidak dijalankan: {pohon.gagal}")
    dalam = _kedalaman(pohon)
    for s in pohon.satuan:
        spasi = "  " * dalam.get(s.id, 0)
        rentang = f"paragraf {s.paragraf_mulai}–{s.paragraf_akhir - 1}"
        baris.append(f"{spasi}[{s.id}] {s.jenis.value} · {rentang}")
        label = label_satuan(s)
        if s.teks or label:
            baris.append(f"{spasi}    {(label + ' ') if label else ''}{s.teks}".rstrip())

    daftar = ambil_definisi(pohon)
    baris += ["", f"===== TAHAP 1 · DEFINISI PASAL 1 ({len(daftar.definisi)}) ====="]
    if daftar.gagal:
        baris.append(f"Tidak terbaca: {daftar.gagal}")
    baris += [f"[{d.satuan_id}] {d.istilah}" for d in daftar.definisi]
    if daftar.tak_terbaca:
        baris.append(
            "Butir Pasal 1 yang tidak terbaca sebagai definisi (tetap dikirim ke AI): "
            + ", ".join(daftar.tak_terbaca)
        )

    lepas = teks_di_luar_satuan(paragraf, pohon)
    baris += [
        "",
        f"===== TAHAP 1 · PARAGRAF BATANG TUBUH DI LUAR TEKS SATUAN ({len(lepas)}) "
        "— tetap dikirim mentah ke AI =====",
    ]
    baris += [f"p{p.index}: {_rapi(p.utuh)}" for p in lepas]

    lampiran = baca_lampiran(paragraf, pohon, tabel_raksasa) if not pohon.gagal else []
    baris += ["", f"===== TAHAP 1 · LAMPIRAN ({len(lampiran)}) ====="]
    for lam in lampiran:
        baris.append(f"{lam.nama or 'Lampiran'} — paragraf {lam.mulai}–{lam.akhir - 1}")
        baris.append("  baris awal : " + " / ".join(lam.kepala))
        baris.append("  baris akhir: " + " / ".join(lam.penutup))
        for b in lam.blok:
            if b.jenis == "kerangka":
                baris.append(
                    f"  kerangka tabel {b.tabel} dari panel — {angka(b.baris)} baris × "
                    f"{b.kolom} kolom, sesudah paragraf {b.mulai - 1}"
                )
            elif b.jenis == "tabel":
                baris.append(
                    f"  tabel {b.tabel} — {b.baris} baris × {b.kolom} kolom, "
                    f"paragraf {b.mulai}–{b.akhir - 1}"
                )
            else:
                baris.append(f"  {b.jenis} — paragraf {b.mulai}–{b.akhir - 1}")
    return "\n".join(baris) + "\n"
