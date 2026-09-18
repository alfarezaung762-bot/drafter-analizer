# Drafter Analiser

**Alat bantu telaah rancangan peraturan untuk Biro Hukum Kementerian Keuangan**

Magang · Biro Hukum, Bagian Hukum Kekayaan Negara dan Informasi Hukum
Versi 3.5 · September 2026

> Bagian 1–7 ringkas. Rincian tiap butir dibahas di Bagian 8.
>
> **Perubahan versi 3.3 (16 Sep 2026):** bagian 3, 4, 5, dan 6 disesuaikan
> setelah cara kerja penelaah yang sebenarnya diketahui dari mentor dan dari
> contoh RPMK/RKMK sungguhan — lihat bagian **8.13**, yang baru.
>
> **Perubahan versi 3.4 (17 Sep 2026):** kelayakan perubahan terlacak sudah
> dibuktikan langsung di Word penelaah (*8.13*). Tingkat keparahan temuan
> dihapus — warna tinggal satu, dan penjelasan pindah seluruhnya ke komentar.
>
> **Perubahan versi 3.5 (18 Sep 2026): Track Changes ditinggalkan.** Terbukti
> tidak bisa memenuhi syarat penelaah — warna revisinya tidak dapat diatur
> add-in sama sekali, sedangkan syaratnya penelaah tidak menyetel apa pun di
> Word. Alat sekarang menggambar tandanya sendiri: merah dicoret untuk yang
> salah, hijau untuk usulannya, blok kuning untuk yang perlu ditinjau tanpa
> jawaban pasti. Bagian 3, 4, 5, 6, 8.10, dan 8.13 disesuaikan. Alasan lengkap
> beserta buktinya di `docs/fase1 drafter.md` bagian 6.1.

> ## Untuk agen coding — baca ini dulu
>
> Dokumen ini menjelaskan **kenapa** alat ini dibangun dan **untuk siapa**.
> Bukan spesifikasi, bukan daftar pekerjaan.
>
> - Kalau bertentangan dengan `docs/fase1 drafter.md` soal cara kerja teknis,
>   **`fase1 drafter.md` yang berlaku.** Dokumen itu disamakan dengan kode
>   setiap kali kode berubah; brief ini menyusul.
> - **Bagian 8.11 bukan backlog.** Isinya dugaan yang disusun dari logika
>   dokumen, belum pernah dikonfirmasi ke penelaah. Jangan dibangun jadi aturan
>   sebelum dikonfirmasi.
> - **Fase 2 dan Fase 3 tidak dikerjakan sekarang.** Azure OpenAI dan OpenSearch
>   disebut di sini sebagai rencana, belum tersambung, dan tidak boleh disambung
>   atas inisiatif sendiri.
> - Yang paling perlu dipahami sebelum menyentuh kode: **bagian 6** (prinsip)
>   dan **bagian 8.13** (cara penelaah bekerja sebenarnya). Keduanya yang
>   menjelaskan kenapa alat ini menandai, bukan memperbaiki.

---

# 1. Latar Belakang

1. **Biro Hukum menelaah rancangan PMK/KMK** sebelum dibahas lintas instansi dan dibawa ke harmonisasi. Bagian tempat proyek ini dikerjakan bermitra dengan DJKN, sekaligus mengelola TIK dan JDIH. → *8.1*
2. **Volume 150–250 PMK per tahun** — rata-rata satu per hari kerja, belum termasuk KMK.
3. **Telaah adalah titik kritis.** Sesudahnya dokumen masuk forum lintas instansi; kekeliruan yang lolos jauh lebih mahal diperbaiki. → *8.2*
4. **Taruhannya besar.** PMK dapat mengikat seluruh kementerian/lembaga, bukan hanya internal Kemenkeu. → *8.3*
5. **Biro Hukum tidak berwenang memutuskan perubahan** rancangan secara sepihak — posisinya mengusulkan; yang menyepakati adalah rapat bersama unit pemrakarsa. Perhatikan: ini batas **kewenangan**, bukan larangan menyunting berkas. Penelaah memang rutin membuat versi rancangan yang sudah dimodifikasi sebagai bahan usulan. → *8.13*
6. **Acuan baku sudah ada:** KMK 527/KMK.01/2022, Lampiran II Teknik Penyusunan. → *8.4*
7. **Penyusunan elektronik sudah bermandat:** Pasal 97B UU 12/2011 jo. UU 13/2022. Prosedur resmi mensyaratkan penyampaian rancangan dalam format `.docx`. → *8.4*
8. **Perangkat yang tersedia:** JDIH, DPH, Law Analyzer, SDSN. → *8.5*

