# Fase 2 & 3 — Rancangan

> **Rancangan, bukan perintah kerja.** Belum ada kode yang ditulis dari dokumen
> ini. Acuan: `project-brief.md` 8.7–8.13 dan `fase1 drafter.md` untuk apa pun
> yang menyangkut lapisan penandaan.

---

## 1. Ringkasnya

Fase 1 memeriksa **bentuk** naskah — kapital, tanda baca, kelengkapan bagian —
dan semuanya bisa dijawab regex. Fase 2 dan 3 menambah dua lapis di atasnya:
**Fase 2** memeriksa apakah dokumen konsisten dengan dirinya sendiri dan
ketentuannya jelas, jawabannya dicari dari dokumen itu sendiri; **Fase 3**
memeriksa apakah ada yang berpotensi bertentangan dengan peraturan lain,
pembandingnya dari korpus di OpenSearch. Keduanya berdiri di atas satu pondasi:
**parser** yang mengubah daftar paragraf datar jadi pohon satuan, karena
pertanyaan seperti *"apakah Pasal 12 yang dirujuk itu ada"* mustahil dijawab
tanpa tahu struktur dokumen. Dari tujuh langkah alurnya, **tiga dikerjakan kode
biasa** — gratis, hasilnya pasti, dan kalau salah bisa ditunjukkan barisnya —
sedangkan empat sisanya dikerjakan model. Karena berjalan menit dan berbayar,
Fase 2 ditekan **terpisah** dari Fase 1 yang tetap hitungan detik, dan hasilnya
disimpan per satuan supaya proses yang terputus tidak menghanguskan panggilan
yang sudah dibayar. Temuannya masuk ke **saluran penandaan yang sama dengan
Fase 1** — merah dicoret, usulan hijau di sebelahnya, blok kuning, satu komentar
per temuan — jadi seluruh pengaman Fase 1 ikut berlaku tanpa dibangun ulang.
Kaidah yang mengikat semuanya: **tidak ada temuan yang boleh lahir sebelum tahap
memastikan** — dugaan yang datang dari membaca ringkasan tidak pernah menyentuh
naskah. Fase 3 sendiri ada di balik gerbang keras, tidak dimulai sebelum Fase 2
memenuhi definisi selesainya.

---

## 2. Struktur folder

Ditata **per fase dan per tahap**, bukan per lapisan teknis. Disetujui
21 Sep 2026.

Kaidah penamaannya satu: **urutan abjad = urutan jalan.** Begitu foldernya
dibuka, daftarnya sudah tersusun sesuai alurnya sendiri — tanpa perlu membuka
apa pun.

```
backend/app/
│
├── __init__.py              PETA SELURUH BACKEND — dibaca sekali, tahu semuanya
│
├── fase2/                   konsistensi + kejelasan rumusan
│   ├── __init__.py             urutan tahapnya tertulis di sini
│   ├── tahap0_struktur.py      naskah datar  → pohon satuan
│   ├── tahap0_definisi.py      pohon satuan  → daftar istilah Pasal 1
│   ├── tahap1_saring.py        175 satuan    → yang memuat norma saja
│   ├── tahap2_baca.py          konteks tetap + satuan → satu baris peta
│   ├── tahap3_menalar.py       peta          → dugaan
│   ├── tahap4_memastikan.py    dugaan        → temuan, atau gugur
│   ├── tahap4_tabrakan.py      cabang: dua satuan dibaca sekaligus (3.2)
│   ├── tahap5_verifikasi.py    empat pemeriksaan sebelum jadi temuan
│   └── mekanis_konsistensi.py  F2-001…007 — DI LUAR jalur AI, langsung ke tahap5
│
├── fase3/                   pertentangan dengan peraturan lain
│   ├── __init__.py
│   ├── tahap6_cari.py          embedding → korpus → saring status berlaku
│   └── tahap6_pastikan_ulang.py  memastikan dengan pembanding di tangan
│
├── bersama/                 DIPAKAI LINTAS TAHAP — wajib tetap kecil
│   ├── prompt.py               PERAN + seluruh instruksi ke model — satu tempat
│   ├── llm.py                  SATU-SATUNYA pintu ke Azure OpenAI (chat + embedding)
│   └── opensearch.py           SATU-SATUNYA pintu ke OpenSearch — HANYA MEMBACA
│
├── models/                  bentuk data, bukan aksi
│   ├── temuan.py               + satuan_id, skor
│   ├── satuan.py               BARU — bentuk satu satuan
│   └── pekerjaan.py            BARU — BarisPeta, Dugaan, CalonTemuan, Pekerjaan
│
├── db/
│   ├── sesi.py                 sambungan Postgres, dan izin untuk tidak ada
│   ├── tabel.py                dua tabel: pekerjaan dan peta
│   └── simpanan.py             satu-satunya pintu tulis/baca yang dipakai kode lain
│
├── rules/format_baku.py     FASE 1 — TIDAK DISENTUH
├── api/analisis_lanjut.py   BARU — mulai, tanya status, ambil hasil
└── core/config.py           + DATABASE_URL dan empat angka penyetelan

frontend/src/
├── lib/aturan-fase2.ts      BARU — keterangan aturan untuk panel Pengaturan
├── lib/types.ts             disamakan dengan temuan.py
├── lib/office.ts            TIDAK DISENTUH — lapisan penandaan yang sudah terbukti
└── app/taskpane/page.tsx    + progres, kelompok fase, batas tampil, penandaan per kelompok
```

