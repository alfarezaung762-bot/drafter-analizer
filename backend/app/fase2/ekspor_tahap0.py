"""Ekspor Tahap 0 — ALAT PENGEMBANG, bukan fitur penelaah.

Menghasilkan teks mentah berisi apa yang BENAR-BENAR akan dibaca model.
Gunanya satu: memperbaiki bug. Alat ini masih dalam pengembangan, dan tanpa
ekspor begini tidak ada cara memeriksa apakah ada yang terpotong di tengah
jalan antara Word dan prompt.

=========================================================================
YANG PALING PENTING DI SINI: KEPUTUSAN LANGKAH 1
=========================================================================

Penyaring Langkah 1 membuang satuan yang dianggapnya tidak memuat norma. Ia
sengaja berpihak pada meloloskan ("ragu → diloloskan"), tetapi belum pernah
ada yang memeriksanya terhadap naskah nyata — dan satuan yang dibuang tidak
pernah sampai ke model, tidak pernah jadi temuan, dan tidak meninggalkan jejak
di panel.

Karena itu bagian DIBUANG ditaruh PALING ATAS, berikut TEKS UTUH tiap satuan
yang dibuang. Tanpa teksnya tidak ada cara menilai apakah pembuangannya benar;
dengan teksnya, satu orang bisa membacanya dari atas dan menjawab satu
pertanyaan per baris: apakah penelaah memang tidak perlu membaca ini?

=========================================================================
WAJIB MEMANGGIL KODE YANG SAMA
=========================================================================

`susun_konteks_tetap`, `susun_bahan`, `kelompokkan`, dan `saring` dipanggil
apa adanya, bukan disusun ulang di sini. Ekspor yang menyusun ulang bisa
menyimpang dari yang sebenarnya dikirim — dan ekspor yang berbohong lebih
berbahaya daripada tidak ada ekspor, karena ia dipakai memutuskan bahwa
sesuatu bukan masalah.

Tidak memanggil model. Tidak berbiaya.
"""

from __future__ import annotations

from typing import Optional

from app.fase2 import tahap2_baca
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import HasilSaring, saring
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import ParagrafInput, Temuan

_GARIS = "=" * 78


def _judul(teks: str) -> list[str]:
    return ["", _GARIS, teks, _GARIS]


def identitas_naskah(
    paragraf: list[ParagrafInput],
    pohon: PohonSatuan,
    dokumen: str,
    per_panggilan: int,
    disaring: HasilSaring,
) -> list[str]:
    """Kepala yang sama untuk Ekspor Tahap 0 dan Tahap 3.

    Ada supaya ekspor dari berkas yang keliru ketahuan di tiga baris pertama.
    Sudah pernah terjadi: sebuah ekspor dibaca sebagai milik naskah 97 Pasal
    padahal judulnya milik naskah 9 Pasal, dan selisihnya dikira bug parser.
    Nama berkas saja tidak cukup — yang meyakinkan judul naskahnya sendiri,
    karena itulah yang juga terbaca di layar Word.
    """
    judul = pohon.semua(JenisSatuan.JUDUL)
    pasal = pohon.semua(JenisSatuan.PASAL)
    kelompok = tahap2_baca.kelompokkan(disaring.dibaca, per_panggilan)
    return [
        f"Berkas   : {dokumen or '(tanpa nama)'}",
        f"Judul    : {judul[0].teks if judul else '(tidak terbaca)'}",
        f"Pasal    : {len(pasal)}",
        f"Satuan   : {len(pohon.satuan)} total, {len(disaring.dibaca)} dibaca, "
        f"{len(disaring.dilewati)} dibuang penyaring",
        f"Paragraf : {len(paragraf)}, {sum(1 for p in paragraf if p.penanda)} "
        "berpenanda nomor otomatis Word",
        f"Panggilan Langkah 2: {len(kelompok)}",
    ]


