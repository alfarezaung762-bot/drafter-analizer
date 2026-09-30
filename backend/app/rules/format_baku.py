"""Aturan pemeriksaan format baku — Fase 1.

Setiap fungsi di modul ini adalah fungsi murni:
- Menerima daftar paragraf (list[ParagrafInput])
- Mengembalikan daftar Temuan
- Tanpa objek Request/Response
- Tanpa state global
- Bisa dites tanpa server
"""

from __future__ import annotations

import difflib
import re
import uuid
from typing import Optional

from app.models.temuan import (
    JenisDokumen,
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)
from app.rules.rujukan_kmk527 import ambil_rujukan


# ---------------------------------------------------------------------------
# Utilitas: buat Temuan
# ---------------------------------------------------------------------------

# Batas panjang teks yang ditandai, dalam karakter.
#
# BUKAN soal selera tampilan — ini batas teknis. Frontend menemukan letak temuan
# di Word lewat Word.search(), yang panjang kata kuncinya dibatasi sekitar 255
# karakter. Temuan yang teksnya lebih panjang dari itu TIDAK AKAN PERNAH
# ketemu, jadi tidak pernah tertandai di naskah: penelaah cuma melihat kartu di
# panel tanpa ada apa pun di dokumen.
#
# Terjadi pada PMK 5 Tahun 2025 (18 Sep 2026): butir Menimbang terakhirnya
# sepanjang ~500 karakter, jauh di atas batas, sehingga F1-004 tidak pernah
# sampai ke naskah.
#
# Angkanya sengaja jauh di bawah batas Word: 120 karakter kira-kira satu setengah
# baris — cukup untuk menunjukkan tempatnya, tidak sampai memblok satu paragraf.
# Alasan lengkapnya tetap di komentar, bukan di sorotan.
_BATAS_PANJANG_TANDA = 120

# Aturan yang BOLEH menghasilkan temuan tanpa lokasi di naskah.
#
# Sejak 27 Sep 2026 ini jalur JARANG lewat — F1-002 (cadangan) dan F1-003
# sekarang memakai anchor netral lewat `_anchor_dokumen` (lihat di sana),
# jadi keduanya HAMPIR SELALU punya lokasi (`tanpa_sorot=True`, bukan tanpa
# lokasi) dan mendapat komentar + Terima/Tolak seperti temuan lain. Set ini
# cuma jaring pengaman untuk kasus yang nyaris mustahil: seluruh dokumen
# tidak punya satu paragraf pun berisi teks. Kalau itu terjadi, temuannya
# tetap dibuat tanpa lokasi, tampil sebagai peringatan dokumen sebaris
# (bagian 6.13) — bukan cacat yang dibuang seperti temuan tanpa lokasi lain.
_BOLEH_TANPA_LOKASI = {"F1-002", "F1-003"}


def _potong_di_batas_kata(teks: str, batas: int) -> int:
    """Panjang potongan teks yang <= batas dan berakhir di batas kata."""
    if len(teks) <= batas:
        return len(teks)
    potong = teks[:batas]
    spasi = potong.rfind(" ")
    return spasi if spasi > 0 else batas


def _buat_temuan(
    aturan_id: str,
    jenis_tanda: JenisTanda,
    paragraf: ParagrafInput,
    offset_mulai: int,
    panjang: int,
    catatan: str,
    usulan_rumusan: Optional[str] = None,
    tanpa_sorot: bool = False,
) -> Temuan:
    """Helper untuk membuat objek Temuan dengan rujukan dari tabel.

    `nomor` sengaja dibiarkan 0 di sini — nomor urut baru bisa ditetapkan
    sesudah SELURUH aturan selesai dan temuannya diurutkan menurut posisi di
    dokumen. Itu tugas jalankan_semua().

    Rentang yang kepanjangan DIPOTONG di batas kata. Lihat _BATAS_PANJANG_TANDA:
    temuan yang tidak bisa dicari di Word sama saja dengan temuan yang tidak
    ada. Pemotongan dilakukan di sini, di satu tempat, supaya aturan yang
    ditambahkan nanti ikut terlindungi tanpa perlu mengingat batas ini.

    `tanpa_sorot=True` untuk temuan yang lokasinya cuma ANCHOR netral (lihat
    `_anchor_dokumen`) — Word tetap mengomentari dan membungkusnya, tapi
    TIDAK mewarnainya, karena teks di situ bukan yang salah.
    """
    if jenis_tanda == JenisTanda.CATATAN and panjang > _BATAS_PANJANG_TANDA:
        panjang = _potong_di_batas_kata(
            paragraf.teks[offset_mulai : offset_mulai + panjang],
            _BATAS_PANJANG_TANDA,
        )

    rujukan_dict = ambil_rujukan(aturan_id)
    return Temuan(
        id=f"f-{uuid.uuid4().hex[:8]}",
        aturan_id=aturan_id,
        fase=1,
        jenis_tanda=jenis_tanda,
        lokasi=LokasiTemuan(
            paragraf_index=paragraf.index,
            offset_mulai=offset_mulai,
            panjang=panjang,
            teks_asli=paragraf.teks[offset_mulai : offset_mulai + panjang],
        ),
        catatan=catatan,
        usulan_rumusan=usulan_rumusan,
        tanpa_sorot=tanpa_sorot,
        rujukan=RujukanTemuan(**rujukan_dict),
        status=StatusTemuan.BELUM_DITINJAU,
    )


def _anchor_dokumen(paragraf: list[ParagrafInput]) -> Optional[tuple[ParagrafInput, int, int]]:
    """Titik aman untuk menempelkan komentar temuan yang kesalahannya adalah
    KETIADAAN sesuatu — bukan kata tertentu yang salah.

    Ditambahkan 27 Sep 2026. Sebelum ini, F1-002 (jalur cadangan) dan F1-003
    dibuat TANPA lokasi sama sekali, sehingga tidak pernah dikomentari di
    Word dan tidak bisa Terima/Tolak — penelaah menyebutnya bug: komentar
    memang bagian dari menelaah yang perlu didiskusikan ke pemrakarsa, dan
    itu cuma bisa terjadi lewat Word, bukan lewat panel yang hilang begitu
    add-in ditutup.

    Yang dipilih SENGAJA bukan tebakan "di mana seharusnya bagian yang
    hilang itu berada" — menebak itu PERSIS kesalahan cadangan lama yang
    sudah terbukti menimpa naskah (CLAUDE.md butir 6, kasus 9 di
    test_format_baku.py). Anchor-nya paragraf JUDUL PEMBUKA dokumen: selalu
    ada kalau sampai di titik ini (pohonnya sudah berhasil dibaca), dan
    tidak pernah jadi bagian dari klaim "teks ini salah" — makanya dipakai
    berbarengan dengan `tanpa_sorot=True`, bukan warna sorot biasa.

    Mengembalikan (paragraf, offset, panjang) menunjuk kata PERTAMA baris
    itu — cukup pendek untuk dicari Word, tidak pernah kosong kalau ada
    baris berisi teks di dokumennya.
    """
    for p in paragraf:
        teks = _trim(p.teks)
        if teks:
            akhir_kata = teks.find(" ")
            panjang = akhir_kata if akhir_kata > 0 else len(teks)
            mulai = p.teks.find(teks)
            return (p, mulai, panjang)
    return None


# ---------------------------------------------------------------------------
# Utilitas: parser struktur dokumen
# ---------------------------------------------------------------------------

# Penutup judul PMK — sesudah judul, sebelum pejabat
_PENUTUP_JUDUL_PMK = "DENGAN RAHMAT TUHAN YANG MAHA ESA"

# Penutup judul KMK — langsung setelah judul
_PENUTUP_JUDUL_KMK = "MENTERI KEUANGAN REPUBLIK INDONESIA,"


def _trim(teks: str) -> str:
    """Strip dan rapatkan spasi ganda."""
    return re.sub(r"\s+", " ", teks.strip())


# ---------------------------------------------------------------------------
# Utilitas: rentang setingkat kata
# ---------------------------------------------------------------------------
#
# Ditambahkan 17 Sep 2026. Sebelumnya F1-001, F1-002, dan F1-004 selalu mengirim
# offset_mulai=0 dan panjang=len(paragraf), sehingga yang tersorot di Word satu
# paragraf penuh — pada blok judul artinya tiga baris kuning untuk persoalan
# yang mungkin cuma satu kata. Yang ditandai sekarang rentang kata yang benar-
# benar bermasalah.

# Satu "kata" termasuk bentuk berimbuhan tanda hubung dan garis miring, supaya
# PERUNDANG-UNDANGAN dan KMK.01/2022 tidak terpotong jadi kepingan.
_POLA_KATA = re.compile(r"\w+(?:[-/.]\w+)*", re.UNICODE)


def _rentang_kata_huruf_kecil(teks: str) -> list[tuple[int, int]]:
    """Rentang (mulai, akhir) tiap DERET kata beruntun yang memuat huruf kecil.

    Deret, bukan kata satuan. Alasannya: kalau judulnya diketik Dengan Huruf
    Awal Kapital, tiap katanya salah, dan satu temuan per kata berarti belasan
    komentar untuk satu persoalan yang sama. Dengan deret, judul yang seluruhnya
    salah menghasilkan satu temuan sepanjang judul — memang itu kenyataannya —
    sedangkan satu kata nyasar di tengah judul kapital menghasilkan satu temuan
    sepanjang satu kata saja.
    """
    hasil: list[tuple[int, int]] = []
    mulai: Optional[int] = None
    akhir = 0

    for m in _POLA_KATA.finditer(teks):
        kata = m.group(0)
        salah = kata != kata.upper()
        if salah:
            if mulai is None:
                mulai = m.start()
            akhir = m.end()
        elif mulai is not None:
            hasil.append((mulai, akhir))
            mulai = None

    if mulai is not None:
        hasil.append((mulai, akhir))

    return hasil


def _pola_frasa(frasa: str) -> Optional[str]:
    """Pola regex frasa yang tahan terhadap spasi ganda antar-katanya."""
    kata = frasa.split()
    if not kata:
        return None
    return r"\s+".join(re.escape(k) for k in kata)


def _hitung_frasa(teks: str, frasa: str) -> int:
    """Berapa kali frasa muncul di teks."""
    pola = _pola_frasa(frasa)
    return len(re.findall(pola, teks, re.IGNORECASE)) if pola else 0


def _cari_frasa(
    teks: str, frasa: str, lewati: int = 0
) -> Optional[tuple[int, int]]:
    """Cari posisi frasa di dalam teks, tahan terhadap spasi ganda.

    Frasa datang dari judul yang sudah dirapatkan spasinya, sedangkan teks
    paragraf aslinya belum — jadi pencarian harfiah bisa meleset hanya karena
    ada dua spasi. Pencocokan dilakukan per kata dengan pemisah \\s+.

    `lewati` melompati sekian kemunculan pertama. Ada karena sebuah frasa bisa
    muncul BERKALI-KALI dalam satu judul sementara yang salah cuma salah
    satunya — lihat `_ordinal_frasa`.
    """
    pola = _pola_frasa(frasa)
    if pola is None:
        return None
    for i, m in enumerate(re.finditer(pola, teks, re.IGNORECASE)):
        if i >= lewati:
            return (m.start(), m.end())
    return None


