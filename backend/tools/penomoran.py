"""Menghitung nomor otomatis Word dari numbering.xml — CERMINAN, bukan Word.

BUKAN BAGIAN PRODUK. Hanya dipakai `cek_docx.py` supaya alat diagnosa
menghasilkan hal yang sama dengan yang diterima add-in dari Office.js.

=========================================================================
KENAPA INI HARUS ADA
=========================================================================

`python-docx` menyimpan DEFINISI penomoran, tetapi tidak menghitung nomornya —
ia tidak tahu paragraf ini "Pasal 5" atau "Pasal 6". Word yang menghitung,
saat menggambar layar.

Akibatnya, tanpa modul ini alat diagnosa membaca naskah yang berbeda dari yang
dibaca add-in: di layar tertulis "Pasal 5", di CLI kosong. Dua alat yang
berbeda isi bacaannya lebih menyesatkan daripada satu alat yang salah, karena
tidak ada cara tahu mana yang benar.

=========================================================================
BATASNYA, DITULIS TERANG-TERANGAN
=========================================================================

Ini CERMINAN Word, bukan Word. Yang belum ditiru:

  - `w:lvlRestart` — di sini tingkat yang lebih dalam SELALU dinolkan saat
    tingkat di atasnya naik. Itu perilaku bawaan Word dan hampir selalu benar,
    tetapi bisa dimatikan per tingkat.
  - Butir berbulir (`numFmt="bullet"`) dikembalikan KOSONG. Bulir tidak punya
    makna struktural di PMK, dan menempelkan karakter simbol ke depan teks
    justru merusak pencocokan pola parser.
  - `w:numFmt` di luar decimal/huruf/Romawi dikembalikan sebagai angka biasa.
  - Penomoran yang dilanjutkan antar-bagian dokumen (`w:startOverride` rumit)
    cuma ditangani bentuk sederhananya.

KALAU CLI DAN WORD BERBEDA, YANG BENAR WORD. Sumber kebenaran sebenarnya
adalah Ekspor Tahap 0 dari panel, yang berjalan di atas data Office.js
sungguhan.
"""

from __future__ import annotations

import re
from typing import Optional

from docx.oxml.ns import qn

