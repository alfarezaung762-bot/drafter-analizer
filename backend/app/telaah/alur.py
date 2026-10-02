"""Orkestrasi analisis lanjut — alur lama (lima tahap) dan Fase 4 (agen), satu fungsi masing-masing.

Saklar `.env` FASE2_ALUR memilih yang dijalankan endpoint: `lama` →
`jalankan_lanjut`, `agen` → `jalankan_agen` (di bagian bawah berkas ini).

Namanya `alur` supaya berkas ini berada di paling atas daftar folder dan
terbaca lebih dulu: inilah peta jalan seluruh fase.

    Tahap 1  PARSER         tahap1_parser/     struktur, definisi,       kode, gratis
                                               rujukan, lampiran
    Tahap 2  PERSIAPAN      tahap2_persiapan/  bahan, mekanis_konsistensi kode, gratis
                                               (F2-0xx), dasar_hukum
                                               (F3-002, korpus tanpa AI)
    Tahap 3  CARI DUGAAN    tahap3_cari_dugaan                           model
    Tahap 4  MEMASTIKAN     tahap4_memastikan/ memastikan (+ alat), lalu  model
                                               korpus_* untuk klaim eksternal
    Tahap 5  VERIFIKASI     tahap5_verifikasi                            kode — SELALU TERAKHIR

Tahap 5 gerbang terakhir untuk SEMUA jalur: apa pun yang dihasilkan model,
dari tahap mana pun, tetap harus dibuktikan kutipannya ada di naskah sebelum
menyentuh dokumen penelaah.

Bug 7 (28–29 Sep 2026) menggantikan Langkah 1–3 lama — penyaring, peta
ringkasan per satuan, dan menalar di atas peta — dengan tahap 2–3: model kini
membaca NASKAH UTUH berikut lampirannya, bukan ringkasan.

FUNGSI MURNI. Masuk daftar paragraf, keluar daftar Temuan. Tanpa Request,
tanpa Response, tanpa state global — bisa dites tanpa menjalankan server, dan
dengan KlienPalsu bisa dites tanpa jaringan sama sekali.
"""

from __future__ import annotations

from typing import Callable, Optional

from app.bersama.llm import Blok, Klien, Ongkos, Perapal
from app.bersama.opensearch import Korpus, PencariPeraturan
from app.models.pekerjaan import CalonTemuan, Dugaan
from app.models.temuan import KerangkaTabel, ParagrafInput, Temuan
from app.telaah import tahap3_cari_dugaan, tahap5_verifikasi
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan import dasar_hukum
from app.telaah.tahap2_persiapan.bahan import Bahan, susun_bahan
from app.telaah.tahap2_persiapan.mekanis_konsistensi import jalankan_mekanis
from app.telaah.tahap4_memastikan import (
    korpus_cari,
    korpus_pastikan,
    korpus_rumusan,
    memastikan,
)

Lapor = Callable[[str, int, int], None]


class HasilLanjut:
    """Seluruh keluaran satu kali analisis Fase 2/3.

    Yang gugur ikut dibawa pulang. Alat yang cuma bilang "tidak ada temuan"
    tidak bisa dibedakan dari alat yang rusak — dan Fase 2 punya belasan
    tempat untuk diam-diam tidak menghasilkan apa-apa.
    """

    def __init__(self) -> None:
        self.temuan: list[Temuan] = []
        self.dugaan: list[Dugaan] = []
        self.gugur: list[str] = []
        self.ongkos = Ongkos()
        self.tidak_dijalankan: str = ""
        self.bahan: Optional[Bahan] = None
        # Percakapan tiap panggilan, urut, apa adanya — untuk Ekspor Tahap 3
        # dan 4. None = tahapnya tidak sampai berjalan; [] = berjalan tanpa
        # mengirim apa pun.
        self.pesan_tahap3: Optional[list[tuple[str, list[Blok]]]] = None
        self.pesan_tahap4: Optional[list[tuple[str, list[Blok]]]] = None
        # Nasib tiap dugaan dan catatan tahap 3–4 — untuk Ekspor Tahap 5.
        self.jejak_tahap3: list[str] = []
        self.jejak_tahap4: list[str] = []
        self.tidak_dijawab: list[str] = []

    @property
    def berjalan(self) -> bool:
        return not self.tidak_dijalankan


