# Rancangan Teknis — Drafter Analiser (Build Pertama: Fase 1)

> **Untuk agen coding:** ikuti tiap bagian di bawah sebagai keputusan yang sudah
> final, bukan draf. Kalau ada bagian yang terbaca seperti pertanyaan terbuka,
> itu kekeliruan — laporkan ke pengguna, jangan menebak sendiri.
>
> **Untuk Alfa:** dokumen ini ditulis supaya bisa kamu pahami juga, bukan cuma
> dibaca mesin. Kalau ada istilah yang tidak jelas, tanya langsung ke Claude —
> jangan diteruskan mentah ke agen coding.
>
> Disusun dari `project-brief.md`, `pemahaman-jdih-law-analyzer.md`, berkas env
> Law Analyzer/JDIH, dan kerangka repo `drafter-analiser` yang sudah ada.
>
> **Revisi 17 Sep 2026 (kedua):** bagian 6 ditulis ulang total. **Track Changes
> ditinggalkan** — alat menggambar tandanya sendiri: merah-dicoret untuk yang
> salah, hijau untuk usulannya, blok kuning untuk yang perlu ditinjau tanpa
> jawaban pasti. Alasannya di bagian 6.1. Penandaan turun ke tingkat kata
> (6.5), aturan judul kapital F1-001 dimatikan dan bug klausul Menetapkan
> diperbaiki (6.10), dan jenis dokumen wajib dipilih tanpa nilai awal (6.12).
>
> **Dokumen ini memuat Fase 1 saja**, dari awal sampai pondasinya tuntas. Hal
> yang baru relevan di Fase 2/3 disebut seperlunya sebagai penanda batas, tidak
> dirancang di sini.

---

## 1. Judul

**Drafter Analiser — Fase 1: Pemeriksaan Format Baku**

Add-in Word (task pane) + backend FastAPI untuk memeriksa rancangan PMK/KMK
terhadap kaidah penyusunan peraturan.

---

## 2. Apa yang dibangun & tujuan

Penelaah membuka rancangan PMK/KMK di Word, menekan satu tombol, dan bagian yang
perlu ditinjau langsung tertandai di dokumen itu juga — lengkap dengan catatan,
rujukan butir KMK 527 yang mengaturnya, dan usulan rumusan. Tidak ada perubahan
yang jadi permanen sebelum penelaah menyetujuinya satu per satu.

Fase 1 menangani kesalahan format baku: hal-hal yang jawabannya pasti (kapital
atau tidak, ada atau tidak ada, sama atau berbeda). Justru jenis kesalahan
inilah yang paling sering jadi bahan koreksi harian dan paling sering lolos dari
mata manusia.

**Ukuran keberhasilan bukan "selesai dibangun", melainkan dipakai penelaah dalam
pekerjaan sehari-hari.**

Pengguna: perancang dan penelaah di **Biro Hukum Kementerian Keuangan** —
seluruh bagian, masing-masing menelaah rancangan dari unit pemrakarsa mitranya.
Bukan masyarakat umum.

---

## 3. Fitur Fase 1 & masalah yang diselesaikan

| Fitur | Masalah yang diselesaikan | Cara kerja |
|---|---|---|
| Baca paragraf dokumen yang sedang terbuka di Word | Telaah dikerjakan satu per satu mengandalkan ketelitian; di dokumen panjang pasti ada yang lolos (PMK 124/2024 = 175 satuan pasal/ayat) | Office.js membaca paragraf dari dokumen aktif, tanpa unggah berkas |
| Cek judul pembuka = judul pada "Menetapkan" | Kesalahan paling sering (brief bagian 8.6) — beda satu kata pun lolos | Bandingkan teks judul di dua lokasi |
| ~~Cek judul ditulis kapital seluruhnya~~ | — | **Dimatikan.** Tidak bisa membedakan judul yang hurufnya campur dari judul yang tampil kapital lewat gaya ALL CAPS — bagian 6.10 |
| Cek kelengkapan Menimbang / Mengingat / Menetapkan | Struktur wajib yang kadang terlewat | Cari pola baku tiap bagian |
| Cek frasa baku butir Menimbang terakhir ("perlu menetapkan … tentang …") | Sering hilang atau salah bentuk (brief bagian 8.6) | Pencocokan pola pada butir terakhir |
| Cek ejaan | Salah tulis lolos saat buru-buru | Kamus/regex bahasa Indonesia, bukan AI — cakupannya lihat bagian 13 langkah 4 |
| **Teks salah ditandai merah + dicoret, usulannya hijau di sebelahnya** | Penelaah tidak perlu mengetik ulang, tapi tetap memutuskan | Alat menggambar sendiri dengan pelacakan mati — bagian 6.3 |
| **Temuan tanpa pengganti diberi blok kuning + komentar** | Sebagian kesalahan tidak punya "jawaban benar" tunggal | `font.highlightColor` + `insertComment` — bagian 6.3 |
| **Yang ditandai hanya rentang kata yang salah, bukan paragraf penuh** | Penelaah tidak perlu mencari sendiri huruf mana yang dipersoalkan | Offset presisi dari backend + `Word.search()` — bagian 6.5 |
| Tiap temuan menyertakan rujukan butir KMK 527 + kutipannya | Penelaah perlu tahu dasar hukumnya, bukan cuma "ini salah" | Tabel rujukan tetap di kode — bagian 10 |
| Setujui / tolak tiap usulan | Prinsip: alat memberi rekomendasi, tidak pernah memutuskan | Tombol Terima/Tolak di task pane — bagian 6.7 |
| Versi bersih tanpa coretan | Penelaah sekarang memelihara dua berkas manual | **Belum dibangun** — jalurnya belum ditetapkan, bagian 6.7 |
| Pilih cakupan: seluruh dokumen atau bagian terpilih | Fleksibilitas penelaah | `document.getSelection()` vs seluruh body |

---

## 4. Di luar cakupan build ini

Jangan dikerjakan agen coding. Diambil dari brief bagian "Di Luar Lingkup" dan
pembagian fase:

- **Menerapkan usulan tanpa persetujuan penelaah.** Usulan boleh *ditampilkan*
  di sebelah teks aslinya sebagai teks hijau yang bisa dicabut satu klik — tapi
  teks lama tidak boleh dihapus, tidak boleh ada tombol "terapkan semua", dan
  tidak boleh ada rentang di luar `lokasi` temuan yang disentuh. Lihat bagian 6
  dan bagian 14 butir 5.
- Validasi gambar logo Garuda
- Deteksi "kelaziman" bahasa
- Versi untuk masyarakat umum
- Menulis apa pun ke basis data produksi JDIH/Law Analyzer
- Pencarian pembanding ke OpenSearch — itu Fase 3
- Pemeriksaan yang butuh penalaran AI (definisi konsisten, potensi multitafsir)
  — itu Fase 2
- **Usulan penggantian untuk temuan Fase 2/3.** Fase 1 dulu yang membuktikan
  skema penandaan ini enak dibaca penelaah. Usulan hasil penalaran jauh lebih
  berisiko disisipkan otomatis ke naskah, dan keputusannya ditunda sampai Fase 1
  terbukti.
- Urutan "Mengingat" sesuai hierarki, dan istilah Pasal 1 dipakai konsisten —
  dua item lain di brief bagian 8.6, tapi keduanya juga masuk daftar
  "kemungkinan pemeriksaan" di brief bagian 8.11 yang eksplisit ditandai belum
  dikonfirmasi penelaah. Ditunda, bukan terlewat.

Kalau agen coding mengusulkan salah satunya, tolak.

---

## 5. Arsitektur & environment

```
Word (dokumen terbuka)
  └── Task pane (Next.js)  ──baca/tulis paragraf via Office.js──┐
                                                                 ▼
                                                         Backend (FastAPI)
                                                         aturan deterministik
                                                         (regex / logika Python murni)
                                                                 ▼
                                                         daftar Temuan (JSON)
                                                                 ▼
                    Task pane menggambar tanda merah/hijau/kuning + komentar
                    (pelacakan perubahan Word DIMATIKAN selama penandaan)
```

| Lapisan | Teknologi | Catatan |
|---|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind v4 | Sudah terpasang di kerangka — jangan diganti, jangan tambah Bootstrap |
| Integrasi Word | Office.js | Lihat `docs/panduan-officejs.md` — API yang sudah diverifikasi ke `index.d.ts` |
| Backend | FastAPI (Python) | Aturan ditulis sebagai fungsi murni bebas framework |
| Model AI | **Tidak dipakai sama sekali di Fase 1** | Semua pemeriksaan di bagian 3 berjawaban pasti. Fase 2 nanti memakai **Azure OpenAI** (deployment `gpt-4.1`, sesuai env Law Analyzer), bukan ChatGPT konsumen |
| Pencarian peraturan | OpenSearch | **Tidak dipakai di Fase 1.** Baru relevan di Fase 3 |
| Database | **Tidak dipakai di Fase 1** | Lihat bagian 9 |
| ORM (untuk Fase 2) | **SQLModel** | Bukan Prisma — lihat alasannya di bagian 9 |

### Syarat teknis add-in Word

Dua hal yang harus dibangun, tidak ada hubungannya dengan env:

1. **Manifest XML** — mendeklarasikan ID add-in, nama, URL task pane, izin, dan
   tombol ribbon.
2. **Hosting HTTPS** — task pane adalah halaman web biasa yang dimuat Word lewat
   URL di manifest. Wajib HTTPS (saat pengembangan boleh sertifikat self-signed
   yang dipercaya lokal).

Untuk pengembangan, sideload dari folder lokal sudah cukup. Di Word 2024 LTSC
tombol "Upload My Add-in" tidak selalu ada; jalur yang terbukti jalan adalah
mendaftarkan manifest lewat registry
`HKEY_CURRENT_USER\Software\Microsoft\Office\16.0\WEF\Developer` — nama value =
`<Id>` add-in, isinya path lengkap ke `manifest.xml`. Jalur pemasangan untuk
banyak penelaah sekaligus adalah keputusan organisasi di luar cakupan agen
coding.

### Agar tidak tersandera urusan manifest

Tulis aturan Fase 1 sebagai fungsi yang menerima **daftar paragraf**, bukan
menerima berkas Word. Dengan begitu sumber paragrafnya bisa dari Office.js
**atau** dari `python-docx` (jalur unggah sementara) — bagi backend sama saja.
Semua aturan bisa diuji lewat jalur unggah sambil izin manifest diurus, tanpa
satu baris pun terbuang.

Catatan: jalur unggah hanya jembatan pengujian. Kalau dijadikan bentuk akhir,
proyek ini kehilangan pembedanya — brief bagian 3 menegaskan "hasil masuk ke
dokumen, bukan panel terpisah".

---

## 6. Cara temuan ditampilkan di dokumen

> Bagian ini ditulis ulang total 17 Sep 2026. Dua rancangan sebelumnya gugur di
> Word penelaah, dan keduanya gugur karena alasan yang baru kelihatan setelah
> dicoba pada naskah sungguhan. Riwayatnya disimpan di 6.1 supaya tidak ada yang
> mencoba jalan itu lagi.

### 6.1 Dua rancangan yang gugur

**Rancangan A — Critique + popup. Gugur 16 Sep 2026.**
Diuji di Word 2024 LTSC: `isSetSupported("WordApi", "1.7")` melaporkan `true`,
tapi `insertAnnotations` melempar `RichApi.Error: NotImplemented`. Annotation
mensyaratkan langganan Microsoft 365 aktif; lisensi beli-putus tidak punya itu.
Ikut mati bersamanya: popup berisi tombol terima/tolak, dan pewarnaan lewat
`Critique.colorScheme`.

Pelajaran yang berlaku seterusnya: **requirement set didukung ≠ fitur
diizinkan.**

**Rancangan B — Track Changes bawaan Word. Gugur 17 Sep 2026.**
Track Changes sendiri terbukti jalan — hasil pengujiannya tetap dicatat di 6.2
karena isinya masih benar dan berguna. Yang membatalkannya dua hal lain:

1. **Warna revisi tidak bisa diatur add-in.** Sudah dicari ke seluruh
   `index.d.ts`: tidak ada `insertedTextColor`, `deletedTextColor`,
   `revisionColor`, maupun `authorColor`. `RevisionsFilter` hanya punya `markup`
   dan `view`. Word mewarnai revisi menurut penulisnya. Satu-satunya cara
   mengubahnya adalah Options Word pada tiap komputer penelaah — dan syarat yang
   ditetapkan penelaah adalah **tidak menyetel apa pun di Word**.
2. **Memberi blok warna selagi pelacakan menyala tercatat sebagai revisi.** Pada
   RKMK 527 sungguhan, dua temuan menghasilkan tiga baris
   `ajat — Formatted: Highlight` di margin, mengubur komentar yang justru perlu
   dibaca.

### 6.2 Hasil pengujian Track Changes — tetap berlaku sebagai catatan

Diuji langsung di Word 2024 LTSC penelaah, 17 Sep 2026, lewat perancah sementara
yang sesudahnya dicopot. Meski jalur ini tidak jadi dipakai, temuannya masih
mengikat kalau suatu saat ada yang mempertimbangkannya lagi:

| Yang diuji | Hasil |
|---|---|
| `isSetSupported("WordApi", "1.4")` dan `"1.6"` | keduanya `true` |
| Membaca `document.changeTrackingMode` | terbaca `"Off"` |
| Menyetel ke `"TrackAll"` lalu membaca ulang | diterima, terbaca `"TrackAll"` |
| `insertText(..., "Replace")` selagi pelacakan menyala | teks terganti |
| Penggantian tercatat sebagai revisi | ya |
| Mengembalikan mode ke semula | berhasil, kembali `"Off"` |

**Penghapusannya ikut terlacak.** Sempat terlihat seolah tidak — teks lama
langsung lenyap. Penyebabnya Word sedang di mode **Simple Markup**, yang memang
menyembunyikan penghapusan. Di **All Markup** teks lama muncul tercoret.

**`getTrackedChanges()` melaporkan kurang dari yang sebenarnya.** Satu
penggantian menghasilkan satu item bertipe `Added` saja, padahal di dokumen ada
sisipan *dan* penghapusan. Jumlah dan tipe dari API ini **tidak boleh dipakai
sebagai bukti** bahwa penandaan berhasil. Inilah salah satu alasan tambahan
kenapa meninggalkan Track Changes justru melegakan: Terima/Tolak tidak lagi
berdiri di atas API yang sudah terbukti tidak jujur.

### 6.3 Keputusan: alat menggambar tandanya sendiri