### Isi `fase2/__init__.py`

```python
"""Fase 2 — konsistensi dan kejelasan rumusan.

  tahap0_struktur      naskah datar  → pohon satuan       kode, gratis
  tahap0_definisi      pohon         → daftar istilah     kode, gratis
  tahap1_saring        175 satuan    → 135 yang bernorma  kode, gratis
  tahap2_baca          satuan        → baris peta         model
  tahap3_menalar       peta          → dugaan             model
  tahap4_memastikan    dugaan        → temuan / gugur     model
  tahap4_tabrakan      cabang dua satuan sekaligus        model
  tahap5_verifikasi    temuan        → lolos / turun      kode, gratis

  mekanis_konsistensi  F2-001…007 — di luar jalur AI, langsung ke tahap5
"""
```

**Kenapa masing-masing perlu ada:**

| Berkas / folder | Kenapa begitu |
|---|---|
| `fase2/` dan `fase3/` **dipisah** | Fase 3 ada di balik gerbang keras. Memisahkannya secara fisik membuat "Fase 3 belum dibangun" **terlihat sekilas** dari struktur foldernya, bukan cuma tertulis di dokumen |
| `tahap0_*` dua berkas, bukan satu | **Supaya gagalnya bisa sendiri-sendiri.** Kalau Pasal 1 tidak terbaca, pohonnya tetap sehat — yang diam cuma F2-002 dan F2-003. Kalau disatukan, kegagalan kecil di ekstraksi definisi bisa disalahartikan sebagai kegagalan struktur, dan seluruh Fase 2 mati padahal tidak perlu |
| `tahap4_tabrakan.py` terpisah dari `tahap4_memastikan.py` | Memastikan tabrakan menuntut **dua satuan dalam satu panggilan** (3.2) — bentuk panggilan yang berbeda dari memastikan biasa |
| `mekanis_konsistensi.py` **bukan** `tahap*` | Karena ia memang bukan tahap: F2-001…007 melompat langsung dari tahap1 ke tahap5, tanpa menyentuh model. Namanya harus mengatakan itu |
| `bersama/` | CLAUDE.md: panggilan ke layanan luar dikumpulkan di satu lapisan. `llm.py` dipakai tahap 2, 3, 4, **dan** 6 — menaruhnya di `tahap2_*` membuat tahap 6 meng-import dari tahap 2, yang terbaca mundur. **Aturan tegasnya:** hanya yang memanggil layanan luar atau mendefinisikan bentuk data boleh masuk sini. Tanpa aturan itu, `bersama/` jadi kode yang sebenarnya dan folder tahap cuma jadi kulit |
| `models/satuan.py`, bukan `fase2/satuan.py` | `Satuan` itu **bentuk data**, bukan aksi — sekelas dengan `temuan.py`. Menaruhnya di antara berkas `tahap*` mencampur dua jenis isi dalam satu folder, dan itulah yang membuat nama jadi susah dibaca sekilas |
| `db/simpanan.py`, bukan memanggil `sesi.py` langsung | Basis datanya **boleh tidak ada.** Kalau `DATABASE_URL` kosong, simpanan pindah ke memori dan Fase 2 tetap berjalan penuh — yang hilang cuma ketahanan terhadap restart. Penelaah yang mencoba add-in ini di mesinnya sendiri tidak perlu menyiapkan Postgres dulu, dan seluruh tes berjalan tanpa jaringan. Itu cuma mungkin kalau ada satu pintu yang menyembunyikan pilihan itu dari seluruh pemanggil |
| `db/` menyimpan peta, **bukan temuan** | Peta bagian termahal: Langkah 2 memanggil model puluhan kali. Backend yang mati di satuan ke-68 meninggalkan 68 baris yang sudah dibayar, dan analisis berikutnya meneruskan dari situ. Temuan lahir di Langkah 5 dari bahan yang sudah tersimpan — kehilangannya cuma menuntut penalaran ulang, bukan pembacaan ulang seluruh naskah |
| `token.py` **tidak jadi dibuat** | Jumlah token dikembalikan Azure di tiap jawaban, jadi menghitungnya sendiri berarti menebak angka yang sudah diberitahukan. Pencatatannya pindah ke `Ongkos` di `llm.py`, tempat angkanya datang |
| `tahap_konfirmasi` **tidak jadi ditambahkan** ke `Temuan` | Nilainya akan selalu sama untuk seluruh temuan Fase 2/3, karena Langkah 5 tidak punya jalan pintas. Field yang isinya bisa ditebak dari `fase` cuma menambah satu hal lagi yang bisa salah |
| `office.ts` **tidak disentuh** | Penandaan bertahap per kelompok dikerjakan pemanggilnya — panel memanggil `tandaiSemuaTemuan` sepuluh temuan sekali jalan. Lapisan penandaannya sendiri sudah terbukti di Fase 1 dan tidak punya alasan berubah |
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
           Berlaku HANYA untuk batang tubuh. Judul, Menimbang, Mengingat,
           dan definisi Pasal 1 TIDAK disaring — mereka masuk KONTEKS TETAP,
           jadi ikut terkirim di setiap panggilan.

           DILEWATI  "…mulai berlaku pada tanggal diundangkan."
           DIBACA    "Menteri wajib menetapkan … paling lambat 30 hari."
           RAGU      → DILOLOSKAN. Boros itu kesalahan yang kelihatan;
                       melewatkan pasal bermuatan norma tidak kelihatan
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
           GERBANG TERAKHIR sebelum sebuah temuan ada. Urutannya:
              klaim internal  :  4 → 5 → temuan
              klaim eksternal :  4 → 6 → 5 → temuan   ← 5 tetap paling akhir

           ✓ teks_asli ada PERSIS di satuan itu?
           ✓ nomor pasal yang dikutip benar-benar ada?
           ✓ istilah berdefinisi di usulan ditulis persis?
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

