"""Membaca FORMAT tiap paragraf .docx seperti panel membacanya — BUKAN bagian produk.

Dipakai `baca_docx.py` (opsi `dengan_format`) dan `cek_docx.py`, supaya
putaran format Fase 4 bisa diuji tanpa Word. Di add-in, Office.js yang
membacanya (`office.ts`) dan memberi nilai efektif langsung; di sini nilai
efektif dihitung sendiri dari rantai gaya:

    bawaan dokumen (docDefaults) → gaya paragraf (basedOn, dari yang terdasar)
    → gaya karakter run → format langsung

KALAU CLI DAN WORD BERBEDA, YANG BENAR WORD. Yang belum ditiru: tema warna,
gaya tabel, dan penomoran yang menyumbang menjorok lewat gaya paragraf.
"""

from __future__ import annotations

import zipfile
from typing import Optional

from docx.oxml.ns import qn
from lxml import etree

from tools.baca_docx import _teks_run

_W_R, _W_HYPERLINK, _W_T = qn("w:r"), qn("w:hyperlink"), qn("w:t")
_TWIP_CM = 567.0

# Nama rata — WAJIB sama dengan `office.ts` (bacaFormat) dan contoh di
# docs/jelaskan.md, supaya klaim format agen bisa dicocokkan gerbang.
_RATA = {
    "left": "rata kiri", "start": "rata kiri",
    "center": "tengah",
    "right": "rata kanan", "end": "rata kanan",
    "both": "rata kiri-kanan", "distribute": "rata kiri-kanan", "justify": "rata kiri-kanan",
}


def _nyala(el) -> Optional[bool]:
    """Nilai on/off OOXML: <w:b/> = True, <w:b w:val="0"/> = False, tidak ada = None."""
    if el is None:
        return None
    v = el.get(qn("w:val"))
    return v not in ("0", "false", "off")


