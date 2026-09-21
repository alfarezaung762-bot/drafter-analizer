# Dokumentasi Drafter Analiser

Enam berkas di sini, plus `CLAUDE.md` di akar. Kalau ada yang bertentangan,
**`fase1 drafter.md` yang berlaku** — dokumen itu disamakan dengan kode setiap
kali kode berubah.

| Berkas | Isinya | Baca kapan |
|---|---|---|
| [`project-brief.md`](project-brief.md) | **Kenapa** alat ini dibangun, untuk siapa, dan cara penelaah bekerja sebenarnya. Bukan spesifikasi | Sekali, untuk memahami konteksnya |
| [`fase1 drafter.md`](fase1%20drafter.md) | Seluruh rancangan Fase 1: apa yang dibangun, cara temuan ditampilkan, kontrak data, aturan untuk agen coding, definisi selesai | Sebelum mengubah apa pun |
| [`cek list fase 1.md`](cek%20list%20fase%201.md) | **Apa yang benar-benar diperiksa, disusun per bagian naskah** (Judul, Menimbang, Mengingat, Menetapkan, batang tubuh, Lampiran) — untuk PMK dan KMK. Memuat juga yang TIDAK diperiksa dan kapan aturan memilih diam | Sambil membuka rancangan, untuk tahu mana yang masih harus diperiksa sendiri |
| [`fase-2dan-3drafter.md`](fase-2dan-3drafter.md) | **Alur, batasan, dan teknologi** Fase 2 & 3: bagaimana model membaca PMK pasal per pasal tanpa ada yang terlewat, apa yang membatasi rancangannya, dan apa saja yang dibutuhkan. **Rancangan, belum dibangun** | Sebelum mulai mengerjakan Fase 2 |
| [`panduan-officejs.md`](panduan-officejs.md) | API Word yang sudah diverifikasi ke `index.d.ts`, dan jebakan yang sudah terbukti | Sebelum memakai API Word yang belum pernah dipakai |
| [`panduan-vibe.md`](panduan-vibe.md) | Ringkasan konvensi kode. **Isinya sudah ada seluruhnya di `CLAUDE.md`** — kandidat dihapus, lihat catatan di bawah | Tidak perlu |
| [`../CLAUDE.md`](../CLAUDE.md) | Aturan kerja repo yang tidak boleh dilanggar | Otomatis dibaca Claude Code |

## Urutan baca

0. `project-brief.md` bagian 6 (prinsip) dan 8.13 (cara penelaah bekerja) —
   dua bagian itu yang menjelaskan kenapa alat ini menandai, bukan memperbaiki.
1. `fase1 drafter.md` bagian 1–4 — apa yang dibangun dan apa yang **tidak**.
2. Bagian 6 — cara temuan ditampilkan di dokumen. Bagian terpanjang dan
   terpenting; memuat riwayat tiga rancangan yang gugur beserta buktinya.
3. `cek list fase 1.md` — apa yang diperiksa tiap bagian naskah. Paling cepat
   untuk tahu cakupan Fase 1 tanpa membaca kode.
4. **Bagian 7 dan 8 — susunan berkas beranotasi dan alur lengkapnya**, dari
   tombol Analisis ditekan sampai tanda muncul di naskah. Bagian 8 juga
   menjelaskan **bagaimana** kesalahan ditemukan: jangkar yang dicari lebih
   dulu, sebelas aturan yang berjalan, dan daftar keadaan ketika aturan
   memilih diam. Baca ini kalau ingin menelusuri kode, bukan merancang.
5. Bagian 11 — kontrak data antara backend dan task pane.
6. Bagian 14 — aturan yang mengikat agen coding.
7. Bagian 13 dan 15 — apa yang sudah selesai dan apa yang belum.
8. **Bagian 16 — cara tahu Fase 1 aman dan selesai.** Daftar periksa yang bisa
   dijalankan sendiri: empat perintah yang wajib hijau, cara menguji aturan
   terhadap naskah nyata tanpa membuka Word, tiga belas hal yang wajib
   dibuktikan di dalam Word, dan syarat sebelum Fase 2 boleh dimulai.

