"""Orkestrasi Fase 2 dan 3 — lima tahap, satu fungsi murni.

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