def _ordinal_frasa(kata: list[str], frasa: str, mulai_kata: int) -> int:
    """Kemunculan ke-berapa (0-based) frasa yang bermula di kata ke-`mulai_kata`.

    KENAPA PERLU. Terbukti pada PMK 45 Tahun 2026, 27 Sep 2026. Judul pada
    Menetapkan memuat "YANG DIPERGUNAKAN" dua kali sementara judul pembuka
    sekali — jadi yang salah kemunculan KEDUA. Pencarian yang berhenti di
    kemunculan pertama menyorot frasa yang justru sudah benar, dan penelaah
    membaca komentar "di sini berbeda" pada kata yang tidak berbeda.
    """
    bagian = frasa.split()
    n = len(bagian)
    if n == 0:
        return 0
    return sum(1 for k in range(mulai_kata) if kata[k : k + n] == bagian)


def _cari_index_anchor(
    paragraf: list[ParagrafInput], anchor: str, mulai: int = 0
) -> Optional[int]:
    """Cari indeks paragraf yang isinya PERSIS sama dengan anchor (case-insensitive, trimmed)."""
    for i in range(mulai, len(paragraf)):
        if _trim(paragraf[i].teks).upper() == anchor.upper():
            return i
    return None


# Catatan: dulu ada _tentukan_jenis_dokumen() yang menebak PMK/KMK dari
# penyebutan pertama di dokumen. Dihapus 17 Sep 2026. Tebakan itu bertumpu pada
# asumsi bahwa penyebutan pertama selalu datang dari blok judul — padahal bagian
# Mengingat sebuah KMK lazim menyebut "Peraturan Menteri Keuangan Nomor ...",
# sehingga KMK bisa dikira PMK lalu F1-004 menuntut bunyi yang salah. Sekarang
# jenisnya dipilih penelaah di task pane dan diteruskan sebagai parameter.
# Lihat docs/fase1 drafter.md bagian 6.7.


# Baris yang MUSTAHIL jadi bagian judul peraturan, dipakai menghentikan
# pengambilan judul kalau penutup menurut jenisnya tidak ketemu.
#
# Kenapa perlu: penutup PMK "DENGAN RAHMAT TUHAN YANG MAHA ESA" tidak selalu
# ada. PMK 104 Tahun 2025 langsung lompat dari judul ke "MENTERI KEUANGAN
# REPUBLIK INDONESIA,", dan pengambilan judul lalu berjalan terus sampai
# paragraf terakhir dokumen — F1-002 mengutip sembilan halaman peraturan ke
# dalam satu kartu panel.
#
# Ketiadaan frasa itu sendiri BELUM diperiksa aturan mana pun: F1-003 hanya
# mencari Menimbang, Mengingat, dan Menetapkan. Jadi jangan membaca penghenti
# ini seolah menutup kekurangan itu — ia cuma menahan akibatnya.
#
# Dijangkar di AWAL baris. "PENETAPAN" tidak tertangkap `Menetapkan\b`, dan
# judul peraturan tidak pernah dibuka salah satu kata ini.
_PENGHENTI_JUDUL = re.compile(
    r"^(DENGAN RAHMAT TUHAN YANG MAHA ESA"
    r"|MENTERI KEUANGAN"
    r"|Menimbang\b|Mengingat\b|Menetapkan\b|MEMUTUSKAN\b"
    r"|BAB\b|Pasal\b)",
    re.IGNORECASE,
)


