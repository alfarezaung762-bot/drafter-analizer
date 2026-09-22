"""Bentuk data untuk analisis panjang Fase 2/3 — pekerjaan, peta, dugaan, calon.

BERKAS INI TIDAK MENGERJAKAN APA PUN, sekelas dengan temuan.py dan satuan.py.
Ia menetapkan empat bentuk yang berpindah tangan antar-langkah:

    BarisPeta     keluaran Langkah 2. Satu baris per satuan. Kumpulan baris
                  inilah yang disebut PETA, dan Langkah 3 menalar di atasnya —
                  bukan di atas teks penuh.
    Dugaan        keluaran Langkah 3. BELUM temuan. Tidak pernah menyentuh
                  naskah sebelum lolos Langkah 4.
    CalonTemuan   keluaran Langkah 4 dan 6. Masih belum menyentuh naskah:
                  Langkah 5 yang memutuskan ia jadi Temuan atau gugur.
    Pekerjaan     keadaan satu kali analisis, supaya panel bisa menampilkan
                  kemajuan dan supaya backend yang mati di tengah jalan tidak
                  menghanguskan yang sudah selesai.

Kenapa dipisah bertingkat begini, tidak langsung jadi Temuan: supaya tidak ada
satu pun jalan pintas dari tebakan model ke naskah orang. Tiap tingkat punya
satu pemeriksa, dan Temuan baru lahir di ujung terakhir.
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


class BarisPeta(BaseModel):
    """Satu baris peta — hasil Langkah 2 untuk satu satuan."""

    satuan_id: str
    ringkasan: str = Field(default="", description="Satu kalimat: satuan ini mengatur apa.")
    memuat_norma: bool = False
    istilah_dipakai: list[str] = Field(default_factory=list)
    merujuk: list[str] = Field(
        default_factory=list,
        description="id satuan yang dirujuk. Diisi PARSER, bukan model.",
    )
    dugaan: str = Field(
        default="",
        description="Kejanggalan yang sudah terlihat saat membaca satuan ini sendirian.",
    )

    def baris(self) -> str:
        """Bentuk sebaris untuk dikirim ke Langkah 3.

        Sengaja padat: seluruh peta dokumen 175 satuan harus muat dalam satu
        panggilan, dan yang membuatnya muat adalah baris ini pendek.
        """
        bagian = [f"[{self.satuan_id}] {self.ringkasan}"]
        if self.merujuk:
            bagian.append("merujuk: " + ", ".join(self.merujuk))
        if self.istilah_dipakai:
            bagian.append("istilah: " + ", ".join(self.istilah_dipakai))
        if self.dugaan:
            bagian.append("DUGAAN: " + self.dugaan)
        return " | ".join(bagian)


class Dugaan(BaseModel):
    """Keluaran Langkah 3. BELUM temuan — wajib lewat Langkah 4 dulu.

    Rancangan bagian 3: "tidak ada temuan yang boleh lahir dari Langkah 3
    saja." Peta kehilangan detail, jadi apa pun yang terlihat di atasnya masih
    dugaan sampai diuji pada teks utuhnya.
    """

    satuan_id: str
    satuan_lain: str = Field(
        default="", description="Terisi hanya bila ini dugaan tabrakan antar-dua satuan."
    )
    jenis: str = Field(
        default="",
        description="tabrakan | pemikul | makna_ganda | operasional | cakupan",
    )
    alasan: str = ""
    eksternal: bool = Field(
        default=False,
        description=(
            "True bila pembuktiannya menuntut dokumen DI LUAR rancangan ini. "
            "Yang menentukan apakah Langkah 6 (korpus) wajib dijalankan."
        ),
    )

    @property
    def tabrakan(self) -> bool:
        return bool(self.satuan_lain)


class CalonTemuan(BaseModel):
    """Keluaran Langkah 4 atau Langkah 6. Masuk ke Langkah 5 untuk diverifikasi.

    Bedanya dengan Temuan: calon masih memegang `teks_asli` sebagai kutipan
    MENTAH dari model. Belum dibuktikan kutipan itu benar-benar ada di naskah.
    Langkah 5 yang membuktikannya, dan yang tidak terbukti tidak pernah
    sampai ke naskah.
    """

    aturan_id: str
    satuan_id: str
    satuan_lain: str = ""
    alasan: str = ""
    teks_asli: str = ""
    saran: str = ""
    usulan_rumusan: str = ""
    skor: float = 0.0
    eksternal: bool = False
    pembanding: str = Field(
        default="", description="Fase 3: nama peraturan pembanding, disalin dari hasil pencarian."
    )


class Pekerjaan(BaseModel):
    """Keadaan satu kali analisis panjang.

    Brief 8.7: Law Analyzer macet di 68/175 satuan. Yang membuat kemacetan itu
    tidak terlihat sampai terlambat adalah tidak adanya angka kemajuan. Di sini
    angkanya ada sejak panggilan pertama.
    """

    id: Optional[int] = None
    dokumen: str = ""
    status: StatusPekerjaan = StatusPekerjaan.MENUNGGU
    satuan_total: int = 0
    satuan_selesai: int = 0
    panggilan: int = 0
    token_masuk: int = 0
    token_keluar: int = 0
    pesan: str = Field(
        default="", description="Alasan gagal, atau keterangan kenapa Fase 2 tidak dijalankan."
    )

    @property
    def kemajuan(self) -> str:
        return f"{self.satuan_selesai}/{self.satuan_total}"
