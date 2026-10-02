# Analisis isi naskah

Satu bagian `##` = satu analisis. Bentuk tiap bagian mengikuti
`_TEMPLATE.md`. Yang di luar bagian `##` tidak dibaca kode maupun agen.

Kode lama dipertahankan (F1-…, F2-…, F3-…) supaya penelaah mengenalinya;
analisis baru memakai kode katalog `docs/fase4-merapikan-backend.md` bagian 6.

## F1-006 · Judul peraturan tidak diakhiri tanda baca

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf A butir 8, hlm 30 (visual)
Butuh: —

### Yang diperiksa
- Baris terakhir judul (sesudah TENTANG, sebelum DENGAN RAHMAT) diakhiri titik, koma, titik koma, atau titik dua

### Yang tidak diperiksa
- Tanda kurung tutup pada akronim, mis. "(LP2P)" — butir 8 mempersoalkan akronimnya, bukan kurungnya
- Huruf kapital judul — bacaan kapital dari gaya huruf belum terbukti (F1-001 dimatikan)

### Cara memeriksa
Judul halaman pertama ada di baris-baris sesudah "TENTANG" sampai sebelum
"DENGAN RAHMAT TUHAN YANG MAHA ESA". Lihat karakter terakhir baris judul yang
terakhir. Kutip kata terakhir beserta tanda bacanya; usulan = kata itu tanpa
tanda baca.

### Bukan kesalahan
- Judul yang berakhir dengan kurung tutup akronim
- Tanda baca di tengah judul (koma pemisah daftar)

## F1-002 · Nama pada Menetapkan sama dengan nama pada judul

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.5 butir 39, hlm 37 (visual)
Butuh: —

### Yang diperiksa
- Nama sesudah TENTANG pada Menetapkan dibandingkan kata per kata dengan nama sesudah TENTANG pada judul halaman pertama

### Yang tidak diperiksa
- Mana dari keduanya yang benar — keputusan penelaah
- Frasa "REPUBLIK INDONESIA" dan titik penutup pada Menetapkan — itu F1-012
- Isi judulnya sendiri

### Cara memeriksa
Ambil nama sesudah TENTANG di judul (bisa beberapa baris) dan nama sesudah
TENTANG pada Menetapkan. Bandingkan kata per kata; abaikan pemenggalan baris,
spasi, dan huruf besar-kecil. Kutip kata yang berbeda di Menetapkan. Kalau
yang berbeda adalah kata yang HILANG dari Menetapkan, kutip kata di
sebelahnya dan sebut kata yang hilang di temuan.

### Bukan kesalahan
- "REPUBLIK INDONESIA" yang tidak ada pada Menetapkan — butir 39 memang membuangnya
- Titik di akhir Menetapkan
- Pemenggalan baris yang berbeda

## F1-003 · Kelengkapan bagian wajib pembukaan

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B butir 13, hlm 33 (visual)
Butuh: —

### Yang diperiksa
- Ada bagian Menimbang, Mengingat, dan Menetapkan
- PMK memuat frasa DENGAN RAHMAT TUHAN YANG MAHA ESA

### Yang tidak diperiksa
- Isi dan urutan bagian-bagian itu
- Letak frasanya; yang diperiksa ada atau tidak

### Cara memeriksa
Cari tiap bagian dengan `cari_teks` SEBELUM menyatakan tidak ada, dan tulis
kata yang dicari di `tidak_ada`. Temuan ketiadaan diisi `ketiadaan: true`;
letaknya ¶ baris pertama judul halaman pertama, kutipannya kata pertama baris
itu, tanpa usulan.

### Bukan kesalahan
- Kata "Menimbang" yang berdiri di sel tabel tersendiri
- Bila tidak satu pun bagian pembukaan terbaca, diam — pertanda naskahnya belum terbaca utuh, bukan cacat

## F1-007 · Penulisan kata "Menimbang"

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.3 butir 16, hlm 34 (visual)
Butuh: —

### Yang diperiksa
- Huruf awal kapital, selebihnya huruf kecil — "MENIMBANG" dan "menimbang" menyimpang
- Diakhiri titik dua (:)

