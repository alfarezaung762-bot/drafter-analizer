# Fase 2 & 3 — Rancangan

> **Rancangan, bukan perintah kerja.** Belum ada kode yang ditulis dari dokumen
> ini. Acuan: `project-brief.md` 8.7–8.13 dan `fase1 drafter.md` untuk apa pun
> yang menyangkut lapisan penandaan.

---

## 1. Ringkasnya

Fase 1 memeriksa **bentuk** — kapital, tanda baca, kelengkapan bagian.
Jawabannya pasti, dan semuanya diselesaikan regex.

| | Pertanyaannya | Sumber jawabannya |
|---|---|---|
| **Fase 2** | Apakah dokumen ini **konsisten dengan dirinya sendiri**, dan ketentuannya jelas? | dokumen itu sendiri |
| **Fase 3** | Apakah ini **berpotensi bertentangan** dengan peraturan lain? | korpus peraturan di OpenSearch |

Bedanya dengan Fase 1: Fase 1 bekerja di atas daftar paragraf datar. Fase 2
tidak bisa — pertanyaan "apakah Pasal 12 yang dirujuk itu ada" menuntut tahu
**struktur** dokumen. Maka pondasinya satu: **parser** yang memecah naskah jadi
pohon satuan (BAB → Pasal → ayat → huruf). Semua yang lain menumpang di atasnya.

Sebagian pemeriksaan tetap tanpa AI karena jawabannya pasti. Sisanya pakai
model, dengan alur tiga tahap: **meringkas → menalar → memastikan**. Tidak ada
temuan yang boleh lahir sebelum tahap memastikan.

---

## 2. Struktur folder

Empat folder sudah disiapkan sejak Fase 1 dan masih kosong. Sekarang diisi.

```
backend/app/
├── parser/                  KOSONG → diisi.  PONDASI semuanya
│   ├── satuan.py               model Satuan + rentang paragraf asalnya
│   ├── struktur.py             paragraf datar → pohon satuan
│   └── definisi.py             ambil daftar istilah dari Pasal 1
│
├── rules/
│   ├── format_baku.py          Fase 1 — TIDAK DISENTUH
│   ├── rujukan_kmk527.py       + entri F2-*
│   └── konsistensi.py          BARU — aturan mekanis Fase 2
│
├── llm/                     KOSONG → diisi
│   ├── klien.py                SATU-SATUNYA pintu ke Azure OpenAI
│   ├── prompt.py               prompt sebagai konstanta bernama
│   └── penalaran.py            tiga tahap
│
├── retrieval/               KOSONG → diisi (Fase 3)
│   ├── opensearch.py           SATU-SATUNYA pintu ke OpenSearch
│   └── pembanding.py           cari pembanding + saring status berlaku
│
├── services/                KOSONG → diisi
│   ├── analisis_fase2.py       orkestrasi tujuh langkah
│   └── antrean.py              pekerjaan latar belakang, simpan per satuan
│
├── db/                      BARU
│   ├── tabel.py                SQLModel: Pekerjaan, HasilSatuan
│   └── sesi.py                 koneksi Postgres
│
├── models/
│   ├── temuan.py               + satuan_id, skor, tahap_konfirmasi
│   └── pekerjaan.py            BARU
│
└── api/
    └── analisis_lanjut.py      BARU — mulai, tanya status, ambil hasil

frontend/src/
├── lib/aturan-fase2.ts      BARU — keterangan aturan untuk panel Pengaturan
├── lib/types.ts             disamakan dengan temuan.py
├── lib/office.ts            + penandaan bertahap per kelompok
└── app/taskpane/page.tsx    + progres, kelompok fase, batas tampil
```

**Kenapa masing-masing perlu ada:**

