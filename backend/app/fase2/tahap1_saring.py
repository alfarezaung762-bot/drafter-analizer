"""TAHAP 1 — memilah satuan mana yang layak dibayar untuk dibaca model.

Kode biasa, gratis, selesai dalam milidetik. Bertanya ke model "perlu dibaca
atau tidak?" SUDAH merupakan membaca — teksnya tetap terkirim, biayanya tetap
keluar. Penyaring cuma ada gunanya kalau gratis.

CAKUPANNYA HANYA BATANG TUBUH. Judul, Menimbang, Mengingat, dan definisi
Pasal 1 tidak disaring di sini — mereka masuk KONTEKS TETAP, ikut terkirim di
setiap panggilan Langkah 2.

KEMIRINGANNYA DISENGAJA: kalau ragu, DILOLOSKAN.

  satuan tanpa norma ikut terkirim  →  rugi beberapa rupiah, kelihatan dari biaya
  satuan bernorma ikut tersaring    →  pasal itu TIDAK PERNAH DIPERIKSA, dan
                                       tidak ada apa pun di layar yang
                                       memberi tahu

Baris kedua itu kegagalan terburuk yang mungkin dialami alat ini: penelaah
mengira Pasal 14 sudah diperiksa padahal tidak pernah tersentuh.
"""

from __future__ import annotations

import re

from app.models.satuan import JenisSatuan, PohonSatuan, Satuan

# ---------------------------------------------------------------------------
# Penanda norma
# ---------------------------------------------------------------------------

# Kata operasional — menandai ada yang diwajibkan, dilarang, atau diberi hak.
_KATA_OPERASIONAL = re.compile(
    r"\b(wajib|harus|dilarang|dapat|berhak|bertanggung\s+jawab"
    r"|ditetapkan|menetapkan|dikenakan|diberikan|mengajukan|menyampaikan"
    r"|melakukan|melaksanakan|menyelesaikan|melaporkan|mengeluarkan)\b",
    re.IGNORECASE,
)

# Batas waktu atau ukuran.
_BATAS_UKURAN = re.compile(
    r"\b(paling\s+(lambat|cepat|sedikit|banyak|lama|singkat|tinggi|rendah)"
    r"|sebesar|sebanyak|selama)\b|\(\s*\w+\s*\)\s*(hari|bulan|tahun|kali)",
    re.IGNORECASE,
)

# Syarat — ketentuan yang berlaku dalam keadaan tertentu.
_SYARAT = re.compile(r"\b(dalam\s+hal|apabila|jika|sepanjang|kecuali)\b", re.IGNORECASE)

# ---------------------------------------------------------------------------
# Penanda BUKAN norma — hanya yang benar-benar pasti
# ---------------------------------------------------------------------------
#
# Daftar ini sengaja PENDEK. Tiap pola yang ditambahkan di sini menyaring
# satuan KELUAR, dan kesalahan ke arah itu tidak kelihatan. Hanya bentuk yang
# betul-betul baku dan tidak pernah memuat norma yang boleh masuk.

_KETENTUAN_PENUTUP = re.compile(
    r"^(Peraturan|Keputusan)\s+Menteri\s+ini\s+mulai\s+berlaku\b", re.IGNORECASE
)
_PERINTAH_PENGUNDANGAN = re.compile(r"^Agar\s+setiap\s+orang\s+mengetahuinya", re.IGNORECASE)
_RUANG_LINGKUP = re.compile(
    r"^(Peraturan|Keputusan)\s+Menteri\s+ini\s+mengatur\s+mengenai\b", re.IGNORECASE
)

# Jenis satuan yang tidak pernah jadi sasaran pemeriksaan penalaran.
_JENIS_DILEWATI = {
    JenisSatuan.JUDUL,
    JenisSatuan.MENIMBANG,
    JenisSatuan.MENGINGAT,
    JenisSatuan.MENETAPKAN,
    JenisSatuan.BAB,
    JenisSatuan.BAGIAN,
    JenisSatuan.PARAGRAF,
    JenisSatuan.PENUTUP,
    JenisSatuan.LAMPIRAN,
}


class HasilSaring:
    """Apa yang dibaca model, apa yang dilewati, dan alasannya.

    Alasan ikut disimpan supaya bisa ditelusuri saat ada temuan yang
    seharusnya keluar tetapi tidak — tanpa ini, penyaring jadi kotak hitam.
    """

    def __init__(self) -> None:
        self.dibaca: list[Satuan] = []
        self.dilewati: list[tuple[Satuan, str]] = []

    @property
    def jumlah(self) -> tuple[int, int]:
        return len(self.dibaca), len(self.dilewati)


def memuat_norma(teks: str) -> bool:
    """Apakah satuan ini mengikat seseorang berbuat atau tidak berbuat."""
    return bool(
        _KATA_OPERASIONAL.search(teks)
        or _BATAS_UKURAN.search(teks)
        or _SYARAT.search(teks)
    )


def saring(pohon: PohonSatuan) -> HasilSaring:
    """Pisahkan satuan batang tubuh yang layak dibaca model."""
    hasil = HasilSaring()
    if pohon.gagal is not None:
        return hasil

    for s in pohon.satuan:
        if s.jenis in _JENIS_DILEWATI:
            hasil.dilewati.append((s, "bukan batang tubuh — masuk konteks tetap"))
            continue

        teks = s.teks.strip()

        # Pasal yang seluruh isinya ayat tidak punya teks sendiri. Yang
        # diperiksa ayat-ayatnya, bukan pasalnya.
        if not teks:
            hasil.dilewati.append((s, "tidak punya teks sendiri; isinya di anaknya"))
            continue

        # Definisi di Pasal 1 sudah masuk konteks tetap lewat tahap0_definisi.
        if s.id.startswith("pasal-1-"):
            hasil.dilewati.append((s, "definisi Pasal 1 — sudah di konteks tetap"))
            continue

        if _KETENTUAN_PENUTUP.match(teks):
            hasil.dilewati.append((s, "ketentuan penutup — tidak mengikat siapa pun"))
            continue
        if _PERINTAH_PENGUNDANGAN.match(teks):
            hasil.dilewati.append((s, "perintah pengundangan"))
            continue
        if _RUANG_LINGKUP.match(teks) and not memuat_norma(teks):
            hasil.dilewati.append((s, "ruang lingkup — tidak ada yang diwajibkan"))
            continue

        # Sampai di sini: dibaca. Termasuk yang meragukan — itu kemiringan
        # yang disengaja, dan alasannya di docstring modul ini.
        hasil.dibaca.append(s)

    return hasil
