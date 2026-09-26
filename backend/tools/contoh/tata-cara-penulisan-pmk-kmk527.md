# Tata Cara Penulisan PMK — KMK 527/KMK.01/2022 Lampiran II

Rujukan lengkap teknik penyusunan Peraturan Menteri Keuangan, disusun berurut
dari halaman pertama sampai lampiran. Dibuat sebagai basis aturan untuk
**Drafter Analiser** — alat bantu telaah rancangan PMK.

---

## 0. Cara membaca dokumen ini

**Sumber tunggal.** Keputusan Menteri Keuangan Nomor 527/KMK.01/2022 tentang
Pedoman Pembentukan Peraturan dan Keputusan di Lingkungan Kementerian Keuangan,
**Lampiran II** (Teknik Penyusunan), halaman 29–73 naskah PDF JDIH, memuat
butir 1 sampai butir 132. Spesifikasi fisik naskah diambil dari **Lampiran III**
huruf A angka IX beserta keteranganya (halaman 86–87), lembar analisis dampak
dari **Lampiran III** huruf C (halaman 89–90), dan daftar periksa penelaahan
dari **Lampiran III** huruf E — dua daftar: PMK pada halaman 92–94 dan KMK pada
halaman 95–97.

**Konvensi rujukan.** Angka dalam tanda kurung, misalnya (butir 54k-8), merujuk
nomor butir pada Lampiran II KMK 527 — **bukan** butir pada PMK yang sedang
disusun. Huruf dan angka setelahnya mengikuti penomoran internal butir tersebut:
`54k-8` berarti butir 54, huruf k, angka 8.

**Status pernyataan.** Setiap paragraf hanya memuat apa yang tertulis dalam KMK
527. Bila ada penafsiran, akibat praktis, atau keterangan dari sumber lain, hal
itu ditandai tegas dengan kata **Dugaan**, **Di luar KMK 527**, atau **Catatan
praktik**. Bagian yang bertentangan atau tidak diatur dalam sumber dicatat apa
adanya pada bagian 9.28.

**Blok Pemeriksaan.** Setiap bagian ditutup daftar hal yang dapat diperiksa,
dengan dua label:

- `[deterministik]` — dapat diputuskan aturan biasa (pencocokan pola, hitung,
  bandingkan string). Tidak memerlukan model bahasa.
- `[penilaian]` — memerlukan pembacaan makna, perbandingan dengan korpus
  peraturan, atau keputusan penelaah. Di sinilah AI dan rujukan OpenSearch
  berguna.

**Penomoran bagian.** Dokumen ini memakai penomoran 9.x berurut sesuai letak
bagian di dalam naskah PMK, dari atas halaman ke bawah. Pemetaan terhadap
catatan sebelumnya: *9.1 Menimbang* lama → **9.6**; *9.2 Mengingat* lama →
**9.7**; *9.3 Batang Tubuh* lama → **9.9 sampai 9.17**.

**Mutu naskah sumber.** Salinan KMK 527 di JDIH adalah hasil pemindaian yang
di-OCR. Kesalahan pengenalan karakter yang berulang: `MENTERI` → `MENTER!`,
`dan` → `clan`, `jika` → `iika`, `Berita` → `Serita`, `B.` → `8.`, `Pasal I` →
`PasalI`. Seluruh kutipan dalam dokumen ini sudah diverifikasi terhadap citra
halaman dan dirapikan, termasuk delapan bagan tata letak pada halaman 74–85 yang
dibaca dari tangkapan layar resolusi penuh. Status kelengkapan sumber ada pada
bagian 9.29.

---

## Peta satu dokumen PMK

```
KEPALA
 Lambang Garuda (kuning emas, tengah margin)          butir 1A
 MENTERI KEUANGAN                                     butir 1B
 REPUBLIK INDONESIA
 │
 ├─ A. JUDUL                                          butir 3–12
 │    PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
 │    NOMOR … TAHUN …
 │    TENTANG
 │    NAMA PERATURAN
 │
 ├─ B. PEMBUKAAN                                      butir 13–39
 │    ├─ DENGAN RAHMAT TUHAN YANG MAHA ESA            butir 14
 │    ├─ MENTERI KEUANGAN REPUBLIK INDONESIA,         butir 15
 │    ├─ Menimbang : a. … b. … c. …                   butir 16–22
 │    ├─ Mengingat  : 1. … 2. … 3. …                  butir 23–35
 │    ├─ MEMUTUSKAN:                                  butir 37
 │    └─ Menetapkan : PERATURAN MENTERI KEUANGAN
 │                    TENTANG … .                     butir 38–39
 │
 ├─ C. BATANG TUBUH                                   butir 40–108
 │    ├─ BAB I KETENTUAN UMUM                         butir 56–69
 │    │    └─ Pasal 1 — daftar definisi
 │    ├─ BAB II … BAB n MATERI POKOK                  butir 70–73
 │    │    └─ Bagian Kesatu, Kedua …      (opsional)  butir 52
 │    │         └─ Paragraf 1, 2 …        (opsional)  butir 53
 │    │              └─ Pasal                         butir 54
 │    │                   └─ (1) ayat                 butir 54e–h
 │    │                        └─ a. huruf            butir 54k-7
 │    │                             └─ 1. angka
 │    │                                  └─ a) → 1)   maks. 4 tingkat
 │    ├─ Ketentuan sanksi administratif               butir 74–78
 │    ├─ BAB … KETENTUAN LAIN-LAIN        (opsional)  butir 43
 │    ├─ BAB … KETENTUAN PERALIHAN        (opsional)  butir 79–85
 │    └─ BAB … KETENTUAN PENUTUP                      butir 86–108
 │         ├─ penunjukan organ pelaksana              butir 88
 │         ├─ nama singkat               (opsional)   butir 89–92
 │         ├─ pencabutan peraturan lama  (bila ada)   butir 93–99
 │         └─ saat mulai berlaku                      butir 100–107
 │
 ├─ D. PENUTUP                                        butir 109–119
 │    ├─ "Agar setiap orang mengetahuinya, …"         butir 110–111
 │    ├─ Ditetapkan di … pada tanggal …  (kanan)      butir 112–114
 │    ├─ Diundangkan di … pada tanggal … (kiri)       butir 115–117
 │    └─ BERITA NEGARA … TAHUN … NOMOR …              butir 118–119
 │
 ├─ E. PENJELASAN   (jika diperlukan)   tidak ada butir teknisnya — lihat 9.19
 └─ F. LAMPIRAN     (jika diperlukan)                 butir 120–121
```

---

## 9.0 PMK

PMK (Peraturan Menteri Keuangan) adalah peraturan yang ditetapkan Menteri
Keuangan untuk mengatur hal di bidang keuangan negara. **Di luar KMK 527:** PMK
tidak termasuk dalam hierarki Pasal 7 UU 12/2011, tetapi diakui dan mengikat
berdasarkan Pasal 8 sepanjang dibuat karena diperintahkan peraturan yang lebih
tinggi atau berdasarkan kewenangan Menteri; kedudukannya secara praktis di bawah
Peraturan Presiden. UU 12/2011 tercantum sebagai dasar hukum pertama KMK 527,
sehingga teknik penyusunan dalam Lampiran II merupakan penyesuaian teknik
nasional ke lingkungan Kementerian Keuangan.

Karena itu PMK dibuat untuk salah satu dari dua alasan: melaksanakan perintah
peraturan di atasnya yang menyerahkan pengaturan rinci kepada Menteri — biasanya
berbunyi "ketentuan lebih lanjut … diatur dengan Peraturan Menteri" — atau
menjalankan kewenangan Menteri sendiri di bidang tugasnya. Pembedaan ini bukan
teoritis: ia menentukan bentuk Menimbang (butir 19 dan butir 20) dan isi
Mengingat (butir 24).

Yang berwenang menetapkan PMK hanya Menteri Keuangan. **Menurut KMK 527 Lampiran
I:** rancangan disusun Unit Pengusul, ditelaah dan disempurnakan bersama Biro
Hukum, diharmonisasi di Kementerian Hukum, memerlukan persetujuan Presiden bila
memenuhi kriteria berdampak luas / strategis / lintas sektor, lalu setelah
ditandatangani Menteri diundangkan dalam Berita Negara.

KMK 527 mengatur enam jenis naskah (Lampiran II angka I): PMK, KMK, Peraturan
dan Keputusan Pimpinan Unit Organisasi Eselon I, serta Peraturan dan Keputusan
Pimpinan Unit Organisasi non Eselon. Teknik yang dirangkum dokumen ini adalah
**angka III**, yang berlaku bagi PMK yang ditandatangani Menteri, KMK yang
ditandatangani Menteri, dan KMK yang ditandatangani pimpinan unit untuk dan atas
nama Menteri. Peraturan dan Keputusan Pimpinan Unit Eselon I memakai kerangka
yang sama dengan lima pengecualian (butir 122, lihat 9.27).

Perbedaan pokok PMK dan KMK yang perlu dipegang sejak awal: batang tubuh PMK
terdiri atas **pasal**, batang tubuh KMK terdiri atas **diktum** (butir 42);
frasa "Dengan Rahmat Tuhan Yang Maha Esa" hanya ada pada PMK (butir 14); perintah
pengundangan dan bagian pengundangan hanya ada pada PMK (butir 110, butir 115);
PMK mulai berlaku saat diundangkan, KMK saat ditetapkan (butir 100).

### Pemeriksaan

- `[deterministik]` Dokumen yang batang tubuhnya memuat "KESATU/KEDUA" tetapi
  judulnya "PERATURAN MENTERI KEUANGAN" — salah satu keliru (butir 42).
- `[penilaian]` Alasan pembentukan (perintah peraturan lebih tinggi vs kewenangan
  sendiri) menentukan bentuk Menimbang dan Mengingat; tentukan dahulu sebelum
  memeriksa dua bagian itu.

---

## 9.1 Kepala halaman

Kepala halaman adalah dua unsur di bagian teratas halaman pertama, sebelum judul.
Pertama, lambang Negara Kesatuan Republik Indonesia berbentuk Garuda Pancasila
**berwarna kuning emas**, terletak di tengah margin (butir 1A). Kedua, di
bawahnya dua baris tulisan — baris pertama "MENTERI KEUANGAN", baris kedua
"REPUBLIK INDONESIA" — seluruhnya huruf kapital, berwarna kuning emas, terletak
di tengah margin (butir 1B).

Ketentuan ini hanya berlaku pada **halaman pertama**. Halaman kedua dan
seterusnya tidak mengulang kepala, dan hanya memuat nomor halaman di tengah atas
(butir 132a).

Dua rincian yang sering luput karena tidak terlihat pada salinan hitam putih:
warnanya **kuning emas**, bukan hitam, dan letaknya **di tengah margin**, bukan
rata kiri. Pada salinan digital yang diedarkan, warna ini sering hilang — itu
persoalan salinan, bukan persoalan rancangan.

### Pemeriksaan

- `[deterministik]` Halaman 1 memuat gambar (lambang) di tengah, diikuti dua
  baris kapital persis "MENTERI KEUANGAN" dan "REPUBLIK INDONESIA" (butir 1B).
- `[deterministik]` Urutan dua baris tidak terbalik.
- `[deterministik]` Halaman 2 dan seterusnya tidak mengulang blok kepala.
- `[penilaian]` Warna lambang pada berkas .docx — hanya dapat diperiksa bila
  gambar diurai; pada umumnya diserahkan ke pemeriksaan visual.

---

## 9.2 Judul

Judul adalah **empat baris** di bawah kepala halaman, bukan hanya baris terakhir:
jenis peraturan, nomor dan tahun, kata "TENTANG", dan nama peraturan. Setiap PMK
atau KMK **harus** diberi judul (butir 3), dan judul itu memuat keterangan
mengenai jenis, nomor, tahun pengundangan atau penetapan, kata tentang, dan nama
(butir 4).

Seluruh judul ditulis dengan **huruf kapital**, diletakkan di **tengah margin**,
dan **tanpa diakhiri tanda baca** (butir 8). Kata "TENTANG" ditulis seluruhnya
kapital, **tanpa spasi** — maksudnya tidak direnggangkan antarhuruf, bukan
`T E N T A N G` — dan diletakkan di tengah margin (butir 6).

```
✓ TENTANG                    ✗ T E N T A N G
✓ STANDAR BIAYA MASUKAN      ✗ STANDAR BIAYA MASUKAN.
                             ✗ Standar Biaya Masukan
```

Bentuk baris pertama berbeda menurut penanda tangan (butir 8, contoh a–c). PMK
yang ditandatangani Menteri: `PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA`.
KMK yang ditandatangani Menteri, dan KMK yang ditandatangani pimpinan unit untuk
dan atas nama Menteri, keduanya: `KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA`
— jadi judul KMK a.n. Menteri **tidak** menyebut jabatan penanda tangan; hal itu
baru muncul di bagian penutup (butir 114).

### 9.2.1 Nomor

Penomoran ditulis **hanya menggunakan angka Arab**, terdiri atas nomor peraturan
**tanpa penambahan huruf, angka Romawi, dan/atau tanda baca**, dilanjutkan dengan
tahun penetapan (butir 5).

```
✓ NOMOR 54 TAHUN 2026
✗ NOMOR 54/PMK.06/2015      ← memuat huruf dan tanda baca
```

**Catatan praktik.** Format lama `nnn/PMK.kk/tttt` masih dipakai luas pada
peraturan yang ditetapkan sebelum ketentuan ini berjalan — KMK 527 sendiri
bernomor `527/KMK.01/2022`, yakni format lama. Parser rancangan **wajib menerima
kedua format**, tetapi pemeriksa rancangan baru harus menolak format lama.
**Dugaan:** peralihan format terjadi sekitar 2023; hal ini tidak dinyatakan dalam
KMK 527 dan perlu diverifikasi ke Biro Hukum sebelum dijadikan aturan keras.

### 9.2.2 Nama

Nama dibuat **secara singkat**, hanya dengan satu kata atau frasa, tetapi secara
esensial maknanya telah mencerminkan isi peraturan (butir 7). Contoh yang
diberikan: `KAWASAN BERIKAT`, `SISTEM AKUNTANSI HIBAH`.

Nama **tidak boleh ditambah singkatan atau akronim** (butir 8), kecuali empat
keadaan: belum diserap atau belum ada padanan dalam bahasa Indonesia; merupakan
istilah teknis yang baku; bila tidak disingkat dapat mengubah makna; atau sudah
merupakan istilah baku yang digunakan secara internasional.

Contoh yang tidak tepat, dikutip langsung dari butir 8:

```
KEPUTUSAN MENTERI KEUANGAN
NOMOR ... TAHUN ...
TENTANG
PENYAMPAIAN DAN PENGELOLAAN LAPORAN PAJAK-PAJAK
PRIBADI (LP2P) PEJABAT/PEGAWAI DI LINGKUNGAN
KEMENTERIAN KEUANGAN
```

Yang keliru di situ adalah `(LP2P)` — akronim buatan sendiri yang tidak memenuhi
satu pun dari empat pengecualian.

### 9.2.3 Judul peraturan perubahan

Pada nama PMK yang diubah ditambahkan frasa **"perubahan atas"** di depan judul
PMK yang diubah (butir 9); untuk KMK berlaku hal yang sama, dengan alternatif
tambahan: nama KMK perubahan boleh pula dibuat mencerminkan atau menyesuaikan isi
KMK, misalnya `PERPANJANGAN MASA KERJA DAN PERUBAHAN SUSUNAN KEANGGOTAAN TIM …`
(butir 10). Kelonggaran ini **hanya ada pada KMK**; judul PMK perubahan selalu
memakai frasa "perubahan atas".

Bila sudah diubah lebih dari satu kali, di antara kata "perubahan" dan kata
"atas" disisipkan keterangan berapa kali perubahan dilakukan, **tanpa merinci
perubahan sebelumnya** (butir 11).

```
✓ PERUBAHAN KEDUA ATAS PERATURAN MENTERI KEUANGAN NOMOR … TAHUN … TENTANG …
✗ PERUBAHAN KEDUA ATAS PERATURAN MENTERI KEUANGAN NOMOR … TAHUN … TENTANG …
  SEBAGAIMANA TELAH DIUBAH DENGAN …        ← merinci perubahan sebelumnya
```

Perhatikan bahwa larangan merinci ini berlaku **di judul**. Di dalam Pasal I
justru sebaliknya: rangkaian perubahan sebelumnya disebut (butir 124c Contoh 2,
lihat 9.21).

### 9.2.4 Judul peraturan pencabutan

Pada nama PMK atau KMK pencabutan ditambahkan kata **"pencabutan"** dengan huruf
kapital di depan nama peraturan yang dicabut (butir 12).

```
PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
NOMOR ... TAHUN ...
TENTANG
PENCABUTAN PERATURAN MENTERI KEUANGAN NOMOR ... TAHUN ... TENTANG ...
```

Bedanya dengan perubahan: `PERUBAHAN ATAS …` berarti peraturan lama tetap hidup
dan sebagian isinya diganti; `PENCABUTAN …` berarti peraturan lama mati
seluruhnya.

### Pemeriksaan

- `[deterministik]` Judul terdiri atas empat baris dengan urutan jenis → nomor
  dan tahun → TENTANG → nama (butir 4).
- `[deterministik]` Seluruh judul kapital, tidak diakhiri titik atau tanda baca
  lain (butir 8).
- `[deterministik]` Nomor cocok dengan pola `NOMOR \d+ TAHUN \d{4}`; format
  `\d+/PMK\.\d+/\d{4}` ditandai sebagai format lama (butir 5).
- `[deterministik]` Nama memuat tanda kurung berisi huruf kapital — indikasi kuat
  akronim; tandai untuk ditinjau (butir 8).
- `[deterministik]` Judul perubahan kedua dan seterusnya memuat frasa
  "SEBAGAIMANA TELAH DIUBAH" → pelanggaran butir 11.
- `[deterministik]` Judul memuat "PERUBAHAN" → batang tubuh harus Pasal I dan
  Pasal II (butir 124b); judul memuat "PENCABUTAN" → batang tubuh Pasal 1 dan
  Pasal 2 (butir 130m). Lihat 9.21 dan 9.22.
- `[penilaian]` Apakah nama sudah singkat dan mencerminkan isi (butir 7).
- `[penilaian]` Apakah akronim yang dipakai memenuhi satu dari empat
  pengecualian butir 8.

---

## 9.3 Pembukaan

Pembukaan adalah seluruh blok antara judul dan batang tubuh. Terdiri atas lima
unsur berurutan (butir 13): frasa Dengan Rahmat Tuhan Yang Maha Esa (khusus PMK);
jabatan pembentuk; konsiderans; dasar hukum; dan diktum. Urutan ini mengikat —
tidak ada unsur yang boleh ditukar tempatnya atau dihilangkan, kecuali frasa
Dengan Rahmat yang memang tidak ada pada KMK.

### Pemeriksaan

- `[deterministik]` Kelima unsur hadir dan berurutan (butir 13).
- `[deterministik]` PMK tanpa "DENGAN RAHMAT TUHAN YANG MAHA ESA" → pelanggaran
  butir 14; KMK yang memuatnya → keliru pula.

---

## 9.4 Frasa Dengan Rahmat Tuhan Yang Maha Esa

Pada pembukaan PMK, **sebelum** nama jabatan pembentuk, dicantumkan frasa
"Dengan Rahmat Tuhan Yang Maha Esa", ditulis seluruhnya dengan huruf kapital dan
diletakkan di tengah margin (butir 14). Frasa ini **khusus PMK**; KMK tidak
memuatnya sama sekali.

