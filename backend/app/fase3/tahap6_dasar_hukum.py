"""F3-002 — dasar hukum di Mengingat yang sudah dicabut.

Bagian dari Langkah 6 karena ia menanyai korpus, tetapi **TIDAK MEMANGGIL
MODEL SAMA SEKALI**. Yang dikerjakan cuma: baca butir Mengingat, cari
peraturannya di korpus menurut bentuk + nomor + tahun, lihat statusnya.
Gratis, dan kalau salah bisa ditunjukkan barisnya.

Itu juga yang membuatnya berbeda watak dari F3-001. F3-001 menilai
*kemungkinan* pertentangan dan bahasanya "berpotensi"; F3-002 melaporkan
*fakta* dari korpus: peraturan ini berstatus Tidak Berlaku.

=========================================================================
KENAPA ATURAN INI PALING RAWAN, DAN APA PENJAGANYA
=========================================================================

Mengatakan dasar hukum penelaah sudah dicabut padahal masih berlaku adalah
salah tandai yang paling mahal di seluruh alat ini: penelaah akan mengubah
bagian Mengingat yang sebenarnya sudah benar, dan kesalahannya baru ketahuan
setelah naskahnya beredar.

Empat keadaan yang membuat aturan ini MEMILIH DIAM:

  1. Bentuk peraturannya tidak dikenali — Ketetapan MPR, Peraturan Daerah,
     peraturan lembaga lain. Dilewati, tidak ditebak.
  2. Tidak ketemu di korpus. Korpus tidak memuat segalanya; tidak ketemu
     BUKAN bukti sudah dicabut.
  3. Dua dokumen bernomor sama berstatus berbeda. Kita tidak tahu yang mana.
  4. Statusnya terbaca sebagai sesuatu di luar Berlaku/Tidak Berlaku —
     misalnya "Tetap", yang ada 211 dokumen di korpus dan artinya belum
     jelas.

Yang dilaporkan HANYA keadaan kelima: ketemu, tunggal, dan berstatus Tidak
Berlaku.
"""

from __future__ import annotations

from typing import Optional

from app.bersama.opensearch import PencariPeraturan, baca_kutipan
from app.fase2.mekanis_konsistensi import buat_temuan
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import ParagrafInput, Temuan

# Batas kewajaran. Naskah dengan Mengingat sepanjang ini hampir pasti salah
# baca parsernya, dan menanyai korpus puluhan kali untuk naskah yang salah
# baca cuma membuang waktu.
_BATAS_BUTIR = 40


def cek_dasar_hukum(
    pohon: PohonSatuan,
    paragraf: list[ParagrafInput],
    pencari: Optional[PencariPeraturan],
) -> tuple[list[Temuan], list[str]]:
    """Periksa tiap butir Mengingat. Kembalikan temuan dan yang dilewati.

    Yang dilewati ikut dikembalikan supaya terlihat saat diagnosa: aturan
    yang diam pada SELURUH butir tidak bisa dibedakan dari aturan yang rusak,
    kecuali alasannya disebut.
    """
    if pencari is None:
        return [], ["F3-002 tidak dijalankan: pencari peraturan tidak tersedia"]

    butir = pohon.semua(JenisSatuan.MENGINGAT)
    if not butir:
        return [], ["F3-002 diam: tidak ada butir Mengingat yang terbaca"]
    if len(butir) > _BATAS_BUTIR:
        return [], [
            f"F3-002 diam: {len(butir)} butir Mengingat melebihi batas kewajaran "
            f"{_BATAS_BUTIR} — strukturnya patut dicurigai salah baca"
        ]

    temuan: list[Temuan] = []
    dilewati: list[str] = []

    for s in butir:
        kutipan = baca_kutipan(s.teks)
        if kutipan is None:
            dilewati.append(f"{s.id}: bentuk peraturannya tidak dikenali")
            continue

        status = pencari.status_peraturan(kutipan)
        if status.berlaku is None:
            dilewati.append(f"{s.id} ({kutipan}): {status.alasan}")
            continue
        if status.berlaku:
            continue

        # Yang ditandai: sebutan peraturannya saja, bukan seluruh butir.
        # Butir Mengingat panjang karena memuat Lembaran Negara; menyorot
        # semuanya membuat penelaah mencari sendiri bagian yang dimaksud.
        petunjuk = _petunjuk(s.teks)
        t = buat_temuan(
            aturan_id="F3-002",
            satuan=s,
            paragraf=paragraf,
            teks_asli=petunjuk,
            catatan=(
                f"{status.nomor or kutipan} berstatus Tidak Berlaku menurut korpus "
                f"peraturan JDIH — {status.judul}."
            ),
            saran=(
                "Periksa apakah peraturan ini memang sudah dicabut, dan kalau ya, "
                "ganti dasar hukumnya dengan peraturan penggantinya. Status di "
                "korpus dapat tertinggal dari keadaan sebenarnya, jadi pastikan "
                "sendiri sebelum mengubah."
            ),
        )
        if t is not None:
            temuan.append(t)
        else:
            dilewati.append(f"{s.id} ({kutipan}): rentang penandaannya tidak ketemu")

    return temuan, dilewati


def _petunjuk(teks: str) -> str:
    """Bagian butir yang ditandai — sebutan peraturannya, sebelum "tentang".

    Kalau tidak ada kata "tentang", dipakai 80 huruf pertama. Rentang yang
    lebih panjang dari itu menyorot Lembaran Negara yang tidak ada urusannya.
    """
    bersih = teks.strip()
    potong = bersih.lower().find(" tentang ")
    if potong > 0:
        return bersih[:potong]
    return bersih[:80]
