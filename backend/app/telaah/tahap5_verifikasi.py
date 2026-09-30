"""TAHAP 5 — gerbang terakhir. SATU-SATUNYA tempat calon jadi Temuan.

Seluruh langkah sebelumnya menghasilkan calon. Tidak ada satu pun yang boleh
menyentuh naskah tanpa lewat sini, dan yang diperiksa di sini bukan pendapat
model melainkan hal-hal yang bisa dibuktikan kode:

  ① Kutipannya ADA di naskah, persis huruf demi huruf, di dalam rentang
    paragraf satuan yang dimaksud. Model terbukti gemar merapikan kutipan.
    Kutipan yang meleset satu koma tidak bisa ditandai — dan yang tidak bisa
    ditandai TIDAK DITANDAI, bukan diperlebar ke satu paragraf.
  ② Pasal yang disebut di alasan/saran BENAR-BENAR ADA di dokumen. Temuan yang
    bertumpu pada pasal karangan gugur seluruhnya, sekalipun kalimatnya
    meyakinkan.
  ③ Peraturan pembanding yang disebut ADA di hasil pencarian (Fase 3). Model
    tidak boleh menyebut peraturan dari ingatannya — brief 8.10.
  ④ Istilah berdefinisi di dalam usulan dieja PERSIS. "Pengeloa Barang" untuk
    "Pengelola Barang" mengubah arti hukumnya.
  ⑤ Skornya di atas ambang yang diatur penelaah.
  ⑨ Klaim "X tidak ada" dicari kode di SELURUH teks mentah — pembukaan,
    batang tubuh, lampiran, isi tabel. Ketemu di mana pun → gugur (bug 7).
    (⑥–⑧ dijelaskan di tempatnya, di `verifikasi_satu`.)

DUA MACAM KEGAGALAN, DAN AKIBATNYA BERBEDA:

  GUGUR       ①②③⑤ gagal → temuannya tidak ada sama sekali.
  DITURUNKAN  ④ gagal, atau usulannya bukan pengganti harfiah → temuannya
              TETAP ADA sebagai catatan kuning, tetapi usulannya tidak pernah
              disisipkan ke naskah. Panel tetap menampilkannya sebagai saran
              yang dibaca penelaah; `office.ts` hanya menyisipkan teks hijau
              untuk jenis_tanda "penggantian", jadi catatan kuning aman
              membawa saran.

Alasan gugurnya ikut dikembalikan supaya bisa dilihat saat menguji. Alat
diagnosa yang cuma bilang "tidak ada temuan" tidak bisa dibedakan dari alat
yang rusak.
"""

from __future__ import annotations

import re
import uuid
from typing import Optional

from app.models.pekerjaan import CalonTemuan
from app.models.satuan import PohonSatuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)
from app.rules.rujukan_kmk527 import ambil_rujukan
from app.telaah.tahap1_parser.definisi import DaftarDefinisi
from app.telaah.tahap1_parser.rujukan import frasa_rujukan_saja

_PASAL_DISEBUT = re.compile(r"\bPasal\s+(\d+[A-Z]?)\b")

# Sesudah nomor pasal menyusul nama peraturan → rujukan ke dokumen lain, bukan
# ke rancangan ini. Tidak diperiksa keberadaannya di pohon.
_PASAL_DOKUMEN_LAIN = re.compile(
    r"\bPasal\s+\d+[A-Z]?\s+(Undang-Undang|Peraturan|Keputusan|UU|PP|PMK|KMK)\b"
)

# Usulan yang dimulai kata-kata ini bukan pengganti harfiah melainkan
# penjelasan — "Sebaiknya diubah menjadi ...". Kalau disisipkan apa adanya,
# kalimat itulah yang muncul hijau di naskah.
_BUKAN_PENGGANTI = re.compile(
    r"^\s*(sebaiknya|seharusnya|ganti|diubah|ubah|misalnya|contoh|gunakan|"
    r"tambahkan|hapus|perjelas|disarankan|dapat ditulis|bisa ditulis)\b",
    re.IGNORECASE,
)

# Batas kewajaran panjang usulan. Pengganti harfiah untuk sebuah frasa tidak
# masuk akal jadi lima kali lipat panjangnya — yang begitu hampir pasti
# penjelasan yang menyamar.
_LIPAT_MAKS = 5
_SELISIH_BEBAS = 40  # frasa pendek boleh melar tanpa dihitung lipatannya

# Panjang ekor teks-sebelum yang dicocokkan ke dalam usulan. Cukup panjang
# untuk jadi khas, cukup pendek supaya tidak menuntut kutipan sempurna.
_EKOR_SEBELUM = 20
_SEBELUM_TERLALU_PENDEK = 8  # di bawah ini ekornya tidak khas, pemeriksaan dilewati

# Panjang coretan yang mulai diperiksa bentuk kalimatnya. Di bawah ini coretan
# masih berupa frasa, dan frasa memang lazim diganti seluruhnya — "30 (tiga
# belas)" jadi "13 (tiga belas)" membuang kata pertamanya, dan itu benar.
# Empat kata ke atas hampir selalu sudah berupa klausa.
_KATA_MINIMAL_PEMBUKA = 4

_TANDA_BACA = ".,;:()[]\"'“”‘’-–—"


# Aturan yang BOLEH mencoret naskah dan menyisipkan usulan hijau.
#
# Hijau berarti dua hal sekaligus: kesalahannya TERBUKTI, dan penggantinya
# didapat DENGAN SUMBER YANG BISA DITUNJUK. Ditetapkan penelaah 22 Sep 2026,
# diperbarui 23 Sep 2026 — yang berubah bukan syarat buktinya, melainkan dari
# mana bukti penggantinya boleh datang:
#
#     "kalo memang alat yakin itu salah rasanya aneh jika tidak memberikan
#      saran perbaikan (karna itulah gunanya tahap 6 opensearch)"
#
# Tiap aturan ditimbang satu per satu, dan hasilnya tidak seragam:
#
#   F2-001  terbukti — Pasal yang dirujuk memang tidak ada. Tetapi
#           penggantinya tidak bisa diketahui siapa pun: Pasal 8, Pasal 17,
#           atau pasal yang memang belum ditulis? Tetap kuning.
#   F2-003  terbukti, dan perbaikannya MEMBUANG bukan mengganti. Dipasang
#           sebagai PENGHAPUSAN — dicoret merah tanpa sisipan hijau.
#   F2-004  terbukti, tetapi nomornya ada di penomoran otomatis Word sehingga
#           rentangnya tidak bisa ditandai sama sekali.
#   F2-007  ketidakcocokannya terbukti, tetapi mana yang benar — 30 atau 13 —
#           justru pertanyaan pokoknya, dan korpus tidak bisa menjawabnya.
#           Usulannya tetap dibawa ke komentar sebagai contoh.
#   F2-1xx  BOLEH hijau, tetapi HANYA kalau rumusannya punya sumber yang bisa
#           ditunjuk — penilaian model atas dirinya sendiri bukan bukti.
#           Syaratnya ditegakkan kode lewat `_HIJAU_BUTUH_SUMBER`, bukan
#           diserahkan ke niat baik.
#   F2-106  lampiran — perbaikannya (menambah pernyataan di pasal, membetulkan
#           kepala atau penutup lampiran) jarang berupa pengganti harfiah satu
#           frasa di tempat yang dicoret. Selalu kuning.
#   F3-001  "berpotensi bertentangan" itu kemungkinan, bukan kesimpulan.
#
# Warisan Fase 1 tidak terpengaruh: F1-005 tetap hijau, karena
# "Undang-undang" → "Undang-Undang" terbukti DAN penggantinya cuma satu.
_ATURAN_BOLEH_HIJAU: set[str] = {
    "F2-101",
    "F2-102",
    "F2-103",
    "F2-104",
    "F2-105",
}