| Folder | Kenapa terpisah |
|---|---|
| `parser/` | Struktur dokumen dipakai **semua** pemeriksaan Fase 2 dan 3. Kalau tiap aturan memecah naskahnya sendiri, tiap aturan punya bug pemecahan sendiri |
| `rules/konsistensi.py` | Aturan mekanis mengikuti pola `format_baku.py` — fungsi murni, bisa dites tanpa server, tanpa model |
| `llm/` | CLAUDE.md: panggilan ke layanan luar dikumpulkan di satu lapisan. Batas waktu, percobaan ulang, pencatatan biaya, dan **penolakan keluaran cacat** ditangani sekali di situ, bukan di tiap pemanggil |
| `retrieval/` | Alasan sama untuk OpenSearch. Sekaligus membuat sumber pembanding bisa ditambah tanpa mengubah alur |
| `services/` | Urutan tujuh langkah hidup di satu tempat. Route handler tetap tipis |
| `db/` | Analisis berjalan menit. Brief 8.9: hasil disimpan per satuan supaya yang sudah selesai tetap ada meski proses terputus |
| `aturan-fase2.ts` | Penelaah harus bisa melihat sendiri apa yang diperiksa dan apa yang **tidak** — kembaran `aturan-fase1.ts` |

### 2.1 Teknologi

**Sudah terpasang, tidak perlu apa-apa lagi:**

| | Untuk apa |
|---|---|
| FastAPI + Pydantic | endpoint dan kontrak data |
| `openai` | Azure OpenAI — sudah terbukti lewat `cek_env.py` |
| `opensearch-py` | korpus Fase 3 |
| `httpx` | panggilan HTTP |
| Office.js | seluruh lapisan penandaan sudah jadi di Fase 1 |

**Yang ditambahkan:**

| | Untuk apa |
|---|---|
| `sqlmodel` | satu model dipakai sekaligus sebagai skema validasi dan tabel |
| `psycopg[binary]` | driver Postgres |
| penghitung token sederhana | menentukan berapa satuan muat per panggilan. Perkiraan kasar (karakter ÷ 4) dulu |

**Yang sengaja TIDAK dipakai:**

| | Kenapa tidak |
|---|---|
| LangChain dsb. | alurnya sudah tetap tujuh langkah. Tidak ada yang perlu diputuskan model soal langkah mana berikutnya. Menambah lapisan berarti menambah tempat kesalahan bersembunyi |
| Celery / Redis | satu penelaah, satu dokumen. Proses latar belakang di dalam FastAPI sudah cukup |
| Basis data vektor terpisah | OpenSearch sudah punya index embedding |

### 2.2 Env yang dibutuhkan

Sudah ada dan terbukti terhubung — tidak berubah:

```
OPENSEARCH_HOST / PORT / USER / PASSWORD / INDEX / EMBEDDING_INDEX
AZURE_OPENAI_TASK_*           chat
AZURE_OPENAI_EMBEDDING_*      emb3small, 1536 dimensi
NEXT_PUBLIC_API_BASE_URL      frontend
```

Yang ditambahkan:

```
DATABASE_URL                  Postgres (Neon) — lihat 2.3
FASE2_SATUAN_PER_PANGGILAN    berapa satuan dikelompokkan jadi satu panggilan
FASE2_PANGGILAN_BERBARENGAN   berapa panggilan jalan sekaligus
FASE2_AMBANG_SKOR             batas bawah temuan AI
```

Keempatnya **angka yang bisa diatur, bukan asumsi tertanam** — nilainya
ditetapkan setelah diukur pada dokumen nyata, dan ikut berubah kalau modelnya
diganti.

### 2.3 Basis data — Neon

Dipakai **Neon** (Postgres serverless), lewat SQLModel.

Yang disimpan cuma dua tabel:

```
Pekerjaan     id, dokumen, jenis, status, mulai, selesai, biaya
HasilSatuan   pekerjaan_id, satuan_id, ringkasan, dugaan, status
```

**Yang TIDAK disimpan:** isi utuh naskah rancangan. Hanya ringkasan per satuan
dan temuannya.

