"""TAHAP 3 — CARI DUGAAN: model membaca naskah UTUH, fokus menurut jenis pemeriksaan.

Menggantikan Langkah 2 (peta ringkasan per satuan) dan Langkah 3 (menalar di
atas peta) — bug 7, diputuskan penelaah 28 Sep 2026 (C + D). Peta kehilangan
detail, dan pertentangan antarpasal lolos karenanya; kini setiap panggilan
membawa bahan yang SAMA dari tahap 2: naskah utuh berikut lampirannya.

Tiga macam panggilan:

    per kelompok pasal  F2-101–103 — pasal fokus bergilir, beberapa sekali jalan
    lintas naskah       F2-104, F2-105 — satu pertanyaan atas seluruh naskah,
                        sekaligus keberatan atas temuan Fase 1
    lampiran            F2-106 — dinilai dengan parameter tertulis KMK 527
                        butir 120–121, berikut fakta yang dikumpulkan kode

Yang keluar DUGAAN — belum temuan. Tidak satu pun menyentuh naskah sebelum
diuji di tahap 4 dan dibuktikan kutipannya di tahap 5.

TIAP PASAL FOKUS WAJIB DIJAWAB. Pasal yang tidak ditulis model ditanyakan
ulang sekali; yang tetap tidak dijawab dicatat terang-terangan — tidak pernah
diam-diam dianggap bersih. Penelaah berhak tahu pasal mana yang tidak diperiksa.

Yang dipertahankan dari Langkah 2–3 lama: temuan Fase 1 dilampirkan supaya
tidak diulang, keberatan model atasnya ditempel (tidak menghapus), id satuan
dan jenis karangan dibuang, dan batas 80 dugaan per naskah.
"""

from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

from app.bersama import prompt as P
from app.bersama.llm import Blok, Klien, Ongkos, baca_json
from app.models.pekerjaan import Dugaan
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import Temuan
from app.telaah.tahap2_persiapan.bahan import Bahan, hitung_token

JENIS_PASAL = ("makna_ganda", "pemikul", "operasional")
JENIS_LINTAS = ("tabrakan", "cakupan")

# Batas kewajaran. Dugaan sebanyak ini dari satu naskah sudah menandakan model
# sedang mencari-cari, bukan menemukan. Yang kelebihan dipotong menurut urutan
# jawaban, bukan diacak — dan pemotongannya dicatat.
BATAS_DUGAAN = 80

# Beban satu panggilan per kelompok pasal: paling banyak sekian pasal, dan
# teks pasal-pasalnya paling banyak sekian token. Pasal tidak pernah dibelah.
PASAL_PER_FOKUS = 6
TOKEN_PER_FOKUS = 4000

Lapor = Callable[[str, int, int], None]


@dataclass
class Panggilan:
    """Satu panggilan tahap 3 yang direncanakan, persis seperti akan dikirim."""

    judul: str
    macam: str  # "pasal" | "lintas" | "lampiran"
    peran: str
    pesan: str
    fokus: list[str] = field(default_factory=list)
    jenis: list[str] = field(default_factory=list)

    @property
    def kunci(self) -> str:
        """Sidik pesan — jawaban tersimpan hanya dipakai ulang untuk pesan yang SAMA."""
        return hashlib.sha1((self.peran + "\n" + self.pesan).encode("utf-8")).hexdigest()


@dataclass
class HasilCari:
    dugaan: list[Dugaan] = field(default_factory=list)
    # (judul, blok percakapan) tiap panggilan, urut — untuk Ekspor Tahap 3.
    rekaman: list[tuple[str, list[Blok]]] = field(default_factory=list)
    tidak_dijawab: list[str] = field(default_factory=list)
    catatan: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Rencana panggilan
# ---------------------------------------------------------------------------


def kelompok_fokus(
    pohon: PohonSatuan, per_fokus: int = PASAL_PER_FOKUS, batas_token: int = TOKEN_PER_FOKUS
) -> list[list[str]]:
    """Pasal dikelompokkan untuk difokuskan bergilir. Satu pasal tidak pernah dibelah."""
    per_fokus = max(1, per_fokus)
    hasil: list[list[str]] = []
    kini: list[str] = []
    token = 0
    for p in pohon.semua(JenisSatuan.PASAL):
        t = hitung_token(pohon.teks_lengkap(p.id, berlabel=True))
        if kini and (len(kini) >= per_fokus or token + t > batas_token):
            hasil.append(kini)
            kini, token = [], 0
        kini.append(p.id)
        token += t
    if kini:
        hasil.append(kini)
    return hasil