def jalankan_lanjut(
    paragraf: list[ParagrafInput],
    klien: Optional[Klien] = None,
    korpus: Optional[Korpus] = None,
    perapal: Optional[Perapal] = None,
    pencari: Optional[PencariPeraturan] = None,
    aturan_aktif: Optional[list[str]] = None,
    ambang: float = 0.7,
    mulai_nomor: int = 1,
    batas_temuan: int = 50,
    lapor: Optional[Lapor] = None,
    jawaban_tersimpan: Optional[dict[str, str]] = None,
    simpan_jawaban: Optional[Callable[[str, str], None]] = None,
    temuan_fase1: Optional[list[Temuan]] = None,
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    anggaran: int = 100_000,
    pasal_per_fokus: int = tahap3_cari_dugaan.PASAL_PER_FOKUS,
    berbarengan: int = 1,
) -> HasilLanjut:
    """Jalankan Fase 2, dan Fase 3 bila korpusnya tersedia.

    `aturan_aktif` datang dari panel Pengaturan — penelaah yang mencentang apa
    yang dianalisis. None berarti semuanya.

    `klien` None berarti jalur AI dimatikan seluruhnya; yang berjalan tinggal
    pemeriksaan kode F2-0xx. Itu bukan kegagalan, melainkan cara memakai
    Fase 2 tanpa biaya.

    `jawaban_tersimpan` jawaban tahap 3 dari analisis sebelumnya, menurut
    sidik pesannya. Pesan yang SAMA tidak dibayar dua kali sesudah backend
    restart; `simpan_jawaban` menyimpan jawaban baru untuk keperluan itu.

    `batas_temuan` BATAS ATAS, bukan target. Model tidak pernah diminta
    mencari sebanyak itu — angka ini cuma memotong kalau kebanyakan.
    """
    hasil = HasilLanjut()
    dipakai = None if aturan_aktif is None else {a.strip().upper() for a in aturan_aktif}
    aktif_f3_002 = pencari is not None and (dipakai is None or "F3-002" in dipakai)

    # --- Tahap 1 : parser ----------------------------------------------
    pohon = bangun_pohon(paragraf)

    # --- F3-002 : dasar hukum dicabut ----------------------------------
    #
    # SENGAJA DI ATAS penjaga struktur. F3-002 cuma membutuhkan bagian
    # Mengingat, dan Mengingat terbaca utuh bahkan pada naskah yang batang
    # tubuhnya gagal diurai. Ia menanyai korpus tetapi TIDAK memanggil model,
    # jadi tidak menambah biaya sepeser pun.
    if aktif_f3_002:
        t_dasar, lewat = dasar_hukum.cek_dasar_hukum(pohon, paragraf, pencari)
        hasil.temuan += t_dasar
        hasil.gugur += lewat

    if pohon.gagal:
        # Termasuk naskah KMK dan naskah perubahan. Fase 1 tetap berjalan
        # seperti biasa; yang berhenti hanya Fase 2 — dan F3-002 sudah jalan.
        hasil.tidak_dijalankan = pohon.gagal
        hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
        return hasil

    daftar = ambil_definisi(pohon)

    # --- Tahap 2 : persiapan — pemeriksaan kode, lalu bahan untuk model ---
    hasil.temuan += jalankan_mekanis(pohon, daftar, paragraf, aturan_aktif)
    fase1 = list(temuan_fase1 or [])
    bahan = susun_bahan(paragraf, pohon, fase1, tabel_raksasa, anggaran)
    hasil.bahan = bahan

    if klien is None:
        hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
        return hasil

    # --- Tahap 3 : cari dugaan pada naskah utuh --------------------------
    rencana = tahap3_cari_dugaan.rencana(
        pohon, bahan, dipakai, ada_fase1=bool(fase1), per_fokus=pasal_per_fokus
    )
    cari = tahap3_cari_dugaan.cari_dugaan(
        rencana,
        pohon,
        bahan,
        klien,
        hasil.ongkos,
        temuan_fase1=fase1,
        lapor=lapor,
        tersimpan=jawaban_tersimpan,
        simpan=simpan_jawaban,
        berbarengan=berbarengan,
    )
    hasil.dugaan = cari.dugaan
    hasil.pesan_tahap3 = cari.rekaman
    hasil.jejak_tahap3 = cari.catatan
    hasil.tidak_dijawab = cari.tidak_dijawab

    # --- Tahap 4 : memastikan tiap dugaan, lalu korpus --------------------
    pastikan = memastikan.memastikan(
        hasil.dugaan, pohon, bahan, klien, hasil.ongkos, dipakai, lapor, berbarengan
    )
    hasil.pesan_tahap4 = pastikan.rekaman
    hasil.jejak_tahap4 = pastikan.jejak
    calon = _cabang_korpus(pastikan.calon, pohon, korpus, perapal, klien, hasil, dipakai)

    # --- Tahap 5 : gerbang terakhir, SELALU --------------------------------
    # Yang jadi pembanding tumpang tindih: temuan Fase 1 DAN temuan kode
    # Fase 2 yang sudah lebih dulu jadi di atas.
    contoh_raksasa = [
        " | ".join(sel) for k in (tabel_raksasa or []) for sel in k.contoh
    ]
    lolos, gugur = tahap5_verifikasi.verifikasi(
        calon,
        pohon,
        daftar,
        paragraf,
        ambang,
        temuan_ada=fase1 + hasil.temuan,
        teks_tambahan=contoh_raksasa,
    )
    hasil.temuan += lolos
    hasil.gugur += gugur
    hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
    return hasil


