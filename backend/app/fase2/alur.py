"""Orkestrasi Fase 2 dan 3 — tujuh langkah, satu fungsi murni.

Namanya `alur` supaya berkas ini berada di paling atas daftar folder dan
terbaca lebih dulu: inilah peta jalan seluruh fase.

    Langkah 0  tahap0_struktur + tahap0_definisi   kode, gratis
    Langkah 1  tahap1_saring                       kode, gratis
    (mekanis)  mekanis_konsistensi F2-0xx          kode, gratis — lompat ke 5
    Langkah 2  tahap2_baca                         model, per kelompok satuan
    Langkah 3  tahap3_menalar                      model, satu panggilan
    Langkah 4  tahap4_memastikan                   model, per dugaan
    Langkah 6  fase3/tahap6_*                      model + korpus, HANYA untuk
                                                   dugaan eksternal
    Langkah 5  tahap5_verifikasi                   kode, gratis — SELALU TERAKHIR

Urutan 4 → 6 → 5 itu disengaja dan bukan salah tulis. Langkah 5 gerbang
terakhir untuk SEMUA jalur: apa pun yang dihasilkan model, dari langkah mana
pun, tetap harus dibuktikan kutipannya ada di naskah sebelum menyentuh
dokumen penelaah.

FUNGSI MURNI. Masuk daftar paragraf, keluar daftar Temuan. Tanpa Request,
tanpa Response, tanpa state global — bisa dites tanpa menjalankan server, dan
dengan KlienPalsu bisa dites tanpa jaringan sama sekali.
"""

from __future__ import annotations

from typing import Callable, Optional

from app.bersama.llm import Klien, Ongkos, Perapal
from app.bersama.opensearch import Korpus, PencariPeraturan
from app.fase2 import tahap2_baca, tahap3_menalar, tahap4_memastikan, tahap5_verifikasi
from app.fase2.mekanis_konsistensi import jalankan_mekanis
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import saring
from app.fase3 import (
    tahap6_cari,
    tahap6_dasar_hukum,
    tahap6_pastikan_ulang,
    tahap6_rumusan,
)
from app.models.pekerjaan import BarisPeta, CalonTemuan, Dugaan
from app.models.temuan import ParagrafInput, Temuan


class HasilLanjut:
    """Seluruh keluaran satu kali analisis Fase 2/3.

    Yang gugur ikut dibawa pulang. Alat yang cuma bilang "tidak ada temuan"
    tidak bisa dibedakan dari alat yang rusak — dan Fase 2 punya belasan
    tempat untuk diam-diam tidak menghasilkan apa-apa.
    """

    def __init__(self) -> None:
        self.temuan: list[Temuan] = []
        self.peta: list[BarisPeta] = []
        self.dugaan: list[Dugaan] = []
        self.gugur: list[str] = []
        self.ongkos = Ongkos()
        self.tidak_dijalankan: str = ""
        self.satuan_total: int = 0
        self.dilewati: list[tuple[str, str]] = []

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
    per_panggilan: int = 6,
    mulai_nomor: int = 1,
    batas_temuan: int = 50,
    lapor: Optional[Callable[[int, int, list[BarisPeta]], None]] = None,
    peta_tersimpan: Optional[list[BarisPeta]] = None,
    temuan_fase1: Optional[list[Temuan]] = None,
) -> HasilLanjut:
    """Jalankan Fase 2, dan Fase 3 bila korpusnya tersedia.

    `aturan_aktif` datang dari panel Pengaturan — penelaah yang mencentang apa
    yang dianalisis. None berarti semuanya.

    `klien` None berarti jalur penalaran dimatikan seluruhnya; yang berjalan
    tinggal pemeriksaan mekanis F2-0xx. Itu bukan kegagalan, melainkan cara
    memakai Fase 2 tanpa biaya.

    `batas_temuan` BATAS ATAS, bukan target. Model tidak pernah diminta
    mencari sebanyak itu — angka ini cuma memotong kalau kebanyakan, supaya
    panel tidak kebanjiran seperti Law Analyzer di 68/175.
    """
    hasil = HasilLanjut()
    dipakai = None if aturan_aktif is None else {a.strip().upper() for a in aturan_aktif}
    aktif_f3_002 = pencari is not None and (dipakai is None or "F3-002" in dipakai)

    # --- Langkah 0 : struktur ------------------------------------------
    pohon = bangun_pohon(paragraf)

    # --- F3-002 : dasar hukum dicabut ----------------------------------
    #
    # SENGAJA DI ATAS penjaga struktur, dan itu bukan kelalaian urutan.
    # F3-002 cuma membutuhkan bagian Mengingat, dan Mengingat terbaca utuh
    # bahkan pada naskah yang batang tubuhnya gagal diurai: KMK berdiktum,
    # naskah perubahan, dan naskah berpenomoran otomatis Word. Menaruhnya
    # di bawah penjaga berarti membuang pemeriksaan yang sebenarnya masih
    # bisa dijalankan pada ketiga naskah itu.
    #
    # Ditaruh di luar cabang Fase 3 bersama F3-001 karena wataknya memang
    # berbeda: ia menanyai korpus tetapi TIDAK memanggil model, jadi tidak
    # perlu menunggu Langkah 2–4 dan tidak menambah biaya sepeser pun.
    if aktif_f3_002:
        t_dasar, lewat = tahap6_dasar_hukum.cek_dasar_hukum(pohon, paragraf, pencari)
        hasil.temuan += t_dasar
        hasil.gugur += lewat

    if pohon.gagal:
        # Termasuk naskah KMK, yang memakai diktum dan belum didukung Fase 2.
        # Fase 1 tetap berjalan seperti biasa; yang berhenti hanya Fase 2 —
        # dan F3-002 di atas sudah sempat jalan.
        hasil.tidak_dijalankan = pohon.gagal
        hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
        return hasil

    daftar = ambil_definisi(pohon)

    # --- Mekanis : F2-0xx, lompat langsung ke Langkah 5 ------------------
    hasil.temuan += jalankan_mekanis(pohon, daftar, paragraf, aturan_aktif)

    # --- Langkah 1 : menyaring ------------------------------------------
    disaring = saring(pohon)
    hasil.dilewati = [(s.id, alasan) for s, alasan in disaring.dilewati]
    hasil.satuan_total = len(disaring.dibaca)

    if klien is None or not disaring.dibaca:
        hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
        return hasil

    # --- Langkah 2 : membaca per satuan ---------------------------------
    konteks = tahap2_baca.susun_konteks_tetap(pohon, daftar)
    hasil.peta = tahap2_baca.baca_satuan(
        pohon,
        daftar,
        disaring.dibaca,
        klien,
        hasil.ongkos,
        per_panggilan,
        lapor=lapor,
        sudah_ada=peta_tersimpan,
        temuan_fase1=temuan_fase1,
    )

    # --- Langkah 3 : menalar di atas peta -------------------------------
    hasil.dugaan = tahap3_menalar.menalar(hasil.peta, pohon, konteks, klien, hasil.ongkos)

    # --- Langkah 4 : memastikan pada teks utuh --------------------------
    calon = tahap4_memastikan.memastikan(
        hasil.dugaan, pohon, konteks, klien, hasil.ongkos, dipakai
    )

    # --- Langkah 6 : Fase 3, hanya untuk klaim eksternal ----------------
    calon = _cabang_fase3(calon, pohon, korpus, perapal, klien, hasil, dipakai)

    # --- Langkah 5 : gerbang terakhir, SELALU ---------------------------
    # Yang jadi pembanding tumpang tindih: temuan Fase 1 DAN temuan mekanis
    # Fase 2 yang sudah lebih dulu jadi di atas.
    lolos, gugur = tahap5_verifikasi.verifikasi(
        calon,
        pohon,
        daftar,
        paragraf,
        ambang,
        temuan_ada=list(temuan_fase1 or []) + hasil.temuan,
    )
    hasil.temuan += lolos
    hasil.gugur += gugur
    hasil.temuan = _nomori(hasil.temuan, mulai_nomor, batas_temuan)
    return hasil