---

# 2. Masalah

1. **Telaah dikerjakan satu per satu.** Mengandalkan ketelitian dan ingatan; kesalahan sederhana justru sering lolos. → *8.6*
2. **Menyusun rumusan dari nol melelahkan.** Menerjemahkan gagasan menjadi bunyi pasal baku menuntut mencari rujukan, menyusun, lalu memeriksa ulang — berulang untuk tiap ketentuan.
3. **Hasil analisis terputus dari dokumen kerja.** Law Analyzer sudah mampu menganalisis rancangan, tetapi hasilnya hanya tampil di panel percakapan — tidak terstruktur, dan untuk tahu kata mana yang dimaksud penelaah harus menggeser panel dan dokumen bergantian. Makin banyak pasal, makin tidak terbaca.
4. **Dokumen besar tidak terlayani.** Analisis berjalan sampai selesai di server, namun antarmuka berhenti merespons sehingga hasilnya tidak dapat diakses. → *8.7*
5. **Rujukan dari AI umum sering mati**, dan rancangan yang belum terbit tidak layak dikirim ke layanan luar.
6. **Menyiapkan dua dokumen dikerjakan dua kali.** Penelaah memelihara versi bercoretan dan versi bersih secara terpisah, dengan isi yang sama. → *8.13*

---

# 3. Gagasan

> Penelaah membuka rancangan di Word, menekan satu tombol, dan bagian yang perlu
> ditinjau langsung tertandai di dokumen itu juga — lengkap dengan catatan,
> rujukan peraturan, dan **usulan rumusan yang seharusnya**. Tidak ada satu pun
> perubahan yang jadi permanen sebelum penelaah menyetujuinya.

1. **Hasil masuk ke dokumen, bukan panel terpisah.** Tidak ada penyalinan manual, tidak ada menggeser dua jendela untuk mencari kata yang dimaksud.
2. **Usulan ditampilkan di sebelah teks aslinya, bukan menggantikannya diam-diam.** Teks yang keliru diberi warna merah dan dicoret; usulan rumusannya disisipkan di sebelahnya dengan warna hijau. Teks lama **tidak dihapus**. Penelaah menyetujui atau menolaknya satu per satu dari panel. Alat tidak pernah menerapkan sendiri.
3. **Satu berkas, dua wujud.** Naskah kerja bertanda merah–hijau adalah versi bercoretan; versi bersih dihasilkan lewat ekspor terpisah. Tidak lagi dipelihara dua berkas sejak awal.
4. **Menyisir sistematis, bukan menunggu ditanya.** Tidak ada pasal terlewat.

**Pengguna:** perancang dan penelaah internal Biro Hukum. Bukan masyarakat umum.

---

# 4. Ruang Lingkup Pemeriksaan

Tiga hal, sesuai arahan mentor agar cakupan dibatasi dan dikerjakan bertahap.

| Fase | Yang diperiksa | Cara | Asal |
|---|---|---|---|
| 1 | **Kesalahan format baku** — judul kapital, kelengkapan Menimbang/Mengingat/Menetapkan, frasa baku pada butir Menimbang terakhir, judul pembuka sama dengan judul di badan dokumen, ejaan | aturan biasa, tanpa AI | disebut tim |
| 2 | **Cara mendefinisikan ketentuan** — termasuk norma yang berpotensi multitafsir | sebagian mekanis, sebagian AI | prioritas mentor |
| 3 | **Potensi pertentangan dengan peraturan lain** | pencarian pembanding + AI | prioritas mentor |

Fase 1 didahulukan karena hasilnya pasti, cepat, dan sudah langsung berguna.
Fase 1 juga yang membuktikan skema penandaannya enak dibaca penelaah — cara
menampilkan temuan Fase 2 dan 3 baru diputuskan setelah itu terbukti.

## Cara Alat Bekerja

