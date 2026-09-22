"""TAHAP 0 — pohon satuan → daftar istilah Pasal 1.

Dipisah dari tahap0_struktur.py supaya GAGALNYA BISA SENDIRI-SENDIRI. Kalau
Pasal 1 bentuknya tidak terbaca, pohonnya tetap sehat dan seluruh pemeriksaan
lain tetap jalan — yang diam cuma F2-002 dan F2-003. Kalau disatukan,
kegagalan kecil di sini bisa disalahartikan sebagai kegagalan struktur dan
seluruh Fase 2 mati padahal tidak perlu.

Hasilnya dipakai tiga tempat:
  1. KONTEKS TETAP di Langkah 2 — seluruh definisi ikut di setiap panggilan
  2. F2-002 / F2-003 — istilah tak terdefinisi, definisi tak terpakai
  3. Langkah 5 pemeriksaan ④ — istilah berdefinisi di usulan wajib ditulis persis
"""

from __future__ import annotations

import re
from typing import Optional

from pydantic import BaseModel, Field

from app.models.satuan import JenisSatuan, PohonSatuan


class Definisi(BaseModel):
    """Satu istilah berikut artinya, dari Pasal 1."""

    istilah: str = Field(..., description="Istilahnya apa adanya, mis. 'Pengelola Barang'")
    arti: str = Field(default="", description="Bunyi definisinya sesudah kata 'adalah'")
    satuan_id: str = Field(
        ..., description="Alamat satuan asalnya, mis. 'pasal-1-angka-8'"
    )


