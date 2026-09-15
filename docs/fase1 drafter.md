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

---

## 1. Judul

**Drafter Analiser — Fase 1: Pemeriksaan Format Baku**

Add-in Word (task pane) + backend FastAPI untuk memeriksa rancangan PMK/KMK
terhadap kaidah penyusunan peraturan.

---

## 2. Apa yang dibangun & tujuan

Penelaah membuka rancangan PMK/KMK di Word, menekan satu tombol, dan bagian yang
perlu ditinjau langsung tersorot di dokumen itu juga — lengkap dengan catatan,
rujukan butir KMK 527 yang mengaturnya, dan usulan rumusan — **tanpa satu
karakter pun berubah**.

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
| Tandai bagian bermasalah dengan warna sesuai keparahan | Hasil analisis Law Analyzer terputus dari dokumen kerja — harus disalin manual (brief bagian 2) | Office.js, lihat tiga lapis di bagian 6 |
| Tiap temuan menyertakan rujukan butir KMK 527 + kutipannya | Penelaah perlu tahu dasar hukumnya, bukan cuma "ini salah" | Tabel rujukan tetap di kode — bagian 10 |
| Terima / tolak tiap temuan | Prinsip: alat memberi rekomendasi, tidak pernah memutuskan | Tombol di popup / task pane |
| Ubah temuan yang diterima jadi komentar permanen | Supaya bisa dibawa ke rapat pembahasan | `Range.insertComment` |
| Pilih cakupan: seluruh dokumen atau bagian terpilih | Fleksibilitas penelaah | `document.getSelection()` vs seluruh body |

---

## 4. Di luar cakupan build ini

Jangan dikerjakan agen coding. Diambil dari brief bagian "Di Luar Lingkup" dan
pembagian fase:

- Mengubah teks dokumen secara otomatis
- Validasi gambar logo Garuda
- Deteksi "kelaziman" bahasa
- Versi untuk masyarakat umum
- Menulis apa pun ke basis data produksi JDIH/Law Analyzer
- Pencarian pembanding ke OpenSearch — itu Fase 3
- Pemeriksaan yang butuh penalaran AI (definisi konsisten, potensi multitafsir)
  — itu Fase 2
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
                                         Task pane menyisipkan sorotan via Office.js
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

Untuk pengembangan, sideload dari folder lokal sudah cukup (Word > Options >
Trust Center > Trusted Add-in Catalogs), tidak perlu izin admin apa pun. Jalur
pemasangan untuk banyak penelaah sekaligus adalah keputusan organisasi di luar
cakupan agen coding.

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

## 6. Tiga lapis tampilan temuan

Komentar Word **tidak bisa punya tombol kustom**. Yang muat di dalam komentar
hanya teks, format dasar, dan satu hyperlink. Jadi tampilannya dibagi tiga,
masing-masing sesuai kemampuan nyatanya:

| Lapis | Isi | Mekanisme | Sifat |
|---|---|---|---|
| Sorotan + popup | Penjelasan singkat, rujukan butir, usulan rumusan, tombol terima/tolak | `Critique` + `popupOptions` (WordApi 1.8) | Sementara, dokumen tidak berubah |
| Komentar permanen | Penjelasan + "KMK 527 Lamp. II butir 3.a" + hyperlink ke PDF JDIH | `Range.insertComment` (1.4) + `contentRange.hyperlink` (1.4) | Tersimpan di berkas |
| Task pane | Kutipan utuh butirnya, sepanjang apa pun | Halaman web biasa | Interaksi bebas |

Kutipan panjang taruh di task pane, jangan dijejalkan ke komentar — komentar
berisi tiga paragraf menyusahkan saat dokumen dibawa ke harmonisasi.
`usulan_rumusan` sengaja tidak ikut ke komentar permanen — biar penelaah
menyunting sendiri, bukan menyalin dari tool.

**Dua risiko yang wajib dicek runtime**, bukan diasumsikan:

- `insertAnnotations` (dasar dari Critique) **mensyaratkan langganan Microsoft
  365** — tercatat di `docs/panduan-officejs.md`.
- `popupOptions` butuh WordApi 1.8 yang tergolong baru.

