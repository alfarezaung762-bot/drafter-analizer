"""Bentuk data Satuan — hasil parser Langkah 0.

Satuan = satu bagian terkecil naskah yang diperiksa. Istilahnya dari
project-brief.md bagian 8.9: "Satuan pemeriksaan ayat/butir, bukan pasal."

BERKAS INI TIDAK MENGERJAKAN APA PUN. Ia cuma menetapkan bentuknya — sekelas
dengan temuan.py. Yang membangun pohonnya telaah/tahap1_parser/struktur.py.

Dua field yang membuat seluruh Fase 2 bisa menandai naskah:
`paragraf_mulai` dan `paragraf_akhir`. Temuan pada sebuah satuan diterjemahkan
balik jadi lokasi paragraf, lalu masuk ke lapisan penandaan Fase 1 yang sudah
ada. Satuan yang tidak punya rentang paragraf TIDAK BOLEH ditandai.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class JenisSatuan(str, Enum):
    """Jenis satuan menurut susunan naskah peraturan (KMK 527 Lampiran II).

    Urutannya mengikuti urutan di dokumen, bukan abjad.
    """

    # --- Judul ---------------------------------------------------------
    JUDUL = "judul"

    # --- Pembukaan -----------------------------------------------------
    MENIMBANG = "menimbang"      # satu butir konsiderans: a, b, c
    MENGINGAT = "mengingat"      # satu butir dasar hukum: 1, 2, 3
    MENETAPKAN = "menetapkan"    # diktum

    # --- Batang tubuh --------------------------------------------------
    BAB = "bab"
    BAGIAN = "bagian"
    # PARAGRAF di sini ISTILAH HUKUM (pembagian di bawah Bagian),
    # BUKAN paragraf Word. Dua hal berbeda dengan nama yang sama — sumber
    # bug yang klasik, jadi disebut terang-terangan di sini.
    PARAGRAF = "paragraf"
    PASAL = "pasal"
    AYAT = "ayat"
    HURUF = "huruf"
    ANGKA = "angka"

    # --- Sisanya -------------------------------------------------------
    PENUTUP = "penutup"
    LAMPIRAN = "lampiran"


class Satuan(BaseModel):
    """Satu simpul di pohon satuan."""

    id: str = Field(
        ...,
        description=(
            "Alamat stabil, mis. 'pasal-12-ayat-2'. Dipakai sebagai kunci di "
            "peta (tabel HasilSatuan) dan saat memeriksa rujukan antar-pasal."
        ),
    )
    jenis: JenisSatuan
    nomor: str = Field(
        default="",
        description="Nomornya apa adanya: '12', '(2)', 'a', 'III'. Kosong untuk judul.",
    )
    teks: str = Field(
        default="",
        description=(
            "Isi satuan ini SAJA, tanpa anak-anaknya. Sebuah Pasal yang "
            "seluruh isinya ayat akan punya teks kosong — isinya ada di ayatnya."
        ),
    )
    induk: Optional[str] = Field(
        default=None, description="id satuan di atasnya. None untuk simpul teratas."
    )
    paragraf_mulai: int = Field(
        ..., description="Indeks paragraf pertama satuan ini, di daftar yang dikirim."
    )
    paragraf_akhir: int = Field(
        ..., description="Indeks paragraf terakhir + 1 (eksklusif, seperti slice)."
    )

    @property
    def bisa_ditandai(self) -> bool:
        """Punya rentang paragraf yang sah untuk ditandai di Word.

        Satuan tanpa rentang tidak boleh ditandai — bukan diperlebar ke
        paragraf terdekat. Kaidah warisan Fase 1 (CLAUDE.md butir 6).
        """
        return self.paragraf_akhir > self.paragraf_mulai >= 0


def label_satuan(s: Satuan) -> str:
    """Label penomoran satuan seperti tertulis di naskah: "(1)", "a.", "Pasal 3".

    Kosong untuk BAB, Bagian, dan Paragraf — teks mereka sudah memuat
    labelnya sendiri ("BAB II PEMBEBASAN BEA MASUK").
    """
    if not s.nomor:
        return ""
    if s.jenis == JenisSatuan.PASAL:
        return f"Pasal {s.nomor}"
    if s.jenis == JenisSatuan.AYAT:
        return s.nomor if s.nomor.startswith("(") else f"({s.nomor})"
    if s.jenis in (
        JenisSatuan.HURUF, JenisSatuan.ANGKA,
        JenisSatuan.MENIMBANG, JenisSatuan.MENGINGAT,
    ):
        return f"{s.nomor}."
    return ""


class PohonSatuan(BaseModel):
    """Seluruh satuan sebuah dokumen, urut posisi.

    Disimpan datar, bukan bersarang. Alasannya: yang paling sering dibutuhkan
    adalah pencarian menurut id ("apakah Pasal 30 ada?"), dan itu jauh lebih
    murah di daftar datar daripada menelusuri pohon bersarang. Hubungan
    induk-anak tetap terjaga lewat field `induk`.
    """

    satuan: list[Satuan] = Field(default_factory=list)
    # Diisi parser kalau strukturnya tidak masuk akal. Selama ini terisi,
    # SELURUH Fase 2 tidak dijalankan — lihat cabang 3.7 di rancangan.
    gagal: Optional[str] = Field(
        default=None,
        description="Alasan parser menyerah. None berarti pohonnya sehat.",
    )

    # -- pencarian ------------------------------------------------------

    def cari(self, id_satuan: str) -> Optional[Satuan]:
        for s in self.satuan:
            if s.id == id_satuan:
                return s
        return None

    def ada(self, id_satuan: str) -> bool:
        """Dipakai F2-001 dan Langkah 5: apakah rujukan ini menunjuk sesuatu?"""
        return self.cari(id_satuan) is not None

    def semua(self, jenis: JenisSatuan) -> list[Satuan]:
        return [s for s in self.satuan if s.jenis == jenis]

    def anak_dari(self, id_satuan: str) -> list[Satuan]:
        return [s for s in self.satuan if s.induk == id_satuan]

    def teks_lengkap(
        self, id_satuan: str, berlabel: bool = False, label_akar: bool = False
    ) -> str:
        """Teks satuan berikut seluruh anak-cucunya, dirangkai urut.

        Dipakai Langkah 4 (memastikan), yang menuntut teks UTUH — bukan
        ringkasan dan bukan potongan.

        `berlabel=True` untuk SETIAP teks yang dibaca model: tiap anak-cucu
        diawali labelnya — "(1)", "a.", "1." — seperti di naskah. Tanpa label,
        "Pasal 3 ayat (1) huruf b" tidak bisa ditemukan di dalam teks ayat
        (1), dan model menyimpulkan huruf b tidak ada. Terbukti pada PMK 45,
        27 Sep 2026 (CLAUDE.md butir 14).

        Tanpa label (bawaan) untuk kode yang mencocokkan kata — `sumber_internal`,
        kueri pencarian korpus — supaya "a" dan "b" tidak terhitung kata.

        `label_akar` ikut melabeli satuan akarnya sendiri. Dimatikan untuk teks
        yang menjadi sumber kutipan `teks_asli`: label di depan kalimat ikut
        tersalin, lalu tidak ketemu di paragraf Word yang labelnya berupa
        penomoran otomatis.
        """
        akar = self.cari(id_satuan)
        if akar is None:
            return ""
        bagian: list[str] = []
        if label_akar and berlabel and label_satuan(akar):
            bagian.append(f"{label_satuan(akar)} {akar.teks}".strip())
        elif akar.teks:
            bagian.append(akar.teks)
        for anak in self.anak_dari(id_satuan):
            isi = self.teks_lengkap(anak.id, berlabel=berlabel, label_akar=berlabel)
            if isi:
                bagian.append(isi)
        return " ".join(bagian).strip()

    def batang_induk(self, id_satuan: str) -> str:
        """Kalimat pembuka induk-induknya, dirangkai dari yang terluar.

        SEBUAH BUTIR TABULASI TIDAK BISA DIBACA SENDIRIAN. "PPK;" tidak
        berarti apa-apa tanpa "KPA BUN ... menetapkan pegawai ... sebagai:"
        yang mendahuluinya, dan "Pertanggungjawaban." tidak berarti apa-apa
        tanpa "Ruang lingkup pengaturan dalam Peraturan Menteri ini meliputi:".

        Terbukti pada PMK 17, 26 Sep 2026. Dikirim tanpa batang induknya,
        model membaca butir daftar ruang lingkup sebagai norma lalu menuduhnya
        tidak menyebut pemikul kewajiban — padahal daftar ruang lingkup tidak
        memuat kewajiban sama sekali. Salah tandai, CLAUDE.md butir 1. Pada
        satuan yang sama, ringkasan Langkah 2 keluar LEBIH PANJANG daripada
        teks aslinya: tanda model sedang mengarang konteks yang tidak dikirim.

        Yang diambil `teks` induknya SAJA, bukan `teks_lengkap` — kalau
        seluruh anak-cucunya ikut, butir yang diperiksa tenggelam di antara
        saudara-saudaranya.

        Tiap induk membawa labelnya ("Pasal 3", "(1)", "a."). Batang ini
        hanya dibaca model, dan tanpa label model tidak tahu butir yang
        diperiksa bernaung di huruf mana.
        """
        simpul = self.cari(id_satuan)
        if simpul is None:
            return ""

        rantai: list[str] = []
        induk = simpul.induk
        # Penjaga lingkaran: id yang menunjuk dirinya sendiri (atau berputar)
        # pernah lahir dari naskah yang penomorannya kacau, dan tanpa ini
        # seluruh analisis menggantung tanpa pesan apa pun.
        dikunjungi = {id_satuan}
        while induk and induk not in dikunjungi:
            dikunjungi.add(induk)
            atas = self.cari(induk)
            if atas is None:
                break
            label = label_satuan(atas)
            if atas.teks or label:
                rantai.append(f"{label} {atas.teks}".strip())
            induk = atas.induk

        rantai.reverse()
        # Dipisah " — ", bukan spasi: tanpa pemisah, judul bab menyatu dengan
        # kalimat pasalnya jadi "BAB I KETENTUAN UMUM Ruang lingkup pengaturan
        # ... meliputi:" — satu kalimat rancu yang tidak ada di naskah mana pun.
        return " — ".join(rantai).strip()

    def teks_dengan_induk(self, id_satuan: str) -> str:
        """`teks_lengkap` yang didahului batang kalimat induknya.

        Inilah bentuk yang dikirim ke model — bukan `teks_lengkap` telanjang.
        Alasannya di `batang_induk`.
        """
        batang = self.batang_induk(id_satuan)
        isi = self.teks_lengkap(id_satuan, berlabel=True, label_akar=True)
        if batang and isi:
            return f"{batang} {isi}"
        return isi or batang