### 3.8 Yang dipilih penelaah, dan bentuk temuannya di naskah

**Penelaah yang menentukan apa yang dianalisis.** Panel Pengaturan yang sudah
ada sejak Fase 1 — kotak centang per aturan, berikut rincian "yang diperiksa"
dan "yang TIDAK diperiksa" — **diperluas memuat aturan Fase 2 dan 3**. Jadi
penelaah bisa mematikan satu pemeriksaan yang salah tandai tanpa menunggu
kodenya diperbaiki, dan bisa menjalankan pemeriksaan mekanis saja tanpa
menyalakan yang berbayar.

Itu sekaligus menjawab "apakah Fase 2 jalan otomatis": **yang jalan adalah apa
yang dicentang penelaah.** Alat ini membantu proses telaah — bukan mengambil
alih keputusan apa yang perlu ditelaah.

**Bentuk temuannya di naskah.** Yang membedakan merah-hijau dari kuning bukan
ada-tidaknya rujukan — keduanya selalu dapat rujukan dan tepat satu komentar.
Yang membedakan: ada-tidaknya **satu pengganti yang pasti**.

| Tanda | Dipakai bila | Menyentuh naskah? |
|---|---|---|
| **Merah dicoret + hijau** | ada satu rumusan pengganti harfiah yang pasti | ya — usulan disisipkan di sebelahnya |
| **Blok kuning** | tidak ada pengganti tunggal; alat tahu ada yang salah tapi tidak tahu sisi mana yang benar | tidak — hanya disorot |

