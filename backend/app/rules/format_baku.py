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

def _buat_temuan(
    aturan_id: str,
    jenis_tanda: JenisTanda,
    paragraf: ParagrafInput,
    offset_mulai: int,
    panjang: int,
    catatan: str,
    usulan_rumusan: Optional[str] = None,
) -> Temuan:
    """Helper untuk membuat objek Temuan dengan rujukan dari tabel.

    `nomor` sengaja dibiarkan 0 di sini — nomor urut baru bisa ditetapkan
    sesudah SELURUH aturan selesai dan temuannya diurutkan menurut posisi di
    dokumen. Itu tugas jalankan_semua().
    """
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
        rujukan=RujukanTemuan(**rujukan_dict),
        status=StatusTemuan.BELUM_DITINJAU,
    )


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


def _cari_frasa(teks: str, frasa: str) -> Optional[tuple[int, int]]:
    """Cari posisi frasa di dalam teks, tahan terhadap spasi ganda.

    Frasa datang dari judul yang sudah dirapatkan spasinya, sedangkan teks
    paragraf aslinya belum — jadi pencarian harfiah bisa meleset hanya karena
    ada dua spasi. Pencocokan dilakukan per kata dengan pemisah \\s+.
    """
    kata = frasa.split()
    if not kata:
        return None
    pola = r"\s+".join(re.escape(k) for k in kata)
    m = re.search(pola, teks, re.IGNORECASE)
    return (m.start(), m.end()) if m else None


def _cari_index_anchor(
    paragraf: list[ParagrafInput], anchor: str, mulai: int = 0
) -> Optional[int]:
    """Cari indeks paragraf yang isinya PERSIS sama dengan anchor (case-insensitive, trimmed)."""
    for i in range(mulai, len(paragraf)):
        if _trim(paragraf[i].teks).upper() == anchor.upper():
            return i
    return None


def _cari_index_mengandung(
    paragraf: list[ParagrafInput], kata_kunci: str, mulai: int = 0
) -> Optional[int]:
    """Cari indeks paragraf yang mengandung kata kunci (case-insensitive)."""
    kata_upper = kata_kunci.upper()
    for i in range(mulai, len(paragraf)):
        if kata_upper in _trim(paragraf[i].teks).upper():
            return i
    return None


# Catatan: dulu ada _tentukan_jenis_dokumen() yang menebak PMK/KMK dari
# penyebutan pertama di dokumen. Dihapus 17 Sep 2026. Tebakan itu bertumpu pada
# asumsi bahwa penyebutan pertama selalu datang dari blok judul — padahal bagian
# Mengingat sebuah KMK lazim menyebut "Peraturan Menteri Keuangan Nomor ...",
# sehingga KMK bisa dikira PMK lalu F1-004 menuntut bunyi yang salah. Sekarang
# jenisnya dipilih penelaah di task pane dan diteruskan sebagai parameter.
# Lihat docs/fase1 drafter.md bagian 6.7.


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
        # Cek juga penutup alternatif (KMK mungkin tanpa "REPUBLIK INDONESIA,")
        if penutup == _PENUTUP_JUDUL_KMK and teks_trimmed.upper().startswith(
            "MENTERI KEUANGAN"
        ):
            break
        judul_parts.append(teks_trimmed)
        judul_indeks.append(i)

    if not judul_parts:
        return None

    return {
        "judul": " ".join(judul_parts),
        "jenis": jenis,
        "paragraf_indeks": judul_indeks,
        "tentang_index": tentang_idx,
    }


# Penanda bahwa klausul Menetapkan sudah lewat. Memuat penomoran diktum KMK
# (KESATU, KEDUA, ...) DAN penomoran PMK (BAB, Pasal), karena satu fungsi ini
# melayani keduanya.
_PENGHENTI_MENETAPKAN = re.compile(
    r"^(BAB\b|Pasal\b|KESATU\b|PERTAMA\b|KEDUA\b|KETIGA\b|KEEMPAT\b|KELIMA\b"
    r"|KEENAM\b|KETUJUH\b|KEDELAPAN\b|KESEMBILAN\b|KESEPULUH\b)",
    re.IGNORECASE,
)

# Batas kewajaran panjang judul Menetapkan, dalam kata. Judul peraturan
# terpanjang di JDIH masih jauh di bawah angka ini; kalau hasil pengambilan
# melewatinya, yang terjadi hampir pasti pengambilan kebablasan seperti bug
# KESATU di atas. Dalam keadaan itu aturan MEMILIH DIAM, bukan melapor:
# temuan yang ditandai wajib benar-benar salah.
_BATAS_KATA_JUDUL_MENETAPKAN = 60


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
    # Cari paragraf yang mengandung "Menetapkan"
    menetapkan_idx = None
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        if re.search(r"Menetapkan\s*:", teks, re.IGNORECASE):
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

    # Normalisasi: buang teks sampai "Menetapkan :"
    gabungan = re.sub(
        r"^.*?Menetapkan\s*:\s*", "", gabungan, flags=re.IGNORECASE
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
    if len(gabungan.split()) > _BATAS_KATA_JUDUL_MENETAPKAN:
        return None

    return {
        "judul": gabungan,
        "paragraf_indeks": indeks,
    }


def _normalisasi_judul_pembuka(judul: str) -> str:
    """Normalisasi judul pembuka untuk perbandingan."""
    return _trim(judul).upper()


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
    judul_menetapkan = _trim(info_menetapkan["judul"]).upper()

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

    frasa_beda: list[str] = []
    kata_hilang: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, kata_pembuka, kata_menetapkan
    ).get_opcodes():
        if tag == "equal":
            continue
        if j2 > j1:
            frasa_beda.append(" ".join(kata_menetapkan[j1:j2]))
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
    for frasa in frasa_beda:
        letak: Optional[tuple[int, int, int]] = None  # (idx, mulai, akhir)
        for kandidat in info_menetapkan["paragraf_indeks"]:
            posisi = _cari_frasa(paragraf[kandidat].teks, frasa)
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
    # entah karena yang salah justru ada yang HILANG, entah karena frasanya
    # terpotong antarparagraf. Tandai paragraf Menetapkan, seperti dulu, tapi
    # sebut sebabnya di catatan supaya penelaah tahu kenapa sorotannya lebar.
    idx = info_menetapkan["paragraf_indeks"][0]
    p = paragraf[idx]
    tambahan = (
        f" Bagian yang tidak ada di Menetapkan: \"{'; '.join(kata_hilang)}\"."
        if kata_hilang
        else ""
    )
    return [
        _buat_temuan(
            aturan_id="F1-002",
            jenis_tanda=JenisTanda.CATATAN,
            paragraf=p,
            offset_mulai=0,
            panjang=len(p.teks.strip()),
            catatan=catatan_dasar + tambahan,
        )
    ]


