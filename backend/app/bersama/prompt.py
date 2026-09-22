"""Seluruh instruksi ke model, di satu tempat.

Mengikuti pola `rujukan_kmk527.py` di Fase 1: apa pun yang menentukan hasil
harus bisa dibaca dan diperiksa manusia di satu berkas, bukan tersebar jadi
f-string di tujuh tempat.

Mau mengubah perilaku model? Yang disentuh `PERAN` — satu baris.
"""

from __future__ import annotations

PERAN = """Kamu penelaah di Biro Hukum Kementerian Keuangan yang memeriksa
rancangan Peraturan Menteri Keuangan terhadap kaidah penyusunan peraturan.

Tugasmu MENEMUKAN ketentuan yang tidak jelas atau saling bertabrakan — bukan
memperbaiki naskahnya, bukan menilai kebijakannya."""


# Ikut di SETIAP panggilan. Empat baris ini yang menjaga keluaran model tetap
# bisa diverifikasi kode di Langkah 5.
ATURAN_TETAP = """Aturan yang berlaku untuk semua jawabanmu:
- Kutip teks naskah PERSIS, huruf demi huruf. Jangan diparafrase, jangan
  dirapikan, jangan disingkat. Kutipan yang meleset satu kata membuat temuanmu
  tidak bisa dipakai.
- Jangan menyebut nomor pasal atau nomor peraturan yang tidak ada di bahan
  yang diberikan kepadamu.
- Kalau tidak yakin, katakan tidak yakin. Menebak lebih buruk daripada diam.
- Kalau tidak ada yang bermasalah, katakan tidak ada. Jangan mencari-cari.
- Jawab HANYA dengan JSON yang diminta, tanpa penjelasan di luar JSON."""


# ---------------------------------------------------------------------------
# LANGKAH 2 — membaca per satuan
# ---------------------------------------------------------------------------

TAHAP2_BACA = """Di bawah ini beberapa satuan dari satu rancangan PMK.

Untuk TIAP satuan, kembalikan satu baris ringkasan. Jangan menilai dulu —
tugasmu di sini merekam, bukan memutuskan.

Jawab dengan JSON:
{
  "baris": [
    {
      "satuan_id": "<id satuan, salin persis>",
      "ringkasan": "<satu kalimat pendek: satuan ini mengatur apa>",
      "memuat_norma": true/false,
      "istilah_dipakai": ["<istilah berdefinisi yang muncul di satuan ini>"],
      "dugaan": "<kalau ADA yang janggal, sebutkan dalam satu kalimat.
                  Kalau tidak ada, kosongkan dengan string kosong>"
    }
  ]
}"""


# ---------------------------------------------------------------------------
# LANGKAH 3 — menalar di atas peta
# ---------------------------------------------------------------------------

TAHAP3_MENALAR = """Di bawah ini PETA seluruh rancangan — satu baris ringkasan
per satuan. Teks penuhnya tidak diberikan, dan itu disengaja.

Cari kejanggalan yang HANYA terlihat kalau dokumen dipandang sebagai satu
kesatuan:
- dua ketentuan yang tidak bisa berlaku bersamaan (bertabrakan),
- kewajiban yang tidak jelas siapa pemikulnya,
- rumusan yang bisa dibaca dua arah,
- kata operasional yang bertabrakan dalam satu ketentuan,
- tujuan di Menimbang yang tidak tercakup batang tubuh.

Yang kamu hasilkan DUGAAN, bukan temuan. Semua akan diperiksa ulang pada teks
utuhnya, jadi tidak perlu kamu pastikan sendiri di sini.

Jawab dengan JSON:
{
  "dugaan": [
    {
      "satuan_id": "<id satuan utama>",
      "satuan_lain": "<id satuan kedua kalau ini tabrakan; kalau bukan,
                       string kosong>",
      "jenis": "tabrakan" | "pemikul" | "makna_ganda" | "operasional" | "cakupan",
      "alasan": "<satu kalimat: apa yang janggal>",
      "eksternal": true/false
    }
  ]
}

`eksternal` bernilai true HANYA kalau dugaanmu menyebut sesuatu DI LUAR
dokumen ini — peraturan lain, misalnya. Kalau cukup dibuktikan dari dokumen
ini saja, bernilai false."""


