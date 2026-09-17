# Keputusan UX Penelaahan — Fase 1

> **Status:** rancangan keputusan produk dari masukan penelaah, 17 September
> 2026. Dokumen ini menjadi acuan untuk perubahan berikutnya dan mengalahkan
> keputusan yang bertentangan di `fase1 drafter.md`, khususnya tentang pilihan
> PMK/KMK awal, sorotan satu paragraf, dan tampilan usulan.

## Jawaban singkat

**Ya, alur yang diinginkan dapat diwujudkan tanpa pengguna menyetel Word.**
Add-in dapat mewajibkan pilihan PMK/KMK, menemukan rentang kata atau kalimat
yang tepat, lalu menampilkan teks lama merah/coret dan usulan hijau.
**Terima menyimpan pasangan revisi itu di naskah kerja Word; Ekspor versi
bersih membuat salinan baru yang telah menerapkan usulan.** Tolak memulihkan
naskah semula.

Warna **Track Changes asli** memang tidak dapat dipaksa oleh Office.js karena
diatur oleh preferensi Word pengguna. Karena pengguna tidak boleh dibebani
pengaturan tersebut, rancangan utama memakai tampilan revisi yang dikelola
add-in, bukan warna Track Changes. Rincian dan pilihan alternatif ada di
[`rancangan-analisis-terima-ekspor.md`](rancangan-analisis-terima-ekspor.md).

## Tujuan pengalaman penelaah

Penelaah harus langsung dapat menjawab tiga hal tanpa mencari-cari:

1. Apa teks yang kurang tepat?
2. Apa usulan penggantinya?
3. Apa yang terjadi jika saya menerima atau menolaknya?

Karena itu, **setiap tanda di dokumen berarti ada temuan yang benar-benar perlu
ditinjau**. Bila alat tidak dapat menentukan lokasi atau statusnya dengan cukup
andal, alat tidak boleh memberi sorotan merah, coretan, atau komentar seolah-olah
temuan itu pasti benar.

## Alur yang disetujui

### 1. Jenis dokumen wajib dipilih

- Saat panel dibuka, **PMK dan KMK sama-sama belum dipilih**.
- Menekan **Analisis** tanpa pilihan tidak mengirim permintaan ke backend dan
  tidak mengubah dokumen.
- Kelompok tombol PMK/KMK mendapat fokus, pesan "Pilih jenis dokumen: PMK atau
  KMK", dan animasi goyang singkat.
- Setelah penelaah memilih salah satunya, nilai itu dikirim sebagai
  `jenis_dokumen` yang wajib ke backend.

Tidak boleh ada nilai awal PMK. Nilai awal ini berisiko membuat KMK diperiksa
dengan kaidah PMK tanpa disadari, yang kemudian menghasilkan temuan palsu.

### 2. Setelah Analisis

Untuk setiap temuan yang dapat dipastikan:

- hanya kata, frasa, atau kalimat yang keliru yang ditandai — **bukan seluruh
  paragraf**;
- teks lama dan usulan pengganti ditampilkan sebagai satu pasangan revisi
  milik add-in, yang dapat disimpan di naskah kerja;
- kartu di panel menampilkan nomor temuan, cuplikan singkat, **Lompat ke Teks**,
  **Terima**, dan **Tolak**;
- maksimal ada **satu komentar ringkas per temuan**, berisi alasan dan rujukan;
  kartu tidak mengulang uraian panjang yang sama.

Asumsi dokumen ini: "satu komentar" berarti satu komentar untuk setiap temuan,
bukan satu komentar untuk seluruh dokumen. Jika yang dimaksud adalah satu
komentar total untuk seluruh dokumen, keputusan itu perlu dikonfirmasi karena
alasan dan rujukan setiap temuan tidak lagi dapat ditempelkan pada lokasinya.

### 3. Terima dan Tolak

| Aksi | Hasil di Word |
|---|---|
| **Terima** | Status temuan menjadi diterima dan pasangan revisi tetap tersimpan di naskah kerja: teks lama merah/coret serta usulan hijau tidak dibersihkan. |
| **Tolak** | Usulan dan tanda revisi dihapus; kata atau kalimat asli kembali persis seperti sebelum analisis. |
| **Lompat ke Teks** | Kursor memilih rentang tepat yang dilaporkan oleh kartu, bukan hanya membuka paragrafnya. |
| **Ekspor versi bersih** | Add-in membuat DOCX baru. Pada salinan itu teks lama dibuang, usulan diterapkan sebagai teks normal, dan seluruh penanda/comment add-in dibersihkan. Naskah kerja tidak diubah. |

Untuk temuan yang tidak mempunyai satu jawaban pasti — misalnya dua judul yang
berbeda tetapi alat tidak tahu mana yang benar — add-in **tidak** boleh
menyisipkan pengganti otomatis. Kartu dan satu komentar menjelaskan masalahnya;
penelaah memilih perbaikan sendiri. Tidak ada teks yang dapat dicoret bila
masalahnya adalah bagian yang hilang.