```
DENGAN RAHMAT TUHAN YANG MAHA ESA
```

### Pemeriksaan

- `[deterministik]` String persis, seluruhnya kapital, satu baris, terletak
  setelah judul dan sebelum nama jabatan (butir 14).

---

## 9.5 Jabatan pembentuk

Jabatan pembentuk ditulis seluruhnya dengan huruf kapital, diletakkan di tengah
margin, dan **diakhiri tanda baca koma** (butir 15).

```
MENTERI KEUANGAN REPUBLIK INDONESIA,
```

Koma di ujung bukan hiasan: ia menandai bahwa kalimat belum selesai dan
bersambung ke konsiderans. Pada KMK bentuknya sama persis, hanya tanpa frasa
Dengan Rahmat di atasnya.

### Pemeriksaan

- `[deterministik]` Baris berakhir koma, bukan titik atau tanpa tanda baca
  (butir 15).
- `[deterministik]` Seluruhnya kapital.

---

## 9.6 Menimbang (Konsiderans)

Konsiderans adalah bagian yang memuat **uraian singkat mengenai pokok-pokok
pikiran yang menjadi pertimbangan dan alasan pembentukan** PMK atau KMK
(butir 17). Letaknya setelah jabatan pembentuk dan sebelum Mengingat. Ia menjawab
pertanyaan *mengapa peraturan ini dibuat*, dan tidak memuat norma apa pun —
seluruh norma ada di batang tubuh.

Diawali kata **"Menimbang"** yang diletakkan di sebelah kiri margin, huruf awal
kapital, diakhiri tanda baca **titik dua** (butir 16). Tiap pokok pikiran diawali
**huruf abjad**, dirumuskan dalam **satu kalimat** yang diawali kata **"bahwa"**
dan diakhiri **titik koma** (butir 21). Bila memuat lebih dari satu pokok
pikiran, setiap pokok pikiran dirumuskan dalam rangkaian kalimat yang merupakan
kesatuan pengertian (butir 18).

```
✓ Menimbang :  a. bahwa … ;
               b. bahwa … ;

✗ MENIMBANG :                  ← huruf awal saja yang kapital
✗ Menimbang.                   ← harus titik dua
✗ 1. bahwa … ;                 ← harus huruf abjad, bukan angka
✗ a. Dalam rangka … ;          ← harus diawali kata "bahwa"
✗ a. bahwa … .                 ← harus titik koma
```

Isinya bergantung pada alasan pembentukan, dan di sinilah pembedaan di 9.0
berbuah:

**Bila PMK merupakan pelaksanaan peraturan yang lebih tinggi** (butir 19),
konsiderans **cukup memuat satu pertimbangan** yang berisi uraian ringkas
mengenai perlunya melaksanakan ketentuan pasal atau beberapa pasal dari peraturan
yang lebih tinggi, **dengan menunjuk pasal** yang memerintahkan pembentukannya.
Selain itu, apabila diperlukan, dapat pula memuat unsur filosofis dan sosiologis
yang menjadi dasar pertimbangan (butir 19a), serta nomor dan ringkasan esensial
amar putusan dan pertimbangan hakim untuk PMK yang disusun sebagai tindak lanjut
Putusan Mahkamah Agung (butir 19b).

```
Menimbang : bahwa untuk melaksanakan ketentuan Pasal 10 ayat (4) Peraturan
            Pemerintah Nomor … tentang …, perlu menetapkan Peraturan Menteri
            Keuangan tentang …;
```

**Bila dibuat dalam rangka menjalankan kewenangan pejabat pembentuk, atau dalam
rangka perubahan atau pencabutan** (butir 20), konsiderans **seyogianya** memuat
unsur **sosiologis dan yuridis** yang menjadi pertimbangan dan alasan
pembentukannya. Kata "seyogianya" menandakan anjuran, bukan kewajiban mutlak —
berbeda dari "harus" pada butir lain.

**Butir terakhir berbunyi baku** bila pertimbangannya lebih dari satu (butir 22):

| Jenis | Rumusan |
|---|---|
| PMK | `bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf …, perlu menetapkan Peraturan Menteri Keuangan tentang …;` |
| KMK | `bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf …, perlu menetapkan Keputusan Menteri Keuangan tentang …;` |

Nama peraturan yang disebut di butir terakhir ini harus sama dengan nama pada
judul (bandingkan butir 39 yang mensyaratkan hal serupa untuk Menetapkan).

Perhatikan konsekuensinya: **bila konsiderans hanya satu butir, ia tidak diberi
huruf dan tidak memuat rumusan "berdasarkan pertimbangan"** — butir 22 hanya
berlaku "jika memuat lebih dari satu pertimbangan". Contoh butir 19 memang
menampilkan konsiderans tunggal tanpa huruf abjad.

### Pemeriksaan

- `[deterministik]` Kata "Menimbang" rata kiri, huruf awal kapital, diakhiri
  titik dua (butir 16).
- `[deterministik]` Penanda rincian berupa huruf `a. b. c.`, bukan angka
  (butir 21).
- `[deterministik]` Setiap butir diawali kata "bahwa" dan diakhiri titik koma
  (butir 21).
- `[deterministik]` Bila butir lebih dari satu, butir terakhir cocok dengan pola
  `bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf .*, perlu
  menetapkan Peraturan Menteri Keuangan tentang .*;` (butir 22a).
- `[deterministik]` Nama peraturan pada butir terakhir sama dengan nama pada
  judul (butir 22 jo. butir 4).
- `[deterministik]` Bila konsiderans menyebut pasal pemerintah ("Pasal … Peraturan
  Pemerintah Nomor …"), peraturan itu **wajib** muncul di Mengingat (butir 19
  jo. butir 24b).
- `[penilaian]` Apakah pertimbangan benar-benar memuat alasan, bukan norma
  terselubung (butir 17).
- `[penilaian]` Kecukupan unsur sosiologis dan yuridis pada PMK kewenangan
  sendiri, perubahan, atau pencabutan (butir 20).

---

## 9.7 Mengingat (Dasar Hukum)

Dasar hukum adalah bagian yang memuat landasan **kewenangan** untuk membentuk
PMK; letaknya setelah konsiderans Menimbang. Ia menjawab pertanyaan *atas dasar
wewenang apa Menteri boleh mengatur hal ini*. Diawali kata **"Mengingat"** yang
diletakkan di sebelah kiri margin, huruf awal kapital, diakhiri **titik dua**
(butir 23).

Isinya **hanya dua hal** (butir 24): dasar kewenangan pembentukan, dan peraturan
perundang-undangan yang memerintahkan pembentukannya. Dasar kewenangan
pembentukan adalah peraturan mengenai Kedudukan, Tugas, dan Fungsi Kementerian
Negara dan/atau Susunan Organisasi, Tugas, dan Fungsi Kementerian Negara
(butir 25).

Konsekuensi yang sering dilanggar: **Mengingat bukan daftar peraturan terkait.**
Peraturan yang topiknya berkaitan tetapi tidak memberi kewenangan dan tidak
memerintahkan pembentukan **tidak dicantumkan**, walau tingkatannya lebih tinggi;
rujukan semacam itu cukup diletakkan di batang tubuh. Konsekuensi kedua:
**Mengingat tidak pernah kosong**, karena PMK atas kewenangan Menteri sendiri
tetap memerlukan dasar kewenangan — kewenangan melekat pada jabatan dan diberikan
oleh peraturan.

**Batas tingkatan** (butir 26): hanya peraturan yang tingkatannya **lebih tinggi**
atau peraturan **yang sama** yang menjadi tugas dan fungsi Kementerian Keuangan.
Jadi PMK boleh mencantumkan PMK lain, tetapi tidak boleh mencantumkan peraturan
menteri dari kementerian lain.

**Yang wajib dan yang dilarang:**

| Keadaan | Status | Butir |
|---|---|---|
| PMK yang akan **diubah** oleh PMK yang dibentuk | **harus** dicantumkan | 27 |
| PMK atau KMK yang akan **dicabut** di bagian penutup | tidak dicantumkan | 28a |
| KMK yang telah **ditetapkan tetapi belum berlaku** | tidak dicantumkan | 28b |
| PMK atau peraturan yang telah **diundangkan tetapi belum berlaku** | tidak dicantumkan | 29 |

Pasangan butir 27 dan 28a adalah pembeda yang tajam antara PMK perubahan dan PMK
pencabutan, dan dapat diperiksa mesin: jika judul memuat "PERUBAHAN ATAS X",
maka X harus ada di Mengingat; jika judul memuat "PENCABUTAN X", maka X harus
tidak ada di Mengingat.

**Urutan** (butir 30): mengikuti tata urutan (hierarki) peraturan
perundang-undangan; bila tingkatannya sama, disusun **kronologis** berdasarkan
saat pengundangan atau penetapan.

**Bentuk penulisan.** Bila memuat lebih dari satu peraturan, tiap dasar hukum
diawali angka Arab 1, 2, 3, dan diakhiri **titik koma** (butir 31). Judul
peraturan diawali huruf kapital, **kecuali kata "tentang" dan kata
penghubung/konjungsi** (butir 32). Bila berupa Undang-Undang, **kedua huruf u
ditulis kapital** (butir 33).

```
✓ 1. Undang-Undang Nomor 39 Tahun 2008 tentang Kementerian Negara …;
✗ a. Undang-Undang Nomor 39 Tahun 2008 …;        ← harus angka
✗ Undang-undang Nomor 39 Tahun 2008 …            ← kedua huruf u kapital
✗ … Nomor 39 Tahun 2008 Tentang Kementerian …    ← "tentang" huruf kecil
```

Undang-Undang, Peraturan Pemerintah, dan Peraturan Presiden dilengkapi
pencantuman **Lembaran Negara Republik Indonesia dan Tambahan Lembaran Negara
Republik Indonesia** dalam tanda kurung (butir 34); PMK dilengkapi **Berita
Negara Republik Indonesia** dalam tanda kurung (butir 35).

```
Mengingat : 1. Undang-Undang Nomor 7 Tahun 2011 tentang Mata Uang (Lembaran
               Negara Republik Indonesia Tahun 2011 Nomor 64, Tambahan
               Lembaran Negara Republik Indonesia Nomor 5223);
            2. Peraturan Menteri Keuangan Nomor 43/PMK.02/2020 tentang …
               (Berita Negara Republik Indonesia Tahun 2020 Nomor 410);
```

**Khusus KMK** (butir 36): bila diperlukan, setelah Mengingat dapat dicantumkan
diktum **"Memperhatikan"**, yang memuat antara lain peraturan di luar tugas dan
fungsi Kementerian Keuangan, nota, surat, keputusan rapat, dan/atau dokumen
anggaran yang sangat relevan dengan materi yang ditetapkan. Ini jalan keluar bagi
rujukan yang ditolak butir 26 — tetapi **hanya tersedia untuk KMK, tidak untuk
PMK**.

**Jumlah dasar hukum tidak diatur.** KMK 527 hanya memakai rumusan "jika lebih
dari satu", sehingga satu dasar hukum tidak dilarang; dalam praktik biasanya
lebih dari satu karena dasar kewenangan disebut berlapis.

**Bila keliru.** Mengingat adalah bukti kewenangan, bukan sumbernya. **Di luar
KMK 527:** PMK yang sudah ditetapkan tetap berlaku walaupun ada dasar hukum yang
terlewat, sampai dicabut, diubah, atau dinyatakan tidak sah oleh Mahkamah Agung
— dengan alasan bertentangan dengan peraturan yang lebih tinggi atau
pembentukannya tidak memenuhi ketentuan yang berlaku (Pasal 31 ayat (2)
UU 3/2009), dan hanya atas permohonan pihak yang merasa haknya dirugikan. Karena
itu kekurangan pada Mengingat jauh lebih murah diperbaiki saat masih rancangan.

### Pemeriksaan

- `[deterministik]` Kata "Mengingat" rata kiri, huruf awal kapital, diakhiri
  titik dua (butir 23).
- `[deterministik]` Penanda berupa angka Arab `1. 2. 3.`, diakhiri titik koma
  (butir 31).
- `[deterministik]` Kata "tentang" dalam judul peraturan ditulis huruf kecil
  (butir 32).
- `[deterministik]` Penulisan `Undang-Undang`, bukan `Undang-undang` (butir 33).
- `[deterministik]` Setiap UU/PP/Perpres diikuti kurung berisi "Lembaran Negara
  … Tambahan Lembaran Negara …" (butir 34); setiap PMK diikuti kurung berisi
  "Berita Negara …" (butir 35).
- `[deterministik]` Urutan menaati hierarki UUD → UU → PP → Perpres → PMK, dan
  kronologis dalam tingkat yang sama (butir 30).
- `[deterministik]` Judul memuat "PERUBAHAN ATAS X" → X ada di Mengingat
  (butir 27). Judul memuat "PENCABUTAN X", atau X disebut dicabut di ketentuan
  penutup → X **tidak** ada di Mengingat (butir 28a).
- `[deterministik]` Mengingat kosong → pelanggaran (butir 24 jo. butir 25).
- `[deterministik]` Terdapat peraturan menteri selain PMK → pelanggaran butir 26.
- `[deterministik]` PMK memuat diktum "Memperhatikan" → pelanggaran; hanya untuk
  KMK (butir 36).
- `[penilaian]` Apakah setiap peraturan yang dicantumkan benar-benar memberi
  kewenangan atau memerintahkan pembentukan, bukan sekadar berkaitan topiknya
  (butir 24). Ini pemeriksaan yang memerlukan rujukan korpus.
- `[penilaian]` Apakah peraturan yang dicantumkan sudah diundangkan dan sudah
  berlaku pada saat rancangan disusun (butir 29).

---

## 9.8 Diktum pembukaan

Diktum pembukaan terdiri atas tiga unsur (butir B.5, tanpa nomor butir): kata
"Memutuskan"; kata "Menetapkan"; dan jenis serta nama peraturan.

Kata **"MEMUTUSKAN:"** ditulis tanpa spasi, seluruhnya huruf kapital, diakhiri
tanda baca titik dua tanpa spasi, dan diletakkan di **tengah margin** (butir 37).

Kata **"Menetapkan"** dicantumkan setelahnya, **disejajarkan ke bawah** dengan
kata "Menimbang" dan "Mengingat" — jadi rata kiri, bukan di tengah. Huruf awal
kapital, diakhiri titik dua (butir 38).

Jenis dan nama yang tercantum dalam judul **dicantumkan kembali** setelah kata
"Menetapkan", **tanpa frasa "Republik Indonesia"**, ditulis seluruhnya huruf
kapital, dan **diakhiri tanda baca titik** (butir 39).

```
                            MEMUTUSKAN:
Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA PEMBERIAN
             PINJAMAN PEMERINTAH DENGAN PERSYARATAN LUNAK KEPADA PT
             PERUSAHAAN LISTRIK NEGARA (PERSERO) MELALUI PUSAT
             INVESTASI PEMERINTAH.
```

Perbandingannya dengan judul menjelaskan dua perbedaan yang wajib ada:

```
Judul      : PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA … TENTANG X   (tanpa titik)
Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG X.
                                        ↑ tanpa "REPUBLIK INDONESIA"   ↑ diakhiri titik
```

Jadi keduanya **tidak boleh identik**. Yang harus sama adalah **namanya**; frasa
"Republik Indonesia" justru wajib dihilangkan, dan titik penutup justru wajib
ditambahkan.

### Pemeriksaan

- `[deterministik]` String persis `MEMUTUSKAN:` — kapital, tanpa spasi sebelum
  titik dua, di tengah margin (butir 37).
- `[deterministik]` "Menetapkan" rata kiri sejajar "Menimbang" dan "Mengingat"
  (butir 38).
- `[deterministik]` Isi Menetapkan **tidak** memuat "REPUBLIK INDONESIA"
  (butir 39).
- `[deterministik]` Isi Menetapkan diakhiri titik (butir 39).
- `[deterministik]` Nama setelah "TENTANG" pada Menetapkan sama persis dengan
  nama pada judul (butir 39).

---

## 9.9 Batang tubuh — kaidah umum

Batang tubuh memuat **semua materi muatan** PMK (butir 40), letaknya setelah
"Menetapkan" dan sebelum bagian penutup. Satuannya adalah **pasal** untuk PMK dan
**diktum** untuk KMK (butir 42).

Materi muatan pada umumnya dikelompokkan ke dalam empat kelompok berurutan
(butir 41): **ketentuan umum**; **materi pokok yang diatur**; **ketentuan
peralihan** (jika diperlukan); dan **ketentuan penutup**. Pengelompokan
dirumuskan secara lengkap sesuai kesamaan materi, dan bila terdapat materi yang
diperlukan tetapi tidak dapat dikelompokkan ke dalam ruang lingkup pengaturan
yang sudah ada, materi itu dimuat dalam **bab ketentuan lain-lain** (butir 43).

Ada aturan sisa yang halus dan mudah terlewat: materi muatan yang tidak memiliki
kesamaan materi namun **tidak termasuk** Bab Ketentuan Lain-Lain ditempatkan di
**pasal terakhir sebelum bab, bagian, atau paragraf berikutnya** (butir 49).

### Pemeriksaan

- `[deterministik]` Urutan empat kelompok tidak tertukar — ketentuan umum di
  awal, ketentuan penutup di akhir (butir 41).
- `[deterministik]` PMK memakai "Pasal", bukan "KESATU/KEDUA" (butir 42).
- `[penilaian]` Apakah pengelompokan benar-benar berdasar kesamaan materi
  (butir 43, butir 48).

---

## 9.10 Pengelompokan: bab, bagian, paragraf

Pengelompokan materi PMK **dapat** disusun secara sistematis dalam bab, bagian,
dan paragraf (butir 46). Kata "dapat" menandakan pilihan, bukan kewajiban:
pengelompokan dilakukan **jika** PMK mempunyai materi muatan yang ruang
lingkupnya sangat luas dan mempunyai banyak pasal (butir 47), dan dilakukan
**atas dasar kesamaan materi** (butir 48).

Tersedia empat susunan (butir 50):

```
a. pasal-pasal (tanpa bab, bagian, dan paragraf)
b. bab dengan pasal-pasal, tanpa bagian dan paragraf
c. bab dengan bagian dan pasal-pasal, tanpa paragraf
d. bab dengan bagian dan paragraf yang berisi pasal-pasal
```

Urutannya berlapis dan **tidak boleh melompat**: bagian hanya ada di dalam bab,
paragraf hanya ada di dalam bagian. Bab, bagian, dan paragraf hanyalah wadah —
norma hanya ada di pasal, dan **penomoran pasal berjalan terus menembus seluruh
bab tanpa dimulai ulang**.

**Bab** (butir 51) diberi nomor urut dengan **angka Romawi**, dan judul bab
seluruhnya ditulis dengan huruf kapital.

```
                        BAB I
                   KETENTUAN UMUM
```

**Bagian** (butir 52) diberi nomor urut dengan **bilangan tingkat yang ditulis
dengan huruf** dan diberi judul. Huruf awal kata "bagian", urutan bilangan, dan
setiap kata pada judul bagian ditulis kapital, kecuali huruf awal partikel yang
tidak terletak pada awal frasa.

```
                     Bagian Kesatu
        Penyerahan Pengurusan Piutang Negara dan
               Piutang Perusahaan Negara
```