- Memeriksa rancangan yang terbuka di Word, tanpa mengunggah berkas
- Menandai teks yang keliru dengan warna merah dan coretan, lalu menyisipkan usulan rumusannya di sebelahnya dengan warna hijau — bisa disetujui atau ditolak per butir dari panel
- Menandai temuan yang tidak punya rumusan pengganti dengan blok kuning dan komentar
- Menaruh alasan dan rujukan butir KMK 527 di komentar — dua baris, bukan diulang di panel
- Memilih jenis pemeriksaan sebelum dijalankan
- Memilih cakupan: seluruh dokumen atau bagian terpilih
- Menghasilkan versi bersih lewat ekspor, tanpa mengetik ulang *(belum dibangun — dua jalurnya di `docs/fase1 drafter.md` bagian 6.7)*

## Di Luar Lingkup

Menerapkan usulan tanpa persetujuan penelaah · menghapus teks penelaah atas
inisiatif kode · validasi gambar logo Garuda · deteksi "kelaziman" · versi untuk
masyarakat umum · menulis apa pun ke basis data produksi

Kemungkinan pemeriksaan lain yang belum dikonfirmasi: *8.11*

# 5. Cara Kerja

```
1. Buka rancangan di Word
2. Pilih jenis pemeriksaan, tekan Analisis
3. Pemeriksaan formal keluar lebih dahulu — hitungan detik
4. Teks yang keliru jadi merah dan dicoret, usulannya muncul hijau di
   sebelahnya; temuan tanpa pengganti diberi blok kuning + komentar
5. Alasan dan rujukan dibaca di komentar, di tempat kesalahannya
6. Penelaah menyetujui atau menolak tiap usulan lewat panel add-in
7. Versi bersih dihasilkan lewat ekspor; naskah kerja bercoretan tetap utuh
8. Pemeriksaan pertentangan menyusul di latar belakang (Fase 3)
```

```
Word (dokumen terbuka)
  └── Panel  ──── baca paragraf lewat Office.js
        ▼
     Backend
        ├── pemeriksaan formal      aturan biasa, tanpa AI
        ├── pemeriksaan mekanis     pencocokan silang definisi & rujukan
        ├── pencarian pembanding    OpenSearch, akses baca saja
        └── penyusunan catatan      model, terikat hasil pencarian
        ▼
     daftar temuan  ──→  digambar ke dokumen sebagai tanda merah/hijau/kuning
                          + komentar, menurut jenisnya
```

Penanganan dokumen besar dibahas di *8.9*.

---

# 6. Prinsip dan Batasan

## Prinsip

1. **Rekomendasi, bukan keputusan.** Usulan dipasang dalam keadaan mentah dan
   selalu bisa dibatalkan satu klik. Tidak ada kode yang menerapkan usulan atas
   inisiatif sendiri, tidak ada "terapkan semua".
2. **Bahasa halus.** "Berpotensi bertentangan dengan…", bukan "bertentangan".
3. **Setiap temuan membawa bukti** — nomor peraturan, pasal, kutipan, tautan JDIH. Diambil dari hasil pencarian, tidak boleh dikarang model.
4. **Dokumen tidak boleh rusak.** Menolak usulan mengembalikan naskah persis
   seperti semula, tanpa bekas. Hasil telaah tetap aman dibawa ke harmonisasi.
5. **Sederhana dahulu.** Yang dapat diselesaikan aturan biasa tidak melibatkan AI.
6. **Satu penjelasan, satu tempat.** Alasan temuan ditulis sekali di komentar,
   tidak diulang di panel. Panel hanya untuk navigasi dan keputusan.

## Batasan

1. Korpus pembanding mencakup peraturan Kemenkeu secara keseluruhan (pajak, kepabeanan, anggaran, perbendaharaan, kekayaan negara, dan domain lain) — pertentangan dengan peraturan **kementerian/lembaga di luar Kemenkeu** tetap ranah harmonisasi. → *8.12*
2. Korpus memuat pula peraturan yang sudah dicabut; penyaringan dilakukan sistem.
3. Temuan bersifat kemungkinan, bukan kesimpulan.
4. Usulan yang belum diputuskan bersifat mentah: tampil sebagai tanda warna
   dan komentar, dan hilang tanpa bekas bila ditolak. Yang disetujui tetap
   terbaca di naskah kerja sebagai bahan rapat, dan baru diterapkan pada versi
   ekspor.