class Gaya:
    """Rantai gaya satu dokumen: styles.xml, tema, numbering."""

    def __init__(self, z: zipfile.ZipFile) -> None:
        self.gaya: dict[str, etree._Element] = {}
        self.dasar_r: Optional[etree._Element] = None
        self.dasar_p: Optional[etree._Element] = None
        self.tema: dict[str, str] = {}
        self.gaya_paragraf_bawaan: Optional[str] = None
        try:
            akar = etree.fromstring(z.read("word/styles.xml"))
        except KeyError:
            akar = None
        if akar is not None:
            dd = akar.find(qn("w:docDefaults"))
            if dd is not None:
                self.dasar_r = dd.find(f"{qn('w:rPrDefault')}/{qn('w:rPr')}")
                self.dasar_p = dd.find(f"{qn('w:pPrDefault')}/{qn('w:pPr')}")
            for s in akar.findall(qn("w:style")):
                sid = s.get(qn("w:styleId"))
                if sid:
                    self.gaya[sid] = s
                if s.get(qn("w:type")) == "paragraph" and s.get(qn("w:default")) in ("1", "true"):
                    self.gaya_paragraf_bawaan = sid
        try:
            tema = etree.fromstring(z.read("word/theme/theme1.xml"))
            a = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
            for nama, jalur in (("major", "majorFont"), ("minor", "minorFont")):
                el = tema.find(f".//{a}{jalur}/{a}latin")
                if el is not None:
                    self.tema[nama] = el.get("typeface", "")
        except KeyError:
            pass

    # -- rantai -------------------------------------------------------------

    def _rantai(self, sid: Optional[str]) -> list[etree._Element]:
        """Gaya dan leluhurnya, dari yang TERDASAR."""
        hasil = []
        terlihat = set()
        while sid and sid in self.gaya and sid not in terlihat:
            terlihat.add(sid)
            s = self.gaya[sid]
            hasil.append(s)
            b = s.find(qn("w:basedOn"))
            sid = b.get(qn("w:val")) if b is not None else None
        return list(reversed(hasil))

    def _rpr_berlapis(self, p, r) -> list:
        lapis = [self.dasar_r]
        ppr = p.find(qn("w:pPr"))
        ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
        sid = ps.get(qn("w:val")) if ps is not None else self.gaya_paragraf_bawaan
        lapis += [s.find(qn("w:rPr")) for s in self._rantai(sid)]
        rpr = r.find(qn("w:rPr")) if r is not None else None
        rs = rpr.find(qn("w:rStyle")) if rpr is not None else None
        if rs is not None:
            lapis += [s.find(qn("w:rPr")) for s in self._rantai(rs.get(qn("w:val")))]
        lapis.append(rpr)
        return [x for x in lapis if x is not None]

    def _ppr_berlapis(self, p) -> list:
        lapis = [self.dasar_p]
        ppr = p.find(qn("w:pPr"))
        ps = ppr.find(qn("w:pStyle")) if ppr is not None else None
        sid = ps.get(qn("w:val")) if ps is not None else self.gaya_paragraf_bawaan
        lapis += [s.find(qn("w:pPr")) for s in self._rantai(sid)]
        lapis.append(ppr)
        return [x for x in lapis if x is not None]

    # -- nilai efektif run ---------------------------------------------------

    def _run(self, p, r) -> dict:
        nilai: dict = {}
        for rpr in self._rpr_berlapis(p, r):
            f = rpr.find(qn("w:rFonts"))
            if f is not None:
                nama = f.get(qn("w:ascii")) or f.get(qn("w:hAnsi"))
                tema = f.get(qn("w:asciiTheme")) or f.get(qn("w:hAnsiTheme"))
                if nama:
                    nilai["huruf"] = nama
                elif tema:
                    nilai["huruf"] = self.tema.get("major" if "major" in tema else "minor", "")
            sz = rpr.find(qn("w:sz"))
            if sz is not None and sz.get(qn("w:val")):
                try:
                    nilai["ukuran"] = int(sz.get(qn("w:val"))) / 2
                except ValueError:
                    pass
            for kunci, tag in (("tebal", "w:b"), ("miring", "w:i"), ("kapital", "w:caps"), ("hidden", "w:vanish")):
                v = _nyala(rpr.find(qn(tag)))
                if v is not None:
                    nilai[kunci] = v
            u = rpr.find(qn("w:u"))
            if u is not None:
                nilai["garis_bawah"] = u.get(qn("w:val"), "single") not in ("none", "0")
            c = rpr.find(qn("w:color"))
            if c is not None and c.get(qn("w:val")):
                nilai["warna"] = c.get(qn("w:val"))
        return nilai

    # -- format satu paragraf -----------------------------------------------

    def format_paragraf(self, p) -> dict:
        """Medan FormatParagraf untuk elemen w:p."""
        runs: list[tuple[str, dict]] = []
        for anak in p:
            daftar = [anak] if anak.tag == _W_R else [r for r in anak if r.tag == _W_R] if anak.tag == _W_HYPERLINK else []
            for r in daftar:
                # Pembaca teks yang SAMA dengan teks paragraf (t, tab, br, …),
                # supaya potongan tersembunyi persis ada di teks paragraf.
                teks = _teks_run(r)
                if teks:
                    runs.append((teks, self._run(p, r)))

        tampak = [(t, v) for t, v in runs if not v.get("hidden")]
        hasil: dict = {"tersembunyi": _potongan_tersembunyi(runs)}

        def kunci(v: dict) -> tuple:
            return (v.get("huruf"), v.get("ukuran"), bool(v.get("tebal")), bool(v.get("miring")), bool(v.get("garis_bawah")), bool(v.get("kapital")))

        if tampak:
            bobot: dict[tuple, int] = {}
            for t, v in tampak:
                bobot[kunci(v)] = bobot.get(kunci(v), 0) + len(t.strip())
            utama = max(bobot, key=lambda k: bobot[k])
            huruf, ukuran, tebal, miring, garis, kapital = utama
            hasil.update(huruf=huruf, ukuran=ukuran, tebal=tebal, miring=miring, garis_bawah=garis, kapital_gaya=kapital)
            warna = next((v.get("warna") for t, v in tampak if v.get("warna")), None)
            if warna:
                hasil["warna"] = "#" + warna if not warna.startswith("#") and warna.lower() != "auto" else warna
            beda: list[dict] = []
            for t, v in tampak:
                if kunci(v) == utama or not t.strip():
                    continue
                ket = _keterangan(utama, kunci(v))
                if beda and beda[-1]["keterangan"] == ket:
                    beda[-1]["kutipan"] += t
                else:
                    beda.append({"keterangan": ket, "kutipan": t})
            # Potongan yang isinya cuma tanda baca ("; " tak bermiring di
            # paragraf miring) tidak ditulis: tidak membawa kata yang bisa
            # dinilai, dan menggandakan anotasi di tabel lampiran.
            hasil["bagian_beda"] = [b for b in beda if any(c.isalnum() for c in b["kutipan"])]
        else:
            v = self._run(p, None)
            hasil.update(huruf=v.get("huruf"), ukuran=v.get("ukuran"))

        jc = ind = sp = None
        for ppr in self._ppr_berlapis(p):
            jc = ppr.find(qn("w:jc")) if ppr.find(qn("w:jc")) is not None else jc
            i = ppr.find(qn("w:ind"))
            if i is not None:
                ind = {**(ind or {}), **{k: v for k, v in i.attrib.items()}}
            s = ppr.find(qn("w:spacing"))
            if s is not None:
                sp = {**(sp or {}), **{k: v for k, v in s.attrib.items()}}
        hasil["rata"] = _RATA.get(jc.get(qn("w:val")), None) if jc is not None else "rata kiri"
        if ind:
            kiri = ind.get(qn("w:left")) or ind.get(qn("w:start"))
            kanan = ind.get(qn("w:right")) or ind.get(qn("w:end"))
            if kiri is not None:
                hasil["kiri_cm"] = round(int(kiri) / _TWIP_CM, 2)
            if kanan is not None:
                hasil["kanan_cm"] = round(int(kanan) / _TWIP_CM, 2)
            if ind.get(qn("w:hanging")) is not None:
                hasil["baris_pertama_cm"] = -round(int(ind[qn("w:hanging")]) / _TWIP_CM, 2)
            elif ind.get(qn("w:firstLine")) is not None:
                hasil["baris_pertama_cm"] = round(int(ind[qn("w:firstLine")]) / _TWIP_CM, 2)
        if sp:
            if sp.get(qn("w:before")) is not None:
                hasil["spasi_sebelum_pt"] = int(sp[qn("w:before")]) / 20
            if sp.get(qn("w:after")) is not None:
                hasil["spasi_sesudah_pt"] = int(sp[qn("w:after")]) / 20
            if sp.get(qn("w:line")) is not None and sp.get(qn("w:lineRule"), "auto") == "auto":
                hasil["spasi_baris"] = round(int(sp[qn("w:line")]) / 240, 2)
        return hasil


