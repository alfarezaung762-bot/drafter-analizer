"""LANGKAH 6c — mencari RUMUSAN dari peraturan yang masih berlaku.

Berbeda maksud dari dua tetangganya di folder ini, dan bedanya menentukan:

    tahap6_cari + tahap6_pastikan_ulang   mencari PERTENTANGAN  (F3-001)
    tahap6_dasar_hukum                    memeriksa STATUS      (F3-002)
    tahap6_rumusan (berkas ini)           mencari CONTOH RUMUSAN (F3-003)

Ada karena penetapan penelaah 23 Sep 2026:

    "kalo memang alat yakin itu salah rasanya aneh jika tidak memberikan saran
     perbaikan (karna itulah gunanya tahap 6 opensearch)"

Sebelum ini, temuan penalaran hampir selalu berakhir kuning: model boleh
menilai sebuah rumusan bermasalah, tetapi penilaiannya sendiri bukan bukti,
jadi usulannya tidak pernah boleh disisipkan. Yang berubah di sini bukan
syarat buktinya, melainkan dari mana bukti penggantinya boleh datang —
rumusan yang dipakai peraturan yang MASIH BERLAKU adalah bukti yang bisa
ditunjuk, dan sumbernya disebut di komentar supaya penelaah memeriksanya
sendiri.

=========================================================================
TIDAK SATU PUN PENJAGA DILEWATI
=========================================================================

Yang keluar dari sini tetap CalonTemuan biasa. Ia masuk Langkah 5 seperti
calon lain dan menghadapi pemeriksaan yang sama persis: kutipannya wajib ada
di naskah, pasal yang disebut wajib ada, istilah berdefinisi wajib dieja
persis, usulannya wajib pengganti harfiah untuk rentang yang dicoret, dan
`pembanding` wajib ada di `pembanding_sah`.

Yang terakhir itu yang menahan karangan: daftar peraturan yang boleh disebut
dibawa calon itu sendiri, diisi dari hasil pencarian, dan Langkah 5
mencocokkannya. Model tidak bisa menyebut peraturan dari ingatannya.

=========================================================================
BATASNYA, DAN KENAPA ADA
=========================================================================

Tiap calon yang masuk sini berarti satu embedding + satu kueri OpenSearch +
satu panggilan model. Pada naskah 527 satuan, tanpa batas itu bisa jadi
puluhan panggilan tambahan yang tidak diminta siapa pun. Tiga penyaring
menahan tagihannya, dan ketiganya murah karena diperiksa sebelum apa pun
dipanggil — lihat `layak_dicarikan()`.
"""

from __future__ import annotations

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, Perapal, baca_json, skor_sah
from app.bersama.opensearch import Korpus
from app.fase3 import tahap6_cari
from app.models.pekerjaan import CalonTemuan
from app.models.satuan import PohonSatuan

# Teks yang lebih panjang dari ini tidak akan pernah punya pengganti harfiah
# yang masuk akal: `usulan_harfiah` di Langkah 5 menolak usulan yang jauh
# lebih panjang daripada yang dicoret, jadi mencarikannya berarti membayar
# panggilan untuk sesuatu yang sudah pasti gugur.
_PANJANG_MAKS = 200

# Batas ATAS per dokumen, bukan target. Dipasang karena Fase 3 satu-satunya
# bagian yang biayanya tumbuh seiring banyaknya temuan, bukan seiring
# panjangnya naskah.
BATAS_RUMUSAN = 15


def layak_dicarikan(calon: CalonTemuan) -> bool:
    """Apakah calon ini pantas dibayarkan satu pencarian korpus.

    Diperiksa SEBELUM apa pun dipanggil. Tiga syarat, dan semuanya soal
    menghindari panggilan yang hasilnya sudah bisa ditebak:

      - sudah punya usulan → tidak ada yang perlu dicari;
      - kutipannya kosong → tidak ada yang bisa diganti;
      - kutipannya terlalu panjang → penggantinya pasti ditolak Langkah 5.
    """
    if calon.usulan_rumusan.strip():
        return False
    teks = calon.teks_asli.strip()
    return bool(teks) and len(teks) <= _PANJANG_MAKS


def susun_bahan(calon: CalonTemuan, pohon: PohonSatuan, pembanding) -> str:
    isi = pohon.teks_lengkap(calon.satuan_id) or ""
    bagian = [
        "== KETENTUAN YANG DIPERBAIKI ==",
        "[" + calon.satuan_id + "] " + isi,
        "",
        "== YANG BERMASALAH (ganti HANYA bagian ini) ==",
        calon.teks_asli,
        "",
        "Kelemahannya: " + calon.alasan,
        "",
        "== RUMUSAN DARI PERATURAN YANG MASIH BERLAKU ==",
    ]
    bagian += [p.baris() for p in pembanding]
    return "\n".join(bagian)


