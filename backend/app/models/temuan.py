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
    CATATAN     — tidak ada pengganti tunggal, cukup blok kuning + komentar.
                  Warna huruf tidak disentuh sama sekali.

    Keterangan lama menyebut PENGGANTIAN dipasang sebagai perubahan terlacak
    (Track Changes). Jalur itu ditinggalkan 17 Sep 2026 karena warna revisinya
    tidak bisa diatur add-in — lihat docs/fase1 drafter.md bagian 6.1.
    """

    PENGGANTIAN = "penggantian"
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
    usulan_rumusan: Optional[str] = Field(
        default=None,
        description=(
            "Wajib terisi bila jenis_tanda = penggantian, dan harus berupa "
            "teks pengganti harfiah untuk lokasi.teks_asli."
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
    """Satu paragraf yang dikirim dari frontend."""

    index: int = Field(..., description="Indeks paragraf di dokumen")
    teks: str = Field(..., description="Isi teks paragraf")
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