def _potongan_tersembunyi(runs: list[tuple[str, dict]]) -> list[str]:
    """Potongan teks hidden, urut. Yang hanya dipisah spasi dirangkai berikut spasinya.

    PMK 4/2025 menyimpan "jJ jJ" sebagai dua run hidden dipisah satu spasi
    biasa. Dirangkai tanpa spasinya jadi "jJjJ" — tidak ada di teks paragraf,
    jadi kutipan agen tidak akan pernah ketemu gerbang.
    """
    hasil: list[str] = []
    kini: Optional[str] = None
    spasi = ""
    for t, v in runs:
        if v.get("hidden"):
            kini = (kini + spasi + t) if kini is not None else t
            spasi = ""
        elif kini is not None and not t.strip():
            spasi += t
        else:
            if kini is not None and kini.strip():
                hasil.append(kini)
            kini, spasi = None, ""
    if kini is not None and kini.strip():
        hasil.append(kini)
    return hasil


def _keterangan(utama: tuple, lain: tuple) -> str:
    huruf, ukuran, tebal, miring, garis, kapital = lain
    bag = []
    if (huruf, ukuran) != utama[:2]:
        bag.append(" ".join(str(x) for x in (huruf or "", f"{ukuran:g}" if ukuran else "") if x))
    for ada, utama_ada, nama in (
        (tebal, utama[2], "tebal"),
        (miring, utama[3], "miring"),
        (garis, utama[4], "garis bawah"),
        (kapital, utama[5], "KAPITAL dari gaya"),
    ):
        if ada and not utama_ada:
            bag.append(nama)
        elif utama_ada and not ada:
            bag.append("tidak " + nama)
    return " ".join(bag) or "gaya lain"


def baca_halaman(z: zipfile.ZipFile) -> list[dict]:
    """Format tiap bagian (section): kertas, marjin, kepala halaman."""
    rels = {}
    try:
        akar_rel = etree.fromstring(z.read("word/_rels/document.xml.rels"))
        rels = {r.get("Id"): r.get("Target") for r in akar_rel}
    except KeyError:
        pass
    hasil: list[dict] = []
    with z.open("word/document.xml") as f:
        for _, el in etree.iterparse(f, events=("end",), tag=qn("w:sectPr"), huge_tree=True):
            h: dict = {"bagian": len(hasil)}
            pg = el.find(qn("w:pgSz"))
            if pg is not None:
                if pg.get(qn("w:w")):
                    h["lebar_cm"] = round(int(pg.get(qn("w:w"))) / _TWIP_CM, 1)
                if pg.get(qn("w:h")):
                    h["tinggi_cm"] = round(int(pg.get(qn("w:h"))) / _TWIP_CM, 1)
            mg = el.find(qn("w:pgMar"))
            if mg is not None:
                for kunci, a in (("marjin_atas_cm", "w:top"), ("marjin_bawah_cm", "w:bottom"), ("marjin_kiri_cm", "w:left"), ("marjin_kanan_cm", "w:right")):
                    if mg.get(qn(a)):
                        h[kunci] = round(int(mg.get(qn(a))) / _TWIP_CM, 1)
            h["halaman_pertama_beda"] = _nyala(el.find(qn("w:titlePg"))) is True
            for ref in el.findall(qn("w:headerReference")):
                jenis = ref.get(qn("w:type"))
                target = rels.get(ref.get(qn("r:id")))
                if not target:
                    continue
                try:
                    kepala = etree.fromstring(z.read("word/" + target))
                except KeyError:
                    continue
                teks = " ".join(t.text or "" for t in kepala.iter(_W_T)).strip()
                instr = "".join(t.text or "" for t in kepala.iter(qn("w:instrText")))
                fld = [x.get(qn("w:instr"), "") for x in kepala.iter(qn("w:fldSimple"))]
                gambar = len(list(kepala.iter(qn("w:drawing")))) + len(list(kepala.iter(qn("w:pict"))))
                if jenis == "first":
                    h["kepala_pertama"] = teks
                    h["gambar_kepala_pertama"] = gambar
                elif jenis == "default":
                    h["kepala_berikut"] = teks
                    h["nomor_halaman"] = "PAGE" in instr.upper() or any("PAGE" in x.upper() for x in fld)
            hasil.append(h)
            el.clear(keep_tail=True)
    return hasil
