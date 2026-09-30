"""Periksa satu usulan hijau dengan tangan — ALAT DIAGNOSA, bukan bagian alur.

Menjawab satu pertanyaan: kalau model mengusulkan teks ini sebagai pengganti,
apakah ia akan disisipkan hijau ke naskah, atau turun jadi kuning?

    python tools/cek_usulan.py \\
      --kalimat "(3) Dalam hal terdapat perbedaan pendapat, penyelesaiannya dilakukan melalui rapat pembahasan." \\
      --dicoret "penyelesaiannya dilakukan melalui rapat pembahasan" \\
      --usulan  "rapat pembahasan yang diselenggarakan oleh unit kerja"

Hijau menuntut DUA hal, dan alat ini memeriksa keduanya:

  1. usulannya MUAT di tempat yang dicoret — selalu diperiksa;
  2. usulannya punya SUMBER yang bisa ditunjuk — diperiksa kalau `--pasal`
     atau `--istilah` diberikan.

Pemeriksaan kedua menirukan jalur dalam (Pilihan B, 26 Sep 2026). Berikan teks
pasal yang memuat ketentuannya, dan istilah yang berdefinisi di Pasal 1:

    python tools/cek_usulan.py \\
      --kalimat "Permohonan dapat disampaikan secara elektronik." \\
      --dicoret "dapat disampaikan secara" \\
      --usulan  "wajib disampaikan secara" \\
      --pasal   "Permohonan dapat disampaikan secara elektronik." \\
      --istilah "Pengelola Barang" --istilah "Pengguna Barang"

Yang dicetak: bunyi naskah SESUDAH usulannya diterima, lalu keputusannya
berikut alasannya. Melihat kalimat jadinya jauh lebih meyakinkan daripada
membaca nama aturan yang berbunyi.

Memanggil `periksa_usulan` dan `sumber_internal` yang sama persis dengan
Langkah 5 — bukan menyusun ulang aturannya di sini. Alat pemeriksa yang
aturannya berbeda dari yang sebenarnya berjalan lebih berbahaya daripada tidak
ada alat.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.models.satuan import JenisSatuan, PohonSatuan, Satuan  # noqa: E402
from app.telaah.tahap1_parser.definisi import Definisi, DaftarDefinisi  # noqa: E402
from app.telaah.tahap5_verifikasi import periksa_usulan, sumber_internal  # noqa: E402

_GARIS = "=" * 70


def _naskah_sepotong(pasal: str, istilah: list[str]):
    """Pohon satu pasal berikut daftar istilahnya, cukup untuk `sumber_internal`.

    Sengaja dirakit di sini dan bukan di-parse dari .docx: yang sedang diuji
    keputusan atas SATU usulan, dan menuntut dokumen utuh membuat alat ini
    tidak terpakai saat menimbang contoh di kepala.
    """
    satuan = [
        Satuan(
            id="pasal-1",
            jenis=JenisSatuan.PASAL,
            nomor="1",
            teks=pasal,
            paragraf_mulai=0,
            paragraf_akhir=1,
        )
    ]
    definisi = [
        Definisi(istilah=t, arti="", satuan_id=f"pasal-1-angka-{i}")
        for i, t in enumerate(istilah, start=1)
    ]
    return PohonSatuan(satuan=satuan), DaftarDefinisi(definisi=definisi)


def laporkan(
    kalimat: str,
    dicoret: str,
    usulan: str,
    pasal: Optional[str] = None,
    istilah: Optional[list[str]] = None,
) -> int:
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

    # Pemeriksaan sumber. Dilewati — dan DIKATAKAN dilewati — kalau pemanggil
    # tidak memberi bahan naskahnya. Diam-diam melewatinya berarti alat ini
    # mengatakan HIJAU untuk usulan yang di alur sebenarnya turun jadi kuning.
    diperiksa_sumbernya = bool(pasal or istilah)
    sumber = ""
    if diperiksa_sumbernya:
        pohon, daftar = _naskah_sepotong(pasal or "", istilah or [])
        sumber = sumber_internal(usulan, dicoret, "pasal-1", pohon, daftar)

    print()
    print(_GARIS)
    print("PEMERIKSAAN 1 — usulannya MUAT di tempat yang dicoret?")
    print(_GARIS)
    print("  LOLOS" if not sebab else f"  TIDAK — {sebab}")

    print()
    print(_GARIS)
    print("PEMERIKSAAN 2 — usulannya punya SUMBER yang bisa ditunjuk?")
    print(_GARIS)
    if not diperiksa_sumbernya:
        print("  TIDAK DIPERIKSA — beri --pasal dan/atau --istilah untuk mengujinya.")
        print("  Di alur sebenarnya, aturan penalaran (F2-101..F2-105) yang tidak")
        print("  punya sumber SELALU turun jadi kuning, sekalipun lolos nomor 1.")
    elif sumber:
        print(f"  LOLOS — {sumber}")
    else:
        print("  TIDAK — rumusannya tidak bisa ditelusuri ke naskah ini. Salah satu:")
        print("    - ada kata di usulan yang belum ada di pasal ini maupun di")
        print("      daftar --istilah; atau")
        print("    - usulan MEMBUANG kata modal (wajib/harus/dapat/dilarang/")
        print("      tidak/bukan) yang ada di coretannya — itu mengubah akibat")
        print("      hukumnya, jadi menuntut peraturan pembanding.")
        print("  Satu kata saja sudah cukup membatalkan.")

    hijau = not sebab and (sumber or not diperiksa_sumbernya)

    print()
    print(_GARIS)
    if hijau:
        print("KEPUTUSAN: HIJAU — teks lama dicoret merah, usulan disisipkan")
        print(_GARIS)
        print("  Baca sekali lagi kalimat di atas. Kalau ia pincang, berarti")
        print("  ada bentuk kerusakan yang belum dijaga — itu temuan baru.")
        if not diperiksa_sumbernya:
            print()
            print("  CATATAN: sumbernya belum diuji. Lihat Pemeriksaan 2.")
        return 0

    print("KEPUTUSAN: KUNING — naskah TIDAK disentuh")
    print(_GARIS)
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
    ap.add_argument(
        "--pasal",
        default="",
        help="Teks pasal yang memuat ketentuannya, untuk menguji sumber usulan",
    )
    ap.add_argument(
        "--istilah",
        action="append",
        default=[],
        help="Istilah yang berdefinisi di Pasal 1. Boleh diulang.",
    )
    args = ap.parse_args()
    return laporkan(
        args.kalimat, args.dicoret, args.usulan, args.pasal, args.istilah
    )


if __name__ == "__main__":
    sys.exit(main())