def cari_rumusan(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    korpus: Korpus,
    perapal: Perapal,
    klien: Klien,
    ongkos: Ongkos,
) -> CalonTemuan:
    """Lengkapi calon dengan usulan rumusan berikut sumbernya.

    Mengembalikan calon yang SAMA (tidak pernah None): kegagalan di sini
    bukan alasan menggugurkan temuannya. Kelemahan yang sudah terbukti tetap
    layak diberitahukan kepada penelaah, cuma tanpa usulan hijau — ia
    berakhir kuning seperti sebelum Langkah 6c ada.
    """
    cari = tahap6_cari.cari_pembanding(calon, pohon, korpus, perapal)
    if cari.gagal or not cari.pembanding:
        return calon

    jawab = klien.tanya(
        P.PERAN, P.susun(P.TAHAP6_RUMUSAN, susun_bahan(calon, pohon, cari.pembanding))
    )
    ongkos.catat(jawab)

    isi = baca_json(jawab.teks)
    if not isi:
        ongkos.gagal += 1
        return calon

    usulan = str(isi.get("usulan_rumusan", "")).strip()
    peraturan = str(isi.get("peraturan", "")).strip()
    if not usulan or not peraturan:
        # Model memilih tidak mengusulkan. Itu jawaban yang baik — prompt
        # memang menyuruhnya mengosongkan daripada memaksakan.
        return calon

    # Nama yang disalin berikut judulnya tetap diterima asal sebutan resminya
    # ada di dalamnya, sama seperti di F3-001. Selain itu usulannya dibuang di
    # sini juga, supaya calon tidak terlanjur membawa pembanding yang nanti
    # menggugurkannya seluruhnya di Langkah 5.
    sah = cari.nama_sah
    if peraturan not in sah:
        cocok = [n for n in sah if n and n in peraturan]
        if len(cocok) != 1:
            return calon
        peraturan = cocok[0]

    calon.usulan_rumusan = usulan
    calon.pembanding = peraturan
    calon.pembanding_sah = sorted(sah)
    if saran := str(isi.get("saran", "")).strip():
        calon.saran = saran
    # Skor calon TIDAK dinaikkan oleh langkah ini. Yang dinilai model di sini
    # ketepatan usulannya, bukan benar-tidaknya temuan — dan temuan yang lolos
    # ambang karena usulannya bagus adalah cara paling halus untuk salah
    # tandai. Yang dipakai skor terendah di antara keduanya.
    calon.skor = min(calon.skor, skor_sah(isi.get("skor")))
    return calon


def lengkapi(
    calon: list[CalonTemuan],
    pohon: PohonSatuan,
    korpus: Korpus,
    perapal: Perapal,
    klien: Klien,
    ongkos: Ongkos,
) -> list[str]:
    """Jalankan Langkah 6c atas seluruh calon. Mengubah calon DI TEMPAT.

    Mengembalikan catatan untuk daftar gugur — yang perlu terlihat saat
    diagnosa bukan cuma apa yang dikerjakan, melainkan juga apa yang
    SENGAJA TIDAK dikerjakan karena batas biaya. Batas yang diam adalah
    batas yang nanti disangka bug.

    Batasnya ditegakkan di sini, bukan di `alur.py`, supaya ia hidup
    bersama aturan yang membayarinya dan bisa diuji tanpa menjalankan
    seluruh Fase 2.
    """
    catatan: list[str] = []
    dibayar = 0
    dapat = 0
    for c in calon:
        if not layak_dicarikan(c):
            continue
        if dibayar >= BATAS_RUMUSAN:
            catatan.append(
                f"F3-003: batas {BATAS_RUMUSAN} pencarian rumusan per dokumen "
                "tercapai — sisanya tidak dicarikan"
            )
            break
        dibayar += 1
        cari_rumusan(c, pohon, korpus, perapal, klien, ongkos)
        if c.pembanding:
            dapat += 1

    # Dicatat SELALU, termasuk saat nihil. Langkah yang berjalan tanpa hasil
    # dan langkah yang tidak pernah berjalan terlihat sama persis dari luar,
    # dan bedanya menentukan saat menelusuri kenapa tidak ada temuan hijau.
    if dibayar:
        catatan.append(
            f"F3-003: {dibayar} temuan dicarikan rumusan, {dapat} dapat "
            "peraturan sumber"
        )
    return catatan