Penandaan berjalan dengan **pelacakan perubahan dimatikan**, lalu mode semula
dikembalikan supaya setelan Word penelaah tidak diam-diam berubah. Tiga tanda,
tiga arti yang berbeda:

| Tanda | Artinya | Dipakai bila |
|---|---|---|
| **Merah `#C00000` + dicoret** | salah, dan ini penggantinya | ada `usulan_rumusan` |
| **Hijau `#00802B`** | rumusan usulannya, disisipkan di sebelahnya | menyertai yang merah |
| **Blok kuning** (`highlightColor = "Yellow"`) | perlu ditinjau, alat tidak tahu jawabannya | tidak ada pengganti tunggal |

Pembedaan kuning itu diminta penelaah dan alasannya benar: memberi warna merah
pada temuan yang tidak punya pengganti membuat alat seolah mengusulkan teks itu
dibuang, padahal yang dimaksud cuma "periksa bagian ini". **Merah dipakai hanya
bila alat punya jawaban.** Pada temuan kuning, warna huruf tidak disentuh sama
sekali — hanya latarnya.

Seluruh API yang dipakai ada di **WordApi 1.1**, himpunan paling dasar:
`Font.color`, `Font.strikeThrough`, `Font.highlightColor`, `Range.insertText`,
`Range.insertContentControl`, `ContentControl.font`, `ContentControl.delete`,
`ContentControlCollection.getByTag`. Hanya komentar dan `changeTrackingMode`
yang butuh 1.4. Tidak ada lagi ketergantungan pada `WordApiDesktop`.

**Yang harus disadari, dan sudah disetujui penelaah:** Word tidak tahu tanda ini
usulan mesin. Tab Review menunjukkan 0 revisions, Accept All/Reject All bawaan
Word tidak melakukan apa-apa, tidak ada nama pengusul maupun waktunya, dan kalau
berkas dibuka orang lain tanpa add-in tidak ada yang memberi tahu bahwa merah-
hijau itu usulan alat. Yang mengenali tandanya hanya add-in ini, lewat content
control bertag yang dipasangnya sendiri.

Itu diterima karena sejalan dengan cara kerja yang sebenarnya: penelaah
menghasilkan **dua dokumen** — versi bercoretan dan versi bersih
(`project-brief.md` bagian 8.13). Naskah kerja merah-hijau inilah dokumen
coretannya; versi bersihnya dibuat terpisah lewat ekspor. Alat ini membantu
menelaah, bukan menggantikan telaah — penelaah tetap wajib memeriksa ulang.

### 6.4 Content control sebagai jangkar

Tiap tanda dibungkus content control bertag, penampilannya `Hidden` supaya tidak
ada kotak yang terlihat:

| Tag | Isinya |
|---|---|
| `DA-ASLI-{nomor}` | teks bermasalah — yang merah dicoret atau yang berblok kuning |
| `DA-USUL-{nomor}` | teks usulan hijau yang disisipkan alat |

Tanpa jangkar ini add-in tidak punya cara mengenali kembali tandanya sendiri,
karena Word tidak menyimpan apa pun tentang "usulan mesin". Dengan jangkar ini
Tolak bisa mencabut tepat yang perlu dicabut, dan Lompat ke Teks tetap tepat
sasaran meski naskah sudah bergeser oleh penyisipan usulan.

Kegagalan memasang content control **tidak** menggagalkan penandaan — tandanya
tetap terpasang, hanya lebih sulit dicabut otomatis nanti.

### 6.5 Penandaan setingkat kata

Sampai 17 Sep 2026, F1-001, F1-002, dan F1-004 selalu mengirim `offset_mulai=0`
dan `panjang=len(paragraf)`, dan `office.ts` mewarnai `p.getRange()` penuh —
mengabaikan offset dari backend sama sekali. Akibatnya blok judul tiga baris
tersorot seluruhnya untuk persoalan yang mungkin cuma satu kata, dan penelaah
harus mencari sendiri huruf mana yang dipersoalkan.

Sekarang yang ditandai rentang kata yang benar-benar bermasalah:

- **F1-001** — tiap **deret kata beruntun** yang memuat huruf kecil. Deret, bukan
  kata satuan: kalau judul diketik Dengan Huruf Awal Kapital tiap katanya salah,
  dan satu temuan per kata berarti belasan komentar untuk satu persoalan yang
  sama. Dengan deret, judul yang seluruhnya salah jadi satu temuan sepanjang
  judul — memang itu kenyataannya — sedangkan satu kata nyasar jadi satu temuan
  sepanjang satu kata.
- **F1-002** — diff kata (`difflib.SequenceMatcher`) antara judul pembuka dan
  judul Menetapkan; yang ditandai hanya kata yang berbeda. Pada dokumen contoh,
  sorotan menyusut dari satu paragraf Menetapkan penuh jadi `PERUNDANG-UNDANGAN`
  saja.
- **F1-004** — butir terakhir di dalam paragrafnya, bukan paragraf penuh. Kalau
  yang kurang cuma titik komanya, yang ditandai satu karakter terakhir.
- **F1-005** — sudah setingkat kata sejak semula.

Sisi Word menerjemahkan offset itu lewat `Word.search()` pada teks temuan,
ditambah perhitungan **kemunculan keberapa** kata itu di dalam paragraf.
Perhitungan itu wajib: tanpa dia, temuan pada kata yang berulang — "PERATURAN"
di judul pencabutan, misalnya — selalu mendarat di kemunculan pertama, bukan di
kata yang sebenarnya dipersoalkan.

**Temuan yang rentang presisinya tidak ketemu TIDAK ditandai sama sekali**, dan
jumlahnya dilaporkan di panel. Menandai satu paragraf penuh karena pencarian
meleset pernah terjadi di proyek ini dan berakhir menutupi naskah yang tidak
bersalah.

### 6.6 Dua kelas temuan

| Kelas (`jenis_tanda`) | Dipakai bila | Cara ditandai |
|---|---|---|
| `penggantian` | Ada satu rumusan pengganti yang deterministik untuk rentang yang ditandai | Merah + dicoret, usulan hijau di sebelahnya |
| `catatan` | Tidak ada pengganti tunggal — yang salah adalah ketiadaan sesuatu, atau alat tidak tahu mana dari dua kemungkinan yang benar | Blok kuning, warna huruf tidak disentuh |

Pemetaan aturan Fase 1 — diverifikasi terhadap `rules/format_baku.py`:

| Aturan | Kelas | Aktif | Alasan |
|---|---|---|---|
| F1-001 judul kapital | `catatan` | **tidak** | Dimatikan — lihat 6.10 |
| F1-002 judul pembuka ≠ judul Menetapkan | `catatan` | ya | Alat tidak tahu mana dari dua judul itu yang benar |
| F1-003 kelengkapan struktur | `catatan` | ya | Yang salah adalah ketiadaan bagian; tidak ada teks untuk diganti |
| F1-004 frasa baku butir Menimbang terakhir | `catatan` | ya | Bunyi bakunya perlu menyebut huruf mana saja yang dirujuk |
| F1-005 ejaan | `penggantian` | ya | Substitusi kata, mis. `Undang-undang` → `Undang-Undang` |
| F1-006 judul diakhiri tanda baca | `penggantian` | ya | butir 8 — imperatif |
| F1-007 penulisan "Menimbang" | `penggantian` / `catatan` | ya | butir 16 — imperatif |
| F1-008 bentuk tiap butir Menimbang | `catatan` | ya | butir 21 — imperatif |
| F1-009 penulisan "Mengingat" | `penggantian` / `catatan` | ya | butir 23 — imperatif |
| F1-010 tanda baca dasar hukum | `catatan` | ya | butir 31 — imperatif. Penomoran angka Arab-nya sendiri BELUM diperiksa |
| F1-011 penulisan "Menetapkan" | `penggantian` / `catatan` | ya | butir 38 — imperatif |
| F1-012 bentuk judul pada Menetapkan | `penggantian` | ya | butir 39 — imperatif |

Pada `backend/tools/contoh/contoh-rancangan-uji.docx` dengan F1-001 mati:
2 temuan `penggantian`, 3 temuan `catatan`. (Angka ini sempat tertulis 2 dan 2
sampai 18 Sep 2026 — ketinggalan sesudah F1-008 ditambahkan. Cara memeriksanya
sendiri ada di bagian 16.)

**Tingkat keparahan (tinggi/sedang/rendah) dihapus dari rancangan ini.** Dulu
dipakai memilih warna sorotan dan menyaring daftar panel; sesudah warnanya
ditentukan ada-tidaknya usulan, tingkat itu tidak dibaca siapa pun.

### 6.7 Terima, Tolak, dan ekspor versi bersih

**Terima — naskah kerja sengaja TIDAK disentuh.** Yang berubah hanya status
kartu di panel. Coretan merah dan usulan hijaunya tetap terbaca, karena naskah
kerja inilah dokumen coretan yang dibawa ke rapat pembahasan bersama unit
pemrakarsa. Usulan baru benar-benar diterapkan saat ekspor versi bersih.

**Tolak — tidak boleh ada bekas.** Content control `DA-USUL-{n}` dihapus berikut
isinya (`delete(false)`); `DA-ASLI-{n}` dikembalikan warna, coretan, dan
sorotannya seperti sebelum ditandai, lalu bungkusnya saja yang dilepas
(`delete(true)`); komentarnya dihapus.

**Yang membedakan sudah-diputuskan dari belum cukup dari kartu di panel.**
Keputusan penelaah, 17 Sep 2026 — naskah tidak perlu ikut menandainya.

**Ekspor versi bersih BELUM DIBANGUN.** Ini pekerjaan Fase 1 yang tersisa, dan
jalurnya belum ditetapkan. Dua kemungkinan, keduanya perlu keputusan penelaah:

| Jalur | Cara | Untung | Rugi |
|---|---|---|---|
| Di dalam Word | Add-in menerapkan temuan berstatus diterima, mencabut seluruh tandanya, lalu penelaah **Save As** | Tanpa infrastruktur baru, naskah tidak keluar dari komputer | Naskah kerja ikut berubah; penelaah harus menyimpan versi coretannya lebih dulu |
| Lewat backend | Dokumen dikirim ke FastAPI, `python-docx` membuat berkas bersihnya | Naskah kerja utuh, hasilnya berkas terpisah | Rancangan PMK/KMK naik ke server — perlu izin |

Sampai salah satunya dipilih, tombol Terima belum menghasilkan naskah final.

### 6.8 Bentuk komentar

Satu komentar per temuan. Tidak lebih.

Komentar memuat **alasan**, bukan mengulang apa yang sudah terlihat. Pada temuan
`penggantian`, coretan merah dan usulan hijau di naskah sudah memperlihatkan apa
yang diusulkan berubah.

Dua baris, ditutup nomor urut temuan:

```
Nama jenis peraturan ditulis dengan huruf kapital pada kedua unsurnya.
KMK 527/KMK.01/2022 Lamp. II butir 33 — jdih.kemenkeu.go.id/... (T4)
```

Temuan `catatan` tidak menghasilkan coretan, jadi komentarnya harus menyebut
sendiri apa yang bermasalah:

```
Judul pada Menetapkan harus sama persis dengan judul pembuka — di sini berbeda.
Mana yang benar ditentukan penelaah.
KMK 527/KMK.01/2022 Lamp. II butir ... — jdih.kemenkeu.go.id/... (T2)
```

Aturan bentuknya:

- **Tanpa nama produk.** Ruang komentar terlalu sempit.
- **Tanpa tingkat keparahan.**
- **Kutipan utuh butirnya tidak ikut di komentar utama.** Taruh sebagai balasan
  komentar (`Comment.replies`, WordApi 1.4) — dibuka hanya bila penelaah ingin
  membaca teks aslinya. *Belum dibangun.*
- **`(T1)`, `(T2)` adalah nomor urut temuan menurut posisinya di dokumen**, sama
  dengan nomor di daftar panel. Bukan kode aturan. Kode aturan (`F1-005`) tetap
  ada di data tapi tidak pernah ditampilkan. Hurufnya **T** (temuan), sengaja
  bukan F, supaya tidak tertukar dengan awalan kode aturan `F1-`.

Nomor itu sekaligus penanda yang dipakai kode untuk menemukan kembali komentarnya
sendiri saat temuan ditolak. Karena nomornya melekat pada urutan dokumen,
menjalankan analisis dua kali menghasilkan dua komentar bernomor sama. Itu bukan
kemungkinan teoretis: pada pengujian 17 Sep 2026 dokumen contoh berakhir dengan
sekitar 18 komentar padahal temuannya 5. Karena itu **panel wajib menolak
menganalisis ulang selama masih ada temuan yang belum diputuskan**; jalan
keluarnya tombol Bersihkan Daftar, yang sekaligus mencabut seluruh tanda bertag
`DA-*` **dan seluruh komentar milik alat** dari naskah.

Komentarnya ikut dihapus sejak 18 Sep 2026. Sebelumnya Bersihkan Daftar hanya
mencabut content control dan meninggalkan komentarnya, sehingga pengaman di
atas bocor: sesudah Bersihkan Daftar penelaah boleh menganalisis lagi, komentar
lama masih ada, dan komentar baru memakai nomor `(T1)`, `(T2)` yang sama persis
— yaitu keadaan yang justru jadi alasan pengaman itu dipasang. Yang dikenali
sebagai milik alat: komentar yang isinya **diakhiri** penanda `(T<angka>)`.
Diikat ke ujung, supaya komentar penelaah yang kebetulan menyebut "(T3)" di
tengah kalimat tidak ikut terhapus. Jumlah yang dihapus disebutkan di panel.

### 6.9 Pembagian tugas antarmuka

| Tempat | Isinya |
|---|---|
| Naskah Word | Tandanya sendiri: merah-dicoret, hijau, blok kuning |
| Komentar Word | Alasan + rujukan butir KMK 527 + tautan PDF JDIH |
| Balasan komentar | Kutipan utuh butirnya (*belum dibangun*) |
| Task pane | Pilihan jenis dokumen (PMK/KMK) sebelum analisis; daftar ringkas: nomor temuan, satu baris cuplikan, Lompat ke Teks, Terima/Tolak |

Penjelasan panjang **tidak diulang** di task pane. Alasan temuan ditulis sekali,
di komentar. Duplikasi catatan yang sama di komentar dan di panel adalah keluhan
utama terhadap versi sebelumnya — penelaah membaca hal yang sama dua kali sambil
menggeser dua jendela.