## Tampilan merah–hijau dan jejak "formatted highlight"

### Rekomendasi

Gunakan **tampilan revisi yang dikelola add-in** untuk penggantian yang
deterministik: teks lama diberi merah/coret dan usulan diberi hijau pada rentang
yang sama-sama presisi. Add-in menyimpan snapshot format asli. Saat **Terima**,
tampilan itu dipertahankan sebagai rekam revisi dalam naskah kerja; saat
**Tolak**, ia dipulihkan ke naskah semula; saat **Ekspor**, ia dibersihkan hanya
di salinan baru.

Dengan cara ini, penelaah tidak mengatur apa pun di Word. Tombol Terima/Tolak
di task pane menyelesaikan keputusan usulan; tombol **Ekspor versi bersih**
membuat dokumen akhir terpisah.

### Batas teknis

- Add-in tidak memiliki API untuk memaksakan warna revisi atau nama penulis
  **Track Changes**. Word memakai pengaturan dan identitas pengguna yang sedang
  membuka berkas.
- `font.color` dan `strikeThrough` dapat dipakai **hanya** dalam tampilan yang
  dikelola add-in: snapshot dan status harus disimpan agar Tolak dapat
  memulihkan naskah kerja dan Ekspor dapat membuat salinan final tanpa warna.
  Warna memang bertahan di naskah kerja setelah Terima; warna tidak boleh ikut
  ke dokumen hasil ekspor.
- `Critique`/annotation berwarna tidak dapat dijadikan solusi pada Word 2024
  LTSC tanpa langganan Microsoft 365; pengujian sebelumnya menghasilkan
  `NotImplemented`.

### Menghapus spam "Ajat … formatted highlight"

Teks seperti "Ajat … formatted highlight" adalah jejak **revisi format Word**,
bukan komentar penelaahan yang berguna. Penyebabnya adalah memberi
`font.highlightColor` ketika Track Changes sedang aktif. Perbaikan yang wajib:

1. simpan mode Track Changes pengguna, matikan sementara hanya saat add-in
   membuat atau membersihkan tampilan review, lalu pulihkan mode semula;
2. jangan memakai sorotan seluruh paragraf sebagai penanda utama;
3. simpan snapshot format asli dan gunakan content control bertag agar add-in
   dapat membersihkan tepat satu temuan;
4. jangan melakukan analisis ulang sebelum semua temuan sebelumnya selesai atau
   dibersihkan dari dokumen.

Dengan aturan ini, add-in tidak membuat revisi format tambahan. Tampilan merah
dan hijau adalah rekam revisi yang dikelola add-in, bukan revisi format Word
yang tercatat atas nama pengguna.

## Ketepatan temuan adalah prioritas

### Judul yang sudah tampak kapital

Kasus judul yang secara visual sudah kapital tetapi tetap ditandai adalah
masalah kepercayaan paling serius. Judul dapat ditulis dengan huruf campur tetapi
ditampilkan kapital melalui atribut atau gaya **All Caps**. Backend hanya melihat
teks polos; frontend harus membaca atribut itu dari Word.

Bila atribut format telah terbaca dan memastikan judul memang belum tampil
kapital, F1-001 boleh menawarkan versi kapitalnya melalui Mode Penelaahan
Otomatis.
Rentangnya adalah isi judul itu sendiri (satu atau beberapa baris judul), tidak
boleh mencakup bagian lain dari dokumen. Bila kepastian format tidak ada, usulan
ini tidak dipasang.

Aturan F1-001 harus bersifat *fail closed terhadap penandaan*:

- bila `font.allCaps` berhasil dibaca dan bernilai `true`, judul **bukan**
  temuan;
- bila atribut itu tidak didukung, gagal dibaca, atau nilainya tidak pasti,
  pemeriksaan kapital judul **dilewati** dan panel hanya memberi informasi
  "kapital judul belum dapat diverifikasi";
- keadaan tidak pasti tidak boleh berubah menjadi sorotan atau komentar
  kesalahan.

Konsekuensinya alat mungkin melewatkan judul yang benar-benar salah pada Word
yang tidak dapat menyampaikan metadata formatnya. Ini sengaja dipilih: lebih
baik tidak memberi tanda daripada menandai naskah yang sudah benar.

### Rentang presisi

Kontrak data sudah mempunyai `offset_mulai`, `panjang`, dan `teks_asli`, tetapi
implementasi harus memperlakukannya sebagai kontrak keselamatan:

- Word harus menemukan satu rentang yang teksnya **persis** cocok dengan
  `teks_asli` pada posisi yang dimaksud;
- bila teks yang sama muncul lebih dari sekali, pemilihan tidak boleh sekadar
  memakai kecocokan pertama;
