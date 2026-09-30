"""Skema data Temuan — kontrak antara backend dan frontend.

Penjelasan lengkap tiap field ada di docs/fase1 drafter.md bagian 11, dan
HANYA di sana. Berkas docs/kontrak-data.md yang dulu memuat salinannya sudah
dihapus 18 Sep 2026: dua berkas yang harus disamakan manual setiap kali berubah
adalah pabrik cacat, dan keduanya sempat benar-benar berbeda isi.

Revisi 17 Sep 2026:
- `tingkat_keparahan` DIHAPUS. Dulu dipakai memilih warna sorotan dan menyaring
  daftar panel; keduanya sudah tidak ada.
- `nomor` DITAMBAHKAN — nomor urut temuan menurut posisinya di dokumen,
  ditampilkan ke penelaah sebagai (T1), (T2), dst.
- `jenis_tanda` DITAMBAHKAN — menentukan cara temuan dipasang di dokumen.
- `jenis_dokumen` DITAMBAHKAN di AnalisisRequest, wajib, dipilih penelaah.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enum
# ---------------------------------------------------------------------------

class JenisDokumen(str, Enum):
    """Jenis dokumen yang sedang ditelaah. Dipilih penelaah, tidak ditebak."""

    PMK = "PMK"
    KMK = "KMK"


class JenisTanda(str, Enum):
    """Cara temuan dipasang di dokumen.

    PENGGANTIAN — ada rumusan pengganti yang pasti untuk lokasi.teks_asli.
                  Teks lama diberi warna merah dan dicoret; usulannya
                  disisipkan hijau di sebelahnya. Teks lama TIDAK dihapus.
    PENGHAPUSAN — kesalahannya terbukti dan perbaikannya MEMBUANG, bukan
                  mengganti. Teks lama merah dan dicoret, tanpa sisipan
                  hijau — tidak ada rumusan pengganti yang masuk akal.
    CATATAN     — tidak ada pengganti tunggal, cukup blok kuning + komentar.
                  Warna huruf tidak disentuh sama sekali.

    PENGHAPUSAN ditambahkan atas penetapan penelaah 23 Sep 2026: kalau alat
    sudah yakin sesuatu salah, aneh kalau ia tidak menawarkan perbaikan —
    "kecuali kesalahannya mewajibkan itu dihapus, baru boleh tidak memberikan
    saran perbaikan (teks berwarna hijau)".

    TIDAK ADA satu pun yang menghapus teks penelaah. PENGHAPUSAN cuma
    mewarnai dan mencoret; yang menghapus tetap penelaah. CLAUDE.md butir 5.

    Keterangan lama menyebut PENGGANTIAN dipasang sebagai perubahan terlacak
    (Track Changes). Jalur itu ditinggalkan 17 Sep 2026 karena warna revisinya
    tidak bisa diatur add-in — lihat docs/fase1 drafter.md bagian 6.1.
    """

    PENGGANTIAN = "penggantian"
    PENGHAPUSAN = "penghapusan"
    CATATAN = "catatan"


class StatusTemuan(str, Enum):
    BELUM_DITINJAU = "belum_ditinjau"
    DITERIMA = "diterima"
    DITOLAK = "ditolak"


# ---------------------------------------------------------------------------
# Bagian-bagian Temuan
# ---------------------------------------------------------------------------

class LokasiTemuan(BaseModel):
    """Posisi temuan di dalam dokumen."""

    paragraf_index: int = Field(
        ..., description="Indeks paragraf dalam daftar yang dikirim"
    )
    offset_mulai: int = Field(
        ..., description="Posisi karakter awal di dalam paragraf"
    )
    panjang: int = Field(
        ..., description="Panjang karakter yang ditandai"
    )
    teks_asli: str = Field(
        ..., description="Teks asli yang bermasalah"
    )


class RujukanTemuan(BaseModel):
    """Rujukan ke butir KMK 527."""

    sumber: str = Field(
        ..., description="Nama peraturan sumber"
    )
    butir: str = Field(
        ..., description="Nomor butir spesifik"
    )
    kutipan: str = Field(
        ..., description="Kutipan isi butir"
    )
    pdf_url: str = Field(
        ..., description="URL PDF di JDIH"
    )
    halaman: str = Field(
        default="",
        description=(
            "Nomor halaman butirnya di PDF KMK 527. Inilah yang benar-benar "
            "menolong penelaah membuka butirnya; `pdf_url` seluruhnya menunjuk "
            "beranda jdih, bukan peraturannya — jadi komentar menyebut halaman "
            "ini dan membuang tautannya (ditetapkan penelaah 26 Sep 2026)."
        ),
    )
    status: str = Field(
        default="placeholder",
        description=(
            "Keandalan rujukan: 'placeholder' (belum diisi), 'ekstraksi' "
            "(dari teks OCR, belum dibaca manusia), atau 'visual' (sudah "
            "diketik ulang manusia dari naskah). Antarmuka menyalakan gate "
            "legal untuk apa pun yang BUKAN 'visual' — keterisian butir "
            "bukan bukti keandalan."
        ),
    )


# ---------------------------------------------------------------------------
# Temuan — objek utama
# ---------------------------------------------------------------------------

class Temuan(BaseModel):
    """Satu temuan hasil pemeriksaan."""

    id: str = Field(
        ..., description="Identifier unik temuan dalam satu sesi analisis"
    )
    nomor: int = Field(
        default=0,
        description=(
            "Nomor urut menurut posisi di dokumen, mulai dari 1. Diisi "
            "jalankan_semua() sesudah seluruh temuan diurutkan — aturan "
            "masing-masing tidak tahu urutan global."
        ),
    )
    aturan_id: str = Field(
        ...,
        description=(
            "Kunci ke tabel rujukan (F1-001, dst.). INTERNAL — tidak pernah "
            "ditampilkan ke penelaah; yang dibaca penelaah adalah `nomor`."
        ),
    )
    fase: int = Field(
        default=1,
        description=(
            "Fase pemeriksaan: 1 format baku, 2 konsistensi dan kejelasan, "
            "3 pertentangan dengan peraturan lain. Dipakai panel untuk "
            "MENGELOMPOKKAN secara visual, tidak pernah untuk menomori ulang."
        ),
    )
    satuan_id: Optional[str] = Field(
        default=None,
        description=(
            "Alamat satuan asal temuan, mis. 'pasal-12-ayat-2'. Kosong untuk "
            "Fase 1, yang bekerja di atas paragraf datar dan tidak mengenal "
            "satuan. Dipakai panel untuk menyebut letaknya dengan bahasa "
            "naskah, bukan nomor paragraf Word."
        ),
    )
    skor: Optional[float] = Field(
        default=None,
        description=(
            "Keyakinan model, 0.0–1.0. Kosong untuk temuan deterministik, dan "
            "kekosongan itu BERARTI: temuan tanpa skor kesalahannya bisa "
            "dibuktikan baris demi baris, temuan berskor hasil penalaran. "
            "Yang di bawah ambang tidak pernah sampai ke sini — sudah gugur "
            "di Langkah 5."
        ),
    )
    jenis_tanda: JenisTanda = Field(
        ..., description="Cara temuan dipasang di dokumen"
    )
    lokasi: LokasiTemuan
    catatan: str = Field(
        ...,
        description=(
            "ALASAN temuan, bukan pengulangan apa yang sudah terlihat di "
            "naskah. Dipasang sebagai baris pertama komentar Word."
        ),
    )
    saran: str = Field(
        default="",
        description=(
            "APA YANG SEBAIKNYA DILAKUKAN penelaah — dipisah dari `catatan` "
            "supaya komentar Word bisa ditata 'Temuan:' lalu 'Saran:'. "
            "Catatan menjelaskan apa yang ditemukan; saran menjelaskan jalan "
            "keluarnya. Menggabung keduanya membuat penelaah harus memilah "
            "sendiri mana pernyataan dan mana anjuran."
        ),
    )
    sumber_usulan: str = Field(
        default="",
        description=(
            "DARI MANA rumusan hijau itu datang, dalam bentuk yang dibaca "
            "manusia — 'istilah berdefinisi Pasal 1: Pengguna Barang', atau "
            "'PMK 40 TAHUN 2024 (masih berlaku)'.\n"
            "\n"
            "Medan sendiri, TIDAK dilebur ke `saran`. Alasannya: komentar "
            "temuan hijau sengaja melewati blok Saran — penggantinya sudah "
            "terbaca hijau di naskah, jadi mengulangnya cuma memanjangkan "
            "balon. Tetapi sumbernya WAJIB tetap terbaca, karena itulah syarat "
            "kebijakan hijau: penelaah harus bisa memeriksa sendiri bahwa ini "
            "bukan asal klaim. Selama ia menumpang di `saran`, melewati blok "
            "itu ikut membuang sumbernya.\n"
            "\n"
            "Hanya terisi pada temuan `penggantian`."
        ),
    )
    juga_di: list[str] = Field(
        default_factory=list,
        description=(
            "Tempat LAIN di naskah yang memuat kesalahan yang sama persis — "
            "aturan sama, teks sama, tempat perbaikan sama — dalam bentuk "
            "yang dibaca manusia: 'Pasal 13 ayat (2)'.\n"
            "\n"
            "Satu kesalahan yang terulang di banyak tempat menjadi SATU kartu "
            "dan SATU komentar di kemunculan pertamanya; kemunculan lainnya "
            "tidak disorot, cuma disebut di sini. Ditetapkan penelaah 27 Sep "
            "2026, sesudah PMK 104 mendapat satu komentar untuk tiap baris "
            "yang memuat 'RPKBUNP SPAN'. Berlaku juga untuk temuan hijau: "
            "hijaunya hanya di kemunculan pertama, sisanya diperbaiki penelaah "
            "sendiri dengan panduan daftar ini."
        ),
    )
    sasaran: str = Field(
        default="",
        description=(
            "DI MANA perbaikannya dikerjakan, sudah dalam bentuk yang dibaca "
            "manusia — 'Pasal 1 (Ketentuan Umum)', 'bagian Menimbang'.\n"
            "\n"
            "Muncul sebagai baris 'Perbaiki di:' di komentar Word, di antara "
            "Temuan dan Saran. Kosong berarti tempatnya tidak bisa dibuktikan, "
            "dan barisnya tidak ditulis sama sekali — bukan ditebak.\n"
            "\n"
            "Juga kosong bila tempatnya sama dengan satuan tempat temuan ini "
            "menempel: menulis 'Perbaiki di: Pasal 5' pada komentar yang "
            "memang ada di Pasal 5 menambah baris tanpa menambah keterangan."
        ),
    )
    sasaran_paragraf: Optional[int] = Field(
        default=None,
        description=(
            "Nomor paragraf tempat `sasaran` berada, supaya panel bisa "
            "melompat ke sana — tombol 'Lompat ke Perbaikan' di kartu.\n"
            "\n"
            "Nomor paragraf, BUKAN id satuan: panel tidak memegang pohon "
            "satuan, dan Word mengalamati isinya dengan nomor paragraf. "
            "Kosong berarti sasarannya bukan satuan yang bisa ditunjuk "
            "(mis. bagian Menimbang) atau tidak terbukti ada."
        ),
    )
    usulan_rumusan: Optional[str] = Field(
        default=None,
        description=(
            "Teks pengganti harfiah untuk lokasi.teks_asli.\n"
            "\n"
            "Wajib terisi bila jenis_tanda = penggantian — dan penggantian "
            "hanya boleh dipakai ketika kesalahannya TERBUKTI dan "
            "penggantinya SATU DAN PASTI. Pada temuan `catatan`, field ini "
            "boleh terisi sebagai contoh rumusan yang ikut dibacakan di "
            "komentar, tetapi TIDAK PERNAH disisipkan ke naskah."
        ),
    )
    catatan_ai: str = Field(
        default="",
        description=(
            "KEBERATAN model atas temuan ini — dan hanya keberatan, bukan "
            "pembatalan.\n"
            "\n"
            "Model membaca temuan Fase 1 saat menyusun peta, sehingga ia tahu "
            "apa yang sudah ditemukan pemeriksaan format. Kalau menurutnya "
            "sebuah temuan keliru karena konteks yang lebih luas, ia menulisnya "
            "di sini dan temuannya TETAP ADA.\n"
            "\n"
            "Ditetapkan penelaah 23 Sep 2026: model tidak pernah menghapus "
            "temuan yang kesalahannya sudah terbukti. Keyakinan tidak "
            "menghapus bukti, dan temuan yang hilang diam-diam adalah "
            "kegagalan yang paling sulit diketahui penelaah."
        ),
    )
    tanpa_sorot: bool = Field(
        default=False,
        description=(
            "True HANYA untuk temuan yang kesalahannya adalah KETIADAAN "
            "sesuatu (bagian wajib hilang, atau frasa hilang dari judul "
            "Menetapkan) — bukan kata tertentu yang salah. `lokasi` di sini "
            "menunjuk anchor NETRAL (baris judul pembuka dokumen), dipilih "
            "hanya karena selalu ada dan aman disentuh — BUKAN klaim bahwa "
            "teks di situ salah.\n"
            "\n"
            "Panel tetap memasang komentar dan content control seperti "
            "temuan lain (sehingga dapat Terima/Tolak seperti biasa), tetapi "
            "MELEWATI pewarnaan sorot/highlight supaya anchor netral itu "
            "tidak terlihat seolah teksnya sendiri yang bermasalah.\n"
            "\n"
            "Ditambahkan 27 Sep 2026. Sebelum ini, temuan begini (F1-002 "
            "jalur cadangan, F1-003) tidak punya lokasi sama sekali — sehingga "
            "tidak pernah dikomentari di Word, dan tidak bisa Terima/Tolak. "
            "Penelaah menyebutnya bug: temuan yang sudah dilaporkan wajib "
            "bisa didiskusikan lewat komentar dan diputuskan, sekalipun "
            "letak persisnya tidak ada. CLAUDE.md butir 6 tetap berlaku —"
            "yang berubah bukan menyorot rentang yang tidak presisi, "
            "melainkan memasang komentar pada rentang PRESISI yang memang "
            "aman (anchor netral), bukan menandai teks yang belum tentu "
            "salah."
        ),
    )
    rujukan: RujukanTemuan
    status: StatusTemuan = Field(
        default=StatusTemuan.BELUM_DITINJAU
    )


# ---------------------------------------------------------------------------
# Request / Response untuk endpoint analisis
# ---------------------------------------------------------------------------

class ParagrafInput(BaseModel):
    """Satu paragraf yang dikirim dari frontend.

    DUA MEDAN UNTUK SATU PARAGRAF, DAN PEMBEDAANNYA MENENTUKAN:

        teks     isi paragraf PERSIS seperti yang Word simpan. Seluruh
                 penghitungan offset penandaan memakai ini, dan hanya ini.
        penanda  nomor yang dibuat mesin penomoran Word — "Pasal 5", "(2)",
                 "a.", "BAB I". Tampil di layar, tetapi BUKAN bagian teks.

    Kenapa tidak ditempel saja jadi satu: `lokasi.offset_mulai` dihitung
    terhadap `teks`, dan `office.ts` mencari teks itu di naskah saat menandai.
    Kalau backend memakai teks berawalan "(2) " sementara Word tidak punya
    awalan itu, SELURUH penandaan meleset sepanjang awalannya.
    """

    index: int = Field(..., description="Indeks paragraf di dokumen")
    teks: str = Field(..., description="Isi teks paragraf, persis seperti di Word")
    penanda: str = Field(
        default="",
        description=(
            "Nomor otomatis Word, apa adanya seperti tampil: 'Pasal 5', '(2)', "
            "'a.', 'BAB I'. Kosong untuk paragraf yang tidak bernomor "
            "otomatis.\n"
            "\n"
            "Tanpa ini, naskah PMK sungguhan tidak terbaca strukturnya: pada "
            "PMK 18 Tahun 2026, 585 dari 974 paragraf bernomor otomatis dan "
            "110 di antaranya teksnya KOSONG SAMA SEKALI — seluruh isinya "
            "nomor. Parser melihat dokumen tanpa satu pun Pasal."
        ),
    )
    tingkat: int = Field(
        default=-1,
        description=(
            "Tingkat kedalaman penomoran (ilvl Word), 0 paling luar. -1 "
            "berarti paragraf ini bukan butir bernomor. Satu definisi "
            "penomoran memuat beberapa tingkat sekaligus — pada PMK 18, "
            "numId 274 mendefinisikan 'Pasal %1' di tingkat 0 dan '(%2)' di "
            "tingkat 1."
        ),
    )
    tampil_kapital: bool = Field(
        default=False,
        description=(
            "True bila paragraf ini DITAMPILKAN kapital seluruhnya lewat "
            "atribut All Caps, meskipun huruf aslinya campur. Diisi frontend "
            "dari font.allCaps. Tanpa ini, aturan judul kapital salah menandai "
            "judul yang sebenarnya sudah tampil kapital — lihat docs/"
            "fase1 drafter.md bagian 6.9."
        ),
    )

    # --- Letak fisik di Word (bug 7 dan 11) ------------------------------
    #
    # Tabel tidak selalu berarti data: PMK 119 menulis hampir seluruh batang
    # tubuhnya di tabel tata letak, nomor "1." di satu sel dan teksnya di sel
    # sebelahnya. Tanpa letak ini parser tidak tahu keduanya satu butir, dan
    # seluruh definisi Pasal 1 tidak pernah sampai ke model.
    tabel: int = Field(
        default=-1,
        description=(
            "Nomor urut tabel TERDALAM yang memuat paragraf ini, menurut urutan "
            "kemunculan di naskah (mulai 0). -1 bila bukan di tabel."
        ),
    )
    baris: int = Field(default=-1, description="Nomor baris di tabel itu (mulai 0); -1 bila bukan di tabel.")
    sel: int = Field(default=-1, description="Nomor sel di baris itu (mulai 0); -1 bila bukan di tabel.")
    gambar: int = Field(
        default=0,
        description=(
            "Jumlah gambar sebaris di paragraf ini. Isinya tidak bisa dibaca "
            "model — bahan menyebutnya terang-terangan, bukan diam."
        ),
    )
    rumus: int = Field(
        default=0,
        description=(
            "Jumlah rumus (persamaan Word) di paragraf ini. Hanya terisi dari "
            "alat uji: Office.js tidak punya API untuk rumus."
        ),
    )
    letak_pasti: bool = Field(
        default=True,
        description=(
            "False untuk paragraf SESUDAH tabel raksasa. Panel tidak membaca isi "
            "tabel itu, jadi tidak bisa menghitung nomor paragraf sesudahnya — "
            "`index`-nya urutan baca, bukan nomor paragraf Word. Temuan di sini "
            "tetap dilaporkan di panel tetapi TIDAK PERNAH ditandai di naskah "
            "(CLAUDE.md butir 6)."
        ),
    )

    @property
    def utuh(self) -> str:
        """Paragraf seperti TERBACA MATA — nomornya ikut, dipisah satu spasi.

        Dipakai PARSER Fase 2 untuk mengenali struktur, dan TIDAK BOLEH
        dipakai menghitung offset penandaan. Pemisahnya sengaja satu spasi,
        sama seperti naskah yang nomornya diketik tangan, supaya pola parser
        yang sudah ada berlaku apa adanya tanpa diubah.
        """
        if not self.penanda:
            return self.teks
        return f"{self.penanda} {self.teks}".strip()


class KerangkaTabel(BaseModel):
    """Tabel raksasa yang TIDAK dibaca per paragraf — cuma kerangkanya.

    PMK 108/2024 memuat 228 ribu baris tabel (609 ribu paragraf). Membacanya
    paragraf demi paragraf lewat Office.js membuat Word macet, jadi tabel
    tingkat teratas di atas 1.000 baris dikirim sebagai kerangka: jumlah baris
    dan kolom, dan beberapa baris pertama (judul kolom biasanya di sana).
    Ditetapkan penelaah 29 Sep 2026. Isi lengkapnya tidak pernah sampai ke
    backend, jadi model diberi tahu terang-terangan bahwa isinya tidak dibaca.
    """

    tabel: int = Field(..., description="Nomor urut tabel, sama dengan ParagrafInput.tabel.")
    sesudah_paragraf: int = Field(
        ..., description="index paragraf terakhir SEBELUM tabel ini; -1 bila tabel di awal naskah."
    )
    jumlah_baris: int
    jumlah_kolom: int
    contoh: list[list[str]] = Field(
        default_factory=list, description="Beberapa baris pertama, teks tiap sel."
    )


class AnalisisRequest(BaseModel):
    """Request body untuk POST /analisis/jalankan."""

    jenis_dokumen: JenisDokumen = Field(
        ...,
        description=(
            "PMK atau KMK. WAJIB — dipilih penelaah di task pane sebelum "
            "menekan Analisis. Backend tidak menebaknya sendiri."
        ),
    )
    paragraf: list[ParagrafInput] = Field(
        ..., description="Daftar paragraf dari dokumen"
    )
    aturan_aktif: Optional[list[str]] = Field(
        default=None,
        description=(
            "Daftar aturan_id yang dijalankan, mis. [\"F1-002\", \"F1-005\"]. "
            "Dipilih penelaah lewat panel Pengaturan di task pane. None berarti "
            "jalankan semua aturan yang aktif secara bawaan — perilaku lama, "
            "supaya pemanggil yang belum tahu field ini tidak berubah artinya."
        ),
    )


class AnalisisResponse(BaseModel):
    """Response body dari POST /analisis/jalankan."""

    temuan: list[Temuan] = Field(
        default_factory=list, description="Daftar temuan hasil pemeriksaan"
    )
    jumlah_paragraf: int = Field(
        ..., description="Jumlah paragraf yang diperiksa"
    )