Satu hal yang perlu diketahui, bukan untuk menghalangi: Neon di-host **di luar
infrastruktur Kemenkeu**, sedangkan `catatan` dan `usulan_rumusan` hampir pasti
mengutip potongan rancangan. Untuk pengembangan dengan dokumen contoh itu tidak
masalah.

Kabar baiknya, ini **tidak mengunci apa pun**: Neon adalah Postgres, dan Law
Analyzer juga memakai Postgres di infrastrukturnya sendiri. Pindah dari Neon ke
Postgres internal berarti **mengganti satu baris `DATABASE_URL`** — nol
perubahan kode. Jadi keputusannya bisa ditunda sampai benar-benar dipakai pada
rancangan sungguhan, tanpa biaya apa pun sekarang.

---

## 3. Alur — tujuh langkah

### 3.1 Alur utama

```
LANGKAH 0  MEMBUAT PETA                         kode · detik · gratis
           paragraf datar → parser → pohon satuan
           sekalian dihitung: berapa satuan, berapa perkiraan token
                    │
LANGKAH 1  MENYARING                            kode · detik · gratis
           satuan tanpa norma dikeluarkan
           DILEWATI  "…mulai berlaku pada tanggal diundangkan."
           DIBACA    "Menteri wajib menetapkan … paling lambat 30 hari."
                    │
LANGKAH 2  MEMBACA PER SATUAN                   model · berbayar
           tiap panggilan = KONTEKS TETAP  (judul, Menimbang, Mengingat,
                                            definisi Pasal 1, kerangka pasal)
                          + SATUAN INI utuh
                          + SATUAN YANG DIRUJUKNYA (dicari parser)
           keluar: satu baris peta per satuan
                    │
LANGKAH 3  MENALAR DI ATAS PETA                 model · 1–2 panggilan
           yang dikirim: SELURUH BARIS PETA, bukan teks penuh
           keluar: DUGAAN — belum temuan
                    │
LANGKAH 4  MEMASTIKAN                           model · beberapa panggilan
           hanya satuan yang dicurigai, dibaca UTUH
           dugaan dipilah:  KLAIM INTERNAL  → lanjut ke 5
                            KLAIM EKSTERNAL → wajib lewat 6 dulu
                    │
LANGKAH 5  VERIFIKASI MEKANIS                   kode · detik · gratis
           ✓ teks_asli ada PERSIS di satuan itu?
           ✓ nomor pasal yang dikutip benar-benar ada?
           ✓ skor di atas ambang?
                    │
LANGKAH 6  MENCARI PEMBANDING                   Fase 3 · hanya klaim eksternal
           embedding → korpus → saring status berlaku
           → MEMASTIKAN SEKALI LAGI dengan pembanding di tangan
           tidak ada hasil pencarian → TIDAK ADA TEMUAN
```

Langkah 0, 1, dan 5 sengaja tanpa AI: hasilnya pasti, gratis, dan kalau salah
bisa ditunjukkan baris mana yang keliru.

### 3.2 Cabang — tabrakan antar-pasal

Cabang yang kamu tanyakan. Terjadi di **Langkah 3**, karena hanya di situ
seluruh dokumen terlihat sekaligus.

Contoh: **Pasal 1 vs Pasal 17.**

> **Pasal 1 angka 8** — "Hari adalah hari kerja."
> **Pasal 17 ayat (1)** — "…diselesaikan paling lambat 30 (tiga puluh) hari
> kalender."