### Yang tidak diperiksa
- Kata yang berdiri sendiri di paragrafnya — pada naskah bertabel titik duanya di sel sebelah
- Kemunculan selain yang pertama sebelum MEMUTUSKAN
- Letaknya di kiri margin — itu tata letak

### Cara memeriksa
Hanya label bagian Menimbang (kemunculan pertama sebelum MEMUTUSKAN). Kutip
kata labelnya saja; usulan "Menimbang" untuk kapital yang salah, atau
"Menimbang :" bila titik duanya tidak ada padahal isi menyusul di paragraf
yang sama.

### Bukan kesalahan
- "Menimbang" sendirian di paragrafnya, tanpa titik dua

## F1-008 · Bentuk tiap butir Menimbang

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.3 butir 21, hlm 34 (visual)
Butuh: —

### Yang diperiksa
- Tiap butir diawali kata "bahwa"
- Tiap butir diakhiri titik koma (;)

### Yang tidak diperiksa
- Isi pertimbangannya
- Butir yang terpotong ke paragraf lanjutan — ujungnya dinilai di paragraf terakhirnya

### Cara memeriksa
Baca tiap butir Menimbang sampai ujungnya, termasuk paragraf lanjutannya.
Kutip awal butir bila "bahwa" tidak ada, atau kata terakhir butir bila titik
komanya tidak ada.

### Bukan kesalahan
- Huruf abjad penanda butir yang berupa penomoran otomatis Word

## F1-004 · Bunyi lazim butir Menimbang terakhir

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.3 butir 22, hlm 35 (visual)
Butuh: —

### Yang diperiksa
- Bila Menimbang lebih dari satu butir: butir terakhir memuat "berdasarkan pertimbangan sebagaimana dimaksud dalam huruf …", "perlu menetapkan Peraturan Menteri Keuangan tentang …", dan diakhiri titik koma

### Yang tidak diperiksa
- Menimbang satu butir
- Isi pertimbangannya

### Cara memeriksa
Bandingkan butir terakhir dengan bunyi butir 22. Kutip awal butir terakhir
(paling banyak 200 huruf).

### Bukan kesalahan
- Butir 22 berbunyi "pada umumnya", bukan "wajib" — temuan ini catatan untuk ditimbang penelaah, bukan kesalahan mutlak; sebut itu di temuan

## F1-009 · Penulisan kata "Mengingat"

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.4 butir 23, hlm 35 (visual)
Butuh: —

### Yang diperiksa
- Huruf awal kapital, selebihnya huruf kecil
- Diakhiri titik dua (:)

### Yang tidak diperiksa
- Kata yang berdiri sendiri di paragrafnya
- Kemunculan selain yang pertama sebelum MEMUTUSKAN

### Cara memeriksa
Sama seperti F1-007, untuk label "Mengingat".

### Bukan kesalahan
- "Mengingat" sendirian di paragrafnya, tanpa titik dua

## F1-010 · Tanda baca dasar hukum

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.4 butir 31, hlm 36 (visual)
Butuh: —

### Yang diperiksa
- Bila dasar hukum lebih dari satu: tiap butir Mengingat diakhiri titik koma (;)

### Yang tidak diperiksa
- Penomorannya — pada naskah bertabel nomornya sering di sel lain
- Urutan hierarkinya, dan kelengkapan Lembaran Negara

### Cara memeriksa
Satu butir dimulai di paragraf bernomor dan berlanjut ke paragraf
lanjutannya; nilai ujungnya di paragraf terakhir butir itu. Kutip kata
terakhir butir.

### Bukan kesalahan
- Butir terakhir yang ditutup titik koma, atau titik, sesuai contoh KMK 527

## F1-005 · Ejaan baku dasar hukum

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.4 butir 32 dan 33, hlm 36 (visual)
Butuh: —

### Yang diperiksa
- "Undang-Undang" dengan kedua huruf u kapital — hanya di bagian Mengingat
- "Peraturan Pemerintah Pengganti Undang-Undang" ditulis lengkap dengan kapital — hanya di Mengingat
- Kata "tentang" di judul peraturan pada dasar hukum tetap huruf kecil — hanya di Mengingat

### Yang tidak diperiksa
- Salah ketik biasa — itu S-64
- Kata penghubung/konjungsi di judul peraturan dasar hukum
- Apa pun di luar bagian Mengingat

