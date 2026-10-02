"""Membaca .docx seperti add-in membacanya lewat Office.js — BUKAN bagian produk.

Dipakai `cek_docx.py`. Dua hal yang dijaga, keduanya dari naskah nyata:

  SATU SEL, SATU KALI (bug 10). Word menyimpan sel gabungan sebagai SATU
  `w:tc`, dan `body.paragraphs` di Word membacanya sekali. `row.cells`
  python-docx mengembalikannya sekali untuk TIAP kolom yang ditempatinya —
  pembaca lama memakai itu, dan PMK 119 terbaca 127 pasal padahal 64, lalu
  F2-004 melaporkan 63 "Pasal nomor N muncul lebih dari sekali" yang tidak
  pernah ada di Word. Di sini tiap `w:tc` dibaca sekali, termasuk tabel
  bersarang dan isi content control, persis urutan `body.paragraphs`.

  MENGALIR, TIDAK DIMUAT SELURUHNYA. document.xml PMK 108/2024 berukuran
  592 MB (609 ribu paragraf); memuatnya jadi pohon XML menghabiskan memori.
  XML dibaca potong demi potong, dan tabel raksasa diringkas jadi KERANGKA —
  sama dengan yang dikirim panel (`office.ts`), supaya backend menerima
  bentuk yang sama dari keduanya.

Batas "raksasa" dan jumlah baris contoh WAJIB sama dengan `office.ts`.
"""

from __future__ import annotations

import posixpath
import zipfile
from pathlib import Path
from typing import BinaryIO, Optional

from docx.oxml.ns import qn
from lxml import etree

from tools.penomoran import Penomoran

# Tabel tingkat teratas dengan baris lebih dari ini tidak dibaca per paragraf.
# Sama dengan BATAS_BARIS_RAKSASA di frontend/src/lib/office.ts.
BATAS_BARIS_RAKSASA = 1000
# Baris pertama tabel raksasa yang ikut dikirim sebagai contoh (judul kolom
# biasanya di baris pertama). Sama dengan BARIS_CONTOH di office.ts.
BARIS_CONTOH = 5

_W_P, _W_TBL, _W_TR, _W_TC = qn("w:p"), qn("w:tbl"), qn("w:tr"), qn("w:tc")
_W_BODY, _W_SDT_ISI, _W_TXBX = qn("w:body"), qn("w:sdtContent"), qn("w:txbxContent")
_W_R, _W_HYPERLINK = qn("w:r"), qn("w:hyperlink")
_W_T, _W_TAB, _W_BR, _W_CR = qn("w:t"), qn("w:tab"), qn("w:br"), qn("w:cr")
_W_NBH, _W_PTAB, _W_TYPE = qn("w:noBreakHyphen"), qn("w:ptab"), qn("w:type")
_WP_INLINE = "{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}inline"
_M_OMATH = "{http://schemas.openxmlformats.org/officeDocument/2006/math}oMath"
_MC_FALLBACK = "{http://schemas.openxmlformats.org/markup-compatibility/2006}Fallback"
_REL_NUMBERING = "/relationships/numbering"

_INDUK_BLOK = {_W_BODY, _W_TC, _W_SDT_ISI, qn("w:customXml")}


def _teks_run(r) -> str:
    """Sama dengan `CT_R.text` python-docx: t, tab, br, cr, noBreakHyphen, ptab."""
    keluar: list[str] = []
    for e in r:
        tag = e.tag
        if tag == _W_T:
            keluar.append(e.text or "")
        elif tag in (_W_TAB, _W_PTAB):
            keluar.append("\t")
        elif tag == _W_BR:
            # Hanya pemutus baris biasa yang jadi "\n"; pemutus halaman/kolom kosong.
            if e.get(_W_TYPE, "textWrapping") == "textWrapping":
                keluar.append("\n")
        elif tag == _W_CR:
            keluar.append("\n")
        elif tag == _W_NBH:
            keluar.append("-")
    return "".join(keluar)


def teks_paragraf(p) -> str:
    """Sama dengan `CT_P.text` python-docx: `w:r` dan `w:hyperlink` anak langsung."""
    keluar: list[str] = []
    for anak in p:
        if anak.tag == _W_R:
            keluar.append(_teks_run(anak))
        elif anak.tag == _W_HYPERLINK:
            keluar.extend(_teks_run(r) for r in anak if r.tag == _W_R)
    return "".join(keluar)


def _hitung_di_luar_fallback(p, tag: str) -> int:
    """Jumlah elemen `tag` di paragraf, tanpa salinan cadangan `mc:Fallback`.

    Gambar baru disimpan dua kali — `mc:Choice` dan `mc:Fallback` versi lama.
    Word cuma menampilkan satu.
    """
    return sum(
        1
        for e in p.iter(tag)
        if not any(a.tag == _MC_FALLBACK for a in e.iterancestors())
    )


def _numbering(z: zipfile.ZipFile) -> Optional[bytes]:
    """Isi bagian numbering dokumen, dicari lewat relasinya — bukan nama tebakan."""
    try:
        rels = etree.fromstring(z.read("word/_rels/document.xml.rels"))
    except KeyError:
        return None
    for rel in rels:
        if rel.get("Type", "").endswith(_REL_NUMBERING):
            sasaran = posixpath.normpath(posixpath.join("word", rel.get("Target", "")))
            try:
                return z.read(sasaran)
            except KeyError:
                return None
    return None


class _Tabel:
    __slots__ = ("id", "atas", "baris", "sel", "raksasa", "tampung", "contoh", "kolom")

    def __init__(self, id_tabel: int, atas: bool) -> None:
        self.id = id_tabel
        self.atas = atas
        self.baris = -1
        self.sel = -1
        self.raksasa = False
        self.tampung: list[dict] = []
        self.contoh: list[list[str]] = []
        self.kolom = 0