class DaftarDefinisi(BaseModel):
    """Seluruh istilah berdefinisi sebuah dokumen."""

    definisi: list[Definisi] = Field(default_factory=list)
    gagal: Optional[str] = Field(
        default=None,
        description=(
            "Alasan ekstraksi menyerah. Selama terisi, F2-002 dan F2-003 DIAM — "
            "tetapi pemeriksaan lain tetap jalan."
        ),
    )

    def ada(self, istilah: str) -> bool:
        return any(d.istilah == istilah for d in self.definisi)

    def istilah_saja(self) -> list[str]:
        return [d.istilah for d in self.definisi]

    def cari_mirip(self, teks: str) -> list[str]:
        """Istilah yang muncul di `teks` tetapi ejaannya BERBEDA tipis.

        Inilah pemeriksaan ④ Langkah 5: menangkap salah ketik pada istilah
        berdefinisi di dalam usulan model — "Pengeloa Barang" untuk
        "Pengelola Barang". Istilah berdefinisi membawa arti hukum yang sudah
        ditetapkan, jadi salah ketiknya paling berakibat.

        Yang dicocokkan huruf pertama + panjang mirip, bukan kemiripan makna —
        murah, dan cukup untuk salah ketik satu-dua huruf.
        """
        mencurigakan: list[str] = []
        kata_teks = set(re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*", teks))
        # Istilah berdefinisi lain yang dieja BENAR tidak boleh dihitung
        # sebagai salah ketik istilah tetangganya.
        #
        # Naskah hukum penuh pasangan istilah yang cuma terpaut satu-dua huruf
        # dan dua-duanya sah: Penelaah/Penelaahan, Pengguna/Penggunaan,
        # Menteri/Kementerian. Tanpa penjagaan ini, usulan yang menulis
        # "Penelaah" dengan benar dituduh salah mengeja "Penelaahan", lalu
        # diturunkan jadi catatan kuning padahal tidak ada yang salah.
        # Terbukti pada contoh-rancangan-uji.docx, 22 Sep 2026.
        berdefinisi = set(self.istilah_saja())
        for istilah in berdefinisi:
            if istilah in teks:
                continue  # ditulis benar
            for kandidat in kata_teks:
                if kandidat in berdefinisi:
                    continue
                if _mirip_tapi_beda(istilah, kandidat):
                    mencurigakan.append(istilah)
                    break
        return mencurigakan


_BATAS_JARAK_UBAH = 2


def _jarak_ubah(a: str, b: str, batas: int = _BATAS_JARAK_UBAH) -> int:
    """Berapa penyuntingan huruf untuk mengubah `a` jadi `b` (Levenshtein).

    Berhenti begitu melewati `batas` — kita cuma peduli "terpaut satu-dua
    huruf", bukan angka pastinya.

    Perbandingan huruf-per-posisi TIDAK cukup di sini: satu huruf yang hilang
    menggeser seluruh sisanya, sehingga "Pengeloa Barang" vs "Pengelola
    Barang" terbaca berbeda di delapan posisi padahal cuma kurang satu huruf.
    """
    if abs(len(a) - len(b)) > batas:
        return batas + 1
    sebelum = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        kini = [i]
        for j, cb in enumerate(b, 1):
            kini.append(
                min(
                    sebelum[j] + 1,                 # hapus
                    kini[j - 1] + 1,                # sisip
                    sebelum[j - 1] + (ca != cb),    # ganti
                )
            )
        if min(kini) > batas:
            return batas + 1
        sebelum = kini
    return sebelum[-1]


def _mirip_tapi_beda(a: str, b: str) -> bool:
    """Dua teks berbeda tetapi cuma terpaut satu-dua penyuntingan huruf.

    Huruf pertama wajib sama — penyaring murah yang memangkas banyak
    kecocokan palsu antar-kata pendek, dengan risiko kecil: salah ketik tepat
    di huruf pertama jarang terjadi.
    """
    if a == b or a[:1].lower() != b[:1].lower():
        return False
    return 0 < _jarak_ubah(a, b) <= _BATAS_JARAK_UBAH


# ---------------------------------------------------------------------------
# Pola definisi
# ---------------------------------------------------------------------------
#
# Bentuk baku KMK 527: "X adalah Y." Kata "adalah" itu penanda yang dipakai
# hampir seluruh peraturan, dan sengaja TIDAK diperluas ke "yaitu"/"merupakan"
# sebelum ada bukti naskah nyata memakainya — memperluas pola tanpa bukti
# adalah cara paling cepat menghasilkan salah tandai.
_POLA_DEFINISI = re.compile(r"^(.{2,120}?)\s+adalah\s+(.+)$", re.IGNORECASE | re.DOTALL)

# Kalimat pengantar sebelum daftar definisi — bukan definisi itu sendiri.
_POLA_PENGANTAR = re.compile(
    r"^Dalam\s+(Peraturan|Keputusan)\s+Menteri\s+ini\s+yang\s+dimaksud\s+dengan",
    re.IGNORECASE,
)


def ambil_definisi(pohon: PohonSatuan) -> DaftarDefinisi:
    """Ambil daftar istilah dari Pasal 1.

    Memilih diam (gagal terisi) kalau Pasal 1 tidak ada atau tidak memuat satu
    pun definisi yang terbaca. F2-002 dan F2-003 ikut diam; sisanya jalan.
    """
    if pohon.gagal is not None:
        return DaftarDefinisi(gagal="Pohon satuan tidak sehat.")

    pasal_1 = pohon.cari("pasal-1")
    if pasal_1 is None:
        return DaftarDefinisi(
            gagal="Pasal 1 tidak ditemukan — daftar definisi tidak bisa disusun."
        )

    # Definisi biasanya jadi angka 1, 2, 3 di bawah Pasal 1. Kalau Pasal 1
    # tidak punya anak, teksnya sendiri yang diperiksa (bentuk satu kalimat).
    calon = [
        s
        for s in pohon.anak_dari("pasal-1")
        if s.jenis in (JenisSatuan.ANGKA, JenisSatuan.HURUF)
    ] or [pasal_1]

    hasil: list[Definisi] = []
    for s in calon:
        teks = s.teks.strip()
        if not teks or _POLA_PENGANTAR.match(teks):
            continue
        m = _POLA_DEFINISI.match(teks)
        if not m:
            continue
        istilah = m.group(1).strip().rstrip(",")
        arti = m.group(2).strip().rstrip(".").strip()

        # Batas kewajaran: istilah yang kepanjangan hampir pasti hasil
        # pembacaan yang meleset, bukan istilah sungguhan.
        if len(istilah.split()) > 8:
            continue

        hasil.append(Definisi(istilah=istilah, arti=arti, satuan_id=s.id))

    if not hasil:
        return DaftarDefinisi(
            gagal=(
                "Pasal 1 ada tetapi tidak satu pun definisi terbaca. Bentuknya "
                "mungkin tidak memakai kata \"adalah\" — F2-002 dan F2-003 diam."
            )
        )
    return DaftarDefinisi(definisi=hasil)