**Temuan kuning tetap membawa saran.** Alat tidak tahu sisi mana yang harus
berubah, tetapi tetap bisa menunjukkan jalan keluarnya. Sarannya hidup di
`usulan_rumusan` dan **hanya ditampilkan di komentar, tidak pernah disisipkan**
— itu sudah jadi kontrak sejak Fase 1 bagian 11.

Komentar kuning karena itu tiga baris, bukan dua:

```
Memakai "hari kalender", sedangkan Pasal 1 angka 8 mendefinisikan Hari
sebagai hari kerja.
Saran: samakan dengan definisinya — "30 (tiga puluh) hari kerja" — atau
ubah Pasal 1 kalau yang dimaksud memang hari kalender.
KMK 527/KMK.01/2022 Lamp. II butir … — jdih.kemenkeu.go.id/… (T14)
```

Komentar merah-hijau tetap dua baris, karena usulannya sudah terlihat di naskah:

```
Kewajiban tidak menyebut pemikulnya; ayat (1) menugaskannya kepada
Pengelola Barang.
KMK 527/KMK.01/2022 Lamp. II butir … — jdih.kemenkeu.go.id/… (T7)
```

Temuan Fase 3 bentuknya sama, rujukannya peraturan pembanding, dan kutipannya
**wajib membawa penanda keandalan** karena teks korpus berasal dari OCR:

```
Berpotensi bertentangan dengan PMK 5/2023 Pasal 8 yang menetapkan batas
14 hari untuk permohonan sejenis.
Saran: selaraskan batas waktunya, atau sebutkan alasan perbedaannya.
PMK 5/2023 Pasal 8 (belum diverifikasi visual) — jdih.kemenkeu.go.id/… (T21)
```

Bahasanya selalu **"berpotensi bertentangan"**, bukan "bertentangan" — temuan
Fase 3 memang kemungkinan, bukan kesimpulan.

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
| **Penomoran otomatis tidak ikut terbaca** | lihat di bawah — batasan terbesar Fase 2 saat ini |
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

**Penomoran otomatis Word — batasan terbesar Fase 2 saat ini**

Di naskah PMK yang ditulis dengan penomoran otomatis Word, **"BAB I", "Pasal 1",
dan nomor butir definisi bukan teks.** Ketiganya dihasilkan mesin penomoran
Word, dan yang sampai ke add-in adalah paragraf yang teksnya kosong atau tanpa
nomornya. Bentuk penomorannya sendiri `"BAB %1"`, `"Pasal %1"`, dan `"%1."` —
jadi yang hilang persis penanda struktur yang dicari parser.

Ini bukan kasus aneh: PMK 18 Tahun 2026 yang sudah diundangkan ditulis begitu.

**Akibatnya:** pada naskah semacam itu parser tidak menemukan satu pun Pasal,
melapor gagal, dan **Fase 2 tidak dijalankan sama sekali.** Perilakunya benar
menurut kaidah proyek — memilih diam daripada menebak — tetapi diamnya jadi
permanen, bukan sesekali. Fase 1 tetap berjalan penuh, karena judul, Menimbang,
Mengingat, dan Menetapkan semuanya teks sungguhan.

**Jalan keluarnya sudah diketahui, dan sengaja ditunda.**
`Paragraph.listItemOrNullObject.listString` (WordApi 1.3, himpunan yang sama
dengan cakupan "Bagian Terpilih") mengembalikan nomor yang tampil apa adanya.
Menempelkannya di depan teks tiap paragraf berlist akan menyelesaikan
seluruhnya.

Yang membuatnya ditunda: `readParagraphs` dipakai **seluruh** aturan, termasuk
dua belas aturan Fase 1 yang sudah terbukti dan sudah ditutup dua belas salah
tandainya. Mengubah teks yang diterimanya berarti menguji ulang semuanya.
Diputuskan 22 Sep 2026 untuk dikerjakan **setelah** Fase 2 terbukti pada naskah
yang penomorannya diketik manual — supaya kalau ada yang bergeser, jelas mana
sebabnya.

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
4. **Berapa ambang skor bawaannya**, dan apakah tiga pilihan bernama sudah cukup
   bagi penelaah. Diukur setelah dipakai, bukan ditetapkan dari meja.