**Semua keputusan diambil dari panel.** Rancangan sebelumnya menyerahkan
Accept/Reject temuan `penggantian` ke ribbon Word. Alasan teknisnya benar,
hasilnya tetap keliru: penelaah melihat satu daftar yang separuh kartunya bisa
ditekan dan separuhnya menyuruh pindah tempat. Dikoreksi 17 Sep 2026 atas
masukan penelaah — dan sejak Track Changes ditinggalkan, ribbon Review memang
tidak punya apa-apa untuk dikerjakan.

### 6.10 Kaidah anti-salah-tandai

> **Apa pun yang ditandai alat ini wajib benar-benar salah. Aturan yang tidak
> bisa membuktikan kesalahannya tidak boleh menandai apa pun.**

Kaidah ini ditetapkan penelaah 17 Sep 2026 sesudah dua salah tandai berturut-
turut pada RKMK 527 sungguhan — keduanya menyorot naskah yang sebenarnya sudah
benar. Satu salah tandai merusak kepercayaan lebih cepat daripada sepuluh temuan
benar membangunnya.

**Kasus 1 — F1-001, judul ber-ALL CAPS. Aturannya DIMATIKAN.**

Judul RKMK diketik huruf campur — "Perubahan Atas Keputusan Menteri Keuangan
Nomor 527/KMK.01/2022 …" — lalu ditampilkan kapital seluruhnya lewat gaya
paragraf bernama **ALL CAPS**. Buktinya terbaca di panel sendiri: kartu temuan
menampilkan cuplikan `"Perubahan Atas Keputusan Menteri Keuan…"` sementara di
badan Word tertulis `PERUBAHAN ATAS KEPUTUSAN MENTERI KEUANGAN NOMOR …`.

Aturan menemukan huruf kecil sungguhan — huruf kecil yang tidak bisa dilihat
siapa pun.

Penjaga `tampil_kapital` sempat dipasang: frontend membaca `font.allCaps` lalu
mengirimkannya per paragraf, dan F1-001 melewati paragraf bernilai `true`.
Penjaga itu **tidak menolong** di Word penelaah. `font.allCaps` ada di
`WordApiDesktop 1.3`, dan belum jelas apakah requirement set-nya tidak tersedia
atau propertinya buta terhadap kapital yang datang dari gaya paragraf. Selama
itu belum jelas, aturannya tidak boleh jalan.

Kandidat jalan keluar: baca OOXML paragrafnya (`Range.getOoxml()`, WordApi 1.1)
lalu cari penanda `<w:caps/>`, yang memuat definisi gaya juga. **Belum diuji, dan
dilarang dipasang sebelum diuji.**

Fungsinya sengaja tidak dihapus — logikanya masih benar untuk naskah yang
hurufnya betul-betul campur, dan tesnya masih menjaga logika itu. Yang dihapus
hanya pemanggilannya, lewat bendera `AKTIFKAN_F1_001 = False`.

Bendera `tampil_kapital` tetap ada di `ParagrafInput` supaya kontrak lama tidak
pecah, tapi frontend **tidak lagi mengirimkannya**: satu-satunya pemakainya
adalah aturan yang sudah mati, dan membacanya berarti satu putaran sync tambahan
atas ratusan paragraf untuk data yang tidak dipakai.

**Kasus 2 — F1-002, klausul Menetapkan kebablasan. Bug, sudah diperbaiki.**

Klausul `Menetapkan` diambil sampai bertemu penanda bagian berikutnya. Daftar
penandanya berbunyi `(BAB|Pasal|PERTAMA|KEDUA|KETIGA)` — itu penomoran diktum
**PMK**. Diktum KMK dimulai **KESATU**, yang tidak ada di daftar itu.

Akibatnya pengambilan melewati klausul Menetapkan dan menelan diktum KESATU
beserta seluruh isinya. Judul Menetapkan jadi sepanjang belasan paragraf, lalu
dilaporkan "berbeda dari judul pembuka" — padahal di naskah sama persis.

Tiga perbaikan, dan yang ketiga yang paling penting:

1. Daftar penanda ditambah seluruh penomoran diktum KMK (KESATU–KESEPULUH).
2. Penghenti yang lebih dapat diandalkan: judul pada Menetapkan selalu diakhiri
   titik, jadi paragraf pertama yang berakhiran titik menutup klausulnya. Tidak
   bergantung menebak kata apa yang datang sesudahnya. Titik di tengah nomor
   peraturan (`527/KMK.01/2022`) tidak kena karena yang diperiksa hanya akhir
   paragraf.
3. **Jaring pengaman: kalau hasil pengambilan lebih dari 60 kata, aturannya
   memilih DIAM.** Judul peraturan terpanjang di JDIH masih jauh di bawah angka
   itu; melewatinya berarti pengambilan gagal dan kita tidak tahu di mana.
   Melapor dalam keadaan itu sama dengan menuduh naskah yang mungkin sudah benar.

Dua tes regresi menyusun ulang struktur RKMK itu persis, termasuk diktum KESATU
dan paragraf lanjutannya. Tanpa perbaikan, keduanya gagal.

Butir 3 adalah bentuk umum kaidah ini di dalam kode: **tiap aturan yang bisa
kebablasan wajib punya batas kewajaran, dan di luar batas itu memilih diam.**

**Kasus 3 — F1-002, kata "menetapkan:" di batang tubuh. Bug, sudah diperbaiki.**

Pada RPMK DBH Sawit, Pasal 4 ayat (1) berbunyi *"Dalam rangka pengelolaan DBH
Sawit, Menteri selaku PA BUN Pengelola TKD **menetapkan:**"*. Pencarian klausul
Menetapkan memakai `re.search` tanpa jangkar, jadi kata itu ikut cocok — dan
isi Pasal 4 dituduh "judulnya berbeda dari judul pembuka", padahal itu bukan
judul sama sekali.

Ada sebab kedua yang memperparah: pada naskah yang menaruh klausul Menetapkan di
dalam **tabel**, label "Menetapkan" dan isinya jatuh di sel — dan karenanya di
paragraf — yang berbeda, sehingga paragraf labelnya cuma berbunyi "Menetapkan"
tanpa titik dua. Pola lama mewajibkan titik dua, jadi klausul yang sah justru
terlewat, lalu pencarian berjalan terus sampai menemukan "menetapkan:" di batang
tubuh.

Tiga perbaikan:

1. **Jendela pencarian.** Klausul Menetapkan yang sah punya letak yang pasti
   menurut KMK 527: sesudah `MEMUTUSKAN:` dan sebelum batang tubuh
   (BAB/Pasal/diktum). Pencarian hanya berlaku di jendela itu. Menetapkan di
   luar jendela itu bukan klausul Menetapkan.
2. **Jangkar di awal paragraf** (`^Menetapkan\b\s*:?`), dengan titik dua
   opsional supaya bentuk bertabel tetap terbaca.
3. Tanpa `MEMUTUSKAN` di dokumen, aturannya **diam** — tidak ada cara memastikan
   mana klausul Menetapkan.

**Kasus 4 — F1-004 mendarat di baris kosong. Bug, sudah diperbaiki.**

Pada PMK 119, penelaah melihat kartu hampa di panel: `#34 ""` — tanpa cuplikan,
tanpa warna, tanpa komentar, tapi bertombol Terima/Tolak yang tidak mengerjakan
apa pun.

Sebabnya, lokasi temuan diambil begitu saja dari `paragraf_akhir - 1`, yaitu
paragraf tepat sebelum "Mengingat" — yang pada naskah nyata sering **baris
kosong**. Teks aslinya kosong, panjangnya nol, tidak ada yang bisa ditandai.

Perbaikannya, paragrafnya dicari dari isi butirnya sendiri, dengan penanda
hurufnya dibuang lebih dulu (pada naskah bertabel, huruf "c." dan isi butirnya
ada di paragraf berbeda). Kalau butirnya tidak ketemu di mana pun, aturannya
diam.

Ditambah **jaring pengaman lapis terakhir di `jalankan_semua()`**: temuan
ber-`teks_asli` kosong dibuang sebelum dinomori. F1-003 dikecualikan — ketiadaan
sebuah bagian memang tidak punya lokasi di naskah, dan panel menampilkannya
sebagai kartu beralasan tanpa tombol keputusan (6.13).

**Kasus 5 — temuan terlalu panjang untuk bisa dicari. Bug, sudah diperbaiki.**

Pada PMK 5 Tahun 2025, F1-004 muncul di panel tetapi tidak ada tandanya di
naskah. Sebabnya bukan lokasi yang salah, melainkan **panjang**: butir Menimbang
terakhir di naskah itu 463 karakter, sedangkan `Word.search()` dibatasi sekitar
255 karakter. Temuan sepanjang itu tidak akan pernah ketemu, jadi tidak akan
pernah tertandai.

Perbaikannya di `_buat_temuan()`, satu tempat untuk semua aturan: rentang temuan
berjenis `catatan` dipotong di batas kata pada 120 karakter
(`_BATAS_PANJANG_TANDA`). Angkanya jauh di bawah batas Word — 120 karakter
kira-kira satu setengah baris, cukup menunjukkan tempatnya tanpa memblok satu
paragraf. Alasannya tetap di komentar, bukan di sorotan.

Pada butir PMK 5 itu, potongannya kebetulan mendarat tepat di penyimpangannya:
naskah menulis *"bahwa berdasarkan pertimbangan **huruf a**"*, bunyi bakunya
*"bahwa berdasarkan pertimbangan **sebagaimana dimaksud dalam** huruf a"*.

Pemotongan sengaja TIDAK berlaku untuk temuan `penggantian`: `teks_asli` di situ
harus sama persis dengan yang akan diganti `usulan_rumusan`. Rentang penggantian
memang selalu pendek — substitusi kata.

Bentuk umum kaidahnya, sejajar dengan butir 3 di Kasus 2: **temuan yang tidak
bisa ditemukan kembali di naskah sama saja dengan temuan yang tidak ada.**

**Kasus 6 — F1-011 menuduh isi diktum KMK. Bug, sudah diperbaiki 18 Sep 2026.**

`_cek_label_bagian()` — yang melayani F1-007, F1-009, dan F1-011 sekaligus —
menyapu **seluruh dokumen** mencari paragraf yang diawali labelnya, tanpa
jendela sama sekali. Pada KMK bertabel, "KESATU" dan isi diktumnya jatuh di
paragraf yang berbeda, sehingga isi diktumnya berbunyi *"Menetapkan Pedoman
Penyusunan … sebagaimana tercantum dalam Lampiran."* — diawali kata
"Menetapkan" tanpa titik dua. Aturan lalu menuduh batang tubuh yang klausul
Menetapkan-nya justru sudah benar.

Ini persis Kasus 3, lahir kembali di aturan yang ditambahkan belakangan.
Obatnya juga sama: tiap label sekarang punya jendela menurut letaknya di KMK
527 — Menimbang dan Mengingat sebelum `MEMUTUSKAN`, Menetapkan sesudahnya
sampai batang tubuh. Tanpa `MEMUTUSKAN` di dokumen, aturannya **diam**.

Pelajaran yang berlaku seterusnya: **aturan baru wajib mewarisi jendela yang
sudah dibayar mahal aturan lama.** Kalau sebuah aturan mencari kata kunci di
naskah, pertanyaan pertamanya "di jendela mana", bukan "polanya apa".

**Kasus 7 — pemindaian label berlanjut sesudah labelnya ketemu. Bug, sudah
diperbaiki.**

Komentar di kode berbunyi `break  # satu label, satu kali periksa`, tetapi
`break` itu hanya tercapai di cabang "titik dua tidak ada". Cabang normal —
labelnya sudah benar — memakai `continue`, jadi pemindaian justru berlanjut
**tepat ketika naskahnya tidak bersalah**. Dokumen yang memuat kata itu lagi di
tempat lain menghasilkan temuan kedua, kadang dengan rentang yang sama persis
dengan yang pertama. Dua tanda di satu rentang tidak bisa digambar maupun
dicabut sendiri-sendiri di Word.

Sekarang hanya kemunculan pertama di dalam jendelanya yang diperiksa, dan
ketiga cabangnya sama-sama mengakhiri pemeriksaan.

**Kasus 8 — F1-012 mencopot nama resmi peraturan lain. Bug, sudah diperbaiki.**

Butir 39 mengatur **jenis dan nama peraturan ini sendiri** yang dicantumkan
kembali sesudah kata "Menetapkan", tanpa frasa "Republik Indonesia". Jenis itu
berhenti di kata "TENTANG"; sesudahnya yang ada **judul**.

Pencarian lama mengenai seluruh kemunculan di klausulnya. Pada judul perubahan
— *"Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG PERUBAHAN ATAS PERATURAN
MENTERI KEUANGAN **REPUBLIK INDONESIA** NOMOR 5 TAHUN 2023 TENTANG …"* — yang
tertandai justru kemunculan kedua, yaitu nama resmi peraturan yang dirujuk.
Alat mengusulkan **mengubah nama resmi dokumen orang lain.**

Sekarang pemeriksaan itu dibatasi ke teks sebelum "TENTANG" pertama. Tanpa kata
"TENTANG" di klausulnya, jenis tidak bisa dipisahkan dari judul, dan
pemeriksaan itu **diam**.

**Kasus 9 — F1-008 menandai ujung paragraf, bukan ujung butir. Bug, sudah
diperbaiki.**

Letak titik koma diambil dari `len(p.teks.rstrip()) - 1`, yaitu karakter
terakhir **paragraf**. Sebuah paragraf Menimbang kerap memuat beberapa butir
sekaligus (*"Menimbang : a. … b. …"*), dan di naskah seperti itu tanda untuk
butir a mendarat di ujung butir b — tempat yang bukan miliknya. Lebih buruk
lagi, dua butir yang sama-sama kurang titik koma menghasilkan dua temuan
dengan rentang **identik**.

Sekarang ujungnya dicari dari isi butirnya sendiri. Kalau butirnya terpotong
antarparagraf, ujungnya tidak bisa dipastikan dan aturannya **diam** untuk
butir itu.

**Kasus 10 — jalur cadangan F1-002 menyorot satu paragraf penuh. Bug, sudah
diperbaiki.**

Ketika judul pada Menetapkan **kekurangan** kata dari judul pembuka, tidak ada
frasa beda yang bisa ditunjuk — yang salah justru kata yang tidak ada. Jalur
cadangannya menandai satu paragraf penuh berikut label `"Menetapkan : "` yang
bukan bagian judul sama sekali. Itu melanggar kaidah yang ditetapkan sendiri di
6.5 dan CLAUDE.md butir 5: **temuan yang rentang presisinya tidak ketemu tidak
ditandai sama sekali, bukan diperlebar ke satu paragraf.**

Sekarang temuannya dibuat **tanpa lokasi**, sama seperti F1-003, dan panel
menampilkannya sebagai peringatan dokumen (6.13). Informasinya utuh, naskahnya
tidak disentuh.