## Berkas yang sudah dihapus, dan kenapa

Jangan dicari, jangan dibuat lagi. Semuanya masih ada di riwayat git kalau
sewaktu-waktu diperlukan.

| Berkas | Alasan dihapus |
|---|---|
| `kontrak-data.md` | Menduplikasi `fase1 drafter.md` bagian 11. Dua berkas yang harus disamakan manual adalah pabrik cacat, dan keduanya sempat benar-benar berbeda isi |
| `keputusan-ux-penelaahan-fase1.md` | Bertentangan dengan kode: masih menyebut Track Changes sebagai cara mendapatkan warna merah–hijau. Isinya yang masih berlaku sudah pindah ke bagian 6 |
| `rancangan-analisis-terima-ekspor.md` | Sama, dan rancangan ekspornya diringkas di bagian 6.7 sebagai dua pilihan yang belum diputuskan |
| `konteks-hukum.md` | Seluruhnya kerangka kosong berisi `<!-- Isi akan ditambahkan kemudian -->`. Isinya ada di `pengetahuan-pmk-kmk.md` di ruang pengetahuan proyek |
| `konteks-sistem-existing.md` | Sama, kerangka kosong. Isinya ada di `pemahaman-jdih-law-analyzer.md` |
| `panduan-vibe.md` | Isinya dipindahkan ke `CLAUDE.md` supaya agen coding membacanya otomatis — **tetapi berkasnya ternyata masih ada di disk.** Ketahuan 18 Sep 2026. Selama masih ada, ia salinan kedua dari konvensi yang sama, yaitu persis pabrik cacat yang jadi alasan `kontrak-data.md` dihapus. Hapus, atau buat isinya menunjuk ke `CLAUDE.md` saja |

## Cara memakai dokumentasi ini dengan agen coding

```
baca konteks di docs/ lalu perbaiki: <masalahnya>
```

Agen wajib membaca `fase1 drafter.md` sampai habis sebelum mengubah kode. Bila
`project-brief.md` dan `fase1 drafter.md` bertentangan soal cara kerja teknis,
**`fase1 drafter.md` yang berlaku** — dokumen itu disamakan dengan kode setiap
kali kode berubah.

Tiga hal yang paling sering dilanggar:

- **`project-brief.md` bagian 8.11 bukan backlog.** Isinya dugaan yang belum
  dikonfirmasi ke penelaah. Jangan dibangun jadi aturan.
- **Bagian 14 butir 16** — apa pun yang ditandai wajib benar-benar salah.
  Aturan yang tidak bisa membuktikan kesalahannya harus dimatikan, bukan
  diperhalus.
- **Bagian 14 butir 9** — Office.js jarang muncul di data latih model.
  Verifikasi tiap method ke `frontend/node_modules/@types/office-js/index.d.ts`
  sebelum menulis kode, jangan mengarang.

## Kalau sudah sampai Fase 2

[`fase-2dan-3drafter.md`](fase-2dan-3drafter.md) berdiri sendiri dan bisa dibaca
sesudah `fase1 drafter.md`. Susunannya: ringkasan, struktur folder berikut
teknologi dan env-nya, **alur tujuh langkah beserta enam cabangnya** (termasuk
apa yang terjadi kalau dua pasal bertabrakan), daftar fitur dan batasannya, sisa
pertanyaan, dan hal janggal yang perlu dipertimbangkan.

Yang paling menentukan di sana: **parser struktur sebagai pondasi tunggal** yang
dipakai bersama seluruh Fase 2 dan 3, dan **contoh isi peta untuk 20 pasal** —
yang memperlihatkan apa sebenarnya yang dibaca model saat menalar.

Dokumen itu **rancangan, bukan perintah kerja.** Penulisan kodenya menunggu
persetujuan terpisah.