def _kode(jenis: list[str]) -> str:
    return " | ".join(f'"{j}"' for j in jenis)


def _nama_pasal(pid: str) -> str:
    return "Pasal " + pid.split("-", 1)[1].upper() if pid.startswith("pasal-") else pid


def panggilan_pasal(bahan: Bahan, fokus: list[str], jenis: list[str], judul: str) -> Panggilan:
    tugas = P.isi(
        P.TAHAP3_PER_PASAL,
        jenis=P.daftar_jenis(jenis),
        fokus=", ".join(fokus),
        kode=_kode(jenis),
    )
    return Panggilan(
        judul=judul,
        macam="pasal",
        peran=P.PERAN,
        pesan=P.susun_dengan_bahan(bahan.teks, tugas),
        fokus=list(fokus),
        jenis=list(jenis),
    )


def panggilan_lintas(bahan: Bahan, jenis: list[str], ada_fase1: bool) -> Panggilan:
    tugas = P.isi(
        P.TAHAP3_LINTAS,
        jenis=P.daftar_jenis(jenis) if jenis else P.TAHAP3_TANPA_JENIS,
        keberatan=P.TAHAP3_KEBERATAN_ADA if ada_fase1 else P.TAHAP3_KEBERATAN_TIDAK,
        kode=_kode(jenis) if jenis else '""',
    )
    return Panggilan(
        judul="TAHAP 3 · LINTAS NASKAH",
        macam="lintas",
        peran=P.PERAN,
        pesan=P.susun_dengan_bahan(bahan.teks, tugas),
        jenis=list(jenis),
    )


def panggilan_lampiran(bahan: Bahan) -> Panggilan:
    tugas = P.isi(P.TAHAP3_LAMPIRAN, fakta=bahan.fakta_lampiran)
    return Panggilan(
        judul="TAHAP 3 · LAMPIRAN",
        macam="lampiran",
        peran=P.PERAN,
        pesan=P.susun_dengan_bahan(bahan.teks, tugas),
        jenis=["lampiran"],
    )


def rencana(
    pohon: PohonSatuan,
    bahan: Bahan,
    aturan_aktif: Optional[set[str]] = None,
    ada_fase1: bool = False,
    per_fokus: int = PASAL_PER_FOKUS,
    batas_token: int = TOKEN_PER_FOKUS,
) -> list[Panggilan]:
    """Seluruh panggilan tahap 3 untuk naskah ini, urut. Fungsi murni.

    Hanya jenis yang dinyalakan penelaah yang ditanyakan — jenis yang mati
    tidak dibayar sama sekali, bukan sekadar dibuang jawabannya.
    """

    def nyala(jenis: str) -> bool:
        return aturan_aktif is None or P.JENIS[jenis][0] in aturan_aktif

    hasil: list[Panggilan] = []
    jenis_pasal = [j for j in JENIS_PASAL if nyala(j)]
    if jenis_pasal:
        kelompok = kelompok_fokus(pohon, per_fokus, batas_token)
        for ke, fokus in enumerate(kelompok, start=1):
            rentang = _nama_pasal(fokus[0]) + (
                f" s.d. {_nama_pasal(fokus[-1])}" if len(fokus) > 1 else ""
            )
            judul = f"TAHAP 3 · PASAL {ke}/{len(kelompok)} ({rentang})"
            hasil.append(panggilan_pasal(bahan, fokus, jenis_pasal, judul))

    jenis_lintas = [j for j in JENIS_LINTAS if nyala(j)]
    # Keberatan atas temuan Fase 1 ikut di panggilan lintas. Kalau kedua jenis
    # lintas dimatikan tetapi ada temuan Fase 1, panggilannya tetap jalan untuk
    # keberatan saja — fitur itu tidak boleh hilang diam-diam.
    if jenis_lintas or (ada_fase1 and (jenis_pasal or nyala("lampiran"))):
        hasil.append(panggilan_lintas(bahan, jenis_lintas, ada_fase1))

    if nyala("lampiran") and bahan.ada_urusan_lampiran:
        hasil.append(panggilan_lampiran(bahan))
    return hasil


# ---------------------------------------------------------------------------
# Menjalankan
# ---------------------------------------------------------------------------