**Satu lubang cakupan yang ikut ditutup — `M E M U T U S K A N :`**

Bukan salah tandai, tetapi ditemukan sambil memperbaiki yang di atas dan
dampaknya besar. Penanda `MEMUTUSKAN` dicocokkan harfiah, padahal naskah
peraturan lazim menuliskannya renggang huruf demi huruf supaya tampak lapang.
Pada naskah seperti itu **F1-002 dan F1-012 sama-sama diam**, dan kesalahan
nyata di klausul Menetapkan lewat tanpa ada yang memberi tahu siapa pun.

Sekarang pengenalannya lewat satu tempat, `_cari_index_memutuskan()`, yang
menerima bentuk rapat maupun renggang. Seluruh aturan yang membutuhkannya wajib
lewat situ — supaya tidak ada aturan yang diam-diam memakai pencocokan yang
lebih sempit lagi.

**Kasus 11 — F1-002 menuduh judul berbeda padahal yang beda cuma titiknya.
Bug, sudah diperbaiki.**

Normalisasi kedua sisi tidak simetris: `_ekstrak_judul_menetapkan()` membuang
titik di akhir, sedangkan judul pembuka dibandingkan apa adanya. Pada naskah
yang judul pembukanya diakhiri titik — kesalahan yang **sudah** dilaporkan
F1-006 — F1-002 ikut melapor "judulnya berbeda", padahal kata per katanya sama
persis. Penelaah melihat dua tanda di dua tempat, salah satunya menuduh
perbedaan yang tidak ada.

Sekarang kedua sisi lewat `_samakan_untuk_banding()` yang sama. Pembagian
tugasnya jadi tegas: **F1-006 dan F1-012 mengurusi tanda baca penutupnya,
F1-002 mengurusi isi judulnya.** Tidak saling menuduh.

**Kasus 12 — F1-002 salah tandai pada naskah BERTABEL. Bug, sudah diperbaiki.**

Yang paling berdampak dari semuanya, karena bentuk bertabel itulah yang dipakai
naskah sungguhan.

Perbaikan Kasus 3 ternyata terpasang **separuh**. `_AWAL_MENETAPKAN` sudah
dibuat menerima label tanpa titik dua — bentuk yang muncul ketika label
"Menetapkan" dan isinya jatuh di sel yang berbeda — tetapi normalisasi di
bawahnya masih mewajibkan titik dua (`^.*?Menetapkan\s*:\s*`). Akibatnya
berantai:

1. kata "Menetapkan" ikut terbawa ke dalam judul;
2. awalan "KEPUTUSAN MENTERI KEUANGAN TENTANG" tidak terpotong, karena
   jangkar `^` tidak lagi mengenai apa pun;
3. judul yang **sama persis** dengan judul pembuka dilaporkan berbeda, dan yang
   tersorot justru kata "Menetapkan" itu sendiri.

Artinya hampir setiap KMK rapi yang pembukaannya bertabel akan mendapat satu
salah tandai. Titik duanya sekarang opsional juga di normalisasinya.

**Cara keduanya ditemukan, dan kenapa itu penting.** Keduanya tidak ketahuan
dari membaca kode maupun dari 86 tes yang sudah ada — keduanya muncul saat
naskah uji di `tools/contoh/` disusun, yaitu saat ada naskah yang
kesalahannya sudah diketahui lebih dulu lalu hasilnya dicocokkan. Itu pula
kegunaan berkas uji itu seterusnya: bukan sekadar contoh, melainkan alat
untuk menemukan salah tandai yang belum terpikirkan. Lihat bagian 16.2.

### 6.11 Batas yang sudah diketahui

- **Warna asli disimpan di memori panel, bukan di dokumen.** Kalau Word ditutup
  sebelum temuan diputuskan, add-in tidak lagi tahu format aslinya.
  Menyimpannya di custom XML part akan menghilangkan batas ini — belum
  dibangun. Sejak 18 Sep 2026 keadaan itu **tidak lagi memaksa semua warna jadi
  hitam**: yang dicabut hanya yang persis sama dengan warna milik alat sendiri
  (merah `#C00000` dan blok kuning), sisanya dibiarkan apa adanya. Sebelumnya
  Bersihkan Daftar menimpa warna huruf milik penyusun pada tiap temuan berblok
  kuning — padahal di situ alat tidak pernah menyentuh warna hurufnya sama
  sekali.
- **Dua temuan dari aturan berbeda bisa berimpit atau bersarang di satu
  rentang.** Contohnya kata terakhir judul Menetapkan yang sekaligus berbeda
  dari judul pembuka (F1-002) dan kehilangan titik penutupnya (F1-012); atau
  butir Menimbang terakhir yang bunyinya menyimpang (F1-004) sekaligus kurang
  titik koma di ujungnya (F1-008). Semuanya benar, tetapi hanya **satu yang
  digambar** — dua content control yang bertindihan membuat Word menyarangkan
  yang satu di dalam yang lain, dan menolak yang luar ikut menghapus tanda yang
  di dalam tanpa ada yang memberi tahu panel. Yang menang **yang lebih dahulu
  menurut urutan dokumen**, karena temuan yang lebih luas biasanya yang
  alasannya lebih lengkap. Yang kalah tetap muncul sebagai kartu, berlabel
  "tidak ditandai di naskah" dan dengan alasannya tercetak di kartunya.
  Temuannya **tidak dibuang** — menyembunyikan temuan yang benar lebih buruk
  daripada satu tanda yang tidak tergambar.
- **Kalau `changeTrackingMode` gagal dimatikan**, tanda alat ikut tercatat Word
  sebagai revisi format. Panel memberitahukannya dan menyarankan mematikan Track
  Changes lalu menjalankan ulang. Belum pernah terjadi pada pengujian.
- **Word tidak memberi tahu add-in** kalau penelaah mengubah naskah sendiri.
  Tanda yang dihapus manual tidak akan tercermin di panel.
- **Penelaah sebaiknya menjalankan alat pada salinan kerja**, bukan pada naskah
  asli. Ini versi pertama yang benar-benar menyisipkan teks ke dokumen. Ctrl+Z
  tetap bekerja normal.

### 6.12 Jenis dokumen dipilih penelaah, dan wajib

Sebagian aturan berperilaku beda menurut jenis dokumennya. Butir Menimbang
terakhir harus berbunyi "perlu menetapkan **Peraturan** Menteri Keuangan
tentang…" pada PMK dan "**Keputusan** Menteri Keuangan" pada KMK (F1-004). Blok
judul juga berakhir di penanda yang berbeda: PMK di
`DENGAN RAHMAT TUHAN YANG MAHA ESA`, KMK di
`MENTERI KEUANGAN REPUBLIK INDONESIA,`.

Sampai 17 Sep 2026 jenis itu **ditebak** oleh `_tentukan_jenis_dokumen()`:
paragraf pertama yang memuat "PERATURAN MENTERI KEUANGAN" dianggap PMK. Cara itu
bertumpu pada asumsi bahwa penyebutan pertama selalu datang dari blok judul —
dan asumsi itu rapuh. Pada RKMK sungguhan, bagian Mengingat memuat *"Peraturan
Menteri Keuangan Nomor 202/PMK.010/2017…"*. Kalau blok judulnya tidak terbaca
lebih dulu, KMK itu dikira PMK, lalu F1-004 menuntut bunyi yang salah — alat
menandai naskah yang sebenarnya sudah benar.

**Keputusan: jenis dokumen dipilih penelaah di task pane, sebelum menekan
Analisis.** Penelaah sudah tahu pasti dokumen apa yang sedang dia buka;
menebaknya berarti membangun kerumitan untuk menjawab pertanyaan yang jawabannya
sudah tersedia gratis.

Ketentuannya:

- **Tidak ada nilai awal.** Panel dimulai tanpa pilihan apa pun. Kalau salah
  satunya jadi bawaan, penelaah yang lupa memilih tetap dapat hasil analisis —
  hasil yang diperiksa memakai kaidah jenis dokumen yang keliru, tanpa ada apa
  pun yang memberi tahu. Lebih baik menolak berjalan daripada diam-diam salah.
  (Rancangan sebelumnya memakai PMK sebagai bawaan; dibatalkan atas masukan
  penelaah 17 Sep 2026.)
- Menekan Analisis tanpa memilih membuat baris pilihan **bergoyang** dan berubah
  merah, analisisnya tidak jalan. Goyangannya dimatikan sendiri bila sistem
  operasi meminta `prefers-reduced-motion`.
- `jenis_dokumen` dikirim ke backend sebagai bagian `AnalisisRequest`, dan
  **wajib terisi** — bukan opsional.
- `_tentukan_jenis_dokumen()` **dihapus**. Jenis diteruskan sebagai parameter ke
  `_ekstrak_judul_pembuka()` dan `cek_frasa_baku_menimbang()`.
- Cabang darurat di F1-004 yang selama ini jalan saat jenis tidak terdeteksi —
  melemah jadi sekadar memeriksa ada-tidaknya kata "tentang", tanpa memberi tahu
  siapa pun — **ikut dihapus**, karena keadaan "jenis tidak diketahui" tidak
  mungkin lagi terjadi. Ini cacat yang hilang, bukan yang ditambal.

Salah pilih tetap mungkin, tapi akibatnya kelihatan: temuan yang keluar janggal
beramai-ramai, labelnya terpampang di panel, dan membetulkannya satu klik.
Peringatan otomatis bila pilihan penelaah bertentangan dengan bunyi baris judul
**belum dibangun** — tambahkan hanya kalau terbukti penelaah sering salah pilih.

---

### 6.13 Temuan yang tidak punya lokasi

F1-003 memeriksa ketiadaan sebuah bagian wajib. Temuan seperti itu tidak punya
teks untuk ditunjuk — tidak ada yang bisa disorot kalau yang salah justru
teksnya tidak ada.

Sejak 18 Sep 2026 **F1-002 ikut bisa menghasilkan temuan tanpa lokasi**, dalam
satu keadaan: judul pada Menetapkan yang *kekurangan* kata dari judul pembuka.
Di situ pun yang salah adalah kata yang tidak ada, jadi tidak ada yang bisa
ditunjuk. Sebelumnya keadaan itu ditangani dengan menyorot satu paragraf penuh
— pelanggaran kaidah 6.5 yang riwayatnya ada di 6.10 Kasus 10. Daftar aturan
yang boleh begini hidup di satu tempat, `_BOLEH_TANPA_LOKASI` di
`rules/format_baku.py`; selain keduanya, temuan ber-`teks_asli` kosong tetap
dianggap cacat dan dibuang.

Sempat dicoba menampilkannya sebagai kartu biasa dengan alasannya dicetak di
dalam kartu dan tombol Terima/Tolak disembunyikan. Penelaah langsung menolaknya,
dan alasannya benar: panel tidak boleh memuat uraian panjang (itu tugas
komentar, bagian 6.9), dan kartu yang bentuknya berubah-ubah membuat daftar
sulit dibaca sekilas.

Ketentuannya sekarang:

- Temuan tanpa lokasi **tidak menjadi kartu**. Ditampilkan sebagai peringatan
  dokumen sebaris di atas daftar, dengan latar merah muda.
- Kartu temuan bentuknya **selalu sama**: nomor, penanda jenis, cuplikan,
  Lompat ke Teks, Terima, Tolak. Tidak ada tombol yang disembunyikan, tidak ada
  uraian panjang.
- **Satu perkecualian, ditambahkan 18 Sep 2026**: kartu yang temuannya **tidak
  tertandai di naskah** mencetak kalimat `catatan`-nya sendiri, di bawah
  cuplikan. Perkecualian ini perlu karena temuan itu tidak punya komentar di
  naskah yang bisa dibaca — kalau kartunya ikut bisu, penelaah cuma melihat
  cuplikan tanpa tahu apa yang dipersoalkan, yaitu persis kartu hampa yang
  dilaporkan pada PMK 119. Tombolnya tetap ada dan urutannya tetap sama, jadi
  daftarnya masih terbaca sekilas. Kartu yang tertandai **tetap tidak** mengulang
  penjelasan komentarnya (bagian 6.9).
- Temuan tanpa lokasi tidak ikut dihitung dalam pengaman analisis berulang —
  kalau ikut, tombol Analisis terkunci selamanya.
- `tandaiSemuaTemuan()` tetap mengembalikan daftar id temuan yang gagal
  ditandai, dan jumlahnya disebut di baris info. Sesudah pemotongan panjang di
  Kasus 5, sebab yang tersisa tinggal dua: rentangnya tidak ketemu di naskah,
  atau rentangnya berimpit dengan temuan lain yang menang (6.11).

### 6.14 Panel Pengaturan — pemeriksaan bisa dipilih dan diperiksa sendiri

Diminta penelaah 18 Sep 2026, dengan alasan yang tepat: **supaya bisa mengecek
manual.** Selama daftar pemeriksaan cuma hidup di kode Python, satu-satunya cara
tahu apa yang sebenarnya diperiksa adalah membaca kodenya — dan itu bukan
pekerjaan penelaah.

Tombol gerigi di header membuka panel berisi seluruh aturan Fase 1. Tiap aturan
punya:

- **Kotak centang** — mematikan aturan yang salah tandai tanpa menunggu kodenya
  diperbaiki. Daftar yang dicentang dikirim ke backend sebagai `aturan_aktif`;
  dihilangkan berarti semua aturan bawaan, supaya pemanggil lama tidak berubah
  artinya.
- **Rincian yang bisa dibuka**, memuat tiga hal: apa yang diperiksa, apa yang
  **TIDAK** diperiksa, dan bentuk tandanya di naskah. Bagian "tidak diperiksa"
  sama pentingnya — itulah yang memberi tahu penelaah apa yang masih harus dia
  periksa sendiri.
- Aturan yang dimatikan di kode (F1-001) tetap **ditampilkan**, dengan kotak
  centang nonaktif dan keterangan kenapa dimatikan. Menyembunyikannya berarti
  penelaah mengira judul kapital ikut diperiksa.

Keterangannya ada di `frontend/src/lib/aturan-fase1.ts`, dan **wajib sama
dengan** `backend/app/rules/format_baku.py`. Kalau aturannya berubah,
keterangannya ikut diubah di commit yang sama: keterangan yang bohong lebih
buruk daripada tidak ada keterangan sama sekali, karena penelaah memakainya
untuk memutuskan apa yang perlu diperiksa manual.

Menekan Analisis dengan nol pemeriksaan tidak dijalankan — panel Pengaturan
dibuka dan penelaah diberi tahu.

---

## 7. Susunan file — apa isinya dan siapa memanggil siapa