def _cabang_korpus(
    calon: list[CalonTemuan],
    pohon,
    korpus: Optional[Korpus],
    perapal: Optional[Perapal],
    klien: Klien,
    hasil: HasilLanjut,
    dipakai: Optional[set[str]],
) -> list[CalonTemuan]:
    """Calon eksternal dicarikan pembanding di korpus; sisanya lewat apa adanya.

    Calon eksternal yang TIDAK menemukan pembanding berlaku DIGUGURKAN, tidak
    diturunkan jadi temuan internal. Klaimnya memang tentang peraturan lain;
    tanpa peraturan lain, klaim itu tidak punya isi. "Tidak ketemu di
    OpenSearch" tidak pernah jadi temuan.
    """
    if korpus is None or perapal is None:
        # Korpus mati. Calon eksternal dibuang, bukan dipaksakan jadi temuan
        # internal — alasannya dicatat supaya terlihat saat diagnosa.
        sisa = []
        for c in calon:
            if c.eksternal:
                hasil.gugur.append(
                    f"{c.aturan_id} {c.satuan_id}: klaim eksternal, korpus (Fase 3) tidak aktif"
                )
            else:
                sisa.append(c)
        return sisa

    pakai_f3_001 = dipakai is None or "F3-001" in dipakai
    pakai_f3_003 = dipakai is None or "F3-003" in dipakai

    if not pakai_f3_001 and not pakai_f3_003:
        return [c for c in calon if not c.eksternal]

    keluar: list[CalonTemuan] = []
    for c in calon:
        if not c.eksternal:
            keluar.append(c)
            continue
        if not pakai_f3_001:
            # Klaim eksternal tanpa F3-001 tidak punya isi, persis seperti
            # ketika korpus mati seluruhnya.
            hasil.gugur.append(f"{c.aturan_id} {c.satuan_id}: F3-001 tidak dinyalakan")
            continue
        cari = korpus_cari.cari_pembanding(c, pohon, korpus, perapal)
        if cari.gagal or not cari.pembanding:
            hasil.gugur.append(
                f"F3-001 {c.satuan_id}: tidak ada pembanding berlaku — {cari.ringkas}"
            )
            continue
        naik = korpus_pastikan.pastikan_ulang(c, pohon, cari, klien, hasil.ongkos)
        if naik is None:
            hasil.gugur.append(f"F3-001 {c.satuan_id}: tidak terbukti pada pembanding")
            continue
        keluar.append(naik)

    # Rumusan pengganti dari peraturan berlaku (F3-003) — SESUDAH F3-001,
    # supaya calon yang gugur di sana tidak sempat dibayari pencarian.
    if pakai_f3_003:
        hasil.gugur += korpus_rumusan.lengkapi(
            keluar, pohon, korpus, perapal, klien, hasil.ongkos
        )
    return keluar