Cek dengan `Office.context.requirements.isSetSupported("WordApi", "1.8")`.
Kalau tidak didukung, jatuh ke lapis komentar permanen + task pane. Karena itu
lapis kedua dan ketiga tidak boleh cuma jadi pelengkap — keduanya harus bisa
berdiri sendiri.

---

## 7. Susunan file

```
drafter-analiser/
├── backend/
│   ├── app/
│   │   ├── main.py              ← sudah ada: FastAPI + CORS + /health
│   │   ├── core/config.py       ← sudah ada: Settings
│   │   ├── api/                 ← KOSONG, isi di sini
│   │   ├── rules/               ← KOSONG, aturan Fase 1 di sini
│   │   ├── models/              ← KOSONG, skema Temuan di sini
│   │   ├── services/            ← KOSONG (belum dipakai di Fase 1)
│   │   ├── parser/              ← KOSONG (belum dipakai di Fase 1)
│   │   ├── llm/                 ← KOSONG (tidak dipakai di Fase 1)
│   │   └── retrieval/           ← KOSONG (tidak dipakai di Fase 1)
│   ├── requirements.txt
│   └── tests/
├── docs/
│   └── kontrak-data.md          ← ISI dengan bagian 11 dokumen ini — lihat bagian 13
└── frontend/
    └── src/app/
        ├── page.tsx
        ├── layout.tsx
        └── taskpane/page.tsx    ← sudah ada, kerangka kosong
```

---

## 8. Penjelasan backend ↔ frontend

```
backend/app/main.py
  ===> daftarkan router: app.include_router(analisis.router)
       FastAPI tidak memindai folder seperti Next.js — router yang tidak
       didaftarkan di sini tidak akan pernah bisa diakses

backend/app/api/analisis.py                      [BARU]
  ===> endpoint POST /analisis/jalankan
       terima daftar paragraf, panggil fungsi di rules/, kembalikan daftar
       Temuan. Handler setipis mungkin: parse → panggil → kembalikan

backend/app/rules/format_baku.py                 [BARU]
  ===> satu fungsi murni per pemeriksaan di bagian 3:
       cek_judul_konsisten(), cek_judul_kapital(),
       cek_kelengkapan_struktur(), cek_frasa_baku_menimbang(), cek_ejaan()
       Tanpa objek Request/Response. Harus bisa dites tanpa server nyala

       Catatan cek_frasa_baku_menimbang(): berlaku HANYA kalau Menimbang
       punya lebih dari satu butir (ada huruf a/b/c). Kalau cuma satu butir
       tanpa huruf, lewati — itu bentuk yang sah menurut KMK 527 butir 19,
       bukan kesalahan. Menandainya berarti salah tandai

backend/app/rules/rujukan_kmk527.py              [BARU]
  ===> tabel tetap: id aturan → butir KMK 527 + kutipannya (bagian 10)
       Ini KODE, bukan isi database — supaya bisa diperiksa lewat review

backend/app/models/temuan.py                     [BARU]
  ===> skema Pydantic bentuk Temuan (bagian 11) — kontrak final

frontend/src/app/taskpane/page.tsx
  ===> UI task pane: tombol Analisis, daftar temuan ringkas, detail kutipan
       fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/analisis/jalankan`)
       — pakai env yang sudah ada di frontend/.env.example, JANGAN hardcode
       URL langsung di kode

frontend/src/lib/office.ts                       [BARU]
  ===> kumpulkan SEMUA panggilan Office.js di satu berkas:
       baca paragraf, sisipkan critique, sisipkan comment, cek requirement set
