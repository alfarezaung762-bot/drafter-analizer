# Perbaiki bug

Hanya bug yang belum selesai. Yang sudah selesai cukup penjaganya, di tabel
paling bawah.

| # | Masalah | Kalau dibiarkan | Perlu diputuskan |
|---|---|---|---|
| 7 | Bahan AI kini naskah utuh, berkasnya sudah di `telaah/` — tinggal uji berbayar | Hasil nyata belum terbukti lebih baik dari cara lama | — |
| 8 | "Belum Ada Pemeriksaan" muncul sesudah analisis tanpa temuan | Penelaah menjalankan ulang, bayar dua kali | — |
| 9 | Peringatan penandaan Fase 2 dibuang | Komentar kosong di temuan Fase 2 tak terlapor | — |
| K4 | Usulan hijau yang cuma menyusun ulang kata | Hijau tidak lagi berarti "terbukti" | A / B |

**Ditunda:** K3 (ekspor versi bersih) — sesudah Fase 4.
**Menunggu uji:** bug 2–3 di Word; bug 1, 5, 6 lewat `--lanjut` PMK 45 dan 104;
bug 7 berbayar (di bawah); bug 11 dan tabel raksasa di Word.

## 7. Penyelarasan bahan yang diterima AI

**Diputuskan C + D, dikerjakan 29 Sep 2026: logika selesai (urutan kerja
1–5) dan berkasnya sudah dipindah ke `telaah/` (urutan kerja 6), 641 tes
lulus.** Tersisa uji berbayar.

Peta ringkasan per satuan dan penalaran di atasnya sudah dihapus. Tiap
panggilan AI kini membawa **naskah utuh** berikut lampirannya, disusun dari
seluruh paragraf. Tidak ada paragraf yang keluar dari bahan; tesnya
`test_tahap2_bahan.py`.

| Tahap | Berkas sekarang | Yang baru |
|---|---|---|
| 1 parser | `tahap1_parser/` — struktur, definisi, rujukan, lampiran | label terpisah sel (bug 11); lampiran dipilah jadi bingkai dan blok |
| 2 persiapan | `tahap2_persiapan/` — bahan, mekanis_konsistensi, dasar_hukum | bahan utuh, ukur token, kerangka tabel data; F2-003 ikut mencari di lampiran |
| 3 cari dugaan | `tahap3_cari_dugaan.py` | per kelompok pasal, lintas naskah, lampiran (**F2-106** baru); pasal terlewat ditanya ulang |
| 4 memastikan | `tahap4_memastikan/` — memastikan, alat, korpus_* | naskah utuh + alat: cari teks, buka tabel, jumlah kolom |
| 5 verifikasi | `tahap5_verifikasi.py` | klaim "X tidak ada" dicari kode; kutipan tahan beda spasi |

Ekspor Tahap 1–5 sudah ada di panel dan `cek_docx.py`.

**Ukuran nyata** (tiktoken, anggaran 100 rb — keempatnya dikirim utuh):

| Naskah | Bahan | Panggilan tahap 3 | Token masuk tahap 3 |
|---|---|---|---|
| PMK 104/2025 | 5,8 rb | 4 | ±26 rb |
| PMK 17/2026 | 11,5 rb | 7 | ±87 rb |
| PMK 45/2026 | 38,5 rb | 8 | ±316 rb |
| PMK 119/2025 | 53,1 rb | 15 | ±809 rb |

Tahap 4 menambah ±(bahan + 2,5 rb) token per dugaan. **Biayanya naik
berlipat** dibanding peta lama (PMK 45 dulu ±110 rb seluruhnya). Kenopnya di
`.env`: `FASE2_PASAL_PER_FOKUS` (bawaan 6; dinaikkan jadi 12 memangkas
panggilan tahap 3 hampir separuh), `FASE2_PANGGILAN_BERBARENGAN` (bawaan 4;
turunkan kalau Azure menolak karena kuota), `FASE2_ANGGARAN_TOKEN` (bawaan
100 rb).

**Uji berbayar yang perlu dijalankan:** `--lanjut --tahap5` pada PMK 17, 45,
104, 119. Ukurannya: temuan benar tidak berkurang dibanding cara lama, salah
tandai tidak bertambah. Ekspor Tahap 5 menunjukkan nasib tiap dugaan.

**Perlu diuji di Word:** letak tabel/baris/sel dari Office.js (bug 11 di
panel), dan mode tabel raksasa. PMK 108 tidak diuji di laptop ini — terlalu
berat.

**Kalau dibiarkan:** alur baru belum terbukti pada model sungguhan.

## 8. "Belum Ada Pemeriksaan" sesudah analisis tanpa temuan

Panel cuma melihat daftar kosong. Perbaikan: tampilkan "✓ Sudah diperiksa —
tidak ada temuan".

## 9. Peringatan penandaan Fase 2 dibuang

Komentar kosong dan Track Changes yang gagal dimatikan hanya dilaporkan untuk
Fase 1. Perbaikan: laporkan Fase 2 dengan cara yang sama.

## K4. Usulan hijau yang cuma menyusun ulang kata

Hijau syaratnya: kata yang ditambahkan sudah ada di naskah. Usulan tanpa kata
baru lolos otomatis (contoh: T12 PMK 45).
- **A (saran):** turun jadi kuning, rumusannya tetap di komentar.
- **B:** biarkan hijau, penelaah yang memutuskan.

## Sudah selesai — penjaganya

| # | Bug | Tes penjaga |
|---|---|---|
| 1 | "Huruf b tidak ada" — label hilang, angka salah induk, Langkah 4 tanpa pasal dirujuk | `test_tahap0_struktur.py`, `test_tahap0_rujukan.py`, `test_alur_fase2.py` |
| 2 | Kotak peringatan menutupi kartu | uji panel Chrome |
| 3 | Tolak tidak memulihkan teks | uji panel Chrome; menunggu uji Word |
| 4 | Komentar ganda | tertutup oleh 3 dan 5 |
| 5 | "RPKBUNP SPAN" di tiap baris | `test_tahap0_definisi.py`, `test_alur_fase2.py` (TestGabungKembar) |
| 6 | Butir 66 di mana-mana | `test_alur_fase2.py` (TestF2101WajibDuaTafsiran), `test_rujukan_kmk527.py` |
| 10 | Alat uji membaca sel gabungan dua kali dan melewatkan tabel bersarang — PMK 119 terbaca 127 pasal, 63 F2-004 palsu | `test_baca_docx.py` |
| 11 | Label nomor terpisah sel dari teksnya — definisi Pasal 1, Menimbang, dan Mengingat PMK 119 hilang dari pohon | `test_tahap0_struktur.py` (TestLabelTerpisahSel), `test_tahap2_bahan.py`; menunggu uji Word |