# Aturan yang hijaunya menuntut sumber. Tanpa satu pun sumber, usulannya turun
# jadi contoh rumusan di komentar seperti sebelumnya.
#
# DUA sumber diterima, dan keduanya sama sahnya (ditetapkan penelaah 26 Sep
# 2026, Pilihan B):
#
#   LUAR — `pembanding`, peraturan berlaku dari korpus OpenSearch (Langkah 6c).
#   DALAM — `sumber_internal`, naskah itu sendiri: kata yang DITAMBAHKAN usulan
#           sudah ada di pasal yang sama atau sudah berdefinisi di Pasal 1.
#
# Kenapa yang dalam ikut diterima: penelaah menyebutnya "pencarian internal",
# dan syarat buktinya sama sekali tidak turun — model tetap tidak boleh
# memasukkan kata yang tidak ada di naskah. Yang berubah cuma dari mana bukti
# penggantinya boleh datang, bukan apakah buktinya wajib ada.
#
# Jalur luar TIDAK dimatikan. Keduanya berdampingan: pemeriksaan yang memang
# menuntut korpus (pencarian eksternal) tetap lewat OpenSearch seperti semula.
_HIJAU_BUTUH_SUMBER: set[str] = {
    "F2-101",
    "F2-102",
    "F2-103",
    "F2-104",
    "F2-105",
}

# Kata yang tidak membawa isi hukum apa pun — perancah kalimat. Usulan boleh
# memakainya tanpa perlu membuktikan ia sudah ada di naskah.
#
# Daftarnya sengaja PENDEK dan hanya berisi partikel. Kata modal — wajib,
# harus, dapat, dilarang — justru TIDAK masuk: menukar "dapat" jadi "wajib"
# mengubah akibat hukumnya, dan itu persis yang diperiksa F2-103. Kalau suatu
# hari ada yang tergoda menambahkannya ke sini demi meloloskan lebih banyak
# hijau, itu bukan penyederhanaan — itu membuka pintu bagi model mengubah
# kewajiban jadi kewenangan tanpa satu pun sumber.
# Kata yang menentukan AKIBAT HUKUM sebuah ketentuan. Menambahkannya,
# membuangnya, atau menukarnya mengubah kewajiban jadi kewenangan dan
# sebaliknya — jadi tidak satu pun boleh berubah atas dasar "kata-katanya
# sudah ada di naskah". Perubahannya menuntut peraturan pembanding.
_KATA_MODAL: tuple[str, ...] = (
    "wajib",
    "harus",
    "dapat",
    "dilarang",
    "tidak",
    "bukan",
)

_KATA_FUNGSI: frozenset[str] = frozenset(
    {
        "yang", "dan", "atau", "dengan", "pada", "dalam", "untuk", "dari",
        "ke", "di", "oleh", "serta", "atas", "bagi", "kepada", "terhadap",
        "antara", "sebagai", "secara", "itu", "ini", "tersebut", "adalah",
        "merupakan", "sebagaimana", "dimaksud", "ayat", "pasal", "huruf",
        "angka",
    }
)


# Tempat perbaikan yang selalu ada di tiap PMK/KMK dan karena itu tidak perlu
# dicari di pohon. Nilainya bacaan untuk penelaah, bukan id.
_SASARAN_TETAP: dict[str, str] = {
    "judul": "judul peraturan",
    "menimbang": "bagian Menimbang",
    "mengingat": "bagian Mengingat",
    "menetapkan": "bagian Menetapkan",
    "penutup": "ketentuan penutup",
}

# Nilai yang berarti "perbaikannya persis di tempat temuan ini". Barisnya tidak
# ditulis di komentar — menyebut tempat yang sedang dibaca penelaah menambah
# baris tanpa menambah keterangan.
_SASARAN_SETEMPAT = {"satuan ini", "satuan_ini", "sini", "di sini", ""}


def sebutan_sasaran(sasaran: str, satuan_id: str, pohon: PohonSatuan) -> str:
    """Ubah `sasaran` jadi bacaan manusia, ATAU kosongkan kalau tak terbukti.

    Tiga keadaan yang semuanya berakhir string kosong, dan ketiganya memang
    seharusnya diam:

      - sasarannya satuan temuan itu sendiri → baris "Perbaiki di" mubazir;
      - sasarannya id yang TIDAK ADA di pohon → model mengarang tempat, dan
        menunjuk Pasal 45 yang tidak ada lebih buruk daripada diam soal
        tempat;
      - sasarannya kalimat bebas, bukan id maupun nama tetap → tidak bisa
        dibuktikan, jadi tidak dipakai.
    """
    kunci = sasaran.strip().lower()
    if kunci in _SASARAN_SETEMPAT or kunci == satuan_id.lower():
        return ""
    if kunci in _SASARAN_TETAP:
        return _SASARAN_TETAP[kunci]

    satuan = pohon.cari(kunci)
    if satuan is None:
        return ""

    nama = _nama_satuan(satuan.id)
    # Pasal 1 hampir selalu Ketentuan Umum, dan menyebutnya membuat penelaah
    # langsung tahu ini soal daftar istilah.
    if satuan.id == "pasal-1":
        return nama + " (Ketentuan Umum)"
    return nama


def definisi_terkait(
    teks_asli: str, daftar: DaftarDefinisi
) -> list[tuple[int, str, str]]:
    """Definisi Pasal 1 yang istilahnya muncul di teks yang ditandai.

    Mengembalikan (nomor angka, istilah, id satuan) terurut menurut nomornya.
    Id satuannya dibawa supaya panel bisa melompat ke angka itu sendiri, bukan
    ke pangkal Pasal 1 — pada naskah yang Pasal 1-nya belasan definisi, mendarat
    di pangkalnya masih menyisakan pekerjaan menggulir dan menebak.
    """
    if daftar.gagal is not None:
        return []

    ketemu: list[tuple[int, str, str]] = []
    for d in daftar.definisi:
        # BATAS KATA, BUKAN SEKADAR TERKANDUNG.
        #
        # Terbukti pada PMK 104 Tahun 2025, 27 Sep 2026: teks yang ditandai
        # "RPKBUNP SPAN", dan panel menyuruh penelaah memperbaiki
        # "Pasal 1 angka 2 (BUN)" — karena "BUN" memang terkandung di dalam
        # "RPK-BUN-P". Singkatan hukum penuh jebakan begini: BUN di dalam
        # RPKBUNP, PA di dalam KPA, SPM di dalam SPM-LS.
        #
        # Menunjuk angka yang salah lebih buruk daripada tidak menunjuk sama
        # sekali — penelaah membuka Pasal 1 angka 2, tidak menemukan apa pun
        # yang bersangkutan, lalu berhenti mempercayai barisnya.
        if not re.search(r"\b" + re.escape(d.istilah) + r"\b", teks_asli):
            continue
        m = re.search(r"-angka-(\d+)$", d.satuan_id)
        if m:
            ketemu.append((int(m.group(1)), d.istilah, d.satuan_id))

    # Diurutkan menurut nomor angkanya, bukan urutan kemunculan di kalimat —
    # penelaah membaca Pasal 1 dari atas ke bawah.
    return sorted(ketemu)