```

---

## 9. Struktur database

### Fase 1 tidak memakai database sama sekali

Ini keputusan sadar, bukan kelalaian:

- Pemeriksaan Fase 1 selesai dalam hitungan detik — tidak ada proses latar
  belakang yang perlu dilanjutkan bila terputus.
- Temuan hidup di memori task pane selama dokumen terbuka.
- Temuan yang **diterima** disimpan sebagai komentar **di dalam berkas .docx itu
  sendiri** — ikut ke mana pun dokumen dibawa, tanpa perlu server.
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
-- inilah yang membuat proses terputus tidak kehilangan hasil
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
sendiri dan merupakan cara standar resmi menghubungkan FastAPI ke database —
skema Temuan yang sudah jadi Pydantic model (bagian 11) bisa langsung dipakai
sebagai definisi tabel, tidak perlu ditulis dua kali.

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

---

## 11. Bentuk data Temuan — KONTRAK FINAL

```json
{
  "id": "f-001",
  "aturan_id": "F1-001",
  "fase": 1,
  "tingkat_keparahan": "tinggi",
  "lokasi": {
    "paragraf_index": 3,
    "offset_mulai": 0,
    "panjang": 58,
    "teks_asli": "Peraturan Menteri Keuangan tentang ..."
  },
  "catatan": "Judul peraturan seharusnya ditulis kapital seluruhnya.",
  "usulan_rumusan": "PERATURAN MENTERI KEUANGAN TENTANG ...",
  "rujukan": {
    "sumber": "KMK 527/KMK.01/2022 Lampiran II",
    "butir": "...",
    "kutipan": "...",
    "pdf_url": "https://jdih.kemenkeu.go.id/..."
  },
  "status": "belum_ditinjau"
}
```

`offset_mulai` dan `panjang` diperlukan untuk `Critique.start` / `.length` supaya
sorotan presisi di dalam paragraf, bukan menyorot satu paragraf penuh.

**Langkah pertama sebelum kode lain ditulis:** salin skema ini jadi isi asli
`docs/kontrak-data.md` di repo (sekarang masih kosong) — lihat bagian 13.

---

## 12. Environment variables

**Nilai asli tidak boleh disalin ke repo, ke chat, atau ke agen coding.** Yang
boleh diketahui agen coding hanya nama variabelnya. Isi sebenarnya diminta ke
admin/mentor lewat jalur aman saat pemasangan.

Fase 1 memakai satu env yang sudah ada di kerangka:

| Variabel | Untuk apa |
|---|---|
| `NEXT_PUBLIC_API_BASE_URL` | Alamat backend yang dipanggil task pane lewat `fetch`. Sudah ada di `frontend/.env.example` — pakai langsung, jangan hardcode URL di kode |

Prefiks `NEXT_PUBLIC_` wajib untuk env yang dibaca kode yang jalan di browser —
Next.js sengaja menyembunyikan env tanpa prefiks itu dari browser. Karena itu
juga: **jangan pernah** beri prefiks ini ke variabel berisi kredensial, karena
otomatis ikut ter-build ke kode yang bisa dibaca siapa pun lewat DevTools.

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
  sebagai field `pdf_url`, jadi tidak perlu mengambil berkas langsung.

---

## 13. Urutan implementasi

Jangan bangun semuanya sekaligus. Brief bagian 7 proyek ini sendiri menyarankan
urutan bertahap — dan ini yang membuat build pertama kemungkinan besar berhasil
tanpa berantakan di tengah jalan:

1. **Salin skema Temuan (bagian 11) ke `docs/kontrak-data.md`.** Berkas itu di
   repo masih kosong padahal dokumennya sendiri menyebut ini prasyarat sebelum
   modul lain ditulis.
2. **Satu alur utuh dengan SATU aturan paling sederhana dulu** — disarankan
   `cek_judul_kapital()`. Dari baca paragraf di Word → kirim ke backend →
   balik sebagai Temuan → tersorot di dokumen. Buktikan pipa-nya nyambung
   ujung ke ujung sebelum menambah apa pun lagi.
3. **Baru setelah langkah 2 terbukti jalan**, tambahkan 3 aturan struktur
   sisanya satu per satu di `rules/format_baku.py`: `cek_judul_konsisten()`,
   `cek_kelengkapan_struktur()`, `cek_frasa_baku_menimbang()`.
4. **`cek_ejaan()` paling akhir, sesudah empat aturan di atas jalan.** Word
   sendiri sudah punya pemeriksa ejaan bahasa Indonesia bawaan, jadi mengejar
   typo biasa berarti menduplikasi yang sudah ada. Yang berguna di sini
   kemungkinan besar ejaan baku penyusunan peraturan — misalnya
   "Undang-Undang" wajib dua huruf u kapital (KMK 527 butir 33), atau kata
   "tentang" tetap huruf kecil di dalam judul dasar hukum (butir 32).
   Kerjakan bentuk paling sederhana dulu; jangan memasang kamus besar sebelum
   cakupannya dipastikan ke penelaah.
5. **Baru setelah semua aturan jalan**, bangun penuh tiga lapis tampilan di
   bagian 6 (popup, komentar permanen, task pane) — jangan dikerjakan paralel
   dengan langkah 2–4.
6. **Terakhir**, lengkapi tabel rujukan KMK 527 (bagian 10) dengan kutipan
   yang sudah dibaca visual, menyusul tiap aturan yang ditambahkan.

Kalau agen coding mencoba membangun lima aturan sekaligus plus tiga lapis
tampilan di awal, hentikan — itu yang biasanya membuat build pertama gagal
setengah jalan, bukan berhasil lebih cepat.

---

## 14. Peraturan untuk agen coding

1. **Dilarang membaca isi berkas `.env`.** Kalau perlu tahu variabel apa saja
   yang tersedia, baca `core/config.py`.
2. **Pastikan `.env` tercantum di `.gitignore`** sebelum menulis berkas apa pun.
3. **Kredensial hanya hidup di backend**, tidak pernah sampai ke browser.
4. **Jangan pakai LLM untuk hal yang bisa diselesaikan regex atau logika biasa.**
   Ini prinsip proyek, bukan saran.
5. **Alat memberi rekomendasi, tidak pernah mengubah naskah sendiri.** Tidak ada
   auto-apply, tidak ada penggantian teks otomatis.
6. **Setiap temuan wajib membawa rujukan yang bisa diperiksa** — diambil dari
   tabel tetap atau hasil pencarian, **tidak boleh dikarang**.
7. **Jangan menulis apa pun ke basis data produksi JDIH/Law Analyzer.**
8. **Jangan menurunkan aturan dari hasil ekstraksi teks PDF KMK 527 atau PMK
   164** — salinannya OCR rusak. Aturan harus diverifikasi manual dari naskah
   yang dibaca visual.
9. **Office.js jarang muncul di data latih model** — model cenderung mengarang
   method yang tidak ada. Verifikasi tiap method ke
   `frontend/node_modules/@types/office-js/index.d.ts` sebelum menulis kode.
   Cara cek: `grep -n "namaMethod" -B 8 index.d.ts`.
10. **Sebelum menambah dependency, periksa apakah kebutuhannya bisa dipenuhi
    yang sudah terpasang.** Tailwind sudah ada — jangan tambah Bootstrap.
    SQLModel sudah ditetapkan sebagai ORM — jangan tambah Prisma.
11. **Route handler FastAPI setipis mungkin**: parse input → panggil fungsi →
    kembalikan JSON. Logika pemeriksaan harus fungsi murni yang bisa dites tanpa
    menjalankan server.
12. **Jangan simpan state global di backend.** Tiap permintaan berdiri sendiri,
    supaya banyak penelaah bisa memakai bersamaan.
13. **Jangan over-engineer untuk skala besar di build pertama.** Tulis kode yang
    wajar efisien — jangan memproses paragraf berulang secara O(n²), jangan
    memblokir event loop saat analisis berjalan — tapi belum perlu antrean,
    worker pool, atau caching berlapis.
14. **Ikuti urutan di bagian 13.** Jangan membangun semua aturan dan semua
    lapis tampilan secara bersamaan di build pertama.

---

## 15. Definisi selesai

Build ini berhasil kalau:

- [ ] `docs/kontrak-data.md` sudah berisi skema Temuan final (bagian 11)
- [ ] Task pane terbuka di Word dan membaca paragraf dokumen aktif
- [ ] Tombol "Analisis" memanggil backend; backend menjalankan seluruh
      pemeriksaan di bagian 3
- [ ] Bagian bermasalah tersorot dengan warna sesuai keparahan
- [ ] Klik sorotan menampilkan catatan, rujukan butir KMK 527, dan usulan
      rumusan
- [ ] Temuan bisa diterima (jadi komentar permanen) atau ditolak
- [ ] Tetap berfungsi saat `popupOptions` tidak didukung (jatuh ke komentar +
      task pane)
- [ ] Diuji pada dokumen panjang, bukan cuma dokumen pendek
- [ ] Tiap fungsi di `rules/` punya tes yang jalan tanpa server