### Cara memeriksa
Hanya butir Mengingat. Kutip kata yang salah; usulan = kata yang sama
dengan huruf kapital yang benar.

### Bukan kesalahan
- "undang-undang" sebagai sebutan umum di luar Mengingat

## F1-011 · Penulisan kata "Menetapkan"

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.5 butir 38, hlm 37 (visual)
Butuh: —

### Yang diperiksa
- Huruf awal kapital, selebihnya huruf kecil
- Diakhiri titik dua (:)

### Yang tidak diperiksa
- Kata yang berdiri sendiri di paragrafnya
- Letaknya disejajarkan dengan Menimbang dan Mengingat — itu tata letak

### Cara memeriksa
Hanya label Menetapkan, kemunculan pertama sesudah MEMUTUSKAN. Sama seperti
F1-007.

### Bukan kesalahan
- "Menetapkan" sendirian di paragrafnya, tanpa titik dua

## F1-012 · Bentuk nama peraturan pada Menetapkan

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.5 butir 39, hlm 37 (visual)
Butuh: —

### Yang diperiksa
- Isi Menetapkan diakhiri titik (.)
- Tanpa frasa "REPUBLIK INDONESIA" sesudah "MENTERI KEUANGAN" — di posisi jenis peraturan, sebelum kata TENTANG pertama

### Yang tidak diperiksa
- Kesamaannya dengan judul — itu F1-002
- Huruf kapitalnya — bacaan kapital dari gaya huruf belum terbukti
- "Republik Indonesia" di dalam nama sesudah TENTANG — itu nama resmi peraturan lain

### Cara memeriksa
Kutip "MENTERI KEUANGAN REPUBLIK INDONESIA" pada Menetapkan, usulan "MENTERI
KEUANGAN"; atau kutip kata terakhir, usulan kata itu dengan titik.

### Bukan kesalahan
- Frasa itu sesudah TENTANG

## F2-001 · Rujukan menunjuk ketentuan yang ada

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf d dan h, hlm 40 (turunan)
Butuh: —

### Yang diperiksa
- "sebagaimana dimaksud dalam/pada Pasal N ayat (n) huruf x angka y" menunjuk satuan yang ada di naskah ini

### Yang tidak diperiksa
- Rujukan ke peraturan lain, mis. "Pasal 12 Undang-Undang Nomor 1 Tahun 2004"
- Apakah isi yang dirujuk cocok dengan maksud kalimatnya — itu I-37

### Cara memeriksa
Teks yang dirujuk tiap pasal fokus sudah disalinkan kode di blok SATUAN YANG
DIRUJUK; "TIDAK ADA di naskah" di sana adalah bukti. Kutip frasa rujukannya
persis; tulis alamat yang tidak ada di `tidak_ada`. Nomor penggantinya tidak
diketahui, jadi tanpa usulan.

### Bukan kesalahan
- Rujukan yang tujuannya ada di naskah
- "Pasal" tanpa frasa "sebagaimana dimaksud"

## I-37 · Rujukan menunjuk ketentuan yang benar

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf d dan h, hlm 40 (turunan)
Butuh: —

### Yang diperiksa
- Acuan "sebagaimana dimaksud dalam …" menunjuk ketentuan yang isinya sesuai dengan yang dimaksud kalimatnya

### Yang tidak diperiksa
- Rujukan ke peraturan lain
- Rujukan yang tujuannya tidak ada — itu F2-001

### Cara memeriksa
Bandingkan yang disebut kalimat dengan teks ketentuan yang dirujuk di blok
SATUAN YANG DIRUJUK. Bila tidak sesuai, cari ketentuan yang benar dengan
`cari_teks`. Kutip alamat rujukannya lengkap seperti tertulis, mis. "Pasal 9
ayat (11)"; usulan = alamat yang benar dalam bentuk yang sama, mis. "Pasal 9
ayat (13)" — hanya bila ketentuan yang benar ketemu di naskah. Selain itu
catatan.

### Bukan kesalahan
- Rujukan yang isinya sesuai walau rumusannya berbeda kata
- Rujukan ke ketentuan yang lebih umum tetapi mencakup maksudnya

### Contoh
PMK 45 Tahun 2026 Pasal 10 ayat (2) huruf b merujuk Pasal 9 ayat (11) —
jangka waktu penelitian — padahal yang dimaksud kalimatnya jangka waktu impor
di Pasal 9 ayat (13).