def _tanya(
    pg: Panggilan,
    klien: Klien,
    ongkos: Ongkos,
    tersimpan: dict[str, str],
    simpan: Optional[Callable[[str, str], None]],
) -> str:
    """Jawaban satu panggilan. Jawaban tersimpan untuk pesan yang SAMA dipakai ulang."""
    if pg.kunci in tersimpan:
        teks = tersimpan[pg.kunci]
    else:
        jawab = klien.tanya(pg.peran, pg.pesan)
        ongkos.catat(jawab)
        teks = jawab.teks
    # Hanya jawaban yang terbaca yang disimpan — yang rusak ditanyakan lagi
    # kalau analisisnya dilanjutkan.
    if simpan is not None and baca_json(teks) is not None:
        simpan(pg.kunci, teks)
    return teks


def _tanya_semua(
    daftar: list[Panggilan],
    klien: Klien,
    ongkos: Ongkos,
    tersimpan: dict[str, str],
    simpan: Optional[Callable[[str, str], None]],
    berbarengan: int,
    lapor: Optional[Lapor],
    sudah: int,
    total: int,
) -> list[str]:
    """Jawaban seluruh panggilan, URUT seperti rencananya walau berjalan berbarengan."""
    hasil: list[Optional[str]] = [None] * len(daftar)
    selesai = sudah

    def satu(i: int) -> tuple[int, str]:
        return i, _tanya(daftar[i], klien, ongkos, tersimpan, simpan)

    if berbarengan <= 1 or len(daftar) <= 1:
        for i in range(len(daftar)):
            _, hasil[i] = satu(i)
            selesai += 1
            if lapor:
                lapor("3 cari dugaan", selesai, total)
    else:
        with ThreadPoolExecutor(max_workers=berbarengan) as pelaksana:
            for i, teks in pelaksana.map(satu, range(len(daftar))):
                hasil[i] = teks
                selesai += 1
                if lapor:
                    lapor("3 cari dugaan", selesai, total)
    return [h or "" for h in hasil]


def _dugaan_sah(
    d: object,
    pg: Panggilan,
    pohon: PohonSatuan,
) -> Optional[Dugaan]:
    """Satu dugaan dari jawaban model, atau None kalau karangan."""
    if not isinstance(d, dict):
        return None
    sid = str(d.get("satuan_id", "")).strip()
    if not pohon.ada(sid):
        return None  # id karangan — satuan itu tidak pernah ada di naskah
    jenis = "lampiran" if pg.macam == "lampiran" else str(d.get("jenis", "")).strip().lower()
    if jenis not in pg.jenis:
        return None
    if pg.macam == "pasal" and not any(sid == f or sid.startswith(f + "-") for f in pg.fokus):
        return None  # di luar pasal fokus — bukan jawaban atas pertanyaan ini
    alasan = str(d.get("alasan", "")).strip()
    if not alasan:
        return None
    lain = str(d.get("satuan_lain", "")).strip() if jenis == "tabrakan" else ""
    if jenis == "tabrakan" and (not pohon.ada(lain) or lain == sid):
        # Tabrakan dengan satuan yang tidak ada, atau dengan dirinya sendiri.
        # Digugurkan seluruhnya: yang diklaim hubungan dua satuan, dan satu
        # sisinya tidak ada.
        return None
    return Dugaan(
        satuan_id=sid,
        satuan_lain=lain,
        jenis=jenis,
        alasan=alasan,
        eksternal=bool(d.get("eksternal", False)),
        asal=pg.judul,
    )


def _serap_keberatan(isi: dict, temuan_fase1: list[Temuan]) -> None:
    """Tempelkan keberatan model ke temuan Fase 1 yang bersangkutan.

    MENEMPEL, TIDAK MENGHAPUS. Temuannya tetap muncul di panel dan di naskah;
    yang bertambah cuma satu baris catatan di komentarnya. Penelaah yang
    memutuskan — ditetapkan 23 Sep 2026.
    """
    daftar = isi.get("keberatan")
    if not isinstance(daftar, list) or not temuan_fase1:
        return
    menurut_nomor = {t.nomor: t for t in temuan_fase1}
    for k in daftar:
        if not isinstance(k, dict):
            continue
        try:
            nomor = int(k.get("nomor"))
        except (TypeError, ValueError):
            continue
        alasan = str(k.get("alasan", "")).strip()
        sasaran = menurut_nomor.get(nomor)
        # Nomor yang tidak ada di daftar yang dikirim berarti model mengarang
        # sasarannya — dilewati, bukan ditebak.
        if sasaran is not None and alasan:
            sasaran.catatan_ai = alasan