def angka_definisi_terkait(teks_asli: str, daftar: DaftarDefinisi) -> list[str]:
    """Angka definisi di Pasal 1 yang istilahnya muncul di teks yang ditandai.

    "Perbaiki di: Pasal 1 (Ketentuan Umum)" menyuruh penelaah membaca ulang
    seluruh daftar definisi untuk menebak yang mana. Padahal kalau teks yang
    ditandai memuat istilah yang MEMANG sudah berdefinisi, angkanya bisa
    disebut langsung.

    Contoh nyata dari PMK PPh 21: frasa "Pegawai tertentu dari Pemberi Kerja
    dengan kriteria tertentu" memuat dua istilah berdefinisi — "Pegawai"
    (angka 5) dan "Pemberi Kerja" (angka 4). Menyebut keduanya memberi
    penelaah titik berangkat, sekalipun istilah yang dipersoalkan sendiri
    ("Pegawai tertentu") memang belum ada definisinya.

    Dicocokkan huruf besar-kecil apa adanya: istilah berdefinisi ditulis
    berhuruf awal kapital (butir 67 KMK 527), dan mencocokkannya tanpa peduli
    kapital akan menangkap kata biasa yang kebetulan sama bunyinya.
    """
    return [
        f"angka {n} ({istilah})" for n, istilah, _ in definisi_terkait(teks_asli, daftar)
    ]


def _nama_satuan(satuan_id: str) -> str:
    """'pasal-2-ayat-3-huruf-a' → 'Pasal 2 ayat (3) huruf a'."""
    bagian = satuan_id.split("-")
    keluar: list[str] = []
    i = 0
    while i < len(bagian):
        kata = bagian[i]
        nilai = bagian[i + 1] if i + 1 < len(bagian) else ""
        if kata == "pasal":
            keluar.append(f"Pasal {nilai.upper() if nilai.isalpha() else nilai}")
        elif kata == "ayat":
            keluar.append(f"ayat ({nilai})")
        elif kata in ("huruf", "angka"):
            keluar.append(f"{kata} {nilai}")
        elif kata in ("bab", "bagian", "paragraf"):
            keluar.append(f"{kata.upper() if kata == 'bab' else kata.capitalize()} {nilai.upper()}")
        else:
            keluar.append(kata)
            i += 1
            continue
        i += 2
    return " ".join(keluar).strip()


def sumber_internal(
    usulan: str,
    teks_asli: str,
    satuan_id: str,
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
) -> str:
    """Sumber usulan DI DALAM naskah sendiri. Kosong berarti tidak ada.

    Ini jalur hijau kedua yang dibuka penelaah 26 Sep 2026, dan syaratnya ia
    rumuskan sendiri: "ada textnya di pasal". Artinya usulan tidak boleh
    membawa masuk kata yang belum ada di naskah — ia hanya boleh menyusun
    ulang apa yang naskahnya sudah katakan.

    Yang diperiksa cuma kata yang DITAMBAHKAN usulan di luar coretannya. Kata
    yang sudah ada di coretan tidak perlu dibuktikan lagi; ia memang sedang
    dikutip. Dua tempat yang dihitung sebagai naskah sendiri:

      1. istilah berdefinisi di Pasal 1 — paling kuat, karena artinya sudah
         ditetapkan naskah ini dan penelaah bisa membacanya di satu tempat;
      2. teks pasal yang memuat temuannya — subjek sebuah ayat sering berada
         di ayat (1) sementara cacatnya di ayat (3), dan itu masih "di pasal".

    Satu kata saja yang tidak ketemu di keduanya sudah membatalkan seluruh
    usulan. Bukan mayoritas, bukan sebagian besar: satu kata karangan cukup
    untuk mengubah arti sebuah ketentuan.

    Nilai baliknya bacaan untuk penelaah, dipakai di komentar supaya ia bisa
    memeriksa sendiri dari mana rumusan itu datang.
    """
    if not usulan.strip():
        return ""

    # KATA MODAL YANG DIBUANG — diperiksa paling dulu.
    #
    # Sisa pemeriksaan di bawah menjaga kata yang DIBAWA MASUK usulan.
    # Lubangnya: kata yang DIBUANG tidak terjaga sama sekali, dan membuang
    # kata modal sama berakibatnya dengan menambahkannya.
    #
    # Terbukti pada PMK 17, 26 Sep 2026. Model mengusulkan
    #
    #     "maka dapat digunakan Otoritas Jasa Keuangan pada tahun berikutnya"
    #   → "maka digunakan oleh Otoritas Jasa Keuangan pada tahun berikutnya"
    #
    # dan itu lolos jadi hijau. Satu-satunya kata yang ditambahkan "oleh",
    # yang memang perancah kalimat — jadi pemeriksaan di bawah menyebutnya
    # "susunan ulang kata" dan meloloskannya. Padahal "dapat" hilang:
    # kewenangan berubah jadi keharusan, persis yang diperiksa F2-103.
    #
    # Perubahan begini bukan tidak boleh — ia cuma menuntut sumber yang lebih
    # kuat daripada "kata-katanya sudah ada di naskah", yaitu peraturan
    # pembanding yang betul-betul memakai rumusan itu.
    dibuang = [
        k
        for k in _KATA_MODAL
        if re.search(r"\b" + k + r"\b", teks_asli, re.IGNORECASE)
        and not re.search(r"\b" + k + r"\b", usulan, re.IGNORECASE)
    ]
    if dibuang:
        return ""

    # Kata yang ditambahkan: ada di usulan, tidak ada di coretannya.
    tambahan = [
        bersih
        for k in _kata(usulan)
        if (bersih := k.strip(_TANDA_BACA))
        and bersih.lower() not in _KATA_FUNGSI
        and not re.search(r"\b" + re.escape(bersih) + r"\b", teks_asli, re.IGNORECASE)
    ]

    if not tambahan:
        # Usulannya menyusun ulang kata-kata coretannya sendiri — tidak ada
        # yang perlu dibuktikan asalnya.
        return f"susunan ulang kata di {_nama_satuan(satuan_id)}"

    # Istilah berdefinisi yang DIBAWA MASUK usulan. Dicocokkan apa adanya,
    # sebab istilah berdefinisi berhuruf awal kapital (butir 67 KMK 527) dan
    # mencocokkannya tanpa peduli kapital akan menangkap kata biasa yang
    # kebetulan sama bunyinya.
    istilah_dipakai: list[str] = []
    kata_istilah: set[str] = set()
    if daftar.gagal is None:
        for d in daftar.definisi:
            if d.istilah in usulan and d.istilah not in teks_asli:
                istilah_dipakai.append(d.istilah)
            if d.istilah in usulan:
                kata_istilah.update(k.lower() for k in _kata(d.istilah))

    # Pasal yang memuat temuannya, berikut seluruh ayat dan hurufnya.
    induk = re.match(r"(pasal-[0-9a-z]+)", satuan_id or "")
    teks_pasal = pohon.teks_lengkap(induk.group(1)) if induk else ""

    for kata in tambahan:
        if kata.lower() in kata_istilah:
            continue
        if re.search(r"\b" + re.escape(kata) + r"\b", teks_pasal, re.IGNORECASE):
            continue
        return ""

    if istilah_dipakai:
        return "istilah berdefinisi Pasal 1: " + ", ".join(istilah_dipakai)
    return f"rumusan yang sudah ada di {_nama_satuan(induk.group(1))}" if induk else ""


