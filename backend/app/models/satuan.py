"""Bentuk data Satuan — hasil parser Langkah 0.

Satuan = satu bagian terkecil naskah yang diperiksa. Istilahnya dari
project-brief.md bagian 8.9: "Satuan pemeriksaan ayat/butir, bukan pasal."

BERKAS INI TIDAK MENGERJAKAN APA PUN. Ia cuma menetapkan bentuknya — sekelas
dengan temuan.py. Yang membangun pohonnya fase2/tahap0_struktur.py.

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


class PohonSatuan(BaseModel):
    """Seluruh satuan sebuah dokumen, urut posisi.

    Disimpan datar, bukan bersarang. Alasannya: yang paling sering dibutuhkan
    adalah pencarian menurut id ("apakah Pasal 30 ada?"), dan itu jauh lebih
    murah di daftar datar daripada menelusuri pohon bersarang. Hubungan
    induk-anak tetap terjaga lewat field `induk`.
    """

    satuan: list[Satuan] = Field(default_factory=list)
    # Diisi parser kalau strukturnya tidak masuk akal. Selama ini terisi,
    # SELURUH Fase 2 tidak dijalankan — lihat cabang 3.6 di rancangan.
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

    def teks_lengkap(self, id_satuan: str) -> str:
        """Teks satuan berikut seluruh anak-cucunya, dirangkai urut.

        Dipakai Langkah 4 (memastikan), yang menuntut teks UTUH — bukan
        ringkasan dan bukan potongan.
        """
        akar = self.cari(id_satuan)
        if akar is None:
            return ""
        bagian = [akar.teks] if akar.teks else []
        for anak in self.anak_dari(id_satuan):
            isi = self.teks_lengkap(anak.id)
            if isi:
                bagian.append(isi)
        return " ".join(bagian).strip()
