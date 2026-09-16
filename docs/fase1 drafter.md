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
> **Revisi 16 Sep 2026:** bagian 3, 4, 6, 7, 8, 11, 13, 14, dan 15 diubah
> menyusul keterangan mentor tentang cara penelaah bekerja sebenarnya. Ringkasan
> perubahannya ada di bagian 6.

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
| Cek judul ditulis kapital seluruhnya | Aturan baku KMK 527 Lampiran II | Pemeriksaan huruf, deterministik |
| Cek kelengkapan Menimbang / Mengingat / Menetapkan | Struktur wajib yang kadang terlewat | Cari pola baku tiap bagian |
| Cek frasa baku butir Menimbang terakhir ("perlu menetapkan … tentang …") | Sering hilang atau salah bentuk (brief bagian 8.6) | Pencocokan pola pada butir terakhir |
| Cek ejaan | Salah tulis lolos saat buru-buru | Kamus/regex bahasa Indonesia, bukan AI — cakupannya lihat bagian 13 langkah 4 |
| **Usulan rumusan dipasang sebagai perubahan terlacak** | Penelaah tidak perlu mengetik ulang, tapi tetap memutuskan | Track Changes bawaan Word — lihat bagian 6 |
| **Temuan tanpa pengganti ditandai komentar + warna keparahan** | Sebagian kesalahan tidak punya "jawaban benar" tunggal | `insertComment` + `font.highlightColor` — bagian 6 |
| Tiap temuan menyertakan rujukan butir KMK 527 + kutipannya | Penelaah perlu tahu dasar hukumnya, bukan cuma "ini salah" | Tabel rujukan tetap di kode — bagian 10 |
| Setujui / tolak tiap usulan | Prinsip: alat memberi rekomendasi, tidak pernah memutuskan | Tombol Accept/Reject bawaan Word di ribbon Review |
| Versi bersih tanpa coretan | Penelaah sekarang memelihara dua berkas manual | Accept All + Save As — satu berkas, dua wujud |
| Pilih cakupan: seluruh dokumen atau bagian terpilih | Fleksibilitas penelaah | `document.getSelection()` vs seluruh body |

---

## 4. Di luar cakupan build ini

Jangan dikerjakan agen coding. Diambil dari brief bagian "Di Luar Lingkup" dan
pembagian fase:

- **Menerapkan usulan tanpa persetujuan penelaah.** Usulan boleh dipasang
  sebagai *perubahan terlacak* (tracked change) yang masih mentah dan bisa
  dibatalkan satu klik — tapi tidak boleh ada kode yang memanggil `accept()`
  sendiri, tidak boleh "terapkan semua", dan tidak boleh menimpa teks saat
  pelacakan perubahan sedang mati. Lihat bagian 6 dan bagian 14 butir 5.
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
                              Task pane memasang perubahan terlacak / komentar