def baca_docx(path: Path, dengan_format: bool = False) -> tuple[list[dict], list[dict]]:
    """Paragraf naskah, dan kerangka tabel raksasa yang tidak dibaca per paragraf.

    Tiap paragraf: teks, penanda, tingkat, dari_tabel, tabel, baris, sel,
    gambar, rumus, letak_pasti — medannya sama dengan `ParagrafInput`.
    `dengan_format` ikut membaca format tiap paragraf (Fase 4, putaran
    format) — lihat `tools/baca_format.py`.
    """
    with zipfile.ZipFile(path) as z:
        nomor = Penomoran.dari_xml(_numbering(z))
        gaya = None
        if dengan_format:
            from tools.baca_format import Gaya

            gaya = Gaya(z)
        with z.open("word/document.xml") as f:
            return _baca(f, nomor, gaya)


def baca_halaman_docx(path: Path) -> list[dict]:
    """Format tiap bagian (section): kertas, marjin, kepala halaman."""
    from tools.baca_format import baca_halaman

    with zipfile.ZipFile(path) as z:
        return baca_halaman(z)


def _baca(f: BinaryIO, nomor: Penomoran, gaya=None) -> tuple[list[dict], list[dict]]:
    paragraf: list[dict] = []
    kerangka: list[dict] = []
    tumpuk: list[_Tabel] = []
    tabel_ke = -1
    dalam_txbx = 0
    # Sesudah tabel raksasa pertama, nomor paragraf tidak lagi sama dengan
    # nomor di Word: panel tidak bisa menghitung paragraf di dalam tabel yang
    # tidak dibacanya. Alat ini meniru panel, bukan membetulkannya.
    letak_pasti = True

    def keluarkan(e: dict) -> None:
        # Paragraf di dalam tabel teratas ditampung dulu: raksasa atau tidaknya
        # baru ketahuan sesudah barisnya dihitung.
        atas = tumpuk[0] if tumpuk else None
        if atas is not None:
            if not atas.raksasa:
                atas.tampung.append(e)
            return
        e["letak_pasti"] = letak_pasti
        paragraf.append(e)

    for peristiwa, el in etree.iterparse(
        f, events=("start", "end"), tag=(_W_P, _W_TBL, _W_TR, _W_TC, _W_TXBX), huge_tree=True
    ):
        tag = el.tag
        if tag == _W_TXBX:
            dalam_txbx += 1 if peristiwa == "start" else -1
            continue
        if dalam_txbx:
            continue  # isi kotak teks bukan paragraf badan naskah

        if peristiwa == "start":
            if tag == _W_TBL:
                tabel_ke += 1
                tumpuk.append(_Tabel(tabel_ke, atas=not tumpuk))
            elif tag == _W_TR and tumpuk:
                t = tumpuk[-1]
                t.baris += 1
                t.sel = -1
                if t.atas and t.baris >= BATAS_BARIS_RAKSASA and not t.raksasa:
                    t.raksasa = True
                    t.tampung = []
            elif tag == _W_TC and tumpuk:
                t = tumpuk[-1]
                t.sel += 1
                if t.atas:
                    t.kolom = max(t.kolom, t.sel + 1)
            continue

        # --- akhir elemen ---------------------------------------------------
        if tag == _W_P:
            induk = el.getparent()
            if induk is None or induk.tag not in _INDUK_BLOK:
                continue
            penanda, tingkat = nomor.berikutnya(el)
            teks = teks_paragraf(el)
            dalam = tumpuk[-1] if tumpuk else None
            atas = tumpuk[0] if tumpuk else None
            if atas is not None and len(tumpuk) == 1 and atas.baris < BARIS_CONTOH:
                while len(atas.contoh) <= atas.baris:
                    atas.contoh.append([])
                baris = atas.contoh[atas.baris]
                while len(baris) <= atas.sel:
                    baris.append("")
                isi = (penanda + " " + teks).strip() if penanda else teks.strip()
                if isi:
                    baris[atas.sel] = f"{baris[atas.sel]} / {isi}" if baris[atas.sel] else isi
            keluarkan(
                {
                    "teks": teks,
                    "penanda": penanda,
                    "tingkat": tingkat,
                    "dari_tabel": dalam is not None,
                    "tabel": dalam.id if dalam else -1,
                    "baris": dalam.baris if dalam else -1,
                    "sel": dalam.sel if dalam else -1,
                    "gambar": _hitung_di_luar_fallback(el, _WP_INLINE),
                    "rumus": _hitung_di_luar_fallback(el, _M_OMATH),
                    "format": gaya.format_paragraf(el) if gaya is not None else None,
                }
            )
        elif tag == _W_TBL and tumpuk:
            t = tumpuk.pop()
            if t.atas:
                if t.raksasa:
                    kerangka.append(
                        {
                            "tabel": t.id,
                            "sesudah_paragraf": len(paragraf) - 1,
                            "jumlah_baris": t.baris + 1,
                            "jumlah_kolom": t.kolom,
                            "contoh": t.contoh,
                        }
                    )
                    letak_pasti = False
                else:
                    for e in t.tampung:
                        e["letak_pasti"] = letak_pasti
                    paragraf.extend(t.tampung)

        # Elemen yang sudah selesai dibuang dari memori. Hanya yang berada di
        # jalur blok — isi kotak teks sudah dilewati di atas.
        el.clear(keep_tail=True)
        while el.getprevious() is not None:
            del el.getparent()[0]

    for i, e in enumerate(paragraf):
        e["index"] = i
    return paragraf, kerangka