def boleh_menyisipkan(
    aturan_id: str, pembanding: str = "", sumber_dalam: str = ""
) -> bool:
    """Apakah aturan ini boleh mencoret naskah dan menyisipkan usulan hijau.

    SATU-SATUNYA tempat kebijakan hijau/kuning ditetapkan. Jalur mekanis
    (F2-0xx) memanggilnya juga, supaya tidak ada dua kebijakan yang bisa
    berselisih diam-diam.

    Aturan penalaran menuntut SALAH SATU sumber terisi. Keduanya kosong berarti
    usulannya lahir dari penilaian model atas dirinya sendiri, dan itu bukan
    bukti — berapa pun skornya.

    `pembanding` nama peraturan berlaku dari korpus; `sumber_dalam` keterangan
    dari `sumber_internal()`.
    """
    if aturan_id not in _ATURAN_BOLEH_HIJAU:
        return False
    if aturan_id in _HIJAU_BUTUH_SUMBER and not (
        pembanding.strip() or sumber_dalam.strip()
    ):
        return False
    return True


class Hasil:
    """Keluaran verifikasi satu calon: temuannya, atau alasan gugurnya."""

    def __init__(self, temuan: Optional[Temuan], alasan: str = "", diturunkan: str = "") -> None:
        self.temuan = temuan
        self.alasan = alasan
        self.diturunkan = diturunkan

    @property
    def lolos(self) -> bool:
        return self.temuan is not None


def cari_di_paragraf(teks: str, kutipan: str) -> Optional[tuple[int, int]]:
    """(awal, panjang) kutipan di teks paragraf, atau None.

    Persis dulu. Kalau tidak ketemu, dicoba lagi dengan SPASI SAJA yang
    dilonggarkan: satu spasi di kutipan boleh bertemu tab, spasi ganda, atau
    pemutus baris di naskah. Model membaca bahan yang spasinya sudah dirapikan,
    jadi kutipan yang benar hurufnya bisa berbeda spasinya dari paragraf Word.
    Huruf, tanda baca, dan besar-kecilnya tetap wajib persis — yang ditandai
    rentang ASLI paragrafnya, bukan kutipan model.
    """
    posisi = teks.find(kutipan)
    if posisi != -1:
        return posisi, len(kutipan)
    potongan = kutipan.split()
    if not potongan:
        return None
    m = re.search(r"\s+".join(re.escape(k) for k in potongan), teks)
    return (m.start(), m.end() - m.start()) if m else None


# Temuan yang letaknya tidak bisa dipastikan di Word — sesudah tabel raksasa
# yang tidak dibaca panel — diberi nomor paragraf ini. Panel tidak menemukan
# paragrafnya, jadi temuan itu tampil di panel TANPA pernah ditandai.
LETAK_TIDAK_PASTI = -1
CATATAN_TIDAK_PASTI = (
    " (Tidak ditandai di naskah: letaknya sesudah tabel raksasa yang tidak "
    "dibaca panel, jadi nomor paragrafnya di Word tidak bisa dipastikan.)"
)


def _cari_lokasi(
    calon: CalonTemuan, pohon: PohonSatuan, paragraf: list[ParagrafInput]
) -> Optional[tuple[LokasiTemuan, int]]:
    """Pemeriksaan ① — kutipannya ada di dalam rentang satuannya.

    Mengembalikan lokasinya dan index paragraf ASAL-nya. Keduanya berbeda
    untuk paragraf sesudah tabel raksasa: lokasinya LETAK_TIDAK_PASTI supaya
    tidak pernah ditandai, index asalnya tetap dipakai pemeriksaan lain.
    """
    satuan = pohon.cari(calon.satuan_id)
    if satuan is None or not satuan.bisa_ditandai:
        return None
    for p in paragraf:
        if not (satuan.paragraf_mulai <= p.index < satuan.paragraf_akhir):
            continue
        ketemu = cari_di_paragraf(p.teks, calon.teks_asli)
        if ketemu is None:
            continue
        awal, panjang = ketemu
        lokasi = LokasiTemuan(
            paragraf_index=p.index if p.letak_pasti else LETAK_TIDAK_PASTI,
            offset_mulai=awal,
            panjang=panjang,
            teks_asli=p.teks[awal : awal + panjang],
        )
        return lokasi, p.index
    return None


def _rapat(teks: str) -> str:
    return re.sub(r"\s+", "", teks).lower()


# Kalimat yang mengklaim sesuatu tidak ada di naskah — dipakai kalau model
# tidak mengisi `tidak_ada` padahal alasannya mengklaim ketiadaan.
_KLAIM_TIDAK_ADA = re.compile(
    r"\b(?:tidak|belum)\s+(?:ada|ditemukan|terdapat|tercantum|dimuat|tertulis|"
    r"disebut(?:kan)?)\s+(?:di|dalam|pada)\s+(?:naskah|rancangan|Peraturan\s+Menteri\s+ini|"
    r"batang\s+tubuh|lampiran)",
    re.IGNORECASE,
)
_KUTIPAN = re.compile(r"[\"“‘']([^\"”’']{3,80})[\"”’']")


def klaim_tidak_ada_keliru(
    calon: CalonTemuan,
    paragraf: list[ParagrafInput],
    index_asal: int,
    teks_tambahan: Optional[list[str]] = None,
) -> Optional[str]:
    """Pemeriksaan ⑨ — teks yang diklaim TIDAK ADA ternyata ada. Kembalikan buktinya.

    Dicari di SELURUH teks mentah — pembukaan, batang tubuh, lampiran, isi
    tabel — tidak peka huruf besar-kecil dan spasi. Paragraf tempat temuan itu
    sendiri dikecualikan: "merujuk Lampiran II yang tidak ada" memang memuat
    kata "Lampiran II" di kalimat rujukannya.

    Sumbernya dua. `tidak_ada` yang diisi model — diperiksa seluruhnya. Dan,
    kalau model tidak mengisinya padahal alasannya mengklaim ketiadaan, teks
    berkutip di alasannya — kecuali yang memang bagian dari teks yang
    ditandai, karena yang itu jelas ada.
    """
    klaim = list(calon.tidak_ada)
    if not klaim and _KLAIM_TIDAK_ADA.search(calon.alasan):
        ditandai = _rapat(calon.teks_asli)
        klaim = [k for k in _KUTIPAN.findall(calon.alasan) if _rapat(k) not in ditandai]

    for x in klaim:
        kunci = _rapat(x)
        if len(kunci) < 3:
            continue
        for p in paragraf:
            if p.index == index_asal:
                continue
            if kunci in _rapat(p.utuh):
                return f"mengklaim {x!r} tidak ada, padahal ada di paragraf {p.index}"
        for t in teks_tambahan or []:
            if kunci in _rapat(t):
                return f"mengklaim {x!r} tidak ada, padahal ada di contoh tabel raksasa"
    return None


# Label penomoran di depan kutipan: "(3) ", "a. ", "1. ".
_LABEL_DEPAN = re.compile(r"^\s*(?:\(\d+\)|[a-z]\.|\d+\.)\s+")