_ROMAWI = [
    (1000, "m"), (900, "cm"), (500, "d"), (400, "cd"),
    (100, "c"), (90, "xc"), (50, "l"), (40, "xl"),
    (10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i"),
]

_RUJUK_TINGKAT = re.compile(r"%(\d)")


def _romawi(n: int) -> str:
    if n <= 0:
        return str(n)
    keluar: list[str] = []
    for nilai, huruf in _ROMAWI:
        while n >= nilai:
            keluar.append(huruf)
            n -= nilai
    return "".join(keluar)


def _huruf(n: int) -> str:
    """1 → a, 26 → z, 27 → aa. Sama dengan lowerLetter di Word."""
    if n <= 0:
        return str(n)
    keluar = ""
    while n > 0:
        n, sisa = divmod(n - 1, 26)
        keluar = chr(ord("a") + sisa) + keluar
    return keluar


def _format(n: int, bentuk: str) -> str:
    if bentuk == "lowerLetter":
        return _huruf(n)
    if bentuk == "upperLetter":
        return _huruf(n).upper()
    if bentuk == "lowerRoman":
        return _romawi(n)
    if bentuk == "upperRoman":
        return _romawi(n).upper()
    return str(n)


class _Tingkat:
    __slots__ = ("bentuk", "pola", "mulai")

    def __init__(self, bentuk: str, pola: str, mulai: int) -> None:
        self.bentuk = bentuk
        self.pola = pola
        self.mulai = mulai


def _baca_definisi(bagian_numbering) -> dict[str, dict[int, _Tingkat]]:
    """numId → {ilvl: _Tingkat}. Dibaca sekali per dokumen."""
    abstrak: dict[str, dict[int, _Tingkat]] = {}
    for a in bagian_numbering.findall(qn("w:abstractNum")):
        kunci = a.get(qn("w:abstractNumId"))
        tingkat: dict[int, _Tingkat] = {}
        for lvl in a.findall(qn("w:lvl")):
            try:
                ilvl = int(lvl.get(qn("w:ilvl")))
            except (TypeError, ValueError):
                continue
            fmt = lvl.find(qn("w:numFmt"))
            teks = lvl.find(qn("w:lvlText"))
            mulai = lvl.find(qn("w:start"))
            tingkat[ilvl] = _Tingkat(
                bentuk=fmt.get(qn("w:val")) if fmt is not None else "decimal",
                pola=teks.get(qn("w:val")) if teks is not None else "%1",
                mulai=int(mulai.get(qn("w:val"))) if mulai is not None else 1,
            )
        abstrak[kunci] = tingkat

    hasil: dict[str, dict[int, _Tingkat]] = {}
    for n in bagian_numbering.findall(qn("w:num")):
        num_id = n.get(qn("w:numId"))
        rujuk = n.find(qn("w:abstractNumId"))
        if rujuk is None:
            continue
        salinan = {
            i: _Tingkat(t.bentuk, t.pola, t.mulai)
            for i, t in abstrak.get(rujuk.get(qn("w:val")), {}).items()
        }
        # startOverride bentuk sederhana: ganti nilai awal satu tingkat.
        for ov in n.findall(qn("w:lvlOverride")):
            try:
                ilvl = int(ov.get(qn("w:ilvl")))
            except (TypeError, ValueError):
                continue
            so = ov.find(qn("w:startOverride"))
            if so is not None and ilvl in salinan:
                salinan[ilvl].mulai = int(so.get(qn("w:val")))
        hasil[num_id] = salinan
    return hasil


class Penomoran:
    """Pencacah berjalan. Paragraf WAJIB disuapkan menurut urutan dokumen."""

    def __init__(self, doc) -> None:
        self._definisi: dict[str, dict[int, _Tingkat]] = {}
        try:
            self._definisi = _baca_definisi(doc.part.numbering_part.element)
        except (AttributeError, KeyError, NotImplementedError):
            # Dokumen tanpa daftar bernomor sama sekali — sah, bukan kegagalan.
            self._definisi = {}
        self._cacah: dict[tuple[str, int], int] = {}

    @staticmethod
    def _ambil_num(paragraf) -> Optional[tuple[str, int]]:
        pPr = paragraf._p.pPr
        if pPr is None:
            return None
        numPr = pPr.find(qn("w:numPr"))
        if numPr is None:
            return None
        nid = numPr.find(qn("w:numId"))
        if nid is None:
            return None
        ilvl_el = numPr.find(qn("w:ilvl"))
        try:
            ilvl = int(ilvl_el.get(qn("w:val"))) if ilvl_el is not None else 0
        except (TypeError, ValueError):
            ilvl = 0
        return nid.get(qn("w:val")), ilvl

    def berikutnya(self, paragraf) -> tuple[str, int]:
        """Kembalikan (penanda, tingkat) untuk paragraf ini.

        ("", -1) berarti paragraf ini bukan butir bernomor otomatis.
        """
        kunci = self._ambil_num(paragraf)
        if kunci is None:
            return "", -1
        num_id, ilvl = kunci
        tingkat = self._definisi.get(num_id)
        if not tingkat or ilvl not in tingkat:
            return "", -1

        # Naikkan cacah tingkat ini, nolkan yang lebih dalam.
        sekarang = self._cacah.get((num_id, ilvl))
        self._cacah[(num_id, ilvl)] = (
            tingkat[ilvl].mulai if sekarang is None else sekarang + 1
        )
        for lebih_dalam in [k for k in self._cacah if k[0] == num_id and k[1] > ilvl]:
            del self._cacah[lebih_dalam]

        def ganti(m: re.Match[str]) -> str:
            sasaran = int(m.group(1)) - 1  # %1 = ilvl 0
            if sasaran not in tingkat:
                return ""
            nilai = self._cacah.get((num_id, sasaran))
            if nilai is None:
                nilai = tingkat[sasaran].mulai
            return _format(nilai, tingkat[sasaran].bentuk)

        if tingkat[ilvl].bentuk == "bullet":
            return "", ilvl
        return _RUJUK_TINGKAT.sub(ganti, tingkat[ilvl].pola).strip(), ilvl