**Paragraf** (butir 53) diberi nomor urut dengan **angka Arab** dan diberi judul.
Huruf awal kata "paragraf" dan setiap kata pada judul paragraf ditulis kapital,
kecuali huruf awal partikel yang tidak terletak pada awal frasa.

```
                      Paragraf 1
              Jenis Piutang yang Diserahkan
```

Perhatikan asimetri penomoran, yang paling sering keliru:

```
✓ BAB I          ✗ BAB 1            ← bab wajib angka Romawi
✓ Bagian Kesatu  ✗ Bagian 1         ← bagian wajib bilangan tingkat berhuruf
✓ Paragraf 1     ✗ Paragraf Kesatu  ← paragraf wajib angka Arab
```

Perhatikan pula asimetri kapitalisasi: judul **bab** kapital seluruhnya, judul
**bagian** dan **paragraf** hanya huruf awal tiap kata.

### Pemeriksaan

- `[deterministik]` Penanda bab cocok `BAB [IVXLC]+`, bukan angka Arab
  (butir 51).
- `[deterministik]` Judul bab kapital seluruhnya (butir 51).
- `[deterministik]` Penanda bagian cocok `Bagian (Kesatu|Kedua|Ketiga|…)`
  (butir 52a).
- `[deterministik]` Penanda paragraf cocok `Paragraf \d+` (butir 53a).
- `[deterministik]` Judul bagian dan paragraf berhuruf awal kapital tiap kata,
  kecuali partikel (butir 52b, butir 53b).
- `[deterministik]` Bagian muncul tanpa bab induk, atau paragraf tanpa bagian
  induk → pelanggaran susunan butir 50.
- `[deterministik]` Nomor pasal berurut menaik dan tidak dimulai ulang tiap bab
  (akibat butir 54c).
- `[penilaian]` Apakah pengelompokan diperlukan sama sekali (butir 47).

---

## 9.11 Pasal dan ayat

**Pasal** adalah satuan aturan dalam PMK yang memuat **satu norma** dan
dirumuskan dalam **satu kalimat** yang disusun secara singkat, jelas, dan lugas.
Pasal juga dapat memuat sejumlah norma dalam beberapa ayat yang memiliki
keterkaitan; rumusan norma dalam ayat dirumuskan dalam **satu kalimat satu ayat**
yang juga singkat, jelas, dan lugas (butir 54a, butir 54g).

Ada arahan gaya yang tegas dan sering diabaikan: materi muatan **lebih baik
dirumuskan ke dalam banyak pasal yang singkat dan jelas** daripada ke dalam
beberapa pasal yang masing-masing memuat banyak ayat, kecuali jika materi itu
merupakan satu rangkaian yang tidak dapat dipisahkan (butir 54b).

**Penulisan:**

| Ketentuan | Butir |
|---|---|
| Pasal diberi nomor urut angka Arab; huruf awal kata "pasal" kapital → `Pasal 5` | 54c |
| Huruf awal kata "pasal" **sebagai acuan** ditulis **kapital** → `sebagaimana dimaksud dalam Pasal 5` | 54d |
| Pasal dapat dirinci ke dalam beberapa ayat | 54e |
| Ayat diberi nomor urut angka Arab di antara tanda kurung, **tanpa** diakhiri titik → `(1)` | 54f |
| Satu ayat hanya memuat satu norma dalam satu kalimat utuh | 54g |
| Huruf awal kata "ayat" **sebagai acuan** ditulis **huruf kecil** → `sebagaimana dimaksud pada ayat (2)` | 54h |
| Rincian unsur boleh dirumuskan dalam bentuk tabulasi | 54i |
| Bilangan ditulis angka Arab diikuti kata atau frasa dalam tanda kurung | 54j |

Butir 54d dan 54h adalah pasangan yang paling sering tertukar dan paling mudah
diperiksa mesin — **Pasal** berkapital, **ayat** tidak:

```
✓ sebagaimana dimaksud dalam Pasal 2 ayat (2) huruf a
✗ sebagaimana dimaksud dalam pasal 2 Ayat (2) huruf a
```

Perhatikan pula pasangan preposisinya dalam contoh resmi KMK 527: acuan ke pasal
memakai **"dalam"**, acuan ke ayat memakai **"pada"** (butir 54h, contoh pada
butir 54). **Dugaan:** pola preposisi ini konsisten di seluruh contoh KMK 527,
tetapi tidak dinyatakan sebagai kaidah tersendiri, sehingga sebaiknya
diperlakukan sebagai peringatan lunak, bukan kesalahan keras.

Butir 54j untuk bilangan:

```
✓ paling lama 3 (tiga) hari kerja
✗ paling lama 3 hari kerja
✗ paling lama tiga hari kerja
```

Contoh pasal berayat yang dikutip KMK 527 (dari PMK 68/PMK.03/2012):

```
                              Pasal 2
(1) Untuk memastikan keadaan Wajib Pajak atau piutang pajak yang tidak dapat
    ditagih lagi sebagaimana dimaksud dalam Pasal 1, wajib dilakukan penelitian
    setempat atau penelitian administrasi oleh Kantor Pelayanan Pajak.
(2) Penelitian sebagaimana dimaksud pada ayat (1) dilakukan oleh Jurusita Pajak
    dan hasilnya dituangkan dalam laporan hasil penelitian.
```

### Pemeriksaan

- `[deterministik]` Penanda pasal cocok `Pasal \d+`, huruf awal kapital
  (butir 54c).
- `[deterministik]` Penanda ayat cocok `\(\d+\)` tanpa titik sesudah kurung
  (butir 54f).
- `[deterministik]` Kata "pasal" sebagai acuan berhuruf kecil → pelanggaran
  butir 54d.
- `[deterministik]` Kata "Ayat" sebagai acuan berhuruf kapital → pelanggaran
  butir 54h.
- `[deterministik]` Bilangan berupa angka tanpa pengulangan dalam kurung →
  pelanggaran butir 54j. Kecualikan nomor peraturan, tahun, nomor Lembaran/Berita
  Negara, dan acuan pasal/ayat.
- `[deterministik]` Acuan `Pasal N` dengan N yang tidak ada di dokumen →
  rujukan menggantung. (Tidak disebut butirnya, tetapi konsekuensi langsung dari
  butir 54d.)
- `[penilaian]` Apakah satu pasal memuat lebih dari satu norma (butir 54a).
- `[penilaian]` Apakah satu ayat memuat lebih dari satu norma (butir 54g).
- `[penilaian]` Apakah pasal yang berayat banyak sebaiknya dipecah (butir 54b).

---

## 9.12 Rincian (tabulasi)

Jika satu pasal atau ayat memuat rincian unsur, selain dirumuskan sebagai kalimat
dengan rincian, dapat dirumuskan dalam bentuk **tabulasi** (butir 54i). KMK 527
memberi contoh perbandingannya: satu kalimat panjang berisi dua dokumen menjadi
lebih mudah dipahami bila dipecah menjadi rincian bernomor.

**Sembilan ketentuan tabulasi** (butir 54k):

1. Setiap rincian harus dapat dibaca sebagai **satu rangkaian kesatuan dengan
   frasa pembuka** (54k-1).
2. Setiap rincian menggunakan **huruf abjad kecil** dan diberi tanda baca titik
   (54k-2).
3. Setiap frasa dalam rincian diawali **huruf kecil** (54k-3).
4. Setiap rincian diakhiri **titik koma** (54k-4).
5. Jika suatu rincian dibagi lagi ke dalam unsur yang lebih kecil, unsur itu
   dituliskan **masuk ke dalam** (54k-5).
6. Di belakang rincian yang **masih mempunyai rincian lebih lanjut** diberi
   **titik dua** (54k-6).
7. Pembagian rincian dengan urutan makin kecil ditulis: huruf abjad kecil diikuti
   titik, angka Arab diikuti titik, abjad kecil dengan kurung tutup, angka Arab
   dengan kurung tutup (54k-7).
8. Pembagian rincian **tidak melebihi 4 (empat) tingkat** (54k-8).
9. Jika rincian melebihi 4 tingkat, pasal yang bersangkutan **dibagi ke dalam
   pasal atau ayat lain** (54k-9).

Tangga empat tingkat itu:

```
a.              ← tingkat 1 — huruf abjad kecil + titik
   1.           ← tingkat 2 — angka Arab + titik
      a)        ← tingkat 3 — huruf abjad kecil + kurung tutup
         1)     ← tingkat 4 — angka Arab + kurung tutup
```

**Konjungsi** (butir 54l–54o). Bila rincian bersifat **kumulatif** ditambahkan
kata "dan"; bila **alternatif** ditambahkan "atau"; bila **kumulatif dan
alternatif** ditambahkan "dan/atau". Letaknya **di belakang rincian kedua dari
rincian terakhir** — yakni pada rincian kedua dari bawah — dan kata itu **tidak
perlu diulangi** pada akhir setiap unsur (butir 54o).

```
✓  a. satuan biaya honorarium;
   b. satuan biaya fasilitas; dan          ← hanya di sini
   c. satuan biaya perjalanan dinas.

✗  a. satuan biaya honorarium; dan
   b. satuan biaya fasilitas; dan          ← diulang, melanggar butir 54o
   c. satuan biaya perjalanan dinas.
```

**Tanda baca rincian terakhir — hati-hati di sini.** Butir 54k-4 berbunyi
"setiap rincian diakhiri dengan tanda baca titik koma", tanpa pengecualian.
Tetapi contoh-contoh resmi KMK 527 sendiri tidak seragam pada rincian terakhir:
contoh butir 55g menutup rincian terakhir dengan **titik**
(`c. Kepala Badan Pengawasan Keuangan dan Pembangunan.`), contoh butir 97
menutupnya dengan **koma** karena kalimatnya bersambung ke frasa penutup
(`b. Keputusan Menteri Keuangan Nomor …,` lalu `dicabut dan dinyatakan tidak
berlaku.`), sedangkan bagan butir 54o memakai titik koma untuk semuanya. **Yang
pasti:** rincian selain yang terakhir diakhiri titik koma. **Yang tidak
seragam:** rincian terakhir. Alat sebaiknya hanya menegakkan bagian yang pasti,
dan memperlakukan tanda baca rincian terakhir sebagai peringatan lunak yang
mengikuti apakah kalimat berlanjut sesudah daftar.

### Pemeriksaan

- `[deterministik]` Penanda tingkat 1 cocok `^[a-z]\.`, tingkat 2 `^\d+\.`,
  tingkat 3 `^[a-z]\)`, tingkat 4 `^\d+\)` (butir 54k-7).
- `[deterministik]` Kedalaman rincian ≤ 4 tingkat (butir 54k-8).
- `[deterministik]` Setiap rincian diawali huruf kecil (butir 54k-3).
- `[deterministik]` Rincian selain yang terakhir diakhiri titik koma
  (butir 54k-4).
- `[deterministik]` Rincian yang masih punya rincian lanjutan diakhiri titik dua
  (butir 54k-6).
- `[deterministik]` Konjungsi "dan"/"atau"/"dan/atau" muncul lebih dari sekali
  dalam satu daftar → pelanggaran butir 54o.
- `[deterministik]` Konjungsi muncul bukan pada rincian kedua dari terakhir →
  pelanggaran butir 54l–54n.
- `[deterministik]` Daftar dengan lebih dari satu rincian tanpa konjungsi sama
  sekali → tandai; sifat kumulatif atau alternatif tidak dinyatakan.
- `[penilaian]` Apakah tiap rincian benar-benar terbaca sebagai satu kesatuan
  dengan frasa pembukanya (butir 54k-1) — ini uji makna, bukan uji pola.
- `[penilaian]` Apakah "dan" yang dipakai memang kumulatif dan "atau" memang
  alternatif (butir 54l–54n).

---

## 9.13 Ketentuan Umum

Ketentuan Umum diletakkan dalam **bab satu**; jika PMK tidak dikelompokkan dalam
bab, ia diletakkan dalam pasal atau beberapa pasal awal (butir 56). Ia **dapat
memuat lebih dari satu pasal** (butir 57) — Pasal 1 lazimnya daftar definisi,
pasal berikutnya memuat hal umum lain.

Isinya tiga hal (butir 58): batasan pengertian atau definisi; singkatan atau
akronim yang dituangkan dalam batasan pengertian; dan hal lain yang bersifat umum
yang berlaku bagi pasal-pasal berikutnya, antara lain ketentuan yang mencerminkan
asas, maksud, dan tujuan tanpa dirumuskan tersendiri dalam pasal atau bab.

**Frasa pembuka baku** (butir 59): `Dalam Peraturan Menteri ini yang dimaksud
dengan:` — diakhiri titik dua. Bila memuat lebih dari satu definisi, masing-masing
uraian diberi **nomor urut angka Arab**, diawali **huruf kapital**, serta diakhiri
**titik** (butir 60). Perhatikan bedanya dengan rincian biasa: definisi berakhir
**titik**, rincian tabulasi berakhir **titik koma**.

```
                              BAB I
                         KETENTUAN UMUM

                              Pasal 1
Dalam Peraturan Menteri ini yang dimaksud dengan:
1. Barang Milik Negara yang selanjutnya disingkat BMN adalah semua barang yang
   dibeli atau diperoleh atas beban Anggaran Pendapatan dan Belanja Negara atau
   berasal dari perolehan lainnya yang sah.
2. …
```

**Hanya istilah yang dipakai berulang** yang boleh dimuat (butir 61). Kecualinya
satu: jika suatu kata hanya digunakan **satu kali** namun pengertiannya diperlukan
untuk suatu bab, bagian, atau paragraf tertentu, kata itu tetap diberi definisi
(butir 64).

**Konsistensi definisi** — tiga butir yang paling menuntut rujukan korpus:

- Apabila rumusan definisi dari suatu peraturan dirumuskan kembali dalam PMK yang
  akan dibentuk, rumusan itu **harus sama** dengan rumusan definisi dalam PMK yang
  mengatur permasalahan sejenis dan telah berlaku (butir 62).
- Rumusan batasan pengertian **dapat berbeda** dengan peraturan lain yang
  **bidangnya berbeda**, karena disesuaikan kebutuhan materi yang diatur
  (butir 63). Contoh yang diberikan: "Pemeriksaan" di bidang pajak berbeda
  rumusannya dengan "Pemeriksaan" di bidang jasa keuangan.
- Jika suatu definisi perlu dikutip kembali dalam ketentuan umum suatu peraturan
  **pelaksanaan**, rumusannya **harus sama** dengan rumusan dalam peraturan lebih
  tinggi yang dilaksanakan (butir 65).

Butir 62, 63, dan 65 membentuk satu aturan gabungan: **sama bidang → wajib sama;
beda bidang → boleh beda; melaksanakan peraturan di atasnya → wajib sama dengan
peraturan itu.** Inilah pemeriksaan yang paling berharga untuk dijalankan atas
indeks OpenSearch, dan paling mustahil dilakukan penelaah secara manual.

**Definisi tidak diberi penjelasan** (butir 66). Karena batasan pengertian
berfungsi menjelaskan makna, ia tidak perlu diberi penjelasan lagi, dan justru
karena itu **harus dirumuskan lengkap dan jelas sehingga tidak menimbulkan
pengertian ganda**.

**Kapitalisasi istilah terdefinisi** (butir 67): huruf awal tiap kata atau istilah
yang sudah didefinisikan ditulis **kapital**, baik digunakan dalam norma yang
diatur, dalam penjelasan, **maupun dalam lampiran**. Ini aturan yang sangat
cocok diperiksa mesin dan sangat sering dilanggar.

**Urutan penempatan** (butir 68): pengertian berlingkup umum ditempatkan lebih
dahulu daripada yang berlingkup khusus; pengertian yang terdapat lebih dahulu di
dalam materi pokok ditempatkan lebih dahulu; dan pengertian yang berkaitan dengan
pengertian di atasnya diletakkan berdekatan secara berurutan.

**Urutan nama jabatan atau instansi** (butir 69): mengikuti hierarki dari yang
tertinggi ke terendah. Organisasi profesi, asosiasi, perkumpulan, dan lembaga
lain yang dibentuk masyarakat **harus** ditempatkan di bawah nama jabatan atau
instansi pemerintah.

### Pemeriksaan

- `[deterministik]` Frasa pembuka persis `Dalam Peraturan Menteri ini yang
  dimaksud dengan:` (butir 59).
- `[deterministik]` Tiap definisi bernomor angka Arab, diawali huruf kapital,
  diakhiri titik (butir 60).
- `[deterministik]` Setiap istilah terdefinisi ditulis berhuruf awal kapital pada
  setiap kemunculannya di seluruh naskah termasuk lampiran (butir 67). Kebalikannya
  juga: istilah berkapital yang tidak pernah didefinisikan → tandai.
- `[deterministik]` Setiap istilah terdefinisi muncul minimal dua kali di luar
  Pasal 1 (butir 61), dengan pengecualian butir 64.
- `[deterministik]` Setiap singkatan yang dipakai diperkenalkan lewat pola
  `… yang selanjutnya disingkat X adalah …` (butir 58b).
- `[deterministik]` Nama jabatan pemerintah mendahului organisasi non-pemerintah
  (butir 69) — dapat diperiksa dengan daftar kata kunci.
- `[penilaian]` Kesamaan rumusan definisi dengan PMK sebidang yang berlaku
  (butir 62) — **pencarian korpus**.
- `[penilaian]` Kesamaan rumusan dengan peraturan lebih tinggi yang dilaksanakan
  (butir 65) — **pencarian korpus**.
- `[penilaian]` Apakah definisi menimbulkan pengertian ganda (butir 66).
- `[penilaian]` Urutan umum → khusus (butir 68).

---

## 9.14 Materi pokok yang diatur

Materi pokok ditempatkan **langsung setelah** bab ketentuan umum; jika tidak ada
pengelompokan bab, ia diletakkan setelah pasal atau beberapa pasal ketentuan umum
(butir 71).

Materi pokok yang diatur dalam peraturan yang jenis dan hierarkinya di bawah
Undang-Undang **secara mutatis mutandis berpedoman pada materi pokok yang diatur
dalam Undang-Undang** (butir 70). Artinya PMK tidak punya daftar materi muatan
sendiri; ia meminjam kaidah materi muatan UU sepanjang dapat diterapkan.

Pembagian materi pokok ke dalam bab, bagian, atau paragraf dilakukan **menurut
kriteria yang dijadikan dasar pembagian** (butir 72) — misalnya pembagian
berdasarkan tujuan, seperti pemisahan "Pemeriksaan untuk menguji kepatuhan" dan
"Pemeriksaan untuk tujuan lain". Bab, bagian, dan/atau paragraf dalam materi
pokok dibagi ke dalam pasal yang mengatur materi muatan pokok yang **memiliki
keterkaitan satu sama lain** (butir 73).

Nama bab materi pokok tidak dibakukan — bebas sesuai isinya, berbeda dari bab
pertama dan bab terakhir yang namanya sudah tertentu.

### Pemeriksaan

- `[deterministik]` Bab materi pokok berada tepat setelah Ketentuan Umum
  (butir 71).
- `[penilaian]` Apakah kriteria pembagian bab konsisten di seluruh naskah
  (butir 72).
- `[penilaian]` Apakah pasal dalam satu bab benar-benar saling berkait
  (butir 73).

---

## 9.15 Ketentuan sanksi administratif

Sanksi dalam PMK **pada prinsipnya hanya dimungkinkan dalam bentuk sanksi
administratif**, dan/atau dimungkinkan berdasarkan peraturan perundang-undangan
(butir 74). Jadi PMK tidak merumuskan sanksi pidana.

