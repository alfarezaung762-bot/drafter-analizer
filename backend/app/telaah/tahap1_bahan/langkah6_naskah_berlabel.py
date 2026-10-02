"""TAHAP 1 · LANGKAH 6 — naskah berlabel: SELURUH paragraf, bernomor ¶, berlabel satuan.

Inilah bacaan utama agen di tiap putaran isi, sama persis di depan tiap
request supaya potongan harga awalan prompt berlaku. Aturannya warisan
`tahap2_persiapan/bahan.py` (bug 7 dan 11), tidak dilonggarkan:

  - Tidak ada paragraf yang keluar dari bahan. Yang tidak berlabel tetap
    ditulis, mentah (CLAUDE.md butir 14).
  - Label penomoran ikut di depan teks — "(1)", "a.", "1." — dan nomor
    otomatis Word ("Pasal 5") ikut sebagai bagian baris.
  - Pembukaan, batang tubuh, dan penutup SELALU utuh. Hanya TABEL DATA di
    LAMPIRAN yang boleh jadi kerangka, dan hanya bila bahan melewati
    anggaran; isinya tetap bisa dibuka agen dengan `buka_tabel`.
  - Gambar dan rumus disebut terang-terangan tidak terbaca.

Yang baru di Fase 4: tiap baris diawali ¶nomor paragraf Word, supaya agen
bisa menunjuk tempat yang tidak berlabel satuan — "Menimbang", "MEMUTUSKAN:",
baris jabatan — dan gerbang bisa membuktikannya.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from app.models.satuan import PohonSatuan
from app.models.temuan import KerangkaTabel, ParagrafInput
from app.telaah.tahap1_bahan.langkah5_lampiran import baca_lampiran, fakta_lampiran
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import (
    id_awal_satuan,
    pasangan_label,
    peta_satuan,
)
from app.telaah.tahap2_persiapan.bahan import (
    Bahan,
    TabelNaskah,
    _baris_paragraf,
    _kerangka_panel,
    _kumpulkan_tabel,
    _sisip_kerangka,
    angka,
    baris_tabel,
    cara_hitung,
    hitung_token,
)

_CONTOH_KERANGKA = 3


@dataclass
class NaskahBerlabel:
    teks: str
    token: int
    kerangka: list[str] = field(default_factory=list)
    """Keterangan tabel yang diringkas jadi kerangka — kosong bila semua utuh."""
    bahan: Optional[Bahan] = None
    """Bentuk lama untuk alat cari_teks/buka_tabel/jumlah_kolom."""
    baris_tabel_paragraf: dict[tuple[int, int], tuple[int, int]] = field(default_factory=dict)
    """(tabel, baris) → (¶ pertama, ¶ terakhir) — supaya agen bisa menunjuk baris tabel."""
    batas_lampiran: int = -1
    """Index paragraf pertama lampiran; -1 bila tanpa lampiran."""


def _nomor(a: int, b: int) -> str:
    return f"¶{a}" if a == b else f"¶{a}–¶{b}"


def _kerangka_tabel(t: TabelNaskah, rentang: dict[tuple[int, int], tuple[int, int]]) -> list[str]:
    contoh = t.baris[: 1 + _CONTOH_KERANGKA]
    kepala = (
        f"[TABEL {t.nomor} · KERANGKA — {angka(len(t.baris))} baris × {t.kolom} kolom. "
        f"Bahan melewati anggaran, jadi yang ikut hanya judul kolom dan "
        f"{len(contoh) - 1} baris pertama. Isi lengkapnya bisa dibuka dengan alat "
        f"buka_tabel.]"
    )
    keluar = [kepala]
    for i, b in enumerate(contoh):
        r = rentang.get((t.nomor, i))
        keluar.append((_nomor(*r) + " " if r else "") + baris_tabel(b))
    return keluar


def _baris_naskah(
    paragraf: list[ParagrafInput],
    id_awal: dict[int, str],
    sisip: dict[int, list[KerangkaTabel]],
) -> list[str]:
    pasangan = pasangan_label(paragraf)
    dilewati: set[int] = set()
    baris: list[str] = []
    for k in sisip.get(-1, []):
        baris += _kerangka_panel(k)
    for i, p in enumerate(paragraf):
        if i not in dilewati:
            teks = p.utuh
            akhir = p.index
            j = pasangan.get(i)
            if j is not None:
                teks = p.utuh + " " + paragraf[j].utuh
                akhir = paragraf[j].index
                dilewati.add(j)
            isi = _baris_paragraf(p, teks)
            if isi:
                sid = id_awal.get(p.index)
                label = f"[{sid}] " if sid else ""
                tabel = " [tabel]" if p.tabel >= 0 else ""
                baris.append(f"{_nomor(p.index, akhir)}{tabel} {label}{isi}")
        for k in sisip.get(p.index, []):
            baris += _kerangka_panel(k)
    return baris


def _rentang_baris(paragraf: list[ParagrafInput]) -> dict[tuple[int, int], tuple[int, int]]:
    hasil: dict[tuple[int, int], tuple[int, int]] = {}
    for p in paragraf:
        if p.tabel < 0:
            continue
        k = (p.tabel, p.baris)
        a, b = hasil.get(k, (p.index, p.index))
        hasil[k] = (min(a, p.index), max(b, p.index))
    return hasil


def _baris_lampiran(
    paragraf: list[ParagrafInput],
    id_awal: dict[int, str],
    tabel: dict[int, TabelNaskah],
    ringkas: set[int],
    sisip: dict[int, list[KerangkaTabel]],
    rentang: dict[tuple[int, int], tuple[int, int]],
) -> list[str]:
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
                if p.tabel in ringkas:
                    baris += _kerangka_tabel(t, rentang)
                else:
                    baris.append(f"[TABEL {t.nomor} · {len(t.baris)} baris × {t.kolom} kolom]")
            if p.tabel not in ringkas and (p.tabel, p.baris) not in baris_ditulis:
                baris_ditulis.add((p.tabel, p.baris))
                r = rentang.get((p.tabel, p.baris), (p.index, p.index))
                baris.append(f"{_nomor(*r)} {baris_tabel(t.baris[p.baris])}")
        else:
            isi = _baris_paragraf(p)
            if isi:
                sid = id_awal.get(p.index)
                label = f"[{sid}] " if sid else ""
                baris.append(f"¶{p.index} {label}{isi}")
        for k in sisip.get(p.index, []):
            baris += _kerangka_panel(k)
    return baris


KEPALA = [
    "== NASKAH UTUH BERLABEL ==",
    "Seluruh naskah, urut seperti di Word, satu baris per paragraf: ¶nomor paragraf,",
    "[label satuan] bila paragraf itu membuka satuan, lalu teksnya — nomor otomatis",
    "Word (\"Pasal 5\", \"(2)\", \"a.\") ikut di depan teks. Tunjuk tempat dengan label",
    "satuan; untuk paragraf tanpa label, dengan ¶nomornya. [tabel] = isi sel tabel.",
    "",
]


def susun_naskah_berlabel(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    anggaran: int = 100_000,
) -> NaskahBerlabel:
    """Naskah berlabel untuk naskah ini. Fungsi murni, gratis."""
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
    rentang = _rentang_baris(paragraf)

    naskah = "\n".join(
        KEPALA + _baris_naskah(naskah_p, id_awal, _sisip_kerangka(raksasa, naskah_p, awal=True))
    )
    tabel = _kumpulkan_tabel(naskah_p, di_lampiran=False)
    tabel_lampiran = _kumpulkan_tabel(lampiran_p, di_lampiran=True)
    tabel.update(tabel_lampiran)
    sisip_lampiran = _sisip_kerangka(raksasa, lampiran_p, awal=False)

    def teks_lampiran(ringkas: set[int]) -> str:
        if not lampiran_p:
            return ""
        return "\n".join(
            ["== LAMPIRAN =="]
            + _baris_lampiran(lampiran_p, id_awal, tabel_lampiran, ringkas, sisip_lampiran, rentang)
        )

    ringkas: set[int] = set()
    kerangka: list[str] = []
    t_naskah = hitung_token(naskah)
    lampiran_teks = teks_lampiran(ringkas)
    t_lampiran = hitung_token(lampiran_teks)
    if t_naskah + t_lampiran > anggaran:
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
            if t_naskah + t_lampiran <= anggaran:
                break

    teks = "\n\n".join(x for x in (naskah, lampiran_teks) if x)
    lampiran = baca_lampiran(paragraf, pohon, list(raksasa.values())) if pohon.gagal is None else []
    fakta, disebut, mirip = fakta_lampiran(paragraf, pohon, lampiran, batas, peta)
    token = hitung_token(teks)
    bahan = Bahan(
        teks=teks,
        token={"naskah": t_naskah, "lampiran": t_lampiran, "temuan fase 1": 0, "total": token},
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
    return NaskahBerlabel(
        teks=teks,
        token=token,
        kerangka=kerangka,
        bahan=bahan,
        baris_tabel_paragraf=rentang,
        batas_lampiran=paragraf[batas].index if batas < len(paragraf) else -1,
    )