## F2-004 · Penomoran tidak melompat atau berulang

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf c, f, dan k angka 7, hlm 40–41 (visual)
Butuh: —

### Yang diperiksa
- Nomor Pasal berurut naik dan berjalan terus menembus bab
- Ayat, huruf, dan angka berurut di dalam induknya
- Nomor yang muncul dua kali

### Yang tidak diperiksa
- Pasal sisipan bernomor huruf (Pasal 5A)
- Penomoran di dalam lampiran
- Nomor yang dibuat penomoran otomatis Word — terbaca, tetapi tidak bisa ditandai

### Cara memeriksa
Telusuri label satuan dari awal sampai akhir. Kutip nomornya persis seperti
tertulis di teks paragraf ("Pasal 7", "(3)"); tulis nomor yang hilang atau
berulang di temuan.

### Bukan kesalahan
- Nomor yang hanya tampil dari penomoran otomatis — tidak ada di teks, jadi tidak bisa dikutip; diam

## F2-007 · Bilangan angka dan hurufnya cocok

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf j, hlm 41 (visual)
Butuh: —

### Yang diperiksa
- Bentuk "30 (tiga puluh)" — angka dan huruf di dalam kurung menyatakan bilangan yang sama

### Yang tidak diperiksa
- Kurung yang isinya bukan bilangan, mis. "Pengguna Barang (PB)"
- Mana yang benar, angkanya atau hurufnya — keputusan penelaah

### Cara memeriksa
Kutip seluruh "angka (huruf)". Tulis bilangan yang dimaksud hurufnya di
temuan; contoh rumusan yang cocok boleh di saran.

### Bukan kesalahan
- Bilangan yang hurufnya tidak bisa dibaca jadi angka pasti — diam

## F2-101 · Rumusan yang bisa dibaca dua arah

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: per pasal
Komentar: lengkap
Dasar:
Butuh: —

### Yang diperiksa
- Ketentuan yang punya DUA tafsiran yang sama-sama masuk akal dan berbeda akibat hukumnya
- Definisi Pasal 1 yang menimbulkan pengertian ganda

### Yang tidak diperiksa
- Rumusan yang cuma "terlalu umum" atau "kurang rinci" — itu bukan dua tafsiran
- Kebijakannya
- Keberadaan pasal atau ayat yang dirujuk — itu F2-001

### Cara memeriksa
Baca tiap pasal fokus dengan seluruh naskah sebagai konteksnya — definisi di
Pasal 1, pasal yang dirujuknya, bab tempatnya bernaung, lampirannya. WAJIB
mengisi `bacaan` dengan dua kalimat utuh yang berbeda akibat hukumnya. Untuk
definisi di Pasal 1, rujukannya ada di skill `pmk-standar/batang-tubuh`
(Ketentuan Umum).

### Bukan kesalahan
- Pengecualian yang sah: "kecuali sebagaimana dimaksud dalam Pasal 12"
- Rumusan baku "sesuai dengan ketentuan peraturan perundang-undangan"
- Rumusan yang satu bacaannya terbantah pasal lain di naskah ini

## F2-102 · Kewajiban tanpa pemikul yang tegas

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: per pasal
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: —

### Yang diperiksa
- Kewajiban atau larangan yang tidak jelas siapa pemikulnya

### Yang tidak diperiksa
- Kewajiban yang subjeknya bisa ditarik dari kalimat induk atau ayat sebelumnya dalam satu rangkaian

### Cara memeriksa
Baca batang kalimat induknya dan ayat-ayat sebelumnya sebelum menilai.
Usulan disusun dari subjek yang sudah tertulis di pasal itu atau istilah
berdefinisi di Pasal 1.

### Bukan kesalahan
- Daftar ruang lingkup atau rincian yang memang tidak memuat kewajiban
- Bentuk pasif yang pemikulnya tertulis di ayat lain pasal yang sama

## F2-103 · Kata operasional yang bertabrakan

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: per pasal
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: —

### Yang diperiksa
- wajib, harus, dapat, dan dilarang yang bertemu dalam SATU ketentuan sehingga tidak jelas perbuatannya diwajibkan atau dibolehkan