```

| Lapisan | Teknologi | Catatan |
|---|---|---|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind v4 | Sudah terpasang di kerangka — jangan diganti, jangan tambah Bootstrap |
| Integrasi Word | Office.js | Lihat `docs/panduan-officejs.md` di repo — API-nya sudah diverifikasi di sana |
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

### 6.1 Kenapa rancangan lama diganti

Rancangan sebelumnya membagi tampilan jadi tiga lapis: sorotan + popup
(`Critique` + `popupOptions`), komentar permanen, dan task pane. Dua hal
membatalkannya, keduanya berdasar bukti, bukan dugaan:

**Critique mati di Word penelaah.** Diuji langsung di Word 2024 LTSC
(16 Sep 2026): `isSetSupported("WordApi", "1.7")` melaporkan `true`, tapi
`insertAnnotations` melempar `RichApi.Error: NotImplemented`. Sebabnya
Annotation mensyaratkan langganan Microsoft 365 aktif — lisensi beli-putus
(LTSC) tidak punya itu, berapa pun tinggi requirement set yang dilaporkan
didukung. Ikut mati bersamanya: popup berisi tombol terima/tolak, dan pewarnaan
per tingkat keparahan lewat `Critique.colorScheme`.

**Cara penelaah bekerja ternyata berbeda dari asumsi awal.** Keterangan mentor
beserta contoh RPMK/RKMK sungguhan (lihat `project-brief.md` bagian 8.13):
penelaah menghasilkan **dua dokumen** — versi bercoretan (teks salah dicoret,
usulan ditulis dengan warna berbeda) dan versi bersih yang sudah dimodifikasi.
Keputusan akhirnya diambil di rapat bersama unit pemrakarsa. Artinya penelaah
memang rutin menyunting salinan rancangan; yang tidak boleh adalah **memutuskan
sepihak**, bukan **menyentuh berkas**.

Konsekuensinya: aturan lama "alat tidak boleh mengubah satu karakter pun" itu
terlalu lebar. Yang dijaga bukan keutuhan karakter, melainkan bahwa **tidak ada
perubahan yang jadi permanen tanpa satu klik persetujuan penelaah.**

### 6.2 Dua kelas temuan

Tiap temuan ditandai menurut apakah ia punya rumusan pengganti yang pasti.
Pembagian ini bukan buatan — ia jatuh sendiri dari aturan yang sudah ada:

| Kelas (`jenis_tanda`) | Dipakai bila | Cara ditandai | Cara diputuskan |
|---|---|---|---|
| `penggantian` | Ada satu rumusan pengganti yang deterministik untuk rentang teks yang ditandai | Perubahan terlacak (Track Changes): teks lama tampil tercoret, usulan tampil di sebelahnya | Accept / Reject bawaan Word (ribbon **Review**) |
| `catatan` | Tidak ada pengganti tunggal — entah yang salah justru ketiadaan sesuatu, atau alat tidak tahu mana dari dua kemungkinan yang benar | `insertComment` + `font.highlightColor` sesuai tingkat keparahan | Tombol Terima/Tolak di task pane |

Pemetaan aturan Fase 1 — diverifikasi terhadap `rules/format_baku.py` yang
sekarang, bukan diperkirakan:

| Aturan | Kelas | Alasan |
|---|---|---|
| F1-001 judul kapital | `penggantian` | Penggantinya `teks.upper()`, mekanis dan pasti |
| F1-002 judul pembuka ≠ judul Menetapkan | `catatan` | Alat tidak tahu mana dari dua judul itu yang benar |
| F1-003 kelengkapan struktur | `catatan` | Yang salah adalah ketiadaan bagian; tidak ada teks untuk diganti |
| F1-004 frasa baku butir Menimbang terakhir | `catatan` | Bunyi bakunya perlu menyebut huruf mana saja yang dirujuk; untuk sekarang cukup jadi catatan. Naik ke `penggantian` hanya setelah aturannya terbukti menyusun butir penuh dengan benar |
| F1-005 ejaan | `penggantian` | Substitusi kata, mis. `Undang-undang` → `Undang-Undang`, `Tentang` → `tentang` |

Pada `backend/tools/contoh/contoh-rancangan-uji.docx` pembagian ini menghasilkan
3 temuan `penggantian` dan 2 temuan `catatan`.

### 6.3 Aturan penanganan Track Changes

1. **Baca mode pelacakan lebih dahulu**, simpan nilainya, baru set
   `context.document.changeTrackingMode = "TrackAll"`. Sesudah seluruh usulan
   terpasang, **kembalikan ke nilai semula**. Menyalakan pelacakan diam-diam dan
   membiarkannya menyala mengubah perilaku Word untuk semua ketikan penelaah
   sesudahnya — itu kejutan yang tidak boleh dibuat alat.
2. **Jangan pernah memanggil `accept()` atau `reject()` atas inisiatif kode.**
   Keduanya hanya boleh jalan sebagai akibat langsung penelaah menekan tombol.
3. **Jangan menyisipkan penggantian kalau mode pelacakan gagal dinyalakan.**
   Tanpa pelacakan, penggantian = menimpa naskah diam-diam. Kalau
   `changeTrackingMode` tidak bisa diset, temuan `penggantian` **turun jadi
   `catatan`** — komentar dan sorotan warna, tanpa menyentuh teks.
4. **Temuan `penggantian` tidak diberi sorotan warna.** Coretan revisinya sudah
   jadi penanda visual; menambah warna di atasnya cuma bikin ramai.
5. **Komentar tetap dipasang untuk kedua kelas** — komentar memuat *kenapa* +
   rujukan butir KMK 527, perubahan terlacak memuat *apa* usulannya.

### 6.4 Pembagian tugas antarmuka

| Tempat | Isinya |
|---|---|
| Perubahan terlacak di naskah | Usulan rumusannya — apa yang diusulkan berubah |
| Komentar Word | Alasan + rujukan butir KMK 527 + tautan PDF JDIH |
| Ribbon **Review** bawaan Word | Accept / Reject / Next / Previous untuk temuan `penggantian` |
| Task pane | Daftar ringkas: nomor temuan, tingkat keparahan, tombol Lompat ke Teks; tombol Terima/Tolak **hanya** untuk temuan `catatan` |

Penjelasan panjang **tidak diulang** di task pane. Alasan temuan cukup ditulis
sekali, di komentar. Duplikasi catatan yang sama di komentar dan di panel adalah
keluhan utama terhadap versi sebelumnya — penelaah jadi membaca hal yang sama
dua kali sambil menggeser dua jendela.

Accept/Reject untuk temuan `penggantian` sengaja diserahkan ke ribbon Word,
bukan dibuatkan tombol di panel. Alasannya bukan malas: mencocokkan kembali
objek `TrackedChange` mana milik temuan mana butuh penanda identitas yang harus
bertahan lintas sesi, sementara Word sudah melakukannya dengan benar sejak
awal, lengkap dengan navigasi antar-perubahan. Kalau setelah dicoba penelaah
ternyata tetap ingin tombolnya ada di panel, itu penambahan belakangan, bukan
prasyarat.

### 6.5 Batas yang sudah diketahui

- **`TrackedChange.author` bersifat `readonly`** — sudah dicek di `index.d.ts`.
  Usulan alat akan tercatat atas nama pengguna Word yang sedang membuka
  dokumen, **bukan** "Drafter Analiser", dan warnanya tidak bisa dibedakan dari
  suntingan penelaah sendiri. Jejak asal-usul tetap ada lewat komentar
  pendampingnya yang berpenanda `[Drafter Analiser — …]`.
- **Warna tidak bisa diatur per makna.** Word mewarnai revisi per penulis.
  Kebiasaan penelaah memakai merah untuk salah dan hijau untuk usulan tidak
  berlaku pada perubahan terlacak. Warna per tingkat keparahan tetap ada, tapi
  hanya pada temuan `catatan`.
- **"Accept All" menerima semua, termasuk revisi penelaah sendiri** yang
  kebetulan ada di dokumen yang sama. Ini perlu disampaikan di panel, dan
  penelaah sebaiknya menjalankan alat pada salinan kerja.
- **Belum diuji runtime.** `changeTrackingMode` (WordApi 1.4) dan
  `TrackedChange` beserta `accept()`/`reject()` (WordApi 1.6) sudah diverifikasi
  ada di `index.d.ts`, dan Word penelaah mendukung sampai 1.9. Tapi pelajaran
  dari Critique berlaku: **requirement set didukung ≠ fitur diizinkan.** Track
  Changes adalah fitur inti Word yang tidak terkunci langganan, jadi peluangnya
  jauh lebih besar — tetapi wajib dibuktikan lewat satu percobaan kecil sebelum
  sisa pekerjaan dibangun di atasnya. Lihat bagian 13 langkah 5.

---

## 7. Susunan file

```
drafter-analiser/
├── backend/
│   ├── app/
│   │   ├── main.py              ← FastAPI + CORS + /health
│   │   ├── core/config.py       ← Settings
│   │   ├── api/analisis.py      ← endpoint POST /analisis/jalankan
│   │   ├── rules/               ← aturan Fase 1 + tabel rujukan
│   │   ├── models/temuan.py     ← skema Temuan (bagian 11)
│   │   ├── services/            ← KOSONG (belum dipakai di Fase 1)
│   │   ├── parser/              ← KOSONG (belum dipakai di Fase 1)
│   │   ├── llm/                 ← KOSONG (tidak dipakai di Fase 1)
│   │   └── retrieval/           ← KOSONG (tidak dipakai di Fase 1)
│   ├── requirements.txt
│   ├── tests/
│   └── tools/
│       ├── cek_docx.py          ← alat diagnosa, BUKAN bagian produk
│       └── contoh/
│           └── contoh-rancangan-uji.docx
├── docs/
│   ├── kontrak-data.md
│   ├── panduan-officejs.md
│   └── fase1 drafter.md         ← dokumen ini
└── frontend/
    └── src/
        ├── app/
        │   ├── layout.tsx
        │   └── taskpane/page.tsx
        └── lib/
            ├── office.ts        ← SEMUA panggilan Office.js
            └── types.ts
