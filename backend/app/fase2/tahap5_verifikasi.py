"""LANGKAH 5 — gerbang terakhir. SATU-SATUNYA tempat calon jadi Temuan.

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

from app.fase2.tahap0_definisi import DaftarDefinisi
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
#   F2-1xx  BOLEH hijau, tetapi HANYA kalau rumusannya datang dari Langkah 6c:
#           penilaian model atas dirinya sendiri bukan bukti, sementara
#           rumusan yang dipakai peraturan yang masih berlaku adalah bukti
#           yang bisa ditunjuk — dan peraturannya disebut di komentar supaya
#           penelaah memeriksanya sendiri. Syarat itu ditegakkan kode lewat
#           `_HIJAU_BUTUH_PEMBANDING`, bukan diserahkan ke niat baik.
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

# Aturan yang hijaunya menuntut sumber luar. Tanpa `pembanding` terisi,
# usulannya turun jadi contoh rumusan di komentar seperti sebelumnya.
#
# Inilah yang membedakan kebijakan baru dari melonggarkan begitu saja: yang
# dibuka bukan izin bagi model menulis ke naskah, melainkan izin bagi rumusan
# yang sudah dipakai peraturan berlaku untuk masuk sebagai usulan.
_HIJAU_BUTUH_PEMBANDING: set[str] = {
    "F2-101",
    "F2-102",
    "F2-103",
    "F2-104",
    "F2-105",
}


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


def boleh_menyisipkan(aturan_id: str, pembanding: str = "") -> bool:
    """Apakah aturan ini boleh mencoret naskah dan menyisipkan usulan hijau.

    SATU-SATUNYA tempat kebijakan hijau/kuning ditetapkan. Jalur mekanis
    (F2-0xx) memanggilnya juga, supaya tidak ada dua kebijakan yang bisa
    berselisih diam-diam.

    `pembanding` nama peraturan yang jadi sumber rumusannya. Wajib terisi
    untuk aturan penalaran: kosong berarti usulannya lahir dari model sendiri,
    dan penilaian model atas dirinya sendiri bukan bukti.
    """
    if aturan_id not in _ATURAN_BOLEH_HIJAU:
        return False
    if aturan_id in _HIJAU_BUTUH_PEMBANDING and not pembanding.strip():
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


def _cari_lokasi(
    calon: CalonTemuan, pohon: PohonSatuan, paragraf: list[ParagrafInput]
) -> Optional[LokasiTemuan]:
    """Pemeriksaan ① — kutipannya ada persis di dalam rentang satuannya."""
    satuan = pohon.cari(calon.satuan_id)
    if satuan is None or not satuan.bisa_ditandai:
        return None
    for p in paragraf:
        if not (satuan.paragraf_mulai <= p.index < satuan.paragraf_akhir):
            continue
        posisi = p.teks.find(calon.teks_asli)
        if posisi == -1:
            continue
        return LokasiTemuan(
            paragraf_index=p.index,
            offset_mulai=posisi,
            panjang=len(calon.teks_asli),
            teks_asli=calon.teks_asli,
        )
    return None


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

    Penjagaannya: kalau ekor teks-sebelum muncul lagi di dalam usulan, berarti
    usulannya menggantikan lebih banyak daripada yang dicoret.
    """
    if not usulan:
        return False
    if _BUKAN_PENGGANTI.match(usulan):
        return False
    if usulan.strip() == teks_asli.strip():
        return False  # tidak mengubah apa pun

    batas = max(len(teks_asli) * _LIPAT_MAKS, len(teks_asli) + _SELISIH_BEBAS)
    if len(usulan) > batas:
        return False

    awal = sebelum.strip()
    if len(awal) >= _SEBELUM_TERLALU_PENDEK and awal[-_EKOR_SEBELUM:] in usulan:
        return False

    return True