def _nomori(temuan: list[Temuan], mulai: int, batas: int) -> list[Temuan]:
    """Urutkan menurut posisi dokumen lalu nomori, mulai dari `mulai`.

    Nomor TIDAK PERNAH dipakai ulang dan TIDAK PERNAH diurutkan ulang sesudah
    terpasang: (T3) sudah tertulis di komentar Word, dan menomori ulang
    membuat komentar itu menunjuk temuan yang berbeda. Fase 2 melanjutkan dari
    nomor terakhir Fase 1 — itulah gunanya `mulai`. Temuan yang letaknya tidak
    pasti (sesudah tabel raksasa) paling akhir.
    """
    temuan.sort(key=tahap5_verifikasi.urutan_dokumen)
    if batas > 0:
        temuan = temuan[:batas]
    for urut, t in enumerate(temuan, start=mulai):
        t.nomor = urut
    return temuan


# ===========================================================================
# FASE 4 — agen penuh dengan skills (di balik saklar FASE2_ALUR = agen)
# ===========================================================================
#
#   Tahap 1  BAHAN        tahap1_bahan/      1 panggilan AI (label) + kode
#   Tahap 2  AGEN         tahap2_agen/       AI — putaran per kelompok pasal,
#                                            lintas naskah, lampiran, format;
#                                            penilai kedua per putaran
#   Tahap 3  GERBANG      tahap3_verifikasi  kode — SATU-SATUNYA tempat
#                                            temuan lahir
#
# Alur lama di atas tetap utuh sampai agen terbukti (rancangan Fase 4 bagian
# 4 langkah 8). Di Fase 4 seluruh pemeriksaan dikerjakan agen; kode hanya
# membaca naskah dan membuktikan klaim agen.

import threading as _threading  # noqa: E402
from dataclasses import dataclass as _dataclass, field as _field  # noqa: E402

from app.models.pekerjaan import CalonAgen as _CalonAgen  # noqa: E402
from app.models.temuan import FormatHalaman as _FormatHalaman, JenisDokumen as _JenisDokumen  # noqa: E402
from app.telaah import tahap3_verifikasi as _gerbang  # noqa: E402
from app.telaah.tahap1_bahan.langkah1_label_ai import UsulanLabel, minta_label  # noqa: E402
from app.telaah.tahap1_bahan.langkah2_bukti_label import PetaLetak, peta_letak  # noqa: E402
from app.telaah.tahap1_bahan.langkah3_istilah_pasal1 import ambil_definisi as _ambil_definisi  # noqa: E402
from app.telaah.tahap1_bahan.langkah4_teks_dirujuk import blok_dirujuk_pasal  # noqa: E402
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import NaskahBerlabel, susun_naskah_berlabel  # noqa: E402
from app.telaah.tahap1_bahan.langkah7_naskah_berformat import NaskahBerformat, susun_naskah_berformat  # noqa: E402
from app.telaah.tahap1_bahan.langkah8_bahan_korpus import susun_bahan_korpus  # noqa: E402
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import (  # noqa: E402
    id_awal_satuan as _id_awal,
    peta_satuan as _peta_satuan,
)
from app.telaah.tahap2_agen.langkah1_pilih_analisis import (  # noqa: E402
    JENIS_PANEL,
    Katalog,
    Pilihan,
    Prasyarat,
    muat_katalog,
    pilih,
)
from app.telaah.tahap2_agen.langkah2_bagi_putaran import (  # noqa: E402
    PASAL_PER_FOKUS,
    TOKEN_PER_FOKUS,
    Pembagian,
    bagi_putaran,
)
from app.telaah.tahap2_agen.langkah3_alat_agen import BahanAlat  # noqa: E402
from app.telaah.tahap2_agen.langkah3_jalankan_agen import HasilPutaran, Setelan, jalankan_semua  # noqa: E402
from app.telaah.tahap2_agen.langkah4_penilai_kedua import HasilPenilai, nilai_calon  # noqa: E402
from app.telaah.tahap2_agen.peran_agen_dan_penilai import tugas_putaran  # noqa: E402