Substansi berupa sanksi administratif atas pelanggaran suatu norma dirumuskan
**menjadi satu bagian (pasal) dengan norma** yang memberikan sanksi administratif
(butir 75, senada butir 44). Jika norma yang memberikan sanksi administratif
terdapat lebih dari satu pasal, sanksi dirumuskan dalam **pasal terakhir** dari
bagian tersebut (butir 76). Bila norma yang dikenai sanksi cukup banyak, dapat
dilakukan pengelompokan dalam **bab atau pasal tersendiri** (butir 44).

Aturan letak yang mengikat: norma yang memberikan sanksi administratif atau
keperdataan **harus ditempatkan setelah** norma yang memuat kewajiban atau
larangan (butir 45). Tidak boleh sanksi mendahului kewajibannya.

Bentuk sanksi administratif antara lain pencabutan izin, pengawasan,
pemberhentian sementara, atau denda administratif (butir 77). Selain itu, jika
diperlukan, dapat pula diatur sanksi **keperdataan** berupa antara lain ganti
kerugian sesuai dengan peraturan perundang-undangan (butir 78).

### Pemeriksaan

- `[deterministik]` Naskah memuat kata "pidana", "kurungan", atau "penjara"
  sebagai sanksi → tandai terhadap butir 74.
- `[deterministik]` Pasal sanksi bernomor lebih kecil daripada pasal kewajiban
  atau larangan yang dirujuknya → pelanggaran butir 45.
- `[penilaian]` Apakah setiap kewajiban dan larangan yang perlu bersanksi sudah
  punya sanksi, dan sebaliknya apakah ada sanksi tanpa norma kewajiban
  (butir 45).

---

## 9.16 Ketentuan Peralihan

Ketentuan Peralihan memuat **penyesuaian pengaturan tindakan hukum atau hubungan
hukum yang sudah ada** pada saat PMK baru mulai berlaku, dengan empat tujuan
(butir 79): menghindari kekosongan hukum; menjamin kepastian hukum; memberikan
perlindungan hukum bagi pihak yang terkena dampak perubahan; dan mengatur hal
yang bersifat transisional atau sementara.

Letaknya dalam **Bab Ketentuan Peralihan, sebelum Bab Ketentuan Penutup**. Jika
tidak ada pengelompokan bab, pasal yang memuatnya ditempatkan sebelum pasal
Ketentuan Penutup; pada KMK, ia dimuat dalam diktum sebelum diktum Ketentuan
Penutup (butir 80).

Dalam PMK baru **dapat dimuat penyimpangan sementara atau penundaan sementara**
bagi tindakan hukum atau hubungan hukum tertentu (butir 81). Penyimpangan
sementara berlaku juga bagi ketentuan yang diberlakusurutkan (butir 82).

Bila PMK diberlakukan surut, PMK itu **hendaknya memuat ketentuan mengenai status
tindakan hukum atau hubungan hukum** yang ada dalam tenggang waktu antara tanggal
mulai berlaku surut dan tanggal pengundangan (butir 83).

Bila penerapan suatu ketentuan dinyatakan **ditunda sementara**, PMK itu **harus
memuat secara tegas dan rinci** tindakan hukum atau hubungan hukum yang dimaksud,
**serta jangka waktu atau persyaratan berakhirnya** penundaan tersebut
(butir 84). Penundaan tanpa batas waktu adalah cacat.

**Larangan perubahan terselubung** (butir 85). Rumusan dalam Ketentuan Peralihan
**tidak memuat perubahan terselubung** atas ketentuan PMK lain. Perubahan semacam
itu hendaknya dilakukan dengan membuat batasan pengertian baru dalam Ketentuan
Umum, atau dengan membuat PMK perubahan. Contoh rumusan terlarang yang dikutip
KMK 527:

```
✗ Pemberian Kredit atau kegiatan sejenis lainnya yang sudah ada pada saat mulai
  berlakunya Peraturan Menteri ini dinyatakan sebagai kegiatan Pembiayaan
  menurut Pasal 1 huruf d.
```

Yang keliru: ketentuan peralihan itu diam-diam mengubah makna istilah di
peraturan lain.

### Pemeriksaan

- `[deterministik]` Bab/pasal Ketentuan Peralihan berada sebelum Ketentuan
  Penutup (butir 80).
- `[deterministik]` Ketentuan Peralihan memuat frasa penundaan ("ditunda",
  "dikecualikan sementara") tanpa jangka waktu atau syarat berakhir → pelanggaran
  butir 84.
- `[deterministik]` Naskah memuat "berlaku surut" tetapi tidak ada Ketentuan
  Peralihan → pelanggaran butir 83 jo. butir 106a.
- `[penilaian]` Apakah rumusan peralihan mengubah makna ketentuan lain secara
  terselubung (butir 85).
- `[penilaian]` Apakah PMK yang mengubah keadaan hukum berjalan memerlukan
  Ketentuan Peralihan tetapi tidak memilikinya (butir 79).

---

## 9.17 Ketentuan Penutup

Ketentuan Penutup ditempatkan dalam **bab terakhir**; jika tidak ada
pengelompokan bab, dalam **pasal atau beberapa pasal terakhir** untuk PMK, atau
diktum terakhir untuk KMK (butir 86). Kata "beberapa pasal" penting: Ketentuan
Penutup lazim terdiri atas lebih dari satu pasal, karena satu pasal memuat satu
norma.

Isinya sudah ditentukan (butir 87): penunjukan organ atau alat kelengkapan yang
melaksanakan; nama singkat; status PMK atau KMK yang sudah ada; dan saat mulai
berlaku.

### 9.17.1 Penunjukan organ pelaksana

Penunjukan organ bersifat **menjalankan** (misalnya menunjuk pejabat tertentu
yang diberi kewenangan memberikan izin, mengangkat pegawai), **mengatur**
(memberikan kewenangan membuat peraturan pelaksanaan), atau **menetapkan**
(memberikan kewenangan menetapkan keputusan sebagai pelaksanaan) — butir 88.

### 9.17.2 Nama singkat

Bagi PMK yang namanya panjang **dapat** dimuat ketentuan mengenai nama singkat,
dengan dua syarat (butir 89): nomor dan tahun tidak dicantumkan; dan nama singkat
bukan berupa singkatan atau akronim, kecuali singkatan itu sudah sangat dikenal
dan tidak menimbulkan salah pengertian.

Nama singkat **tidak memuat pengertian yang menyimpang** dari isi dan nama PMK
(butir 90). Nama yang sudah singkat **tidak perlu** diberi nama singkat
(butir 91). **Sinonim tidak dapat digunakan** untuk nama singkat (butir 92).

Contoh yang tidak tepat, ketiganya dikutip KMK 527: memendekkan tanpa kehilangan
makna tetapi membuang bagian yang membatasi ruang lingkup (butir 90); memberi
nama singkat pada "Kawasan Berikat" yang sudah singkat (butir 91); dan mengganti
"Perusahaan Penjaminan Kredit dan Perusahaan Penjaminan Ulang Kredit" menjadi
"Perusahaan Penjaminan" (butir 92).

### 9.17.3 Pencabutan peraturan lama

Jika materi muatan PMK baru menyebabkan perubahan atau penggantian seluruh atau
sebagian materi PMK lama, dalam PMK baru **harus secara tegas diatur** mengenai
pencabutan seluruh atau sebagian materi PMK lama (butir 93).

Rumusan pencabutan **diawali frasa** `Pada saat Peraturan Menteri ini mulai
berlaku, …`, kecuali untuk pencabutan yang dilakukan dengan PMK tersendiri
(butir 94). Demi kepastian hukum, pencabutan **tidak dirumuskan secara umum**,
tetapi menyebutkan dengan tegas peraturan yang dicabut (butir 95).

Dua rumusan yang **tidak boleh tertukar**:

| Keadaan peraturan yang dicabut | Rumusan | Butir |
|---|---|---|
| sudah diundangkan dan/atau sudah mulai berlaku | `dicabut dan dinyatakan tidak berlaku` | 96 |
| sudah diundangkan atau ditetapkan **tetapi belum mulai berlaku** | `ditarik kembali dan dinyatakan tidak berlaku` | 99 |

```
                              Pasal 18
Pada saat Peraturan Menteri ini mulai berlaku, Peraturan Menteri Keuangan Nomor
136/PMK.01/2018 tentang Pedoman Tata Naskah Dinas Kementerian Keuangan (Berita
Negara Republik Indonesia Tahun 2018 Nomor 1388), dicabut dan dinyatakan tidak
berlaku.
```

Jika yang dicabut **lebih dari satu**, penulisan dilakukan dengan rincian dalam
bentuk tabulasi (butir 97) — perhatikan letak frasa penutupnya, yang berdiri
sesudah daftar dan berlaku untuk seluruh rincian:

```
Pada saat Peraturan Menteri ini mulai berlaku:
a. Peraturan Menteri Keuangan Nomor … tentang … (Berita Negara …); dan
b. Keputusan Menteri Keuangan Nomor … tentang … (Berita Negara …),
dicabut dan dinyatakan tidak berlaku.
```

Pencabutan **disertai keterangan mengenai status hukum** dari peraturan
pelaksanaan, peraturan lebih rendah, atau keputusan yang telah dikeluarkan
berdasarkan peraturan yang dicabut (butir 98). Ini butir yang paling sering
terlewat, dan akibatnya nyata: peraturan pelaksanaan menggantung tanpa status.

### 9.17.4 Saat mulai berlaku

Pada dasarnya **PMK mulai berlaku pada saat diundangkan**, sedangkan KMK mulai
berlaku pada saat ditetapkan (butir 100).

```
Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.
Keputusan Menteri ini mulai berlaku pada tanggal ditetapkan.
```

Jika ada **penyimpangan**, hal itu dinyatakan secara tegas dengan salah satu dari
empat cara (butir 101):

- **a.** menentukan tanggal tertentu — `Peraturan Menteri ini mulai berlaku pada
  tanggal 1 Januari 2022.` atau `… mulai berlaku pada tanggal diundangkan dan
  berlaku surut sejak tanggal 1 Januari 2021.`
- **b.** menentukan tanggal tertentu suatu **norma** akan berlaku —
  `Ketentuan mengenai … mulai berlaku pada tanggal …`
- **c.** menyerahkan penetapan saat mulai berlakunya kepada PMK atau KMK lain.
- **d.** menentukan lewatnya tenggang waktu tertentu sejak pengundangan atau
  penetapan. Agar tidak menimbulkan kekeliruan penafsiran, **gunakan frasa
  "setelah … (tenggang waktu) terhitung sejak tanggal diundangkan"** —
  `Peraturan Menteri ini mulai berlaku setelah 3 (tiga) bulan terhitung sejak
  tanggal diundangkan.`

**Frasa yang dilarang** (butir 102): ketentuan pemberlakuan **tidak menggunakan
frasa "… mulai berlaku efektif pada tanggal …"** atau sejenisnya, karena
menimbulkan ketidakpastian antara saat diundangkan dan saat berlaku efektif. Ini
larangan eksplisit dan mudah diperiksa mesin.

Pada dasarnya saat mulai berlaku **sama bagi seluruh bagian PMK dan seluruh
wilayah negara** (butir 103). Penyimpangan dinyatakan tegas dengan menetapkan
ketentuan yang berbeda saat mulai berlakunya, atau menetapkan saat mulai berlaku
yang berbeda bagi wilayah tertentu (butir 104).

**Berlaku surut** (butir 105–107). Pada dasarnya saat mulai berlaku PMK **tidak
dapat ditentukan lebih awal daripada saat pengundangannya** (butir 105a). Jika
ada alasan kuat untuk memberlakukan lebih awal, tiga hal diperhatikan
(butir 106): rincian pengaruh ketentuan berlaku surut terhadap tindakan hukum,
hubungan hukum, dan akibat hukum yang sudah ada **dimuat dalam ketentuan
peralihan**; awal saat mulai berlaku ditetapkan **tidak lebih dahulu daripada
saat rancangan mulai diketahui masyarakat**; dan pembebanan kewajiban yang
memberatkan para pihak serta yang mempengaruhi penerimaan negara **sedapat
mungkin tidak diberlakusurutkan**.

Saat mulai berlakunya peraturan **pelaksanaan** dari PMK **tidak boleh ditetapkan
lebih awal** daripada saat mulai berlakunya PMK yang mendasarinya (butir 107).

Terakhir, **PMK hanya dicabut dengan PMK atau peraturan perundang-undangan yang
lebih tinggi**, sedangkan KMK dicabut dengan PMK atau KMK (butir 108).

### Pemeriksaan

- `[deterministik]` Ketentuan Penutup memuat pasal saat mulai berlaku
  (butir 87d).
- `[deterministik]` Rumusan saat mulai berlaku cocok salah satu bentuk baku
  butir 100 atau butir 101 (lihat Lampiran B).
- `[deterministik]` Naskah memuat "mulai berlaku efektif" → pelanggaran
  butir 102.
- `[deterministik]` Pasal pencabutan diawali `Pada saat Peraturan Menteri ini
  mulai berlaku` (butir 94), kecuali PMK pencabutan tersendiri.
- `[deterministik]` Peraturan yang dicabut disebut lengkap dengan nomor, tahun,
  judul, dan Berita Negara — bukan rumusan umum semacam "peraturan lain yang
  bertentangan dengan Peraturan Menteri ini dicabut" → pelanggaran butir 95.
- `[deterministik]` Pilihan frasa `dicabut dan dinyatakan tidak berlaku` vs
  `ditarik kembali dan dinyatakan tidak berlaku` sesuai status keberlakuan
  peraturan yang dicabut (butir 96 vs butir 99) — memerlukan tanggal
  pengundangan dan tanggal mulai berlaku peraturan sasaran.
- `[deterministik]` Lebih dari satu peraturan dicabut → ditulis tabulasi
  (butir 97).
- `[deterministik]` Ada pencabutan tetapi tidak ada keterangan status peraturan
  pelaksanaannya → tandai terhadap butir 98.
- `[deterministik]` "berlaku surut" ada tetapi ketentuan peralihan tidak ada →
  pelanggaran butir 106a.
- `[deterministik]` Nama singkat memuat nomor atau tahun → pelanggaran butir 89a.
- `[penilaian]` Apakah nama singkat menyimpang dari isi, sinonim, atau tidak
  perlu (butir 90–92).
- `[penilaian]` Apakah pemberlakuan surut membebani para pihak atau penerimaan
  negara (butir 106c).

---

## 9.18 Penutup (kaki)

Penutup adalah bagian akhir PMK yang memuat empat unsur berurutan (butir 109a):
rumusan perintah pengundangan dan penempatan dalam Berita Negara;
penandatanganan penetapan; pengundangan; dan akhir bagian penutup. Untuk KMK
empat unsurnya berbeda (butir 109b): rumusan penyampaian KMK; penandatanganan
penetapan; penetapan; dan akhir bagian penutup.

**Perintah pengundangan** hanya terdapat pada PMK, **bukan merupakan bagian dari
pasal di atasnya**, dan **tidak perlu ditempatkan dalam pasal tersendiri**
(butir 110). Bunyinya baku (butir 111):

```
Agar setiap orang mengetahuinya, memerintahkan pengundangan Peraturan Menteri
ini dengan penempatannya dalam Berita Negara Republik Indonesia.
```

**Penandatanganan penetapan** memuat empat hal (butir 112): tempat dan tanggal
penetapan; nama jabatan; tanda tangan pejabat; dan nama lengkap pejabat yang
menandatangani, **tanpa gelar, pangkat, golongan, dan nomor induk pegawai**.
Tempat dan tanggal penetapan diletakkan di **sebelah kanan** (butir 113). Nama
jabatan dan nama pejabat ditulis kapital, dan pada akhir nama jabatan diberi
**tanda baca koma** (butir 114).

```
                              Ditetapkan di Jakarta
                              pada tanggal . . .

                              MENTERI KEUANGAN REPUBLIK INDONESIA,

                                        tanda tangan

                                 SRI MULYANI INDRAWATI
```

Khusus KMK yang ditandatangani Pimpinan Unit Pengusul atau Eselon di bawahnya
untuk dan atas nama Menteri, sebelum nama jabatan diberikan frasa "atas nama"
yang disingkat **"a.n."** (butir 114):

```
                   a.n.  MENTERI KEUANGAN REPUBLIK INDONESIA
                             SEKRETARIS JENDERAL,

                                  tanda tangan

                                 HERU PAMBUDI
```

**Pengundangan** hanya ada pada PMK, memuat empat hal yang sejajar dengan
penandatanganan (butir 115): tempat dan tanggal pengundangan; nama jabatan yang
berwenang mengundangkan; tanda tangan; dan nama lengkap tanpa gelar, pangkat,
golongan, dan NIP. Tempat dan tanggal pengundangan diletakkan di **sebelah kiri,
di bawah penandatanganan penetapan** (butir 116). Nama jabatan dan nama pejabat
ditulis kapital, akhir nama jabatan diberi koma (butir 117).

```
Diundangkan di Jakarta
pada tanggal ....

DIREKTUR JENDERAL
PERATURAN PERUNDANG-UNDANGAN
KEMENTERIAN HUKUM DAN HAK ASASI MANUSIA
REPUBLIK INDONESIA,

tanda tangan

BENNY RIYANTO
```

**Catatan praktik.** Nama pejabat dan nomenklatur kementerian dalam contoh KMK 527
adalah keadaan tahun 2022; nomenklatur "Kementerian Hukum dan Hak Asasi Manusia"
telah berubah sesudahnya. Alat pemeriksa **tidak boleh** memeriksa nama pejabat
atau nama kementerian terhadap contoh dalam KMK 527 — yang diperiksa adalah
strukturnya: ada tempat, tanggal, nama jabatan berkapital diakhiri koma, ruang
tanda tangan, dan nama tanpa gelar.

**Akhir bagian penutup** (butir 118): dicantumkan Berita Negara Republik
Indonesia beserta tahun dan nomornya. Frasa "Berita Negara Republik Indonesia"
ditulis seluruhnya dengan huruf kapital (butir 119).

```
BERITA NEGARA REPUBLIK INDONESIA TAHUN ... NOMOR ...
```

### Pemeriksaan

- `[deterministik]` Rumusan perintah pengundangan cocok persis dengan butir 111.
- `[deterministik]` Perintah pengundangan **tidak** berada di dalam pasal
  (butir 110).
- `[deterministik]` Blok "Ditetapkan di … pada tanggal …" ada dan rata kanan
  (butir 113).
- `[deterministik]` Blok "Diundangkan di … pada tanggal …" ada, rata kiri, dan
  berada **di bawah** blok penetapan (butir 116).
- `[deterministik]` Nama jabatan diakhiri koma (butir 114, butir 117).
- `[deterministik]` Nama pejabat memuat gelar (`S.E.`, `M.M.`, `Dr.`), pangkat,
  atau `NIP` → pelanggaran butir 112d dan butir 115d.
- `[deterministik]` Baris terakhir cocok `BERITA NEGARA REPUBLIK INDONESIA TAHUN
  \S+ NOMOR \S+`, seluruhnya kapital (butir 118, butir 119).
- `[deterministik]` KMK memuat perintah pengundangan atau blok pengundangan →
  keliru; keduanya khusus PMK (butir 110, butir 115).

---

## 9.19 Penjelasan