5. **Word tidak tahu tanda ini usulan mesin.** Karena alat menggambar sendiri
   dan tidak memakai Track Changes, tab Review menunjukkan nol revisi,
   Accept All/Reject All bawaan Word tidak melakukan apa-apa, dan tidak ada
   nama pengusul maupun waktunya. Yang mengenali tandanya hanya add-in, lewat
   content control bertag miliknya sendiri. Ini pertukaran yang disadari:
   rekam resmi Word ditukar dengan warna merah–hijau yang dituntut penelaah,
   tanpa penelaah menyetel apa pun. → *8.13*
6. Waktu proses pada dokumen besar tidak hilang — hanya ditangani agar tidak menggagalkan hasil. → *8.9*

Daftar risiko dan penanganannya di *8.10*.

---

# 7. Pengukuran dan Langkah Berikutnya

## Cara mengukur

Belum tersedia data acuan "pasal ini bertentangan dengan pasal itu" — catatan
telaah internal tidak pernah dipublikasikan. Pendekatannya: mengumpulkan **5–10
rancangan yang sudah pernah ditelaah** beserta catatan koreksinya, lalu
membandingkan hasil sistem terhadap catatan tersebut.

## Urutan pengerjaan

```
1. Uji kelayakan penyisipan sorotan di Word          — selesai
2. Tetapkan bentuk data temuan                        — selesai
3. Satu alur utuh dengan satu aturan paling sederhana — selesai
4. Lengkapi aturan Fase 1                             — selesai
5. Uji kelayakan perubahan terlacak di Word           — selesai, tapi jalurnya
                                                        ditinggalkan (8.13)
6. Pasang skema penandaan merah/hijau/kuning          — selesai, terbukti di
                                                        naskah nyata
7. Ekspor versi bersih                                — belum, jalurnya belum
                                                        diputuskan
8. Lengkapi tabel rujukan KMK 527                     — belum, pekerjaan manusia
9. Fase 2, lalu Fase 3
```

## Yang masih perlu dipastikan

1. **Apa saja yang sebenarnya diperiksa penelaah.** Sebagian sudah terjawab
   lewat keterangan mentor (*8.13*), tetapi daftar butir pemeriksaan di *8.11*
   masih berupa dugaan dan belum dikonfirmasi ke penelaah yang mengerjakan
   telaah sehari-hari.
2. ~~Rancangan yang sudah ditelaah beserta catatan koreksinya.~~ **Sudah
   diperoleh** — mentor memberikan sejumlah RPMK/RKMK beserta coretan telaahnya.
   Berikutnya: memakainya sebagai bahan uji, membandingkan temuan sistem dengan
   koreksi manusia.
3. Keandalan penanda relasi antar-peraturan. → *8.10*
4. ~~Apakah perubahan terlacak benar-benar bisa dipasang lewat Office.js.~~
   **Sudah dibuktikan 17 Sep 2026**, tetapi jalurnya tetap ditinggalkan sehari
   kemudian karena warnanya tidak bisa diatur. → *8.13*
5. **Bunyi butir 22 KMK 527 yang sebenarnya.** Dokumen pengetahuan proyek
   menulis butir terakhir "**wajib** berbunyi baku"; hasil ekstraksi PDF-nya
   menulis "**pada umumnya** berbunyi". Satu kata itu menentukan apakah aturan
   F1-004 menemukan kesalahan atau sekadar ketidaklaziman. OCR-nya rusak, jadi
   harus diperiksa visual pada naskah aslinya — butir 22, halaman 35.

---

# 8. Rincian

## 8.1 Kedudukan Biro Hukum

Berada di bawah Sekretariat Jenderal, terdiri atas enam bagian (PMK 124/2024
Pasal 60, sebagaimana telah diubah dengan PMK 117/2025 — perubahan tersebut
menyangkut penataan organisasi Direktorat Jenderal Pajak). Masing-masing bagian
menjadi mitra telaah bagi kelompok unit Eselon I tertentu.

Litigasi bukan tugas Biro Hukum. Gugatan atas PMK ditangani **Biro Advokasi**,
biro terpisah di bawah Setjen yang sama.

Produk hukum yang ditelaah terbatas pada **PMK dan KMK**. Peraturan tingkat
Eselon I ke bawah dikelola unit masing-masing.

## 8.2 Alur Penyusunan dan Posisi Telaah