```
LANGKAH 3   dari peta terlihat dua baris berbenturan:
            pasal-1-angka-8   mendefinisikan "Hari" = hari kerja
            pasal-17-ayat-1   memakai "hari kalender"
            → DUGAAN TABRAKAN, menyebut DUA alamat sekaligus
                    │
LANGKAH 4′  MEMASTIKAN VERSI TABRAKAN
            KEDUA satuan dibaca utuh DALAM SATU PANGGILAN YANG SAMA —
            bukan dua panggilan terpisah. Menilai tabrakan menuntut
            keduanya ada di hadapan model sekaligus.
                    │
            ┌───────┴────────┐
            ▼                ▼
        GUGUR            BERTAHAN
   Pasal 17 ternyata   → lanjut: MANA YANG DITANDAI?
   menyebut "hari
   kalender" sebagai
   pengecualian yang
   sah → berhenti,
   tidak ada temuan
                             │
LANGKAH 4″  MENENTUKAN SISI YANG MENYIMPANG
            Yang ditandai satuan yang MENYIMPANG dari yang lain.
            Di sini: Pasal 17, karena Pasal 1 yang memegang definisi.

            Kalau tidak bisa ditentukan mana yang menyimpang — misal
            Pasal 5 dan Pasal 17 sama-sama menugaskan hal yang sama ke
            pejabat berbeda — yang ditandai yang LEBIH BELAKANG, dan
            komentarnya menyebut keduanya.
                    │
            SATU temuan, bukan dua. Penelaah mengambil satu keputusan,
            bukan dua yang saling bergantung.
                    │
LANGKAH 5   teks_asli = "30 (tiga puluh) hari kalender"
            → dicari di paragraf Pasal 17 → ketemu persis
            → nomor "Pasal 1" yang disebut komentar ada di pohon satuan ✓
                    │
            JENIS TANDA: `catatan` (blok kuning), bukan penggantian.
            Alat tahu keduanya tidak cocok, tapi tidak tahu sisi mana
            yang seharusnya berubah — itu keputusan penelaah.
                    │
            Komentarnya:
            "Memakai 'hari kalender', sedangkan Pasal 1 angka 8
             mendefinisikan Hari sebagai hari kerja."
```

**Kenapa satu temuan, bukan dua?** Kalau Pasal 1 dan Pasal 17 masing-masing jadi
temuan, menolak salah satunya meninggalkan yang lain menggantung — padahal
persoalannya satu. Satu temuan, satu keputusan.

### 3.3 Cabang — satuan terlalu panjang

Satu pasal yang teksnya melebihi anggaran satu panggilan.

```
LANGKAH 2   satuan dipecah menurut ayat, bukan menurut karakter.
            Kalau satu AYAT pun masih terlalu panjang → dikirim sendirian,
            tanpa satuan lain, dan konteks tetapnya dipangkas ke
            definisi + judul saja.
            Tidak pernah dipotong di tengah kalimat.
```

### 3.4 Cabang — rentang temuan tidak ketemu di naskah

```
LANGKAH 5   teks_asli TIDAK ketemu persis
                    │
            ┌───────┴────────┐
            ▼                ▼
   ada usulan?          tidak ada usulan
   → TURUN jadi         → temuan tetap keluar, tapi TIDAK
     `catatan`,           ditandai di naskah. Kartunya di panel
     tidak disisipkan     mencetak alasannya sendiri
```

Tidak pernah diperlebar ke satu paragraf. Itu pelanggaran yang sudah pernah
terjadi di Fase 1 dan berakhir menimpa naskah.

### 3.5 Cabang — pencarian korpus kosong

```
LANGKAH 6   klaim eksternal, tapi pencarian tidak menemukan apa pun
                    │
            TEMUAN TIDAK KELUAR SAMA SEKALI.
            Bukan "temuan tanpa rujukan" — brief 8.10: catatan hanya
            boleh menyebut yang ada di hasil pencarian.
```

### 3.6 Cabang — parser gagal

```
LANGKAH 0   struktur tidak masuk akal (nol pasal padahal dokumen panjang,
            ayat di luar pasal, penomoran melompat belasan)
                    │
            SELURUH FASE 2 TIDAK DIJALANKAN, dan panel mengatakannya.
            Fase 1 tetap jalan seperti biasa.
            Diam lebih baik daripada memeriksa struktur yang salah baca.
```