Butir 2 menempatkan **Penjelasan (jika diperlukan)** sebagai huruf E dalam
kerangka PMK, di antara Penutup dan Lampiran.

**Namun KMK 527 tidak memuat satu pun butir teknis mengenai Penjelasan.** Dalam
Lampiran II angka III, sub-bagian berjalan A. Judul (butir 3–12), B. Pembukaan
(butir 13–39), C. Batang Tubuh (butir 40–108), D. PENUTUP (butir 109–119), lalu
langsung **E. LAMPIRAN** (butir 120–121). Tidak ada sub-bagian untuk Penjelasan,
dan penomoran huruf sub-bagian pun bergeser terhadap butir 2 — Lampiran yang di
butir 2 berhuruf F, di angka III berhuruf E. Hal ini sudah diperiksa terhadap
citra halaman 54–57 naskah asli, jadi bukan kesalahan OCR.

Akibat praktisnya: **bila suatu rancangan PMK memuat Penjelasan, KMK 527 tidak
memberi rujukan teknik untuk memeriksanya.** **Dugaan:** rujukan yang berlaku
dalam keadaan itu adalah Lampiran II UU 12/2011, yang memuat teknik penyusunan
penjelasan peraturan perundang-undangan dan merupakan dasar hukum pertama
KMK 527. Ini perlu dikonfirmasi ke Biro Hukum sebelum dijadikan aturan.

**Catatan praktik.** PMK pada umumnya tidak memuat Penjelasan; keterangan yang
setara biasanya dituangkan dalam Lampiran atau dalam dokumen pendukung seperti
briefing sheet dan lembar analisis dampak (lihat 9.26). Alat pemeriksa sebaiknya
memperlakukan kehadiran Penjelasan sebagai **temuan untuk ditinjau manusia**,
bukan sebagai kesalahan maupun sebagai hal yang wajar.

### Pemeriksaan

- `[deterministik]` Naskah memuat bagian berjudul "PENJELASAN" → tandai sebagai
  hal yang tidak diatur KMK 527, rujuk ke penelaah.
- `[deterministik]` Istilah terdefinisi tetap berkapital di dalam penjelasan bila
  penjelasan ada (butir 67 menyebut penjelasan secara tegas).

---

## 9.20 Lampiran

Bila PMK memerlukan lampiran, hal itu **harus dinyatakan dalam batang tubuh**,
beserta pernyataan bahwa lampiran itu **merupakan bagian yang tidak terpisahkan**
dari Peraturan Menteri Keuangan yang bersangkutan (butir 120). Frasa "merupakan
bagian tidak terpisahkan" itulah yang mengikat lampiran secara hukum ke
peraturannya. Lampiran yang tidak pernah ditunjuk dari pasal mana pun tidak punya
pijakan.

Tiga rumusan yang dicontohkan (butir 120):

```
… sebagaimana tercantum dalam Lampiran … yang merupakan bagian tidak terpisahkan
  dari Peraturan Menteri ini.
… tercantum dalam Lampiran … yang merupakan bagian tidak terpisahkan dari
  Peraturan Menteri ini.
… yang tercantum dalam Lampiran … yang merupakan bagian tidak terpisahkan dari
  Peraturan Menteri ini.
```

**Format lampiran** — sepuluh ketentuan (butir 121):

- **a.** Lampiran diletakkan di halaman berikut sesudah penutup.
- **b.** Kata "LAMPIRAN" ditempatkan di **bagian kanan margin**, seluruhnya
  kapital. Bila lebih dari satu, ditambahkan **angka Romawi** I, II, dan
  seterusnya.
- **c.** Di bawah kata "LAMPIRAN" ditempatkan **judul PMK**, seluruhnya kapital,
  tanpa tanda baca.
- **d.** Di bawah nama PMK ditempatkan **judul/nama Lampiran** di bagian **tengah
  margin**, huruf kapital, tanpa tanda baca.
- **e.** Di bawah judul lampiran ditempatkan materi/isi lampiran.
- **f.** Bila lampiran lebih dari satu halaman, kata "LAMPIRAN" cukup diletakkan
  pada **halaman paling awal** setiap lampiran.
- **g.** Setiap halaman lampiran diberi **nomor halaman** di bagian **tengah atas
  margin** dengan angka Arab.
- **h.** Pada akhir lampiran **harus** dicantumkan **nama dan tanda tangan
  pejabat** yang menetapkan PMK.
- **i.** Penyusunan lampiran **dihindari dalam jumlah lebih dari satu**.
- **j.** Bila terpaksa lebih dari satu, dilakukan **pengelompokan tema/topik**.

```
                                    LAMPIRAN I
                                    PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
                                    NOMOR ... TAHUN ...
                                    TENTANG
                                    (JUDUL PMK, KAPITAL, TANPA TANDA BACA)

                      (JUDUL/NAMA LAMPIRAN DI TENGAH MARGIN)

A. …
   1. …

                          MENTERI KEUANGAN REPUBLIK INDONESIA,

                                 SRI MULYANI INDRAWATI
```

Penomoran internal lampiran memakai huruf atau angka — **bukan "Pasal"**, karena
pasal hanya milik batang tubuh. Nomor halaman lampiran **melanjutkan** nomor
halaman batang tubuh, tidak dimulai dari 1 (butir 132a, dan gambar format pada
halaman 86).

Butir 121i adalah anjuran yang sering diabaikan: KMK 527 secara tegas meminta
jumlah lampiran **dihindari** lebih dari satu. Bila alat menemukan lima lampiran,
itu bukan kesalahan, tetapi layak ditandai.

### Pemeriksaan

- `[deterministik]` Setiap Lampiran N ditunjuk oleh sekurang-kurangnya satu pasal
  di batang tubuh (butir 120).
- `[deterministik]` Kalimat penunjuk memuat frasa `merupakan bagian tidak
  terpisahkan dari Peraturan Menteri ini` (butir 120).
- `[deterministik]` Setiap pasal yang menyebut "Lampiran N" punya lampiran dengan
  nomor itu — dan sebaliknya, tidak ada lampiran yatim (butir 120).
- `[deterministik]` Penomoran lampiran memakai angka Romawi bila lebih dari satu
  (butir 121b).
- `[deterministik]` Kepala lampiran memuat nomor, tahun, dan judul PMK yang sama
  persis dengan judul di halaman pertama (butir 121c).
- `[deterministik]` Akhir setiap lampiran memuat nama jabatan dan nama pejabat
  (butir 121h).
- `[deterministik]` Lampiran memuat kata "Pasal" sebagai penanda satuan → tandai;
  pasal hanya milik batang tubuh (akibat butir 42).
- `[deterministik]` Nomor halaman lampiran melanjutkan batang tubuh (butir 132a).
- `[deterministik]` Jumlah lampiran > 1 → tandai terhadap butir 121i.
- `[penilaian]` Apakah lampiran yang banyak sudah dikelompokkan per tema
  (butir 121j).

---

## 9.21 Perubahan PMK

Perubahan dilakukan dengan **menyisipkan atau menambah** materi ke dalam PMK,
atau **menghapus atau mengganti** sebagian materi PMK (butir 124a).

**Batang tubuh PMK perubahan terdiri atas dua pasal yang ditulis dengan angka
Romawi** (butir 124b):

- **Pasal I** memuat judul peraturan yang diubah atau pasal yang diubah, dan
  memuat **seluruh materi perubahan**.
- **Pasal II** memuat ketentuan tentang **saat mulai berlaku**. Dalam hal
  tertentu, Pasal II juga dapat memuat ketentuan peralihan dari peraturan
  perubahan — yang maksudnya berbeda dengan ketentuan peralihan dari peraturan
  yang diubah.

Bila Pasal II memuat ketentuan peralihan dan/atau penutup dengan materi lebih
dari satu, setiap materi dirinci dengan **angka Arab** (butir 125).

Jika materi perubahan lebih dari satu pasal, setiap urutan perubahan dirinci
dengan angka Arab (butir 124c):

```
                                 Pasal I
Beberapa ketentuan dalam Peraturan Menteri Keuangan Nomor … tentang …
(Berita Negara Republik Indonesia Tahun … Nomor …), diubah sebagai berikut:
1. Ketentuan Pasal 7 diubah sehingga berbunyi sebagai berikut:
                                 Pasal 7
   …
2. Ketentuan Pasal 8 diubah sehingga berbunyi sebagai berikut:
                                 Pasal 8
   …
```

Bila peraturan yang diubah sudah pernah diubah, rangkaian itu **disebut di Pasal
I** (butir 124c Contoh 2) — berbeda dari judul, yang justru dilarang merincinya
(butir 11):

```
Beberapa ketentuan dalam Peraturan Menteri Keuangan Nomor … tentang …
(Berita Negara …) sebagaimana telah diubah dengan Peraturan Menteri Keuangan
Nomor … (Berita Negara …), diubah sebagai berikut:
```

**Penyisipan pasal** (butir 124d): pasal baru dicantumkan di tempat sesuai
materinya; pasal baru yang disisipkan di antara dua pasal ditambah **huruf
kapital** (A, B, C) pada nomornya.

```
Di antara Pasal 1 dan Pasal 2 disisipkan 2 (dua) pasal, yakni Pasal 1A dan
Pasal 1B yang berbunyi sebagai berikut:
```

**Penambahan buku/bab/bagian/paragraf/pasal** (butir 124e) memakai kalimat baku:
`Setelah Bab …/Bagian …/Paragraf …/Pasal … ditambahkan 1 (satu)
buku/bab/bagian/paragraf/pasal, yakni Bab …/Bagian …/Paragraf …/Pasal …
sehingga berbunyi sebagai berikut:`

**Penyisipan ayat** (butir 124f): ayat baru yang bukan pengganti ayat yang
dihapus disisipkan dengan tambahan **huruf abjad kecil** a, b, c yang diletakkan
di dalam tanda kurung bersama nomor ayat.

```
Di antara ayat (1) dan ayat (2) Pasal 18 disisipkan 2 (dua) ayat, yakni ayat (1a)
dan ayat (1b) sehingga Pasal 18 berbunyi sebagai berikut:
```

**Penyisipan bab** (butir 124g): bab baru ditambah **huruf kapital** pada
nomornya — `Di antara BAB IV dan BAB V disisipkan 1 (satu) bab, yakni BAB IVA`.

Perhatikan asimetri penanda sisipan, yang mudah tertukar:

| Yang disisipkan | Penanda | Contoh | Butir |
|---|---|---|---|
| Pasal | huruf **kapital** | `Pasal 1A` | 124d |
| Bab | huruf **kapital** | `BAB IVA` | 124g |
| Ayat | huruf **kecil** dalam kurung | `ayat (1a)` | 124f |

**Penghapusan** (butir 124h): jika dilakukan penghapusan atas suatu bab, bagian,
paragraf, pasal, atau ayat, **urutannya tetap dicantumkan dengan diberi
keterangan dihapus**. Nomor tidak boleh digeser atau dihilangkan.

```
1. Pasal 16 dihapus.
2. Pasal 18 ayat (2) dihapus, sehingga Pasal 18 berbunyi sebagai berikut:
                                Pasal 18
   (1) …
   (2) Dihapus.
```

**Batas perubahan** (butir 127): perubahan PMK **tidak mengubah sistematika** yang
ada. Jika sistematika berubah, atau materi berubah **lebih dari 50%**, atau
**esensinya berubah**, PMK itu **lebih baik dicabut dan disusun kembali** dalam
PMK baru. Ini satu-satunya ambang kuantitatif dalam seluruh Lampiran II, dan
karena itu layak dijadikan indikator otomatis — meski keputusannya tetap di
tangan penelaah.

**Perubahan lampiran** (butir 124i, butir 127b, butir 128, butir 129):

- Bila materi yang diubah pada Lampiran cukup banyak sehingga tidak mungkin
  diubah seluruhnya, **perubahan cukup meliputi materi yang diubah saja**
  (butir 124i).
- Bila yang diubah adalah Lampiran PMK, **nama PMK tetap ditulis "Perubahan Atas
  Peraturan Menteri Keuangan …"**, dan redaksional untuk mengubah lampiran
  dituangkan **dalam Pasal** (butir 127b).
- **Penomoran Lampiran pada PMK perubahan memakai nomor baru** sesuai PMK
  perubahan (butir 128) — Lampiran I, III, VII, IX milik PMK lama menjadi
  Lampiran I, II, III, IV pada PMK perubahan.
- Perubahan Lampiran cukup memuat ketentuan yang diubah, dihapus, dan/atau
  ditambah. **Teknik penyusunan rumusan norma perubahan batang tubuh berlaku
  mutatis mutandis** terhadap perubahan Lampiran (butir 129).

### Pemeriksaan

- `[deterministik]` Judul memuat "PERUBAHAN" → batang tubuh tepat dua pasal
  bernomor Romawi, `Pasal I` dan `Pasal II` (butir 124b). Adanya `Pasal 1`
  berangka Arab pada PMK perubahan adalah kesalahan.
- `[deterministik]` `Pasal II` memuat rumusan saat mulai berlaku (butir 124b-2).
- `[deterministik]` Setiap butir perubahan di Pasal I bernomor angka Arab
  (butir 124c).
- `[deterministik]` Peraturan yang diubah disebut lengkap dengan nomor, judul,
  dan Berita Negara di Pasal I (butir 124c), **dan** hadir di Mengingat
  (butir 27).
- `[deterministik]` Penanda sisipan sesuai jenisnya: pasal/bab huruf kapital,
  ayat huruf kecil dalam kurung (butir 124d, 124f, 124g).
- `[deterministik]` Pasal atau ayat yang dihapus tetap tercantum dengan
  keterangan "Dihapus" dan nomor tidak digeser (butir 124h).
- `[deterministik]` Jumlah pasal yang diubah dibanding jumlah pasal peraturan
  asal > 50% → tandai terhadap butir 127a.
- `[deterministik]` Sistematika bab/bagian/paragraf PMK perubahan berbeda dari
  peraturan asal → tandai terhadap butir 127.
- `[deterministik]` Penomoran lampiran pada PMK perubahan dimulai dari I secara
  berurut, tidak meniru nomor lampiran lama (butir 128).
- `[penilaian]` Apakah esensi peraturan berubah sehingga sebaiknya dicabut dan
  disusun ulang (butir 127a).
- `[penilaian]` Apakah matriks persandingan konsisten dengan Pasal I — bandingkan
  teks lama dan baru pasal demi pasal.

---

## 9.22 Pencabutan PMK

**Siapa yang boleh mencabut** (butir 130a–b, butir 108): PMK hanya dapat dicabut
dengan peraturan perundang-undangan yang tingkatannya **sama atau lebih tinggi**;
KMK dicabut dengan peraturan atau keputusan yang tingkatannya sama atau lebih
tinggi. Peraturan Pimpinan Unit Organisasi Eselon I **tidak dapat mencabut PMK**
(butir 130i).

Pencabutan PMK dengan peraturan yang lebih tinggi dilakukan **jika peraturan
lebih tinggi itu dimaksudkan menampung kembali** seluruh atau sebagian materi PMK
yang dicabut (butir 130c).

**Kewajiban mencabut secara tegas** (butir 130e, 130g): jika ada PMK yang tidak
diperlukan lagi dan diganti dengan PMK baru, PMK baru **harus secara tegas
mencabut** PMK itu. Jika materinya sudah ditampung kembali dalam peraturan yang
lebih tinggi, peraturan yang lebih tinggi itu yang harus secara tegas mencabut.

**Letak rumusan** (butir 130j): jika PMK baru mengatur kembali materi yang sudah
diatur dan diberlakukan, pencabutan dinyatakan dalam **salah satu pasal dalam
ketentuan penutup** PMK baru, dengan rumusan `dicabut dan dinyatakan tidak
berlaku`.

**Pencabutan dengan PMK tersendiri** (butir 130l, 130m). Pencabutan PMK yang
sudah diundangkan tetapi **belum mulai berlaku** dapat dilakukan dengan PMK
tersendiri, dengan rumusan `ditarik kembali dan dinyatakan tidak berlaku`. PMK
pencabutan tersendiri pada dasarnya memuat **dua pasal yang ditulis dengan angka
Arab**:

```
                                Pasal 1
Peraturan Menteri Keuangan Nomor … tentang … dicabut dan dinyatakan tidak
berlaku.

                                Pasal 2
Peraturan Menteri Keuangan ini mulai berlaku pada tanggal diundangkan.
```

Bandingkan dengan PMK perubahan yang memakai **angka Romawi** (butir 124b).
Pasangan ini adalah pembeda paling bersih antara dua jenis PMK dan sangat layak
dijadikan aturan otomatis:

| Jenis PMK | Penomoran batang tubuh | Butir |
|---|---|---|
| PMK perubahan | `Pasal I`, `Pasal II` — Romawi | 124b |
| PMK pencabutan tersendiri | `Pasal 1`, `Pasal 2` — Arab | 130m |

**Dua akibat hukum yang wajib diketahui alat** (butir 130n, 130o):

- Pencabutan PMK yang menimbulkan perubahan dalam PMK lain yang terkait **tidak
  mengubah** PMK lain tersebut, kecuali ditentukan lain secara tegas.
- PMK atau ketentuan yang telah dicabut **tetap tidak berlaku kembali**, meskipun
  PMK yang mencabutnya di kemudian hari dicabut pula. Tidak ada kebangkitan
  otomatis.

### Pemeriksaan

- `[deterministik]` Judul memuat "PENCABUTAN" → batang tubuh dua pasal berangka
  Arab (butir 130m).
- `[deterministik]` Rumusan pencabutan memakai frasa baku yang sesuai status
  peraturan sasaran (butir 96, butir 99, butir 130l).
- `[deterministik]` Peraturan yang dicabut **tidak** dicantumkan dalam Mengingat
  (butir 28a).
- `[deterministik]` Naskah Peraturan Pimpinan Unit Eselon I mencabut PMK →
  pelanggaran butir 130i.
- `[penilaian]` Apakah materi PMK lama benar-benar ditampung kembali dalam
  peraturan yang mencabut (butir 130c).
- `[penilaian]` Apakah ada PMK lama sebidang yang seharusnya dicabut tetapi tidak
  disebut (butir 130e) — **pencarian korpus**.

---

## 9.23 Pendelegasian kewenangan

Pendelegasian kewenangan pengaturan kepada Peraturan Pimpinan Unit Organisasi
Eselon I **hanya dimungkinkan untuk hal yang bersifat sangat teknis
administratif**, dan **sepanjang diamanatkan** peraturan yang lebih tinggi
(butir 123a).

Pendelegasian **harus menyebutkan secara tegas** ruang lingkup materi dan jenis
peraturan pelaksanaannya (butir 123b):

```
Ketentuan lebih lanjut mengenai … (materi yang akan diatur lebih lanjut) diatur
dengan Peraturan Direktur Jenderal …
```

**Tidak boleh ada delegasi blangko** (butir 123c). Contoh yang dilarang, dikutip
langsung:

```
✗ Hal-hal yang belum cukup diatur dalam Peraturan Menteri ini, diatur lebih
  lanjut dengan Peraturan Direktur Jenderal …
```