def _buang_label_depan(calon: CalonTemuan) -> Optional[CalonTemuan]:
    """Salinan calon yang kutipannya tanpa label di depan, atau None.

    Usulannya ikut dilepas labelnya kalau diawali label yang SAMA — kalau
    tidak, usulan yang tadinya pengganti harfiah jadi kelebihan satu label.
    """
    m = _LABEL_DEPAN.match(calon.teks_asli)
    if not m:
        return None
    label = m.group(0)
    usulan = calon.usulan_rumusan
    if usulan.startswith(label):
        usulan = usulan[len(label):]
    return calon.model_copy(
        update={"teks_asli": calon.teks_asli[m.end():], "usulan_rumusan": usulan}
    )


def _kunci_rujukan(calon: CalonTemuan) -> str:
    """Entri tabel rujukan untuk calon ini.

    F2-101 di Pasal 1 memakai butir 66 (definisi tidak boleh bermakna ganda)
    sebagai kutipan langsung. Di luar Pasal 1 butir itu bukan dasarnya, dan
    rujukannya prioritas penelaah — lihat catatan entri F2-101.
    """
    sid = calon.satuan_id
    if calon.aturan_id == "F2-101" and (sid == "pasal-1" or sid.startswith("pasal-1-")):
        return "F2-101-definisi"
    return calon.aturan_id


def _rapi_bacaan(teks: str) -> str:
    return re.sub(r"\W+", " ", teks).strip().lower()


def _catatan_dengan_bacaan(calon: CalonTemuan) -> str:
    """Catatan temuan; untuk F2-101 ditambah kedua tafsirannya.

    Kedua tafsiran itulah BUKTI-nya. Tanpa keduanya tertulis di komentar,
    penelaah cuma bisa percaya atau tidak — dengan keduanya ia bisa menilai
    sendiri apakah rumusan itu memang bercabang.
    """
    catatan = calon.alasan.strip()
    bacaan = [b.strip().rstrip(".") for b in calon.bacaan if b.strip()]
    if calon.aturan_id == "F2-101" and len(bacaan) >= 2:
        catatan = f"{catatan} Bisa dibaca: (1) {bacaan[0]}; atau (2) {bacaan[1]}."
    return catatan


# Tuduhan bahwa sebuah istilah tidak punya definisi. Sengaja sempit: temuan
# yang mempersoalkan ISI definisi ("definisi X tidak mencakup Y") tidak boleh
# ikut tertangkap, karena istilahnya memang tertulis di Pasal 1.
_KLAIM_TAK_BERDEFINISI = re.compile(
    r"(?:tidak|belum)\s+(?:di)?definisikan"
    r"|tanpa\s+definisi"
    r"|(?:tidak|belum)\s+(?:ditemukan|ada|terdapat|tercantum|dimuat|memiliki|mempunyai)"
    r"\s+(?:\w+\s+){0,3}?definisi"
    r"|definisi\w*\s+(?:\w+\s+){0,4}?(?:tidak|belum)\s+"
    r"(?:ditemukan|ada|tercantum|terdapat|dimuat)",
    re.IGNORECASE,
)


def pasal_karangan(teks: str, pohon: PohonSatuan) -> list[str]:
    """Pemeriksaan ② — nomor pasal yang disebut tetapi tidak ada di dokumen."""
    if not teks:
        return []
    # Buang dulu rujukan ke peraturan lain supaya tidak ikut diperiksa.
    bersih = _PASAL_DOKUMEN_LAIN.sub(" ", teks)
    hilang: list[str] = []
    for m in _PASAL_DISEBUT.finditer(bersih):
        nomor = m.group(1)
        if not pohon.ada("pasal-" + nomor.lower()) and nomor not in hilang:
            hilang.append(nomor)
    return hilang


def _kata(teks: str) -> list[str]:
    """Pecah jadi kata, tanpa tanda baca di pinggirnya."""
    return [k for k in re.split(r"\s+", teks.strip()) if k.strip(_TANDA_BACA)]


def periksa_usulan(usulan: str, teks_asli: str, sebelum: str = "") -> str:
    """Kenapa `usulan` TIDAK layak disisipkan. String kosong berarti layak.

    Dipisah dari `usulan_harfiah` supaya alasannya bisa dibaca — baik di
    daftar gugur saat diagnosa, maupun oleh `tools/cek_usulan.py` yang dipakai
    memeriksa satu contoh dengan tangan.
    """
    if not usulan:
        return "usulan kosong"
    if _BUKAN_PENGGANTI.match(usulan):
        return "usulan berupa penjelasan, bukan teks pengganti"
    if usulan.strip() == teks_asli.strip():
        return "usulan sama persis dengan yang dicoret — tidak mengubah apa pun"

    batas = max(len(teks_asli) * _LIPAT_MAKS, len(teks_asli) + _SELISIH_BEBAS)
    if len(usulan) > batas:
        return f"usulan {len(usulan)} huruf, terlalu panjang untuk mengganti {len(teks_asli)} huruf"

    awal = sebelum.strip()
    if len(awal) >= _SEBELUM_TERLALU_PENDEK and awal[-_EKOR_SEBELUM:] in usulan:
        return "usulan mengulang teks yang ada SEBELUM coretan — kalimatnya akan tertulis dua kali"

    # PENJAGA BENTUK KALIMAT, ditetapkan penelaah 25 Sep 2026.
    #
    # Kaidah yang ia sebutkan sendiri: "selama memang kata yang benarnya bisa
    # disisipkan di kalimat yang berpotensi salah, masukkan saja; tapi kalau
    # mengharuskan di tempat yang berbeda, hanya bertanda kuning dan ada
    # komentar."
    #
    # Masalahnya ada usulan yang KELIHATAN muat padahal tidak. Terbukti pada
    # contoh-rancangan-uji.docx:
    #
    #     dicoret : "penyelesaiannya dilakukan melalui rapat pembahasan"
    #     usulan  : "rapat pembahasan yang diselenggarakan oleh unit kerja
    #                yang melakukan penelaahan"
    #
    # Panjangnya masuk akal dan tidak mengulang teks sebelumnya, jadi kedua
    # penjaga di atas meloloskannya. Tetapi kata kerja "dilakukan" ikut
    # tercoret tanpa pengganti, dan ayatnya kehilangan predikat.
    #
    # Tandanya: kata PERTAMA yang dicoret lenyap dari usulannya. Itu berarti
    # satu klausa diganti satu frasa, bukan frasa diganti frasa.
    #
    # Hanya berlaku pada coretan panjang. Frasa pendek memang lazim diganti
    # seluruhnya — "30 (tiga belas)" jadi "13 (tiga belas)" membuang kata
    # pertamanya dan itu benar.
    kata = _kata(teks_asli)
    if len(kata) >= _KATA_MINIMAL_PEMBUKA:
        pembuka = kata[0].strip(_TANDA_BACA)
        if pembuka and not re.search(
            r"\b" + re.escape(pembuka) + r"\b", usulan, re.IGNORECASE
        ):
            return (
                f'usulan membuang kata pembuka "{pembuka}" dari coretan '
                "sepanjang ini — satu klausa diganti satu frasa, kalimatnya "
                "akan kehilangan predikat"
            )

    return ""