LaporPutaran = Callable[[str, dict], None]


@_dataclass
class HasilAgen:
    """Seluruh keluaran satu analisis Fase 4 — yang tampil, dan yang gugur."""

    temuan: list[Temuan] = _field(default_factory=list)
    gugur: list[str] = _field(default_factory=list)
    peringatan: list[str] = _field(default_factory=list)
    ongkos: Ongkos = _field(default_factory=Ongkos)
    tidak_dijalankan: str = ""
    dibatalkan: bool = False
    label: Optional[UsulanLabel] = None
    peta: Optional[PetaLetak] = None
    berlabel: Optional[NaskahBerlabel] = None
    berformat: Optional[NaskahBerformat] = None
    bahan_korpus: str = ""
    pilihan: Optional[Pilihan] = None
    pembagian: Optional[Pembagian] = None
    putaran: list[HasilPutaran] = _field(default_factory=list)
    penilai: dict[str, HasilPenilai] = _field(default_factory=dict)
    pesan_awal: dict[str, str] = _field(default_factory=dict)
    calon_disetujui: list[_CalonAgen] = _field(default_factory=list)
    calon_ditolak: list[_CalonAgen] = _field(default_factory=list)
    kunci_jawaban: list[str] = _field(default_factory=list)

    @property
    def berjalan(self) -> bool:
        return not self.tidak_dijalankan


def _blok_temuan_lama(lama: list[Temuan]) -> str:
    """Periksa ulang: temuan lama beserta keputusan penelaah — dibaca agen."""
    if not lama:
        return ""
    baris = [
        "== TEMUAN ANALISIS SEBELUMNYA — sudah diputuskan penelaah ==",
        "Yang ditolak dan yang diterima JANGAN diajukan ulang. Yang diterima: pastikan",
        "perbaikannya benar di naskah sekarang. Tugas utamamu mencari yang TERLEWAT.",
    ]
    for t in sorted(lama, key=lambda x: x.nomor):
        putusan = {"diterima": "diterima", "ditolak": "ditolak"}.get(t.status.value, "belum diputuskan")
        letak = t.satuan_id or f"¶{t.lokasi.paragraf_index}"
        baris.append(
            f"(T{t.nomor}) {t.aturan_id} [{letak}] {putusan}: {t.lokasi.teks_asli!r} — {t.catatan[:160]}"
        )
    return "\n".join(baris)


def _kunci_jawaban(
    paragraf: list[ParagrafInput], jenis_panel: str, temuan: list[Temuan], pohon, dikirim: set[str]
) -> list[str]:
    """Kunci jawaban peralihan (rancangan bagian 4 langkah 8): yang ditemukan kode lama.

    Tidak memengaruhi temuan — hanya ditulis di ekspor, supaya terlihat apakah
    agen menemukan SEMUA yang ditemukan pemeriksaan kode yang lama. Hanya
    aturan yang analisisnya DIKIRIM ke agen yang dibandingkan: aturan yang
    tidak dijalankan bukan "terlewat".
    """
    from app.rules.format_baku import jalankan_semua as _fase1

    try:
        jenis = _JenisDokumen(jenis_panel)
    except ValueError:
        return ["kunci jawaban tidak disusun: jenis naskah tidak dikenal"]
    lama = _fase1(paragraf, jenis)
    if pohon.gagal is None:
        lama += jalankan_mekanis(pohon, ambil_definisi(pohon), paragraf)
    lama = [t for t in lama if t.aturan_id in dikirim]
    keluar: list[str] = []
    for t in lama:
        a = _gerbang._rapat(t.lokasi.teks_asli)
        kena = [
            x
            for x in temuan
            if x.lokasi.paragraf_index == t.lokasi.paragraf_index
            and (
                x.aturan_id == t.aturan_id
                or (a and (_gerbang._rapat(x.lokasi.teks_asli) in a or a in _gerbang._rapat(x.lokasi.teks_asli)))
            )
        ]
        tanda = "KETEMU" if kena else "TERLEWAT"
        keluar.append(
            f"{tanda:8} {t.aturan_id} ¶{t.lokasi.paragraf_index} {t.lokasi.teks_asli!r} — {t.catatan[:110]}"
            + (("  <- agen: " + ", ".join(f"{x.aturan_id} (T{x.nomor})" for x in kena)) if kena else "")
        )
    return keluar