```

**Tidak ada folder baru** yang perlu dibuat untuk perubahan ini. Yang bertambah
hanya isi `office.ts` dan satu field di `models/temuan.py`.

---

## 8. Penjelasan backend ↔ frontend

```
backend/app/rules/format_baku.py
  ===> satu fungsi murni per pemeriksaan di bagian 3:
       cek_judul_konsisten(), cek_judul_kapital(),
       cek_kelengkapan_struktur(), cek_frasa_baku_menimbang(), cek_ejaan()

       BARU: tiap fungsi wajib menetapkan jenis_tanda secara EKSPLISIT,
       bukan disimpulkan dari ada-tidaknya usulan_rumusan. Alasannya:
       suatu saat sebuah aturan bisa punya usulan_rumusan yang sifatnya
       contoh bunyi, bukan pengganti harfiah — dan menebaknya dari
       null-tidaknya field lain akan salah menandai naskah orang

       Catatan cek_frasa_baku_menimbang(): berlaku HANYA kalau Menimbang
       punya lebih dari satu butir (ada huruf a/b/c). Kalau cuma satu butir
       tanpa huruf, lewati — itu bentuk yang sah menurut KMK 527 butir 19

backend/app/models/temuan.py
  ===> BARU: field jenis_tanda (enum "penggantian" | "catatan"), bagian 11