### 3.7 Contoh isi peta — 20 pasal

Beginilah peta yang dipegang Langkah 3. Satu baris per satuan, teks penuhnya
tidak ikut.

| satuan | ringkasan | norma | merujuk | dugaan |
|---|---|---|---|---|
| `pasal-1-angka-1` | definisi: Barang Milik Negara | — | — | — |
| `pasal-1-angka-5` | definisi: Pengelola Barang | — | — | — |
| `pasal-1-angka-8` | definisi: **Hari = hari kerja** | — | — | — |
| `pasal-1-angka-9` | definisi: Sistem Informasi | — | — | **tidak pernah dipakai** |
| `pasal-2` | ruang lingkup pengaturan | — | — | — |
| `pasal-3` | asas pengelolaan | — | — | — |
| `pasal-4-ayat-1` | Pengguna Barang mengajukan permohonan | ya | — | — |
| `pasal-4-ayat-2` | dokumen yang dilampirkan | ya | `pasal-4-ayat-1` | — |
| `pasal-5` | Pengelola Barang menetapkan status | ya | `pasal-4-ayat-1` | — |
| `pasal-6` | jangka waktu penetapan | ya | `pasal-5` | — |
| `pasal-7` | penolakan permohonan | ya | `pasal-5` | — |
| `pasal-8` | permohonan ulang | ya | `pasal-7` | — |
| `pasal-9` | tata cara pencatatan | ya | **`pasal-30`** | **Pasal 30 tidak ada** |
| `pasal-10` | kewajiban pelaporan | ya | — | — |
| `pasal-11` | pemantauan | ya | — | — |
| `pasal-12-ayat-1` | permohonan perubahan status | ya | — | — |
| `pasal-12-ayat-2` | batas 30 hari kerja | ya | `pasal-12-ayat-1` | **tidak menyebut siapa yang menyelesaikan** |
| `pasal-15` | sanksi administratif | ya | `pasal-10` | — |
| `pasal-17-ayat-1` | batas **30 hari kalender** | ya | — | **berbenturan dengan `pasal-1-angka-8`** |
| `pasal-20` | ketentuan penutup | — | — | — |

**Yang disimpulkan Langkah 3 dari peta ini:**

| Dugaan | Jenis | Ditindaklanjuti |
|---|---|---|
| `pasal-9` merujuk Pasal 30 yang tidak ada | **mekanis** — sudah ketahuan parser, tanpa model | langsung jadi temuan |
| `pasal-1-angka-9` definisi tak terpakai | **mekanis** | langsung jadi temuan |
| `pasal-12-ayat-2` tanpa pemikul | penalaran, internal | Langkah 4 |
| `pasal-17-ayat-1` vs `pasal-1-angka-8` | penalaran, **tabrakan** | Langkah 4′ (3.2) |
| `pasal-2` dan `pasal-3` | tanpa norma | dilewati sejak Langkah 1 |

Peta 20 baris ini ukurannya beberapa ratus token. Untuk 175 satuan pun masih
beberapa ribu — **muat dikirim sekaligus, sementara teks penuhnya tidak.** Itu
sebabnya peta ada.

---

## 4. Fitur — apa saja yang bisa dianalisis

### Fase 2 — mekanis, tanpa AI, hasilnya pasti

| Kode | Menemukan |
|---|---|
| F2-001 | Rujukan "sebagaimana dimaksud dalam Pasal N" ke pasal/ayat yang **tidak ada** |
| F2-002 | Istilah berkapital yang **tidak ada** di daftar definisi Pasal 1 |
| F2-003 | Definisi di Pasal 1 yang **tidak pernah dipakai** |
| F2-004 | Penomoran melompat atau berulang (Pasal 5 → Pasal 7; dua ayat (2)) |
| F2-005 | Lampiran dirujuk tapi tidak ada, atau ada tapi tidak dirujuk |
| F2-006 | Urutan "Mengingat" tidak mengikuti hierarki |