```
1. Unit pemrakarsa (DJKN) menyusun rancangan
2. ► TELAAH BIRO HUKUM ◄
3. Pembahasan dengan kementerian/lembaga terkait
4. Harmonisasi di Kementerian Hukum — melibatkan K/L lain
5. Kembali ke Biro Hukum untuk finalisasi
6. Penetapan Menteri Keuangan
7. Pengundangan (khusus PMK) — nomor Berita Negara
8. Penyebarluasan melalui JDIH
```

Bila kekeliruan lolos sampai terbit, jalan keluarnya hanya tiga: revisi melalui
PMK Perubahan, pencabutan dan penggantian, atau gugatan masyarakat ke Mahkamah
Agung.

## 8.3 Kedudukan PMK dalam Sistem Hukum

PMK tidak termasuk hierarki Pasal 7 UU 12/2011. Keberadaannya diakui melalui
Pasal 8, dan mengikat sepanjang diperintahkan peraturan yang lebih tinggi atau
dibentuk berdasarkan kewenangan. Praktisnya berada di bawah Perpres.

PMK dapat mengikat ke luar Kemenkeu. Untuk Barang Milik Negara, Menteri Keuangan
berkedudukan sebagai Pengelola Barang sementara Pengguna Barang adalah seluruh
menteri dan pimpinan lembaga — sehingga PMK-nya mengikat seluruh
kementerian/lembaga.

## 8.4 Dasar Baku dan Mandat

| Rujukan | Isi |
|---|---|
| UU 12/2011 jo. UU 13/2022 | pembentukan peraturan; asas kejelasan rumusan |
| **Pasal 97B** UU 12/2011 jo. UU 13/2022 | pembentukan peraturan **dapat dilakukan secara elektronik** |
| PMK 164/PMK.01/2021 | Pedoman Tata Naskah Dinas; untuk peraturan perundang-undangan menunjuk balik ke ketentuan pembentukan peraturan |
| **KMK 527/KMK.01/2022** | Pedoman Pembentukan Peraturan dan Keputusan di Lingkungan Kemenkeu — Lampiran II Teknik Penyusunan |

Pasal 97B dikutip KMK 527 pada butir Menimbang pertamanya. Dengan demikian alat
bantu digital pada proses penyusunan berpijak pada mandat yang ada.

Catatan: salinan KMK 527 dan PMK 164 di JDIH keduanya hasil pemindaian yang
di-OCR, dan teksnya memuat kesalahan pengenalan karakter. Aturan pemeriksaan
harus diturunkan dari naskah yang diverifikasi secara visual.

## 8.5 Perangkat yang Tersedia

| Sistem | Fungsi |
|---|---|
| **JDIH** | penyebarluasan peraturan ke publik; sumber dokumen |
| **DPH** | aplikasi induk, tersusun mengikuti tahapan penyusunan |
| **Law Analyzer** | asisten AI: tanya bebas, penyusun draf, analisis hukum, matriks persandingan, pembuat slide. Tersedia pula sebagai panel di Word |
| **SDSN** | penggabungan peraturan induk dengan seluruh perubahannya |

Alur datanya: JDIH mendorong pemberitahuan ke Law Analyzer, dokumen diuraikan
pekerja latar belakang, hasilnya disimpan ke OpenSearch. Pencarian AI membaca
dari OpenSearch, bukan dari basis data JDIH.

Gambaran skala: pemakaian model pada Law Analyzer sekitar Rp7,5 juta per bulan,
dengan pengajuan Rp80 juta untuk 2026.

## 8.6 Kesalahan yang Berulang

- Judul pembuka berbeda satu kata dengan judul pada "Menetapkan"
- Butir Menimbang terakhir tidak memuat frasa baku "perlu menetapkan … tentang"
- Urutan "Mengingat" tidak sesuai hierarki
- Logo Garuda salah arah kepala, tanpa bintang, atau tanpa tulisan pengiring
- Istilah dipakai tidak konsisten dengan definisi di Pasal 1

## 8.7 Temuan Pengujian: Dokumen Besar

Pada PMK 124/2024 (175 satuan pasal/ayat), analisis di server berjalan sampai
selesai, namun antarmuka berhenti merespons di tengah jalan — dan tetap macet
setelah halaman dimuat ulang.

| Percobaan | Konteks tambahan | Berhenti di |
|---|---|---|
| 1 | ringkas | 68/175 |
| 2 (dua kali) | panjang & rinci | 17/175 |
| 3 | ringkas | 68/175 |