5. **Uji Word Fase 1 belum dijalankan.** Seluruh Fase 2 menumpang lapisan
   penandaan yang dibuktikan di situ.
6. **Kapan penomoran otomatis dibaca** (lihat 4.1). Selama belum, Fase 2 cuma
   bisa diuji pada naskah yang "Pasal 1"-nya diketik sebagai teks.

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
Tiap aturan `F2-*` harus muncul di `mekanis_konsistensi.py`, `aturan-fase2.ts`, **dan**
`cek list fase 1.md`. Di Fase 1 sudah dua dan sempat tidak sinkron. Layak
dipikirkan apakah keterangan aturan sebaiknya dibangkitkan dari satu sumber,
seperti `KUNCI-UJI.md` yang dibangkitkan skrip.

**5. Temuan AI yang menyisipkan usulan hijau membalik penundaan Fase 1.**
`fase1 drafter.md` bagian 4 sengaja menunda keputusan itu sampai Fase 1
terbukti, dan uji Word Fase 1 belum dijalankan. Keputusannya sudah diambil dan
rancangan ini mengikutinya — dengan tiga syarat di Langkah 4–5. Dicatat di sini
supaya jelas bahwa urutannya memang dibalik, bukan terlewat.

---

## 7. Istilah

Tujuh istilah yang dipakai berulang di dokumen ini.

| Istilah | Artinya |
|---|---|
| **Naskah datar** | Daftar paragraf apa adanya dari Word — potongan teks bernomor, tanpa hubungan antarbagian. Komputer tidak tahu paragraf mana isi pasal mana. Seperti buku tamu: nama berbaris, tidak ada yang tahu siapa keluarga siapa. **Cukup untuk seluruh Fase 1** |
| **Pohon satuan** dan **satuan** | Naskah yang sama sesudah diberi arti parser: BAB memuat Pasal, Pasal memuat ayat, ayat memuat huruf. Seperti silsilah keluarga. **Isi teksnya sama persis** — parser tidak mengubah satu huruf, ia cuma menambahkan pengetahuan tentang hubungannya. Satu kotak di pohon itu disebut **satuan** — bagian terkecil yang diperiksa, biasanya setingkat ayat. Istilahnya dari brief 8.9: *"Satuan pemeriksaan ayat/butir, bukan pasal"* |
| **Norma** | Aturan yang mengikat seseorang berbuat atau tidak berbuat. Punya subjek dan perbuatan. *"Pengguna Barang **wajib** melaporkan"* = norma. *"Barang Milik Negara adalah…"* = bukan, itu definisi. *"…mulai berlaku pada tanggal diundangkan"* = bukan, itu administratif |
| **Peta** | Hasil Langkah 2: satu baris ringkasan per satuan, bukan teks penuhnya. 175 satuan jadi beberapa ribu token — **muat dikirim sekaligus di Langkah 3, sementara teks penuhnya tidak.** Itu seluruh alasan peta ada. Tempatnya: tabel `HasilSatuan` |
| **Dugaan** ≠ **Temuan** | **Dugaan** keluar dari Langkah 3, dari membaca peta. Belum boleh menyentuh naskah. **Temuan** adalah dugaan yang sudah lolos Langkah 4 (dibaca utuh) dan Langkah 5 (diverifikasi kode). Brief 8.9: *"kejanggalan pada tahap 2 masih berupa dugaan, belum temuan"* |
| **Klaim internal** ≠ **klaim eksternal** | Menentukan wajib-tidaknya pencarian. **Internal** = bisa dibuktikan dari dokumen ini saja (*"Pasal 47 tidak ada"*) → pencarian tidak perlu. **Eksternal** = menyentuh apa pun di luar dokumen (*"bertentangan dengan PMK 5/2023"*) → pencarian **wajib**, dan tanpa hasil pencarian temuannya tidak keluar |
| **Konteks tetap** | Bagian prompt yang **sama persis di setiap panggilan** untuk satu dokumen: judul, Menimbang, Mengingat, seluruh definisi Pasal 1, dan kerangka pasal. Kecil dan berulang — ditaruh di paling depan supaya potongan harga awalan prompt berlaku, kalau deployment-nya mendukung |