### Yang tidak diperiksa
- Kata operasional berbeda di pasal yang berbeda — itu lazim dan sah

### Cara memeriksa
Nilai per ketentuan (ayat, atau pasal tanpa ayat). Kutip kata operasional
yang bertabrakan.

### Bukan kesalahan
- "dapat" untuk kewenangan dan "wajib" untuk kewajiban pihak lain dalam satu ayat

## F2-104 · Dua ketentuan yang tidak bisa berlaku bersamaan

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C butir 54 huruf a dan g, hlm 39–40 (turunan)
Butuh: —

### Yang diperiksa
- Dua satuan yang saling meniadakan; keduanya dibaca utuh

### Yang tidak diperiksa
- Pengecualian yang sah — "kecuali sebagaimana dimaksud dalam Pasal 12" bukan tabrakan
- Tabrakan dengan peraturan lain — itu F3-001

### Cara memeriksa
Sebut KEDUA satuan di temuan. Tandai satuan yang menyimpang; kalau tidak
bisa ditentukan, yang letaknya lebih belakang. Sasaran perbaikannya sering
satuan yang satunya.

### Bukan kesalahan
- Ketentuan khusus yang mengecualikan ketentuan umum secara tegas

## F2-105 · Tujuan di Menimbang yang tidak ada ketentuannya

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf B.3 butir 17 dan 19, hlm 34 (turunan)
Butuh: —

### Yang diperiksa
- Maksud yang dinyatakan Menimbang dicari padanannya di batang tubuh

### Yang tidak diperiksa
- Arah sebaliknya — ketentuan yang tidak disebut Menimbang

### Cara memeriksa
Cari kata kunci tujuannya dengan `cari_teks` sebelum menyatakan tidak ada,
dan tulis di `tidak_ada`. Letaknya butir Menimbang itu.

### Bukan kesalahan
- Menimbang yang hanya menunjuk pasal peraturan lebih tinggi yang memerintahkan pembentukannya

## F2-003 · Istilah berdefinisi dipakai di batang tubuh

Berlaku untuk: pmk-standar
Respons: dibuang
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C.1 butir 61 dan 64, hlm 45 (visual)
Butuh: —

### Yang diperiksa
- Tiap istilah Pasal 1 dicari kemunculannya di luar Pasal 1 — batang tubuh dan lampiran
- Istilah yang tidak pernah muncul di luar Pasal 1 ditandai

### Yang tidak diperiksa
- Istilah yang dipakai sekali — pengecualian butir 64 tidak bisa dinilai pasti
- Isi tabel lampiran lebih dari 1.000 baris
- Bentuk panjang: pada "X yang selanjutnya disebut Y" yang dicari Y

### Cara memeriksa
Pakai `cari_teks` untuk TIAP istilah yang tampak tidak dipakai, sebelum
menyatakan tidak dipakai. Kutip istilahnya di definisi Pasal 1; isi
`tidak_ada` dengan istilah itu dan `alasan_buang: tidak_dipakai`.

### Bukan kesalahan
- Istilah yang hanya dipakai di lampiran — tetap terpakai
- Istilah yang ditulis huruf kecil di batang tubuh — tetap terpakai

## F2-106 · Lampiran dinyatakan di batang tubuh dan berformat baku

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: lampiran
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf E butir 120 dan 121 huruf b, c, dan h, hlm 57 (visual)
Butuh: —

### Yang diperiksa
- Tiap lampiran disebut pasal, berikut pernyataan bahwa lampiran merupakan bagian tidak terpisahkan dari Peraturan Menteri ini
- Lampiran yang disebut pasal memang ada, dan lampiran yang ada memang disebut pasal
- Salah ketik kata "Lampiran" di pasal atau di kepala lampiran
- Kepala lampiran: LAMPIRAN kapital, berangka Romawi bila lebih dari satu, judul PMK sama dengan halaman pertama
- Nama dan tanda tangan pejabat di akhir tiap lampiran
- Bilangan angka dan huruf di lampiran cocok

### Yang tidak diperiksa
- Tata letak — kanan dan tengah margin, nomor halaman
- Isi dan kebijakan lampiran
- Jumlah lampiran lebih dari satu — butir 121 huruf i hanya anjuran
- Isi tabel lebih dari 1.000 baris