> Ditulis ulang 18 Sep 2026. Versi lama menyebut tujuh fungsi `office.ts` yang
> **tidak ada di kode** (`siapkanPelacakanPerubahan()`, `usulkanPenggantian()`,
> `sorotSementara()`, `tandaiTemuan()`, `insertCritiqueAnnotation()`,
> `insertPermanentComment()`, `critiqueTersedia()`) — sisa dua rancangan yang
> sudah gugur — dan menyatakan Terima/Tolak hanya untuk temuan `catatan`,
> padahal tombolnya selalu ada. Keterangan yang bohong lebih berbahaya daripada
> tidak ada keterangan.

```
drafter-analiser/
│
├── manifest.xml                     ← yang dibaca Word: ID add-in, nama, dan
│                                      URL task pane (https://localhost:3000/taskpane).
│                                      Didaftarkan lewat registry, lihat bagian 5
├── manifest-penuh.xml               ← varian bertombol ribbon + <Requirements>
├── pasang-addin.reg                 ← pendaftaran registry sekali klik
├── CLAUDE.md                        ← aturan kerja yang mengikat agen coding
│
├── docs/
│   ├── README.md                    ← indeks + urutan baca
│   ├── fase1 drafter.md             ← dokumen ini. SATU-SATUNYA acuan rancangan
│   ├── project-brief.md             ← KENAPA alat ini dibangun. Bukan spesifikasi
│   ├── panduan-officejs.md          ← API Word yang sudah diverifikasi + jebakannya
│   └── panduan-vibe.md              ← ringkasan konvensi (isinya pindah ke CLAUDE.md)
│
├── frontend/                        ← task pane. Ini yang DILIHAT penelaah
│   └── src/
│       ├── app/
│       │   ├── layout.tsx           ← kerangka HTML, memuat office.js, DAN
│       │   │                           penjaga history API — lihat Tahap 0
│       │   ├── page.tsx             ← halaman akar, tidak dipakai add-in
│       │   └── taskpane/page.tsx    ← ★ SELURUH panel: tombol, kartu temuan,
│       │                               panel Pengaturan, gerbang jenis dokumen.
│       │                               Tidak memanggil Office.js langsung —
│       │                               semuanya lewat office.ts
│       └── lib/
│           ├── office.ts            ← ★ SATU-SATUNYA berkas yang menyentuh Word.
│           │                           Baca paragraf, gambar tanda, pasang
│           │                           komentar, cabut tanda. Aturan repo:
│           │                           panggilan Office.js tidak boleh tersebar
│           ├── types.ts             ← bentuk data yang sama persis dengan backend
│           └── aturan-fase1.ts      ← keterangan tiap aturan untuk panel
│                                       Pengaturan. WAJIB sama dengan
│                                       format_baku.py — penelaah memakainya
│                                       untuk memutuskan apa yang perlu
│                                       diperiksa manual
│
└── backend/                         ← otaknya. Tidak tahu apa-apa soal Word
    ├── app/
    │   ├── main.py                  ← FastAPI + CORS + /health
    │   ├── core/config.py           ← nama env. Fase 1 tidak memakai satu pun
    │   ├── api/analisis.py          ← ★ POST /analisis/jalankan. SETIPIS MUNGKIN:
    │   │                               parse → panggil fungsi → kembalikan JSON.
    │   │                               Tidak ada logika pemeriksaan di sini
    │   ├── models/temuan.py         ← ★ KONTRAK. Bentuk Temuan, AnalisisRequest,
    │   │                               AnalisisResponse. Pydantic memvalidasinya
    │   ├── rules/
    │   │   ├── format_baku.py       ← ★★ SELURUH pemeriksaan ada di sini.
    │   │   │                            Fungsi murni: masuk daftar paragraf,
    │   │   │                            keluar daftar Temuan. Bisa dites tanpa
    │   │   │                            menyalakan server
    │   │   └── rujukan_kmk527.py    ← tabel tetap "aturan → butir KMK 527".
    │   │                               Diketik manusia dari pindaian halaman.
    │   │                               TIDAK BOLEH dikarang, tidak dari OCR
    │   ├── services/ parser/ llm/ retrieval/   ← KOSONG. Disiapkan untuk Fase 2/3
    │   └── tests/
    │       ├── test_format_baku.py  ← 86 tes. Tiap salah tandai yang pernah
    │       │                           terjadi punya tes regresinya sendiri
    │       └── test_api_analisis.py ← tes endpoint
    └── tools/                       ← alat diagnosa. BUKAN bagian produk,
        │                              tidak ikut ke add-in
        ├── cek_docx.py              ← jalankan aturan terhadap sebuah .docx
        │                              TANPA membuka Word
        ├── buat_contoh_uji.py       ← bangkitkan naskah uji + kunci jawabannya
        └── contoh/
            ├── contoh-rancangan-uji.docx  ← naskah contoh lama
            ├── uji-pmk-lengkap.docx       ← naskah PMK, kesalahannya diketahui
            ├── uji-kmk-lengkap.docx       ← naskah KMK, pembukaan BERTABEL
            └── KUNCI-UJI.md               ← kunci, DIBANGKITKAN — jangan
                                             disunting tangan
```

Tiga berkas bertanda ★★ dan ★ itu yang menanggung hampir seluruh pekerjaan.
Kalau ada yang salah, urutan menebaknya: `format_baku.py` (aturannya keliru) →
`office.ts` (tandanya tidak mendarat di tempat yang benar) → `page.tsx`
(panelnya yang keliru menampilkan).

---

## 8. Alur lengkap — dari tombol ditekan sampai tanda muncul di naskah

```
     PENELAAH                TASK PANE              BACKEND              WORD
        │                  (page.tsx)            (FastAPI)           (office.ts)
        │
  tekan │ Analisis
        ├──────────────────────▶ 3 gerbang
        │                        (jenis? aturan? temuan lama?)
        │                            │
        │                            ├──────────────────────────────────▶ baca
        │                            │                         readParagraphs()
        │                            ◀──────────── [{index, teks}, …] ───────┤
        │                            │
        │                            ├── POST /analisis/jalankan ──▶ jalankan_semua()
        │                            │                                   │
        │                            │                          11 aturan berjalan
        │                            │                          → saring → urutkan
        │                            │                          → nomori T1..Tn
        │                            ◀───── [Temuan, …] ─────────────────┤
        │                            │
        │                            ├──────────────────────────────────▶ gambar
        │                            │                      tandaiSemuaTemuan()
        │                            │                                   │
        │   ◀── kartu T1..Tn ────────┤                      merah/hijau/kuning
        │                                                   + content control
        │                                                   + satu komentar
```

### Tahap 0 — sebelum apa pun (sekali, saat panel dibuka)

Word membaca `manifest.xml`, memuat `https://localhost:3000/taskpane` sebagai
halaman web biasa di dalam panel. `Office.onReady` memberi tahu panel bahwa
host-nya Word, lalu panel memeriksa requirement set yang dibutuhkannya —
**1.1** untuk penandaan, **1.3** untuk cakupan terpilih, **1.4** untuk komentar
dan `changeTrackingMode`. Hasilnya yang terlihat di tombol "Word Connected".

Satu hal yang mudah membingungkan kalau halaman tiba-tiba gagal render:
**`layout.tsx` memasang penjaga `history.pushState` / `history.replaceState`
sebelum office.js dimuat.** Office.js sengaja melumpuhkan keduanya supaya
add-in tidak bisa berpindah halaman keluar dari task pane — sedangkan router
Next.js membutuhkannya, dan tanpa penjaga itu halaman mati dengan
`window.history.replaceState is not a function`. Urutan tag di `<head>`
menentukan urutan pemuatan; jangan ditukar.

Panel sengaja dimulai **tanpa jenis dokumen terpilih**. Alasannya di 6.12.

### Tahap 1 — tiga gerbang sebelum analisis jalan

`handleJalankanAnalisis()` di `taskpane/page.tsx`. Tidak satu pun boleh dilewati:

| Gerbang | Kalau gagal | Kenapa |
|---|---|---|
| Jenis dokumen sudah dipilih? | Baris pilihan **bergoyang** merah, analisis tidak jalan | Tanpa PMK/KMK, F1-004 menuntut bunyi frasa yang salah — alat akan menandai naskah yang benar |
| Ada aturan yang dinyalakan? | Panel Pengaturan dibuka | Nol aturan berarti nol temuan, dan penelaah mengira naskahnya bersih |
| Masih ada temuan yang belum diputuskan? | Tombol Analisis **mati** | Analisis ulang memasang komentar bernomor sama. Pernah menghasilkan ~18 komentar untuk 5 temuan (6.8) |

### Tahap 2 — membaca naskah (`readParagraphs`, office.ts)

```
context.document.body.paragraphs → load("text") → sync()
```

Hasilnya daftar `{ index, teks }`. **`index` selalu nomor paragraf di seluruh
dokumen**, bahkan pada mode "Bagian Terpilih" — kalau dihitung ulang dari nol di
dalam seleksi, tanda akan mendarat di paragraf yang sama sekali lain saat
digambar nanti.

Yang **tidak** dibaca: gaya paragraf, warna, ALL CAPS. Backend hanya menerima
teks apa adanya. Itu sebabnya F1-001 (judul kapital) dimatikan — dari teks saja,
judul ber-gaya ALL CAPS tidak bisa dibedakan dari judul yang hurufnya campur.

### Tahap 3 — dikirim ke backend

```json
POST /analisis/jalankan
{ "jenis_dokumen": "PMK",
  "aturan_aktif": ["F1-002", "F1-004", …],
  "paragraf": [ { "index": 0, "teks": "PERATURAN MENTERI KEUANGAN …" }, … ] }
```

`api/analisis.py` sengaja setipis mungkin — **parse → panggil `jalankan_semua()`
→ kembalikan JSON**. Tidak ada logika pemeriksaan di situ, supaya seluruh aturan
bisa dites tanpa menyalakan server. Pydantic yang menolak request cacat: tanpa
`jenis_dokumen`, permintaannya ditolak sebelum menyentuh aturan apa pun.

### Tahap 4 — BAGAIMANA KESALAHAN DITEMUKAN (`format_baku.py`)

Ini intinya. Empat lapis, berurutan.

**Lapis 1 — cari jangkar dulu, jangan cari kesalahan dulu.**

Aturan tidak boleh menyapu seluruh dokumen. Ia harus tahu dulu **di mana** dia
berhak memeriksa. Pencarian jangkarnya:

| Jangkar | Fungsi | Dipakai untuk menandai batas |
|---|---|---|
| `TENTANG` (paragraf yang isinya persis itu) | `_ekstrak_judul_pembuka()` | Awal blok judul |
| `DENGAN RAHMAT TUHAN YANG MAHA ESA` (PMK) / `MENTERI KEUANGAN REPUBLIK INDONESIA,` (KMK) | idem | Akhir blok judul |
| `MEMUTUSKAN` — rapat **atau** berspasi `M E M U T U S K A N` | `_cari_index_memutuskan()` | Batas pembukaan ↔ diktum |
| `Menimbang` / `Mengingat` di awal paragraf | `_ekstrak_bagian()`, `_ekstrak_rentang_mengingat()` | Rentang konsiderans dan dasar hukum |
| `BAB` / `Pasal` / `KESATU`…`KESEBELAS…` | `_PENGHENTI_MENETAPKAN` | Awal batang tubuh |

Jangkar inilah yang membuat aturan aman. Contoh nyatanya: kata `menetapkan:`
juga muncul di tengah Pasal 4 RPMK DBH Sawit. Tanpa jendela "sesudah MEMUTUSKAN,
sebelum batang tubuh", isi Pasal 4 dituduh sebagai judul yang salah (6.10 Kasus 3).

**Lapis 2 — sebelas aturan berjalan, masing-masing fungsi murni.**

Tiap fungsi menerima `list[ParagrafInput]` dan mengembalikan `list[Temuan]`.
Tidak ada state, tidak ada Request/Response, jadi semuanya bisa dites langsung.

| Aturan | Yang dicari | Jenis tanda |
|---|---|---|
| F1-002 | Judul pembuka ≠ judul pada Menetapkan, dibandingkan **kata per kata** dengan `difflib` | `catatan` |
| F1-003 | Ada tidaknya Menimbang / Mengingat / Menetapkan | `catatan`, tanpa lokasi |
| F1-004 | Bunyi butir Menimbang terakhir (butir 22) | `catatan` |
| F1-005 | Ejaan di **dasar hukum saja**: `Undang-undang` → `Undang-Undang`, `Tentang` → `tentang` | `penggantian` |
| F1-006 | Judul diakhiri tanda baca (butir 8) | `penggantian` |
| F1-007 / F1-009 / F1-011 | Penulisan label Menimbang / Mengingat / Menetapkan (butir 16/23/38) | keduanya |
| F1-008 | Tiap butir Menimbang diawali "bahwa", diakhiri ";" (butir 21) | `catatan` |
| F1-010 | Tiap dasar hukum diakhiri ";" (butir 31) | `catatan` |
| F1-012 | Judul pada Menetapkan: tanpa "Republik Indonesia", diakhiri "." (butir 39) | `penggantian` |

F1-001 (judul kapital) ada di kode tetapi **tidak dipanggil** —
`AKTIFKAN_F1_001 = False`.

**Kaidah yang mengikat semuanya: kalau tidak bisa dibuktikan, DIAM.** Ini bukan
gaya bahasa, ini cabang `return []` sungguhan di kode:

- Judul hasil pengambilan lebih dari 60 kata → pengambilannya gagal → diam
- `MEMUTUSKAN` tidak ada → letak klausul Menetapkan tidak pasti → diam
- Paragraf labelnya cuma berbunyi "Menimbang" tanpa titik dua → pada naskah
  bertabel titik duanya ada di sel sebelah → tidak bisa dibuktikan hilang → diam
- Butir Menimbang tidak ketemu paragrafnya → diam
- Potongan butir < 15 karakter → hampir pasti hasil pemecahan yang gagal → diam
- Tidak ada satu pun dasar hukum berangka → nomornya mungkin di sel lain → diam
- Kata "TENTANG" tidak ada di klausul Menetapkan → jenis tidak bisa dipisahkan
  dari judul → diam

**Lapis 3 — tiap temuan dibentuk lewat satu pintu, `_buat_temuan()`.**

Di situ tiga hal terjadi sekaligus:

