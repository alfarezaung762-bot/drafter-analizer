"""TAHAP 0 — naskah datar → pohon satuan.

Pondasi seluruh Fase 2 dan 3. Kode biasa, tanpa AI: bentuk naskah peraturan
kaku dan polanya bisa dikenali, jadi hasilnya pasti dan bisa dites tanpa
server maupun kredensial.

  masuk  : list[ParagrafInput]  — daftar paragraf apa adanya dari Word
  keluar : PohonSatuan          — teks yang SAMA PERSIS, plus hubungan antarbagian

Parser TIDAK PERNAH mengubah teks. Ia cuma mengelompokkan.

KAIDAH YANG DIWARISI FASE 1, BERLAKU PENUH:
  - Satuan yang tidak bisa dipetakan balik ke paragraf asalnya tidak boleh
    ditandai. Lihat Satuan.bisa_ditandai.
  - Kalau strukturnya tidak masuk akal, parser MELAPOR GAGAL — bukan menebak.
    PohonSatuan.gagal terisi, dan seluruh Fase 2 tidak dijalankan (cabang 3.6).
"""

from __future__ import annotations

import re
from typing import Optional

from app.models.satuan import JenisSatuan, PohonSatuan, Satuan
from app.models.temuan import ParagrafInput


def _trim(teks: str) -> str:
    """Strip dan rapatkan spasi ganda.

    Sengaja ditulis ulang, tidak di-import dari rules/format_baku.py: Fase 2
    tidak boleh bergantung pada bagian dalam Fase 1 yang sudah terbukti.
    """
    return re.sub(r"\s+", " ", teks.strip())


# ---------------------------------------------------------------------------
# Pola pengenal — inilah seluruh "kecerdasan" parser ini
# ---------------------------------------------------------------------------
#
# Semuanya DIJANGKAR di awal paragraf. Tanpa jangkar, kata "Pasal" di tengah
# kalimat ("sebagaimana dimaksud dalam Pasal 5") ikut tertangkap sebagai judul
# pasal — pelajaran yang sudah dibayar Fase 1 di Kasus 3.

# "Pasal 12", "Pasal 12A" (pasal sisipan pada peraturan perubahan)
_POLA_PASAL = re.compile(r"^Pasal\s+(\d+[A-Z]?)\s*$", re.IGNORECASE)

# "BAB I", "BAB XII"
_POLA_BAB = re.compile(r"^BAB\s+([IVXLCDM]+)\b", re.IGNORECASE)

# "Bagian Kesatu", "Bagian Ketiga", "Bagian Kedua Belas"
#
# DUA PENJAGA, dan keduanya perlu. Pola lamanya `^Bagian\s+(\w+)` menerima
# kalimat apa pun yang kebetulan diawali kata "Bagian" — dan PMK organisasi
# penuh dengan unit bernama begitu:
#
#     "Bagian Umum mempunyai tugas melaksanakan urusan sumber daya manusia…"
#
# Kalimat itu dibaca sebagai JUDUL BAGIAN, lalu ia menutup Pasal 8 yang baru
# saja dibuka dan menelan isinya — Pasal 8 berakhir kosong, dan isinya tidak
# pernah sampai ke model. Terbukti pada PMK 18 Tahun 2026, 23 Sep 2026.
#
#   1. Nomornya wajib kata bilangan tingkat — "Kesatu", "Kedua", "Pertama".
#      "Umum", "Kepegawaian", "Keuangan" tidak lolos.
#   2. Barisnya wajib HABIS di situ. Judul bagiannya ada di baris berikutnya,
#      dan itu sudah ditangani judul_sesudah().
_POLA_BAGIAN = re.compile(
    r"^Bagian\s+(Pertama|Ke[a-z]+(?:\s+(?:Belas|Puluh)(?:\s+[A-Za-z]+)?)?)\s*$",
    re.IGNORECASE,
)

# "Paragraf 1" — ISTILAH HUKUM, bukan paragraf Word
_POLA_PARAGRAF_HUKUM = re.compile(r"^Paragraf\s+(\d+)\s*$", re.IGNORECASE)

# "(1) Pengguna Barang mengajukan…"
_POLA_AYAT = re.compile(r"^\((\d+)\)\s*")