### Cara memeriksa
Fakta lampiran yang dikumpulkan kode ada di tugas putaran — BUKAN
kesimpulan, pastikan sendiri di naskah. Muat skill `pmk-standar/lampiran`.
Temuan hanya boleh lahir dari pelanggaran salah satu butir yang diperiksa.

### Bukan kesalahan
- "Lampiran Surat" di tengah contoh format surat — bukan kepala lampiran

## F3-001 · Berpotensi bertentangan dengan peraturan lain

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran III huruf C keterangan angka 3 dan 4, hlm 89; Lampiran III huruf E Daftar I angka 2 huruf b, hlm 93 (visual)
Butuh: korpus

### Yang diperiksa
- Ketentuan yang menyangkut peraturan lain — pembandingnya dicari di korpus peraturan yang masih berlaku

### Yang tidak diperiksa
- Peraturan yang sudah dicabut atau status berlakunya tidak terbaca
- Peraturan yang tidak muncul di hasil pencarian

### Cara memeriksa
Muat skill `korpus`. Cari pembanding dengan `cari_korpus` memakai rumusan
ketentuannya. Bahasanya wajib "berpotensi bertentangan", tidak pernah
"bertentangan". `pembanding` disalin persis dari hasil `cari_korpus`.

### Bukan kesalahan
- "Tidak ketemu di korpus" — tidak pernah jadi temuan
- Perbedaan yang memang disengaja dan disebut alasannya di naskah

## F3-002 · Dasar hukum di Mengingat masih berlaku

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: seluruh naskah
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: korpus

### Yang diperiksa
- Tiap peraturan di Mengingat dicek status berlakunya di korpus

### Yang tidak diperiksa
- Bentuk di luar UU, Perppu, PP, Perpres, Keppres, PMK, dan KMK
- Peraturan yang tidak ketemu di korpus — tidak ketemu bukan bukti dicabut
- Dua dokumen bernomor sama berstatus berbeda
- Status di luar Berlaku dan Tidak Berlaku

### Cara memeriksa
`cek_peraturan` untuk tiap butir Mengingat. Hanya status "Tidak Berlaku" yang
tunggal jadi temuan. Kutip sebutan peraturannya sebelum kata "tentang"; isi
`status_peraturan` dengan sebutan dan status persis dari hasil
`cek_peraturan`. Status di korpus bisa tertinggal dari keadaan sebenarnya —
sebut itu di saran.

### Bukan kesalahan
- Hasil "tidak tahu" dari `cek_peraturan`

## F3-003 · Usulan rumusan dari peraturan yang masih berlaku

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C.1 butir 62 dan 65, hlm 45 (turunan)
Butuh: korpus

### Yang diperiksa
- Untuk calon temuan analisis lain yang usulannya belum bersumber dari naskah sendiri, rumusan dicontoh dari peraturan yang masih berlaku

### Yang tidak diperiksa
- Pencarian kesalahan baru — analisis ini hanya melengkapi temuan lain
- Kutipan lebih dari 200 huruf

### Cara memeriksa
Saat mencatat temuan analisis lain yang perlu rumusan pengganti, cari
rumusan serupa dengan `cari_korpus`. Bila ketemu di peraturan yang masih
berlaku, usulan mencontoh rumusannya dan `pembanding` disalin persis dari
hasilnya. Kode analisisnya tetap kode temuan asal.

### Bukan kesalahan
- Tidak ada rumusan serupa di korpus — temuan asalnya tetap, tanpa pembanding

## S-64 · Salah ketik

Berlaku untuk: pmk-standar
Respons: usulan
Lingkup: per pasal
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: —

### Yang diperiksa
- Kata yang salah ketik — huruf tertukar, hilang, atau berlebih — sehingga bukan kata baku

### Yang tidak diperiksa
- Istilah teknis, singkatan, nama diri, dan kata asing yang memang ditulis begitu
- Ejaan "Undang-Undang" di Mengingat — itu F1-005

### Cara memeriksa
Kutip KATA yang salah ketik itu saja; usulan = kata yang benar. Satu temuan
per kata.

### Bukan kesalahan
- Ejaan lama yang masih baku di peraturan, mis. "dan/atau"
- Kata yang sengaja disingkat di definisi