Titik berhenti selalu sama untuk isi yang sama — menunjukkan penyebabnya beban
penggambaran hasil, bukan kegagalan acak atau batas waktu.

Rancangan ini menghindarinya karena penggambaran ditangani Word, dengan syarat:
panel hanya menampilkan daftar ringkas, hasil ditambahkan tanpa menggambar ulang
seluruh daftar, jumlah tampil dibatasi, dan penandaan disisipkan per kelompok.

## 8.8 Pemeriksaan Tanpa AI

Aturan biasa cukup bila pertanyaannya berjawaban pasti — kapital atau tidak, ada
atau tidak ada, sama atau berbeda, urutannya benar atau tidak.

| | Aturan biasa | Dengan AI |
|---|---|---|
| Hasil | selalu sama untuk dokumen yang sama | dapat berbeda tiap dijalankan |
| Ketepatan | pasti | dapat salah tebak |
| Waktu | hitungan detik | menit sampai jam |
| Biaya | nol | dibayar per satuan |
| Bila salah | dapat ditunjukkan aturan mana yang keliru | sulit dilacak |

Seluruh pemeriksaan Fase 1 dapat dikerjakan tanpa AI — dan justru itu yang paling
sering menjadi bahan koreksi harian.

## 8.9 Penanganan Dokumen Besar dan Pasal Panjang

- Satuan pemeriksaan **ayat/butir**, bukan pasal — agar pencarian tajam dan
  penandaan presisi. PMK 124/2024 memuat 144 pasal namun 175 satuan pasal/ayat.
- Pemeriksaan murah dijalankan dan ditampilkan lebih dahulu.
- Pemrosesan di latar belakang; hasil disimpan per satuan sehingga yang sudah
  selesai tetap dapat diakses meskipun proses terputus.
- Penyaringan: satuan yang tidak memuat norma tidak perlu dicari pembandingnya.

Untuk kesinambungan lintas dokumen, dibuat peta lebih dahulu:

| Tahap | Yang dipegang model | Ukuran |
|---|---|---|
| 1. Meringkas | satu pasal, diulang sebanyak pasalnya | kecil |
| 2. Menalar | seluruh baris ringkasan + Menimbang + Mengingat + definisi | kecil |
| 3. Memastikan | hanya pasal yang dicurigai, dibaca utuh | kecil |

Tahap 3 tidak boleh dilewat: ringkasan kehilangan detail, sehingga kejanggalan
pada tahap 2 masih berupa dugaan, belum temuan.

## 8.10 Risiko dan Penanganan

| Risiko | Penanganan |
|---|---|
| Terlalu banyak salah tandai | ambang skor; mulai dari pemeriksaan formal yang pasti benar |
| Menyitir pasal yang sudah dicabut | filter status berlaku sebagai penyaring keras |
| Model mengarang nomor peraturan | catatan hanya boleh menyebut yang ada di hasil pencarian |
| Usulan rumusan keliru namun tampak meyakinkan | ditampilkan mentah di sebelah teks aslinya, disertai rujukan, dan ditolak dengan satu klik |
| **Usulan alat tertukar dengan suntingan penelaah sendiri** | tiap tanda dibungkus content control bertag `DA-ASLI-{n}`/`DA-USUL-{n}` dan disertai komentar berpenanda; tanpa add-in, merah–hijau itu terbaca sebagai teks berwarna biasa |
| **Tanda tertinggal bila Word ditutup sebelum temuan diputuskan** | tombol Bersihkan Daftar mencabut seluruh tanda bertag `DA-*`; warna asli disimpan di memori panel, jadi penelaah tetap wajib memeriksa ulang |
| **Salah tandai pada naskah yang sebenarnya benar** | kaidah mengikat: apa pun yang ditandai wajib benar-benar salah; aturan yang tidak bisa membuktikannya dimatikan, bukan diperhalus. Empat kasus nyata dan perbaikannya di `docs/fase1 drafter.md` bagian 6.10 |
| Metadata relasi antar-peraturan keliru | ditemukan kekeliruan data pada riwayat dokumen — peraturan tahun lebih awal tercatat mencabut peraturan tahun lebih akhir; perlu pemeriksaan kewajaran tahun |
| Kerahasiaan rancangan | kredensial hanya di sisi server; pengembangan memakai dokumen contoh |