def _baca(
    pg: Panggilan,
    teks: str,
    pohon: PohonSatuan,
    ongkos: Ongkos,
    temuan_fase1: list[Temuan],
    hasil: HasilCari,
) -> set[str]:
    """Olah satu jawaban. Kembalikan pasal fokus yang BENAR-BENAR dijawab."""
    isi = baca_json(teks)
    kunci = "hasil" if pg.macam == "pasal" else "dugaan"
    if not isi or not isinstance(isi.get(kunci), list):
        ongkos.catat_gagal()
        hasil.catatan.append(f"{pg.judul}: jawaban model tidak terbaca")
        return set()

    dijawab: set[str] = set()
    if pg.macam == "pasal":
        for entri in isi["hasil"]:
            if not isinstance(entri, dict):
                continue
            pid = str(entri.get("pasal", "")).strip()
            if pid in pg.fokus:
                dijawab.add(pid)
            for d in entri.get("dugaan") or []:
                if (dg := _dugaan_sah(d, pg, pohon)) is not None:
                    hasil.dugaan.append(dg)
    else:
        for d in isi["dugaan"]:
            if (dg := _dugaan_sah(d, pg, pohon)) is not None:
                hasil.dugaan.append(dg)
        if pg.macam == "lintas":
            _serap_keberatan(isi, temuan_fase1)
    return dijawab


def cari_dugaan(
    daftar: list[Panggilan],
    pohon: PohonSatuan,
    bahan: Bahan,
    klien: Klien,
    ongkos: Ongkos,
    temuan_fase1: Optional[list[Temuan]] = None,
    lapor: Optional[Lapor] = None,
    tersimpan: Optional[dict[str, str]] = None,
    simpan: Optional[Callable[[str, str], None]] = None,
    berbarengan: int = 1,
) -> HasilCari:
    """Jalankan rencana tahap 3, lalu tanya ulang pasal fokus yang terlewat."""
    hasil = HasilCari()
    fase1 = list(temuan_fase1 or [])
    tersimpan = tersimpan or {}

    jawaban = _tanya_semua(
        daftar, klien, ongkos, tersimpan, simpan, berbarengan, lapor, 0, len(daftar)
    )
    ulang: list[Panggilan] = []
    for pg, teks in zip(daftar, jawaban):
        hasil.rekaman.append((pg.judul, [("system", pg.peran), ("user", pg.pesan)]))
        dijawab = _baca(pg, teks, pohon, ongkos, fase1, hasil)
        if pg.macam == "pasal":
            terlewat = [f for f in pg.fokus if f not in dijawab]
            if terlewat:
                ulang.append(
                    panggilan_pasal(bahan, terlewat, pg.jenis, pg.judul + " · TANYA ULANG")
                )

    if ulang:
        total = len(daftar) + len(ulang)
        jawaban = _tanya_semua(
            ulang, klien, ongkos, tersimpan, simpan, berbarengan, lapor, len(daftar), total
        )
        for pg, teks in zip(ulang, jawaban):
            hasil.rekaman.append((pg.judul, [("system", pg.peran), ("user", pg.pesan)]))
            dijawab = _baca(pg, teks, pohon, ongkos, fase1, hasil)
            for f in pg.fokus:
                if f not in dijawab:
                    hasil.tidak_dijawab.append(f)
                    hasil.catatan.append(
                        f"{_nama_pasal(f)}: tidak dijawab AI walau sudah ditanyakan ulang — "
                        "pasal ini TIDAK diperiksa F2-101 s.d. F2-103"
                    )

    # Dugaan kembar (mis. dari tanya ulang) cukup sekali.
    unik: dict[tuple[str, str, str], Dugaan] = {}
    for d in hasil.dugaan:
        unik.setdefault((d.satuan_id, d.jenis, d.satuan_lain), d)
    hasil.dugaan = list(unik.values())

    if len(hasil.dugaan) > BATAS_DUGAAN:
        hasil.catatan.append(
            f"batas {BATAS_DUGAAN} dugaan per naskah tercapai — {len(hasil.dugaan) - BATAS_DUGAAN} "
            "dugaan terakhir tidak dipastikan"
        )
        hasil.dugaan = hasil.dugaan[:BATAS_DUGAAN]
    return hasil
