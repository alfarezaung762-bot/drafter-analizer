"""Periksa satu usulan hijau dengan tangan — ALAT DIAGNOSA, bukan bagian alur.

Menjawab satu pertanyaan: kalau model mengusulkan teks ini sebagai pengganti,
apakah ia akan disisipkan hijau ke naskah, atau turun jadi kuning?

    python tools/cek_usulan.py \\
      --kalimat "(3) Dalam hal terdapat perbedaan pendapat, penyelesaiannya dilakukan melalui rapat pembahasan." \\
      --dicoret "penyelesaiannya dilakukan melalui rapat pembahasan" \\
      --usulan  "rapat pembahasan yang diselenggarakan oleh unit kerja"

Yang dicetak: bunyi naskah SESUDAH usulannya diterima, lalu keputusannya
berikut alasannya. Melihat kalimat jadinya jauh lebih meyakinkan daripada
membaca nama aturan yang berbunyi.

Memanggil `periksa_usulan` yang sama persis dengan Langkah 5 — bukan menyusun
ulang aturannya di sini. Alat pemeriksa yang aturannya berbeda dari yang
sebenarnya berjalan lebih berbahaya daripada tidak ada alat.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.fase2.tahap5_verifikasi import periksa_usulan  # noqa: E402

_GARIS = "=" * 70


def laporkan(kalimat: str, dicoret: str, usulan: str) -> int:
    if dicoret not in kalimat:
        print("GAGAL: teks --dicoret tidak ditemukan di dalam --kalimat.")
        print("       Salin huruf demi huruf, termasuk tanda bacanya.")
        return 1

    potong = kalimat.index(dicoret)
    sebelum = kalimat[:potong]
    sesudah = kalimat[potong + len(dicoret) :]

    print(_GARIS)
    print("NASKAH ASLI")
    print(_GARIS)
    print(f"  {kalimat}")
    print()
    print(f"  yang dicoret: {dicoret!r}")
    print(f"  usulannya   : {usulan!r}")

    print()
    print(_GARIS)
    print("KALAU USULANNYA DISISIPKAN, NASKAH JADI")
    print(_GARIS)
    print(f"  {sebelum}{usulan}{sesudah}")

    sebab = periksa_usulan(usulan, dicoret, sebelum)

    print()
    print(_GARIS)
    if not sebab:
        print("KEPUTUSAN: HIJAU — teks lama dicoret merah, usulan disisipkan")
        print(_GARIS)
        print("  Baca sekali lagi kalimat di atas. Kalau ia pincang, berarti")
        print("  ada bentuk kerusakan yang belum dijaga — itu temuan baru.")
        return 0

    print("KEPUTUSAN: KUNING — naskah TIDAK disentuh")
    print(_GARIS)
    print(f"  Sebabnya: {sebab}")
    print()
    print("  Usulannya tidak hilang. Ia tetap ditulis di komentar sebagai")
    print("  contoh rumusan, dan penelaah bisa menyalinnya sendiri.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Periksa apakah sebuah usulan akan disisipkan hijau atau turun jadi kuning."
    )
    ap.add_argument("--kalimat", required=True, help="Ayat atau kalimat utuh dari naskah")
    ap.add_argument("--dicoret", required=True, help="Potongan yang akan dicoret merah")
    ap.add_argument("--usulan", required=True, help="Teks pengganti yang diusulkan")
    args = ap.parse_args()
    return laporkan(args.kalimat, args.dicoret, args.usulan)


if __name__ == "__main__":
    sys.exit(main())