# "a. dokumen kepemilikan;"
_POLA_HURUF = re.compile(r"^([a-z])\.\s+")

# "1. fotokopi sertifikat;"  — di dalam Pasal 1 ini definisi, bukan dasar hukum
_POLA_ANGKA = re.compile(r"^(\d+)\.\s+")

# Penanda batas bagian, dipakai menutup pembukaan dan membuka batang tubuh.
_POLA_MEMUTUSKAN = re.compile(
    r"^M\s*E\s*M\s*U\s*T\s*U\s*S\s*K\s*A\s*N\s*:?$", re.IGNORECASE
)
_POLA_MENIMBANG = re.compile(r"^Menimbang\b\s*:?", re.IGNORECASE)
_POLA_MENGINGAT = re.compile(r"^Mengingat\b\s*:?", re.IGNORECASE)
_POLA_MENETAPKAN = re.compile(r"^Menetapkan\b\s*:?", re.IGNORECASE)
_POLA_PENUTUP = re.compile(r"^(Ditetapkan di|Diundangkan di)\b", re.IGNORECASE)
_POLA_LAMPIRAN = re.compile(r"^LAMPIRAN\b", re.IGNORECASE)

# Penomoran diktum KMK: KESATU … KEDUAPULUHLIMA. Kata lain berawalan KE-
# tidak ikut kena karena harus diikuti nama angka.
_POLA_DIKTUM_KMK = re.compile(
    r"^KE(SATU|DUA|TIGA|EMPAT|LIMA|ENAM|TUJUH|DELAPAN|SEMBILAN|SEPULUH"
    r"|SEBELAS)[A-Z]*\b",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Batas kewajaran — di luar ini parser MELAPOR GAGAL
# ---------------------------------------------------------------------------
#
# Bentuk umum kaidah Fase 1: tiap yang bisa kebablasan wajib punya batas, dan
# di luar batas itu memilih diam. Untuk parser, "diam" berarti seluruh Fase 2
# tidak dijalankan — jauh lebih baik daripada memeriksa struktur salah baca.

# Dokumen sepanjang ini tanpa satu pun Pasal hampir pasti bukan PMK/KMK,
# atau paragrafnya gagal terbaca.
_MIN_PARAGRAF_WAJIB_ADA_PASAL = 30

# Lompatan penomoran sebesar ini menandakan pembacaan yang kacau, bukan
# naskah yang penomorannya cacat. Naskah yang cacat penomorannya urusan
# F2-004, bukan urusan parser.
_BATAS_LOMPATAN_PASAL = 20


def bangun_pohon(paragraf: list[ParagrafInput]) -> PohonSatuan:
    """Ubah daftar paragraf datar jadi pohon satuan.

    Selalu mengembalikan PohonSatuan. Kalau strukturnya tidak masuk akal,
    `gagal` terisi dan `satuan` boleh kosong — pemanggil WAJIB memeriksa
    `gagal` sebelum memakai isinya.
    """
    if not paragraf:
        return PohonSatuan(satuan=[], gagal="Tidak ada paragraf untuk dibaca.")

    hasil: list[Satuan] = []

    # Jangkar-jangkar utama, dicari lebih dulu supaya tiap paragraf tahu
    # ia sedang berada di bagian mana.
    idx_memutuskan = _cari(paragraf, _POLA_MEMUTUSKAN)
    idx_menimbang = _cari(paragraf, _POLA_MENIMBANG)
    idx_mengingat = _cari(paragraf, _POLA_MENGINGAT)
    idx_lampiran = _cari(paragraf, _POLA_LAMPIRAN, mulai=(idx_memutuskan or 0) + 1)
    idx_penutup = _cari(paragraf, _POLA_PENUTUP, mulai=(idx_memutuskan or 0) + 1)

    # Batang tubuh dimulai sesudah diktum dan berakhir di penutup/lampiran.
    awal_batang = (idx_memutuskan + 1) if idx_memutuskan is not None else 0
    akhir_batang = min(
        x for x in (idx_penutup, idx_lampiran, len(paragraf)) if x is not None
    )

    hasil += _baca_judul(paragraf, batas=idx_menimbang or awal_batang)
    hasil += _baca_butir_pembukaan(
        paragraf, idx_menimbang, idx_mengingat, JenisSatuan.MENIMBANG, "menimbang"
    )
    hasil += _baca_butir_pembukaan(
        paragraf, idx_mengingat, idx_memutuskan, JenisSatuan.MENGINGAT, "mengingat"
    )
    hasil += _baca_diktum(paragraf, idx_memutuskan, akhir_batang)
    hasil += _baca_batang_tubuh(paragraf, awal_batang, akhir_batang)

    if idx_penutup is not None:
        hasil.append(
            Satuan(
                id="penutup",
                jenis=JenisSatuan.PENUTUP,
                teks=_trim(paragraf[idx_penutup].utuh),
                paragraf_mulai=paragraf[idx_penutup].index,
                paragraf_akhir=paragraf[idx_penutup].index + 1,
            )
        )
    if idx_lampiran is not None:
        hasil.append(
            Satuan(
                id="lampiran",
                jenis=JenisSatuan.LAMPIRAN,
                teks=_trim(paragraf[idx_lampiran].utuh),
                paragraf_mulai=paragraf[idx_lampiran].index,
                paragraf_akhir=len(paragraf),
            )
        )

    gagal = _periksa_kewajaran(paragraf, hasil)
    return PohonSatuan(satuan=hasil, gagal=gagal)


# ---------------------------------------------------------------------------
# Pembantu
# ---------------------------------------------------------------------------

def _cari(
    paragraf: list[ParagrafInput], pola: re.Pattern, mulai: int = 0
) -> Optional[int]:
    """Indeks paragraf PERTAMA yang cocok pola, atau None."""
    for i in range(mulai, len(paragraf)):
        if pola.match(_trim(paragraf[i].utuh)):
            return i
    return None


def _baca_judul(paragraf: list[ParagrafInput], batas: int) -> list[Satuan]:
    """Judul = paragraf sesudah baris yang isinya persis TENTANG."""
    idx_tentang = None
    for i in range(min(batas, len(paragraf))):
        if _trim(paragraf[i].utuh).upper() == "TENTANG":
            idx_tentang = i
            break
    if idx_tentang is None:
        return []

    bagian: list[str] = []
    akhir = idx_tentang + 1
    for i in range(idx_tentang + 1, min(batas, len(paragraf))):
        teks = _trim(paragraf[i].utuh)
        if not teks:
            continue
        # Penutup blok judul: PMK memakai frasa Dengan Rahmat, KMK langsung
        # ke baris jabatan. Dua-duanya diawali kata yang tetap.
        if teks.upper().startswith(
            ("DENGAN RAHMAT", "MENTERI KEUANGAN")
        ):
            break
        bagian.append(teks)
        akhir = i + 1

    if not bagian:
        return []
    return [
        Satuan(
            id="judul",
            jenis=JenisSatuan.JUDUL,
            teks=" ".join(bagian),
            paragraf_mulai=paragraf[idx_tentang + 1].index,
            paragraf_akhir=paragraf[akhir - 1].index + 1,
        )
    ]


def _baca_butir_pembukaan(
    paragraf: list[ParagrafInput],
    awal: Optional[int],
    akhir: Optional[int],
    jenis: JenisSatuan,
    awalan_id: str,
) -> list[Satuan]:
    """Butir Menimbang (a, b, c) atau Mengingat (1, 2, 3)."""
    if awal is None:
        return []
    batas = akhir if akhir is not None else len(paragraf)

    hasil: list[Satuan] = []
    berjalan: Optional[Satuan] = None

    for i in range(awal, min(batas, len(paragraf))):
        teks = _trim(paragraf[i].utuh)
        if not teks:
            continue
        # Buang label bagiannya ("Menimbang :") kalau menyatu dengan butirnya.
        bersih = re.sub(r"^(Menimbang|Mengingat)\b\s*:?\s*", "", teks, flags=re.I)

        m = _POLA_HURUF.match(bersih) or _POLA_ANGKA.match(bersih)
        if m:
            nomor = m.group(1)
            berjalan = Satuan(
                id=f"{awalan_id}-{nomor}",
                jenis=jenis,
                nomor=nomor,
                teks=bersih[m.end() :].strip(),
                paragraf_mulai=paragraf[i].index,
                paragraf_akhir=paragraf[i].index + 1,
            )
            hasil.append(berjalan)
            continue

        # Lanjutan butir yang sedang berjalan.
        #
        # Butir Menimbang dan dasar hukum kerap terpotong antarparagraf —
        # judul peraturan yang panjang memenuhi dua sampai tiga baris, dan
        # pada naskah bertabel huruf penandanya bahkan jatuh di sel berbeda.
        # Tanpa penyambungan ini, satuan cuma memuat baris pertamanya, dan
        # temuan pada baris lanjutannya tidak bisa ditandai dengan benar.
        if berjalan is not None:
            berjalan.teks = f"{berjalan.teks} {bersih}".strip()
            berjalan.paragraf_akhir = paragraf[i].index + 1

    return hasil


def _baca_diktum(
    paragraf: list[ParagrafInput], idx_memutuskan: Optional[int], akhir: int
) -> list[Satuan]:
    """Klausul Menetapkan — jenis dan nama peraturan yang diulang."""
    if idx_memutuskan is None:
        return []

    idx = None
    for i in range(idx_memutuskan + 1, min(akhir, len(paragraf))):
        teks = _trim(paragraf[i].utuh)
        if teks and _POLA_MENETAPKAN.match(teks):
            idx = i
            break
    if idx is None:
        return []

    # Judulnya bisa di paragraf yang sama (bentuk biasa) atau di paragraf
    # berikutnya (bentuk bertabel — label dan isi jatuh di sel berbeda).
    bagian = [_trim(paragraf[idx].utuh)]
    akhir_idx = idx
    for i in range(idx + 1, min(akhir, len(paragraf))):
        teks = _trim(paragraf[i].utuh)
        if not teks:
            continue
        if _POLA_PASAL.match(teks) or _POLA_BAB.match(teks) or _POLA_DIKTUM_KMK.match(teks):
            break
        bagian.append(teks)
        akhir_idx = i
        if teks.endswith("."):
            break

    gabung = re.sub(
        r"^.*?Menetapkan\b\s*:?\s*", "", " ".join(bagian), flags=re.IGNORECASE
    )
    return [
        Satuan(
            id="menetapkan",
            jenis=JenisSatuan.MENETAPKAN,
            teks=gabung.strip(),
            paragraf_mulai=paragraf[idx].index,
            paragraf_akhir=paragraf[akhir_idx].index + 1,
        )
    ]


def _baca_batang_tubuh(
    paragraf: list[ParagrafInput], awal: int, akhir: int
) -> list[Satuan]:
    """BAB → Bagian → Paragraf(hukum) → Pasal → ayat → huruf/angka."""
    hasil: list[Satuan] = []

    induk_bab: Optional[str] = None
    induk_bagian: Optional[str] = None
    induk_paragraf: Optional[str] = None
    pasal_kini: Optional[Satuan] = None
    ayat_kini: Optional[Satuan] = None

    lewati: set[int] = set()

    def tutup(s: Optional[Satuan], sampai: int) -> None:
        if s is not None:
            s.paragraf_akhir = sampai

    def judul_sesudah(posisi: int) -> Optional[int]:
        """Posisi baris JUDUL milik sebuah BAB/Bagian/Paragraf, kalau ada.

        "BAB I" hampir selalu diikuti "KETENTUAN UMUM" di paragraf berikutnya.
        Tanpa ini judulnya terbuang, dan satuan BAB jadi cuma berisi nomornya.
        """
        for j in range(posisi + 1, min(akhir, len(paragraf))):
            t = _trim(paragraf[j].utuh)
            if not t:
                continue
            sudah_penanda = any(
                pola.match(t)
                for pola in (
                    _POLA_BAB, _POLA_BAGIAN, _POLA_PARAGRAF_HUKUM,
                    _POLA_PASAL, _POLA_AYAT, _POLA_HURUF, _POLA_ANGKA,
                )
            )
            return None if sudah_penanda else j
        return None

    def buat_penanda(
        p_idx: int, id_satuan: str, jenis: JenisSatuan, nomor: str,
        teks_awal: str, induk: Optional[str],
    ) -> Satuan:
        """BAB/Bagian/Paragraf + judulnya, jadi satu satuan."""
        akhir_p = paragraf[p_idx].index + 1
        isi = teks_awal
        j = judul_sesudah(p_idx)
        if j is not None:
            isi = f"{teks_awal} {_trim(paragraf[j].utuh)}"
            akhir_p = paragraf[j].index + 1
            lewati.add(j)
        s = Satuan(
            id=id_satuan, jenis=jenis, nomor=nomor, teks=isi, induk=induk,
            paragraf_mulai=paragraf[p_idx].index, paragraf_akhir=akhir_p,
        )
        hasil.append(s)
        return s

    for i in range(awal, min(akhir, len(paragraf))):
        if i in lewati:
            continue
        p = paragraf[i]
        teks = _trim(p.utuh)
        if not teks:
            continue

        # BAB, Bagian, dan Paragraf sama-sama MENUTUP pasal/ayat yang terbuka.
        # Tanpa ini, ayat terakhir sebuah Bagian membentang menelan judul
        # Bagian berikutnya — dan rentang tandanya menimpa baris yang tidak
        # bersalah.
        if m := _POLA_BAB.match(teks):
            tutup(ayat_kini, p.index)
            tutup(pasal_kini, p.index)
            pasal_kini = ayat_kini = None
            induk_bab = f"bab-{m.group(1).lower()}"
            induk_bagian = induk_paragraf = None
            buat_penanda(i, induk_bab, JenisSatuan.BAB, m.group(1), teks, None)
            continue

        if m := _POLA_BAGIAN.match(teks):
            tutup(ayat_kini, p.index)
            tutup(pasal_kini, p.index)
            pasal_kini = ayat_kini = None
            induk_bagian = f"{induk_bab or 'bab'}-bagian-{m.group(1).lower()}"
            induk_paragraf = None
            buat_penanda(
                i, induk_bagian, JenisSatuan.BAGIAN, m.group(1), teks, induk_bab
            )
            continue

        if m := _POLA_PARAGRAF_HUKUM.match(teks):
            tutup(ayat_kini, p.index)
            tutup(pasal_kini, p.index)
            pasal_kini = ayat_kini = None
            induk_paragraf = f"{induk_bagian or induk_bab or 'bab'}-paragraf-{m.group(1)}"
            buat_penanda(
                i, induk_paragraf, JenisSatuan.PARAGRAF, m.group(1), teks,
                induk_bagian or induk_bab,
            )
            continue

        if m := _POLA_PASAL.match(teks):
            tutup(ayat_kini, p.index)
            tutup(pasal_kini, p.index)
            ayat_kini = None
            pasal_kini = Satuan(
                id=f"pasal-{m.group(1).lower()}", jenis=JenisSatuan.PASAL,
                nomor=m.group(1), teks="",
                induk=induk_paragraf or induk_bagian or induk_bab,
                paragraf_mulai=p.index, paragraf_akhir=p.index + 1,
            )
            hasil.append(pasal_kini)
            continue

        if pasal_kini is None:
            continue  # di luar pasal mana pun — tidak dipetakan, tidak ditebak

        if m := _POLA_AYAT.match(teks):
            tutup(ayat_kini, p.index)
            ayat_kini = Satuan(
                id=f"{pasal_kini.id}-ayat-{m.group(1)}", jenis=JenisSatuan.AYAT,
                nomor=f"({m.group(1)})", teks=teks[m.end() :].strip(),
                induk=pasal_kini.id,
                paragraf_mulai=p.index, paragraf_akhir=p.index + 1,
            )
            hasil.append(ayat_kini)
            pasal_kini.paragraf_akhir = p.index + 1
            continue

        induk_kini = ayat_kini or pasal_kini
        if m := _POLA_HURUF.match(teks):
            hasil.append(
                Satuan(
                    id=f"{induk_kini.id}-huruf-{m.group(1)}", jenis=JenisSatuan.HURUF,
                    nomor=m.group(1), teks=teks[m.end() :].strip(),
                    induk=induk_kini.id,
                    paragraf_mulai=p.index, paragraf_akhir=p.index + 1,
                )
            )
        elif m := _POLA_ANGKA.match(teks):
            hasil.append(
                Satuan(
                    id=f"{induk_kini.id}-angka-{m.group(1)}", jenis=JenisSatuan.ANGKA,
                    nomor=m.group(1), teks=teks[m.end() :].strip(),
                    induk=induk_kini.id,
                    paragraf_mulai=p.index, paragraf_akhir=p.index + 1,
                )
            )
        elif not induk_kini.teks:
            # Pasal atau ayat tanpa penomoran anak — teksnya langsung di sini.
            induk_kini.teks = teks

        induk_kini.paragraf_akhir = p.index + 1
        pasal_kini.paragraf_akhir = p.index + 1

    return hasil


# "PERUBAHAN ATAS", "PERUBAHAN KEDUA ATAS", "PERUBAHAN KETIGA ATAS", …
_JUDUL_PERUBAHAN = re.compile(r"\bPERUBAHAN\b(\s+\w+)?\s+\bATAS\b", re.IGNORECASE)

# Batang tubuh naskah perubahan: "Pasal I", "Pasal II". Sengaja TIDAK memakai
# [IVXLC]+ yang longgar — "Pasal I" sampai "Pasal IV" sudah mencakup seluruh
# naskah perubahan yang wajar, dan pola longgar ikut menangkap "Pasal C" yang
# bukan Romawi.
_PASAL_ROMAWI = re.compile(r"^\s*Pasal\s+(I{1,3}|IV)\s*$", re.IGNORECASE)


def _naskah_perubahan(
    paragraf: list[ParagrafInput], hasil: list[Satuan]
) -> Optional[str]:
    """Alasan gagal bila naskahnya peraturan PERUBAHAN, None kalau bukan.

    Dua penanda, dan salah satu saja sudah cukup. Keduanya dipakai karena
    masing-masing bisa luput sendirian: judul bisa terpotong di naskah yang
    belum rapi, dan "Pasal I" bisa hilang kalau penomorannya otomatis.
    """
    judul = next((s for s in hasil if s.jenis == JenisSatuan.JUDUL), None)
    lewat_judul = judul is not None and bool(_JUDUL_PERUBAHAN.search(judul.teks))
    lewat_romawi = any(_PASAL_ROMAWI.match(p.utuh) for p in paragraf)

    if not (lewat_judul or lewat_romawi):
        return None

    penanda = "judulnya memuat \"PERUBAHAN ATAS\"" if lewat_judul else "batang tubuhnya memakai \"Pasal I\""
    return (
        f"Naskah ini peraturan PERUBAHAN ({penanda}) — Fase 2 tidak "
        "dijalankan. Pasal yang dikutip di dalamnya milik peraturan induk, "
        "bukan draf ini, sehingga pemeriksaan rujukan dan istilah akan salah "
        "tandai. Memeriksanya dengan benar menuntut membaca peraturan "
        "induknya. Fase 1 tetap berjalan seperti biasa."
    )


def _periksa_kewajaran(
    paragraf: list[ParagrafInput], hasil: list[Satuan]
) -> Optional[str]:
    """Batas kewajaran. Mengembalikan alasan gagal, atau None kalau sehat."""
    pasal = [s for s in hasil if s.jenis == JenisSatuan.PASAL]

    # Naskah PERUBAHAN belum didukung Fase 2 — dan ini penjaga yang paling
    # menentukan dari ketiganya, karena tanpa dia alat SALAH TANDAI.
    #
    # PMK perubahan susunannya berbeda sama sekali: batang tubuhnya "Pasal I"
    # dan "Pasal II" (angka Romawi), dan di dalam Pasal I dikutip pasal-pasal
    # milik peraturan INDUK yang sedang diubah. Tiga akibatnya, semuanya sudah
    # dibuktikan 22 Sep 2026:
    #
    #   1. Romawi tidak dikenali, jadi kutipan "Pasal 5" milik induk dibaca
    #      sebagai pasal dokumen ini, dan butir perubahan di bawahnya nyangkut
    #      jadi anaknya. Pohonnya keliru, tetapi `gagal` tetap None.
    #   2. F2-001 menandai "sebagaimana dimaksud dalam Pasal 18" sebagai
    #      rujukan menggantung — padahal Pasal 18 memang ada, di peraturan
    #      induknya. Itu salah tandai, dan CLAUDE.md butir 1 melarangnya.
    #   3. Pasal 1 definisi biasanya tidak ada di naskah perubahan, sehingga
    #      seluruh pemeriksaan istilah kehilangan dasarnya.
    #
    # Memeriksa naskah perubahan dengan benar menuntut membaca peraturan
    # induknya, dan itu pekerjaan tersendiri. Sampai itu ada, alat memilih
    # diam — dengan suara.
    if alasan := _naskah_perubahan(paragraf, hasil):
        return alasan

    if len(paragraf) >= _MIN_PARAGRAF_WAJIB_ADA_PASAL and not pasal:
        # Sampai 23 Sep 2026 sebab tersering adalah penomoran otomatis Word:
        # "Pasal 1" dan "BAB I" bukan teks, jadi tidak ikut terbaca add-in.
        # Itu sudah diperbaiki — `ParagrafInput.penanda` kini membawanya.
        #
        # Karena itu pesan ini menunjuk sebab yang TERSISA, dan yang pertama
        # bisa diperiksa sendiri penelaah: kalau tidak satu pun paragraf punya
        # penanda, berarti pembacaan nomor otomatis memang tidak berjalan —
        # Word-nya belum mendukung WordApi 1.3, atau jalur cadangan menyala.
        berpenanda = sum(1 for p in paragraf if p.penanda)
        if berpenanda == 0:
            sebab = (
                "Tidak satu pun paragraf membawa nomor otomatis, padahal naskah "
                "PMK biasanya memakainya. Kemungkinan Word ini belum mendukung "
                "pembacaan nomor daftar (WordApi 1.3)."
            )
        else:
            sebab = (
                f"{berpenanda} paragraf sudah membawa nomor otomatis, tetapi tidak "
                "satu pun berbentuk \"Pasal N\". Periksa apakah naskahnya memang "
                "belum punya batang tubuh."
            )
        return (
            f"Tidak satu pun Pasal terbaca dari {len(paragraf)} paragraf — "
            f"Fase 2 tidak dijalankan. {sebab} Fase 1 tetap berjalan seperti biasa."
        )

    # KMK belum didukung Fase 2 — dan diamnya harus TERDENGAR.
    #
    # KMK tidak memakai Pasal, melainkan diktum KESATU/KEDUA/KETIGA. Parser
    # ini cuma mengenal Pasal, jadi pada KMK ia menghasilkan pembukaan saja
    # dan isi diktumnya tidak terbaca sama sekali. Tanpa penjaga ini, `gagal`
    # bernilai None dan penelaah mengira KMK-nya sudah diperiksa padahal
    # isinya tidak pernah tersentuh — persis kegagalan paling berbahaya
    # menurut ukuran proyek ini: diam yang tidak kelihatan.
    #
    # Diputuskan 22 Sep 2026: Fase 2/3 fokus PMK dulu supaya batas dan alurnya
    # jelas. KMK menyusul, bukan dibuang.
    if not pasal:
        for p in paragraf:
            if _POLA_DIKTUM_KMK.match(_trim(p.utuh)):
                return (
                    "Naskah ini memakai diktum (KESATU, KEDUA, …), bukan Pasal — "
                    "ciri KMK. Fase 2 baru mendukung PMK; pemeriksaan Fase 2 "
                    "tidak dijalankan. Fase 1 tetap berjalan seperti biasa."
                )

    nomor_terbaca = []
    for s in pasal:
        m = re.match(r"^(\d+)", s.nomor)
        if m:
            nomor_terbaca.append(int(m.group(1)))
    for a, b in zip(nomor_terbaca, nomor_terbaca[1:]):
        if b - a > _BATAS_LOMPATAN_PASAL:
            return (
                f"Penomoran pasal melompat dari {a} ke {b}. Itu menandakan "
                "pembacaan yang kacau, bukan penomoran naskah yang cacat."
            )

    for s in hasil:
        if not s.bisa_ditandai:
            return (
                f"Satuan '{s.id}' tidak punya rentang paragraf yang sah. "
                "Satuan tanpa rentang tidak boleh ditandai."
            )
    return None
