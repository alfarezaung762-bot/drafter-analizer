# Cek List Fase 1 — apa yang benar-benar diperiksa

> Disusun menurut **bagian naskah**, bukan menurut kode aturan. Gunanya satu:
> supaya bisa dibaca sambil membuka rancangan, bagian per bagian, untuk tahu
> mana yang sudah dijaga alat dan mana yang **masih harus diperiksa sendiri**.
>
> Kode aturan (`F1-005`, dst.) dicantumkan hanya sebagai jalan menelusuri ke
> kodenya. Kode itu tidak pernah muncul di panel maupun di komentar Word.
>
> **Aturan pemeliharaan.** Berkas ini keterangan ketiga tentang hal yang sama,
> setelah `backend/app/rules/format_baku.py` (yang menjalankan) dan
> `frontend/src/lib/aturan-fase1.ts` (yang dibaca penelaah di panel
> Pengaturan). Kalau aturannya berubah, **ketiganya diubah di commit yang
> sama.** Yang berlaku kalau bertentangan: `format_baku.py`. Cara membuktikan
> berkas ini masih benar ada di bagian terakhir.
>
> Status: sesuai kode per 21 Sep 2026, 11 aturan aktif dari 12.

---

## Ringkasan sebaris

| Bagian naskah | Diperiksa? |
|---|---|
| Judul pembuka | **ya** — tanda baca penutup, dan kesamaan dengan judul di Menetapkan |
| Menimbang | **ya** — penulisan labelnya, bentuk tiap butir, bunyi butir terakhir |
| Mengingat | **ya** — penulisan labelnya, tanda baca tiap dasar hukum, ejaan baku |
| MEMUTUSKAN | **tidak** — hanya dipakai sebagai penanda letak, penulisannya sendiri tidak diperiksa |
| Menetapkan | **ya** — penulisan labelnya, bentuk judulnya |
| Kelengkapan ketiga bagian wajib | **ya** |
| Batang tubuh (BAB, Pasal, ayat) | **TIDAK SAMA SEKALI** |
| Lampiran | **TIDAK SAMA SEKALI** |
| Penutup (Ditetapkan/Diundangkan, tanda tangan) | **TIDAK SAMA SEKALI** |