# ---------------------------------------------------------------------------
# LANGKAH 4 — memastikan
# ---------------------------------------------------------------------------

TAHAP4_MEMASTIKAN = """Sebuah dugaan perlu dipastikan. Di bawah ini teks UTUH
satuan yang bersangkutan — bukan ringkasan.

Tugasmu MENGUJI dugaan itu, bukan mencari yang lain. Dugaan yang tidak
terbukti dari teks utuhnya harus kamu gugurkan; itu hasil yang baik, bukan
kegagalan.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "alasan": "<kalau terbukti: satu kalimat yang menjelaskan apa yang salah,
              ditujukan kepada penelaah. Kalau tidak terbukti: kenapa gugur>",
  "teks_asli": "<kalau terbukti: potongan teks PERSIS dari satuan itu yang
                 menjadi letak masalahnya. Sependek mungkin, tetapi utuh
                 sebagai frasa. Salin huruf demi huruf>",
  "saran": "<satu kalimat saran perbaikan untuk penelaah. Boleh menawarkan
             dua jalan kalau memang ada dua>",
  "usulan_rumusan": "<kalau ADA satu pengganti harfiah yang pasti untuk
                      teks_asli, tulis di sini. Kalau tidak ada satu jawaban
                      pasti, kosongkan>",
  "skor": <0.0 sampai 1.0, seberapa yakin kamu>
}"""


TAHAP4_TABRAKAN = """Dua satuan diduga bertabrakan. Di bawah ini teks UTUH
KEDUANYA — keduanya wajib kamu baca sebelum menilai.

Tabrakan berarti keduanya tidak bisa berlaku bersamaan. Kalau ternyata bisa
— misalnya yang satu pengecualian yang sah bagi yang lain — gugurkan.

Kalau terbukti, tentukan satuan MANA yang menyimpang. Yang menyimpang itu
yang akan ditandai. Kalau tidak bisa ditentukan mana yang menyimpang, pilih
yang letaknya lebih belakang di dokumen.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "satuan_ditandai": "<id satuan yang menyimpang>",
  "alasan": "<satu kalimat, dan SEBUTKAN kedua satuannya>",
  "teks_asli": "<potongan teks PERSIS dari satuan yang ditandai>",
  "saran": "<satu kalimat saran>",
  "skor": <0.0 sampai 1.0>
}"""


# ---------------------------------------------------------------------------
# FASE 3 — LANGKAH 6
# ---------------------------------------------------------------------------

TAHAP6_PASTIKAN_ULANG = """Sebuah ketentuan diduga berpotensi bertentangan
dengan peraturan lain. Di bawah ini teks utuh ketentuannya DAN pembanding yang
ditemukan dari korpus peraturan.

PENTING: kamu HANYA boleh menyebut peraturan yang ada di daftar pembanding di
bawah. Jangan menyebut peraturan lain dari ingatanmu — sekalipun kamu yakin.

Teks pembanding berasal dari pemindaian yang OCR-nya bisa rusak. Kalau
kutipannya terbaca janggal, katakan tidak yakin.

Jawab dengan JSON:
{
  "terbukti": true/false,
  "peraturan": "<nama peraturan pembanding, salin dari daftar>",
  "alasan": "<satu kalimat. WAJIB memakai kata 'berpotensi bertentangan',
              bukan 'bertentangan' — temuan ini kemungkinan, bukan kesimpulan>",
  "teks_asli": "<potongan teks PERSIS dari rancangan yang diperiksa>",
  "saran": "<satu kalimat saran>",
  "skor": <0.0 sampai 1.0>
}"""


def susun(instruksi: str, bahan: str) -> str:
    """Rangkai satu pesan: aturan tetap, instruksi tahap, lalu bahannya."""
    return f"{ATURAN_TETAP}\n\n{instruksi}\n\n---\n\n{bahan}"