### Fase 2 — penalaran, dengan AI

| Kode | Menemukan |
|---|---|
| F2-101 | **Pasal bertabrakan** — dua ketentuan yang tidak bisa berlaku bersamaan |
| F2-102 | Kewajiban **tanpa pemikul** yang jelas |
| F2-103 | Rumusan yang **bisa dibaca dua arah** — syarat kumulatif atau alternatif |
| F2-104 | Kata operasional **bertabrakan** dalam satu ketentuan (wajib + dapat) |
| F2-105 | Tujuan di Menimbang yang **tidak tercakup** batang tubuh |

### Fase 3 — pembanding dari korpus

| Kode | Menemukan |
|---|---|
| F3-001 | **Berpotensi bertentangan** dengan peraturan lain yang masih berlaku |
| F3-002 | Dasar hukum di Mengingat yang **sudah dicabut atau diubah** |

Penomoran sengaja dibedakan: **`F2-0xx` deterministik, `F2-1xx` hasil
penalaran.** Penelaah berhak tahu mana yang pasti dan mana yang tebakan mesin —
dan itu terlihat dari kodenya sendiri.

### 4.1 Batasan

**Dari Word**

| | |
|---|---|
| Tidak ada penghitung kata/karakter | dihitung sendiri dari teks yang sudah dibaca |
| `Word.search()` ~255 karakter | temuan lebih panjang tidak pernah ketemu → dipotong 120 karakter, warisan Fase 1 |
| Penandaan butuh teks **cocok persis** | keluaran model wajib diverifikasi kode (Langkah 5) |
| Panel = halaman web di dalam Word | beban penggambaran jadi titik gagal |

**Dari model**

| | |
|---|---|
| Bentuk keluarannya tidak bisa dipercaya | prompt minta JSON ≠ dapat JSON. Validasi di kode |
| Bisa mengarang nomor peraturan | nomor wajib ada di pohon satuan atau di hasil pencarian |
| Hasilnya bisa berbeda tiap dijalankan | temuan AI wajib bisa dibedakan dari yang deterministik |
| Berbayar, dan modelnya akan diganti | ukuran potongan jadi angka yang bisa diatur |
| Ada kuota panggilan per menit | jumlah yang berbarengan dibatasi, dengan perlambatan otomatis |

**Dari korpus (Fase 3)**

| | |
|---|---|
| Teksnya hasil **OCR yang rusak** | kutipan wajib bawa penanda "belum diverifikasi" — mekanismenya sudah ada di `RujukanTemuan` |
| Memuat peraturan yang sudah dicabut | saring status berlaku sebagai penyaring **keras** |
| Metadata relasinya pernah keliru | perlu pemeriksaan kewajaran tahun |
| Cakupannya belum diverifikasi | brief 8.12 menandai sendiri kesimpulannya belum diperiksa langsung |
| Akses **baca saja** | tidak ada `index`, `update`, `delete` |

**Dari pengalaman yang sudah gagal**

Law Analyzer macet di 68/175 satuan pada PMK 124/2024 — tiga kali percobaan,
titik berhentinya selalu sama, jadi penyebabnya **beban penggambaran**, bukan
kegagalan acak. Empat syarat yang mengikat: panel hanya daftar ringkas; hasil
**ditambahkan** tanpa menggambar ulang; jumlah tampil dibatasi; penandaan
disisipkan **per kelompok**.

**Yang diwarisi Fase 1 dan tidak boleh dilonggarkan**

- Apa pun yang ditandai wajib benar-benar salah.
- Rentang yang tidak ketemu **tidak ditandai sama sekali** — bukan diperlebar.
- Alat mengusulkan, penelaah memutuskan. Tidak ada "terapkan semua".
- Penandaan berjalan dengan pelacakan perubahan dimatikan.
- **Nomor temuan tidak pernah diurutkan ulang.** Fase 2 melanjutkan dari nomor
  terakhir Fase 1 — nomor itu melekat pada komentar dan tag `DA-ASLI-{n}` yang
  sudah terpasang di naskah.