frontend/src/lib/office.ts
  ===> kumpulkan SEMUA panggilan Office.js di satu berkas.
       BARU, untuk perubahan terlacak:
         siapkanPelacakanPerubahan()  -> baca mode lama, set "TrackAll",
                                         kembalikan mode lama sebagai nilai
         kembalikanModePelacakan(m)   -> pulihkan mode semula
         usulkanPenggantian(temuan)   -> cari rentang, insertText("Replace")
                                         DALAM keadaan pelacakan menyala
       Fungsi lama yang tetap dipakai: readParagraphs, selectFindingLocation,
       tandaiSemuaTemuan (kini bercabang menurut jenis_tanda),
       hapusSorotan, hapusKomentarTemuan

       Fungsi warisan yang TIDAK dipanggil alur aktif dan boleh dihapus
       kalau sudah pasti tidak dipakai: sorotSementara, tandaiTemuan,
       insertCritiqueAnnotation, insertPermanentComment, critiqueTersedia

frontend/src/app/taskpane/page.tsx
  ===> panel diringkas: nomor temuan, tingkat keparahan, Lompat ke Teks.
       Terima/Tolak hanya untuk temuan berjenis "catatan".
       Penjelasan panjang TIDAK ditampilkan lagi di panel — sudah di komentar
```

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

Di Fase 2/3, saat analisis berjalan menit sampai jam. Brief bagian 8.9
mensyaratkan: *"hasil disimpan per satuan sehingga yang sudah selesai tetap
dapat diakses meskipun proses terputus."* Itu baru butuh penyimpanan.

Skema minimal untuk saat itu tiba — dirancang sekarang supaya tidak perlu
dibongkar ulang:

```sql
-- satu baris per kali analisis dijalankan
CREATE TABLE analisis (
    id              UUID PRIMARY KEY,
    nama_dokumen    TEXT NOT NULL,
    sidik_dokumen   TEXT NOT NULL,     -- hash isi, untuk deteksi dokumen berubah
    cakupan         TEXT NOT NULL,     -- 'seluruh' | 'terpilih'
    fase            SMALLINT NOT NULL,
    status          TEXT NOT NULL,     -- 'berjalan' | 'selesai' | 'terputus'
    dibuat_pada     TIMESTAMPTZ NOT NULL DEFAULT now(),
    selesai_pada    TIMESTAMPTZ
);