- bila rentang tidak dapat diverifikasi, jangan mengganti atau mewarnai
  paragraf penuh; tampilkan kegagalan lokasi pada kartu dan minta penelaah
  meninjau secara manual.

Aturan struktur atau kelengkapan yang memang tidak mempunyai teks salah tidak
boleh berpura-pura memiliki rentang merah. Tampilkan sebagai kartu penelaahan
dengan satu komentar pada jangkar terdekat yang relevan.

## Kondisi saat ini yang harus diperbaiki

| Perilaku saat ini | Mengapa tidak sesuai | Keputusan baru |
|---|---|---|
| PMK terpilih secara default | KMK dapat dianalisis dengan aturan PMK | Nilai awal kosong dan validasi goyang sebelum analisis |
| `catatan` diberi highlight kuning untuk satu paragraf penuh | Penelaah harus mencari kata/kalimat yang dimaksud; dapat menghasilkan revisi format spam | Hanya rentang presisi atau tidak ada sorotan jika tidak dapat dipastikan |
| Komentar ditempel pada seluruh paragraf | Lokasi komentar tidak menunjukkan masalah yang sebenarnya | Satu komentar, berjangkar pada rentang presisi |
| Sebagian penggantian masih memakai Track Changes | Warna bergantung pada Word, usulan dapat tidak terlihat pada Simple Markup, dan pencocokannya masih perlu diuji | Ganti dengan tampilan revisi yang dikelola add-in dan uji Terima/Tolak/Ekspor dengan teks berulang |
| Deteksi All Caps gagal bila metadata Word tidak tersedia | Judul yang sudah benar dapat ditandai | Lewati pemeriksaan yang tidak dapat diverifikasi, jangan buat temuan palsu |

## Kriteria penerimaan sebelum disebut selesai

- [ ] Ketika PMK/KMK belum dipilih, Analisis tidak berjalan, pemilih bergoyang,
      dan backend tidak menerima permintaan.
- [ ] Judul yang tampak All Caps — baik diketik kapital maupun melalui format
      All Caps — tidak menghasilkan temuan F1-001.
- [ ] Jika format All Caps tidak dapat dibaca, F1-001 tidak membuat tanda salah;
      panel menyatakan pemeriksaan dilewati.
- [ ] Salah ejaan seperti `Undang-undang` hanya menandai kata itu, bukan
      paragrafnya; usulan tampil sebagai perubahan terlacak.
- [ ] Dua kesalahan dalam satu paragraf dapat dipilih, diterima, dan ditolak
      secara terpisah, termasuk saat kata yang sama muncul berulang.
- [ ] Satu temuan menghasilkan paling banyak satu komentar add-in dan tidak
      menambahkan revisi `formatted highlight`.
- [ ] Terima menyimpan teks lama merah/coret serta usulan hijau setelah Word
      ditutup lalu dibuka kembali; Tolak mengembalikan teks asli tanpa komentar
      atau sorotan add-in yang tersisa.
- [ ] Ekspor menghasilkan salinan DOCX bersih yang telah menerapkan semua
      usulan diterima tanpa mengubah naskah kerja.
- [ ] Analisis ulang tidak dapat menumpuk komentar atau revisi lama.
- [ ] Seluruh skenario diuji pada dokumen KMK 527 yang disebut penelaah, bukan
      hanya dokumen contoh.

## Urutan kerja yang disarankan

1. Ubah pemilih jenis dokumen menjadi wajib dan tanpa nilai awal.
2. Terapkan kebijakan anti-*false positive* untuk judul All Caps.
3. Buat resolver rentang presisi yang memverifikasi posisi dan teks sebelum
   menulis ke Word.
4. Ganti penandaan paragraf penuh dengan tampilan revisi milik add-in pada
   rentang presisi, serta hentikan perubahan format yang terekam sebagai
   `formatted highlight`.
5. Simpan status Terima/Tolak di dokumen kerja dan bangun Ekspor versi bersih
   sebagai DOCX baru, tanpa mengubah dokumen kerja.
6. Uji Terima/Tolak/Ekspor pada Word penelaah, termasuk teks berulang dan
   beberapa temuan dalam satu paragraf.
7. Setelah hasilnya benar pada berkas nyata, baru perluas aturan ejaan atau
   pemeriksaan lain.

## AI: opsional, bukan syarat Fase 1

AI dapat berguna pada fase berikutnya untuk menemukan calon kalimat ambigu,
inkonsistensi istilah, atau menawarkan rumusan alternatif. Namun AI tidak boleh
memasang perubahan langsung ke Word. Setiap hasil AI harus diberi label
"saran", menampilkan dasar/tingkat keyakinan, dan selalu menunggu Terima dari
penelaah. Untuk pemeriksaan Fase 1 yang aturan dan jawabannya pasti, gunakan
aturan deterministik agar hasil dapat diuji dan tidak menambah temuan palsu.