def usulan_harfiah(usulan: str, teks_asli: str, sebelum: str = "") -> bool:
    """Apakah `usulan` layak disisipkan sebagai pengganti `teks_asli`.

    `sebelum` teks paragraf yang mendahului `teks_asli`. Dipakai menangkap
    kesalahan yang paling merusak dan paling sulit dilihat dari usulannya
    sendiri: **model menulis ulang seluruh kalimat padahal yang dicoret cuma
    penggalannya.**

    Usulan begitu terbaca wajar kalau dibaca sendirian, panjangnya pun masih
    masuk akal, tetapi begitu disisipkan naskahnya jadi:

        "Catatan telaah sebagaimana dimaksud pada ayat (1) ~~disampaikan
         kepada Unit Pemrakarsa.~~ Catatan telaah sebagaimana dimaksud pada
         ayat (1) disampaikan kepada Unit Pemrakarsa oleh Penelaah."

    Kalimatnya tertulis dua kali. Itu menyentuh naskah di luar rentang
    `lokasi` — pelanggaran CLAUDE.md butir 5. Terbukti pada
    contoh-rancangan-uji.docx, 22 Sep 2026.

    Alasan penolakannya ada di `periksa_usulan`.
    """
    return periksa_usulan(usulan, teks_asli, sebelum) == ""