Ini rumusan yang sangat lazim di lapangan dan sangat mudah ditangkap mesin —
ciri khasnya adalah objek delegasi yang tidak tertentu ("hal-hal yang belum cukup
diatur", "hal-hal lain", "hal teknis lainnya").

Peraturan pelaksanaan **tidak mengulangi** ketentuan norma yang telah diatur di
dalam peraturan yang mendelegasikan, kecuali jika hal itu memang tidak dapat
dihindari (butir 123d), dan **tidak mengutip kembali** rumusan norma peraturan
yang lebih tinggi yang mendelegasikan — pengutipan hanya boleh sepanjang
diperlukan sebagai **pengantar (aanloop)** untuk merumuskan norma lebih lanjut
(butir 123e).

**Dua rumusan delegasi yang berbeda maknanya** (butir 123f, butir 123g):

| Keadaan | Rumusan | Butir |
|---|---|---|
| Beberapa materi tersebar di beberapa pasal atau ayat, didelegasikan dalam satu peraturan | `Ketentuan mengenai … diatur dalam ….` | 123f |
| Pokoknya sudah diatur, materi hanya boleh diatur dalam peraturan yang didelegasikan, **tidak boleh disubdelegasikan** lebih rendah | `Ketentuan lebih lanjut mengenai … diatur dengan ….` | 123g |

Jadi `diatur dalam` dan `diatur dengan` bukan variasi gaya; keduanya membawa
akibat hukum berbeda mengenai boleh atau tidaknya subdelegasi.

### Pemeriksaan

- `[deterministik]` Naskah memuat pola `[Hh]al-hal yang belum cukup diatur` atau
  `[Hh]al-hal lain .{0,40} diatur (lebih lanjut )?(dengan|dalam)` → delegasi
  blangko, pelanggaran butir 123c.
- `[deterministik]` Kalimat delegasi menyebut jenis peraturan pelaksana secara
  tegas (butir 123b); "diatur lebih lanjut kemudian" tanpa jenis → pelanggaran.
- `[deterministik]` Pemakaian `diatur dengan` vs `diatur dalam` — tandai untuk
  dicocokkan dengan maksudnya (butir 123f, 123g).
- `[penilaian]` Apakah materi yang didelegasikan benar-benar bersifat sangat
  teknis administratif (butir 123a).
- `[penilaian]` Apakah ada pengulangan norma dari peraturan yang mendelegasikan
  (butir 123d, 123e) — **pencarian korpus**.

---

## 9.24 Format fisik naskah

Ketentuan ini berada di **Lampiran III huruf A angka IX beserta keterangannya**
(halaman 86–87), bukan di Lampiran II, tetapi mengikat naskah PMK, KMK, serta
Peraturan dan Keputusan Pimpinan Unit Organisasi Eselon I.

| Unsur | Nilai |
|---|---|
| Jenis huruf | **Bookman Old Style** |
| Ukuran huruf | **12** |
| Jenis kertas | **F4** |
| Lebar kertas | **21 sentimeter** |
| Panjang kertas | **33 sentimeter** |
| Marjin atas — halaman 1 PMK dan KMK | **8 sentimeter** |
| Marjin atas — halaman 1 Peraturan/Keputusan Pimpinan Unit Eselon I | **4 sentimeter** |
| Marjin atas — halaman 2 dan seterusnya | **2,5 sentimeter** |
| Marjin bawah | **2,5 sentimeter** |
| Marjin kiri | **2,5 sentimeter** |
| Marjin kanan | **2,5 sentimeter** |
| Line spacing | **1** |
| Spacing before | **0 pt** |
| Spacing after | **0 pt** |

Marjin atas 8 sentimeter pada halaman pertama itulah yang memberi ruang bagi
lambang Garuda dan dua baris nama jabatan (butir 1).

**Nomor halaman** (angka 2 keterangan Lampiran III): halaman 2 dan seterusnya
dicantumkan di **bagian atas tengah**, **didahului dan diakhiri tanda baca
hubung**, serta diberi jarak satu spasi — bentuknya `- 4 -`. Halaman pertama
**tidak** diberi nomor (butir 132a).

Format Lampiran PMK berlaku **mutatis mutandis** untuk format lampiran pada KMK
dan pada peraturan/keputusan pimpinan unit (angka 3 keterangan Lampiran III).

Seluruh angka di atas dapat diperiksa langsung dari berkas .docx tanpa membaca
isinya — bagian paling murah dari seluruh pemeriksaan, dan bagian yang paling
sering salah karena penyalinan dari dokumen lain membawa serta gaya asalnya.

### 9.24.1 Jarak antarblok — satuan enter

Diambil dari bagan tata letak Lampiran III huruf A angka I–VIII (halaman 74–85).
Kedelapan bagan memakai pola yang **sama persis**, sehingga angka di bawah ini
berlaku untuk PMK, KMK, dan peraturan/keputusan pimpinan unit.

**Pembukaan — halaman pertama:**

| Dari | Ke | Jarak |
|---|---|---|
| Baris terakhir judul | `DENGAN RAHMAT TUHAN YANG MAHA ESA` (PMK) | **1 enter** |
| `DENGAN RAHMAT…` | nama jabatan pembentuk | **1 enter** |
| Baris terakhir judul | nama jabatan pembentuk (KMK — tanpa Dengan Rahmat) | **1 enter** |
| Nama jabatan pembentuk | `Menimbang` | **2 enter** |
| Butir terakhir Menimbang | `Mengingat` | **1 enter** |
| Angka terakhir Mengingat | `MEMUTUSKAN:` | **1 enter** |
| `MEMUTUSKAN:` | `Menetapkan` | **1 enter** |
| `Menetapkan` | `BAB I` / diktum `KESATU` | **1 enter** |

**Batang tubuh:**

| Dari | Ke | Jarak |
|---|---|---|
| Akhir isi satu blok | `BAB …` berikutnya | **1 enter** |
| `BAB …` | judul bab | **tanpa enter** — baris berikutnya |
| Judul bab | `Bagian Kesatu` | **1 enter** |
| `Bagian …` | judul bagian | **tanpa enter** |
| Judul bagian | `Paragraf 1` | **1 enter** |
| `Paragraf …` | judul paragraf | **tanpa enter** |
| Judul paragraf | `Pasal …` | **1 enter** |
| `Pasal …` | teks pasal / ayat (1) | **tanpa enter** |
| Akhir isi pasal | `Pasal …` berikutnya | **1 enter** |

**Penutup:**

| Dari | Ke | Jarak |
|---|---|---|
| Perintah pengundangan (PMK) atau isi diktum terakhir (KMK) | `Ditetapkan di …` | **2 enter** |
| `pada tanggal …` | nama jabatan penanda tangan | **1 enter** |
| Nama jabatan | nama pejabat (ruang tanda tangan) | **3 enter** |
| Nama pejabat penetapan | `Diundangkan di …` (PMK) | **1 enter** |
| `pada tanggal …` pengundangan | nama jabatan pengundang | **1 enter** |
| Nama jabatan pengundang | nama pejabat | **3 enter** |
| Nama pejabat pengundang | `BERITA NEGARA REPUBLIK INDONESIA TAHUN … NOMOR …` | **2 enter** |
| Rumusan saat mulai berlaku (KMK) | `Keputusan Menteri ini disampaikan kepada:` | **1 enter** |

**Indentasi:**

- **0,5 cm** — jarak antara label `Menimbang` / `Mengingat` / `Menetapkan` dan
  tanda titik dua beserta isinya. Tampak konsisten di seluruh delapan bagan.
- **1 cm** — pertambahan indentasi **setiap turun satu tingkat** pada rincian
  bertabulasi. Tangga `a.` → `1.` → `a)` → `1)` masing-masing masuk 1 cm dari
  tingkat di atasnya (bagan halaman 75, 77, 79, 81, 82). Angka ini juga dipakai
  untuk baris lanjutan butir Menimbang yang lebih dari satu baris.

**Posisi horizontal — diukur dari margin kiri** (bagan halaman 74 dan 83,
resolusi penuh). Keempat penanda saling mengunci dan membentuk satu susunan yang
utuh:

| Penanda | Menandai | Nilai dari margin kiri |
|---|---|---|
| `0,5 cm` | jarak dari akhir label `Menimbang` / `Menetapkan` ke isinya | — |
| `3 cm` | kolom huruf abjad butir Menimbang — `a.` `b.` `c.` | **3 cm** |
| `1 cm` | jarak dari huruf abjad ke teks butirnya | **4 cm** (3 + 1) |
| `3,5 cm` | baris lanjutan butir Menimbang, **dan** seluruh paragraf badan | **3,5 cm** |

Jadi butir Menimbang memakai indentasi menggantung yang tidak lazim: penanda
huruf menjorok keluar ke 3 cm, teks baris pertama mulai di 4 cm, dan baris
lanjutannya turun ke 3,5 cm. Angka 3,5 cm itu bukan angka khusus konsiderans —
ia posisi yang sama dengan paragraf badan mana pun. Dua contoh pada bagan
memperlihatkannya: `Dalam Peraturan Menteri ini yang dimaksud dengan:` (halaman
74) dan `Peraturan Direktur Jenderal ini mulai berlaku pada tanggal ditetapkan.`
(halaman 83), keduanya ditunjuk penanda 3,5 cm.

**Ringkasnya:** teks badan pasal dan frasa pembuka Ketentuan Umum mulai di
**3,5 cm** dari margin kiri; label pembukaan (`Menimbang`, `Mengingat`,
`Menetapkan`) mulai di margin kiri; isinya berjarak **0,5 cm** dari akhir label;
kolom huruf abjad rincian konsiderans di **3 cm**; dan setiap turun satu tingkat
pada rincian bertabulasi menambah **1 cm**.

**Catatan.** Susunan menggantung 3 → 4 → 3,5 cm itu terbaca jelas pada bagan,
tetapi jarang ditemui pada tata naskah pada umumnya. Sebelum dijadikan aturan
keras di alat pemeriksa, sebaiknya dicocokkan sekali dengan satu berkas .docx PMK
asli — bukan karena bagannya meragukan, melainkan karena praktik penulisan di
lapangan bisa saja sudah menyederhanakannya.

**Perbedaan pemrosesan elektronik dan selain elektronik.** Bagan angka II dan IV
(elektronik) memakai `Keputusan Menteri ini disampaikan kepada:`, sedangkan
bagan angka III dan V (selain elektronik) memakai `Salinan Keputusan Menteri ini
disampaikan kepada:`. Hanya kata "Salinan" yang membedakan keduanya; selebihnya
identik. Ini sejalan dengan butir 131 yang memang hanya berlaku untuk pemrosesan
selain elektronik.

### Pemeriksaan

- `[deterministik]` Seluruh run memakai Bookman Old Style ukuran 12.
- `[deterministik]` Ukuran halaman 21 × 33 cm.
- `[deterministik]` Marjin section pertama: atas 8 cm; section berikutnya 2,5 cm;
  bawah/kiri/kanan 2,5 cm.
- `[deterministik]` Line spacing 1, spacing before dan after 0 pt.
- `[deterministik]` Header halaman ≥ 2 cocok pola `-\s*\d+\s*-` dan berada di
  tengah.
- `[deterministik]` Halaman 1 tanpa nomor halaman (butir 132a).

---

## 9.25 Salinan dan penomoran halaman

**Salinan** (butir 131). Dalam hal peraturan diproses secara selain elektronik,
PMK, KMK, dan Keputusan a.n. Menteri Keuangan **hanya boleh beredar jika
salinannya telah disahkan** oleh pimpinan unit atau pejabat yang diberi wewenang
mengesahkan (butir 131a). Bentuk pengesahan:

```
Salinan sesuai dengan aslinya,
Kepala Biro Umum
       u.b.
Kepala Bagian Administrasi Kementerian

tanda tangan dan cap dinas

NAMA (tanpa gelar, pangkat, dan NIP)
```

Huruf awal kata "salinan" pada penyampaian salinan KMK dan Keputusan a.n. Menteri
ditulis kapital, diakhiri **titik dua**, dan **tidak menggunakan frasa "yang
terhormat" yang disingkat "Yth."** (butir 131b):

```
Salinan Keputusan Menteri ini disampaikan kepada:
```

Salinan KMK dan Keputusan Pimpinan Unit Organisasi Eselon I **hanya disampaikan
kepada pejabat yang terkait dengan substansi** (butir 131c). Salinan diberi cap
dinas sesuai ketentuan (butir 131d).

**Penomoran halaman** (butir 132). PMK dan KMK **harus** diberi nomor halaman
pada setiap lembar dengan angka Arab di **tengah atas**, **kecuali halaman
pertama** yang tidak diberi nomor. Setiap lampiran diberi nomor halaman dengan
**melanjutkan** nomor halaman batang tubuh.

### Pemeriksaan

- `[deterministik]` Blok salinan memuat frasa "Salinan sesuai dengan aslinya,"
  (butir 131a).
- `[deterministik]` Nama pengesah tanpa gelar, pangkat, atau NIP (butir 131a).
- `[deterministik]` Daftar penyampaian salinan memuat "Yth." → pelanggaran
  butir 131b.
- `[deterministik]` Nomor halaman lampiran melanjutkan batang tubuh, tidak
  mengulang dari 1 (butir 132).

---

## 9.26 Daftar periksa penelaahan rancangan PMK

Lampiran III huruf E KMK 527 memuat **dua** daftar periksa resmi, bukan satu —
diverifikasi terhadap citra halaman 25 Sep 2026:

| | Untuk | Halaman |
|---|---|---|
| Daftar I | rancangan **PMK** | 92–94 |
| Daftar II | rancangan **KMK** | 95–97 |

Isinya berpasangan: Syarat Administratif dan Syarat Substantif dengan butir yang
sebagian besar sama. Yang diuraikan di bawah ini daftar **PMK**; daftar KMK
berbeda pada beberapa syarat administratif (satu rangkap, bukan dua) tetapi
**Syarat Substantif 2a dan 2b berbunyi sama persis**, jadi dasar pemeriksaan
Drafter Analiser berlaku untuk kedua jenis naskah.

Ini bukan teknik penulisan, tetapi ia adalah **bentuk telaah yang sudah
dipakai**, dan karena itu acuan paling langsung untuk keluaran Drafter Analiser.

**1. Syarat Administratif**

- a. Dua rangkap naskah asli yang telah disetujui Pimpinan Unit Eselon
  II/setingkat pada setiap halaman, dan oleh Pimpinan Unit Pengusul pada kolom
  tanda tangan Menteri.
- b. Telah disusun sesuai format dalam Lampiran KMK mengenai pedoman penyusunan
  jo. Peraturan Menteri Hukum dan HAM mengenai pengundangan. — **Inilah butir
  yang diperiksa alat ini.**
- c. Salinan digital dalam format `.docx` atau format standar lain.
- d. Penjelasan singkat (briefing sheet) dan bahan tayang, memuat sekurangnya
  latar belakang/maksud dan tujuan, dasar hukum, tahapan pemrosesan, pokok materi
  muatan, dan pendapat/rekomendasi.
- e. Untuk rancangan yang bersifat perubahan: PMK/KMK yang akan diubah, **dan
  matriks persandingan** antara peraturan lama dengan rancangan.
- f. Surat keterangan telah dilakukan pengharmonisasian, pembulatan, dan
  pemantapan konsepsi dari Kementerian Hukum.
- g. Konsep dokumen strategi komunikasi.
- h. Surat persetujuan Presiden bagi rancangan yang berdampak luas, bersifat
  strategis, atau lintas sektor/lintas Kementerian.
- i. Surat keterangan telah dilakukan penyelarasan, ditandatangani Pimpinan Unit
  Pengusul.
- j. Lembar analisis dampak dan kesesuaian dengan peraturan perundang-undangan
  dan putusan pengadilan.

**2. Syarat Substantif**

- a. Rancangan disusun berdasarkan kewenangan Menteri Keuangan atau pelimpahan
  kewenangan peraturan yang lebih tinggi dan/atau setara.
- b. Rancangan **tidak bertentangan dengan peraturan yang lebih tinggi**.
- c. Rancangan dengan kriteria berdampak luas/strategis/lintas sektor telah
  mendapat persetujuan Presiden sebelum ditetapkan.
- d. Materi muatan telah dibahas dan disepakati dengan unit/instansi terkait,
  dituangkan dalam matriks Unit Terkait × Pasal Rancangan × Peraturan Terkait.
- e. Materi yang bersifat strategis/sensitif dituangkan dalam Nota Dinas.

**3. Program Perencanaan** — apakah termasuk Program Perencanaan tahun berjalan
(Prioritas Tahunan), Kumulatif Terbuka, atau di Luar Program Perencanaan yang
memerlukan izin/persetujuan prinsip Menteri lebih dahulu.

**Lembar analisis dampak** (Lampiran III huruf C, halaman 89–90) berkolom: Latar
Belakang Pembentukan, Analisis Dampak, Analisis dengan Peraturan yang Lebih
Tinggi, Analisis dengan Peraturan yang Setingkat, dan Analisis dengan Putusan
Pengadilan. Analisis dampak mengkaji lima hal: tidak menghambat pelayanan publik;
mendukung iklim usaha dan investasi; mendorong pertumbuhan ekonomi; tidak
melanggar hak warga negara; dan perizinan tidak berbelit-belit. Ditegaskan pula
bahwa analisis terhadap peraturan yang lebih tinggi dan yang setingkat **tidak
sebatas** pada peraturan yang mengamanatkan penyusunan rancangan.

**Catatan rancang bangun.** Syarat 1b, 2a, dan 2b adalah tiga tempat Drafter
Analiser masuk. Syarat 1b sepenuhnya deterministik — itulah seluruh isi dokumen
ini. Syarat 2a bersandar pada Menimbang dan Mengingat (9.6 dan 9.7). Syarat 2b,
dan butir "tidak sebatas pada peraturan yang mengamanatkan", adalah pekerjaan
pencarian korpus yang tidak mungkin dituntaskan manual — di sanalah OpenSearch
dan model bahasa memberi nilai yang tidak bisa diberikan aturan biasa.

---

## 9.27 Peraturan dan Keputusan Pimpinan Unit Organisasi Eselon I

Kerangka dan isinya **sama dengan PMK dan KMK**, dengan lima pengecualian
(butir 122):

- **a. Kop.** Memakai kertas dengan kop frasa "Kementerian Keuangan Republik
  Indonesia" di tengah margin, seluruhnya kapital, tanpa tanda baca — bukan
  lambang Garuda dengan "MENTERI KEUANGAN".
- **b. Judul.** Di bawah kop terdapat nama Unit Organisasi Eselon I pengusul, lalu
  jenis peraturan, lalu nomor beserta **nomor kodering pengusul** dan tahun
  penetapan, lalu kata "TENTANG" di tengah margin tanpa spasi, lalu nama
  peraturan dengan huruf kapital tanpa tanda baca.
- **c. Pembukaan.** Jabatan pembentuk ditulis sesuai nama jabatan Pimpinan Unit
  Organisasi Eselon I yang bersangkutan, seluruhnya kapital.
- **d. Isi.** Pada dasarnya **hanya memuat aturan teknis**, antara lain prosedur
  pelaksanaan tugas dan format/bentuk surat atau dokumen lain.
- **e. Penutup.** Jabatan pembentuk ditulis sesuai nama jabatan unit yang
  bersangkutan, seluruhnya kapital, **tanpa akronim**, diakhiri koma.

Perhatikan perbedaan penomoran: judul peraturan pimpinan unit memuat **nomor
kodering pengusul**, sedangkan judul PMK justru dilarang memuat huruf dan tanda
baca dalam nomornya (butir 5). Keduanya tidak bertentangan karena berlaku pada
jenis naskah yang berbeda.

**Dua hal tambahan dari bagan Lampiran III angka VI–VIII** (halaman 83–85), yang
tidak dinyatakan dalam butir 122 tetapi terbaca jelas dari tata letaknya:

- Peraturan dan Keputusan Pimpinan Unit Organisasi Eselon I **mulai berlaku pada
  tanggal ditetapkan**, bukan pada tanggal diundangkan — `Peraturan Direktur
  Jenderal ini mulai berlaku pada tanggal ditetapkan.`
- Keduanya **tidak memiliki blok pengundangan maupun perintah pengundangan**.
  Bagian penutupnya berhenti pada `Ditetapkan di …`, nama jabatan, tanda tangan,
  dan nama pejabat. Konsisten dengan butir 110 dan butir 115 yang membatasi
  pengundangan hanya pada PMK.
- Nama pejabat ditulis `NAMA (tanpa mencantumkan gelar, pangkat, dan/atau nomor
  induk pegawai)` — sejalan dengan butir 112d.

---

## 9.28 Ketidakselarasan dan kekosongan dalam KMK 527

Dicatat apa adanya agar alat tidak memaksakan aturan yang memang tidak ada.

1. **Penjelasan tidak punya teknik.** Butir 2 mencantumkan Penjelasan sebagai
   huruf E kerangka, tetapi angka III tidak memuat sub-bagian maupun butir untuk
   Penjelasan. Sudah diverifikasi terhadap citra halaman 54–57.
2. **Pergeseran huruf sub-bagian.** Lampiran di butir 2 berhuruf **F**, tetapi
   sub-bagian teknisnya berhuruf **E** (halaman 57). Penomoran huruf pada angka
   III tidak konsisten dengan butir 2.
3. **Format nomor.** Butir 5 melarang huruf dan tanda baca dalam penomoran,
   sedangkan KMK 527 sendiri bernomor 527/KMK.01/2022 dan seluruh contoh di
   dalamnya memakai format lama. Korpus peraturan yang berlaku karena itu memuat
   dua format sekaligus.
4. **Nomenklatur usang.** Contoh pengundangan menyebut "Kementerian Hukum dan Hak
   Asasi Manusia" dan nama pejabat tahun 2022. Struktur yang diperiksa, bukan
   namanya.
5. **Butir 44 dan butir 75 tumpang tindih.** Keduanya mengatur penempatan sanksi
   administratif dengan rumusan yang hampir sama; butir 44 berada di bagian umum
   batang tubuh, butir 75 di sub-bagian sanksi. Tidak bertentangan, tetapi bila
   dikutip sebagai rujukan temuan, sebut keduanya.
6. **Jumlah dasar hukum tidak dibatasi.** Tidak ada butir yang mensyaratkan
   jumlah minimum dasar hukum; yang ada hanya syarat isi (butir 24–25). Alat
   tidak boleh menuntut "minimal dua".
7. **Preposisi acuan tidak dibakukan.** Pola "dalam Pasal" dan "pada ayat"
   konsisten di seluruh contoh, tetapi tidak dirumuskan sebagai kaidah. Perlakukan
   sebagai peringatan lunak.
8. **Ambang 50% tidak dijelaskan cara hitungnya** (butir 127a). Tidak dinyatakan
   apakah dihitung dari jumlah pasal, jumlah kata, atau bobot materi. Alat harus
   menyatakan dasar hitungnya secara terbuka agar penelaah dapat menilai sendiri.
9. **Dasar hukum yang SUDAH DICABUT tidak dilarang di mana pun.** Butir 28 dan 29
   hanya melarang mencantumkan peraturan yang **belum berlaku** — butir 28a untuk
   peraturan yang justru akan dicabut oleh rancangan ini, butir 28b untuk KMK yang
   sudah ditetapkan tetapi belum berlaku, dan butir 29 untuk peraturan yang sudah
   diundangkan tetapi belum berlaku. Tidak satu butir pun berbicara tentang
   peraturan yang sudah dicabut. Diverifikasi terhadap citra halaman 36,
   25 Sep 2026.

   Larangannya berdiri di atas asas umum, bukan di atas KMK 527. Alat tetap
   memeriksanya (F3-002) tetapi tidak boleh mengaku butir 29 sebagai dasarnya.
10. **Tidak ada butir tentang subjek norma maupun benturan kata operasional.**
    Dicari 25 Sep 2026 di seluruh Lampiran II: tidak ada butir yang mewajibkan
    norma menyebut siapa pemikulnya, dan tidak ada yang mengatur benturan
    wajib/harus/dapat/dilarang di dalam satu ketentuan. Butir 54g hanya menuntut
    satu ayat memuat satu norma dalam satu kalimat utuh. Dua pemeriksaan Drafter
    Analiser (F2-102 dan F2-103) karena itu berjalan **tanpa dasar KMK 527**, dan
    mengaku begitu di panel.

---

## 9.29 Kelengkapan sumber

Seluruh bagan tata letak Lampiran III huruf A angka I–VIII (halaman 74–85) sudah
dibaca dari tangkapan layar resolusi penuh, termasuk halaman 74 dan 83 dalam
versi jernih; hasilnya masuk ke bagian 9.24.1 dan 9.27. Tidak ada lagi bagian
sumber yang tidak terbaca.

| Hal | Status | Tindakan |
|---|---|---|
| Jarak antarblok dalam satuan enter, delapan format | **pasti** | 9.24.1 |
| Indentasi 0,5 cm pada label dan 1 cm per tingkat rincian | **pasti** | 9.24.1 |
| Marjin, ukuran kertas, huruf, spasi, nomor halaman | **pasti** | 9.24 |
| Posisi horizontal 0,5 / 3 / 1 / 3,5 cm pada bagan halaman 74 dan 83 | **pasti** — terbaca dari tangkapan layar resolusi penuh | 9.24.1 |
| Apakah praktik di lapangan masih memakai susunan menggantung 3 → 4 → 3,5 cm | belum diuji | cocokkan sekali dengan satu .docx PMK asli |

## Lampiran A — Indeks butir 1–132

| Butir | Pokok | Bagian |
|---|---|---|
| 1 | Kepala halaman: Garuda, MENTERI KEUANGAN / REPUBLIK INDONESIA | 9.1 |
| 2 | Kerangka A–F | peta |
| 3–4 | Kewajiban judul dan unsurnya | 9.2 |
| 5 | Penomoran angka Arab + tahun | 9.2.1 |
| 6 | Kata TENTANG | 9.2 |
| 7 | Nama singkat dan mencerminkan isi | 9.2.2 |
| 8 | Judul kapital, tanpa tanda baca, larangan akronim | 9.2, 9.2.2 |
| 9–11 | Judul peraturan perubahan | 9.2.3 |
| 12 | Judul peraturan pencabutan | 9.2.4 |
| 13 | Unsur pembukaan | 9.3 |
| 14 | Frasa Dengan Rahmat (khusus PMK) | 9.4 |
| 15 | Jabatan pembentuk | 9.5 |
| 16–18 | Bentuk dan isi konsiderans | 9.6 |
| 19 | Konsiderans PMK pelaksanaan peraturan lebih tinggi | 9.6 |
| 20 | Konsiderans PMK kewenangan sendiri / perubahan / pencabutan | 9.6 |
| 21 | Huruf abjad, kata "bahwa", titik koma | 9.6 |
| 22 | Rumusan butir pertimbangan terakhir | 9.6 |
| 23 | Kata "Mengingat" | 9.7 |
| 24–25 | Isi dasar hukum dan dasar kewenangan | 9.7 |
| 26 | Batas tingkatan peraturan | 9.7 |
| 27 | PMK yang diubah wajib dicantumkan | 9.7 |
| 28–29 | Yang tidak dicantumkan | 9.7 |
| 30 | Urutan hierarki dan kronologis | 9.7 |
| 31–33 | Angka Arab, kapitalisasi judul, Undang-Undang | 9.7 |
| 34–35 | Lembaran Negara / Berita Negara | 9.7 |
| 36 | Diktum Memperhatikan (khusus KMK) | 9.7 |
| 37–39 | MEMUTUSKAN, Menetapkan, jenis dan nama | 9.8 |
| 40–41 | Isi dan pengelompokan batang tubuh | 9.9 |
| 42 | Pasal untuk PMK, diktum untuk KMK | 9.9 |
| 43 | Ketentuan lain-lain | 9.9 |
| 44–45 | Letak sanksi administratif | 9.15 |
| 46–50 | Bab, bagian, paragraf, dan empat susunan | 9.10 |
| 51–53 | Penomoran bab, bagian, paragraf | 9.10 |
| 54a–j | Pasal dan ayat | 9.11 |
| 54k–o | Tabulasi dan konjungsi | 9.12 |
| 55 | Diktum dalam KMK | 9.0 |
| 56–58 | Letak dan isi Ketentuan Umum | 9.13 |
| 59–60 | Frasa pembuka dan penomoran definisi | 9.13 |
| 61, 64 | Istilah berulang dan pengecualiannya | 9.13 |
| 62–63, 65 | Konsistensi rumusan definisi | 9.13 |
| 66 | Definisi tidak diberi penjelasan | 9.13 |
| 67 | Kapitalisasi istilah terdefinisi | 9.13 |
| 68–69 | Urutan penempatan definisi | 9.13 |
| 70–73 | Materi pokok yang diatur | 9.14 |
| 74–78 | Sanksi administratif dan keperdataan | 9.15 |
| 79–85 | Ketentuan Peralihan | 9.16 |
| 86–88 | Letak, isi, penunjukan organ | 9.17, 9.17.1 |
| 89–92 | Nama singkat | 9.17.2 |
| 93–99 | Pencabutan dalam ketentuan penutup | 9.17.3 |
| 100–107 | Saat mulai berlaku dan berlaku surut | 9.17.4 |
| 108 | PMK dicabut dengan apa | 9.17.4 |
| 109–111 | Unsur penutup dan perintah pengundangan | 9.18 |
| 112–114 | Penandatanganan penetapan | 9.18 |
| 115–117 | Pengundangan | 9.18 |
| 118–119 | Berita Negara | 9.18 |
| 120–121 | Lampiran | 9.20 |
| 122 | Peraturan/Keputusan Pimpinan Unit Eselon I | 9.27 |
| 123 | Pendelegasian kewenangan | 9.23 |
| 124–125 | Perubahan PMK | 9.21 |
| 126 | Perubahan KMK | 9.21 |
| 127–129 | Batas perubahan dan perubahan Lampiran | 9.21 |
| 130 | Pencabutan | 9.22 |
| 131 | Salinan | 9.25 |
| 132 | Penomoran halaman | 9.25 |

---

## Lampiran B — Daftar rumusan baku

Kumpulan string yang bentuknya ditentukan KMK 527 dan karena itu dapat dicocokkan
langsung. `…` menandai bagian yang berubah-ubah.

| Rumusan | Letak | Butir |
|---|---|---|
| `DENGAN RAHMAT TUHAN YANG MAHA ESA` | pembukaan PMK | 14 |
| `MENTERI KEUANGAN REPUBLIK INDONESIA,` | jabatan pembentuk | 15 |
| `bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf …, perlu menetapkan Peraturan Menteri Keuangan tentang …;` | Menimbang butir terakhir | 22a |
| `bahwa untuk melaksanakan ketentuan Pasal … , perlu menetapkan Peraturan Menteri Keuangan tentang …;` | Menimbang PMK pelaksanaan | 19 |
| `MEMUTUSKAN:` | diktum | 37 |
| `Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG … .` | diktum | 39 |
| `Dalam Peraturan Menteri ini yang dimaksud dengan:` | Pasal 1 | 59 |
| `… yang selanjutnya disingkat … adalah …` | definisi bersingkatan | 58b |
| `sebagaimana dimaksud dalam Pasal …` | acuan pasal | 54d |
| `sebagaimana dimaksud pada ayat (…)` | acuan ayat | 54h |
| `… (…)` — angka diikuti kata dalam kurung | bilangan | 54j |
| `Ketentuan lebih lanjut mengenai … diatur dengan ….` | delegasi tanpa subdelegasi | 123g |
| `Ketentuan mengenai … diatur dalam ….` | delegasi materi tersebar | 123f |
| `Pada saat Peraturan Menteri ini mulai berlaku, …` | pembuka pencabutan | 94 |
| `dicabut dan dinyatakan tidak berlaku` | pencabutan yang sudah berlaku | 96 |
| `ditarik kembali dan dinyatakan tidak berlaku` | pencabutan yang belum berlaku | 99 |
| `Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.` | saat mulai berlaku | 100 |
| `Peraturan Menteri ini mulai berlaku pada tanggal … .` | tanggal tertentu | 101a |
| `… mulai berlaku pada tanggal diundangkan dan berlaku surut sejak tanggal … .` | berlaku surut | 101a |
| `Peraturan Menteri ini mulai berlaku setelah … terhitung sejak tanggal diundangkan.` | tenggang waktu | 101d |
| `… mulai berlaku efektif pada tanggal …` | **DILARANG** | 102 |
| `Hal-hal yang belum cukup diatur … diatur lebih lanjut dengan …` | **DILARANG** (delegasi blangko) | 123c |
| `Agar setiap orang mengetahuinya, memerintahkan pengundangan Peraturan Menteri ini dengan penempatannya dalam Berita Negara Republik Indonesia.` | perintah pengundangan | 111 |
| `Ditetapkan di …` / `pada tanggal …` | penandatanganan, rata kanan | 112–113 |
| `a.n. MENTERI KEUANGAN REPUBLIK INDONESIA` | KMK atas nama Menteri | 114 |
| `Diundangkan di …` / `pada tanggal …` | pengundangan, rata kiri | 115–116 |
| `BERITA NEGARA REPUBLIK INDONESIA TAHUN … NOMOR …` | akhir penutup | 118–119 |
| `… sebagaimana tercantum dalam Lampiran … yang merupakan bagian tidak terpisahkan dari Peraturan Menteri ini.` | penunjuk lampiran | 120 |
| `Beberapa ketentuan dalam Peraturan Menteri Keuangan Nomor … tentang … (Berita Negara …), diubah sebagai berikut:` | Pasal I PMK perubahan | 124c |
| `Ketentuan Pasal … diubah sehingga berbunyi sebagai berikut:` | butir perubahan | 124c |
| `Di antara Pasal … dan Pasal … disisipkan … pasal, yakni Pasal …A …` | sisipan pasal | 124d |
| `Setelah Bab … ditambahkan 1 (satu) bab, yakni Bab … sehingga berbunyi sebagai berikut:` | penambahan bab | 124e |
| `Di antara ayat (…) dan ayat (…) Pasal … disisipkan … ayat, yakni ayat (…a) …` | sisipan ayat | 124f |
| `Pasal … dihapus.` / `(…) Dihapus.` | penghapusan | 124h |
| `Salinan sesuai dengan aslinya,` | blok salinan | 131a |
| `Salinan Keputusan Menteri ini disampaikan kepada:` | penyampaian salinan KMK | 131b |

---

## Lampiran C — Urutan pemeriksaan yang disarankan

Disusun dari yang paling murah dan paling pasti ke yang paling mahal, agar
temuan deterministik selesai sebelum model bahasa dipanggil.

1. **Format berkas** — huruf, ukuran kertas, marjin, spasi, nomor halaman (9.24).
   Tidak perlu membaca isi.
2. **Struktur kerangka** — keberadaan dan urutan kepala, judul, pembukaan, batang
   tubuh, penutup, lampiran (9.1–9.3, 9.18, 9.20).
3. **Rumusan baku** — pencocokan seluruh string di Lampiran B, termasuk dua pola
   terlarang (butir 102 dan butir 123c).
4. **Penomoran dan penanda** — bab Romawi, bagian bilangan tingkat, paragraf angka
   Arab, pasal angka Arab, ayat dalam kurung, tangga rincian empat tingkat
   (9.10–9.12).
5. **Keterkaitan internal** — acuan pasal/ayat yang menggantung, lampiran yatim,
   istilah terdefinisi yang tak pernah dipakai atau tak pernah dikapitalkan,
   sanksi yang mendahului kewajiban (9.11, 9.13, 9.15, 9.20).
6. **Konsistensi jenis naskah** — perubahan vs pencabutan: penomoran Pasal I/II
   atau 1/2, kehadiran peraturan sasaran di Mengingat, frasa pencabutan yang tepat
   (9.21, 9.22, 9.7).
7. **Pemeriksaan korpus** — kesamaan definisi dengan PMK sebidang dan peraturan
   lebih tinggi; kelengkapan Mengingat; PMK lama sebidang yang seharusnya dicabut;
   pertentangan dengan peraturan lebih tinggi dan setingkat (9.13, 9.7, 9.22,
   9.26). Ini bagian yang memerlukan OpenSearch dan model bahasa.
8. **Penilaian penelaah** — satu pasal satu norma, kecukupan konsiderans,
   kelayakan pengelompokan, ambang perubahan 50%, perubahan terselubung
   (9.11, 9.6, 9.10, 9.21, 9.16).

Prinsip yang dipegang: **setiap temuan menyebut nomor butir**, dan temuan yang
berasal dari langkah 7 dan 8 selalu ditandai sebagai usulan yang menunggu
keputusan penelaah, bukan kesalahan yang sudah pasti.

---

## Lampiran D — Katalog analisis Drafter Analiser

Konsolidasi seluruh blok Pemeriksaan di dokumen ini menjadi satu daftar berkode,
diurutkan dari yang paling murah dan paling pasti ke yang paling mahal dan paling
mungkin keliru. Kode ini dimaksudkan menjadi identitas tetap temuan, sehingga
catatan di dokumen Word dapat berbunyi `S-07 · butir 51` dan penelaah dapat
menelusuri sendiri dasarnya.

Kolom **Sifat** memakai tiga nilai: **pasti** (pelanggaran, tidak ada tafsir),
**tandai** (menyimpang dari anjuran atau memerlukan konteks), dan **usul**
(rekomendasi yang menunggu keputusan penelaah).

### T1 — Format berkas (F)

Dibaca dari properti .docx. Tidak membaca isi, tidak memerlukan model bahasa.
Paling murah dan paling sering gagal karena naskah disalin dari dokumen lain.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| F-01 | Jenis huruf Bookman Old Style pada seluruh run | Lamp. III ket. 1a | pasti |
| F-02 | Ukuran huruf 12 | Lamp. III ket. 1a | pasti |
| F-03 | Ukuran kertas 21 × 33 cm (F4) | Lamp. III ket. 1b | pasti |
| F-04 | Marjin atas halaman 1 = 8 cm (PMK/KMK) atau 4 cm (pimpinan unit) | Lamp. III ket. 1b | pasti |
| F-05 | Marjin atas halaman 2 dst = 2,5 cm | Lamp. III ket. 1b | pasti |
| F-06 | Marjin bawah, kiri, kanan = 2,5 cm | Lamp. III ket. 1b | pasti |
| F-07 | Line spacing 1; spacing before dan after 0 pt | Lamp. III ket. 1c | pasti |
| F-08 | Halaman pertama tanpa nomor halaman | butir 132a | pasti |
| F-09 | Nomor halaman ≥ 2 di tengah atas, berpola `- n -` | butir 132a, Lamp. III ket. 2 | pasti |
| F-10 | Nomor halaman lampiran melanjutkan batang tubuh | butir 132a | pasti |
| F-11 | Jarak antarblok pembukaan sesuai tabel 9.24.1 | Lamp. III bagan I–VIII | tandai |
| F-12 | Jarak 3 enter pada ruang tanda tangan | Lamp. III bagan I–VIII | tandai |
| F-13 | Indentasi rincian bertambah 1 cm tiap tingkat | Lamp. III bagan I–VIII | tandai |
| F-14 | Paragraf badan pasal mulai di 3,5 cm dari margin kiri | Lamp. III bagan I, VI | tandai |
| F-15 | Kolom huruf abjad butir Menimbang di 3 cm; teksnya di 4 cm | Lamp. III bagan I, VI | tandai |
| F-16 | Label pembukaan rata margin kiri, isinya berjarak 0,5 cm | Lamp. III bagan I, VI | tandai |

### T2 — Struktur dan penanda (S)

Parsing naskah menjadi pohon: judul → pembukaan → bab → bagian → paragraf →
pasal → ayat → rincian. Seluruhnya pencocokan pola.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| S-01 | Judul terdiri atas empat baris berurutan | butir 4 | pasti |
| S-02 | Judul kapital seluruhnya, tanpa tanda baca penutup | butir 8 | pasti |
| S-03 | Nomor berpola `NOMOR n TAHUN tttt`; format lama ditandai | butir 5 | tandai |
| S-04 | Nama judul memuat kurung berisi kapital — indikasi akronim | butir 8 | tandai |
| S-05 | Lima unsur pembukaan hadir dan berurutan | butir 13 | pasti |
| S-06 | PMK memuat `DENGAN RAHMAT TUHAN YANG MAHA ESA`; KMK tidak | butir 14 | pasti |
| S-07 | Nama jabatan pembentuk diakhiri koma | butir 15 | pasti |
| S-08 | `Menimbang` rata kiri, huruf awal kapital, titik dua | butir 16 | pasti |
| S-09 | Butir Menimbang berhuruf abjad, diawali "bahwa", diakhiri titik koma | butir 21 | pasti |
| S-10 | `Mengingat` rata kiri, angka Arab, diakhiri titik koma | butir 23, 31 | pasti |
| S-11 | `Undang-Undang` — kedua huruf u kapital | butir 33 | pasti |
| S-12 | Kata "tentang" dalam judul dasar hukum huruf kecil | butir 32 | pasti |
| S-13 | UU/PP/Perpres disertai Lembaran Negara; PMK disertai Berita Negara | butir 34, 35 | pasti |
| S-14 | Urutan dasar hukum menaati hierarki lalu kronologi | butir 30 | pasti |
| S-15 | `MEMUTUSKAN:` kapital, tanpa spasi sebelum titik dua | butir 37 | pasti |
| S-16 | `Menetapkan` sejajar `Menimbang` dan `Mengingat` | butir 38 | pasti |
| S-17 | Isi Menetapkan tanpa "REPUBLIK INDONESIA", diakhiri titik | butir 39 | pasti |
| S-18 | PMK memakai Pasal, KMK memakai diktum | butir 42 | pasti |
| S-19 | Bab berangka Romawi, judul kapital seluruhnya | butir 51 | pasti |
| S-20 | Bagian berbilangan tingkat berhuruf (`Bagian Kesatu`) | butir 52 | pasti |
| S-21 | Paragraf berangka Arab (`Paragraf 1`) | butir 53 | pasti |
| S-22 | Bagian tidak muncul tanpa bab; paragraf tidak tanpa bagian | butir 50 | pasti |
| S-23 | Nomor pasal berurut menaik, tidak dimulai ulang tiap bab | butir 54c | pasti |
| S-24 | Ayat berpola `(n)` tanpa titik | butir 54f | pasti |
| S-25 | Acuan `Pasal` kapital, acuan `ayat` huruf kecil | butir 54d, 54h | pasti |
| S-26 | Bilangan berpola `n (kata)` | butir 54j | tandai |
| S-27 | Tangga rincian `a.` → `1.` → `a)` → `1)` | butir 54k-7 | pasti |
| S-28 | Kedalaman rincian ≤ 4 tingkat | butir 54k-8 | pasti |
| S-29 | Rincian diawali huruf kecil | butir 54k-3 | pasti |
| S-30 | Rincian selain yang terakhir diakhiri titik koma | butir 54k-4 | pasti |
| S-31 | Rincian yang punya rincian lanjutan diakhiri titik dua | butir 54k-6 | pasti |
| S-32 | Konjungsi hanya sekali, pada rincian kedua dari terakhir | butir 54l–o | pasti |
| S-33 | Daftar tanpa konjungsi sama sekali | butir 54l–n | tandai |
| S-34 | Definisi bernomor Arab, huruf awal kapital, diakhiri titik | butir 60 | pasti |
| S-35 | Urutan empat kelompok batang tubuh tidak tertukar | butir 41 | pasti |
| S-36 | Ketentuan Peralihan berada sebelum Ketentuan Penutup | butir 80 | pasti |
| S-37 | Blok penetapan rata kanan, blok pengundangan rata kiri di bawahnya | butir 113, 116 | pasti |
| S-38 | Nama jabatan penutup diakhiri koma | butir 114, 117 | pasti |
| S-39 | Nama pejabat tanpa gelar, pangkat, golongan, NIP | butir 112d, 115d | pasti |
| S-40 | Baris akhir `BERITA NEGARA REPUBLIK INDONESIA TAHUN … NOMOR …` kapital | butir 118, 119 | pasti |
| S-41 | Lampiran memakai huruf/angka, bukan "Pasal" | butir 42 | pasti |
| S-42 | Kepala lampiran memuat nomor, tahun, judul PMK yang sama dengan halaman 1 | butir 121c | pasti |
| S-43 | Setiap lampiran diakhiri nama jabatan dan nama pejabat | butir 121h | pasti |
| S-44 | Jumlah lampiran lebih dari satu | butir 121i | tandai |

### T3 — Rumusan baku dan pola terlarang (R)

Pencocokan string terhadap Lampiran B. Temuan paling mudah dijelaskan kepada
penelaah karena dasarnya berupa kalimat yang bunyinya memang sudah ditentukan.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| R-01 | Frasa Dengan Rahmat persis | butir 14 | pasti |
| R-02 | Frasa pembuka Ketentuan Umum persis | butir 59 | pasti |
| R-03 | Butir Menimbang terakhir memakai rumusan baku | butir 22 | pasti |
| R-04 | Perintah pengundangan persis | butir 111 | pasti |
| R-05 | Rumusan saat mulai berlaku cocok salah satu bentuk butir 100/101 | butir 100, 101 | pasti |
| R-06 | **Larangan** `mulai berlaku efektif pada tanggal` | butir 102 | pasti |
| R-07 | **Larangan** delegasi blangko `hal-hal yang belum cukup diatur …` | butir 123c | pasti |
| R-08 | Pembuka pencabutan `Pada saat Peraturan Menteri ini mulai berlaku` | butir 94 | pasti |
| R-09 | `dicabut dan dinyatakan tidak berlaku` vs `ditarik kembali …` sesuai status | butir 96, 99 | pasti |
| R-10 | Pencabutan menyebut peraturan secara tegas, bukan rumusan umum | butir 95 | pasti |
| R-11 | Lebih dari satu peraturan dicabut ditulis bertabulasi | butir 97 | pasti |
| R-12 | Penunjuk lampiran memuat `merupakan bagian tidak terpisahkan` | butir 120 | pasti |
| R-13 | Kalimat delegasi menyebut jenis peraturan pelaksana secara tegas | butir 123b | pasti |
| R-14 | `diatur dengan` vs `diatur dalam` — dicocokkan dengan maksudnya | butir 123f, 123g | tandai |
| R-15 | Judul perubahan ke-n memuat `SEBAGAIMANA TELAH DIUBAH` | butir 11 | pasti |
| R-16 | Rumusan Pasal I PMK perubahan sesuai bentuk baku | butir 124c | pasti |
| R-17 | Penanda sisipan: pasal/bab huruf kapital, ayat huruf kecil | butir 124d, f, g | pasti |
| R-18 | Pasal/ayat yang dihapus tetap tercantum dengan keterangan `Dihapus` | butir 124h | pasti |
| R-19 | Nama singkat tidak memuat nomor atau tahun | butir 89a | pasti |
| R-20 | Blok salinan memuat `Salinan sesuai dengan aslinya,` | butir 131a | pasti |
| R-21 | **Larangan** `Yth.` pada daftar penyampaian salinan | butir 131b | pasti |

### T4 — Konsistensi internal (I)

Memerlukan graf rujukan di dalam satu dokumen. Masih deterministik, tetapi
menuntut parser yang benar. Inilah kelompok yang paling menghemat waktu penelaah
karena manusia hampir mustahil melacaknya pada naskah 60 pasal.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| I-01 | Acuan `Pasal n` menunjuk pasal yang tidak ada — rujukan menggantung | akibat butir 54d | pasti |
| I-02 | Acuan `ayat (n)` menunjuk ayat yang tidak ada pada pasal itu | akibat butir 54h | pasti |
| I-03 | `Lampiran n` disebut di pasal tetapi lampirannya tidak ada | butir 120 | pasti |
| I-04 | Lampiran ada tetapi tidak pernah ditunjuk pasal mana pun | butir 120 | pasti |
| I-05 | Istilah terdefinisi tidak pernah ditulis berhuruf awal kapital | butir 67 | pasti |
| I-06 | Kata berkapital berulang yang tidak pernah didefinisikan | butir 61, 67 | tandai |
| I-07 | Istilah didefinisikan tetapi dipakai hanya sekali | butir 61, 64 | tandai |
| I-08 | Singkatan dipakai tanpa diperkenalkan `yang selanjutnya disingkat` | butir 58b | pasti |
| I-09 | Nama peraturan pada butir Menimbang terakhir ≠ nama pada judul | butir 22 | pasti |
| I-10 | Nama pada `Menetapkan` ≠ nama pada judul | butir 39 | pasti |
| I-11 | Pasal yang disebut di Menimbang, peraturannya tidak ada di Mengingat | butir 19, 24b | pasti |
| I-12 | Judul `PERUBAHAN ATAS X` tetapi X tidak ada di Mengingat | butir 27 | pasti |
| I-13 | Peraturan yang dicabut di penutup masih tercantum di Mengingat | butir 28a | pasti |
| I-14 | PMK perubahan tidak memakai `Pasal I`/`Pasal II` Romawi | butir 124b | pasti |
| I-15 | PMK pencabutan tersendiri tidak memakai `Pasal 1`/`Pasal 2` Arab | butir 130m | pasti |
| I-16 | Pasal sanksi bernomor lebih kecil daripada pasal kewajiban yang dirujuk | butir 45 | pasti |
| I-17 | Ada pencabutan tetapi tidak ada keterangan status peraturan pelaksana | butir 98 | tandai |
| I-18 | `berlaku surut` ada tetapi tidak ada Ketentuan Peralihan | butir 83, 106a | pasti |
| I-19 | Penundaan sementara tanpa jangka waktu atau syarat berakhir | butir 84 | pasti |
| I-20 | Mengingat kosong | butir 24, 25 | pasti |
| I-21 | Mengingat memuat peraturan menteri selain PMK | butir 26 | pasti |
| I-22 | PMK memuat diktum `Memperhatikan` | butir 36 | pasti |
| I-23 | Naskah memuat sanksi pidana | butir 74 | tandai |
| I-24 | Nomor lampiran PMK perubahan tidak dimulai ulang dari I | butir 128 | tandai |
| I-25 | Rasio pasal yang diubah terhadap pasal peraturan asal > 50% | butir 127a | usul |
| I-26 | Sistematika PMK perubahan berbeda dari peraturan asal | butir 127 | usul |

### T5 — Konsistensi terhadap korpus (K)

Memerlukan indeks OpenSearch berisi peraturan yang berlaku, idealnya terurai
sampai tingkat pasal dan definisi. Di sinilah alat memberi sesuatu yang tidak
dapat dikerjakan penelaah secara manual maupun oleh aturan biasa.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| K-01 | Rumusan definisi berbeda dari PMK sebidang yang telah berlaku | butir 62 | usul |
| K-02 | Rumusan definisi berbeda dari peraturan lebih tinggi yang dilaksanakan | butir 65 | usul |
| K-03 | Peraturan di Mengingat **belum berlaku** | butir 28, 29 | pasti |
| K-03b | Peraturan di Mengingat **sudah dicabut** | — tidak ada butirnya, lihat 9.28 angka 9 | pasti |
| K-04 | Peraturan di Mengingat tidak memberi kewenangan dan tidak memerintahkan | butir 24 | usul |
| K-05 | Nomor Lembaran/Berita Negara yang dicantumkan tidak cocok dengan basis data | butir 34, 35 | pasti |
| K-06 | Pasal yang dirujuk di peraturan lain memang ada dan berbunyi demikian | butir 19 | pasti |
| K-07 | Ada PMK sebidang yang tampaknya harus dicabut tetapi tidak disebut | butir 130e | usul |
| K-08 | Materi rancangan bertentangan dengan peraturan yang lebih tinggi | checklist 2b | usul |
| K-09 | Materi rancangan bertentangan dengan peraturan setingkat | Lamp. III huruf C angka 4 | usul |
| K-10 | Materi rancangan bersinggungan dengan putusan pengadilan | Lamp. III huruf C angka 5 | usul |
| K-11 | Norma mengulang ketentuan peraturan yang mendelegasikan | butir 123d, 123e | usul |
| K-12 | Status peraturan yang dicabut: sudah berlaku atau belum — penentu R-09 | butir 96, 99 | pasti |

### T6 — Penilaian makna (P)

Memerlukan model bahasa. Seluruhnya bersifat **usul**, tidak pernah dinyatakan
sebagai kesalahan, dan selalu disertai kalimat yang dipersoalkan agar penelaah
dapat menilai sendiri dalam hitungan detik.

| Kode | Pemeriksaan | Rujukan | Sifat |
|---|---|---|---|
| P-01 | Satu pasal memuat lebih dari satu norma | butir 54a | usul |
| P-02 | Satu ayat memuat lebih dari satu norma | butir 54g | usul |
| P-03 | Pasal berayat banyak sebaiknya dipecah | butir 54b | usul |
| P-04 | Rincian tidak terbaca sebagai kesatuan dengan frasa pembukanya | butir 54k-1 | usul |
| P-05 | "dan" dipakai untuk rincian yang sebenarnya alternatif, atau sebaliknya | butir 54l–n | usul |
| P-06 | Definisi menimbulkan pengertian ganda | butir 66 | usul |
| P-07 | Urutan definisi tidak dari lingkup umum ke khusus | butir 68 | usul |
| P-08 | Konsiderans memuat norma, bukan alasan | butir 17 | usul |
| P-09 | Konsiderans kurang unsur sosiologis dan yuridis | butir 20 | usul |
| P-10 | Nama judul tidak mencerminkan isi, atau tidak singkat | butir 7 | usul |
| P-11 | Akronim pada judul tidak memenuhi pengecualian | butir 8 | usul |
| P-12 | Ketentuan Peralihan memuat perubahan terselubung | butir 85 | usul |
| P-13 | Ada kewajiban atau larangan tanpa sanksi, atau sebaliknya | butir 45 | usul |
| P-14 | Pengelompokan bab tidak berdasar kesamaan materi | butir 43, 48 | usul |
| P-15 | Kriteria pembagian bab tidak konsisten | butir 72 | usul |
| P-16 | Materi yang didelegasikan tidak bersifat teknis administratif | butir 123a | usul |
| P-17 | Nama singkat menyimpang dari isi, sinonim, atau tidak perlu | butir 90–92 | usul |
| P-18 | PMK mengubah keadaan hukum berjalan tetapi tanpa Ketentuan Peralihan | butir 79 | usul |
| P-19 | Esensi peraturan berubah sehingga sebaiknya dicabut dan disusun ulang | butir 127a | usul |
| P-20 | Pemberlakuan surut membebani para pihak atau penerimaan negara | butir 106c | usul |
| P-21 | Usulan rumusan perbaikan untuk setiap temuan T1–T5 | — | usul |

### Catatan rancang bangun

**Sebaran beban.** Dari 121 pemeriksaan di atas, 94 berada di T1–T4 dan tidak
memerlukan model bahasa sama sekali. **Dugaan** yang belum diuji: sebagian besar
temuan pada rancangan nyata akan berasal dari kelompok itu, terutama F dan S,
karena kesalahan teknis penulisan jauh lebih sering daripada kesalahan substansi.
Angka pastinya baru diketahui setelah alat dijalankan atas beberapa rancangan
sungguhan — dan itu sebaiknya dilakukan **sebelum** Minggu 4, karena hasilnya
menentukan bagian mana yang layak disempurnakan.

**Urutan pembangunan yang masuk akal.** T1 dan T3 dapat berjalan tanpa parser
sama sekali — cukup membaca properti dokumen dan mencocokkan string. T2 menuntut
parser pohon, dan parser itulah prasyarat T4, T5, dan T6; kalau parser meleset,
seluruh lapisan di atasnya ikut meleset. Karena itu **parser adalah satu-satunya
bagian yang pantas diberi waktu lebih dari perkiraan**.

**Penambat catatan di Word.** Temuan T1–T4 punya rentang karakter yang pasti,
sehingga catatan dapat ditambatkan tepat pada kata atau kalimat yang
dipersoalkan. Temuan T5 dan T6 sebaiknya ditambatkan pada tingkat pasal, karena
alasannya menyangkut keseluruhan pasal, bukan satu frasa. Membedakan dua
perlakuan ini sejak awal menghindari catatan yang menunjuk ke tempat yang
membingungkan penelaah.

**Yang paling mungkin gagal.** Tiga hal, disebut apa adanya:

1. **T5 bergantung penuh pada mutu indeks.** Bila indeks OpenSearch Law Analyzer
   hanya menyimpan peraturan sebagai dokumen utuh tanpa uraian pasal dan
   definisi, maka K-01, K-02, dan K-06 tidak dapat dikerjakan sebagaimana
   dibayangkan. Ini asumsi yang **belum diuji** dan sebaiknya diperiksa lebih
   dahulu, sebelum arsitektur dikunci.
2. **P-01 akan banyak keliru.** "Satu pasal satu norma" adalah penilaian yang
   bahkan antarpenelaah bisa berbeda. Bila ditampilkan sebagai kesalahan, alat
   akan kehilangan kepercayaan pada pemakaian pertama. Tampilkan sebagai usul,
   dan sediakan cara menyembunyikan seluruh kelompok P.
3. **Terlalu banyak temuan sama buruknya dengan terlalu sedikit.** Naskah 60
   pasal yang setiap bilangannya tidak berkurung akan menghasilkan ratusan
   temuan S-26. Perlu pengelompokan temuan sejenis menjadi satu catatan
   bernomor, bukan satu catatan per kemunculan.

**Yang berada di luar jangkauan alat ini.** Apakah kebijakannya tepat, apakah
dampaknya sesuai lima kriteria lembar analisis dampak, apakah harmonisasi di
Kementerian Hukum akan lolos, dan apakah persetujuan Presiden diperlukan — semua
itu keputusan manusia. Alat dapat mengingatkan bahwa pertanyaannya ada, tetapi
tidak menjawabnya. Menyatakan batas ini secara terbuka di antarmuka justru
menaikkan kepercayaan penelaah, bukan menurunkannya.

---

*Disusun dari KMK 527/KMK.01/2022 Lampiran II butir 1–132 dan Lampiran III huruf
A, C, dan E. Seluruh kutipan telah dicocokkan dengan citra halaman naskah JDIH.
Halaman yang belum dapat dipastikan tercatat pada bagian 9.29.*