def verifikasi_satu(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    ambang: float = 0.7,
    pembanding_sah: Optional[set[str]] = None,
) -> Hasil:
    """Jalankan kelima pemeriksaan atas satu calon."""

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

    # ① Kutipannya wajib ketemu persis.
    lokasi = _cari_lokasi(calon, pohon, paragraf)
    if lokasi is None:
        return Hasil(None, "kutipan tidak ketemu persis di naskah: " + repr(calon.teks_asli))

    # ④ Boleh hijau hanya bila aturannya memang membuktikan kesalahan DAN
    #    penggantinya pasti; lalu usulannya wajib pengganti harfiah, dan
    #    istilah berdefinisi di dalamnya wajib dieja persis.
    diturunkan = ""
    usulan = calon.usulan_rumusan
    boleh_hijau = boleh_menyisipkan(calon.aturan_id, calon.pembanding)

    if usulan and not boleh_hijau:
        # Usulannya TIDAK dibuang — ia ikut ke komentar sebagai contoh rumusan
        # yang dibaca penelaah. Yang tidak terjadi cuma penyisipannya ke naskah.
        diturunkan = (
            "usulan tanpa peraturan sumber — jadi contoh rumusan, bukan coretan"
            if calon.aturan_id in _HIJAU_BUTUH_PEMBANDING
            else "aturan ini tidak membuktikan kesalahan — usulan jadi saran, bukan coretan"
        )
    elif usulan:
        sebelum = ""
        for p in paragraf:
            if p.index == lokasi.paragraf_index:
                sebelum = p.teks[: lokasi.offset_mulai]
                break
        if not usulan_harfiah(usulan, calon.teks_asli, sebelum):
            diturunkan = "usulan bukan pengganti harfiah untuk rentang yang dicoret"
        elif daftar.gagal is None and (salah_eja := daftar.cari_mirip(usulan)):
            diturunkan = "istilah berdefinisi salah eja di usulan: " + ", ".join(salah_eja)

    hijau = boleh_hijau and bool(usulan) and not diturunkan

    # Usulan yang tidak jadi hijau tetap dibawa, tetapi pindah tempat: ia
    # masuk ke Saran sebagai CONTOH rumusan, bukan sebagai pengganti yang
    # disisipkan. Membuangnya berarti membuang bagian paling berguna dari
    # jawaban model; menyisipkannya berarti mengubah naskah tanpa bukti.
    saran = calon.saran
    if usulan and not hijau:
        contoh = f'Contoh rumusan: "{usulan}"'
        saran = f"{saran} {contoh}".strip() if saran else contoh

    # Usulan hijau yang bersumber dari peraturan lain WAJIB menyebut sumbernya
    # di komentar. Itu syarat kebijakan hijau, bukan hiasan: penelaah harus
    # bisa memeriksa sendiri bahwa ini bukan asal klaim. Namanya sudah
    # dibuktikan ada di hasil pencarian pada pemeriksaan ③ di atas.
    if hijau and calon.pembanding:
        sumber = f"Rumusan serupa: {calon.pembanding} (masih berlaku)."
        saran = f"{saran} {sumber}".strip() if saran else sumber

    return Hasil(
        Temuan(
            id="f-" + uuid.uuid4().hex[:8],
            aturan_id=calon.aturan_id,
            fase=3 if calon.aturan_id.startswith("F3") else 2,
            jenis_tanda=JenisTanda.PENGGANTIAN if hijau else JenisTanda.CATATAN,
            satuan_id=calon.satuan_id,
            skor=calon.skor,
            lokasi=lokasi,
            catatan=calon.alasan.strip(),
            saran=saran.strip(),
            sasaran=sebutan_sasaran(calon.sasaran, calon.satuan_id, pohon),
            usulan_rumusan=usulan if hijau else None,
            rujukan=RujukanTemuan(**ambil_rujukan(calon.aturan_id)),
            status=StatusTemuan.BELUM_DITINJAU,
        ),
        diturunkan=diturunkan,
    )


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
) -> tuple[list[Temuan], list[str]]:
    """Verifikasi seluruh calon. Kembalikan temuan yang lolos dan alasan gugur.

    `temuan_ada` temuan yang sudah terpasang di naskah — Fase 1, dan temuan
    mekanis Fase 2 yang lebih dulu jadi. Calon yang rentangnya bertindihan
    dengan salah satunya dibuang, supaya tidak ada dua komentar pada huruf
    yang sama.

    Temuan yang lolos diurutkan menurut posisi dokumen. Penomorannya TIDAK
    dilakukan di sini: nomor Fase 2 melanjutkan nomor terakhir Fase 1 dan
    tidak pernah diurutkan ulang, jadi hanya pemanggil yang tahu mulai dari
    berapa.
    """
    lolos: list[Temuan] = []
    gugur: list[str] = []
    # Temuan yang baru lahir ikut jadi pembanding untuk calon berikutnya —
    # dua temuan Fase 2 pada rentang yang sama sama menumpuknya dengan
    # bertabrakan dengan Fase 1.
    sudah: list[Temuan] = list(temuan_ada or [])

    for c in calon:
        hasil = verifikasi_satu(c, pohon, daftar, paragraf, ambang, pembanding_sah)
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

    lolos.sort(key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai))
    return lolos, gugur
