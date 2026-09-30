"""TAHAP 1 (parser) — lampiran: bingkainya, dan jenis fisik tiap blok isinya.

KMK 527 butir 120–121 (hlm 57, dibaca dari citra halaman 29 Sep 2026) hanya
membakukan BINGKAI lampiran: kata LAMPIRAN (berangka Romawi bila lebih dari
satu), judul PMK di bawahnya, judul lampiran, isi, lalu nama dan tanda tangan
pejabat di akhir. ISINYA BEBAS — teks, tabel, gambar, rumus.

Kode di sini MENGUMPULKAN, tidak memutuskan. Pola lampiran terlalu beragam
untuk dinilai regex: PMK 119 memuat "Lampiran Surat" di tengah contoh format
surat, dan itu bukan kepala lampiran. Yang dikerjakan cuma memilah naskah jadi
satuan lampiran dan blok berjenis fisik; menilai apakah bingkainya benar
urusan model di tahap 3 (F2-106), dengan parameter tertulis — sah menurut
CLAUDE.md butir 12, karena parser sudah berulang gagal dengan pola serupa.

Tidak ada teks yang dibuang di sini. Blok hanya pengelompokan; bahan untuk
model tetap disusun dari seluruh paragraf (`tahap2_persiapan/bahan.py`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from app.models.satuan import PohonSatuan
from app.models.temuan import KerangkaTabel, ParagrafInput

# Kepala satuan lampiran: "LAMPIRAN", "LAMPIRAN II" — satu paragraf sendiri,
# atau langsung disambung judul peraturannya.
_KEPALA = re.compile(
    r"^LAMPIRAN(?:\s+([IVXLCDM]+))?\s*(?:$|PERATURAN\s+MENTERI\b)", re.IGNORECASE
)
_PERATURAN_MENTERI = re.compile(r"^PERATURAN\s+MENTERI\b", re.IGNORECASE)

# Baris awal dan akhir tiap lampiran yang dikumpulkan sebagai fakta: cukup untuk
# memuat LAMPIRAN, judul PMK, dan judul lampiran; dan jabatan, ttd., nama.
_BARIS_KEPALA = 8
_BARIS_PENUTUP = 4


@dataclass
class Blok:
    """Sederet paragraf lampiran yang jenis fisiknya sama."""

    jenis: str  # "teks" | "tabel" | "gambar" | "rumus" | "kerangka"
    mulai: int  # index paragraf pertama
    akhir: int  # index paragraf terakhir + 1
    tabel: int = -1
    baris: int = 0
    kolom: int = 0


@dataclass
class Lampiran:
    nomor: str  # "" untuk lampiran tunggal, atau angka Romawi
    mulai: int
    akhir: int
    kepala: list[str] = field(default_factory=list)
    penutup: list[str] = field(default_factory=list)
    blok: list[Blok] = field(default_factory=list)

    @property
    def nama(self) -> str:
        return f"Lampiran {self.nomor}".strip()


def _rapi(teks: str) -> str:
    return re.sub(r"\s+", " ", teks).strip()


def _jenis(p: ParagrafInput) -> str:
    if p.tabel >= 0:
        return "tabel"
    if p.rumus:
        return "rumus"
    if p.gambar and not p.teks.strip():
        return "gambar"
    return "teks"


def _kepala_lampiran(paragraf: list[ParagrafInput], i: int) -> bool:
    """Paragraf ke-i membuka satuan lampiran baru."""
    teks = _rapi(paragraf[i].utuh)
    m = _KEPALA.match(teks)
    if not m:
        return False
    if _PERATURAN_MENTERI.search(teks[len("LAMPIRAN"):].lstrip(" IVXLCDM")):
        return True
    # Judul peraturannya di paragraf-paragraf berikutnya.
    dilihat = 0
    for q in paragraf[i + 1 :]:
        t = _rapi(q.utuh)
        if not t:
            continue
        if _PERATURAN_MENTERI.match(t):
            return True
        dilihat += 1
        if dilihat >= 3:
            break
    return False


def _blok(isi: list[ParagrafInput], kerangka: list[KerangkaTabel]) -> list[Blok]:
    """Kelompokkan paragraf berurutan yang jenis fisiknya sama.

    Tabel dipisah menurut nomornya — dua tabel yang berdempetan tetap dua blok.
    Kerangka tabel raksasa dari panel disisipkan di tempatnya.
    """
    hasil: list[Blok] = []
    sisip = {k.sesudah_paragraf: k for k in kerangka}
    for p in isi:
        jenis = _jenis(p)
        kini = hasil[-1] if hasil else None
        sama = kini is not None and kini.jenis == jenis and (
            jenis != "tabel" or kini.tabel == p.tabel
        )
        if sama:
            kini.akhir = p.index + 1
            if jenis == "tabel":
                kini.baris = max(kini.baris, p.baris + 1)
                kini.kolom = max(kini.kolom, p.sel + 1)
        else:
            hasil.append(
                Blok(
                    jenis=jenis,
                    mulai=p.index,
                    akhir=p.index + 1,
                    tabel=p.tabel,
                    baris=p.baris + 1 if jenis == "tabel" else 0,
                    kolom=p.sel + 1 if jenis == "tabel" else 0,
                )
            )
        if p.index in sisip:
            k = sisip[p.index]
            hasil.append(
                Blok(
                    jenis="kerangka",
                    mulai=p.index + 1,
                    akhir=p.index + 1,
                    tabel=k.tabel,
                    baris=k.jumlah_baris,
                    kolom=k.jumlah_kolom,
                )
            )
    return hasil


def baca_lampiran(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    kerangka: list[KerangkaTabel] | None = None,
) -> list[Lampiran]:
    """Satuan lampiran di naskah, urut. Kosong bila naskah tanpa lampiran."""
    induk = pohon.cari("lampiran")
    if induk is None:
        return []
    kerangka = kerangka or []

    posisi = [i for i, p in enumerate(paragraf) if p.index >= induk.paragraf_mulai]
    if not posisi:
        return []
    awal_unit = [posisi[0]] + [
        i for i in posisi[1:] if _kepala_lampiran(paragraf, i)
    ]

    hasil: list[Lampiran] = []
    for n, mulai in enumerate(awal_unit):
        akhir = awal_unit[n + 1] if n + 1 < len(awal_unit) else len(paragraf)
        isi = paragraf[mulai:akhir]
        m = _KEPALA.match(_rapi(isi[0].utuh))
        tak_kosong = [_rapi(p.utuh) for p in isi if p.utuh.strip()]
        k_di_sini = [
            k for k in kerangka if isi[0].index <= k.sesudah_paragraf < isi[-1].index + 1
        ]
        hasil.append(
            Lampiran(
                nomor=(m.group(1) or "").upper() if m else "",
                mulai=isi[0].index,
                akhir=isi[-1].index + 1,
                kepala=tak_kosong[:_BARIS_KEPALA],
                penutup=tak_kosong[-_BARIS_PENUTUP:],
                blok=_blok(isi, k_di_sini),
            )
        )
    return hasil
