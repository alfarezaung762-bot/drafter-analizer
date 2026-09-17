# Rancangan Alur Analisis–Terima–Ekspor Tanpa Pengaturan Word

> **Nama yang dipakai pengguna:** tidak ada “mode” tambahan. Di antarmuka,
> alurnya cukup: **Analisis → Terima/Tolak → Ekspor versi bersih**.

> **Status:** keputusan rancangan UX yang menggantikan versi sebelumnya.
> Pengguna tidak perlu membuka pengaturan Word, Track Changes, atau warna
> revisi.

## Hasil yang diminta

Ada dua dokumen dengan fungsi yang berbeda:

| Dokumen | Isi | Tujuan |
|---|---|---|
| **Naskah kerja di Word** | Revisi yang telah diterima tetap terlihat: teks lama merah/coret dan usulan hijau. Status keputusan ikut tersimpan. | Bukti dan ruang penelaahan yang dapat dibuka lagi. |
| **Hasil Ekspor Bersih** | Hanya rumusan yang telah diterima, dengan format naskah normal. Tidak ada teks lama, coretan, warna hijau, komentar add-in, atau metadata penelaahan. | Berkas final untuk dikirim. |

Dengan demikian, **Terima bukan “bersihkan sekarang”**. Terima berarti
penelaah menerima rekomendasi dan add-in **menetapkan pasangan revisi itu secara
permanen di naskah kerja**. Pembersihan hanya dilakukan pada **salinan baru**
saat Ekspor.

## Perilaku yang wajib

1. Analisis menandai tepat kata, frasa, atau kalimat yang salah — bukan satu
   paragraf penuh.
2. Teks lama terlihat merah dan tercoret; usulan terlihat hijau di sebelahnya.
3. Klik **Terima** menyimpan kedua bagian tersebut serta status
   `diterima` dalam naskah kerja Word.
4. Klik **Tolak** menghapus usulan dan tanda revisi itu, lalu memulihkan teks
   serta format asli.
5. Klik **Ekspor versi bersih** membuat dokumen baru; dokumen kerja tidak
   diubah.
6. Pengguna tidak menyetel apa pun di Word dan add-in tidak membuat jejak
   seperti `Ajat … formatted highlight`.

## Siklus satu temuan penggantian

| Aksi pengguna | Naskah kerja Word | Metadata temuan | Hasil ekspor bersih |
|---|---|---|---|
| **Analisis** | Pasangan merah/coret + hijau dipasang sebagai usulan yang belum diputuskan. | `belum_ditinjau` | Ekspor belum tersedia untuk temuan ini. |
| **Terima** | Pasangan tetap terlihat dan menjadi bagian permanen dari naskah kerja. | `diterima` | Teks lama dibuang; usulan dipertahankan sebagai teks normal. |
| **Tolak** | Naskah kembali ke teks dan format asli tanpa tanda add-in. | `ditolak` atau riwayat keputusan internal | Teks asli dipertahankan. |
| **Ekspor versi bersih** | Tidak berubah. | Dibaca untuk menentukan transformasi. | Dibuat sebagai DOCX baru. |

Untuk menghindari hasil final yang tidak sengaja melewatkan masalah, perilaku
aman Fase 1 adalah **menahan Ekspor** selama masih ada temuan
`belum_ditinjau`. Panel harus menampilkan jumlahnya dan meminta penelaah
menekan Terima atau Tolak terlebih dahulu.

## Rancangan yang dipilih

### A. Add-in menyimpan tampilan revisi dan membuat ekspor bersih — direkomendasikan

Ini paling sesuai dengan permintaan: warna merah–hijau konsisten, tidak ada
setting Word, naskah kerja menyimpan jejak revisi, dan hasil akhir diekspor
bersih.

Add-in tidak bergantung pada warna **Track Changes** Word karena warna itu
ditentukan oleh preferensi pengguna. Sebagai gantinya, add-in mengelola
pasangan revisi sendiri:

```text
Undang-undang  →  Undang-Undang
[merah + coret]   [hijau]
```