**Batas temuan** — model **tidak pernah** diberi tahu angka target. Pertanyaannya
per satuan: "ada yang bermasalah di sini? kalau tidak ada, katakan tidak ada."
Penyaring sebenarnya adalah ambang skor; batas tampil cuma jaring pengaman
penggambaran. Kalau keluar 213 temuan, panel mengatakannya apa adanya — jumlah
sebanyak itu sendiri adalah informasi.

---

## 5. Sisa pertanyaan

1. **Berapa satuan per panggilan, berapa yang berbarengan, berapa ambang skor.**
   Tidak bisa ditetapkan dari meja — diukur pada dokumen nyata.
2. **Aturan mekanis mana yang dibangun lebih dulu.** Brief 8.11 menandai
   daftarnya belum dikonfirmasi penelaah. Jalan murahnya: bandingkan dengan
   coretan telaah pada RPMK/RKMK yang sudah diberikan mentor.
3. **Bentuk index OpenSearch yang sebenarnya.** Keterangan "Dokumen → Blok, satu
   blok per pasal" masih lisan. Perlu dilihat langsung sebelum Fase 3 ditulis.
4. **Fase 2 jalan otomatis sesudah Fase 1, atau ditekan terpisah.** Menentukan
   bentuk panel. Analisis yang berjalan menit dan berbayar sebaiknya tidak jalan
   tanpa diminta.
5. **Uji Word Fase 1 belum dijalankan.** Seluruh Fase 2 menumpang lapisan
   penandaan yang dibuktikan di situ.

---

## 6. Hal janggal yang saya temukan

**1. Keputusan Neon cuma hidup di folder yang ditandai usang.**
Pembahasan Neon — berikut rekomendasi "Postgres internal untuk data sungguhan"
— ada di `Claude outputs/fase1 drafter.md`, bukan di `docs/`. Folder itu memuat
tiga salinan dokumen rancangan yang isinya **sudah berbeda** dari `docs/`, dan
terlacak git. Keputusan penting yang hanya ada di salinan usang cepat atau
lambat akan hilang atau bertabrakan.

**2. Pengaman analisis berulang akan mengunci penelaah.**
Sekarang tombol Analisis mati selama masih ada temuan belum diputuskan. Dengan
Fase 2 berjalan menit, penelaah jadi terkunci menunggu — padahal temuan Fase 1
sudah di depan mata. Pengaman itu perlu jadi **per fase**, bukan global.

**3. Warna asli tersimpan di memori panel, dan analisis kini panjang.**
Sudah tercatat sebagai batas yang diketahui di Fase 1. Tapi dengan analisis
berjalan menit, kemungkinan Word ditutup di tengah jalan naik banyak. Kandidat
penyelesaiannya — custom XML part — jadi lebih layak dibangun di Fase 2
daripada ditunda lagi.

**4. Beban penyamaan keterangan naik jadi tiga berkas per aturan.**
Tiap aturan `F2-*` harus muncul di `konsistensi.py`, `aturan-fase2.ts`, **dan**
`cek list fase 1.md`. Di Fase 1 sudah dua dan sempat tidak sinkron. Layak
dipikirkan apakah keterangan aturan sebaiknya dibangkitkan dari satu sumber,
seperti `KUNCI-UJI.md` yang dibangkitkan skrip.

**5. Temuan AI yang menyisipkan usulan hijau membalik penundaan Fase 1.**
`fase1 drafter.md` bagian 4 sengaja menunda keputusan itu sampai Fase 1
terbukti, dan uji Word Fase 1 belum dijalankan. Keputusannya sudah diambil dan
rancangan ini mengikutinya — dengan tiga syarat di Langkah 4–5. Dicatat di sini
supaya jelas bahwa urutannya memang dibalik, bukan terlewat.