# ---------------------------------------------------------------------------
# Aturan 3: cek_kelengkapan_struktur (F1-003)
# ---------------------------------------------------------------------------

_BAGIAN_WAJIB = ["Menimbang", "Mengingat", "Menetapkan"]


def cek_kelengkapan_struktur(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek keberadaan bagian wajib: Menimbang, Mengingat, Menetapkan."""
    temuan: list[Temuan] = []

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
                break

        if not ditemukan:
            # Laporkan di paragraf pertama — tidak ada lokasi spesifik
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-003",
                    jenis_tanda=JenisTanda.CATATAN,
                    paragraf=paragraf[0] if paragraf else ParagrafInput(
                        index=0, teks=""
                    ),
                    offset_mulai=0,
                    panjang=0,
                    catatan=(
                        f"Bagian \"{bagian}\" tidak ditemukan. Menimbang, "
                        "Mengingat, dan Menetapkan wajib ada pada tiap "
                        "rancangan."
                    ),
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

    # Cari paragraf terdekat untuk lokasi temuan
    # Butir terakhir kemungkinan ada di paragraf menjelang akhir bagian Menimbang
    idx_temuan = bagian["paragraf_akhir"] - 1
    if idx_temuan < 0 or idx_temuan >= len(paragraf):
        idx_temuan = bagian["paragraf_mulai"]

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
        posisi = _cari_frasa(p.teks, _trim(butir_terakhir_asli))
        if posisi is None:
            # Butirnya mungkin terpotong antarparagraf. Coba pembukanya saja —
            # cukup untuk mengarahkan mata penelaah ke butir yang benar.
            pembuka_butir = " ".join(_trim(butir_terakhir_asli).split()[:8])
            posisi = _cari_frasa(p.teks, pembuka_butir)
        if posisi is not None:
            mulai, panjang = posisi[0], posisi[1] - posisi[0]

    return [
        _buat_temuan(
            aturan_id="F1-004",
            jenis_tanda=JenisTanda.CATATAN,
            paragraf=p,
            offset_mulai=mulai,
            panjang=panjang,
            catatan=(
                "Butir Menimbang terakhir belum memakai bunyi baku. Belum ada: "
                + "; ".join(kekurangan)
                + "."
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
        if re.match(r"^(MEMUTUSKAN|Menetapkan|BAB\s|Pasal\s)", teks, re.IGNORECASE):
            akhir_idx = i
            break

    return mulai_idx, akhir_idx


def cek_ejaan(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek ejaan baku penyusunan peraturan.

    Bentuk paling sederhana: hanya ejaan khusus peraturan.
    BUKAN kamus besar bahasa Indonesia.
    """
    temuan: list[Temuan] = []

    # 1. Pola umum di seluruh dokumen (Undang-Undang, dsb.)
    for p in paragraf:
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

    # 2. Pola butir 32: kata "tentang" tetap huruf kecil di dalam judul peraturan pada dasar hukum.
    # Berlaku HANYA di dalam bagian Mengingat, bukan di seluruh dokumen.
    mulai_mengingat, akhir_mengingat = _ekstrak_rentang_mengingat(paragraf)
    if mulai_mengingat != -1:
        for i in range(mulai_mengingat, akhir_mengingat):
            p = paragraf[i]
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
# Fungsi utama: jalankan semua pemeriksaan
# ---------------------------------------------------------------------------

def jalankan_semua(
    paragraf: list[ParagrafInput], jenis: JenisDokumen
) -> list[Temuan]:
    """Jalankan semua aturan Fase 1, lalu urutkan dan nomori temuannya.

    Urutannya mengikuti posisi di dokumen — paragraf lebih dahulu, lalu offset
    di dalam paragraf. Nomor itulah yang dibaca penelaah sebagai (T1), (T2),
    dan yang dipakai kode untuk menemukan kembali komentarnya sendiri.
    """
    semua_temuan: list[Temuan] = []
    if AKTIFKAN_F1_001:
        semua_temuan.extend(cek_judul_kapital(paragraf, jenis))
    semua_temuan.extend(cek_judul_konsisten(paragraf, jenis))
    semua_temuan.extend(cek_kelengkapan_struktur(paragraf))
    semua_temuan.extend(cek_frasa_baku_menimbang(paragraf, jenis))
    semua_temuan.extend(cek_ejaan(paragraf))

    semua_temuan.sort(
        key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai)
    )
    for urutan, t in enumerate(semua_temuan, start=1):
        t.nomor = urutan

    return semua_temuan