Office.js dapat mengatur warna dan coretan pada rentang teks. Content control
bertag membuat setiap sisi pasangan dapat ditemukan lagi setelah dokumen
disimpan atau dibuka ulang. Referensi resmi: [Word Font](https://learn.microsoft.com/en-us/javascript/api/word/word.font?view=word-js-preview),
[Word Range](https://learn.microsoft.com/en-us/javascript/api/word/word.range?view=word-js-preview),
dan [Word ContentControl](https://learn.microsoft.com/en-us/javascript/api/word/word.contentcontrol?view=word-js-preview).

### B. Track Changes asli dengan aplikasi Windows pendamping

Aplikasi Windows/COM dapat mengubah preferensi warna Track Changes. Ini dapat
membuat revisi Word asli, tetapi hanya cocok untuk Windows, mengubah preferensi
global Word, butuh instalasi organisasi, dan memengaruhi dokumen lain. Karena
itu bukan rancangan Fase 1.

### C. Diff hanya di panel add-in

Pilihan ini tidak mengubah naskah kerja sampai ekspor, sehingga aman namun tidak
memenuhi kebutuhan merah/coret dan hijau langsung di badan Word. Ini hanya
fallback bila dokumen terkunci atau rentang tidak aman disentuh.

## Cara kerja teknis pilihan A

### Saat Analisis

1. Backend mengembalikan rentang presisi: indeks paragraf, offset, panjang,
   teks asli, dan usulan.
2. Add-in membuktikan bahwa rentang itu masih cocok secara persis. Jika kata
   yang sama muncul berulang atau teks telah berubah, add-in tidak menulis dan
   menampilkan kartu untuk penelaahan manual.
3. Sebelum menulis, add-in menyimpan snapshot teks dan format asli (OOXML atau
   format yang relevan), serta format dasar yang akan dipakai usulan saat
   diekspor.
4. Add-in membuat pasangan teks lama dan usulan, masing-masing dalam content
   control bertag dengan ID temuan. Jika `WordApiDesktop 1.3` tersedia, isi
   yang masih belum diputuskan dapat dikunci; bila tidak, isi harus diverifikasi
   ulang saat tombol diklik.
5. Add-in memberi teks lama format merah + coret dan usulan format hijau. Satu
   komentar ringkas boleh dibuat bila temuan memang memerlukannya; tidak ada
   sorotan paragraf penuh.
6. Add-in menyimpan mode Track Changes saat ini, mematikannya hanya selama
   add-in memasang atau memulihkan formatnya, lalu mengembalikan mode semula.
   Ini mencegah Word mencatat perubahan format add-in sebagai `formatted
   highlight`.
7. ID content control, snapshot, dan status disimpan persisten dalam
   `CustomXmlPart` atau document settings. Custom XML tersedia pada WordApi
   1.4; lihat [CustomXmlPartCollection](https://learn.microsoft.com/en-us/javascript/api/word/word.customxmlpartcollection?view=word-js-preview).

### Saat Terima

1. Add-in mengubah status temuan menjadi `diterima`.
2. **Tidak ada teks yang dihapus dan tidak ada warna yang dibersihkan.** Teks
   lama merah/coret dan usulan hijau tetap ada sebagai rekam revisi pada naskah
   kerja.
3. Status dan snapshot dipersistenkan bersama dokumen. Add-in meminta Word
   menyimpan dokumen; bila penyimpanan gagal, panel harus memberi tahu pengguna
   dan tidak mengklaim bahwa keputusan sudah permanen.
4. Satu komentar penelaahan, bila ada, tetap maksimal satu per temuan di naskah
   kerja. Ia tidak ikut ke dokumen ekspor bersih.

### Saat Tolak

1. Add-in menghapus usulan hijau dan separator pasangan.
2. Add-in mengembalikan teks serta format asli dari snapshot; teks tidak lagi
   merah atau tercoret.
3. Content control dan komentar add-in untuk temuan itu dihapus. Riwayat status
   `ditolak` boleh dipertahankan hanya dalam metadata audit, bukan di badan
   dokumen.

### Saat Ekspor versi bersih

1. Add-in memastikan tidak ada temuan `belum_ditinjau`.
2. Add-in membuat **salinan DOCX baru**, bukan menjalankan pembersihan pada
   naskah kerja yang sedang dibuka.
3. Pada salinan itu, untuk setiap temuan `diterima`, teks lama merah/coret dan
   separator dihapus; usulan dipertahankan lalu dikembalikan ke format naskah
   normal yang tersimpan pada snapshot.
4. Content control, komentar add-in, metadata penelaahan, serta seluruh warna
   dan coretan milik add-in dihapus dari salinan.
5. Pengguna menerima unduhan/berkas `-bersih.docx`. Naskah kerja tetap memiliki
   seluruh rekam revisi yang diterima.

### Jalur ekspor yang realistis

1. Add-in menyimpan naskah kerja dengan `context.document.save()` setelah
   keputusan Terima/Tolak berhasil.
2. Add-in mengambil **salinan** DOCX aktif sebagai file OOXML terkompresi lewat
   `Office.context.document.getFileAsync(Office.FileType.Compressed)`.
3. Salinan itu dikirim satu kali ke endpoint Ekspor. Backend tidak menyusun
   ulang seluruh dokumen dengan `python-docx`; ia menyalin paket DOCX dan hanya
   membersihkan content control/tag milik add-in pada XML yang relevan.
4. Backend mengembalikan `-bersih.docx`; task pane mengunduhkannya atau
   membukanya sebagai dokumen Word baru untuk disimpan.

Dengan cara itu, tabel, header/footer, nomor halaman, gambar, gaya, dan bagian
Word lain tidak dibuat ulang oleh aplikasi. Yang diubah hanya penanda add-in
yang memang dibuat pada tahap Analisis.

`getFileAsync(...Compressed)` tersedia pada Word Windows, Mac, dan iPad, tetapi
tidak pada Word di web. Karena penelaah target memakai Word desktop, Fase 1
menjadikan Word desktop sebagai jalur resmi Ekspor. Pada Word di web, tombol
Ekspor harus memberi alasan yang jelas, bukan menghasilkan berkas yang tidak
lengkap. Referensi resmi: [mengambil seluruh dokumen dari add-in Word](https://learn.microsoft.com/en-us/office/dev/add-ins/develop/get-the-whole-document-from-an-add-in-for-powerpoint-or-word)
dan [Word Document.save](https://learn.microsoft.com/en-us/javascript/api/word/word.document?view=word-js-preview).

Backend wajib memproses salinan dalam memori atau penyimpanan sementara yang
segera dibersihkan setelah respons. Naskah rancangan tidak boleh disimpan
permanen di server hanya karena pengguna menekan Ekspor.

## Pengaman

- Tidak ada penulisan bila rentang tidak dapat diverifikasi secara unik.
- Temuan yang saling tumpang tindih ditahan atau digabung; jangan pernah
  membentuk pasangan revisi yang saling merusak.
- Bila ada revisi pengguna yang belum selesai pada rentang sasaran, dokumen
  terlindungi, atau formatnya tidak aman dipulihkan, gunakan kartu manual.
- Setelah dokumen dibuka kembali, add-in membaca metadata untuk membangun lagi
  kartu dan status temuan yang telah diterima maupun yang masih menunggu.
- Tombol **Accept/Reject** bawaan ribbon Word bukan cara menyelesaikan temuan
  add-in ini. Tombol **Terima/Tolak** di panel mengubah status penelaahan;
  tombol **Ekspor versi bersih** membuat hasil final.

## Batas untuk temuan `catatan`

Temuan tanpa pengganti pasti tidak boleh dipalsukan menjadi perubahan teks.
Tombol Terima pada `catatan` hanya dapat mencatat bahwa penelaah telah melihat
catatan tersebut. Agar ekspor tidak menutup-nutupi masalah yang belum diperbaiki,
Fase 1 perlu menambah status eksplisit **“sudah diperbaiki manual”** sebelum
Ekspor diizinkan untuk temuan seperti ini. Aturan ini tidak mengubah alur
`penggantian` di atas.

## Kriteria selesai

- [ ] Pengguna baru melihat merah/coret dan hijau tanpa menyetel Word.
- [ ] Terima menyimpan pasangan revisi dan statusnya setelah Word ditutup lalu
      dibuka kembali.
- [ ] Tolak memulihkan teks dan format asli secara presisi.
- [ ] Tidak muncul revisi `formatted highlight` akibat tindakan add-in.
- [ ] Ekspor menghasilkan DOCX baru yang hanya berisi perubahan yang diterima,
      tanpa coretan, warna add-in, komentar add-in, atau metadata penelaahan.
- [ ] Ekspor tidak mengubah naskah kerja yang masih menampilkan jejak revisi.
- [ ] Semua skenario diuji pada berkas KMK 527 nyata serta dokumen contoh.