1. Rujukan diambil dari `rujukan_kmk527.py` — tidak pernah dikarang aturan.
2. Rentang temuan `catatan` **dipotong di 120 karakter** pada batas kata.
   Bukan soal tampilan: `Word.search()` dibatasi ~255 karakter, dan temuan yang
   lebih panjang tidak akan pernah ketemu di naskah — penelaah cuma melihat
   kartu tanpa ada apa pun di dokumen (6.10 Kasus 5). Temuan `penggantian`
   **tidak** dipotong; `teks_asli`-nya harus sama persis dengan yang diganti.
3. `teks_asli` diiris dari `paragraf.teks` apa adanya, memakai `offset_mulai`
   dan `panjang`. Irisan inilah kata kunci yang dipakai sisi Word nanti.

**Lapis 4 — `jalankan_semua()` merapikan hasil gabungannya.**

```
buang temuan ber-teks_asli kosong   (kecuali F1-002 dan F1-003 — 6.13)
      ↓
urutkan menurut (paragraf_index, offset_mulai)
      ↓
buang temuan kembar dari aturan yang SAMA di rentang yang sama persis
      ↓
nomori 1, 2, 3 … → inilah (T1), (T2) yang dibaca penelaah
```

Nomor itu penting: ia muncul di kartu panel, di ujung komentar Word, **dan**
jadi isi tag content control `DA-ASLI-{nomor}`. Tiga tempat, satu nomor — itu
yang membuat panel dan naskah bisa saling menemukan.

### Tahap 5 — menggambar tanda (`tandaiSemuaTemuan`, office.ts)

Backend tahu "paragraf 11, karakter 5–97". Word tidak mengenal offset — ia
hanya bisa **mencari teks**. Delapan langkah, semuanya dalam satu `Word.run`:

1. **Matikan pelacakan perubahan**, ingat mode semula. Kalau tidak, tiap
   pewarnaan tercatat Word sebagai revisi `Formatted: Highlight` dan mengubur
   komentarnya (6.1).
2. **Cari rentang presisi seluruh temuan sekaligus** — satu batch, bukan satu
   per satu: `paragraph.search(teks_asli, { matchCase: true })`.
3. **Hitung kemunculan keberapa.** `search()` mengembalikan SEMUA kemunculan di
   paragraf itu. Tanpa `ordinalKemunculan()`, temuan pada kata berulang —
   "PERATURAN" di judul pencabutan — selalu mendarat di kemunculan pertama.
4. **Rekam format asli** tiap rentang (warna, coretan, sorotan), disimpan di
   memori panel dengan kunci nomor temuan. Inilah yang dipakai Tolak nanti.
5. **Pilih pemenang untuk rentang yang bertumpuk**, menurut urutan dokumen.
   Dua content control yang bertindihan membuat Word menyarangkan yang satu di
   dalam yang lain (6.11).
6. **Gambar dari BAWAH ke ATAS.** Menyisipkan usulan hijau menggeser posisi
   karakter sesudahnya, jadi yang paling bawah dikerjakan lebih dulu.
   - punya usulan → teks lama `#C00000` + dicoret, usulannya disisipkan
     `insertText(" …", "After")` warna `#00802B`
   - tanpa usulan → `highlightColor = "Yellow"`, **warna huruf tidak disentuh**
7. **Bungkus content control** bertag `DA-ASLI-{n}` / `DA-USUL-{n}`,
   penampilannya `Hidden`. Word tidak menyimpan apa pun tentang "usulan mesin";
   tag inilah satu-satunya cara add-in mengenali kembali tandanya sendiri.
8. **Satu komentar per temuan**, dua baris: alasan, lalu rujukan butir + tautan
   + `(Tn)`. Terakhir, **kembalikan mode pelacakan** ke semula.

**Temuan yang rentangnya tidak ketemu TIDAK ditandai sama sekali** — bukan
diperlebar ke satu paragraf. Id-nya dikembalikan lewat `idTidakDitandai`, dan
kartunya di panel mencetak alasannya sendiri, karena bagi temuan itu tidak ada
komentar di naskah yang bisa dibaca.

### Tahap 6 — keputusan penelaah

| Tombol | Yang terjadi di naskah |
|---|---|
| **Lompat ke Teks** | `selectFindingLocation()` — pakai content control kalau ada (paling tepat sesudah naskah bergeser), kalau tidak jatuh ke pencarian teks + hitungan kemunculan |
| **Terima** | **Naskah sengaja tidak disentuh.** Yang berubah hanya status kartu. Naskah merah-hijau ini justru dokumen coretan yang dibawa ke rapat; usulannya baru diterapkan saat ekspor versi bersih (6.7, belum dibangun) |
| **Tolak** | `tolakTemuan()` — `DA-USUL-{n}` dihapus berikut isinya, `DA-ASLI-{n}` dipulihkan formatnya lalu bungkusnya saja dilepas, komentarnya dihapus. Tidak boleh ada bekas |
| **Bersihkan Daftar** | `bersihkanSemuaTanda()` — cabut seluruh tanda `DA-*` **dan** seluruh komentar milik alat. Warna milik penyusun tidak disentuh |

### Kalau mau menelusurinya sendiri

Jalur tercepat memahami satu temuan, tanpa membuka Word:

```bash
cd backend && python tools/cek_docx.py <berkas.docx> --jenis PMK
```

Keluarannya memperlihatkan daftar paragraf apa adanya (termasuk isi tabel),
lalu tiap temuan berikut `[offset:offset+panjang]`-nya. Dari situ bisa dilacak
mundur: aturan mana yang mengeluarkannya, jangkar apa yang dipakainya, dan
kenapa rentangnya sepanjang itu.

---

## 9. Struktur database

### Fase 1 tidak memakai database sama sekali

Ini keputusan sadar, bukan kelalaian:

- Pemeriksaan Fase 1 selesai dalam hitungan detik — tidak ada proses latar
  belakang yang perlu dilanjutkan bila terputus.
- Temuan hidup di memori task pane selama dokumen terbuka.
- Keputusan penelaah tersimpan **di dalam berkas .docx itu sendiri** — sebagai
  perubahan terlacak yang diterima/ditolak, dan sebagai komentar. Ikut ke mana
  pun dokumen dibawa, tanpa perlu server.
- Tabel rujukan KMK 527 ada di kode (bagian 10), bukan di database.

Menambahkan database di Fase 1 berarti menambah satu komponen yang bisa gagal,
satu kredensial yang harus dijaga, dan satu langkah pemasangan — tanpa satu pun
kemampuan baru. Bertentangan dengan prinsip "sederhana dahulu".

### Kapan database benar-benar diperlukan

Di Fase 2/3, saat analisis berjalan menit sampai jam dan hasilnya harus bertahan
meski prosesnya terputus (brief bagian 8.9). Skemanya dirancang saat itu tiba —
**bukan sekarang**. Dokumen ini memuat Fase 1 saja; merancang tabel untuk
kebutuhan yang belum ada berarti mengunci keputusan sebelum kebutuhannya
diketahui.

Yang perlu diingat sekarang hanya dua hal, supaya tidak menyulitkan nanti:

- ORM-nya **SQLModel**, bukan Prisma — satu model dipakai sekaligus sebagai
  skema validasi FastAPI dan tabel database, sejalan dengan Pydantic yang sudah
  dipakai di `models/temuan.py`.
- Nama variabel `DATABASE_URL` sudah disiapkan di `core/config.py` supaya
  berkas itu tidak dirombak ulang.

## 10. Tabel rujukan KMK 527 — tanpa AI, tanpa OpenSearch

Pemetaan "aturan → butir KMK 527" bersifat **tetap dan satu lawan satu**. Aturan
"judul harus kapital" selalu bersumber dari butir yang sama, dokumen apa pun
yang diperiksa. Yang tidak pernah berubah tidak perlu dicari ulang.

```python
# backend/app/rules/rujukan_kmk527.py
RUJUKAN = {
    "F1-001": {
        "nama_aturan": "Judul ditulis kapital seluruhnya",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",          # diisi dari hasil baca visual
        "kutipan": "...",        # diketik ulang manual
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
    # satu entri per aturan Fase 1
}
```

**Jangan ambil kutipan ini dari OpenSearch:**

1. Salinan KMK 527 di JDIH hasil pemindaian dengan OCR rusak. Apa pun yang masuk
   index diturunkan dari teks korup — tidak boleh ditampilkan ke penelaah
   sebagai dasar koreksi.
2. Struktur index OpenSearch itu Dokumen → Blok, **satu blok per pasal**.
   Aturan teknik penyusunan ada di Lampiran II yang penomorannya butir, bukan
   pasal — pemotongan per-pasal tidak presisi sampai tingkat butir.

**Jangan pakai model untuk mencari butirnya.** Brief bagian 8.10 mencantumkan
"model mengarang nomor peraturan" sebagai risiko. Tabel statis yang diverifikasi
manusia tidak pernah salah kutip.

Pekerjaan manusia sekali di depan: baca KMK 527 Lampiran II **secara visual**,
catat butir mana mengatur apa, ketik ulang kutipannya. Untuk 5–10 aturan Fase 1
itu pekerjaan setengah hari, hasilnya aset permanen.

**Status sekarang: seluruh entri masih placeholder `"..."`.** Selama itu,
temuan wajib ditandai "rujukan belum diverifikasi" di antarmuka.

---

## 11. Bentuk data Temuan — KONTRAK

> Bagian ini **satu-satunya** sumber kontrak data. Berkas `docs/kontrak-data.md`
> yang dulu memuat salinannya sudah dihapus 18 Sep 2026: dua berkas yang harus
> disamakan manual setiap kali berubah adalah pabrik cacat, dan sempat benar-
> benar berbeda isi.

```json
{
  "id": "f-a1b2c3d4",
  "nomor": 1,
  "aturan_id": "F1-005",
  "fase": 1,
  "jenis_tanda": "penggantian",
  "lokasi": {
    "paragraf_index": 15,
    "offset_mulai": 5,
    "panjang": 13,
    "teks_asli": "Undang-undang"
  },
  "catatan": "Nama jenis peraturan ditulis dengan huruf kapital pada kedua unsurnya.",
  "usulan_rumusan": "Undang-Undang",
  "rujukan": {
    "sumber": "KMK 527/KMK.01/2022 Lampiran II",
    "butir": "...",
    "kutipan": "...",
    "pdf_url": "https://jdih.kemenkeu.go.id/..."
  },
  "status": "belum_ditinjau"
}
```

### Penjelasan field

| Field | Tipe | Keterangan |
|---|---|---|
| `id` | string | Identifier unik temuan dalam satu sesi analisis |
| `nomor` | integer | Nomor urut menurut posisi di dokumen, mulai dari 1 |
| `aturan_id` | string | Kunci ke tabel rujukan (`F1-001`, dst.). **INTERNAL** — tidak pernah ditampilkan ke penelaah |
| `fase` | integer | Selalu `1` untuk Fase 1 |
| `jenis_tanda` | enum | `"penggantian"` \| `"catatan"` |
| `lokasi.paragraf_index` | integer | Indeks paragraf dalam daftar yang dikirim |
| `lokasi.offset_mulai` | integer | Posisi karakter awal di dalam paragraf |
| `lokasi.panjang` | integer | Panjang karakter yang ditandai |
| `lokasi.teks_asli` | string | Teks asli yang bermasalah — dipakai frontend sebagai kata kunci `Word.search()` |
| `catatan` | string | **Alasan** temuan, bukan pengulangan apa yang sudah terlihat di naskah |
| `usulan_rumusan` | string \| null | Rumusan pengganti — lihat aturan yang mengikat di bawah |
| `rujukan.sumber` | string | Nama peraturan sumber |
| `rujukan.butir` | string | Nomor butir spesifik |
| `rujukan.kutipan` | string | Kutipan isi butir |
| `rujukan.pdf_url` | string | URL PDF di JDIH |
| `status` | enum | `"belum_ditinjau"` \| `"diterima"` \| `"ditolak"` |

### `nomor` — penomoran temuan

Nomor urut menurut posisi di dokumen: temuan paling atas `1`, berikutnya `2`.
Ditetapkan **backend**, sesudah seluruh aturan dijalankan dan temuannya
diurutkan menurut `paragraf_index` lalu `offset_mulai`.

Nomor inilah yang tampil sebagai `(T1)`, `(T2)` di ujung komentar dan sebagai
nomor di daftar panel, supaya penelaah bisa melompat bolak-balik antara naskah
dan panel tanpa menerjemahkan apa pun. `aturan_id` tidak pernah muncul di
antarmuka.

### `jenis_tanda` — cara temuan dipasang di dokumen

| Nilai | Dipakai bila | Cara dipasang |
|---|---|---|
| `penggantian` | Ada satu rumusan pengganti yang deterministik untuk `lokasi.teks_asli` | Teks lama MERAH `#C00000` + dicoret; `usulan_rumusan` disisipkan di sebelahnya, HIJAU `#00802B` |
| `catatan` | Tidak ada pengganti tunggal — yang salah adalah ketiadaan sesuatu, atau alat tidak tahu mana dari dua kemungkinan yang benar | BLOK KUNING (`font.highlightColor = "Yellow"`); warna huruf TIDAK disentuh |

Keduanya diberi tepat satu komentar dan diputuskan dari task pane. Seluruh
penandaan berjalan dengan `changeTrackingMode = "Off"`, lalu mode semula
dikembalikan. Tiap tanda dibungkus content control bertag `DA-ASLI-{nomor}` atau
`DA-USUL-{nomor}`. Lihat bagian 6.3 dan 6.4.

**Aturan yang mengikat:**

- Bila `jenis_tanda` = `"penggantian"`, `usulan_rumusan` **wajib terisi** dan
  harus berupa teks pengganti harfiah untuk `lokasi.teks_asli` — bukan contoh
  bunyi, bukan penjelasan. Isi field inilah yang benar-benar disisipkan ke
  naskah orang.
- Bila `jenis_tanda` = `"catatan"`, `usulan_rumusan` boleh `null` atau berisi
  contoh bunyi yang hanya ditampilkan, tidak pernah disisipkan.
- Fungsi aturan **wajib menetapkan `jenis_tanda` secara eksplisit.** Jangan
  menyimpulkannya dari ada-tidaknya `usulan_rumusan` — suatu saat ada aturan
  yang usulannya cuma contoh, dan menebak di situ berarti salah menyunting
  naskah orang.
- Temuan `penggantian` **tidak** diberi blok kuning, dan temuan `catatan`
  **tidak** diberi warna merah. Merah berarti "ada penggantinya".

### Pemetaan aturan Fase 1