-- satuan pemeriksaan = ayat/butir, BUKAN pasal (brief bagian 8.9)
CREATE TABLE satuan_periksa (
    id              UUID PRIMARY KEY,
    analisis_id     UUID NOT NULL REFERENCES analisis(id) ON DELETE CASCADE,
    urutan          INTEGER NOT NULL,
    label           TEXT NOT NULL,     -- mis. 'Pasal 3 ayat (2)'
    status          TEXT NOT NULL,     -- 'antre' | 'selesai' | 'gagal'
    diperiksa_pada  TIMESTAMPTZ,
    UNIQUE (analisis_id, urutan)
);

CREATE TABLE temuan (
    id                UUID PRIMARY KEY,
    analisis_id       UUID NOT NULL REFERENCES analisis(id) ON DELETE CASCADE,
    satuan_id         UUID REFERENCES satuan_periksa(id) ON DELETE CASCADE,
    aturan_id         TEXT NOT NULL,   -- mis. 'F1-001', kunci ke tabel rujukan di kode
    tingkat_keparahan TEXT NOT NULL,   -- 'tinggi' | 'sedang' | 'rendah'
    jenis_tanda       TEXT NOT NULL,   -- 'penggantian' | 'catatan'
    catatan           TEXT NOT NULL,
    usulan_rumusan    TEXT,
    status            TEXT NOT NULL DEFAULT 'belum_ditinjau',
    dibuat_pada       TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- hanya untuk Fase 3: rujukan hasil pencarian OpenSearch, beda tiap dokumen
CREATE TABLE rujukan_temuan (
    id           UUID PRIMARY KEY,
    temuan_id    UUID NOT NULL REFERENCES temuan(id) ON DELETE CASCADE,
    nomor        TEXT NOT NULL,
    tahun        TEXT NOT NULL,
    pasal        TEXT,
    kutipan      TEXT NOT NULL,
    pdf_url      TEXT,
    skor         REAL
);
```

Yang **tidak** masuk database: tabel rujukan KMK 527 (itu kode), dan isi utuh
dokumen rancangan.

### Lokasi database

**Sekarang, belum dipakai sama sekali:** Neon. Cukup untuk pengembangan, tidak
ada urgensi karena Fase 1 tidak menyentuhnya sama sekali.

**Sebelum Fase 2 mengolah rancangan sungguhan:** lokasi ini wajib
dipertimbangkan ulang. Neon di-host di luar infrastruktur Kemenkeu; brief
bagian 2 dan 8.10 menegaskan rancangan yang belum terbit tidak layak dikirim ke
layanan luar. Tujuan akhir proyek ini juga bermigrasi ke Law Analyzer yang
memakai Postgres internal (`POSTGRES_HOST=localhost` di env-nya) — karena
formatnya sama-sama Postgres, pindah nanti cuma ganti `DATABASE_URL`, tidak ada
kode yang ditulis ulang.

**ORM: SQLModel, bukan Prisma.** Prisma Client Python sudah tidak dipelihara
(diarsipkan April 2025), bukan produk resmi Prisma, dan tetap butuh Node.js di
baliknya meski namanya "untuk Python". SQLModel dibuat oleh pembuat FastAPI
sendiri dan merupakan cara standar resmi menghubungkan FastAPI ke database.

---

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

```json
{
  "id": "f-001",
  "aturan_id": "F1-001",
  "fase": 1,
  "tingkat_keparahan": "tinggi",
  "jenis_tanda": "penggantian",
  "lokasi": {
    "paragraf_index": 3,
    "offset_mulai": 0,
    "panjang": 48,
    "teks_asli": "Tata Cara Uji Coba Penelaahan Rancangan Peraturan"
  },
  "catatan": "Judul peraturan seharusnya ditulis kapital seluruhnya.",
  "usulan_rumusan": "TATA CARA UJI COBA PENELAAHAN RANCANGAN PERATURAN",
  "rujukan": {
    "sumber": "KMK 527/KMK.01/2022 Lampiran II",
    "butir": "...",
    "kutipan": "...",
    "pdf_url": "https://jdih.kemenkeu.go.id/..."
  },
  "status": "belum_ditinjau"
}
```

**`jenis_tanda`** — `"penggantian"` | `"catatan"`. Menentukan cara temuan
dipasang di dokumen (bagian 6.2). Aturan yang menghasilkan temuan wajib
menetapkannya eksplisit.

Bila `jenis_tanda` = `"penggantian"`, maka `usulan_rumusan` **wajib terisi** dan
harus berupa teks pengganti harfiah untuk `lokasi.teks_asli` — bukan contoh
bunyi, bukan penjelasan. Ini kontrak yang mengikat: isi field inilah yang
disisipkan ke naskah orang.

Bila `jenis_tanda` = `"catatan"`, `usulan_rumusan` boleh `null` atau berisi
contoh bunyi yang hanya ditampilkan, tidak pernah disisipkan.

`offset_mulai` dan `panjang` tetap ada untuk menandai rentang presisi di dalam
paragraf.

Salin bentuk ini ke `docs/kontrak-data.md` setiap kali berubah — dua berkas itu
harus selalu sama.

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

Tabel di bawah ini untuk Fase 2/3, disiapkan sejak awal supaya `core/config.py`
tidak dirombak ulang:

| Variabel | Untuk apa | Mulai fase |
|---|---|---|
| `DATABASE_URL` | Koneksi Postgres (analisis, satuan, temuan) | Fase 2 |
| `OPENSEARCH_HOST`, `OPENSEARCH_PORT` | Alamat server pencarian | Fase 3 |
| `OPENSEARCH_USER`, `OPENSEARCH_PASSWORD` | Autentikasi OpenSearch | Fase 3 |
| `OPENSEARCH_INDEX` | Index teks pasal (pencarian kata) | Fase 3 |
| `OPENSEARCH_EMBEDDING_INDEX` | Index vektor (pencarian makna) | Fase 3 |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION` | Model penjawab | Fase 2 |
| `AZURE_TASK_DEPLOYMENT` | Nama deployment model penjawab | Fase 2 |
| `AZURE_EMBEDDING_DEPLOYMENT` | Deployment model pengubah teks→vektor | Fase 3 |

Dua catatan:

- Penamaan di `core/config.py` (`AZURE_TASK_DEPLOYMENT`) **tidak sama** dengan
  penamaan di env Law Analyzer (`AZURE_OPENAI_TASK_DEPLOYMENT_NAME`). Perlu
  diselaraskan saat Fase 2 dimulai, belum masalah sekarang.
- `MINIO_*` tidak diperlukan. Tautan PDF sudah ikut terkirim dari OpenSearch
  sebagai field `pdf_url`.

---

## 13. Urutan implementasi

Langkah 1–4 **sudah selesai** dan terbukti jalan di Word sungguhan. Langkah 5
ke bawah adalah pekerjaan yang tersisa.

1. ~~Salin skema Temuan ke `docs/kontrak-data.md`.~~ **Selesai** — perlu
   diperbarui dengan `jenis_tanda`.
2. ~~Satu alur utuh dengan satu aturan paling sederhana.~~ **Selesai.**
3. ~~Tiga aturan struktur sisanya.~~ **Selesai** — kelimanya jalan, diverifikasi
   lewat `backend/tools/cek_docx.py` terhadap dokumen contoh dan satu RPMK nyata.
4. ~~`cek_ejaan()`.~~ **Selesai** — cakupannya masih sempit dan sengaja begitu:
   "Undang-Undang" dua huruf U kapital (KMK 527 butir 33) dan kata "tentang"
   huruf kecil di judul dasar hukum (butir 32). Jangan memasang kamus besar
   sebelum cakupannya dipastikan ke penelaah.
5. **Buktikan Track Changes jalan, sebelum apa pun dibangun di atasnya.**
   Percobaan sekecil mungkin: set `changeTrackingMode = "TrackAll"`, ganti satu
   kata lewat `insertText(..., "Replace")`, sync, lalu `getTrackedChanges()` dan
   pastikan jumlahnya bertambah. Kalau melempar `NotImplemented` seperti
   Critique, **berhenti** dan laporkan — seluruh bagian 6 harus dirancang ulang,
   jangan diakali sendiri.
6. **Tambahkan `jenis_tanda`** di `models/temuan.py`, isi eksplisit di tiap
   fungsi `rules/format_baku.py` sesuai tabel bagian 6.2, perbarui
   `docs/kontrak-data.md`, tambah tes untuk tiap aturan.
7. **Pasang jalur `penggantian`** di `office.ts` sesuai aturan bagian 6.3 —
   termasuk penurunan otomatis ke `catatan` bila pelacakan gagal dinyalakan.
8. **Ringkas task pane** sesuai bagian 6.4: buang penjelasan panjang, sisakan
   nomor, tingkat, Lompat ke Teks, dan Terima/Tolak untuk temuan `catatan`.
9. **Terakhir**, lengkapi tabel rujukan KMK 527 (bagian 10) dengan kutipan
   yang sudah dibaca visual.

---

## 14. Peraturan untuk agen coding

1. **Dilarang membaca isi berkas `.env`.** Kalau perlu tahu variabel apa saja
   yang tersedia, baca `core/config.py`.
2. **Pastikan `.env` tercantum di `.gitignore`** sebelum menulis berkas apa pun.
3. **Kredensial hanya hidup di backend**, tidak pernah sampai ke browser.
4. **Jangan pakai LLM untuk hal yang bisa diselesaikan regex atau logika biasa.**
   Ini prinsip proyek, bukan saran.
5. **Alat mengusulkan, penelaah yang memutuskan.** Usulan boleh disisipkan ke
   naskah **hanya** sebagai perubahan terlacak yang bisa dibatalkan satu klik,
   dan **hanya** setelah `changeTrackingMode` terbukti menyala. Dilarang:
   memanggil `accept()`/`reject()` dari kode atas inisiatif sendiri, membuat
   tombol "terapkan semua", menimpa teks saat pelacakan mati, dan menyentuh
   rentang di luar `lokasi` temuan. Pelanggaran aturan ini pernah terjadi sekali
   (fungsi `applyUsulanRumusan` yang menimpa satu paragraf penuh ketika
   pencarian meleset) dan berakhir dihapus — jangan diulang.
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
15. **Ikuti urutan di bagian 13**, dan jangan lewati langkah 5.

---

## 15. Definisi selesai

Build ini berhasil kalau:

- [x] `docs/kontrak-data.md` berisi skema Temuan — perlu diperbarui dengan
      `jenis_tanda`
- [x] Task pane terbuka di Word dan membaca paragraf dokumen aktif
- [x] Tombol "Analisis" memanggil backend; backend menjalankan seluruh
      pemeriksaan di bagian 3
- [x] Tiap fungsi di `rules/` punya tes yang jalan tanpa server
- [ ] Track Changes terbukti jalan di Word penelaah (bagian 13 langkah 5)
- [ ] Temuan `penggantian` muncul sebagai perubahan terlacak: teks lama tercoret,
      usulan di sebelahnya
- [ ] Accept di ribbon Review menghasilkan teks bersih; Reject mengembalikan
      naskah asli tanpa bekas
- [ ] Temuan `catatan` muncul sebagai komentar + warna sesuai keparahan, dan
      bisa diterima/ditolak dari task pane
- [ ] Komentar memuat alasan + rujukan butir KMK 527; task pane tidak mengulang
      penjelasan yang sama
- [ ] Accept All menghasilkan versi bersih yang layak dikirim ke unit pemrakarsa
- [ ] Diuji pada dokumen panjang, bukan cuma dokumen contoh
- [ ] Tabel rujukan KMK 527 tidak lagi placeholder