def _cabang_fase3(
    calon: list[CalonTemuan],
    pohon,
    korpus: Optional[Korpus],
    perapal: Optional[Perapal],
    klien: Klien,
    hasil: HasilLanjut,
    dipakai: Optional[set[str]],
) -> list[CalonTemuan]:
    """Calon eksternal dicarikan pembanding; sisanya lewat apa adanya.

    Calon eksternal yang TIDAK menemukan pembanding berlaku DIGUGURKAN, tidak
    diturunkan jadi temuan internal. Klaimnya memang tentang peraturan lain;
    tanpa peraturan lain, klaim itu tidak punya isi.
    """
    if korpus is None or perapal is None:
        # Fase 3 mati. Calon eksternal dibuang, bukan dipaksakan jadi temuan
        # internal — alasannya dicatat supaya terlihat saat diagnosa.
        sisa = []
        for c in calon:
            if c.eksternal:
                hasil.gugur.append(
                    f"{c.aturan_id} {c.satuan_id}: klaim eksternal, Fase 3 tidak aktif"
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
            # ketika Fase 3 mati seluruhnya.
            hasil.gugur.append(f"{c.aturan_id} {c.satuan_id}: F3-001 tidak dinyalakan")
            continue
        cari = tahap6_cari.cari_pembanding(c, pohon, korpus, perapal)
        if cari.gagal or not cari.pembanding:
            hasil.gugur.append(
                f"F3-001 {c.satuan_id}: tidak ada pembanding berlaku — {cari.ringkas}"
            )
            continue
        naik = tahap6_pastikan_ulang.pastikan_ulang(c, pohon, cari, klien, hasil.ongkos)
        if naik is None:
            hasil.gugur.append(f"F3-001 {c.satuan_id}: tidak terbukti pada pembanding")
            continue
        keluar.append(naik)

    # --- Langkah 6c : mencarikan rumusan pengganti ----------------------
    #
    # SESUDAH F3-001 selesai, supaya calon yang gugur di sana tidak sempat
    # dibayari pencarian. Berlaku untuk calon internal MAUPUN yang baru naik
    # jadi F3-001 — keduanya sama-sama berakhir kuning tanpa usulan.
    if pakai_f3_003:
        hasil.gugur += tahap6_rumusan.lengkapi(
            keluar, pohon, korpus, perapal, klien, hasil.ongkos
        )
    return keluar


def _nomori(temuan: list[Temuan], mulai: int, batas: int) -> list[Temuan]:
    """Urutkan menurut posisi dokumen lalu nomori, mulai dari `mulai`.

    Nomor TIDAK PERNAH dipakai ulang dan TIDAK PERNAH diurutkan ulang sesudah
    terpasang: (T3) sudah tertulis di komentar Word, dan menomori ulang
    membuat komentar itu menunjuk temuan yang berbeda. Fase 2 melanjutkan dari
    nomor terakhir Fase 1 — itulah gunanya `mulai`.
    """
    temuan.sort(key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai))
    if batas > 0:
        temuan = temuan[:batas]
    for urut, t in enumerate(temuan, start=mulai):
        t.nomor = urut
    return temuan