def _ekstrak_judul_pembuka(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> Optional[dict]:
    """Ekstrak judul dari blok pembuka.

    Struktur:
        PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
        NOMOR ... TAHUN ...
        TENTANG                           <- anchor
        <JUDUL, bisa >1 paragraf>
        DENGAN RAHMAT TUHAN YANG MAHA ESA <- penutup PMK
        MENTERI KEUANGAN REPUBLIK INDONESIA, <- penutup KMK

    Returns dict:
        - 'judul': teks gabungan judul
        - 'jenis': 'PMK' atau 'KMK'
        - 'paragraf_indeks': list indeks paragraf yang membentuk judul
        - 'tentang_index': indeks paragraf "TENTANG"
    """
    # Cari anchor TENTANG — harus PERSIS isinya "TENTANG", bukan sekadar mengandung
    tentang_idx = _cari_index_anchor(paragraf, "TENTANG")
    if tentang_idx is None:
        return None

    # Penutup blok judul berbeda menurut jenis dokumen
    penutup = (
        _PENUTUP_JUDUL_PMK if jenis == JenisDokumen.PMK else _PENUTUP_JUDUL_KMK
    )

    # Judul = semua paragraf sesudah TENTANG sampai penutup
    judul_parts: list[str] = []
    judul_indeks: list[int] = []
    for i in range(tentang_idx + 1, len(paragraf)):
        teks_trimmed = _trim(paragraf[i].teks)
        if teks_trimmed.upper() == penutup.upper():
            break
        # Penghenti cadangan — lihat `_PENGHENTI_JUDUL`. Penutup menurut jenis
        # di atas tetap diperiksa lebih dulu supaya perilaku naskah normal
        # tidak berubah sama sekali.
        if _PENGHENTI_JUDUL.match(teks_trimmed):
            break
        judul_parts.append(teks_trimmed)
        judul_indeks.append(i)

    if not judul_parts:
        return None

    judul = " ".join(judul_parts)

    # BATAS KEWAJARAN — CLAUDE.md butir 2.
    #
    # Jaring terakhir kalau seluruh penghenti di atas meleset juga. Tanpa ini
    # pengambilannya berjalan sampai akhir dokumen, dan F1-002 melaporkan
    # "judulnya berbeda" dengan mengutip SELURUH NASKAH ke dalam komentar dan
    # kartu panel. Terbukti pada PMK 104 Tahun 2025, 27 Sep 2026: satu kartu
    # memuat sembilan halaman peraturan.
    #
    # Di luar batas ini aturan MEMILIH DIAM. Judul yang tidak bisa diambil
    # dengan yakin tidak bisa dibandingkan dengan yakin.
    if len(judul.split()) > _BATAS_KATA_JUDUL:
        return None

    return {
        "judul": judul,
        "jenis": jenis,
        "paragraf_indeks": judul_indeks,
        "tentang_index": tentang_idx,
    }


# Penanda bahwa klausul Menetapkan sudah lewat. Memuat penomoran diktum KMK
# (KESATU, KEDUA, ...) DAN penomoran PMK (BAB, Pasal), karena satu fungsi ini
# melayani keduanya.
#
# Diperluas 18 Sep 2026. Daftar lama berhenti di KESEPULUH. KMK 527 sendiri
# punya diktum sampai KEDUAPULUHLIMA, dan penomoran gabungan seperti
# KEDUAPULUHLIMA tidak cocok dengan pola `KEDUA\b` karena ada lanjutannya.
# Sekarang lanjutannya diizinkan: KE + angka + huruf apa pun.
#
# Kata lain yang berawalan KE- tidak ikut kena karena harus diikuti nama angka:
# KEUANGAN, KEPUTUSAN, KEMENTERIAN, KETENTUAN semuanya lolos.
_PENGHENTI_MENETAPKAN = re.compile(
    r"^(BAB\b|Pasal\b|PERTAMA\b"
    r"|KE(SATU|DUA|TIGA|EMPAT|LIMA|ENAM|TUJUH|DELAPAN|SEMBILAN|SEPULUH"
    r"|SEBELAS)[A-Z]*\b)",
    re.IGNORECASE,
)

# Batas kewajaran panjang judul Menetapkan, dalam kata. Judul peraturan
# terpanjang di JDIH masih jauh di bawah angka ini; kalau hasil pengambilan
# melewatinya, yang terjadi hampir pasti pengambilan kebablasan seperti bug
# KESATU di atas. Dalam keadaan itu aturan MEMILIH DIAM, bukan melapor:
# temuan yang ditandai wajib benar-benar salah.
#
# Dipakai KEDUA sisi sejak 27 Sep 2026. Sebelumnya cuma sisi Menetapkan yang
# dijaga, dan sisi pembuka kebablasan sampai akhir dokumen pada PMK 104.
_BATAS_KATA_JUDUL = 60

# Awal klausul Menetapkan. DIJANGKAR di awal paragraf — tanpa jangkar, kata
# "menetapkan:" di tengah kalimat batang tubuh ikut tertangkap.
#
# Titik dua sengaja OPSIONAL: pada naskah yang menaruh klausul ini di dalam
# tabel, label "Menetapkan" dan isinya berada di sel — dan karenanya di paragraf
# — yang berbeda, sehingga paragraf labelnya cuma berbunyi "Menetapkan" tanpa
# tanda apa pun. Kalau titik dua diwajibkan, klausul yang sah justru terlewat,
# lalu pencarian berlanjut sampai menemukan "menetapkan:" di batang tubuh.
_AWAL_MENETAPKAN = re.compile(r"^Menetapkan\b\s*:?", re.IGNORECASE)

# Penanda "MEMUTUSKAN:", termasuk bentuk BERSPASI HURUF.
#
# DIPERBAIKI 18 Sep 2026. Pencocokan lama menuntut teksnya persis "MEMUTUSKAN",
# padahal naskah peraturan lazim menuliskannya renggang — "M E M U T U S K A N :"
# — supaya tampak lapang di halaman. Pada naskah seperti itu penanda ini tidak
# ketemu, dan SELURUH aturan yang bergantung padanya (F1-002, F1-011, F1-012)
# memilih diam tanpa memberi tahu siapa pun: kesalahan yang nyata di klausul
# Menetapkan lewat begitu saja.
#
# Yang dicocokkan tetap satu paragraf utuh berisi kata itu saja, jadi kata
# "memutuskan" di tengah kalimat tidak ikut kena.
_POLA_MEMUTUSKAN = re.compile(
    r"^M\s*E\s*M\s*U\s*T\s*U\s*S\s*K\s*A\s*N\s*:?$", re.IGNORECASE
)


def _cari_index_memutuskan(paragraf: list[ParagrafInput]) -> Optional[int]:
    """Indeks paragraf "MEMUTUSKAN:", atau None kalau tidak ada.

    Satu-satunya tempat penanda ini dikenali. Aturan yang membutuhkannya wajib
    lewat sini, supaya bentuk berspasi huruf tidak perlu diingat di banyak
    tempat — dan supaya tidak ada aturan yang diam-diam memakai pencocokan
    yang lebih sempit.
    """
    for i, p in enumerate(paragraf):
        if _POLA_MEMUTUSKAN.match(_trim(p.teks)):
            return i
    return None


def _ekstrak_judul_menetapkan(paragraf: list[ParagrafInput]) -> Optional[dict]:
    """Ekstrak judul dari bagian Menetapkan.

    Bentuk:
        MEMUTUSKAN:
        Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG
                     STANDAR BIAYA MASUKAN.

    Normalisasi:
        - Buang teks sampai "Menetapkan" + tanda titik dua
        - Buang awalan "PERATURAN/KEPUTUSAN MENTERI KEUANGAN TENTANG"
        - Buang titik di akhir
        - Rapatkan spasi

    Returns dict:
        - 'judul': teks judul yang sudah dinormalisasi
        - 'paragraf_indeks': list indeks paragraf
    """
    # --- Cari klausul Menetapkan, DI DALAM JENDELA YANG BENAR ------------------
    #
    # BUG YANG DIPERBAIKI 18 Sep 2026 — ditemukan pada RPMK DBH Sawit sungguhan.
    # Pencarian lama memakai re.search tanpa jangkar, sehingga kata "menetapkan:"
    # DI TENGAH KALIMAT ikut cocok. Pada Pasal 4 ayat (1) berbunyi "…Menteri
    # selaku PA BUN Pengelola TKD menetapkan:" — dan itulah yang dikira klausul
    # Menetapkan. Akibatnya isi Pasal 4 dituduh "judulnya berbeda dari judul
    # pembuka", padahal itu bukan judul sama sekali.
    #
    # Klausul Menetapkan yang sah punya letak yang pasti menurut KMK 527: SETELAH
    # "MEMUTUSKAN:" dan SEBELUM batang tubuh (BAB/Pasal/diktum). Jendela itulah
    # yang dipakai sekarang, ditambah jangkar di awal paragraf. Menetapkan di
    # luar jendela itu bukan klausul Menetapkan, titik.
    memutuskan_idx = _cari_index_memutuskan(paragraf)

    if memutuskan_idx is None:
        # Tanpa MEMUTUSKAN, tidak ada cara memastikan mana klausul Menetapkan.
        # Aturan memilih diam.
        return None

    menetapkan_idx = None
    for i in range(memutuskan_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if not teks:
            continue
        if _PENGHENTI_MENETAPKAN.match(teks):
            # Sudah masuk batang tubuh tanpa melewati klausul Menetapkan.
            break
        if _AWAL_MENETAPKAN.match(teks):
            menetapkan_idx = i
            break

    if menetapkan_idx is None:
        return None

    # Ambil teks dari Menetapkan sampai akhir klausulnya.
    #
    # BUG YANG DIPERBAIKI 17 Sep 2026 — ditemukan pada RKMK 527 sungguhan.
    # Daftar penghenti lama cuma (BAB|Pasal|PERTAMA|KEDUA|KETIGA). Itu penomoran
    # diktum PMK. Diktum KMK dimulai "KESATU", yang tidak ada di daftar itu,
    # sehingga pengambilan melewati klausul Menetapkan dan menelan diktum KESATU
    # beserta seluruh isinya. Judul Menetapkan jadi sepanjang belasan paragraf,
    # lalu dilaporkan "berbeda dari judul pembuka" — padahal sama persis.
    # Penelaah melihat satu paragraf disorot tanpa ada yang salah di situ.
    parts: list[str] = []
    indeks: list[int] = []
    for i in range(menetapkan_idx, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if i > menetapkan_idx and _PENGHENTI_MENETAPKAN.match(teks):
            break
        parts.append(teks)
        indeks.append(i)
        # Judul pada Menetapkan diakhiri titik. Begitu ketemu, klausulnya
        # selesai — ini penghenti yang jauh lebih dapat diandalkan daripada
        # menebak kata apa yang datang sesudahnya. Titik di tengah nomor
        # peraturan (527/KMK.01/2022) tidak kena karena yang diperiksa hanya
        # akhir paragraf.
        if teks.endswith("."):
            break

    if not parts:
        return None

    gabungan = " ".join(parts)

    # Normalisasi: buang teks sampai label "Menetapkan", titik dua OPSIONAL.
    #
    # DIPERBAIKI 18 Sep 2026 — memperbaiki salah tandai yang terbukti.
    #
    # Titik dua sempat diwajibkan di sini, padahal `_AWAL_MENETAPKAN` di atas
    # sudah membuatnya opsional untuk naskah BERTABEL — di situ label
    # "Menetapkan" dan isinya jatuh di sel, dan karenanya di paragraf, yang
    # berbeda, sehingga paragraf labelnya cuma berbunyi "Menetapkan" tanpa
    # tanda apa pun. Perbaikan Kasus 3 hanya terpasang separuh: klausulnya
    # ketemu, tapi normalisasinya gagal.
    #
    # Akibatnya kata "Menetapkan" ikut terbawa ke dalam judul, awalan
    # "KEPUTUSAN MENTERI KEUANGAN TENTANG" tidak terpotong karena jangkar `^`
    # tidak lagi mengenai apa pun, dan judul yang SAMA PERSIS dengan judul
    # pembuka dilaporkan berbeda. Ditemukan 18 Sep 2026 lewat naskah uji KMK
    # bertabel di tools/contoh/.
    gabungan = re.sub(
        r"^.*?Menetapkan\b\s*:?\s*", "", gabungan, flags=re.IGNORECASE
    )

    # Buang awalan "PERATURAN/KEPUTUSAN MENTERI KEUANGAN TENTANG"
    gabungan = re.sub(
        r"^(PERATURAN|KEPUTUSAN)\s+MENTERI\s+KEUANGAN\s+(REPUBLIK\s+INDONESIA\s+)?TENTANG\s+",
        "",
        gabungan,
        flags=re.IGNORECASE,
    )

    # Rapatkan spasi DULU, baru buang titik di akhir. Urutannya penting:
    # kalau ada paragraf kosong sesudah klausul Menetapkan — bentuk yang lazim
    # di naskah nyata — teks gabungan berakhir dengan spasi, sehingga
    # rstrip(".") tidak mengenai apa pun dan judulnya tetap berakhiran titik.
    # Akibatnya judul yang sebenarnya konsisten dilaporkan tidak konsisten.
    gabungan = _trim(gabungan)
    gabungan = gabungan.rstrip(".").strip()

    # Jaring pengaman terakhir. Kalau hasilnya tidak masuk akal panjangnya,
    # pengambilannya gagal dan kita tidak tahu di mana. Melapor dalam keadaan
    # itu berarti menuduh judul yang mungkin sudah benar.
    if len(gabungan.split()) > _BATAS_KATA_JUDUL:
        return None

    return {
        "judul": gabungan,
        "paragraf_indeks": indeks,
    }


# Tanda baca penutup yang dibuang dari KEDUA judul sebelum dibandingkan.
#
# DITAMBAHKAN 18 Sep 2026 — memperbaiki salah tandai yang terbukti.
#
# Normalisasinya dulu tidak simetris: `_ekstrak_judul_menetapkan()` membuang
# titik di akhir (`rstrip(".")`), sedangkan judul pembuka dibandingkan apa
# adanya. Akibatnya naskah yang judul pembukanya diakhiri titik — kesalahan
# yang SUDAH dilaporkan F1-006 — membuat F1-002 ikut melapor "judulnya
# berbeda", padahal kata per katanya sama persis. Penelaah melihat dua tanda
# di dua tempat, salah satunya menuduh perbedaan yang tidak ada.
#
# Pembagian tugasnya sekarang tegas: F1-006 dan F1-012 mengurusi TANDA BACA
# penutupnya, F1-002 mengurusi ISI judulnya. Tidak saling menuduh.
_TANDA_BACA_PENUTUP = ".,;:"


def _samakan_untuk_banding(judul: str) -> str:
    """Bentuk judul yang dipakai membandingkan dua sisi. Simetris untuk keduanya."""
    return _trim(judul).upper().rstrip(_TANDA_BACA_PENUTUP).strip()


def _normalisasi_judul_pembuka(judul: str) -> str:
    """Normalisasi judul pembuka untuk perbandingan.

    Dipertahankan sebagai nama tersendiri supaya jelas sisi mana yang sedang
    dinormalkan, tetapi isinya kini sama persis dengan sisi Menetapkan —
    lihat `_samakan_untuk_banding()`.
    """
    return _samakan_untuk_banding(judul)


# ---------------------------------------------------------------------------
# Utilitas: parser Menimbang/Mengingat
# ---------------------------------------------------------------------------

def _ekstrak_bagian(
    paragraf: list[ParagrafInput],
    kata_kunci_mulai: str,
    kata_kunci_akhir: str,
) -> Optional[dict]:
    """Ekstrak teks dari bagian tertentu.

    Menangani dua bentuk:
    - Bentuk A: "Menimbang" berdiri sendiri, butir di paragraf sesudahnya
    - Bentuk B: "Menimbang : a. bahwa ..." menyatu dalam satu paragraf

    Returns dict:
        - 'teks_gabungan': seluruh teks bagian digabung
        - 'paragraf_mulai': indeks paragraf pertama
        - 'paragraf_akhir': indeks paragraf terakhir (eksklusif)
    """
    # Cari posisi kata kunci mulai
    mulai_idx = None
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        # Bentuk A: paragraf isinya persis kata kunci (mungkin diikuti " :")
        # Bentuk B: paragraf dimulai dengan kata kunci
        if (
            teks.upper() == kata_kunci_mulai.upper()
            or teks.upper().startswith(kata_kunci_mulai.upper() + " ")
            or teks.upper().startswith(kata_kunci_mulai.upper() + ":")
            or re.match(
                rf"^{re.escape(kata_kunci_mulai)}\s*:",
                teks,
                re.IGNORECASE,
            )
        ):
            mulai_idx = i
            break

    if mulai_idx is None:
        return None

    # Cari posisi kata kunci akhir
    akhir_idx = len(paragraf)
    for i in range(mulai_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if (
            teks.upper() == kata_kunci_akhir.upper()
            or teks.upper().startswith(kata_kunci_akhir.upper() + " ")
            or teks.upper().startswith(kata_kunci_akhir.upper() + ":")
            or re.match(
                rf"^{re.escape(kata_kunci_akhir)}\s*:",
                teks,
                re.IGNORECASE,
            )
        ):
            akhir_idx = i
            break

    # Gabungkan teks
    parts = [_trim(paragraf[i].teks) for i in range(mulai_idx, akhir_idx)]
    return {
        "teks_gabungan": " ".join(parts),
        "paragraf_mulai": mulai_idx,
        "paragraf_akhir": akhir_idx,
    }


def _pecah_butir_menimbang(teks_gabungan: str) -> list[str]:
    """Pecah teks Menimbang menjadi butir-butir berdasarkan penanda huruf.

    Menangani pola: a. bahwa ... ; b. bahwa ... ;

    Tanda titik koma di akhir butir SENGAJA dipertahankan — butir 22 KMK 527
    mensyaratkan butir terakhir diakhiri titik koma, jadi tandanya perlu ikut
    terbawa supaya bisa diperiksa.
    """
    # Hapus awalan "Menimbang :"
    teks = re.sub(r"^Menimbang\s*:\s*", "", teks_gabungan, flags=re.IGNORECASE)
    teks = teks.strip()

    # Pecah berdasarkan penanda huruf: a. / b. / c. dst.
    # Pattern: huruf kecil diikuti titik dan spasi, di awal atau sesudah pemisah
    butir_list = re.split(r"(?:^|\s)([a-z])\.\s+", teks)

    if len(butir_list) <= 1:
        # Tidak ada penanda huruf = satu butir saja
        return [teks] if teks else []

    # re.split dengan group menghasilkan: ['', 'a', 'teks a', 'b', 'teks b', ...]
    butir_hasil: list[str] = []
    i = 1  # Lewati elemen kosong pertama
    while i < len(butir_list) - 1:
        huruf = butir_list[i]
        isi = butir_list[i + 1].strip()
        butir_hasil.append(f"{huruf}. {isi}")
        i += 2

    return butir_hasil


# ---------------------------------------------------------------------------
# Aturan 1: cek_judul_kapital (F1-001)
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# F1-001 DINONAKTIFKAN — 17 Sep 2026
# ---------------------------------------------------------------------------
#
# Aturan ini tidak bisa membedakan judul yang hurufnya memang campur dari judul
# yang TERSIMPAN campur tetapi DITAMPILKAN kapital lewat atribut/gaya All Caps.
# Di RKMK 527 sungguhan, gaya "ALL CAPS" dipakai pada blok judul: yang tersimpan
# "Perubahan Atas Keputusan Menteri Keuangan Nomor ...", yang terbaca di layar
# "PERUBAHAN ATAS KEPUTUSAN MENTERI KEUANGAN NOMOR ...". Aturan menemukan huruf
# kecil sungguhan, tapi huruf kecil yang tidak bisa dilihat siapa pun.
#
# Penjaga tampil_kapital yang sempat dipasang bergantung pada font.allCaps
# (WordApiDesktop 1.3) dan terbukti tidak menolong di Word penelaah — belum
# jelas apakah karena requirement set-nya tidak ada atau karena properti itu
# buta terhadap kapital yang datang dari gaya paragraf.
#
# Kaidah yang dipegang: apa pun yang disorot alat ini wajib benar-benar salah.
# Aturan yang tidak bisa membuktikan kesalahannya tidak boleh menyorot. Jadi
# aturan ini dimatikan sampai ada cara deteksi yang terbukti — kandidatnya
# membaca OOXML paragraf (Range.getOoxml(), WordApi 1.1) dan mencari penanda
# <w:caps/>, tetapi itu BELUM diuji dan tidak boleh dipasang sebelum diuji.
#
# Fungsinya sengaja TIDAK dihapus: logikanya masih benar untuk naskah yang
# hurufnya betul-betul campur, dan tesnya masih menjaga logika itu. Yang
# dihapus hanya pemanggilannya dari jalankan_semua().
AKTIFKAN_F1_001 = False


def cek_judul_kapital(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """Cek apakah judul ditulis kapital seluruhnya.

    Judul = gabungan paragraf sesudah anchor TENTANG sampai penutup.

    TIDAK dipanggil jalankan_semua() saat ini — lihat AKTIFKAN_F1_001 di atas.
    """
    info_judul = _ekstrak_judul_pembuka(paragraf, jenis)
    if info_judul is None:
        return []

    temuan: list[Temuan] = []
    for idx in info_judul["paragraf_indeks"]:
        p = paragraf[idx]

        # Paragraf yang ditampilkan kapital lewat atribut All Caps sudah
        # memenuhi kaidahnya di mata pembaca, meskipun huruf aslinya campur.
        # Menandainya berarti salah tandai: usulan .upper() tidak mengubah
        # apa pun yang terlihat, dan penelaah melihat coretan yang isinya
        # sama persis dengan penggantinya. Ditemukan pada RKMK sungguhan
        # 17 Sep 2026.
        if p.tampil_kapital:
            continue

        # Offset dihitung terhadap p.teks APA ADANYA, bukan versi .strip()-nya.
        # LokasiTemuan.teks_asli diiris dari p.teks, dan frontend mencocokkan
        # irisan itu ke dokumen Word; menghitung dari teks yang sudah dipangkas
        # membuat seluruh penandaan bergeser sepanjang spasi di awal paragraf.
        for mulai, akhir in _rentang_kata_huruf_kecil(p.teks):
            cuplikan = p.teks[mulai:akhir]
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-001",
                    # CATATAN, bukan PENGGANTIAN — diubah 17 Sep 2026.
                    #
                    # Kalau paragrafnya ternyata ditampilkan kapital lewat
                    # atribut All Caps sementara hurufnya tersimpan campur,
                    # penggantian menghasilkan coretan yang di layar terlihat
                    # sama persis dengan penggantinya — penelaah melihat kata
                    # kapital dicoret lalu diganti kata kapital yang sama.
                    # Blok kuning + komentar tidak punya masalah itu.
                    jenis_tanda=JenisTanda.CATATAN,
                    paragraf=p,
                    offset_mulai=mulai,
                    panjang=akhir - mulai,
                    catatan=(
                        "Judul peraturan ditulis kapital seluruhnya; bagian "
                        "yang ditandai masih memuat huruf kecil."
                    ),
                    usulan_rumusan=cuplikan.upper(),
                )
            )

    return temuan


# ---------------------------------------------------------------------------
# Aturan 2: cek_judul_konsisten (F1-002)
# ---------------------------------------------------------------------------

def cek_judul_konsisten(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """Cek apakah judul di pembuka konsisten dengan judul pada Menetapkan.

    Dua sisi TIDAK simetris — perlu normalisasi:
    - Pembuka: judul berdiri sendiri tanpa awalan
    - Menetapkan: judul memakai awalan dan titik akhir
    """
    info_pembuka = _ekstrak_judul_pembuka(paragraf, jenis)
    info_menetapkan = _ekstrak_judul_menetapkan(paragraf)

    if info_pembuka is None or info_menetapkan is None:
        return []

    judul_pembuka = _normalisasi_judul_pembuka(info_pembuka["judul"])
    judul_menetapkan = _samakan_untuk_banding(info_menetapkan["judul"])

    if judul_pembuka == judul_menetapkan:
        return []

    if not info_menetapkan["paragraf_indeks"]:
        return []

    # --- Cari BAGIAN MANA yang berbeda, bukan sekadar "berbeda" -------------
    #
    # Dulu seluruh paragraf Menetapkan disorot. Pada naskah nyata paragraf itu
    # memuat "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG ..." sepanjang
    # beberapa baris, dan yang berbeda dari judul pembuka bisa cuma satu kata.
    # SequenceMatcher dipakai untuk mengambil kata-kata yang benar-benar beda
    # di sisi Menetapkan.
    kata_pembuka = judul_pembuka.split()
    kata_menetapkan = judul_menetapkan.split()

    # Tiap frasa dibawa BERIKUT kemunculan ke-berapa ia di judul Menetapkan.
    # Tanpa itu, frasa yang muncul dua kali disorot di kemunculan pertama —
    # padahal yang berlebih justru yang kedua (PMK 45 Tahun 2026).
    frasa_beda: list[tuple[str, int]] = []
    kata_hilang: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, kata_pembuka, kata_menetapkan
    ).get_opcodes():
        if tag == "equal":
            continue
        if j2 > j1:
            frasa = " ".join(kata_menetapkan[j1:j2])
            frasa_beda.append((frasa, _ordinal_frasa(kata_menetapkan, frasa, j1)))
        else:
            # Ada di judul pembuka tapi tidak ada di Menetapkan \u2014 tidak ada
            # yang bisa disorot di naskah; disebut di catatan saja.
            kata_hilang.append(" ".join(kata_pembuka[i1:i2]))

    catatan_dasar = (
        "Judul pada Menetapkan harus sama persis dengan judul pembuka \u2014 "
        "di sini berbeda. Mana yang benar ditentukan penelaah. Judul pembuka: "
        f"\"{info_pembuka['judul']}\"."
    )

    temuan: list[Temuan] = []
    for frasa, ordinal in frasa_beda:
        letak: Optional[tuple[int, int, int]] = None  # (idx, mulai, akhir)
        for kandidat in info_menetapkan["paragraf_indeks"]:
            # Ordinalnya dihitung pada judul yang SUDAH dinormalkan, sedangkan
            # yang dicari paragraf MENTAH — yang masih memuat awalan
            # "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG". Kalau frasanya
            # kebetulan juga ada di awalan itu, penomorannya bergeser.
            #
            # Jadi ordinalnya hanya dipakai kalau jumlah kemunculan di kedua
            # sisi memang sama. Kalau tidak, kembali ke perilaku lama —
            # menyorot yang pertama. Menebak di luar itu lebih berbahaya
            # daripada tidak setepat mungkin.
            teks_kandidat = paragraf[kandidat].teks
            sejajar = _hitung_frasa(teks_kandidat, frasa) == _hitung_frasa(
                judul_menetapkan, frasa
            )
            posisi = _cari_frasa(
                teks_kandidat, frasa, ordinal if sejajar else 0
            )
            if posisi is not None:
                letak = (kandidat, posisi[0], posisi[1])
                break
        if letak is None:
            # Frasanya terpotong antarparagraf; lewati, biar tidak menandai
            # tempat yang salah. Kalau semua frasa bernasib begini, cadangan
            # di bawah yang jalan.
            continue
        idx_frasa, mulai, akhir = letak
        temuan.append(
            _buat_temuan(
                aturan_id="F1-002",
                jenis_tanda=JenisTanda.CATATAN,
                paragraf=paragraf[idx_frasa],
                offset_mulai=mulai,
                panjang=akhir - mulai,
                catatan=catatan_dasar,
            )
        )

    if temuan:
        return temuan

    # Cadangan: tidak ada satu pun frasa beda yang bisa ditemukan letaknya \u2014
    # entah karena yang salah justru ada yang HILANG dari Menetapkan, entah
    # karena frasanya terpotong antarparagraf.
    #
    # DIPERBAIKI 18 Sep 2026, DIPERBAIKI LAGI 27 Sep 2026.
    #
    # Cadangan MULA-MULA menandai SATU PARAGRAF PENUH (`offset_mulai=0,
    # panjang=len(p.teks.strip())`), termasuk label "Menetapkan : " yang
    # bukan bagian judul sama sekali. Itu melanggar CLAUDE.md butir 6 dan
    # berakhir menimpa naskah \u2014 lihat kasus 9 di test_format_baku.py.
    #
    # Perbaikan 18 Sep menghapus lokasinya sama sekali (temuan TANPA LOKASI,
    # tampil sebagai peringatan dokumen sebaris). Itu memang berhenti
    # menyalahi naskah, tapi membawa cacat baru: temuannya tidak pernah
    # dikomentari di Word dan tidak bisa Terima/Tolak \u2014 penelaah menyebutnya
    # bug, karena komentar Word juga yang dibawa ke rapat pembahasan bersama
    # pemrakarsa, dan peringatan sebaris di panel hilang begitu add-in
    # ditutup.
    #
    # Sekarang dipakai anchor NETRAL \u2014 lihat `_anchor_dokumen`. Bukan tebakan
    # "di mana bagian yang hilang seharusnya berada" (itu justru kesalahan
    # yang sama dengan cadangan mula-mula), melainkan baris judul pembuka
    # dokumen, yang tidak pernah jadi bagian dari klaim "ini yang salah".
    # `tanpa_sorot=True` menjaga bedanya: Word tetap mengomentari dan
    # membungkusnya (jadi Terima/Tolak berfungsi normal), tapi TIDAK
    # mewarnainya \u2014 supaya baris judul tidak terlihat seolah teksnya sendiri
    # yang keliru.
    tambahan = (
        f" Bagian yang tidak ada di Menetapkan: \"{'; '.join(kata_hilang)}\"."
        if kata_hilang
        else ""
    )
    anchor = _anchor_dokumen(paragraf)
    if anchor is None:
        # Tidak ada satu pun paragraf berisi teks di seluruh dokumen \u2014 kalau
        # sampai di sini, sesuatu yang lain sudah pasti gagal lebih dulu.
        # Diam sepenuhnya lebih aman daripada memaksakan anchor yang tidak
        # ada.
        return []
    p_anchor, mulai, panjang = anchor
    return [
        _buat_temuan(
            aturan_id="F1-002",
            jenis_tanda=JenisTanda.CATATAN,
            paragraf=p_anchor,
            offset_mulai=mulai,
            panjang=panjang,
            catatan=(
                catatan_dasar
                + tambahan
                + " Letak persisnya tidak bisa ditunjuk di naskah \u2014 periksa"
                " klausul Menetapkan sendiri."
            ),
            tanpa_sorot=True,
        )
    ]


# ---------------------------------------------------------------------------
# Aturan 3: cek_kelengkapan_struktur (F1-003)
# ---------------------------------------------------------------------------

_BAGIAN_WAJIB = ["Menimbang", "Mengingat", "Menetapkan"]


def cek_kelengkapan_struktur(
    paragraf: list[ParagrafInput], jenis: Optional[JenisDokumen] = None
) -> list[Temuan]:
    """Cek keberadaan bagian wajib pembukaan.

    Menimbang, Mengingat, dan Menetapkan untuk kedua jenis; ditambah frasa
    "Dengan Rahmat Tuhan Yang Maha Esa" KHUSUS PMK — butir 13 menyebut
    kekhususan itu dengan kata-katanya sendiri, jadi menerapkannya ke KMK
    justru salah tandai.

    `jenis` opsional supaya pemanggil lama tidak pecah; dihilangkan berarti
    pemeriksaan frasa itu dilewati.
    """
    temuan: list[Temuan] = []
    ada_yang_ketemu = False

    for bagian in _BAGIAN_WAJIB:
        ditemukan = False
        for p in paragraf:
            teks = _trim(p.teks)
            if (
                teks.upper() == bagian.upper()
                or teks.upper().startswith(bagian.upper() + " ")
                or teks.upper().startswith(bagian.upper() + ":")
                or re.match(
                    rf"^{re.escape(bagian)}\s*:", teks, re.IGNORECASE
                )
            ):
                ditemukan = True
                ada_yang_ketemu = True
                break

        if not ditemukan:
            # Ketiadaan sesuatu tidak punya lokasi untuk ditunjuk secara
            # jujur — anchor-nya NETRAL (baris judul pembuka dokumen), sama
            # seperti cadangan F1-002. Lihat `_anchor_dokumen` untuk kenapa
            # ini BUKAN pengulangan kesalahan "menyorot satu paragraf penuh"
            # yang sudah pernah menimpa naskah (CLAUDE.md butir 6).
            anchor = _anchor_dokumen(paragraf)
            if anchor is not None:
                p_anchor, mulai, panjang = anchor
                temuan.append(
                    _buat_temuan(
                        aturan_id="F1-003",
                        jenis_tanda=JenisTanda.CATATAN,
                        paragraf=p_anchor,
                        offset_mulai=mulai,
                        panjang=panjang,
                        catatan=(
                            f"Bagian \"{bagian}\" tidak ditemukan. Menimbang, "
                            "Mengingat, dan Menetapkan wajib ada pada tiap "
                            "rancangan."
                        ),
                        tanpa_sorot=True,
                    )
                )

    # --- Frasa "Dengan Rahmat Tuhan Yang Maha Esa", KHUSUS PMK -------------
    #
    # Butir 13 menyebut kekhususannya dengan kata-katanya sendiri: "a. Frasa
    # Dengan Rahmat Tuhan Yang Maha Esa (khusus PMK)". Jadi KMK tidak boleh
    # ikut diperiksa — kalau ikut, tiap KMK yang benar akan dituduh cacat.
    #
    # BATAS KEWAJARAN (CLAUDE.md butir 2): hanya dilaporkan kalau setidaknya
    # SATU bagian pembukaan lain memang terbaca. Kalau tidak satu pun ketemu,
    # yang terjadi hampir pasti blok pembukaannya tidak sampai ke parser —
    # mis. tersimpan dalam bentuk yang belum terbaca — dan menambahkan tuduhan
    # keempat di atas naskah yang memang belum terbaca tidak menolong siapa
    # pun. Dalam keadaan itu aturan MEMILIH DIAM.
    if jenis == JenisDokumen.PMK and ada_yang_ketemu:
        gabungan = " ".join(_trim(p.teks) for p in paragraf).upper()
        gabungan = re.sub(r"\s+", " ", gabungan)
        if _PENUTUP_JUDUL_PMK not in gabungan:
            # Anchor netral yang sama dengan cadangan di atas — lihat
            # `_anchor_dokumen`. Ketiadaan frasa ini juga bukan kata tertentu
            # yang salah, jadi tidak boleh menebak lokasi.
            anchor = _anchor_dokumen(paragraf)
            if anchor is not None:
                p_anchor, mulai, panjang = anchor
                temuan.append(
                    _buat_temuan(
                        aturan_id="F1-003",
                        jenis_tanda=JenisTanda.CATATAN,
                        paragraf=p_anchor,
                        offset_mulai=mulai,
                        panjang=panjang,
                        catatan=(
                            "Frasa \"DENGAN RAHMAT TUHAN YANG MAHA ESA\" tidak "
                            "ditemukan. Butir 13 menetapkannya sebagai bagian "
                            "pembukaan PMK, diletakkan di antara judul dan "
                            "jabatan pembentuk. Khusus PMK — KMK memang tidak "
                            "memakainya."
                        ),
                        tanpa_sorot=True,
                    )
                )

    return temuan


# ---------------------------------------------------------------------------
# Aturan 4: cek_frasa_baku_menimbang (F1-004)
# ---------------------------------------------------------------------------

# Bunyi baku butir Menimbang terakhir (KMK 527 Lampiran II butir 22):
#   PMK: "bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf ...,
#         perlu menetapkan Peraturan Menteri Keuangan tentang ...;"
#   KMK: sama, dengan "Keputusan Menteri Keuangan"
# Bagian "huruf ..." dan judul sesudah "tentang" bebas isinya; yang wajib persis
# adalah kata-kata di sekitarnya, nama jenis peraturannya, dan titik komanya.

_FRASA_BERDASARKAN = "berdasarkan pertimbangan sebagaimana dimaksud dalam huruf"
_FRASA_PERLU_MENETAPKAN = "perlu menetapkan"

_FRASA_JENIS = {
    "PMK": "peraturan menteri keuangan tentang",
    "KMK": "keputusan menteri keuangan tentang",
}

_NAMA_JENIS = {
    "PMK": "Peraturan Menteri Keuangan",
    "KMK": "Keputusan Menteri Keuangan",
}


def cek_frasa_baku_menimbang(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """Cek frasa baku butir Menimbang terakhir (KMK 527 butir 22).

    Berlaku HANYA kalau Menimbang punya lebih dari satu butir (ada huruf a/b/c).
    Kalau cuma satu butir tanpa huruf → lewati (bentuk sah, KMK 527 butir 19).

    Empat bagian yang diperiksa pada butir terakhir:
      1. frasa "bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf"
      2. frasa "perlu menetapkan"
      3. nama jenis peraturan sesuai dokumennya, diikuti kata "tentang"
      4. diakhiri tanda titik koma (;)
    """
    bagian = _ekstrak_bagian(paragraf, "Menimbang", "Mengingat")
    if bagian is None:
        return []

    butir_list = _pecah_butir_menimbang(bagian["teks_gabungan"])

    # Kalau <= 1 butir, bentuk sah — lewati
    if len(butir_list) <= 1:
        return []

    butir_terakhir_asli = butir_list[-1].strip()
    butir_terakhir = _trim(butir_terakhir_asli).lower()

    kekurangan: list[str] = []

    if _FRASA_BERDASARKAN not in butir_terakhir:
        kekurangan.append(
            "frasa \"berdasarkan pertimbangan sebagaimana dimaksud dalam huruf\""
        )

    if _FRASA_PERLU_MENETAPKAN not in butir_terakhir:
        kekurangan.append("frasa \"perlu menetapkan\"")

    # Jenis dokumen datang dari pilihan penelaah, bukan tebakan. Karena itu
    # tidak ada lagi cabang "jenis tidak diketahui" yang dulu diam-diam
    # melemahkan pemeriksaan jadi sekadar mencari kata "tentang".
    if _FRASA_JENIS[jenis.value] not in butir_terakhir:
        kekurangan.append(
            f"nama jenis \"{_NAMA_JENIS[jenis.value]}\" sebelum kata \"tentang\""
        )

    if not butir_terakhir_asli.endswith(";"):
        kekurangan.append("titik koma di akhir butir")

    if not kekurangan:
        return []

    # --- Cari paragraf yang BENAR-BENAR memuat butir terakhir -----------------
    #
    # BUG YANG DIPERBAIKI 18 Sep 2026 — ditemukan pada PMK 119 sungguhan.
    # Dulu lokasinya diambil begitu saja dari paragraf_akhir - 1, yaitu paragraf
    # tepat sebelum "Mengingat". Pada naskah nyata paragraf itu sering BARIS
    # KOSONG. Akibatnya teks_asli kosong, panjangnya nol, tidak ada yang bisa
    # ditandai di Word — dan penelaah melihat kartu tanpa cuplikan, tanpa warna,
    # tanpa komentar, tapi dengan tombol Terima/Tolak yang tidak mengerjakan
    # apa pun.
    #
    # Sekarang paragrafnya dicari dari isi butirnya sendiri. Penanda hurufnya
    # dibuang lebih dulu: pada naskah bertabel, huruf "c." dan isi butirnya
    # berada di sel — dan karenanya di paragraf — yang berbeda.
    isi_butir = re.sub(r"^[a-z]\.\s*", "", _trim(butir_terakhir_asli))
    petunjuk = " ".join(isi_butir.split()[:8])

    idx_temuan = None
    for i in range(bagian["paragraf_mulai"], bagian["paragraf_akhir"]):
        if _cari_frasa(paragraf[i].teks, petunjuk) is not None:
            idx_temuan = i
            break

    if idx_temuan is None:
        # Tidak tahu di mana butirnya berada. Menandai paragraf asal-asalan
        # melanggar kaidah "yang ditandai wajib benar-benar salah" — diam saja.
        return []

    p = paragraf[idx_temuan]

    # --- Persempit sasaran sorotan -----------------------------------------
    #
    # Yang dipersoalkan aturan ini adalah bunyi SATU butir, bukan seluruh
    # paragraf — dan sebuah paragraf Menimbang kerap memuat beberapa butir
    # sekaligus. Urutan percobaan: butir utuh, lalu pembukanya saja, baru
    # paragraf penuh sebagai cadangan.
    mulai, panjang = 0, len(p.teks.strip())

    if kekurangan == ["titik koma di akhir butir"]:
        # Satu-satunya yang kurang cuma tanda bacanya. Sorotan sepanjang butir
        # untuk itu berlebihan; tandai karakter terakhirnya saja.
        akhir_isi = len(p.teks.rstrip())
        if akhir_isi > 0:
            mulai, panjang = akhir_isi - 1, 1
    else:
        # Butir utuh dulu; kalau terpotong antarparagraf, pakai pembukanya saja —
        # itu sudah pasti ada, karena paragrafnya memang dipilih berdasarkan
        # petunjuk ini.
        posisi = _cari_frasa(p.teks, isi_butir) or _cari_frasa(p.teks, petunjuk)
        if posisi is not None:
            mulai, panjang = posisi[0], posisi[1] - posisi[0]

    return [
        _buat_temuan(
            aturan_id="F1-004",
            jenis_tanda=JenisTanda.CATATAN,
            paragraf=p,
            offset_mulai=mulai,
            panjang=panjang,
            # DIUBAH 18 Sep 2026 sesudah butir 22 dibaca. Butir itu berbunyi
            # "rumusan butir pertimbangan terakhir PADA UMUMNYA berbunyi
            # sebagai berikut" — bukan "wajib". Menyimpang darinya belum tentu
            # kesalahan, jadi kalimatnya tidak boleh terdengar seperti vonis.
            # Kalimat lama, "belum memakai bunyi baku", menuduh lebih jauh
            # daripada yang didukung sumbernya.
            catatan=(
                "Butir Menimbang terakhir berbeda dari rumusan yang lazim. "
                "Tidak ada: "
                + "; ".join(kekurangan)
                + ". Butir 22 menyebut rumusan ini \"pada umumnya\", bukan "
                "keharusan — penelaah yang menimbang apakah perbedaan ini "
                "perlu dibetulkan."
            ),
        )
    ]


# ---------------------------------------------------------------------------
# Aturan 5: cek_ejaan (F1-005)
# ---------------------------------------------------------------------------

# Ejaan baku peraturan yang sering salah — bentuk paling sederhana dulu.
# Fokus pada ejaan khusus penyusunan peraturan, bukan typo umum.
# Urutan: frasa yang lebih panjang ditaruh lebih dulu.
_POLA_EJAAN: list[dict] = [
    {
        "salah": re.compile(r"\bperaturan\s+pemerintah\s+pengganti\s+undang-undang\b", re.IGNORECASE),
        "benar_cek": lambda m: m.group(0) != "Peraturan Pemerintah Pengganti Undang-Undang",
        "saran": "Peraturan Pemerintah Pengganti Undang-Undang",
        "catatan": "Nama jenis peraturan mengikuti ejaan baku.",
    },
    {
        "salah": re.compile(r"\bundang-undang\b", re.IGNORECASE),
        "benar_cek": lambda m: m.group(0) != "Undang-Undang",
        "saran": "Undang-Undang",
        # Nomor butirnya TIDAK ditulis di sini — itu tugas tabel rujukan
        # (rujukan_kmk527.py), supaya tidak ada dua sumber yang bisa berbeda.
        "catatan": "Nama jenis peraturan ditulis dengan huruf kapital pada kedua unsurnya.",
    },
]


def _ekstrak_rentang_mengingat(paragraf: list[ParagrafInput]) -> tuple[int, int]:
    """Cari rentang indeks paragraf untuk bagian Mengingat.

    Returns (mulai_idx, akhir_idx) dimana akhir_idx adalah eksklusif.
    Jika tidak ditemukan, return (-1, -1).
    """
    mulai_idx = -1
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        if (
            teks.upper() == "MENGINGAT"
            or teks.upper().startswith("MENGINGAT ")
            or teks.upper().startswith("MENGINGAT:")
            or re.match(r"^Mengingat\s*:", teks, re.IGNORECASE)
        ):
            mulai_idx = i
            break

    if mulai_idx == -1:
        return -1, -1

    akhir_idx = len(paragraf)
    for i in range(mulai_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        # Bentuk berspasi "M E M U T U S K A N :" ikut menghentikan, lewat
        # _POLA_MEMUTUSKAN. Tanpa itu, rentang Mengingat bisa membentang jauh
        # ke batang tubuh dan cek_ejaan menandai rujukan generik yang bukan
        # dasar hukum — kesalahan yang sudah pernah dilaporkan penelaah.
        if _POLA_MEMUTUSKAN.match(teks) or re.match(
            r"^(Menetapkan|BAB\s|Pasal\s)", teks, re.IGNORECASE
        ):
            akhir_idx = i
            break

    return mulai_idx, akhir_idx


def cek_ejaan(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek ejaan baku penyusunan peraturan.

    Bentuk paling sederhana: hanya ejaan khusus peraturan.
    BUKAN kamus besar bahasa Indonesia.
    """
    temuan: list[Temuan] = []

    # SELURUH pemeriksaan di sini dibatasi pada bagian Mengingat.
    #
    # DIPERSEMPIT 18 Sep 2026, setelah naskah Lampiran II dibaca. Kedua butir
    # yang mendasari aturan ini berbicara tentang DASAR HUKUM, bukan seluruh
    # dokumen:
    #   butir 32 — "Penulisan judul peraturan perundang-undangan yang
    #               DIJADIKAN DASAR HUKUM, diawali dengan huruf kapital,
    #               kecuali kata 'tentang' dan kata penghubung/konjungsi."
    #   butir 33 — "Jika terdapat DASAR HUKUM berupa Undang-Undang, kedua
    #               huruf u ditulis dengan huruf kapital."
    #
    # Sebelumnya pola "Undang-Undang" berlaku di seluruh dokumen, dan pada PMK
    # sungguhan ia menandai rujukan generik di dalam Lampiran — "…atau
    # undang-undang yang mengatur mengenai pencegahan…" — yang sama sekali
    # bukan dasar hukum. Penelaah melaporkannya sebagai janggal, dan memang
    # janggal.
    mulai_mengingat, akhir_mengingat = _ekstrak_rentang_mengingat(paragraf)
    if mulai_mengingat == -1:
        return []

    dalam_mengingat = paragraf[mulai_mengingat:akhir_mengingat]

    # 1. Nama jenis peraturan (Undang-Undang, Perppu)
    for p in dalam_mengingat:
        teks = p.teks
        spans_tercatat: list[tuple[int, int]] = []
        for pola in _POLA_EJAAN:
            for match in pola["salah"].finditer(teks):
                start, end = match.start(), match.end()
                # Lewati jika span tumpang tindih dengan temuan frasa yang lebih panjang
                if any(not (end <= s or start >= e) for s, e in spans_tercatat):
                    continue
                if pola["benar_cek"](match):
                    spans_tercatat.append((start, end))
                    temuan.append(
                        _buat_temuan(
                            aturan_id="F1-005",
                            jenis_tanda=JenisTanda.PENGGANTIAN,
                            paragraf=p,
                            offset_mulai=start,
                            panjang=end - start,
                            catatan=pola["catatan"],
                            usulan_rumusan=pola["saran"],
                        )
                    )

    # 2. Butir 32: kata "tentang" tetap huruf kecil di dalam judul peraturan
    #    pada dasar hukum.
    for p in dalam_mengingat:
        for match in re.finditer(r"\btentang\b", p.teks, re.IGNORECASE):
            if match.group(0) != "tentang":
                temuan.append(
                    _buat_temuan(
                        aturan_id="F1-005",
                        jenis_tanda=JenisTanda.PENGGANTIAN,
                        paragraf=p,
                        offset_mulai=match.start(),
                        panjang=match.end() - match.start(),
                        catatan=(
                            "Kata \"tentang\" dalam judul peraturan pada "
                            "dasar hukum tetap ditulis dengan huruf kecil."
                        ),
                        usulan_rumusan="tentang",
                    )
                )

    return temuan


# ---------------------------------------------------------------------------
# Aturan 6-12: butir yang terverifikasi visual 18 Sep 2026
# ---------------------------------------------------------------------------
#
# Ketujuh aturan di bawah dikutip dari pindaian KMK 527 Lampiran II halaman 30,
# 35, 36, dan 37 — bukan dari ekstraksi teks, bukan dari dugaan. Semuanya
# IMPERATIF di naskahnya, berbeda dari F1-004 yang bersandar pada butir 22 yang
# cuma menyebut "pada umumnya".
#
# SATU BAHAYA YANG MEMBAYANGI SEMUANYA: naskah PMK/KMK sungguhan menaruh label
# "Menimbang", "Mengingat", dan "Menetapkan" di dalam TABEL, sehingga labelnya
# dan titik duanya jatuh di sel — dan karenanya di paragraf — yang berbeda.
# Paragraf labelnya lalu cuma berbunyi "Menimbang", tanpa tanda apa pun.
#
# Aturan yang menuntut titik dua akan salah tandai di naskah seperti itu. Karena
# itu semuanya MEMILIH DIAM ketika paragraf labelnya berdiri sendiri: kita tidak
# bisa membuktikan titik duanya hilang, jadi kita tidak menuduh.


def _jendela_label(
    paragraf: list[ParagrafInput], label: str
) -> Optional[tuple[int, int]]:
    """Rentang paragraf [mulai, akhir) tempat sebuah label bagian boleh dicari.

    DITAMBAHKAN 18 Sep 2026 — memperbaiki salah tandai yang terbukti.

    Tanpa jendela, `_cek_label_bagian()` menyapu SELURUH dokumen mencari
    paragraf yang diawali labelnya. Pada KMK bertabel, "KESATU" dan isi
    diktumnya jatuh di paragraf berbeda, sehingga isi diktum berbunyi
    "Menetapkan Pedoman ... sebagaimana tercantum dalam Lampiran ..." —
    diawali kata "Menetapkan" tanpa titik dua. Aturan lalu menuduh batang
    tubuh yang sama sekali tidak bersalah.

    Ini persis bug Kasus 3 (bagian 6.10) yang sudah ditutup untuk F1-002,
    lahir kembali di aturan yang ditambahkan belakangan. Obatnya sama:
    tiap label punya letak yang pasti menurut KMK 527, dan kata yang sama di
    luar letak itu adalah kata biasa, bukan label bagian.

        Menimbang (butir 16) — di pembukaan, sebelum MEMUTUSKAN
        Mengingat (butir 23) — di pembukaan, sebelum MEMUTUSKAN
        Menetapkan (butir 38) — sesudah MEMUTUSKAN, sebelum batang tubuh

    Tanpa MEMUTUSKAN di dokumen, batas pembukaan tidak bisa dipastikan sama
    sekali, jadi aturannya MEMILIH DIAM — sejalan dengan
    `_ekstrak_judul_menetapkan()` yang sudah lebih dulu begitu.
    """
    memutuskan_idx = _cari_index_memutuskan(paragraf)
    if memutuskan_idx is None:
        return None

    if label.upper() != "MENETAPKAN":
        return (0, memutuskan_idx)

    akhir = len(paragraf)
    for i in range(memutuskan_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if teks and _PENGHENTI_MENETAPKAN.match(teks):
            akhir = i
            break
    return (memutuskan_idx + 1, akhir)


def _cek_label_bagian(
    paragraf: list[ParagrafInput],
    label: str,
    aturan_id: str,
) -> list[Temuan]:
    """Periksa penulisan label bagian: huruf awal kapital, diakhiri titik dua.

    Dipakai bersama oleh F1-007 (Menimbang, butir 16), F1-009 (Mengingat,
    butir 23), dan F1-011 (Menetapkan, butir 38) — ketiganya berbunyi sama.

    Hanya KEMUNCULAN PERTAMA di dalam jendelanya yang diperiksa, lalu fungsi
    ini berhenti. Sebelum 18 Sep 2026 pemindaian justru BERLANJUT setiap kali
    labelnya ternyata sudah benar — komentar `break` di bawah menjanjikan
    "satu label, satu kali periksa" padahal cabang normalnya memakai
    `continue`. Akibatnya naskah yang memuat kata itu lagi di tempat lain
    menghasilkan temuan kedua, kadang dengan rentang yang sama persis dengan
    temuan pertama — dua tanda di satu rentang tidak bisa digambar maupun
    dicabut sendiri-sendiri di Word.
    """
    temuan: list[Temuan] = []

    jendela = _jendela_label(paragraf, label)
    if jendela is None:
        return []
    mulai_jendela, akhir_jendela = jendela

    for p in paragraf[mulai_jendela:akhir_jendela]:
        teks = p.teks.strip()
        if not teks or not teks.upper().startswith(label.upper()):
            continue

        # Pastikan ini benar-benar labelnya, bukan kata lain yang kebetulan
        # berawalan sama. Sesudah labelnya harus ada batas kata.
        sisa = teks[len(label) :]
        if sisa and sisa[0].isalnum():
            continue

        tertulis = teks[: len(label)]
        mulai = p.teks.index(tertulis)

        # 1. Huruf awal kapital, sisanya kecil. "MENIMBANG" dan "menimbang"
        #    dua-duanya menyimpang dari butir 16/23/38.
        if tertulis != label:
            temuan.append(
                _buat_temuan(
                    aturan_id=aturan_id,
                    jenis_tanda=JenisTanda.PENGGANTIAN,
                    paragraf=p,
                    offset_mulai=mulai,
                    panjang=len(tertulis),
                    catatan=(
                        f"Kata \"{label}\" ditulis dengan huruf awal kapital, "
                        "selebihnya huruf kecil."
                    ),
                    usulan_rumusan=label,
                )
            )

        # 2. Diakhiri titik dua.
        #
        # Ketiga cabang di bawah sama-sama MENGAKHIRI pemeriksaan: labelnya
        # sudah ketemu, dan kemunculan berikutnya di dokumen bukan label lagi.
        sisa_bersih = sisa.strip()
        if not sisa_bersih:
            # Label berdiri sendiri di paragrafnya. Pada naskah bertabel,
            # titik duanya ada di sel sebelah dan tidak terbaca dari sini.
            # Tidak bisa dibuktikan hilang -> tidak dituduhkan.
            break
        if sisa_bersih.startswith(":"):
            break

        # Ada isi sesudah label tapi bukan titik dua -> titik duanya memang
        # tidak ada. Yang ditandai labelnya saja, bukan seluruh baris.
        temuan.append(
            _buat_temuan(
                aturan_id=aturan_id,
                jenis_tanda=JenisTanda.CATATAN,
                paragraf=p,
                offset_mulai=mulai,
                panjang=len(tertulis),
                catatan=(
                    f"Kata \"{label}\" diakhiri tanda baca titik dua (:)."
                ),
                usulan_rumusan=f"{label} :",
            )
        )
        break  # satu label, satu kali periksa

    return temuan


def cek_judul_tanpa_tanda_baca(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """F1-006 — butir 8: judul tidak diakhiri tanda baca."""
    info = _ekstrak_judul_pembuka(paragraf, jenis)
    if info is None:
        return []

    # Paragraf judul TERAKHIR yang ada isinya. Blok judul kerap diikuti baris
    # kosong sebelum penutupnya; memeriksa baris kosong tidak ada gunanya.
    idx_terakhir = None
    for idx in info["paragraf_indeks"]:
        if paragraf[idx].teks.strip():
            idx_terakhir = idx
    if idx_terakhir is None:
        return []

    p = paragraf[idx_terakhir]
    teks = p.teks.rstrip()

    # Kurung tutup sengaja TIDAK ikut dilarang: judul yang memuat akronim
    # berkurung memang dicontohkan butir 8 sebagai bentuk yang salah, tetapi
    # yang dipersoalkan di situ akronimnya, bukan tanda kurungnya. Menuduh
    # tanda kurung berarti menuduh hal yang tidak diatur butir ini.
    if not teks.endswith((".", ",", ";", ":")):
        return []

    # Yang ditandai kata terakhirnya beserta tanda bacanya, dan penggantinya
    # kata itu tanpa tanda baca — bukan menyisipkan teks kosong, yang tidak
    # bisa dilakukan Range.insertText.
    m = list(_POLA_KATA.finditer(teks))
    mulai = m[-1].start() if m else len(teks) - 1
    cuplikan = teks[mulai:]

    return [
        _buat_temuan(
            aturan_id="F1-006",
            jenis_tanda=JenisTanda.PENGGANTIAN,
            paragraf=p,
            offset_mulai=mulai,
            panjang=len(cuplikan),
            catatan="Judul peraturan tidak diakhiri tanda baca.",
            usulan_rumusan=cuplikan.rstrip(".,;:"),
        )
    ]


def cek_butir_menimbang(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """F1-008 — butir 21: tiap butir Menimbang diawali "bahwa", diakhiri ";"."""
    bagian = _ekstrak_bagian(paragraf, "Menimbang", "Mengingat")
    if bagian is None:
        return []

    butir_list = _pecah_butir_menimbang(bagian["teks_gabungan"])
    if not butir_list:
        return []

    temuan: list[Temuan] = []
    for butir in butir_list:
        isi = re.sub(r"^[a-z]\.\s*", "", _trim(butir)).strip()

        # Potongan yang terlalu pendek hampir pasti hasil pemecahan yang
        # gagal — pada naskah bertabel, huruf penanda dan isinya ada di
        # paragraf berbeda. Tidak diperiksa daripada salah tuduh.
        if len(isi) < 15:
            continue

        # Cari paragraf yang memuatnya, supaya tandanya mendarat di tempat
        # yang benar. Kalau tidak ketemu, aturannya diam untuk butir ini.
        petunjuk = " ".join(isi.split()[:8])
        idx = None
        for i in range(bagian["paragraf_mulai"], bagian["paragraf_akhir"]):
            if _cari_frasa(paragraf[i].teks, petunjuk) is not None:
                idx = i
                break
        if idx is None:
            continue

        p = paragraf[idx]
        posisi = _cari_frasa(p.teks, petunjuk)
        if posisi is None:
            continue
        mulai, akhir = posisi

        if not isi.lower().startswith("bahwa"):
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-008",
                    jenis_tanda=JenisTanda.CATATAN,
                    paragraf=p,
                    offset_mulai=mulai,
                    panjang=akhir - mulai,
                    catatan=(
                        "Tiap pokok pikiran pada Menimbang dirumuskan dalam "
                        "satu kalimat yang diawali kata \"bahwa\"."
                    ),
                )
            )

        if not isi.endswith(";"):
            # Tandanya ditaruh di ujung BUTIR, bukan ujung paragraf.
            #
            # DIPERBAIKI 18 Sep 2026. Dulu letaknya diambil dari
            # `len(p.teks.rstrip()) - 1`, yaitu karakter terakhir PARAGRAF.
            # Sebuah paragraf Menimbang kerap memuat beberapa butir sekaligus
            # ("Menimbang : a. ... b. ..."), dan di naskah seperti itu:
            #   - tanda untuk butir a mendarat di ujung butir b — tempat yang
            #     sama sekali bukan miliknya;
            #   - dua butir yang sama-sama kurang titik koma menghasilkan dua
            #     temuan dengan rentang IDENTIK, yang di Word berarti dua
            #     content control dan dua komentar di satu karakter.
            #
            # Sekarang ujungnya dicari dari isi butirnya sendiri. Kalau butirnya
            # terpotong antarparagraf, ujungnya tidak bisa dipastikan dari sini
            # dan aturannya MEMILIH DIAM untuk butir itu — sejalan dengan kaidah
            # bahwa yang tidak bisa dibuktikan tidak dituduhkan.
            letak_butir = _cari_frasa(p.teks, isi)
            if letak_butir is not None and letak_butir[1] > 0:
                temuan.append(
                    _buat_temuan(
                        aturan_id="F1-008",
                        jenis_tanda=JenisTanda.CATATAN,
                        paragraf=p,
                        offset_mulai=letak_butir[1] - 1,
                        panjang=1,
                        catatan=(
                            "Tiap pokok pikiran pada Menimbang diakhiri tanda "
                            "baca titik koma (;)."
                        ),
                    )
                )

    return temuan


def cek_penomoran_dasar_hukum(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """F1-010 — butir 31: tiap dasar hukum diawali angka Arab, diakhiri ";"."""
    mulai_idx, akhir_idx = _ekstrak_rentang_mengingat(paragraf)
    if mulai_idx == -1:
        return []

    # Kelompokkan paragraf jadi butir: sebuah butir dimulai di paragraf yang
    # diawali "1.", "2.", dan seterusnya, lalu berlanjut sampai butir berikutnya.
    #
    # Pengelompokan ini yang membuat aturannya aman. Judul peraturan yang
    # panjang memenuhi beberapa paragraf, dan paragraf lanjutannya memang tidak
    # berangka dan tidak berakhir titik koma. Memeriksa per paragraf berarti
    # menuduh tiap lanjutan sebagai pelanggaran.
    kelompok: list[list[int]] = []
    for i in range(mulai_idx, akhir_idx):
        teks = _trim(paragraf[i].teks)
        if not teks:
            continue
        if re.match(r"^\d+\.", teks):
            kelompok.append([i])
        elif kelompok:
            kelompok[-1].append(i)

    # Tidak satu pun paragraf berangka. Dua kemungkinan: dasar hukumnya
    # memang tunggal tanpa nomor (sah menurut butir 31, yang hanya berlaku
    # bila lebih dari satu), atau nomornya ada di sel tabel yang lain.
    # Keduanya tidak bisa dibedakan dari sini, jadi aturannya diam.
    if len(kelompok) < 2:
        return []

    temuan: list[Temuan] = []
    for anggota in kelompok:
        idx_akhir = anggota[-1]
        p = paragraf[idx_akhir]
        teks = p.teks.rstrip()
        if not teks or teks.endswith(";"):
            continue
        temuan.append(
            _buat_temuan(
                aturan_id="F1-010",
                jenis_tanda=JenisTanda.CATATAN,
                paragraf=p,
                offset_mulai=len(teks) - 1,
                panjang=1,
                catatan=(
                    "Tiap dasar hukum diakhiri tanda baca titik koma (;)."
                ),
            )
        )

    return temuan


def cek_judul_menetapkan(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """F1-012 — butir 39: judul pada Menetapkan diakhiri titik, tanpa "Republik
    Indonesia"."""
    info = _ekstrak_judul_menetapkan(paragraf)
    if info is None or not info["paragraf_indeks"]:
        return []

    temuan: list[Temuan] = []

    # 1. Frasa "Republik Indonesia" sengaja dibuang di klausul Menetapkan.
    #
    # Rentangnya sengaja mencakup "MENTERI KEUANGAN" sekalian, dan
    # penggantinya "MENTERI KEUANGAN" saja. Menandai frasa "REPUBLIK
    # INDONESIA" sendirian akan memaksa penggantinya berupa teks kosong —
    # dan Range.insertText tidak bisa menyisipkan teks kosong, sehingga
    # usulannya diam-diam batal terpasang.
    #
    # DIBATASI 18 Sep 2026 — memperbaiki salah tandai yang terbukti.
    #
    # Yang diatur butir 39 adalah JENIS DAN NAMA peraturan ini sendiri, yang
    # dicantumkan kembali sesudah kata "Menetapkan". Jenis itu berhenti di kata
    # "TENTANG"; sesudahnya yang ada JUDUL, dan judul boleh memuat nama resmi
    # peraturan LAIN — "PERUBAHAN ATAS PERATURAN MENTERI KEUANGAN REPUBLIK
    # INDONESIA NOMOR 5 TAHUN 2023 TENTANG ...". Sebelum pembatasan ini,
    # pencarian mengenai seluruh kemunculan, sehingga alat mengusulkan
    # MENGUBAH NAMA RESMI PERATURAN ORANG LAIN. Itu jenis usulan yang paling
    # cepat merusak kepercayaan penelaah.
    #
    # Tanpa kata "TENTANG" di klausulnya, jenis tidak bisa dipisahkan dari
    # judul sama sekali — dalam keadaan itu pemeriksaan ini MEMILIH DIAM.
    batas: Optional[tuple[int, int]] = None  # (indeks paragraf, offset)
    for idx in info["paragraf_indeks"]:
        m = re.search(r"\bTENTANG\b", paragraf[idx].teks, re.IGNORECASE)
        if m:
            batas = (idx, m.start())
            break

    if batas is not None:
        idx_batas, off_batas = batas
        for idx in info["paragraf_indeks"]:
            if idx > idx_batas:
                break
            p = paragraf[idx]
            akhir_jenis = off_batas if idx == idx_batas else len(p.teks)
            for m in re.finditer(
                r"MENTERI\s+KEUANGAN\s+REPUBLIK\s+INDONESIA", p.teks, re.IGNORECASE
            ):
                if m.end() > akhir_jenis:
                    break
                asli = m.group(0)
                temuan.append(
                    _buat_temuan(
                        aturan_id="F1-012",
                        jenis_tanda=JenisTanda.PENGGANTIAN,
                        paragraf=p,
                        offset_mulai=m.start(),
                        panjang=len(asli),
                        catatan=(
                            "Jenis peraturan pada Menetapkan ditulis tanpa frasa "
                            "\"Republik Indonesia\"."
                        ),
                        usulan_rumusan=asli[
                            : asli.upper().index("REPUBLIK")
                        ].rstrip(),
                    )
                )

    # 2. Diakhiri tanda baca titik.
    idx_terakhir = None
    for idx in info["paragraf_indeks"]:
        if paragraf[idx].teks.strip():
            idx_terakhir = idx
    if idx_terakhir is not None:
        p = paragraf[idx_terakhir]
        teks = p.teks.rstrip()
        if teks and not teks.endswith("."):
            m = list(_POLA_KATA.finditer(teks))
            mulai = m[-1].start() if m else len(teks) - 1
            cuplikan = teks[mulai:]
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-012",
                    jenis_tanda=JenisTanda.PENGGANTIAN,
                    paragraf=p,
                    offset_mulai=mulai,
                    panjang=len(cuplikan),
                    catatan=(
                        "Judul pada Menetapkan diakhiri tanda baca titik (.)."
                    ),
                    usulan_rumusan=cuplikan.rstrip(",;:") + ".",
                )
            )

    return temuan


# ---------------------------------------------------------------------------
# Fungsi utama: jalankan semua pemeriksaan
# ---------------------------------------------------------------------------

def jalankan_semua(
    paragraf: list[ParagrafInput],
    jenis: JenisDokumen,
    aturan_aktif: Optional[list[str]] = None,
) -> list[Temuan]:
    """Jalankan aturan Fase 1, lalu urutkan dan nomori temuannya.

    `aturan_aktif` berisi daftar aturan_id yang dijalankan. None berarti semua
    aturan yang aktif secara bawaan — perilaku lama. Penelaah memilihnya lewat
    panel Pengaturan di task pane, supaya aturan yang salah tandai bisa
    dimatikan sendiri tanpa menunggu kode diperbaiki.

    Urutannya mengikuti posisi di dokumen — paragraf lebih dahulu, lalu offset
    di dalam paragraf. Nomor itulah yang dibaca penelaah sebagai (T1), (T2),
    dan yang dipakai kode untuk menemukan kembali komentarnya sendiri.
    """
    dipakai = (
        None if aturan_aktif is None else {a.strip().upper() for a in aturan_aktif}
    )

    def aktif(aturan_id: str) -> bool:
        return dipakai is None or aturan_id in dipakai

    semua_temuan: list[Temuan] = []
    if AKTIFKAN_F1_001 and aktif("F1-001"):
        semua_temuan.extend(cek_judul_kapital(paragraf, jenis))
    if aktif("F1-002"):
        semua_temuan.extend(cek_judul_konsisten(paragraf, jenis))
    if aktif("F1-003"):
        semua_temuan.extend(cek_kelengkapan_struktur(paragraf, jenis))
    if aktif("F1-004"):
        semua_temuan.extend(cek_frasa_baku_menimbang(paragraf, jenis))
    if aktif("F1-005"):
        semua_temuan.extend(cek_ejaan(paragraf))
    if aktif("F1-006"):
        semua_temuan.extend(cek_judul_tanpa_tanda_baca(paragraf, jenis))
    if aktif("F1-007"):
        semua_temuan.extend(_cek_label_bagian(paragraf, "Menimbang", "F1-007"))
    if aktif("F1-008"):
        semua_temuan.extend(cek_butir_menimbang(paragraf, jenis))
    if aktif("F1-009"):
        semua_temuan.extend(_cek_label_bagian(paragraf, "Mengingat", "F1-009"))
    if aktif("F1-010"):
        semua_temuan.extend(cek_penomoran_dasar_hukum(paragraf))
    if aktif("F1-011"):
        semua_temuan.extend(_cek_label_bagian(paragraf, "Menetapkan", "F1-011"))
    if aktif("F1-012"):
        semua_temuan.extend(cek_judul_menetapkan(paragraf))

    # --- Buang temuan yang tidak punya teks untuk ditunjuk ---------------------
    #
    # Ditambahkan 18 Sep 2026. Temuan bertext_asli kosong tidak bisa ditandai di
    # Word sama sekali, dan di panel muncul sebagai kartu hampa: tanpa cuplikan,
    # tanpa warna, tanpa komentar, tapi dengan tombol Terima/Tolak yang tidak
    # mengerjakan apa-apa. Penelaah menemukannya pada PMK 119.
    #
    # Ini jaring pengaman lapis terakhir, bukan pengganti perbaikan di aturannya
    # masing-masing: aturan yang menghasilkan lokasi kosong tetap dianggap cacat
    # dan sudah dibetulkan sendiri-sendiri.
    #
    # F1-003 dan F1-002 DIKECUALIKAN dari saringan ini — keduanya kini hampir
    # selalu punya lokasi (anchor netral, lihat `_anchor_dokumen`), tapi pada
    # kasus langka anchor-nya tidak ketemu (dokumen tanpa satu paragraf pun
    # berisi teks), temuannya tetap dibuat tanpa lokasi dan tidak boleh ikut
    # terbuang di sini. Panel menampilkan itu sebagai peringatan dokumen.
    semua_temuan = [
        t
        for t in semua_temuan
        if t.aturan_id in _BOLEH_TANPA_LOKASI or t.lokasi.teks_asli.strip()
    ]

    semua_temuan.sort(
        key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai)
    )

    # --- Buang temuan kembar dari aturan yang SAMA ----------------------------
    #
    # Ditambahkan 18 Sep 2026, jaring pengaman lapis terakhir. Satu aturan yang
    # mengeluarkan dua temuan dengan rentang SAMA PERSIS selalu cacat: itu satu
    # kesalahan yang dilaporkan dua kali, dan di Word berarti dua content
    # control bersarang, dua komentar di satu tempat, serta menolak yang satu
    # ikut menghapus tanda yang lain tanpa ada yang memberi tahu panel.
    #
    # Ini bukan pengganti perbaikan di aturannya masing-masing — dua penyebab
    # yang sudah terbukti (pemindaian label yang kebablasan dan letak titik koma
    # butir Menimbang) sudah dibetulkan di tempatnya sendiri. Jaring ini untuk
    # aturan yang ditambahkan nanti, supaya tidak perlu mengingat batas ini.
    #
    # Temuan dari aturan BERBEDA yang kebetulan berimpit sengaja TIDAK dibuang:
    # keduanya persoalan yang berlainan, dan membuang salah satunya berarti
    # menyembunyikan temuan yang benar. Yang menanganinya sisi Word — hanya satu
    # yang digambar, sisanya dilaporkan sebagai "tidak ditandai di naskah"
    # lengkap dengan alasannya di kartu panel.
    unik: list[Temuan] = []
    terpakai: set[tuple[str, int, int, int]] = set()
    for t in semua_temuan:
        kunci = (
            t.aturan_id,
            t.lokasi.paragraf_index,
            t.lokasi.offset_mulai,
            t.lokasi.panjang,
        )
        if t.lokasi.teks_asli.strip() and kunci in terpakai:
            continue
        terpakai.add(kunci)
        unik.append(t)
    semua_temuan = unik

    for urutan, t in enumerate(semua_temuan, start=1):
        t.nomor = urutan

    return semua_temuan
