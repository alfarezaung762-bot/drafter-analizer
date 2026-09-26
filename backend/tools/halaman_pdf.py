"""Render halaman PDF jadi PNG — ALAT DIAGNOSA, tidak dipakai backend.

Dibuat untuk satu pekerjaan: memverifikasi butir KMK 527 yang dikutip aturan
Drafter Analiser, dengan cara MEMBACA CITRA HALAMANNYA.

=========================================================================
KENAPA GAMBAR, BUKAN TEKS
=========================================================================

CLAUDE.md butir 4 melarang menurunkan aturan dari ekstraksi teks salinan KMK
527. Salinan di JDIH hasil pemindaian, dan OCR-nya rusak dengan pola yang
berulang: "clan" untuk "dan", "MENTER!" untuk "MENTERI", "iika" untuk "jika",
"Serita" untuk "Berita". Butir yang diturunkan dari teks begitu bisa salah
nomor atau salah bunyi, lalu tertulis di komentar naskah penelaah sebagai
dasar hukum.

Alat ini TIDAK mengekstrak teks. Ia menghasilkan gambar halaman supaya dibaca
mata — persis cara yang diminta butir 4.

    python tools/halaman_pdf.py "tools/contoh/527KMK.012022Kep 1.pdf" 45-47

Keluarannya ke folder sementara, bukan ke dalam repo: gambar halaman peraturan
tidak perlu ikut ke riwayat git.
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

# Perbesaran render. 2x cukup membuat teks hasil pemindaian terbaca tanpa
# membuat berkasnya terlalu besar untuk dibuka sekaligus.
_SKALA = 2.0


def baca_rentang(teks: str) -> list[int]:
    """'45-47' atau '45' atau '45,50-52' → daftar nomor halaman 1-berbasis."""
    nomor: list[int] = []
    for bagian in teks.split(","):
        bagian = bagian.strip()
        if not bagian:
            continue
        if "-" in bagian:
            awal, akhir = bagian.split("-", 1)
            nomor.extend(range(int(awal), int(akhir) + 1))
        else:
            nomor.append(int(bagian))
    return nomor


def render(berkas: Path, halaman: list[int], keluar: Path, skala: float) -> list[Path]:
    """Render halaman terpilih. Halaman di luar jangkauan DILEWATI, tidak diam.

    Nomor halaman yang salah lebih berbahaya daripada gagal: butir yang
    diverifikasi dari halaman yang keliru tetap terlihat terverifikasi.
    """
    import pymupdf  # noqa: PLC0415 — alat sekali jalan, impor ditahan di sini

    hasil: list[Path] = []
    with pymupdf.open(berkas) as dok:
        for n in halaman:
            if not (1 <= n <= dok.page_count):
                print(f"  halaman {n} di luar jangkauan (1-{dok.page_count})")
                continue
            gambar = dok[n - 1].get_pixmap(matrix=pymupdf.Matrix(skala, skala))
            tujuan = keluar / f"hal-{n:03d}.png"
            gambar.save(tujuan)
            hasil.append(tujuan)
            # Keluarannya ASCII saja: konsol Windows bawaan memakai cp1252 dan
            # melempar UnicodeEncodeError pada panah maupun tanda pisah panjang.
            print(f"  halaman {n:>3} -> {tujuan}")
    return hasil


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Render halaman PDF jadi PNG untuk dibaca visual."
    )
    ap.add_argument("berkas", help="Path ke .pdf")
    ap.add_argument("halaman", help="Nomor halaman: '45', '45-47', atau '45,50-52'")
    ap.add_argument(
        "--keluar",
        default="",
        help="Folder tujuan. Bawaan: folder sementara sistem.",
    )
    ap.add_argument("--skala", type=float, default=_SKALA)
    args = ap.parse_args()

    berkas = Path(args.berkas)
    if not berkas.exists():
        print(f"Berkas tidak ditemukan: {berkas}")
        return 1

    keluar = Path(args.keluar) if args.keluar else Path(tempfile.mkdtemp(prefix="kmk527-"))
    keluar.mkdir(parents=True, exist_ok=True)
    print(f"Folder keluaran: {keluar}")

    nomor = baca_rentang(args.halaman)
    if not nomor:
        print("Tidak ada nomor halaman yang terbaca.")
        return 1

    return 0 if render(berkas, nomor, keluar, args.skala) else 1


if __name__ == "__main__":
    sys.exit(main())