Tiga baris terakhir itu bukan kelalaian — Fase 1 sengaja berhenti di pembukaan
dan diktum. Buktinya di bagian [Yang tidak disentuh sama sekali](#yang-tidak-disentuh-sama-sekali).

---

## ⚠ Satu hal yang menentukan segalanya: penanda `MEMUTUSKAN`

Kata itu dipakai seluruh aturan untuk tahu di mana pembukaan berakhir dan
diktum dimulai. Kalau paragrafnya tidak ketemu, **lima dari sebelas aturan
mati sekaligus, tanpa peringatan apa pun.** Sudah diuji:

| Keadaan | Aturan yang masih jalan |
|---|---|
| Ada `MEMUTUSKAN` | F1-002, F1-005, F1-007, F1-009, F1-011, F1-012 |
| **Tidak ada** | **F1-005 saja** |

Itu disengaja — menebak letak klausul Menetapkan tanpa penanda itu sudah
pernah membuat alat menuduh isi Pasal 4 sebagai judul yang salah. Tetapi
akibatnya perlu diketahui: **analisis yang mengembalikan sangat sedikit temuan
belum tentu berarti naskahnya bersih.** Periksa dulu apakah `MEMUTUSKAN`-nya
terbaca.

Bentuk yang dikenali — paragraf yang isinya **hanya** kata itu:

| Tertulis | Dikenali? |
|---|---|
| `MEMUTUSKAN:` | ya |
| `MEMUTUSKAN :` | ya |
| `MEMUTUSKAN` (tanpa titik dua) | ya |
| `M E M U T U S K A N :` (berspasi huruf) | ya |
| `Menteri memutuskan:` (di tengah kalimat) | **tidak** — dan memang tidak boleh |

---

# PMK

## 1. Judul

Yang dianggap "judul": seluruh paragraf **sesudah** baris yang isinya persis
`TENTANG`, sampai bertemu `DENGAN RAHMAT TUHAN YANG MAHA ESA`.

### Yang diperiksa

- **Judul tidak boleh diakhiri tanda baca** — titik, koma, titik koma, atau
  titik dua. *(F1-006, butir 8)*
  Yang ditandai kata terakhirnya beserta tanda bacanya, dicoret merah, dengan
  usulan hijau berupa kata yang sama tanpa tanda bacanya.
- **Judul harus sama persis dengan judul yang diulang di klausul Menetapkan**
  — dibandingkan kata per kata. *(F1-002, butir 39)*
  Yang ditandai hanya **kata yang berbeda**, diblok kuning, di sisi Menetapkan.
  Alat tidak menentukan mana dari dua judul itu yang benar — itu keputusan
  penelaah.

### Yang TIDAK diperiksa

- **Apakah judulnya ditulis kapital seluruhnya.** *(F1-001 — dimatikan)*
  Aturannya ada di kode tetapi tidak dijalankan. Sebabnya: alat tidak bisa
  membedakan judul yang hurufnya memang campur dari judul yang **tersimpan**
  campur tetapi **ditampilkan** kapital lewat gaya paragraf ALL CAPS. Pada
  RKMK sungguhan hal itu membuat alat menandai judul yang di mata penelaah
  sudah benar. **Periksa kapitalnya sendiri.**
- Singkatan atau akronim di dalam judul, berikut keempat pengecualian yang
  disebut butir 8 huruf a–d.
- Letaknya di tengah margin — itu tata letak, tidak terbaca dari teks.
- Penulisan nomor dan tahunnya.

### Kapan aturannya memilih diam

- Tidak ada baris yang isinya persis `TENTANG` → seluruh pemeriksaan judul mati.
- Tidak ada `DENGAN RAHMAT TUHAN YANG MAHA ESA` → batas akhir judul tidak
  ketemu, judulnya tidak terbaca.
- Untuk F1-002: tidak ada `MEMUTUSKAN` di dokumen → klausul Menetapkan tidak
  bisa dipastikan letaknya → diam.
- Untuk F1-002: judul hasil pengambilan lebih dari 60 kata → dianggap
  pengambilan yang gagal → diam.

---

## 2. Menimbang (konsiderans)

Rentangnya: dari paragraf yang diawali `Menimbang` sampai paragraf yang
diawali `Mengingat`.

### Yang diperiksa

- **Kata "Menimbang" ditulis huruf awal kapital, selebihnya huruf kecil.**
  *(F1-007, butir 16)* `MENIMBANG` dan `menimbang` dua-duanya menyimpang.
  Dicoret merah dengan usulan hijau `Menimbang`.
- **Kata "Menimbang" diakhiri titik dua (`:`).** *(F1-007, butir 16)*
  Diblok kuning pada kata labelnya saja.
- **Tiap butir diawali kata "bahwa".** *(F1-008, butir 21)* Diblok kuning pada
  awal butirnya.
- **Tiap butir diakhiri titik koma (`;`).** *(F1-008, butir 21)* Diblok kuning
  pada satu karakter terakhir **butir itu sendiri** — bukan karakter terakhir
  paragraf, karena satu paragraf bisa memuat beberapa butir sekaligus.
- **Butir terakhir memakai rumusan lazim butir 22.** *(F1-004)* Empat hal
  diperiksa sekaligus:
  1. ada frasa `berdasarkan pertimbangan sebagaimana dimaksud dalam huruf`;
  2. ada frasa `perlu menetapkan`;
  3. ada nama jenis **`Peraturan Menteri Keuangan`** diikuti kata `tentang`;
  4. diakhiri titik koma.

  Kekurangan apa pun dari keempatnya disebut satu per satu di komentarnya.

> **Butir 22 tidak imperatif.** Naskahnya berbunyi *"pada umumnya berbunyi
> sebagai berikut"*, bukan "wajib". Karena itu komentar F1-004 sengaja
> berbunyi "berbeda dari rumusan yang lazim", bukan menyatakan naskahnya
> salah. Penelaah yang menimbang apakah perbedaannya perlu dibetulkan.

### Yang TIDAK diperiksa

- **Apakah huruf yang dirujuk butir terakhir benar-benar ada.** Kalau butir c
  menyebut "sebagaimana dimaksud dalam huruf d" padahal huruf d tidak ada,
  alat tidak tahu.
- Isi pertimbangannya, urutannya, maupun nalarnya.
- Penomoran hurufnya sendiri (a, b, c berurutan atau tidak).
- **Konsiderans yang cuma satu butir tanpa huruf** — bentuk yang sah menurut
  butir 19, jadi F1-004 melewatinya sama sekali.

### Kapan aturannya memilih diam

- Tidak ada `MEMUTUSKAN` di dokumen → F1-007 diam, karena batas pembukaan
  tidak bisa dipastikan.
- **Paragraf labelnya cuma berbunyi `Menimbang` tanpa apa pun sesudahnya** →
  pemeriksaan titik dua diam. Pada naskah **bertabel**, titik duanya ada di
  sel sebelah dan tidak terbaca dari paragraf itu — tidak bisa dibuktikan
  hilang, jadi tidak dituduhkan.
- Potongan butir lebih pendek dari 15 karakter → dianggap hasil pemecahan yang
  gagal, dilewati.
- Paragraf tempat sebuah butir berada tidak ketemu → butir itu dilewati.
- Butir terpotong antarparagraf → pemeriksaan titik komanya diam, karena ujung
  butirnya tidak bisa dipastikan.
- Hanya kemunculan **pertama** kata `Menimbang` sebelum `MEMUTUSKAN` yang
  diperiksa. Kata yang sama di batang tubuh atau lampiran bukan label bagian.

---

## 3. Mengingat (dasar hukum)

Rentangnya: dari paragraf yang diawali `Mengingat` sampai bertemu
`MEMUTUSKAN`, `Menetapkan`, `BAB `, atau `Pasal `.

### Yang diperiksa

- **Kata "Mengingat" ditulis huruf awal kapital, selebihnya huruf kecil.**
  *(F1-009, butir 23)*
- **Kata "Mengingat" diakhiri titik dua (`:`).** *(F1-009, butir 23)*
- **Tiap dasar hukum diakhiri titik koma (`;`).** *(F1-010, butir 31)*
  Paragraf dikelompokkan jadi butir lebih dulu: sebuah butir dimulai di
  paragraf berangka dan berlanjut ke paragraf lanjutannya — tanpa itu, judul
  peraturan panjang yang memenuhi beberapa paragraf akan dituduh melanggar di
  tiap lanjutannya. Diblok kuning pada satu karakter terakhir butirnya.
- **Ejaan "Undang-Undang" — kedua huruf u kapital.** *(F1-005, butir 33)*
  `Undang-undang` → dicoret merah, usulan hijau `Undang-Undang`.
  Termasuk bentuk panjangnya, `Peraturan Pemerintah Pengganti Undang-Undang`.
- **Kata "tentang" di judul dasar hukum tetap huruf kecil.** *(F1-005, butir 32)*
  `Tentang` atau `TENTANG` → dicoret merah, usulan hijau `tentang`.

> **Kedua pemeriksaan ejaan itu berlaku HANYA di dalam rentang Mengingat.**
> Butir 32 dan 33 memang bicara tentang **dasar hukum**, bukan seluruh
> dokumen. Sebelum dipersempit, alat sempat menandai rujukan generik di dalam
> Lampiran — *"…atau undang-undang yang mengatur mengenai pencegahan…"* — yang
> sama sekali bukan dasar hukum.

### Yang TIDAK diperiksa

- **Penomoran angka Arab-nya sendiri.** Butir 31 mensyaratkan `1.`, `2.`,
  `3.`, tetapi dasar hukum yang bernomor huruf (`a.`, `b.`) **tidak ditandai**.
  Pada naskah bertabel nomornya sering ada di sel lain, sehingga ketiadaannya
  tidak bisa dibuktikan dari teks paragraf. **Periksa penomorannya sendiri.**
- **Urutan hierarkinya** (butir 30 — UU, lalu PP, lalu Perpres, lalu PMK, dan
  seterusnya, lalu kronologis). Belum dibangun.
- **Kelengkapan `(Lembaran Negara …, Tambahan Lembaran Negara …)`** pada
  UU/PP/Perpres (butir 34). Belum dibangun.
- **Kata penghubung dan konjungsi lain** yang menurut butir 32 tetap huruf
  kecil. Baru kata `tentang` yang diperiksa.
- Apakah peraturan yang dirujuk benar-benar ada, masih berlaku, atau nomornya
  benar. Itu ranah Fase 3.
- Typo umum bahasa Indonesia. Kamusnya sengaja belum dipasang.

### Kapan aturannya memilih diam

- Tidak ada paragraf yang diawali `Mengingat` → seluruh pemeriksaan bagian ini
  mati, termasuk ejaan.
- Tidak ada `MEMUTUSKAN` → F1-009 diam.
- Paragraf labelnya cuma berbunyi `Mengingat` → pemeriksaan titik dua diam
  (alasan bertabel yang sama dengan Menimbang).
- **Tidak ada satu pun paragraf yang diawali angka** → F1-010 diam seluruhnya.
  Dua kemungkinan yang tidak bisa dibedakan dari sini: dasar hukumnya memang
  tunggal tanpa nomor (sah menurut butir 31, yang hanya berlaku bila lebih
  dari satu), atau nomornya ada di sel tabel yang lain.

---

## 4. MEMUTUSKAN dan Menetapkan (diktum)

### Yang diperiksa

- **Kata "Menetapkan" ditulis huruf awal kapital, selebihnya huruf kecil.**
  *(F1-011, butir 38)*
- **Kata "Menetapkan" diakhiri titik dua (`:`).** *(F1-011, butir 38)*
- **Jenis peraturan ditulis tanpa frasa "Republik Indonesia".** *(F1-012,
  butir 39)* Yang ditandai `MENTERI KEUANGAN REPUBLIK INDONESIA`, dicoret
  merah, usulan hijau `MENTERI KEUANGAN`.
- **Judul pada Menetapkan diakhiri titik (`.`).** *(F1-012, butir 39)*
- **Judulnya sama persis dengan judul pembuka.** *(F1-002, butir 39)* — sama
  dengan yang disebut di bagian Judul.

### Yang TIDAK diperiksa

- **Penulisan kata `MEMUTUSKAN` itu sendiri.** Alat hanya memakainya sebagai
  penanda letak; benar-salahnya penulisannya tidak pernah diperiksa. Bentuk
  rapat `MEMUTUSKAN:` maupun berspasi `M E M U T U S K A N :` sama-sama
  diterima sebagai penanda.
- **Apakah judul pada Menetapkan ditulis kapital seluruhnya** (butir 39).
  Kendalanya sama dengan F1-001: gaya ALL CAPS.
- Ketentuan "disejajarkan ke bawah dengan Menimbang dan Mengingat" — itu tata
  letak, tidak terbaca dari daftar paragraf.

### Kapan aturannya memilih diam

- **Tidak ada `MEMUTUSKAN`** → F1-002, F1-011, dan F1-012 **mati semuanya.**
  Ini penting: tanpa penanda itu, letak klausul Menetapkan tidak bisa
  dipastikan, dan kata `menetapkan:` juga muncul di tengah kalimat batang
  tubuh.
- Hanya kemunculan **pertama** kata `Menetapkan` di antara `MEMUTUSKAN` dan
  batang tubuh yang diperiksa. Isi diktum yang kebetulan diawali kata
  "Menetapkan" bukan label bagian.
- Frasa "Republik Indonesia" hanya diperiksa **sebelum kata `TENTANG`
  pertama** — yaitu di posisi jenis peraturan. Sesudahnya yang ada judul, dan
  judul boleh mengutip nama resmi peraturan **lain** berikut frasa itu.
  Mencopotnya berarti mengubah nama resmi dokumen orang.
- Tidak ada kata `TENTANG` di klausulnya → pemeriksaan frasa itu diam.

---

## 5. Kelengkapan bagian wajib

- **Ada tidaknya bagian `Menimbang`, `Mengingat`, dan `Menetapkan`.**
  *(F1-003, butir 13/16/23/37/38)*

Temuan ini **tidak ditandai di naskah** dan tidak menghasilkan komentar —
ketiadaan sebuah bagian memang tidak punya teks untuk ditunjuk. Ditampilkan
sebagai **peringatan berlatar merah muda** di atas daftar temuan, tanpa tombol
Terima/Tolak.

**Yang tidak diperiksa:** isi maupun urutan ketiganya, dan bagian pembukaan
lain yang disebut butir 13 (frasa Dengan Rahmat, jabatan pembentuk, diktum).

---

## 6. Batang tubuh — BAB, Pasal, ayat

**Tidak ada satu pun aturan Fase 1 yang memeriksa bagian ini.**

Sudah dibuktikan: naskah yang pembukaannya sempurna tetapi batang tubuhnya
memuat `pasal 1` huruf kecil, `ketentuan umum` sebagai judul BAB huruf kecil,
ejaan `Undang-undang` yang salah, dan pasal tanpa titik penutup — menghasilkan
**nol temuan**.

Seluruhnya masih pekerjaan mata penelaah.

---

## 7. Lampiran

**Tidak ada satu pun aturan Fase 1 yang memeriksa Lampiran.**

Termasuk judul lampiran, penomorannya, kesesuaiannya dengan yang dirujuk
batang tubuh, maupun ejaan di dalamnya. Ini **disengaja**: butir 32 dan 33
yang mendasari pemeriksaan ejaan berbicara tentang dasar hukum, dan
memberlakukannya di Lampiran sudah pernah menghasilkan salah tandai.

---

## 8. Penutup — Ditetapkan, Diundangkan, tanda tangan

**Tidak diperiksa.** Termasuk urutan `Ditetapkan di` / `pada tanggal`,
nama pejabat, dan nomor Berita Negara.

---

# KMK

**Strukturnya sama persis dengan PMK di atas.** Kedua belas aturan berjalan
dengan cara yang sama, kecuali **tiga** hal berikut.

## Perbedaan 1 — batas akhir judul

| | Penanda akhir blok judul |
|---|---|
| PMK | `DENGAN RAHMAT TUHAN YANG MAHA ESA` |
| **KMK** | `MENTERI KEUANGAN REPUBLIK INDONESIA,` |

KMK tidak memakai frasa Dengan Rahmat. Kalau penanda yang benar tidak ketemu,
judulnya tidak terbaca dan seluruh pemeriksaan judul ikut mati — itu sebabnya
**salah memilih PMK/KMK di panel membuat hasilnya janggal beramai-ramai.**

## Perbedaan 2 — nama jenis pada butir Menimbang terakhir

Butir 22 menuntut bunyi yang berbeda menurut jenis dokumennya:

| | Yang wajib disebut butir terakhir |
|---|---|
| PMK | `perlu menetapkan` **`Peraturan Menteri Keuangan`** `tentang …` |
| **KMK** | `perlu menetapkan` **`Keputusan Menteri Keuangan`** `tentang …` |

**Inilah alasan jenis dokumen wajib dipilih dan tanpa nilai awal.** Sebuah KMK
yang butir terakhirnya menyebut "Peraturan Menteri Keuangan" akan ditandai
F1-004 — dan itu benar. Sebaliknya, kalau jenisnya salah pilih, alat menuntut
bunyi yang keliru dan menandai naskah yang sebenarnya sudah benar.

Jenis dokumen **tidak pernah ditebak alat.** Cara menebak yang lama —
"paragraf pertama yang memuat PERATURAN MENTERI KEUANGAN dianggap PMK" —
sudah dihapus, karena bagian Mengingat sebuah KMK lazim menyebut *"Peraturan
Menteri Keuangan Nomor 202/PMK.010/2017…"* sehingga KMK dikira PMK.

## Perbedaan 3 — penanda awal batang tubuh

| | Yang menandai batang tubuh sudah dimulai |
|---|---|
| PMK | `BAB`, `Pasal` |
| **KMK** | diktum `KESATU`, `KEDUA`, `KETIGA`, … sampai `KEDUAPULUHLIMA` dan seterusnya |

Penanda ini menentukan di mana klausul Menetapkan berakhir. Daftar penanda
yang dulu hanya memuat penomoran PMK membuat pengambilan judul Menetapkan
menelan seluruh isi diktum KESATU, lalu melaporkan judul sepanjang belasan
paragraf sebagai "berbeda dari judul pembuka".

**Diktum KMK sendiri tidak diperiksa isinya** — sama seperti batang tubuh PMK.

---

# Yang tidak disentuh sama sekali

Ringkasnya, Fase 1 bekerja **hanya di pembukaan dan diktum**. Ini yang tetap
menjadi tugas penelaah sepenuhnya:

- Seluruh batang tubuh: BAB, Pasal, ayat, huruf, angka
- Seluruh Lampiran
- Bagian penutup dan tanda tangan
- Kapital pada judul *(F1-001 dimatikan — lihat bagian Judul)*
- Urutan hierarki dasar hukum *(butir 30)*
- Kelengkapan Lembaran Negara pada dasar hukum *(butir 34)*
- Penomoran angka Arab pada dasar hukum *(butir 31, sebagian)*
- Konjungsi selain kata "tentang" *(butir 32, sebagian)*
- Validasi logo Garuda, kelaziman bahasa → **di luar lingkup seluruhnya**

Dua hal yang dulu tertulis di sini sudah pindah ke Fase 2 dan 3 — lihat
bagian berikutnya.

---

# Fase 2 dan 3 — batang tubuh, dengan tombol terpisah

Dijalankan tombol sendiri, bukan lanjutan otomatis dari Fase 1. Fase 2
berjalan beberapa menit dan sebagian besarnya berbayar, jadi memulainya
keputusan sadar penelaah. Seluruhnya bisa dimatikan satu per satu di panel
Pengaturan.

**HANYA PMK.** Naskah KMK memakai diktum (KESATU, KEDUA), bukan Pasal —
parsernya belum mendukung itu dan memilih diam dengan menyebut alasannya.
Fase 1 pada KMK tetap berjalan seperti biasa.

**BUKAN NASKAH PERUBAHAN.** Kalau judulnya memuat "PERUBAHAN ATAS", atau
batang tubuhnya memakai "Pasal I" berangka Romawi, Fase 2 **tidak dijalankan**
dan panel menyebutkan alasannya. Sebabnya: pasal yang dikutip di dalam naskah
perubahan milik peraturan **induk**, bukan draf ini — memeriksanya seolah
milik draf ini menghasilkan salah tandai. Fase 1 tetap berjalan penuh.

**Naskah berpenomoran otomatis sudah didukung** sejak 23 Sep 2026. Kalau
"BAB I", "Pasal 1", atau nomor ayat dibuat dengan penomoran otomatis Word,
nomornya kini ikut terbaca add-in. Sebelum itu Fase 2 tidak menemukan satu pun
Pasal, dan pada naskah yang ayatnya bernomor otomatis F2-001 **salah tandai**.

Satu hal yang tersisa: temuan yang letaknya persis di nomor itu sendiri — mis.
F2-004 yang menandai nomor pasal yang melompat — tidak bisa disorot di Word,
jadi aturannya memilih diam.

## Kalau tidak ada yang dicentang

Sejak 23 Sep 2026 tombolnya **satu**: "Jalankan Analisis". Apa yang dijalankan
ditentukan panel Pengaturan. Kalau tidak ada satu pun pemeriksaan dicentang,
tombolnya mati dan panel menyebutkan alasannya.

Fase 1 dan Fase 2 bisa menemukan hal yang sama. Penanganannya: temuan Fase 1
dikirim ke AI supaya tidak diulang, tumpang tindih yang tersisa dibuang kode,
dan kalau AI menilai sebuah temuan keliru ia menempelkan baris `Catatan AI:`
di komentarnya. **Temuannya tidak pernah dihapus AI** — penelaah yang
memutuskan.

## Warna tandanya, dan apa artinya

| Warna | Artinya | Di naskah |
|---|---|---|
| **Hijau** | kesalahannya **terbukti** dan penggantinya punya sumber yang bisa ditunjuk | teks lama dicoret merah, usulannya hijau di sebelahnya, sumbernya disebut di komentar |
| **Merah saja** | kesalahannya terbukti dan perbaikannya **membuang** | teks lama dicoret merah, tidak ada usulan hijau |
| **Kuning** | kemungkinan, atau penggantinya tidak diketahui | blok kuning saja, tidak ada yang dicoret |

**Tidak ada yang menghapus tulisan Anda.** Merah dan coretan cuma warna;
yang menghapus tetap Anda.

Temuan Fase 2 yang **hasil penalaran** (F2-101 sampai F2-105) berwarna hijau
hanya kalau rumusan penggantinya dicontoh dari peraturan yang masih berlaku
lewat F3-003 — dan peraturannya disebut di komentar supaya bisa Anda periksa.
Tanpa itu tetap kuning: penilaian AI atas dirinya sendiri bukan bukti. F2-003
satu-satunya yang merah saja, karena definisi yang tidak terpakai memang
dibuang, bukan diganti. F3-001 selalu kuning — "berpotensi bertentangan" itu
kemungkinan, bukan kesimpulan.

Komentarnya bisa sampai empat bagian:

```
Temuan:
<apa yang ditemukan>

Perbaiki di: <di mana perbaikannya dikerjakan>

Saran:
<apa yang sebaiknya dilakukan, kadang berikut contoh rumusan>

<rujukan> — <tautan> (T2)
```

**Perbaiki di** muncul kalau perbaikannya ada di tempat lain — komentar di
Pasal 5 yang perlu ditindaklanjuti dengan menambah definisi di Pasal 1,
misalnya. Ia tidak ditulis kalau perbaikannya memang persis di tempat
komentarnya, dan tidak ditulis kalau alat tidak bisa memastikan tempatnya.

**Saran** dikosongkan kalau penggantinya memang tidak diketahui. Anjuran yang
cuma mengulang masalahnya tidak menolong siapa pun.

Baris rujukan paling bawah supaya bisa **ditimbang sendiri**, bukan dipercaya
begitu saja.

## Tanpa AI — gratis, hasilnya pasti

| Kode | Yang diperiksa | Yang TIDAK diperiksa | Kapan diam | Dasar KMK 527 |
|---|---|---|---|---|
| F2-001 | Rujukan bentuk baku "sebagaimana dimaksud dalam/pada Pasal N ayat (n)" menunjuk satuan yang ada | Rujukan ke peraturan lain ("Pasal 12 Undang-Undang Nomor 1 Tahun 2004"); kata "Pasal" tanpa frasa baku | Pohon satuan tidak sehat | butir 54d, 54h — **turunan** |
| F2-003 | Tiap istilah berdefinisi Pasal 1 dipakai di batang tubuh, **termasuk Pasal 10–19** | Lampiran — belum dibaca parser sama sekali, padahal butir 67 menghitungnya | Pasal 1 tidak ada, atau tidak memuat satu pun definisi | butir 61, pengecualian butir 64 |
| F2-004 | Deret nomor Pasal, ayat, huruf, angka tidak melompat atau berulang | Pasal sisipan berhuruf (Pasal 5A) dianggap sah; penomoran di lampiran | Rentang paragrafnya tidak ketemu | butir 54c, 54f, 54k-7 |
| F2-007 | Bilangan "30 (tiga puluh)" — angka dan hurufnya cocok | Kurung yang isinya bukan bilangan ("Pengguna Barang (PB)"); bilangan di atas ribuan | Hurufnya tidak bisa dibaca jadi angka yang pasti | butir 54j |

**F2-003 mencoret merah, bukan memblok kuning** — perbaikannya membuang
definisinya, bukan menggantinya. Teksnya tetap tidak dihapus alat.

**Butir 64 adalah pengecualian yang tidak bisa dinilai alat.** Istilah yang
dipakai sekali tetapi pengertiannya diperlukan untuk suatu bab tetap boleh
didefinisikan. Karena itu F2-003 baru berbunyi kalau istilahnya **tidak muncul
sama sekali** di luar Pasal 1 — lebih longgar daripada butir 61, dan itu
disengaja.

## Dengan AI — berjalan menit, berbiaya

Semua temuan di bawah **hasil penalaran**, bukan kesalahan yang bisa
ditunjukkan barisnya. Semuanya sudah dibaca ulang pada teks utuh pasalnya dan
kutipannya sudah dibuktikan kode ada di naskah — tetapi penilaiannya tetap
penilaian. Periksa sendiri sebelum menerima.

| Kode | Yang diperiksa | Kapan gugur |
|---|---|---|
| F2-101 | Rumusan yang bisa dibaca dua arah | Kutipannya tidak ketemu persis; menyebut Pasal yang tidak ada; skor di bawah ambang |
| F2-102 | Kewajiban tanpa pemikul yang tegas | sda |
| F2-103 | wajib / harus / dapat / dilarang bertabrakan dalam satu ketentuan | sda |
| F2-104 | Dua ketentuan yang tidak bisa berlaku bersamaan | sda, ditambah: pengecualian yang sah bukan tabrakan |
| F2-105 | Tujuan di Menimbang yang tidak ada ketentuannya di batang tubuh | sda |
| F3-001 | Berpotensi bertentangan dengan peraturan lain — **KMK 527 Lampiran III huruf C angka 3–4 dan huruf E Syarat Substantif 2b** | Tidak ada pembanding yang status berlakunya terbaca; peraturan yang disebut tidak ada di hasil pencarian; kalimatnya tidak memakai "berpotensi bertentangan" |
| F3-003 | **Bukan mencari temuan** — melengkapi temuan F2-1xx dengan usulan rumusan yang dicontoh dari peraturan yang masih berlaku, lalu menyebut peraturannya di komentar. Satu-satunya jalan temuan penalaran bisa jadi hijau | Temuan sudah punya usulan; kutipannya lebih dari 200 huruf; sudah 15 temuan dicarikan di dokumen ini; peraturan yang disebut tidak ada di hasil pencarian |

## Fase 3 tanpa AI — gratis

| Kode | Yang diperiksa | Kapan diam |
|---|---|---|
| F3-002 | Tiap dasar hukum di Mengingat dicari di korpus JDIH, status berlakunya dibaca. **Tidak memanggil AI sama sekali** | Bentuk di luar UU/Perppu/PP/Perpres/Keppres/PMK/KMK; tidak ketemu di korpus; dua dokumen bernomor sama berstatus beda; status di luar Berlaku/Tidak Berlaku |

F3-002 tetap berjalan **walau Fase 2 menolak** — pada KMK, naskah perubahan,
dan naskah berpenomoran otomatis. Yang dibutuhkannya cuma bagian Mengingat,
dan itu terbaca di ketiganya.

Yang dilaporkannya **fakta dari korpus**, bukan penilaian. Tetapi status di
korpus bisa tertinggal dari keadaan sebenarnya — pastikan sendiri sebelum
mengganti dasar hukum.

**Yang belum dibangun di Fase 2:** F2-002 (istilah berkapital yang tidak
berdefinisi — menunggu daftar pengecualian dari naskah nyata), F2-005
(lampiran), F2-006 (urutan hierarki Mengingat).

**Yang tetap tidak disentuh siapa pun:** seluruh Lampiran, bagian penutup dan
tanda tangan, kelengkapan Lembaran Negara.

---

# Cara membuktikan berkas ini masih benar

Berkas ini bisa usang tanpa ada yang sadar. Dua cara memeriksanya, keduanya
bisa dijalankan sendiri:

**1. Lewat naskah uji yang kesalahannya sudah diketahui.**

```bash
cd backend && python tools/cek_docx.py tools/contoh/uji-pmk-lengkap.docx --jenis PMK
cd backend && python tools/cek_docx.py tools/contoh/uji-kmk-lengkap.docx --jenis KMK
```

Cocokkan dengan `backend/tools/contoh/KUNCI-UJI.md`. Hasil yang benar saat
ini: **PMK 13 temuan, KMK 1 temuan.** Angka yang berbeda berarti ada yang
berubah dan berkas ini perlu ditinjau.

Untuk Fase 2 tanpa AI, naskah ujinya berbeda dan jawabannya juga sudah
diketahui:

```bash
cd backend && python tools/cek_docx.py tools/contoh/uji-fase2-batangtubuh.docx --fase2
```

Hasil yang benar saat ini: **4 temuan** — F2-003 pada "Sistem Informasi",
F2-007 pada "30 (tiga belas)", F2-001 pada "Pasal 25", dan F2-004 pada
lompatan Pasal 3 ke 5.

Jalur AI-nya diperiksa dengan `--lanjut`, dan itu **memanggil model sungguhan
serta berbiaya**. Yang dicetaknya bukan cuma temuan melainkan juga daftar yang
GUGUR di Langkah 5 berikut alasannya — daftar itu yang membuktikan gerbangnya
benar-benar bekerja.

**2. Lewat panel Pengaturan di add-in.** Tombol gerigi di header membuka
daftar seluruh aturan Fase 1 dan Fase 2/3 berikut rincian "yang diperiksa" dan
"yang TIDAK diperiksa" — isinya harus sejalan dengan berkas ini.

Kalau ketiga sumber bertentangan, yang berlaku kodenya:
`backend/app/rules/format_baku.py` untuk Fase 1,
`backend/app/fase2/mekanis_konsistensi.py` dan
`backend/app/fase2/tahap4_memastikan.py` untuk Fase 2/3. Riwayat lengkap tiap salah tandai yang
pernah terjadi ada di `fase1 drafter.md` bagian 6.10.