| Aturan | `jenis_tanda` | Aktif | Alasan |
|---|---|---|---|
| F1-001 judul kapital | `catatan` | **tidak** | Dimatikan — bagian 6.10 |
| F1-002 judul pembuka ≠ judul Menetapkan | `catatan` | ya | Alat tidak tahu mana dari dua judul itu yang benar |
| F1-003 kelengkapan struktur | `catatan` | ya | Yang salah adalah ketiadaan bagian |
| F1-004 frasa baku butir Menimbang terakhir | `catatan` | ya | Bunyi bakunya perlu menyebut huruf mana saja yang dirujuk |
| F1-005 ejaan | `penggantian` | ya | Substitusi kata |
| F1-006 judul diakhiri tanda baca | `penggantian` | ya | butir 8 — imperatif |
| F1-007 penulisan "Menimbang" | `penggantian` / `catatan` | ya | butir 16 — imperatif |
| F1-008 bentuk tiap butir Menimbang | `catatan` | ya | butir 21 — imperatif |
| F1-009 penulisan "Mengingat" | `penggantian` / `catatan` | ya | butir 23 — imperatif |
| F1-010 tanda baca dasar hukum | `catatan` | ya | butir 31 — imperatif. Penomoran angka Arab-nya sendiri BELUM diperiksa |
| F1-011 penulisan "Menetapkan" | `penggantian` / `catatan` | ya | butir 38 — imperatif |
| F1-012 bentuk judul pada Menetapkan | `penggantian` | ya | butir 39 — imperatif |

Pada `backend/tools/contoh/contoh-rancangan-uji.docx`: 2 `penggantian`,
3 `catatan`.

### Bentuk `catatan`

Ditulis sebagai alasan, dua baris, tanpa nama produk dan tanpa tingkat
keparahan. Apa yang berubah sudah terlihat dari coretan di naskah, jadi tidak
diulang:

```
Nama jenis peraturan ditulis dengan huruf kapital pada kedua unsurnya.
KMK 527/KMK.01/2022 Lamp. II butir 33 — jdih.kemenkeu.go.id/... (T4)
```

Temuan `catatan` tidak menghasilkan coretan, jadi harus menyebut sendiri apa
yang bermasalah:

```
Judul pada Menetapkan harus sama persis dengan judul pembuka — di sini berbeda.
Mana yang benar ditentukan penelaah.
KMK 527/KMK.01/2022 Lamp. II butir ... — jdih.kemenkeu.go.id/... (T2)
```

### Bentuk AnalisisRequest

