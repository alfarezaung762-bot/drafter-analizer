"""TAHAP 1 · LANGKAH 7 — naskah berformat: tiap paragraf ¶ beserta formatnya.

Bacaan putaran format. Kode HANYA menuliskan apa yang dibaca Office.js — ia
tidak tahu satu pun kaidah format. Yang menilai agen, dengan skill
`pmk-standar/format`; yang membuktikan klaimnya gerbang, dengan mencocokkan
klaim itu ke anotasi ⟨⟩ paragraf yang sama.

Bentuk satu baris (contoh asli PMK 45, `docs/jelaskan.md` Contoh 2):

    ¶36 [pasal-1-angka-6] 6. Sistem Indonesia National Single Window …
        ⟨Bookman Old Style 12 · rata kiri-kanan · miring: "National Single Window"⟩

Ditulis ringkas tanpa membuang makna: format satu paragraf sekali; bagian
yang berbeda disebut dengan kutipannya. Paragraf kosong tidak ditulis —
jumlahnya disebut di paragraf sesudahnya. Dua pengecualian, karena keduanya
justru yang dicari: paragraf kosong yang ikut daftar bernomor, dan paragraf
yang isinya hanya teks tersembunyi.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.satuan import PohonSatuan
from app.models.temuan import FormatHalaman, FormatParagraf, ParagrafInput
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import id_awal_satuan
from app.telaah.tahap2_persiapan.bahan import hitung_token

BUTIR_KOSONG = "butir bernomor tanpa isi"


@dataclass
class NaskahBerformat:
    teks: str
    token: int
    anotasi: dict[int, str]
    """¶ → isi ⟨⟩ persis — dipakai gerbang membuktikan klaim format."""
    terbaca: bool
    """False bila tidak satu paragraf pun membawa format dari Word."""


def _cm(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def _angka(x: float) -> str:
    return f"{x:g}".replace(".", ",")


def _rapat(t: str) -> str:
    return " ".join(t.split())


def anotasi_format(f: Optional[FormatParagraf], kosong: int, butir_kosong: bool) -> str:
    """Isi ⟨⟩ satu paragraf. Medan yang tidak terbaca tidak ditulis."""
    bag: list[str] = []
    if f is not None:
        if f.huruf or f.ukuran:
            bag.append(" ".join(x for x in (f.huruf or "", _angka(f.ukuran) if f.ukuran else "") if x))
        if f.tebal:
            bag.append("tebal")
        if f.miring:
            bag.append("miring")
        if f.garis_bawah:
            bag.append("garis bawah")
        if f.kapital_gaya:
            bag.append("KAPITAL dari gaya")
        if f.warna and f.warna.lower() not in ("#000000", "000000", "auto", "automatic"):
            bag.append(f"warna {f.warna}")
        if f.rata:
            bag.append(f.rata)
        if f.kiri_cm is not None and abs(f.kiri_cm) >= 0.05:
            bag.append(f"kiri {_cm(f.kiri_cm)} cm")
        if f.kanan_cm is not None and abs(f.kanan_cm) >= 0.05:
            bag.append(f"kanan {_cm(f.kanan_cm)} cm")
        if f.baris_pertama_cm is not None and abs(f.baris_pertama_cm) >= 0.05:
            bag.append(f"baris pertama {_cm(f.baris_pertama_cm)} cm")
        if f.spasi_baris is not None and abs(f.spasi_baris - 1.0) >= 0.01:
            bag.append(f"spasi baris {_angka(f.spasi_baris)}")
        if f.spasi_sebelum_pt:
            bag.append(f"spasi sebelum {_angka(f.spasi_sebelum_pt)} pt")
        if f.spasi_sesudah_pt:
            bag.append(f"spasi sesudah {_angka(f.spasi_sesudah_pt)} pt")
        for b in f.bagian_beda:
            bag.append(f'{b.keterangan}: "{_rapat(b.kutipan)}"')
        for t in f.tersembunyi:
            if t.strip():
                bag.append(f'tersembunyi: "{_rapat(t)}"')
    if butir_kosong:
        bag.append(BUTIR_KOSONG)
    if kosong:
        bag.append(f"{kosong} baris kosong sebelumnya")
    return " · ".join(bag)


def _halaman(h: FormatHalaman) -> list[str]:
    bag = []
    if h.lebar_cm and h.tinggi_cm:
        bag.append(f"kertas {_cm(h.lebar_cm)} × {_cm(h.tinggi_cm)} cm")
    marjin = [
        (n, v)
        for n, v in (
            ("atas", h.marjin_atas_cm),
            ("bawah", h.marjin_bawah_cm),
            ("kiri", h.marjin_kiri_cm),
            ("kanan", h.marjin_kanan_cm),
        )
        if v is not None
    ]
    if marjin:
        bag.append("marjin " + " · ".join(f"{n} {_cm(v)}" for n, v in marjin) + " cm")
    if h.halaman_pertama_beda is not None:
        bag.append("halaman pertama beda kepala: " + ("ya" if h.halaman_pertama_beda else "tidak"))
    baris = [f"Bagian {h.bagian + 1}: " + (" · ".join(bag) if bag else "format halaman tidak terbaca")]
    kepala = []
    if h.kepala_pertama or h.gambar_kepala_pertama:
        kepala.append(
            f'kepala halaman pertama "{_rapat(h.kepala_pertama)}"'
            + (f" · gambar {h.gambar_kepala_pertama}" if h.gambar_kepala_pertama else "")
        )
    if h.kepala_berikut or h.nomor_halaman is not None:
        kepala.append(
            f'kepala halaman berikutnya "{_rapat(h.kepala_berikut)}"'
            + (" · nomor halaman" if h.nomor_halaman else "")
        )
    if kepala:
        baris.append("  " + " · ".join(kepala))
    return baris


def susun_naskah_berformat(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    halaman: Optional[list[FormatHalaman]] = None,
) -> NaskahBerformat:
    terbaca = any(p.format is not None for p in paragraf)
    id_awal = id_awal_satuan(pohon) if pohon.gagal is None else {}
    baris = ["== FORMAT DOKUMEN =="]
    if halaman:
        for h in halaman:
            baris += _halaman(h)
    else:
        baris.append("Format halaman tidak terbaca dari Word.")
    baris += [
        "",
        "== NASKAH UTUH BERFORMAT ==",
        "Satu baris per paragraf: ¶nomor, [label satuan] bila paragraf itu membuka",
        "satuan, teks, lalu format di dalam ⟨⟩. Paragraf kosong tidak ditulis;",
        "jumlahnya disebut di paragraf sesudahnya (\"n baris kosong sebelumnya\").",
        "[tabel t:b:s] = sel tabel t, baris b, sel s.",
    ]
    if not terbaca:
        baris.append(
            "PERHATIAN: format huruf, rata, menjorok, dan spasi tidak terbaca dari Word; "
            "yang tersedia hanya teks, label, baris kosong, dan butir bernomor tanpa isi."
        )
    baris.append("")

    anotasi: dict[int, str] = {}
    kosong = 0
    for p in paragraf:
        teks = _rapat(p.teks)
        tersembunyi = bool(p.format and any(t.strip() for t in p.format.tersembunyi))
        butir_kosong = bool(p.penanda.strip()) and not teks
        if not teks and not butir_kosong and not tersembunyi and not p.gambar:
            kosong += 1
            continue
        a = anotasi_format(p.format, kosong, butir_kosong)
        anotasi[p.index] = a
        sid = id_awal.get(p.index)
        label = f"[{sid}] " if sid else ""
        sel = f"[tabel {p.tabel}:{p.baris}:{p.sel}] " if p.tabel >= 0 else ""
        isi = _rapat(p.utuh)
        if p.gambar:
            isi = (isi + " [GAMBAR — isinya tidak bisa dibaca]").strip()
        baris.append(f"¶{p.index} {sel}{label}{isi}" + (f"  ⟨{a}⟩" if a else ""))
        kosong = 0
    teks = "\n".join(baris)
    return NaskahBerformat(teks=teks, token=hitung_token(teks), anotasi=anotasi, terbaca=terbaca)