## 8.11 Kemungkinan Pemeriksaan Lain — Belum Dikonfirmasi

Butir berikut disusun dari logika dokumen dan ketentuan KMK 527, **bukan** dari
keterangan penelaah. Belum ada bukti bahwa hal-hal ini termasuk yang diperiksa
dalam praktik. Perlu dikonfirmasi lebih dahulu sebelum dijadikan aturan.

| Kemungkinan pemeriksaan | Pijakan |
|---|---|
| Urutan "Mengingat" sesuai hierarki | KMK 527 Lampiran II |
| Penomoran bertingkat Pasal → Ayat → Huruf → Angka | KMK 527 Lampiran II |
| Setiap lampiran dirujuk "bagian tidak terpisahkan" | KMK 527 Lampiran II |
| Penempatan konjungsi "dan" / "atau" / "dan atau" | KMK 527 Lampiran II |
| Istilah di Pasal 1 dipakai konsisten di pasal lain | asas kejelasan rumusan |
| Istilah berkapital yang tidak ada dalam daftar definisi | asas kejelasan rumusan |
| Definisi yang tidak pernah dipakai | logika dokumen |
| Rujukan "sebagaimana dimaksud dalam Pasal N" menunjuk pasal yang ada | logika dokumen |
| Peraturan pada "Mengingat" sudah dicabut atau sudah diubah | logika dokumen |
| Pemakaian kata operasional: wajib / dilarang / dapat / harus | asas kejelasan rumusan |
| Tujuan pada Menimbang tercakup di batang tubuh | logika dokumen |
| Peraturan sumber delegasi tercantum dalam Mengingat | Pasal 8 UU 12/2011 |
| Antar-pasal tidak saling bertabrakan | logika dokumen |

**Cara mengonfirmasi:** bawa daftar Fase 1–3 kepada penelaah yang mengerjakan
telaah sehari-hari, lalu tanyakan apa lagi yang biasanya diperiksa, apa yang
paling sering salah, dan apa yang paling melelahkan. Daftar ini tumbuh dari
keterangan mereka, bukan dari penyusunan di depan.

Pendekatan ini sejalan dengan saran mentor bahwa observasi lebih sesuai daripada
kuesioner untuk alat yang bersifat inovasi.

Sekarang ada jalan konfirmasi kedua yang lebih murah: membandingkan temuan
sistem dengan coretan telaah pada RPMK/RKMK yang sudah diberikan mentor. Apa
yang berulang kali dikoreksi manusia di sana adalah bukti, bukan dugaan.

## 8.12 Cakupan Korpus vs Cakupan Penggunaan

Dua hal berbeda yang mudah tertukar.

**Cakupan korpus** (apa yang bisa dicari sebagai pembanding): kemungkinan besar
**seluruh Kemenkeu**, bukan hanya Kekayaan Negara. Batas "peraturan kementerian
lain" pada poin batasan merujuk pada kementerian/lembaga **di luar Kemenkeu** —
bukan Ditjen lain di dalamnya.

Struktur organisasi Kemenkeu (Perpres 158/2024; PMK 124/2024) menunjukkan Ditjen
Pajak, Ditjen Bea dan Cukai, Ditjen Anggaran, Ditjen Perbendaharaan, Ditjen
Kekayaan Negara, Ditjen Perimbangan Keuangan, dan lainnya berkedudukan sejajar,
langsung di bawah Menteri Keuangan — satu kementerian yang sama. "Peraturan
keuangan negara" sebagai kategori mencakup seluruh domain itu, bukan hanya
topik kekayaan negara secara sempit.

*Catatan kejujuran:* kesimpulan ini berdasarkan penjelasan lisan, belum
diverifikasi langsung dengan memeriksa isi index. Layak dikonfirmasi ulang bila
menjadi dasar keputusan besar.

**Cakupan penggunaan** (siapa yang memakai alat ini sekarang): dibatasi ke
Bagian Hukum Kekayaan Negara dan Informasi Hukum — bukan karena keterbatasan
teknis, melainkan karena itu bagian yang mengajukan dan mendapat persetujuan
mentor. Fase 1 dan Fase 2 (berdasarkan KMK 527) berlaku sama untuk PMK/KMK topik
apa pun, tidak spesifik ke Kekayaan Negara.