def verifikasi_satu(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    ambang: float = 0.7,
    pembanding_sah: Optional[set[str]] = None,
    teks_tambahan: Optional[list[str]] = None,
) -> Hasil:
    """Jalankan seluruh pemeriksaan atas satu calon.

    `teks_tambahan` teks naskah yang tidak berbentuk paragraf — baris contoh
    tabel raksasa — supaya klaim "tidak ada" juga diperiksa di sana.
    """

    # ⑤ Skor — diperiksa paling dulu karena paling murah.
    if calon.skor < ambang:
        return Hasil(None, f"skor {calon.skor:.2f} di bawah ambang {ambang:.2f}")

    # ③ Pembanding Fase 3 wajib berasal dari hasil pencarian.
    #
    # Daftarnya dibawa calon itu sendiri (`pembanding_sah`), karena tiap
    # ketentuan punya pembandingnya masing-masing. `pembanding_sah` sebagai
    # argumen tetap ada untuk tes dan untuk pemanggil yang mau memaksakan
    # satu daftar.
    sah = pembanding_sah if pembanding_sah is not None else (
        set(calon.pembanding_sah) if calon.pembanding_sah else None
    )
    if sah is not None and calon.pembanding not in sah:
        return Hasil(
            None,
            "peraturan pembanding tidak ada di hasil pencarian: "
            + (calon.pembanding or "(kosong)"),
        )

    # ② Pasal yang disebut wajib ada.
    if hilang := pasal_karangan(calon.alasan + " " + calon.saran, pohon):
        return Hasil(None, "menyebut Pasal yang tidak ada: " + ", ".join(hilang))

    # ① Kutipannya wajib ketemu persis (spasi saja yang dilonggarkan).
    ketemu = _cari_lokasi(calon, pohon, paragraf)
    if ketemu is None and (tanpa_label := _buang_label_depan(calon)) is not None:
        # Model ikut menyalin label "(3)" / "a." yang sejak 27 Sep 2026 ada
        # di teks yang dikirim kepadanya. Di Word label itu penomoran
        # otomatis, bukan teks, jadi kutipannya dicari tanpa label.
        calon = tanpa_label
        ketemu = _cari_lokasi(calon, pohon, paragraf)
    if ketemu is None:
        return Hasil(None, "kutipan tidak ketemu persis di naskah: " + repr(calon.teks_asli))
    lokasi, index_asal = ketemu

    # ⑨ Klaim "X tidak ada" dibuktikan kode di seluruh teks mentah (bug 7).
    #
    # Salah tandai 27 Sep 2026 lahir dari klaim begini: model menyimpulkan
    # sesuatu tidak ada tanpa pernah mencarinya. Kini model wajib menulis
    # klaimnya di `tidak_ada`, dan yang ternyata ada di mana pun — pembukaan,
    # batang tubuh, lampiran, isi tabel — menggugurkan seluruh temuannya.
    if bukti := klaim_tidak_ada_keliru(calon, paragraf, index_asal, teks_tambahan):
        return Hasil(None, bukti)

    # ⑥ Yang ditandai cuma sebuah rujukan internal, dan tujuannya ADA.
    #
    # Keabsahan rujukan urusan F2-001, yang memeriksanya dengan kode pada
    # pohon satuan. Model yang menuduh "Pasal 3 ayat (1) tidak memiliki huruf
    # b" sedang menebak sesuatu yang bisa dipastikan — dan pada PMK 45 tebakan
    # itu salah, 27 Sep 2026. Hanya berlaku kalau SELURUH kutipan adalah
    # alamat rujukan; "atas permohonan sebagaimana dimaksud pada ayat (4)"
    # memuat kata lain dan tetap dinilai.
    rujukan = frasa_rujukan_saja(calon.teks_asli, calon.satuan_id, pohon)
    if rujukan and all(r.tepat for r in rujukan):
        return Hasil(
            None,
            "yang ditandai cuma rujukan internal, dan tujuannya ada di naskah: "
            + ", ".join(r.id_sasaran for r in rujukan),
        )

    # ⑦ Menuduh istilah tidak berdefinisi, padahal istilahnya tertulis di
    #    Pasal 1.
    #
    # Diperiksa pada teks Pasal 1 yang MENTAH, bukan pada daftar definisi hasil
    # parser — daftar itu yang dulu kehilangan "RPKBUNP SPAN" (nama panjangnya
    # melewati batas 120 huruf), dan model yang menerima daftar bolong lalu
    # menuduh istilah itu di setiap kemunculannya. PMK 104, 27 Sep 2026.
    if calon.sasaran.strip().lower() == "pasal-1" and _KLAIM_TAK_BERDEFINISI.search(
        calon.alasan
    ):
        pasal_1 = pohon.teks_lengkap("pasal-1")
        istilah = calon.teks_asli.strip()
        if istilah and re.search(
            r"(?<!\w)" + re.escape(istilah) + r"(?!\w)", pasal_1, re.IGNORECASE
        ):
            return Hasil(
                None,
                f"menuduh {istilah!r} tidak berdefinisi, padahal tertulis di Pasal 1",
            )

    # ⑧ F2-101 wajib menyebut DUA tafsiran yang berbeda.
    #
    # "Bisa dibaca dua arah" tanpa menyebut kedua arahnya cuma kesan. Pada uji
    # 27 Sep 2026 F2-101 menandai rumusan baku "sesuai dengan peraturan
    # perundang-undangan mengenai …" sebagai "terlalu umum" — itu bukan dua
    # arah, dan bukan kesalahan. Yang tidak bisa menyebut dua bacaan tidak
    # membuktikan apa pun, jadi gugur di sini oleh kode, bukan oleh penilaian.
    if calon.aturan_id == "F2-101":
        bacaan = [b.strip() for b in calon.bacaan if b.strip()]
        if len(bacaan) < 2 or _rapi_bacaan(bacaan[0]) == _rapi_bacaan(bacaan[1]):
            return Hasil(
                None,
                "F2-101 tanpa dua tafsiran yang berbeda — 'bisa dibaca dua arah' "
                "tidak terbukti",
            )

    # ④ Boleh hijau hanya bila aturannya memang membuktikan kesalahan DAN
    #    penggantinya pasti; lalu usulannya wajib pengganti harfiah, dan
    #    istilah berdefinisi di dalamnya wajib dieja persis.
    diturunkan = ""
    usulan = calon.usulan_rumusan

    # Sumber dari dalam naskah dicari hanya kalau korpus tidak memberi apa-apa.
    # Urutannya begitu karena pembanding dari peraturan berlaku lebih kuat: ia
    # menunjuk rumusan yang SUDAH dipakai di tempat lain, bukan sekadar
    # kata-kata yang kebetulan tersedia di naskah ini.
    sumber_dalam = ""
    if usulan and not calon.pembanding.strip():
        sumber_dalam = sumber_internal(
            usulan, calon.teks_asli, calon.satuan_id, pohon, daftar
        )

    boleh_hijau = boleh_menyisipkan(calon.aturan_id, calon.pembanding, sumber_dalam)

    if usulan and not boleh_hijau:
        # Usulannya TIDAK dibuang — ia ikut ke komentar sebagai contoh rumusan
        # yang dibaca penelaah. Yang tidak terjadi cuma penyisipannya ke naskah.
        diturunkan = (
            "usulan tanpa sumber — tidak ada peraturan pembanding, dan rumusannya "
            "tidak bisa ditelusuri ke naskah ini sendiri (kata yang belum ada di "
            "naskah, atau kata modal yang dibuang). Jadi contoh rumusan, bukan coretan"
            if calon.aturan_id in _HIJAU_BUTUH_SUMBER
            else "aturan ini tidak membuktikan kesalahan — usulan jadi saran, bukan coretan"
        )
    elif lokasi.paragraf_index == LETAK_TIDAK_PASTI:
        # Letaknya di Word tidak pasti — tidak ada yang boleh disisipkan.
        diturunkan = "letaknya sesudah tabel raksasa — usulan jadi saran, bukan coretan"
    elif usulan:
        sebelum = ""
        for p in paragraf:
            if p.index == index_asal:
                sebelum = p.teks[: lokasi.offset_mulai]
                break
        if sebab := periksa_usulan(usulan, calon.teks_asli, sebelum):
            diturunkan = sebab
        elif daftar.gagal is None and (salah_eja := daftar.cari_mirip(usulan)):
            diturunkan = "istilah berdefinisi salah eja di usulan: " + ", ".join(salah_eja)
    elif calon.aturan_id in _ATURAN_BOLEH_HIJAU and calon.sasaran.strip().lower() in (
        "",
        "satuan ini",
    ):
        # MODEL DIAM PADAHAL SEHARUSNYA MENJAWAB.
        #
        # Ia menyatakan cacatnya ada PERSIS di teks yang dikutipnya sendiri,
        # lalu tidak mengusulkan penggantinya. Penelaah menyebut itu logika
        # yang cacat, 26 Sep 2026: "ai dapat menemukan kesalahan internal tapi
        # ia tidak bisa memberi rekomendasi apapun ... seharusnya kamu dapat
        # memaksanya". Prompt Langkah 4 sejak itu menyebut kekosongan begini
        # kegagalan menjawab, bukan kehati-hatian.
        #
        # Temuannya TETAP ADA dan tetap kuning — yang ditambahkan cuma
        # keterangannya. Gunanya: sesudah satu kali jalan berbiaya, berapa kali
        # model masih diam bisa DIHITUNG, bukan ditebak dari tangkapan layar.
        diturunkan = (
            "model tidak mengusulkan pengganti padahal sasarannya satuan ini "
            "sendiri — prompt tahap 4 mewajibkannya terisi"
        )

    hijau = boleh_hijau and bool(usulan) and not diturunkan

    # Usulan yang tidak jadi hijau tetap dibawa, tetapi pindah tempat: ia
    # masuk ke Saran sebagai CONTOH rumusan, bukan sebagai pengganti yang
    # disisipkan. Membuangnya berarti membuang bagian paling berguna dari
    # jawaban model; menyisipkannya berarti mengubah naskah tanpa bukti.
    saran = calon.saran
    if usulan and not hijau:
        contoh = f'Contoh rumusan: "{usulan}"'
        saran = f"{saran} {contoh}".strip() if saran else contoh

    # --- Sasaran: sebutan yang dibaca penelaah, dan tempat melompatnya ------
    #
    # Sasaran "pasal-1" dipertajam ke nomor angkanya bila teks yang ditandai
    # memuat istilah yang sudah berdefinisi. Tanpa ini, komentar cuma berkata
    # "Perbaiki di: Pasal 1 (Ketentuan Umum)" pada naskah yang Pasal 1-nya
    # memuat empat belas definisi — penelaah harus menebak sendiri yang mana.
    sasaran_terbaca = sebutan_sasaran(calon.sasaran, calon.satuan_id, pohon)

    # Id satuan yang BENAR-BENAR dituju tombol lompat. Bisa lebih dalam
    # daripada yang disebut model: kalau model menunjuk "pasal-1" sementara
    # teks yang ditandai memuat istilah berdefinisi, yang dituju angkanya —
    # mendarat di pangkal Pasal 1 pada naskah berbelas definisi masih
    # menyisakan pekerjaan menggulir dan menebak.
    id_tujuan = calon.sasaran.strip().lower()
    if sasaran_terbaca and id_tujuan == "pasal-1":
        terkait = definisi_terkait(calon.teks_asli, daftar)
        if terkait:
            sasaran_terbaca += " — " + ", ".join(
                f"angka {n} ({istilah})" for n, istilah, _ in terkait
            )
            id_tujuan = terkait[0][2]

    # Nomor paragraf sasaran dibawa terpisah supaya panel bisa melompat ke
    # sana. Sengaja nomor paragraf, bukan id satuan: panel tidak memegang
    # pohon satuan, dan Word mengalamati isinya dengan nomor paragraf.
    sasaran_paragraf: Optional[int] = None
    if sasaran_terbaca:
        tujuan = pohon.cari(id_tujuan)
        if tujuan is not None and tujuan.bisa_ditandai and _letak_pasti(paragraf, tujuan.paragraf_mulai):
            # Paragraf sesudah tabel raksasa tidak punya nomor Word yang pasti;
            # tombol lompat ke sana mendarat di tempat yang salah.
            sasaran_paragraf = tujuan.paragraf_mulai

    # Usulan hijau yang bersumber dari peraturan lain WAJIB menyebut sumbernya
    # di komentar. Itu syarat kebijakan hijau, bukan hiasan: penelaah harus
    # bisa memeriksa sendiri bahwa ini bukan asal klaim. Namanya sudah
    # dibuktikan ada di hasil pencarian pada pemeriksaan ③ di atas.
    # Sumbernya dibawa di MEDAN SENDIRI, tidak dilebur ke `saran`.
    #
    # Dipisah 27 Sep 2026 saat komentar temuan hijau diringkas: blok Saran
    # dilewati karena penggantinya sudah terbaca hijau di naskah, dan selama
    # sumbernya menumpang di sana, melewati blok itu ikut membuang sumbernya —
    # padahal menyebut sumber adalah SYARAT kebijakan hijau, bukan hiasan.
    sumber_usulan = ""
    if hijau and calon.pembanding:
        sumber_usulan = f"{calon.pembanding} (masih berlaku)"
    elif hijau and sumber_dalam:
        # Sumber dari naskah sendiri. Syaratnya sama; yang berbeda cuma tempat
        # penelaah memeriksanya — di dokumen yang sedang dibukanya.
        sumber_usulan = sumber_dalam

    return Hasil(
        Temuan(
            id="f-" + uuid.uuid4().hex[:8],
            aturan_id=calon.aturan_id,
            fase=3 if calon.aturan_id.startswith("F3") else 2,
            jenis_tanda=JenisTanda.PENGGANTIAN if hijau else JenisTanda.CATATAN,
            satuan_id=calon.satuan_id,
            skor=calon.skor,
            lokasi=lokasi,
            catatan=_catatan_dengan_bacaan(calon)
            + (CATATAN_TIDAK_PASTI if lokasi.paragraf_index == LETAK_TIDAK_PASTI else ""),
            saran=saran.strip(),
            sumber_usulan=sumber_usulan,
            sasaran=sasaran_terbaca,
            sasaran_paragraf=sasaran_paragraf,
            usulan_rumusan=usulan if hijau else None,
            rujukan=RujukanTemuan(**ambil_rujukan(_kunci_rujukan(calon))),
            status=StatusTemuan.BELUM_DITINJAU,
        ),
        diturunkan=diturunkan,
    )