```json
{
  "jenis_dokumen": "PMK",
  "aturan_aktif": ["F1-002", "F1-003", "F1-004", "F1-005"],
  "paragraf": [
    { "index": 0, "teks": "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA" }
  ]
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `jenis_dokumen` | enum | `"PMK"` \| `"KMK"` — **wajib**, dipilih penelaah sebelum menekan Analisis (bagian 6.12). Backend tidak menebaknya |
| `aturan_aktif` | array \| null | Daftar `aturan_id` yang dijalankan, dipilih di panel Pengaturan (bagian 6.14). `null`/dihilangkan berarti seluruh aturan bawaan |
| `paragraf[].index` | integer | Indeks paragraf di dokumen |
| `paragraf[].teks` | string | Isi teks paragraf |
| `paragraf[].tampil_kapital` | boolean | Opsional, default `false`. **Tidak lagi dikirim frontend** — satu-satunya pemakainya F1-001 yang sudah dimatikan. Dibiarkan ada supaya kontrak lama tidak pecah |

### Batas yang wajib dipatuhi aturan

- **Rentang temuan `catatan` dipotong di 120 karakter**, di batas kata
  (`_BATAS_PANJANG_TANDA`). Bukan soal tampilan: `Word.search()` dibatasi
  sekitar 255 karakter, jadi temuan yang lebih panjang tidak pernah ketemu dan
  tidak pernah tertandai di naskah. Temuan `penggantian` TIDAK dipotong —
  `teks_asli`-nya harus sama persis dengan yang diganti `usulan_rumusan`.
- **Temuan ber-`teks_asli` kosong dibuang `jalankan_semua()`**, kecuali F1-003.
  Temuan tanpa teks tidak bisa ditandai di Word dan muncul di panel sebagai
  kartu hampa. F1-003 dikecualikan karena ketiadaan sebuah bagian memang tidak
  punya lokasi; panel menampilkannya sebagai peringatan dokumen (bagian 6.13).
- **`offset_mulai` dan `panjang` menandai rentang presisi**, bukan satu paragraf
  penuh (bagian 6.5). Temuan yang rentangnya tidak ketemu di Word **tidak
  ditandai sama sekali**, bukan diperlebar.
- Selama `rujukan.butir` atau `rujukan.kutipan` masih `"..."`, panel wajib
  menampilkan penanda "rujukan belum diverifikasi". Tidak boleh ditampilkan
  seolah punya dasar hukum final.
- Nomor `(T1)`, `(T2)` juga dipakai kode untuk menemukan kembali komentarnya
  sendiri. Karena nomornya melekat pada urutan dokumen, menjalankan analisis dua
  kali menghasilkan komentar bernomor sama — panel wajib menolak menganalisis
  ulang selama masih ada temuan yang belum diputuskan (bagian 6.8).

---

## 12. Environment variables

**Nilai asli tidak boleh disalin ke repo, ke chat, atau ke agen coding.** Yang
boleh diketahui agen coding hanya nama variabelnya.

Fase 1 memakai satu env yang sudah ada di kerangka:

| Variabel | Untuk apa |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Alamat backend yang dipanggil task pane lewat `fetch`. Sudah ada di `frontend/.env.example` — pakai langsung, jangan hardcode URL di kode |

Prefiks `NEXT_PUBLIC_` wajib untuk env yang dibaca kode yang jalan di browser.
Karena itu juga: **jangan pernah** beri prefiks ini ke variabel berisi
kredensial, karena otomatis ikut ter-build ke kode yang bisa dibaca siapa pun
lewat DevTools.

Nama variabel untuk Fase 2/3 (`DATABASE_URL`, `OPENSEARCH_*`, `AZURE_OPENAI_*`)
sudah dicantumkan di `core/config.py` sejak awal supaya berkas itu tidak dirombak
ulang nanti. **Tidak satu pun dipakai di Fase 1**, dan rinciannya bukan urusan
dokumen ini.

Dua catatan yang perlu diingat saat Fase 2 dimulai:

- Penamaan di `core/config.py` (`AZURE_TASK_DEPLOYMENT`) **tidak sama** dengan
  penamaan di env Law Analyzer (`AZURE_OPENAI_TASK_DEPLOYMENT_NAME`). Perlu
  diselaraskan, belum masalah sekarang.
- `MINIO_*` tidak diperlukan. Tautan PDF sudah ikut terkirim dari OpenSearch
  sebagai field `pdf_url`.

---

## 13. Urutan implementasi

Diperbarui 17 Sep 2026. Yang bertanda **selesai** sudah dikerjakan dan lolos
tesnya; yang bertanda **belum diuji di Word** sudah ditulis dan lolos typecheck
tetapi belum sekali pun dijalankan di dalam Word.

1. ~~Tetapkan skema Temuan.~~ **Selesai** — hidup di bagian 11 saja.
   `docs/kontrak-data.md` dihapus 18 Sep 2026 karena menduplikasinya.
2. ~~Satu alur utuh dengan satu aturan paling sederhana.~~ **Selesai.**
3. ~~Tiga aturan struktur sisanya.~~ **Selesai** — kelimanya jalan, diverifikasi
   lewat `backend/tools/cek_docx.py` terhadap dokumen contoh dan satu RPMK nyata.
4. ~~`cek_ejaan()`.~~ **Selesai** — cakupannya masih sempit dan sengaja begitu:
   "Undang-Undang" dua huruf U kapital (KMK 527 butir 33) dan kata "tentang"
   huruf kecil di judul dasar hukum (butir 32). Jangan memasang kamus besar
   sebelum cakupannya dipastikan ke penelaah.
5. ~~Buktikan Track Changes jalan.~~ **Selesai 17 Sep 2026** — hasilnya di
   bagian 6.2. Lolos tanpa `NotImplemented`, tetapi jalur ini **tidak jadi
   dipakai**; alasannya di bagian 6.1. Langkahnya tidak dihapus karena hasil
   pengujiannya masih mengikat.
6. ~~Ubah kontrak data.~~ **Selesai** — `tingkat_keparahan` dihapus, `nomor` dan
   `jenis_tanda` ditambahkan, `jenis_dokumen` jadi wajib di `AnalisisRequest`,
   `_tentukan_jenis_dokumen()` dihapus, teks `catatan` ditulis ulang jadi bentuk
   alasan.
7. ~~Pasang pengaman analisis berulang~~ (bagian 6.8). **Selesai** — panel
   menolak analisis ulang selama masih ada temuan yang belum diputuskan, dengan
   jalan keluar Bersihkan Daftar.
8. ~~Ringkas task pane~~ (bagian 6.9). **Selesai** — penjelasan panjang dibuang,
   tersisa pemilih jenis dokumen, nomor temuan, cuplikan, Lompat ke Teks, dan
   Terima/Tolak untuk semua temuan.
9. ~~Penandaan setingkat kata~~ (bagian 6.5). **Selesai di backend, belum diuji
   di Word.** F1-001/002/004 mengirim offset presisi; `office.ts` mencarinya
   lewat `Word.search()` + hitungan kemunculan keberapa.
10. ~~Matikan F1-001 dan perbaiki bug klausul Menetapkan~~ (bagian 6.10).
    **Selesai** — dua tes regresi menjaga keduanya.
11. ~~Ganti lapisan penandaan ke merah/hijau/kuning gambar sendiri~~
    (bagian 6.3–6.4). **Belum diuji di Word.** Yang wajib dibuktikan di Word
    sungguhan, pada **salinan** naskah:
    - content control ber-`appearance: "Hidden"` benar-benar tidak terlihat;
    - `insertText(..., "After")` mendarat di sebelah teks aslinya, bukan di
      dalam bungkusnya;
    - `delete(false)` membuang usulan hijau berikut isinya, `delete(true)`
      melepas bungkus tanpa menghapus naskah;
    - Tolak memulihkan naskah tanpa bekas;
    - tidak ada lagi baris `Formatted: Highlight` di margin.
12. **Ekspor versi bersih** (bagian 6.7) — jalurnya belum ditetapkan, perlu
    keputusan penelaah lebih dulu.
13. ~~Tambah aturan.~~ **Tujuh selesai 18 Sep 2026** (F1-006 s.d. F1-012).
    Tiga sisanya di tabel bawah belum. Dengan F1-001 mati, dulu tersisa empat aturan dan pada RKMK
    yang rapi hasilnya bisa nol temuan. Itu benar, tapi belum cukup untuk
    peragaan.

    Sejak 18 Sep 2026 sumbernya tidak perlu lagi tebakan. Penelaah mengirim
    pindaian Lampiran II halaman 30, 35, 36, dan 37, dan di situ ada
    butir-butir yang **imperatif, deterministik, dan sudah terverifikasi
    visual** tetapi belum dibangun:

    | Butir | Bunyi ringkasnya | Sifat | Kesulitan |
    |---|---|---|---|
    | 8 | Judul tidak diakhiri tanda baca | imperatif | mudah |
    | 16 | "Menimbang" diakhiri titik dua (:) | imperatif | mudah |
    | 21 | Tiap butir Menimbang diawali "bahwa", diakhiri titik koma (;) | imperatif | mudah |
    | 23 | "Mengingat" diakhiri titik dua (:) | imperatif | mudah |
    | 31 | Tiap dasar hukum diawali angka Arab 1, 2, 3 dan diakhiri titik koma (;) | imperatif | mudah |
    | 32 | Kata penghubung/konjungsi di judul dasar hukum tetap huruf kecil | imperatif | sedang — perlu daftar konjungsi |
    | 34 | UU/PP/Perpres di dasar hukum wajib disertai (Lembaran Negara ..., Tambahan Lembaran Negara ...) | imperatif | sedang |
    | 38 | "Menetapkan" huruf awal kapital, diakhiri titik dua (:) | imperatif | mudah |
    | 39 | Judul pada Menetapkan diakhiri titik (.) | imperatif | mudah |
    | 30 | Urutan dasar hukum mengikuti hierarki, lalu kronologis | imperatif | sulit — perlu tahu hierarki tiap jenis |

    Perhatikan bedanya dengan daftar di brief bagian 8.11: yang di sana disusun
    dari logika dokumen dan **belum dikonfirmasi siapa pun**; yang di sini
    dikutip dari naskah KMK 527 yang sudah dibaca halamannya. Kerjakan yang
    ini dulu.

    Sembilan dari sepuluh bersifat imperatif — berbeda dari F1-004 yang
    bersandar pada butir 22 yang cuma menyebut "pada umumnya". Artinya
    temuannya lebih kuat, dan lebih pantas jadi `penggantian` ketimbang
    `catatan`.

    Konfirmasi ke penelaah tetap berguna, tapi bukan lagi penghalang: yang
    ditanyakan sekarang "mana yang paling sering salah", bukan "apakah ini
    memang aturan".
14. ~~Lengkapi tabel rujukan KMK 527.~~ **Selesai 18 Sep 2026.** Kedua belas
    entri terisi dan berstatus `"visual"` — dicocokkan kata per kata terhadap
    pindaian halaman 30, 33, 34, 35, 36, dan 37 yang dikirim penelaah. Gate
    legal di panel padam untuk semuanya. Riwayat verifikasinya di
    `rules/rujukan_kmk527.py`, dan tes
    `test_semua_aturan_punya_rujukan_terverifikasi` menjaganya tetap begitu.
15. ~~Tutup enam salah tandai dan satu lubang cakupan yang ditemukan pada
    pembacaan ulang seluruh kode dan penyusunan naskah uji~~ (bagian 6.10
    Kasus 6–12). **Selesai 18 Sep 2026**, dengan sepuluh tes regresi di kelas
    `TestRegresi18September`. Ikut dibereskan di sisi Word: Bersihkan Daftar
    tidak lagi menimpa warna penyusun dan ikut menghapus komentar alat,
    cakupan "Bagian Terpilih" punya jalur cadangan runtime, dan rentang yang
    berimpit tidak lagi digambar dua kali.
16. **Jalankan daftar periksa bagian 16** sebelum menyatakan Fase 1 selesai.
    Itu satu-satunya cara tahu bahwa yang sudah lolos tes juga benar di Word.

---

## 14. Peraturan untuk agen coding

1. **Dilarang membaca isi berkas `.env`.** Kalau perlu tahu variabel apa saja
   yang tersedia, baca `core/config.py`.
2. **Pastikan `.env` tercantum di `.gitignore`** sebelum menulis berkas apa pun.
3. **Kredensial hanya hidup di backend**, tidak pernah sampai ke browser.
4. **Jangan pakai LLM untuk hal yang bisa diselesaikan regex atau logika biasa.**
   Ini prinsip proyek, bukan saran.
5. **Alat mengusulkan, penelaah yang memutuskan.** Usulan disisipkan sebagai
   teks hijau **di sebelah** teks aslinya, dibungkus content control bertag,
   dan teks lama **tidak dihapus** — cuma diberi warna merah dan coretan.
   Dilarang: menghapus teks penelaah atas inisiatif kode, membuat tombol
   "terapkan semua", dan menyentuh rentang di luar `lokasi` temuan. Pelanggaran
   aturan ini pernah terjadi sekali (fungsi `applyUsulanRumusan` yang menimpa
   satu paragraf penuh ketika pencarian meleset) dan berakhir dihapus — jangan
   diulang. Karena itu juga: temuan yang rentang presisinya tidak ketemu
   **tidak ditandai sama sekali**, bukan diperlebar ke satu paragraf.
6. **Setiap temuan wajib membawa rujukan yang bisa diperiksa** — diambil dari
   tabel tetap, **tidak boleh dikarang**.
7. **Jangan menulis apa pun ke basis data produksi JDIH/Law Analyzer.**
8. **Jangan menurunkan aturan dari hasil ekstraksi teks PDF KMK 527 atau PMK
   164** — salinannya OCR rusak. Aturan harus diverifikasi manual dari naskah
   yang dibaca visual.
9. **Office.js jarang muncul di data latih model** — model cenderung mengarang
   method yang tidak ada. Verifikasi tiap method ke
   `frontend/node_modules/@types/office-js/index.d.ts` sebelum menulis kode.
   Cara cek: `grep -n "namaMethod" -B 8 index.d.ts`.
10. **Requirement set didukung ≠ fitur diizinkan.** `isSetSupported` bisa
    melaporkan `true` sementara pemanggilannya melempar `NotImplemented` karena
    terkunci lisensi — sudah terbukti pada Critique. Tiap fitur Office.js yang
    baru dipakai wajib punya jalur cadangan bila pemanggilannya gagal saat
    runtime, bukan cuma pengecekan requirement set.
11. **Sebelum menambah dependency, periksa apakah kebutuhannya bisa dipenuhi
    yang sudah terpasang.** Tailwind sudah ada — jangan tambah Bootstrap.
12. **Route handler FastAPI setipis mungkin**: parse input → panggil fungsi →
    kembalikan JSON. Logika pemeriksaan harus fungsi murni yang bisa dites tanpa
    menjalankan server.
13. **Jangan simpan state global di backend.** Tiap permintaan berdiri sendiri.
14. **Jangan over-engineer untuk skala besar di build pertama.**
15. **Ikuti urutan di bagian 13.**
16. **Apa pun yang ditandai wajib benar-benar salah** (bagian 6.10). Aturan yang
    tidak bisa membuktikan kesalahannya harus dimatikan, bukan diperhalus. Tiap
    aturan yang bisa kebablasan wajib punya batas kewajaran, dan di luar batas
    itu memilih diam. Satu salah tandai merusak kepercayaan lebih cepat daripada
    sepuluh temuan benar membangunnya.
17. **Seluruh penandaan berjalan dengan `changeTrackingMode = "Off"`**, lalu mode
    semula dikembalikan. Menandai selagi pelacakan menyala membuat tiap warna
    tercatat sebagai revisi `Formatted: Highlight` dan mengubur komentar yang
    justru perlu dibaca.

---

## 15. Definisi selesai

Build ini berhasil kalau:

**Sudah tercapai:**

- [x] Kontrak data hidup di satu tempat saja (bagian 11)
- [x] Task pane terbuka di Word dan membaca paragraf dokumen aktif
- [x] Tombol "Analisis" memanggil backend; backend menjalankan seluruh
      pemeriksaan di bagian 3
- [x] Tiap fungsi di `rules/` punya tes yang jalan tanpa server
- [x] Jenis dokumen wajib dipilih; menekan Analisis tanpa memilih tidak jalan
- [x] Yang ditandai rentang kata yang salah, bukan paragraf penuh (di backend)
- [x] Tidak ada aturan yang menandai naskah yang sudah benar — dua belas salah
      tandai yang sudah ditemukan semuanya ditutup dan dijaga tes regresi
      (bagian 6.10 Kasus 1–12). **Yang belum ditemukan tentu tidak terhitung** —
      karena itu 16.2 wajib dijalankan pada naskah sungguhan, bukan cuma pada
      naskah uji
- [x] Menjalankan analisis dua kali tidak menumpuk komentar, dan Bersihkan
      Daftar benar-benar mengosongkan naskah dari tanda **dan** komentar alat
- [x] Task pane tidak mengulang penjelasan yang sudah ada di komentar
- [x] Tiap fitur Office.js di luar WordApi 1.1 punya jalur cadangan runtime,
      bukan cuma pengecekan requirement set (cakupan terpilih, komentar,
      `changeTrackingMode`)

**Belum, dan wajib dibuktikan di Word sungguhan pada salinan naskah:**

- [ ] Temuan `penggantian` muncul merah tercoret dengan usulan hijau di
      sebelahnya
- [ ] Temuan `catatan` muncul sebagai blok kuning tanpa mengubah warna hurufnya
- [ ] Tepat satu komentar per temuan, berisi alasan + rujukan butir, dua baris
- [ ] Tidak ada satu pun baris `Formatted: Highlight` di margin
- [ ] Tolak memulihkan naskah persis seperti sebelum ditandai
- [ ] Bersihkan Daftar mencabut seluruh tanda `DA-*` tanpa menyentuh warna milik
      penyusun sendiri
- [ ] Yang tersorot di Word benar-benar kata yang salah, bukan paragrafnya

**Belum dibangun:**

- [ ] Ekspor versi bersih yang layak dikirim ke unit pemrakarsa (bagian 6.7)
- [ ] Kutipan utuh butir sebagai balasan komentar (bagian 6.8)
- [ ] Diuji pada dokumen panjang, bukan cuma dokumen contoh
- [x] Tabel rujukan KMK 527 tidak lagi placeholder — selesai 18 Sep 2026,
      kedua belas entri berstatus `"visual"`
- [ ] Aturan yang cukup banyak untuk berguna pada RKMK yang rapi — lihat
      bagian 13 langkah 13

---

## 16. Cara tahu Fase 1 aman dan selesai

Bagian ini ditulis 18 Sep 2026 untuk menjawab satu pertanyaan langsung: apa
yang harus dijalankan supaya yakin alat ini tidak merusak naskah orang, dan apa
yang masih kurang sebelum Fase 2 boleh dimulai.

Urutannya sengaja dari yang paling murah ke yang paling mahal. **Jangan lompat
ke bawah sebelum yang di atas hijau** — kalau tes saja merah, menguji di Word
cuma membuang naskah uji.

### 16.1 Empat perintah yang wajib hijau sebelum apa pun

```bash
cd backend && python -m pytest tests/ -q          # harus: 88 passed
cd frontend && npx tsc --noEmit                    # harus: tanpa keluaran
cd frontend && npx eslint src --max-warnings=0     # harus: tanpa keluaran
cd frontend && npm run build                       # harus: Compiled successfully
```

Kalau keempatnya hijau, yang terbukti baru satu hal: kode yang ada sudah sesuai
dengan yang dijanjikannya sendiri. **Itu belum berarti aturannya benar.**

### 16.2 Uji aturan terhadap naskah, tanpa membuka Word

**Mulai dari naskah uji yang kesalahannya sudah diketahui.** Dua berkas di
`tools/contoh/`, beserta kunci jawabannya:

```bash
cd backend && python tools/cek_docx.py tools/contoh/uji-pmk-lengkap.docx --jenis PMK
cd backend && python tools/cek_docx.py tools/contoh/uji-kmk-lengkap.docx --jenis KMK
```

Cocokkan hasilnya dengan `tools/contoh/KUNCI-UJI.md`. Kunci itu memuat dua
tabel yang harus dibandingkan: **apa yang sengaja dirusak** dan **apa yang
benar-benar keluar hari ini**. Selisihnya yang berarti:

- ada di keduanya → aturannya bekerja;
- ada di rencana, tidak ada di hasil → aturannya diam, belum tentu cacat;
- **ada di hasil, tidak ada di rencana → salah tandai.** Ini yang wajib
  dilaporkan.

Kedua berkas itu juga memuat **jebakan yang sengaja dipasang** — bagian yang
kelihatan salah tetapi sebenarnya benar, dan tidak boleh ditandai: isi diktum
KMK yang diawali kata "Menetapkan", nama resmi peraturan lain yang memuat
"Republik Indonesia", "undang-undang" generik di batang tubuh, label yang
berdiri sendiri di sel tabel, dan `M E M U T U S K A N :` berspasi huruf.

Keduanya dibangkitkan `tools/buat_contoh_uji.py`, dan **kuncinya ikut
dibangkitkan dari sumber yang sama** — supaya tidak pernah bisa berbeda dari
naskahnya. Kalau aturannya berubah, jalankan ulang skripnya.

Cara ini bukan basa-basi: **Kasus 11 dan 12 di bagian 6.10 ditemukan justru
saat naskah uji itu disusun**, bukan dari membaca kode dan bukan dari 86 tes
yang sudah ada.

**Lalu lanjutkan ke naskah sungguhan.**

```bash
cd backend && python tools/cek_docx.py <berkas.docx> --jenis PMK
```

Jalankan pada **5–10 RPMK/RKMK sungguhan** yang sudah pernah ditelaah, bukan
pada dokumen contoh. Untuk tiap temuan yang keluar, jawab satu pertanyaan:

> Kalau penelaah melihat tanda ini di naskahnya, apakah dia akan setuju bahwa
> di situ memang ada yang salah?

- **Ya** → aturannya bekerja.
- **Tidak** → itu salah tandai. Matikan aturannya lewat panel Pengaturan,
  catat naskah dan kalimatnya, lalu perbaiki dengan satu tes regresi seperti
  Kasus 1–10 di bagian 6.10. **Jangan diperhalus kalimatnya** — aturan yang
  tidak bisa membuktikan kesalahannya harus dimatikan.

Yang juga harus diperiksa: temuan yang **seharusnya keluar tetapi tidak**.
Bandingkan hasilnya dengan coretan telaah manusia pada naskah yang sama.
Diam yang salah tidak merusak kepercayaan, tapi membuat alat ini tidak berguna.

Pada dokumen contoh, hasil yang benar saat ini: **5 temuan — 2 `penggantian`,
3 `catatan`.** Angka yang berbeda berarti ada yang berubah tanpa dokumen ini
ikut diperbarui.

### 16.3 Uji di Word, pada SALINAN naskah

Wajib pada salinan. Ini satu-satunya bagian yang benar-benar menulis ke
dokumen, dan sampai daftar ini hijau semuanya, Fase 1 belum boleh disebut
selesai. Tiap baris bisa dijawab ya/tidak dengan mata sendiri:

| Yang diperiksa | Cara melihatnya |
|---|---|
| Temuan `penggantian` merah tercoret, usulannya hijau di sebelahnya | Lihat naskah |
| Temuan `catatan` blok kuning, **warna hurufnya tidak berubah** | Bandingkan dengan sebelum analisis |
| Tepat satu komentar per temuan, dua baris | Buka panel komentar Word, hitung |
| Nomor `(T1)`, `(T2)` di komentar cocok dengan nomor kartu di panel | Cocokkan satu per satu |
| **Nol** baris `Formatted: Highlight` di margin | Tab Review, All Markup |
| Tab Review menunjukkan **0 revisions** | Tab Review |
| Content control tidak terlihat sebagai kotak | Lihat naskah |
| Lompat ke Teks mendarat di kata yang benar, termasuk pada kata berulang | Klik tiap kartu |
| Tolak memulihkan naskah **tanpa bekas** — warna, coretan, sorotan, komentar | Tolak satu temuan, bandingkan |
| Bersihkan Daftar mencabut semua tanda **dan** komentar alat | Jalankan, lalu periksa naskah dan panel komentar |
| Bersihkan Daftar **tidak** menyentuh warna milik penyusun | Warnai satu kata biru sebelum analisis, pastikan tetap biru sesudahnya |
| Analisis ulang ditolak selama ada temuan yang belum diputuskan | Tekan Analisis dua kali |
| Mode "Bagian Terpilih" jalan, atau tombolnya mati kalau WordApi 1.3 tidak ada | Tombol Word Connected → lihat baris v1.3 |

Uji juga **pada dokumen panjang**, bukan cuma yang pendek. PMK 124/2024 punya
175 satuan pasal/ayat; yang perlu dilihat di situ bukan cuma hasilnya, tapi
juga apakah panel masih merespons.

### 16.4 Yang membuat Fase 1 belum selesai

Tiga hal, dan hanya satu yang berupa pekerjaan kode:

1. **Daftar 16.3 belum pernah dijalankan.** Ini penghalang terbesar. Seluruh
   lapisan penandaan merah/hijau/kuning sudah ditulis dan lolos typecheck,
   tetapi **belum sekali pun berjalan di dalam Word**.
2. **Ekspor versi bersih belum dibangun**, dan jalurnya belum ditetapkan.
   Ini menunggu **keputusan penelaah**, bukan menunggu kode — dua pilihannya
   di bagian 6.7.
3. **Kutipan utuh butir sebagai balasan komentar** (6.8) dan **tiga aturan
   yang sudah terverifikasi visual tetapi belum dibangun** (butir 30 hierarki,
   butir 32 konjungsi, butir 34 Lembaran Negara). Keduanya menambah kegunaan,
   bukan menutup cacat.

### 16.5 Syarat sebelum Fase 2 boleh dimulai

Fase 2 menumpang lapisan penandaan yang sama, dan bagian 4 sudah menetapkan
Fase 1 harus lebih dulu membuktikan skema itu enak dibaca penelaah. Temuan
Fase 2 datang dari penalaran, jadi lebih mudah salah daripada temuan Fase 1 —
menaruhnya di atas pondasi yang belum terbukti memperbesar kerusakan, bukan
menundanya.

Syaratnya dua:

- **Daftar 16.3 hijau seluruhnya** pada salinan naskah sungguhan.
- **16.2 dijalankan pada minimal lima RPMK/RKMK nyata tanpa satu pun salah
  tandai yang tersisa.** Satu salah tandai merusak kepercayaan lebih cepat
  daripada sepuluh temuan benar membangunnya.

Ekspor versi bersih **tidak** jadi syarat Fase 2 — itu pekerjaan yang berdiri
sendiri dan menunggu keputusan penelaah.