def jalankan_agen(
    paragraf: list[ParagrafInput],
    jenis_panel: str = "PMK",
    klien=None,
    katalog: Optional[Katalog] = None,
    kode_dipilih: Optional[list[str]] = None,
    korpus: Optional[Korpus] = None,
    perapal: Optional[Perapal] = None,
    pencari: Optional[PencariPeraturan] = None,
    halaman: Optional[list[_FormatHalaman]] = None,
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    ambang: float = 0.7,
    mulai_nomor: int = 1,
    temuan_lama: Optional[list[Temuan]] = None,
    tersimpan: Optional[dict[str, str]] = None,
    simpan: Optional[Callable[[str, str], None]] = None,
    batal: Optional[_threading.Event] = None,
    lapor: Optional[Lapor] = None,
    lapor_putaran: Optional[LaporPutaran] = None,
    setelan: Optional[Setelan] = None,
    anggaran: int = 100_000,
    per_fokus: int = PASAL_PER_FOKUS,
    token_per_fokus: int = TOKEN_PER_FOKUS,
    berbarengan: int = 4,
    pakai_label_ai: bool = True,
    kunci_jawaban: bool = True,
) -> HasilAgen:
    """Fase 4: Tahap 1 bahan → Tahap 2 agen → Tahap 3 gerbang. Fungsi murni.

    `klien` None berarti tidak ada AI — tidak ada yang bisa dijalankan, karena
    seluruh pemeriksaan Fase 4 dikerjakan agen. `batal` dinyalakan tombol
    Batal: kode berhenti mengirim request baru; naskah tidak tersentuh.
    """
    hasil = HasilAgen()
    katalog = katalog or muat_katalog()
    jenis = JENIS_PANEL.get(jenis_panel, jenis_panel.lower())
    lama = list(temuan_lama or [])

    if klien is None:
        hasil.tidak_dijalankan = "AI tidak terhubung — seluruh pemeriksaan Fase 4 dikerjakan agen."
        return hasil

    prasyarat = Prasyarat(
        korpus=(korpus is not None and perapal is not None) or pencari is not None,
        bacaan_format=any(p.format is not None for p in paragraf),
    )
    hasil.pilihan = pilih(katalog, jenis, kode_dipilih, prasyarat)
    for kode, alasan in hasil.pilihan.tidak_dikirim:
        hasil.peringatan.append(f"{kode} tidak dijalankan: {alasan}")
    if not hasil.pilihan.dikirim:
        hasil.tidak_dijalankan = "Tidak ada analisis yang bisa dijalankan untuk naskah ini."
        return hasil

    # --- Tahap 1 : bahan -----------------------------------------------------
    if batal is not None and batal.is_set():
        hasil.dibatalkan = True
        hasil.tidak_dijalankan = "Dibatalkan penelaah — naskah tidak disentuh."
        return hasil
    if lapor:
        lapor("1 bahan", 0, 1)
    label = None
    if pakai_label_ai and katalog.ada_label(jenis):
        hasil.label = minta_label(
            paragraf, katalog.skill[f"{jenis}/label"].teks, klien, hasil.ongkos, tersimpan, simpan
        )
        if hasil.label.terbaca:
            if "perubahan" in hasil.label.jenis:
                hasil.tidak_dijalankan = (
                    "Naskah ini peraturan PERUBAHAN menurut pembaca label — skill PMK perubahan "
                    "belum ada, jadi Fase 4 belum memeriksanya. Skop sekarang PMK biasa."
                )
                return hasil
            label = hasil.label.label
    if batal is not None and batal.is_set():
        hasil.dibatalkan = True
        hasil.tidak_dijalankan = "Dibatalkan penelaah — naskah tidak disentuh."
        return hasil
    hasil.peta = peta_letak(label, paragraf, pmk_biasa=(jenis == "pmk-standar"))
    if hasil.label is not None and not hasil.label.terbaca:
        hasil.peta.catatan.insert(0, "jawaban label AI tidak terbaca — peta letak dari parser cadangan")
    pohon = hasil.peta.pohon
    if pohon.gagal is not None:
        hasil.tidak_dijalankan = pohon.gagal
        return hasil

    definisi = _ambil_definisi(pohon)
    hasil.berlabel = susun_naskah_berlabel(paragraf, pohon, tabel_raksasa, anggaran)
    if any(a.format for a in hasil.pilihan.dikirim):
        hasil.berformat = susun_naskah_berformat(paragraf, pohon, halaman)
    if any("bahan korpus" in a.butuh for a in hasil.pilihan.dikirim):
        hasil.bahan_korpus = susun_bahan_korpus(pohon, paragraf, pencari)
    bahan_alat = BahanAlat(
        paragraf=paragraf,
        pohon=pohon,
        peta=_peta_satuan(pohon),
        id_awal=_id_awal(pohon),
        berlabel=hasil.berlabel,
        anotasi_format=hasil.berformat.anotasi if hasil.berformat else {},
        katalog=katalog,
        korpus=korpus,
        perapal=perapal,
        pencari=pencari,
    )
    if lapor:
        lapor("1 bahan", 1, 1)

    # --- Tahap 2 : agen ------------------------------------------------------
    bahan_lama = hasil.berlabel.bahan
    hasil.pembagian = bagi_putaran(
        hasil.pilihan.dikirim,
        pohon,
        bool(bahan_lama and bahan_lama.ada_urusan_lampiran),
        per_fokus,
        token_per_fokus,
    )
    for kode, alasan in hasil.pembagian.tidak_dijalankan:
        hasil.peringatan.append(f"{kode} tidak dijalankan: {alasan}")
    blok_lama = _blok_temuan_lama(lama)
    skill = [(s.nama, s.deskripsi) for s in katalog.skill_jenis(jenis)]
    naskah_putaran: dict[str, str] = {}
    for p in hasil.pembagian.putaran:
        naskah = hasil.berformat.teks if (p.berformat and hasil.berformat) else hasil.berlabel.teks
        naskah_putaran[p.kode] = naskah
        tambahan: list[str] = []
        if p.fokus:
            tambahan.append("\n".join(blok_dirujuk_pasal(pohon, p.fokus)))
        if p.lingkup == "lampiran" and bahan_lama is not None:
            tambahan.append(bahan_lama.fakta_lampiran)
        if blok_lama:
            tambahan.append(blok_lama)
        korpus_putaran = any("korpus" in a.butuh for a in p.analisis) and prasyarat.korpus
        bagian = [naskah]
        if hasil.bahan_korpus and any("bahan korpus" in a.butuh for a in p.analisis):
            bagian.append(hasil.bahan_korpus)
        bagian.append(
            tugas_putaran(p.judul, [a.teks for a in p.analisis], p.fokus, tambahan, skill, korpus_putaran)
        )
        hasil.pesan_awal[p.kode] = "\n\n---\n\n".join(bagian)

    kunci = _threading.Lock()

    def kabar(kode: str, keadaan: dict) -> None:
        if lapor_putaran:
            lapor_putaran(kode, keadaan)

    def sesudah(h: HasilPutaran) -> None:
        """Penilai kedua, begitu putaran itu selesai — tidak menunggu putaran lain."""
        if h.berakhir.startswith(("dibatalkan", "gagal")) or not h.catatan.calon:
            return
        if batal is not None and batal.is_set():
            return
        kabar(h.putaran.kode, {"judul": h.putaran.judul, "keadaan": "menilai", "langkah": len(h.langkah), "calon": len(h.catatan.calon)})
        n = nilai_calon(
            h.catatan.calon, h.putaran, naskah_putaran[h.putaran.kode], klien, hasil.ongkos, tersimpan, simpan
        )
        h.penilai = n
        with kunci:
            hasil.penilai[h.putaran.kode] = n

    for p in hasil.pembagian.putaran:
        kabar(p.kode, {"judul": p.judul, "keadaan": "menunggu", "langkah": 0, "calon": 0})
    if lapor:
        lapor("2 agen", 0, len(hasil.pembagian.putaran))
    hasil.putaran = jalankan_semua(
        hasil.pembagian.putaran,
        hasil.pesan_awal,
        {p.kode: bahan_alat for p in hasil.pembagian.putaran},
        klien,
        hasil.ongkos,
        tersimpan,
        simpan,
        batal,
        kabar,
        setelan,
        berbarengan,
        sesudah,
    )
    for h in hasil.putaran:
        akhir = h.berakhir
        kabar(h.putaran.kode, {
            "judul": h.putaran.judul,
            "keadaan": "selesai" if akhir in ("selesai", "ditagih") else akhir.split(":")[0],
            "langkah": len(h.langkah),
            "calon": len(h.catatan.calon),
        })
        if akhir.startswith("macet"):
            hasil.peringatan.append(f"{h.putaran.judul}: analisis macet — {akhir[7:]}")
        elif akhir.startswith("gagal"):
            hasil.peringatan.append(f"{h.putaran.judul}: gagal — {akhir[7:]}")
        if h.tidak_diperiksa:
            daftar = ", ".join(f"{p} × {k}" for p, k in h.tidak_diperiksa[:8])
            lebih = f" (+{len(h.tidak_diperiksa) - 8})" if len(h.tidak_diperiksa) > 8 else ""
            hasil.peringatan.append(f"{h.putaran.judul}: tidak diperiksa — {daftar}{lebih}")
    if batal is not None and batal.is_set():
        hasil.dibatalkan = True
        hasil.tidak_dijalankan = "Dibatalkan penelaah — naskah tidak disentuh."
        return hasil

    # --- Tahap 3 : gerbang ---------------------------------------------------
    if lapor:
        lapor("3 gerbang", 0, 1)
    setuju: list[_CalonAgen] = []
    for h in hasil.putaran:
        for c in h.catatan.calon:
            if c.penilai == "setuju":
                setuju.append(c)
                continue
            if not c.penilai:
                c.penilai = "tidak dinilai"
                c.alasan_penilai = f"putaran berakhir {h.berakhir or 'tanpa selesai'} sebelum penilai kedua"
            hasil.calon_ditolak.append(c)
            hasil.gugur.append(
                f"{c.putaran} {c.nomor} {c.analisis} [{c.letak}]: DITOLAK PENILAI — {c.alasan_penilai}"
            )
    hasil.calon_disetujui = setuju
    contoh_raksasa = [" | ".join(sel) for k in (tabel_raksasa or []) for sel in k.contoh]
    g = _gerbang.BahanGerbang(
        bahan=bahan_alat,
        definisi=definisi,
        katalog=katalog,
        catatan={h.putaran.judul: h.catatan for h in hasil.putaran},
        teks_tambahan=contoh_raksasa,
        ambang=ambang,
        temuan_lama=lama,
    )
    lolos, gugur = _gerbang.verifikasi(setuju, g)
    hasil.gugur += gugur
    lolos.sort(key=tahap5_verifikasi.urutan_dokumen)
    for urut, t in enumerate(lolos, start=mulai_nomor):
        t.nomor = urut
    hasil.temuan = lolos
    if kunci_jawaban:
        hasil.kunci_jawaban = _kunci_jawaban(
            paragraf, jenis_panel, lolos, bangun_pohon(paragraf), {a.kode for a in hasil.pilihan.dikirim}
        )
    if lapor:
        lapor("3 gerbang", 1, 1)
    return hasil