Implikasinya: memperluas penggunaan ke bagian lain kelak adalah keputusan
organisasi yang butuh persetujuan terpisah — bukan pembangunan ulang dari sisi
teknis.

## 8.13 Cara Penelaah Bekerja dalam Praktik

*Sumber: keterangan mentor, diperkuat sejumlah RPMK/RKMK sungguhan beserta
coretan telaahnya yang diberikan mentor (September 2026). Bagian ini mengubah
beberapa asumsi yang sebelumnya dipegang — lihat "Akibatnya" di bawah.*

### Yang sebenarnya terjadi

Setelah rancangan diterima dari unit pemrakarsa, penelaah umumnya menyiapkan
**dua dokumen**:

1. **Versi bercoretan.** Teks yang dinilai keliru dicoret, usulan perbaikan
   ditulis dengan warna berbeda. Contoh yang diberikan memakai merah untuk yang
   dicoret, biru atau hijau untuk usulan, dan sorotan kuning untuk bagian yang
   dipersoalkan.
2. **Versi bersih.** Isi yang sama tanpa coretan, sudah dimodifikasi menurut
   usulan penelaah — supaya unit pemrakarsa mudah membacanya.

Keputusan akhir **tidak** diambil oleh penelaah. Kedua dokumen dibawa ke rapat
pembahasan bersama unit pemrakarsa; yang berlaku adalah yang disepakati di sana.
Prosesnya bisa selesai dalam satu rapat, bisa juga berminggu-minggu.

### Tidak ada standar bentuk

Tidak ada ketentuan baku tentang bagaimana coretan itu harus ditampilkan. Warna,
cara mencoret, dan tata letak catatan diserahkan ke masing-masing penelaah.
Yang mengikat hanya hasil akhirnya: naskah bersih yang disepakati kedua pihak.

### Akibatnya bagi rancangan alat ini

- **Menyunting salinan rancangan itu hal biasa**, bukan pelanggaran. Yang
  dilarang adalah memutuskan sepihak. Asumsi lama bahwa alat "tidak boleh
  mengubah satu karakter pun" terlalu lebar — yang benar: tidak boleh ada
  perubahan yang jadi permanen tanpa persetujuan penelaah.
- **Track Changes sempat dikira padanan langsung dari alur ini — dan itu
  keliru.** Kelayakannya memang terbukti 17 Sep 2026 di Word 2024 LTSC
  penelaah: `changeTrackingMode` terbaca, bisa diset `"TrackAll"` dan
  dikembalikan, penggantian tercatat sebagai revisi, tanpa `NotImplemented`.
  Tetapi sehari kemudian jalurnya ditinggalkan, karena dua hal:
  1. **Warna revisi tidak bisa diatur add-in sama sekali.** Office.js tidak
     punya propertinya; Word mewarnai menurut penulis. Satu-satunya cara
     mengubahnya adalah Options Word di tiap komputer — sedangkan syarat yang
     ditetapkan penelaah adalah tidak menyetel apa pun di Word.
  2. **Memberi blok warna selagi pelacakan menyala** membuat Word mencatat tiap
     pewarnaan sebagai revisi `Formatted: Highlight`, memenuhi margin dan
     mengubur komentar yang justru perlu dibaca.
- **Gantinya: alat menggambar tandanya sendiri**, dengan pelacakan perubahan
  dimatikan sepanjang penandaan lalu mode semula dikembalikan. Merah dicoret
  untuk yang salah, hijau untuk usulannya, blok kuning untuk yang perlu
  ditinjau tanpa jawaban pasti. Persis warna yang dipakai penelaah di contoh
  coretan mereka sendiri.
- **Yang hilang sebagai gantinya: rekam resmi Word.** Tab Review menunjukkan nol
  revisi, Accept All tidak melakukan apa-apa, dan versi bersih harus dibangun
  sendiri — Word tidak punya apa pun untuk diterima. Pertukaran ini diterima
  penelaah 18 Sep 2026 dengan alasan: alat ini membantu menelaah, penelaah tetap
  wajib memeriksa ulang.
- **Naskah kerja merah–hijau itulah versi bercoretan.** Versi bersih dibuat
  lewat ekspor terpisah — belum dibangun.

Rinciannya, termasuk pembagian temuan ke dua kelas penandaan, ada di
`docs/fase1 drafter.md` bagian 6.