def susun_ekspor(
    paragraf: list[ParagrafInput],
    per_panggilan: int = 6,
    temuan_fase1: Optional[list[Temuan]] = None,
    dokumen: str = "",
) -> str:
    """Rangkai seluruh isi ekspor jadi satu teks. Fungsi murni."""
    pohon = bangun_pohon(paragraf)
    daftar = ambil_definisi(pohon)
    disaring = saring(pohon)

    # Identitas naskah ditaruh paling atas supaya ekspor dari berkas yang
    # keliru ketahuan di tiga baris pertama. Sudah pernah terjadi: sebuah
    # ekspor dibaca sebagai milik PMK 18 padahal judulnya jelas milik naskah
    # lain, dan bagian yang ganjil dikira bug parser.
    baris: list[str] = [
        _GARIS,
        "EKSPOR TAHAP 0 — apa yang akan dibaca model",
        _GARIS,
    ] + identitas_naskah(paragraf, pohon, dokumen, per_panggilan, disaring)

    if pohon.gagal:
        baris += _judul("FASE 2 TIDAK DIJALANKAN")
        baris.append(f"  {pohon.gagal}")

    # --- Yang dibuang penyaring: PALING ATAS, dengan teks utuhnya ---------
    baris += _judul(
        f"LANGKAH 1 — YANG DIBUANG ({len(disaring.dilewati)}). PERIKSA INI DULU."
    )
    baris.append(
        "  Satuan di bawah TIDAK pernah dikirim ke model. Baca teksnya, lalu"
    )
    baris.append(
        "  tanyakan satu hal: apakah penelaah memang tidak perlu membaca ini?"
    )
    if not disaring.dilewati:
        baris.append("\n  (tidak ada yang dibuang)")
    for s, alasan in disaring.dilewati:
        isi = pohon.teks_lengkap(s.id) or s.teks
        baris.append("")
        baris.append(f"  {s.id}   alasan: {alasan}")
        baris.append(f"      {isi!r}")

    # --- Yang dibaca ------------------------------------------------------
    baris += _judul(f"LANGKAH 1 — YANG DIBACA ({len(disaring.dibaca)} satuan)")
    for s in disaring.dibaca:
        baris.append(f"  {s.id}")

    # --- Paragraf apa adanya ---------------------------------------------
    baris += _judul("PARAGRAF APA ADANYA (index | penanda | teks)")
    baris.append(
        "  `penanda` nomor otomatis Word. TIDAK ditempel ke teks: offset"
    )
    baris.append("  penandaan dihitung terhadap `teks`, dan Word tidak punya")
    baris.append("  awalan itu di teksnya.")
    baris.append("")
    for p in paragraf:
        baris.append(f"  {p.index:>5} | {p.penanda!r:<14} | {p.teks!r}")

    # --- Pohon satuan -----------------------------------------------------
    baris += _judul(f"POHON SATUAN ({len(pohon.satuan)} satuan)")
    for s in pohon.satuan:
        dalam = 0 if s.induk is None else 1 + s.id.count("-") // 2
        baris.append(
            f"  {'  ' * dalam}{s.id:<34} [{s.jenis.value:<10}] "
            f"p{s.paragraf_mulai}-{s.paragraf_akhir}  {s.teks[:60]!r}"
        )

    # --- Definisi ---------------------------------------------------------
    baris += _judul("DAFTAR DEFINISI (Pasal 1)")
    if daftar.gagal:
        baris.append(f"  TIDAK TERBACA: {daftar.gagal}")
    else:
        for d in daftar.definisi:
            baris.append(f"  {d.istilah}  [{d.satuan_id}]")
            baris.append(f"      = {d.arti}")

    # --- Konteks tetap ----------------------------------------------------
    konteks = tahap2_baca.susun_konteks_tetap(pohon, daftar)
    baris += _judul("KONTEKS TETAP — ikut di SETIAP panggilan Langkah 2")
    baris.append(konteks)

    # --- Muatan tiap kelompok --------------------------------------------
    kelompok = tahap2_baca.kelompokkan(disaring.dibaca, per_panggilan)
    baris += _judul(
        f"MUATAN LANGKAH 2 — {len(kelompok)} panggilan, "
        f"{per_panggilan} satuan per panggilan"
    )
    baris.append("  Ini PERSIS yang dikirim ke model, konteks tetap ikut di dalamnya.")
    baris.append("")
    baris.append("  CARA MEMBACANYA. Bagian KONTEKS DOKUMEN — judul, Menimbang,")
    baris.append("  Mengingat, daftar definisi, kerangka pasal — DIULANG UTUH di")
    baris.append("  setiap panggilan. Yang berganti dari satu panggilan ke panggilan")
    baris.append("  berikutnya cuma daftar di bawah '== SATUAN YANG DIPERIKSA ==',")
    baris.append("  yaitu satuan yang harus dibaca dan diringkas pada panggilan itu.")
    baris.append("  Jadi jumlah panggilan jauh lebih kecil daripada jumlah satuan.")
    for ke, kel in enumerate(kelompok, start=1):
        bahan = tahap2_baca.susun_bahan(kel, pohon, konteks, temuan_fase1)
        baris.append("")
        baris.append(f"  --- panggilan {ke}/{len(kelompok)} "
                     f"({len(kel)} satuan, {len(bahan)} huruf) ---")
        baris.append(bahan)

    baris.append("")
    return "\n".join(baris)
