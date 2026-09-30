"""Bentuk data untuk analisis panjang Fase 2/3 — pekerjaan, dugaan, calon.

BERKAS INI TIDAK MENGERJAKAN APA PUN, sekelas dengan temuan.py dan satuan.py.
Ia menetapkan tiga bentuk yang berpindah tangan antar-tahap:

    Dugaan        keluaran tahap 3 (cari dugaan). BELUM temuan. Tidak pernah
                  menyentuh naskah sebelum lolos tahap 4.
    CalonTemuan   keluaran tahap 4 (memastikan) dan korpus. Masih belum
                  menyentuh naskah: tahap 5 yang memutuskan ia jadi Temuan
                  atau gugur.
    Pekerjaan     keadaan satu kali analisis, supaya panel bisa menampilkan
                  kemajuan dan supaya backend yang mati di tengah jalan tidak
                  menghanguskan yang sudah dibayar.

Kenapa dipisah bertingkat begini, tidak langsung jadi Temuan: supaya tidak ada
satu pun jalan pintas dari tebakan model ke naskah orang. Tiap tingkat punya
satu pemeriksa, dan Temuan baru lahir di ujung terakhir.

`BarisPeta` sudah dihapus 29 Sep 2026 bersama petanya (bug 7): model kini
membaca naskah utuh, bukan ringkasan per satuan.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class StatusPekerjaan(str, Enum):
    MENUNGGU = "menunggu"
    BERJALAN = "berjalan"
    SELESAI = "selesai"
    GAGAL = "gagal"


class Dugaan(BaseModel):
    """Keluaran tahap 3. BELUM temuan — wajib lewat tahap 4 dulu."""

    satuan_id: str
    satuan_lain: str = Field(
        default="", description="Terisi hanya bila ini dugaan tabrakan antar-dua satuan."
    )
    jenis: str = Field(
        default="",
        description="makna_ganda | pemikul | operasional | tabrakan | cakupan | lampiran",
    )
    alasan: str = ""
    eksternal: bool = Field(
        default=False,
        description=(
            "True bila pembuktiannya menuntut dokumen DI LUAR rancangan ini. "
            "Yang menentukan apakah pencarian korpus (F3-001) dijalankan."
        ),
    )
    asal: str = Field(
        default="", description="Panggilan tahap 3 yang melahirkannya — untuk Ekspor Tahap 5."
    )

    @property
    def tabrakan(self) -> bool:
        return bool(self.satuan_lain)


class CalonTemuan(BaseModel):
    """Keluaran tahap 4 atau korpus. Masuk ke tahap 5 untuk diverifikasi.

    Bedanya dengan Temuan: calon masih memegang `teks_asli` sebagai kutipan
    MENTAH dari model. Belum dibuktikan kutipan itu benar-benar ada di naskah.
    Tahap 5 yang membuktikannya, dan yang tidak terbukti tidak pernah sampai
    ke naskah.
    """

    aturan_id: str
    satuan_id: str
    satuan_lain: str = ""
    alasan: str = ""
    teks_asli: str = ""
    saran: str = ""
    sasaran: str = Field(
        default="",
        description=(
            "DI MANA perbaikannya dikerjakan — id satuan atau salah satu nama "
            "tetap, BUKAN kalimat bebas, supaya bisa dibuktikan kode.\n"
            "\n"
            "Ada karena komentar yang menempel di Pasal 5 bisa menyuruh "
            "menambah definisi, padahal definisinya harus ditulis di Pasal 1. "
            "Penelaah tidak punya cara menebaknya. Tahap 5 membuktikan tempat "
            "yang disebut memang ada di naskah; yang tidak terbukti dikosongkan, "
            "karena menunjuk Pasal yang tidak ada lebih buruk daripada diam soal "
            "tempat."
        ),
    )
    usulan_rumusan: str = ""
    bacaan: list[str] = Field(
        default_factory=list,
        description=(
            "F2-101: dua cara membaca rumusan yang sama-sama masuk akal dan "
            "berbeda akibatnya. Tanpa keduanya, 'bisa dibaca dua arah' cuma "
            "kesan — tahap 5 menggugurkannya. Ditambahkan 27 Sep 2026, sesudah "
            "F2-101 menandai rumusan baku 'sesuai dengan peraturan "
            "perundang-undangan' sebagai 'terlalu umum', yang bukan dua arah."
        ),
    )
    tidak_ada: list[str] = Field(
        default_factory=list,
        description=(
            "Teks yang diklaim model TIDAK ADA di naskah. Tahap 5 mencarinya di "
            "seluruh teks mentah — ketemu di mana pun berarti klaimnya keliru, "
            "dan calonnya gugur (bug 7). Salah tandai 27 Sep 2026 lahir dari "
            "klaim begini yang tidak pernah dibuktikan."
        ),
    )
    skor: float = 0.0
    eksternal: bool = False
    pembanding: str = Field(
        default="", description="Korpus: nama peraturan pembanding, disalin dari hasil pencarian."
    )
    pembanding_sah: list[str] = Field(
        default_factory=list,
        description=(
            "Korpus: nama peraturan yang BOLEH disebut — persis yang dikirim ke "
            "model saat membandingkan. Dibawa per calon, bukan satu daftar untuk "
            "seluruh dokumen, karena tiap ketentuan punya pembandingnya sendiri. "
            "Tahap 5 memakainya untuk membuktikan model tidak menyebut peraturan "
            "dari ingatannya."
        ),
    )


class Pekerjaan(BaseModel):
    """Keadaan satu kali analisis panjang.

    Brief 8.7: Law Analyzer macet di 68/175 satuan. Yang membuat kemacetan itu
    tidak terlihat sampai terlambat adalah tidak adanya angka kemajuan. Di sini
    angkanya ada sejak panggilan pertama — per tahap: "Tahap 3 · 4/12
    panggilan", lalu "Tahap 4 · 3/10 dugaan".
    """

    id: Optional[int] = None
    dokumen: str = ""
    status: StatusPekerjaan = StatusPekerjaan.MENUNGGU
    tahap: str = Field(default="", description="Tahap yang sedang berjalan, mis. '3 cari dugaan'.")
    selesai: int = 0
    total: int = 0
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = Field(
        default="", description="Alasan gagal, atau keterangan kenapa Fase 2 tidak dijalankan."
    )

    @property
    def kemajuan(self) -> str:
        return f"{self.selesai}/{self.total}"
