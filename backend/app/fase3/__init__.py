"""Fase 3 — pertentangan dengan peraturan lain.

  tahap6_cari            teks ketentuan → embedding → korpus → saring status
  tahap6_pastikan_ulang  memastikan dengan pembanding di tangan

DI BALIK GERBANG. Kodenya sudah ada dan bisa dijalankan, tetapi MATI SECARA
BAWAAN di panel Pengaturan: penelaah harus menyalakannya sendiri. Alasannya
satu, dan belum berubah — cakupan isi index OpenSearch belum diverifikasi
langsung (brief 8.12), jadi "tidak ada pembanding ditemukan" belum bisa
dibedakan dari "korpusnya memang tidak memuatnya".

Dipanggil HANYA untuk dugaan yang ditandai eksternal, dan hasilnya tetap
kembali ke Langkah 5 di fase2/tahap5_verifikasi.py seperti jalur lain.
"""
