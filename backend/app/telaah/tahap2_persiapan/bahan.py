"""TAHAP 2 — PERSIAPAN: bahan yang dibaca model, disusun dari SELURUH paragraf.

Bahan inilah yang ikut di SETIAP panggilan tahap 3 dan 4, sama persis dan di
depan pesan — supaya potongan harga awalan prompt berlaku, dan supaya tiap
panggilan menilai di atas naskah yang sama.

Dulu model menalar di atas PETA, satu kalimat ringkasan per satuan. Pertentangan
antarpasal bisa lolos karena ringkasannya kehilangan detail, lampiran tidak
pernah dibaca, dan paragraf yang tidak dikenali parser tidak pernah terkirim —
PMK 119: 79 paragraf, termasuk seluruh definisi Pasal 1. Diputuskan penelaah
28 Sep 2026 (bug 7, C + D): naskah dibaca UTUH.

ATURAN YANG DIPEGANG
  - Tidak ada paragraf yang keluar dari bahan. Yang tidak dikenali parser tetap
    dikirim, mentah.
  - Pembukaan, batang tubuh, dan penutup SELALU utuh, apa pun bentuk fisiknya.
    Tabel tidak selalu berarti data: PMK 119 menulis batang tubuhnya di tabel
    tata letak.
  - Hanya TABEL DATA di LAMPIRAN yang boleh diringkas jadi kerangka, dan hanya
    kalau bahan melewati anggaran. Tabel sejenis satu kelompok: semua utuh,
    atau semua kerangka. Isi yang diringkas tetap bisa dibuka model lewat alat
    di tahap 4.
  - Gambar dan rumus disebut terang-terangan tidak terbaca. Model tidak boleh
    mengira tidak ada apa-apa di sana.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from typing import Optional

from app.models.satuan import PohonSatuan
from app.models.temuan import KerangkaTabel, ParagrafInput, Temuan
from app.telaah.tahap1_parser.definisi import _jarak_ubah
from app.telaah.tahap1_parser.lampiran import Lampiran, baca_lampiran
from app.telaah.tahap1_parser.struktur import pasangan_label

# Batas bawah tabel yang dianggap TABEL DATA (bukan tata letak): cukup baris,
# dan lebih dari satu kolom.
_DATA_MIN_BARIS = 4
_DATA_MIN_KOLOM = 2
# Baris isi yang ditampilkan di kerangka, sesudah baris judul kolom.
_CONTOH_KERANGKA = 3
# Rasio cadangan kalau tiktoken tidak tersedia. Teks hukum berbahasa Indonesia
# ±3,3 huruf per token pada tokenizer gpt-4.1; 3,0 sengaja lebih boros supaya
# perkiraannya tidak pernah di bawah kenyataan.
_HURUF_PER_TOKEN_CADANGAN = 3.0

_GAMBAR = "[GAMBAR — isinya tidak bisa dibaca]"
_RUMUS = "[RUMUS — tidak terbaca]"


# ---------------------------------------------------------------------------
# Penghitung token
# ---------------------------------------------------------------------------

_penyandi = None
_cara_hitung = ""


def _siapkan_penyandi() -> None:
    global _penyandi, _cara_hitung
    if _cara_hitung:
        return
    try:
        import tiktoken

        _penyandi = tiktoken.get_encoding("o200k_base")
        _cara_hitung = "tiktoken o200k_base (tokenizer gpt-4.1)"
    except Exception:  # noqa: BLE001 — paket atau berkas kosakatanya tidak ada
        _penyandi = None
        _cara_hitung = (
            f"perkiraan kasar — huruf ÷ {_HURUF_PER_TOKEN_CADANGAN:g}; "
            "tiktoken tidak tersedia"
        )


def hitung_token(teks: str) -> int:
    """Jumlah token menurut tokenizer gpt-4.1, atau perkiraan kasarnya."""
    _siapkan_penyandi()
    if _penyandi is not None:
        return len(_penyandi.encode(teks, disallowed_special=()))
    return math.ceil(len(teks) / _HURUF_PER_TOKEN_CADANGAN)


def cara_hitung() -> str:
    _siapkan_penyandi()
    return _cara_hitung


# ---------------------------------------------------------------------------
# Bentuk bahan
# ---------------------------------------------------------------------------


@dataclass
class TabelNaskah:
    """Satu tabel, disusun ulang dari paragraf-paragrafnya."""

    nomor: int
    baris: list[list[str]] = field(default_factory=list)
    di_lampiran: bool = False

    @property
    def kolom(self) -> int:
        return max((len(b) for b in self.baris), default=0)

    @property
    def data(self) -> bool:
        return len(self.baris) >= _DATA_MIN_BARIS and self.kolom >= _DATA_MIN_KOLOM

    def kunci_sejenis(self) -> tuple:
        """Tabel sejenis: kolomnya sama banyak dan judul kolomnya sama."""
        judul = tuple(_rapi(s).lower() for s in (self.baris[0] if self.baris else []))
        return (self.kolom, judul)


@dataclass
class Bahan:
    """Bahan satu naskah — teks yang dikirim, dan yang dibutuhkan alat tahap 4."""

    teks: str
    token: dict[str, int]
    cara_hitung: str
    anggaran: int
    kerangka: list[str]
    tabel: dict[int, TabelNaskah]
    tabel_raksasa: dict[int, KerangkaTabel]
    fakta_lampiran: str
    lampiran: list[Lampiran]
    paragraf: list[ParagrafInput]
    id_paragraf: dict[int, str]
    # Berapa paragraf pembukaan/batang tubuh yang menyebut "Lampiran", dan
    # berapa kata mirip "Lampiran". Nol keduanya dan tanpa lampiran berarti
    # tidak ada yang perlu diperiksa F2-106.
    lampiran_disebut: int = 0
    lampiran_mirip: int = 0

    @property
    def total_token(self) -> int:
        return self.token.get("total", 0)

    @property
    def ada_urusan_lampiran(self) -> bool:
        return bool(self.lampiran or self.lampiran_disebut or self.lampiran_mirip)


def _rapi(teks: str) -> str:
    return re.sub(r"\s+", " ", teks).strip()


def angka(n: int) -> str:
    """12345 → "12.345", pemisah ribuan cara Indonesia."""
    return f"{n:,}".replace(",", ".")


def _baris_paragraf(p: ParagrafInput, teks: Optional[str] = None) -> str:
    """Isi satu paragraf, berikut catatan gambar/rumus yang tidak terbaca."""
    isi = _rapi(p.utuh if teks is None else teks)
    catatan = []
    if p.gambar:
        catatan.append(_GAMBAR)
    if p.rumus:
        catatan.append(_RUMUS)
    return " ".join([isi] + catatan).strip()


def id_awal_satuan(pohon: PohonSatuan) -> dict[int, str]:
    """index paragraf → id satuan yang DIMULAI di paragraf itu (yang terdalam)."""
    peta: dict[int, str] = {}
    for s in pohon.satuan:
        peta[s.paragraf_mulai] = s.id
    return peta


def peta_satuan(pohon: PohonSatuan) -> dict[int, str]:
    """index paragraf → id satuan TERDALAM yang memuatnya.

    Pohon disimpan induk lebih dulu daripada anaknya, dan rentang saudara tidak
    bertindihan — jadi yang ditulis belakangan memang yang terdalam.
    """
    peta: dict[int, str] = {}
    for s in pohon.satuan:
        for i in range(s.paragraf_mulai, s.paragraf_akhir):
            peta[i] = s.id
    return peta


def _letak(peta: dict[int, str], index: int) -> str:
    return peta.get(index) or f"paragraf {index}"


def _sisip_kerangka(
    raksasa: dict[int, KerangkaTabel], paragraf: list[ParagrafInput], awal: bool
) -> dict[int, list[KerangkaTabel]]:
    """Kerangka tabel raksasa yang jatuh di rentang paragraf ini, menurut letaknya.

    Kunci -1 berarti sebelum paragraf pertama rentang ini. Tidak ada kerangka
    yang boleh terlewat: yang di luar rentang mana pun ditaruh di depan.
    """
    if not paragraf:
        return {}
    pertama, terakhir = paragraf[0].index, paragraf[-1].index
    hasil: dict[int, list[KerangkaTabel]] = {}
    for k in raksasa.values():
        if pertama <= k.sesudah_paragraf <= terakhir:
            hasil.setdefault(k.sesudah_paragraf, []).append(k)
        elif awal and k.sesudah_paragraf < pertama:
            hasil.setdefault(-1, []).append(k)
    return hasil


def _baris_naskah(
    paragraf: list[ParagrafInput],
    id_awal: dict[int, str],
    sisip: dict[int, list[KerangkaTabel]],
) -> list[str]:
    """Pembukaan, batang tubuh, penutup: satu baris per paragraf, tanpa kecuali.

    Label yang terpisah sel dari teksnya disatukan jadi satu baris, sama seperti
    parser membacanya (bug 11). Paragraf kosong tidak memuat teks apa pun, jadi
    dilewati; yang bergambar tetap disebut.
    """
    pasangan = pasangan_label(paragraf)
    dilewati: set[int] = set()
    baris: list[str] = []
    for k in sisip.get(-1, []):
        baris += _kerangka_panel(k)
    for i, p in enumerate(paragraf):
        if i not in dilewati:
            teks = p.utuh
            j = pasangan.get(i)
            if j is not None:
                teks = p.utuh + " " + paragraf[j].utuh
                dilewati.add(j)
            isi = _baris_paragraf(p, teks)
            if isi:
                sid = id_awal.get(p.index)
                baris.append(f"[{sid}] {isi}" if sid else isi)
        for k in sisip.get(p.index, []):
            baris += _kerangka_panel(k)
    return baris


def _kumpulkan_tabel(paragraf: list[ParagrafInput], di_lampiran: bool) -> dict[int, TabelNaskah]:
    tabel: dict[int, TabelNaskah] = {}
    for p in paragraf:
        if p.tabel < 0:
            continue
        t = tabel.setdefault(p.tabel, TabelNaskah(nomor=p.tabel, di_lampiran=di_lampiran))
        while len(t.baris) <= p.baris:
            t.baris.append([])
        sel = t.baris[p.baris]
        while len(sel) <= p.sel:
            sel.append("")
        isi = _baris_paragraf(p)
        if isi:
            sel[p.sel] = f"{sel[p.sel]} / {isi}" if sel[p.sel] else isi
    return tabel


def baris_tabel(sel: list[str]) -> str:
    return "| " + " | ".join(sel) + " |"


def _kepala_tabel(t: TabelNaskah) -> str:
    return f"[TABEL {t.nomor} · {len(t.baris)} baris × {t.kolom} kolom]"


def _kerangka_tabel(t: TabelNaskah) -> list[str]:
    contoh = t.baris[: 1 + _CONTOH_KERANGKA]
    return [
        f"[TABEL {t.nomor} · KERANGKA — {angka(len(t.baris))} baris × {t.kolom} kolom. "
        f"Bahan melewati anggaran, jadi yang ikut hanya judul kolom dan "
        f"{len(contoh) - 1} baris pertama. Isi lengkapnya bisa dibuka dengan alat "
        f"buka_tabel saat memastikan.]"
    ] + [baris_tabel(b) for b in contoh]


def _kerangka_panel(k: KerangkaTabel) -> list[str]:
    return [
        f"[TABEL {k.tabel} · KERANGKA DARI PANEL — {angka(k.jumlah_baris)} baris × "
        f"{k.jumlah_kolom} kolom. Tabel ini terlalu besar untuk dibaca panel, jadi "
        f"yang dikirim hanya {len(k.contoh)} baris pertama. Isi selebihnya TIDAK "
        f"ada di bahan ini dan tidak bisa dibuka.]"
    ] + [baris_tabel(b) for b in k.contoh]


def _baris_lampiran(
    paragraf: list[ParagrafInput],
    id_awal: dict[int, str],
    tabel: dict[int, TabelNaskah],
    ringkas: set[int],
    sisip: dict[int, list[KerangkaTabel]],
) -> list[str]:
    """Lampiran: teks per paragraf, tabel per baris sel, kerangka di tempatnya.

    Tiap baris tabel ditulis SEKALI, saat pertama muncul — isinya sudah lengkap
    karena disusun lebih dulu. Tabel bersarang menyela baris tabel luarnya di
    urutan paragraf Word, dan tanpa penjagaan ini baris luarnya tertulis dua kali.
    """
    baris: list[str] = []
    tabel_ditulis: set[int] = set()
    baris_ditulis: set[tuple[int, int]] = set()

    for k in sisip.get(-1, []):
        baris += _kerangka_panel(k)

    for p in paragraf:
        if p.tabel >= 0:
            t = tabel[p.tabel]
            if p.tabel not in tabel_ditulis:
                tabel_ditulis.add(p.tabel)
                baris += _kerangka_tabel(t) if p.tabel in ringkas else [_kepala_tabel(t)]
            if p.tabel not in ringkas and (p.tabel, p.baris) not in baris_ditulis:
                baris_ditulis.add((p.tabel, p.baris))
                baris.append(baris_tabel(t.baris[p.baris]))
        else:
            isi = _baris_paragraf(p)
            if isi:
                sid = id_awal.get(p.index)
                baris.append(f"[{sid}] {isi}" if sid else isi)
        for k in sisip.get(p.index, []):
            baris += _kerangka_panel(k)
    return baris



def _baris_temuan_fase1(temuan: list[Temuan], peta: dict[int, str]) -> list[str]:
    if not temuan:
        return []
    baris = [
        "== TEMUAN PEMERIKSAAN FORMAT YANG SUDAH ADA — jangan diulang ==",
        "Sudah terpasang di naskah sebagai komentar. Kalau menurutmu salah satunya",
        "keliru, sampaikan sebagai keberatan HANYA bila tugasmu memintanya.",
    ]
    for t in sorted(temuan, key=lambda x: x.nomor):
        letak = _letak(peta, t.lokasi.paragraf_index)
        baris.append(f"(T{t.nomor}) [{letak}] pada teks {t.lokasi.teks_asli!r}: {t.catatan}")
    return baris


# ---------------------------------------------------------------------------
# Fakta lampiran — dikumpulkan kode, dinilai model (F2-106)
# ---------------------------------------------------------------------------

_KATA = re.compile(r"[A-Za-z]+")
_LAMPIRAN = re.compile(r"lampiran", re.IGNORECASE)
_NOMOR_PMK = re.compile(r"^NOMOR\s+\S+.*TAHUN\s+\d{4}", re.IGNORECASE)
# Kata sah berakar "lampir" yang terpaut sedikit dari "lampiran".
_AKHIRAN_SAH = ("", "an", "kan", "annya", "kannya")


def _tertukar_sebelah(a: str, b: str) -> bool:
    """`a` sama dengan `b` kecuali dua huruf bersebelahan yang tertukar."""
    if len(a) != len(b) or a == b:
        return False
    beda = [i for i in range(len(a)) if a[i] != b[i]]
    return len(beda) == 2 and beda[1] == beda[0] + 1 and a[beda[0]] == b[beda[1]] and a[beda[1]] == b[beda[0]]


def _mirip_lampiran(kata: str) -> bool:
    """Kata yang kemungkinan salah ketik "lampiran" — SATU huruf meleset.

    Satu huruf hilang, lebih, atau salah ("Lampirn", "Lampiraan", "Lanpiran"),
    atau dua huruf bersebelahan tertukar ("Lamipran"). Dua huruf meleset sudah
    terlalu longgar: "laporan" terpaut dua huruf dan menyeret panggilan
    lampiran pada PMK 104 yang tidak berlampiran sama sekali.
    """
    k = kata.lower()
    if k.startswith("lampir") and k[len("lampir"):] in _AKHIRAN_SAH:
        return False  # lampiran, lampirkan, lampirannya — sah
    if abs(len(k) - len("lampiran")) > 1 or not k.startswith("l"):
        return False
    return _jarak_ubah(k, "lampiran", batas=1) == 1 or _tertukar_sebelah(k, "lampiran")


def fakta_lampiran(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    lampiran: list[Lampiran],
    batas_naskah: int,
    peta: dict[int, str],
) -> tuple[str, int, int]:
    """Fakta tentang lampiran, disusun kode. BUKAN kesimpulan — model yang menilai.

    Mengembalikan teksnya, jumlah paragraf yang menyebut "Lampiran", dan jumlah
    kata mirip "Lampiran".
    """
    baris = ["== FAKTA LAMPIRAN (dikumpulkan kode dari naskah, bukan kesimpulan) =="]

    judul = pohon.cari("judul")
    baris.append(f"Judul PMK di halaman pertama: {judul.teks if judul else '(tidak terbaca)'}")
    nomor = next(
        (_rapi(p.utuh) for p in paragraf[:batas_naskah] if _NOMOR_PMK.match(_rapi(p.utuh))),
        "",
    )
    if nomor:
        baris.append(f"Nomor PMK di halaman pertama: {nomor}")

    baris.append(f"Satuan lampiran yang dikenali kode: {len(lampiran)}")
    for lam in lampiran:
        baris.append(f"- {lam.nama or 'Lampiran'} (paragraf {lam.mulai}–{lam.akhir - 1})")
        baris.append("    baris awal : " + " / ".join(lam.kepala))
        baris.append("    baris akhir: " + " / ".join(lam.penutup))

    sebutan = [
        f"- [{_letak(peta, p.index)}] {_rapi(p.utuh)}"
        for p in paragraf[:batas_naskah]
        if _LAMPIRAN.search(p.utuh)
    ]
    baris.append(f"Paragraf pembukaan/batang tubuh yang menyebut \"Lampiran\": {len(sebutan)}")
    baris += sebutan

    mirip = [
        f"- \"{kata}\" di [{_letak(peta, p.index)}]"
        for p in paragraf
        for kata in _KATA.findall(p.utuh)
        if _mirip_lampiran(kata)
    ]
    baris.append(f"Kata mirip \"Lampiran\" (mungkin salah ketik): {len(mirip) or 'tidak ada'}")
    baris += mirip
    return "\n".join(baris), len(sebutan), len(mirip)


# ---------------------------------------------------------------------------
# Penyusun
# ---------------------------------------------------------------------------


def susun_bahan(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    temuan_fase1: Optional[list[Temuan]] = None,
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    anggaran: int = 100_000,
) -> Bahan:
    """Susun bahan naskah ini. Fungsi murni, tanpa AI, gratis."""
    raksasa = {k.tabel: k for k in (tabel_raksasa or [])}
    lampiran_induk = pohon.cari("lampiran")
    batas = len(paragraf)
    if lampiran_induk is not None:
        batas = next(
            (i for i, p in enumerate(paragraf) if p.index >= lampiran_induk.paragraf_mulai),
            len(paragraf),
        )
    naskah_p, lampiran_p = paragraf[:batas], paragraf[batas:]
    id_awal = id_awal_satuan(pohon)
    peta = peta_satuan(pohon)
    lampiran = baca_lampiran(paragraf, pohon, list(raksasa.values()))

    kepala = [
        "== NASKAH UTUH ==",
        "Seluruh naskah, urut seperti di Word, satu baris per paragraf. Baris",
        "berawalan [id] membuka satuan yang dikenali parser — id itulah yang kamu",
        "pakai untuk menunjuk tempat. Baris tanpa id tetap bagian naskah.",
        "",
    ]
    sisip_naskah = _sisip_kerangka(raksasa, naskah_p, awal=True)
    naskah = "\n".join(kepala + _baris_naskah(naskah_p, id_awal, sisip_naskah))

    tabel = _kumpulkan_tabel(naskah_p, di_lampiran=False)
    tabel_lampiran = _kumpulkan_tabel(lampiran_p, di_lampiran=True)
    tabel.update(tabel_lampiran)

    fase1 = "\n".join(_baris_temuan_fase1(list(temuan_fase1 or []), peta))

    sisip_lampiran = _sisip_kerangka(raksasa, lampiran_p, awal=False)

    def teks_lampiran(ringkas: set[int]) -> str:
        if not lampiran_p:
            return ""
        return "\n".join(
            ["== LAMPIRAN =="]
            + _baris_lampiran(lampiran_p, id_awal, tabel_lampiran, ringkas, sisip_lampiran)
        )

    ringkas: set[int] = set()
    kerangka: list[str] = []
    t_naskah, t_fase1 = hitung_token(naskah), hitung_token(fase1)
    lampiran_teks = teks_lampiran(ringkas)
    t_lampiran = hitung_token(lampiran_teks)

    if t_naskah + t_lampiran + t_fase1 > anggaran:
        # Kelompok tabel data sejenis, dari yang paling besar. Diringkas satu
        # kelompok demi satu kelompok sampai bahan masuk anggaran — teks dan
        # tabel kecil tidak pernah disentuh.
        kelompok: dict[tuple, list[TabelNaskah]] = {}
        for t in tabel_lampiran.values():
            if t.data:
                kelompok.setdefault(t.kunci_sejenis(), []).append(t)
        ukuran = {
            kunci: sum(hitung_token("\n".join(baris_tabel(b) for b in t.baris)) for t in isi)
            for kunci, isi in kelompok.items()
        }
        for kunci in sorted(kelompok, key=lambda k: ukuran[k], reverse=True):
            isi = kelompok[kunci]
            ringkas |= {t.nomor for t in isi}
            nomor = ", ".join(str(t.nomor) for t in isi)
            kerangka.append(
                f"{len(isi)} tabel sejenis (nomor {nomor}; {isi[0].kolom} kolom, "
                f"±{angka(ukuran[kunci])} token) jadi kerangka"
            )
            lampiran_teks = teks_lampiran(ringkas)
            t_lampiran = hitung_token(lampiran_teks)
            if t_naskah + t_lampiran + t_fase1 <= anggaran:
                break

    bagian = [naskah]
    if lampiran_teks:
        bagian.append(lampiran_teks)
    if fase1:
        bagian.append(fase1)
    teks = "\n\n".join(bagian)
    fakta, disebut, mirip = fakta_lampiran(paragraf, pohon, lampiran, batas, peta)

    return Bahan(
        teks=teks,
        token={
            "naskah": t_naskah,
            "lampiran": t_lampiran,
            "temuan fase 1": t_fase1,
            "total": hitung_token(teks),
        },
        cara_hitung=cara_hitung(),
        anggaran=anggaran,
        kerangka=kerangka,
        tabel=tabel,
        tabel_raksasa=raksasa,
        fakta_lampiran=fakta,
        lampiran=lampiran,
        paragraf=paragraf,
        id_paragraf=peta,
        lampiran_disebut=disebut,
        lampiran_mirip=mirip,
    )