def _letak_pasti(paragraf: list[ParagrafInput], index: int) -> bool:
    """Apakah paragraf ber-index ini nomornya sama dengan nomor di Word."""
    for p in paragraf:
        if p.index == index:
            return p.letak_pasti
    return False


def bertindihan(lokasi: LokasiTemuan, temuan: list[Temuan]) -> Optional[Temuan]:
    """Temuan yang sudah ada dan rentangnya bertindihan dengan lokasi ini.

    Jaring kedua untuk duplikat Fase 1 ↔ Fase 2. Jaring pertamanya ada di
    Langkah 2: model diberi tahu apa yang sudah ditemukan dan diminta tidak
    mengulang. Yang lolos dari situ dibuang di sini — oleh KODE, dengan
    perbandingan rentang yang bisa ditunjukkan, bukan oleh penilaian.

    Dua rentang dianggap bertindihan kalau ada satu huruf pun yang sama. Dua
    komentar pada huruf yang sama adalah persis keadaan yang dulu membuat
    margin penuh sampai yang penting terkubur.
    """
    if lokasi.paragraf_index == LETAK_TIDAK_PASTI:
        return None  # tidak pernah ditandai, jadi tidak bisa bertumpuk di naskah
    awal, akhir = lokasi.offset_mulai, lokasi.offset_mulai + lokasi.panjang
    for t in temuan:
        if t.lokasi.paragraf_index != lokasi.paragraf_index:
            continue
        awal_t = t.lokasi.offset_mulai
        akhir_t = awal_t + t.lokasi.panjang
        if awal < akhir_t and awal_t < akhir:
            return t
    return None


def verifikasi(
    calon: list[CalonTemuan],
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    ambang: float = 0.7,
    pembanding_sah: Optional[set[str]] = None,
    temuan_ada: Optional[list[Temuan]] = None,
    teks_tambahan: Optional[list[str]] = None,
) -> tuple[list[Temuan], list[str]]:
    """Verifikasi seluruh calon. Kembalikan temuan yang lolos dan alasan gugur.

    `temuan_ada` temuan yang sudah terpasang di naskah — Fase 1, dan temuan
    mekanis Fase 2 yang lebih dulu jadi. Calon yang rentangnya bertindihan
    dengan salah satunya dibuang, supaya tidak ada dua komentar pada huruf
    yang sama.

    Temuan yang lolos diurutkan menurut posisi dokumen; yang letaknya tidak
    pasti (sesudah tabel raksasa) paling akhir. Penomorannya TIDAK dilakukan
    di sini: nomor Fase 2 melanjutkan nomor terakhir Fase 1 dan tidak pernah
    diurutkan ulang, jadi hanya pemanggil yang tahu mulai dari berapa.
    """
    lolos: list[Temuan] = []
    gugur: list[str] = []
    # Temuan yang baru lahir ikut jadi pembanding untuk calon berikutnya —
    # dua temuan Fase 2 pada rentang yang sama sama menumpuknya dengan
    # bertabrakan dengan Fase 1.
    sudah: list[Temuan] = list(temuan_ada or [])

    for c in calon:
        hasil = verifikasi_satu(
            c, pohon, daftar, paragraf, ambang, pembanding_sah, teks_tambahan
        )
        if hasil.temuan is None:
            gugur.append(f"{c.aturan_id} {c.satuan_id}: {hasil.alasan}")
            continue

        tabrak = bertindihan(hasil.temuan.lokasi, sudah)
        if tabrak is not None:
            gugur.append(
                f"{c.aturan_id} {c.satuan_id}: bertindihan dengan T{tabrak.nomor} "
                f"({tabrak.aturan_id}) pada teks {tabrak.lokasi.teks_asli!r}"
            )
            continue

        if hasil.diturunkan:
            gugur.append(f"{c.aturan_id} {c.satuan_id}: DITURUNKAN — {hasil.diturunkan}")
        lolos.append(hasil.temuan)
        sudah.append(hasil.temuan)

    lolos.sort(key=urutan_dokumen)
    return gabungkan_kembar(lolos, gugur), gugur


def urutan_dokumen(t: Temuan) -> tuple[int, int, int]:
    """Kunci urut temuan menurut posisi di naskah; letak tidak pasti paling akhir."""
    tidak_pasti = t.lokasi.paragraf_index == LETAK_TIDAK_PASTI
    return (1 if tidak_pasti else 0, t.lokasi.paragraf_index, t.lokasi.offset_mulai)


def _kunci_kembar(t: Temuan) -> tuple[str, str, str]:
    """Aturan, teks yang ditandai, dan tempat perbaikannya — dinormalkan."""

    def rapi(teks: str) -> str:
        return re.sub(r"\s+", " ", teks).strip().strip(".,;:").lower()

    return (t.aturan_id, rapi(t.lokasi.teks_asli), rapi(t.sasaran))


def gabungkan_kembar(lolos: list[Temuan], gugur: list[str]) -> list[Temuan]:
    """Satu kesalahan yang terulang di banyak tempat → satu temuan.

    Aturan sama, teks yang ditandai sama, tempat perbaikan sama: itu SATU
    kesalahan, bukan sepuluh. Yang dipertahankan kemunculan PERTAMA menurut
    urutan dokumen; kemunculan lainnya tidak ditandai, cukup disebut di
    `juga_di` supaya penelaah tahu harus ke mana lagi.

    Ditambahkan 27 Sep 2026. PMK 104 mendapat satu kartu dan satu komentar
    untuk tiap baris yang memuat "RPKBUNP SPAN", dan PMK 17 mendapat komentar
    kembar di dua huruf yang bunyinya sama persis. Penelaah menetapkannya:
    "masalahnya cukup 1 kotak add ins dan 1 komentar" — termasuk untuk usulan
    hijau (Pilihan A): hijaunya hanya di kemunculan pertama.

    `lolos` wajib sudah urut dokumen. `gugur` ditambahi alasan tiap yang
    digabung, supaya jumlahnya tetap bisa dihitung.
    """
    pertama: dict[tuple[str, str, str], Temuan] = {}
    hasil: list[Temuan] = []
    for t in lolos:
        kunci = _kunci_kembar(t)
        induk = pertama.get(kunci)
        if induk is None:
            pertama[kunci] = t
            hasil.append(t)
            continue
        nama = _nama_satuan(t.satuan_id or "") or f"paragraf {t.lokasi.paragraf_index}"
        if nama not in induk.juga_di and nama != _nama_satuan(induk.satuan_id or ""):
            induk.juga_di.append(nama)
        gugur.append(
            f"{t.aturan_id} {t.satuan_id}: digabung ke temuan yang sama di "
            f"{_nama_satuan(induk.satuan_id or '')} — teks {t.lokasi.teks_asli!r}"
        )
    return hasil
