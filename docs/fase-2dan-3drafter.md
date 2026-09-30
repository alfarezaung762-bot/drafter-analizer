# Fase 2 & 3 — Rancangan

> **Acuan rancangan Fase 2 dan 3.** Alur lima tahap (bagian 3.1) dan
> susunan foldernya di `telaah/` (bagian 2) sudah dibangun.
> Acuan lain: `project-brief.md` 8.7–8.13 dan `fase1 drafter.md` untuk apa pun
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
tanpa tahu struktur dokumen. Dari lima tahap alurnya, **tiga dikerjakan kode
biasa** — gratis, hasilnya pasti, dan kalau salah bisa ditunjukkan barisnya —
sedangkan dua sisanya dikerjakan model yang membaca **naskah utuh**. Karena
berjalan menit dan berbayar, Fase 2 berjalan sesudah Fase 1 yang tetap
hitungan detik, dan jawaban model disimpan supaya proses yang terputus tidak
menghanguskan panggilan yang sudah dibayar. Temuannya masuk ke **saluran penandaan yang sama dengan
Fase 1** — merah dicoret, usulan hijau di sebelahnya, blok kuning, satu komentar
per temuan — jadi seluruh pengaman Fase 1 ikut berlaku tanpa dibangun ulang.
Kaidah yang mengikat semuanya: **tidak ada temuan yang boleh lahir sebelum tahap
memastikan** — dugaan yang lahir di tahap 3 tidak pernah menyentuh naskah
sebelum diuji ulang dan dibuktikan kutipannya. Fase 3 sendiri ada di balik gerbang keras, tidak dimulai sebelum Fase 2
memenuhi definisi selesainya.

---

## 2. Struktur folder

Ditata **per tahap**, bukan per lapisan teknis. Kaidah penamaannya satu:
**urutan abjad = urutan jalan.** Tahap yang berisi lebih dari satu berkas
diberi folder sendiri; nama folder tidak boleh diawali angka atau memakai
titik (batasan Python), jadi `tahap1_parser/`, bukan `1.parser/`.

```
backend/app/
├── __init__.py                PETA SELURUH BACKEND
│
├── telaah/                    Fase 2 dan 3 — lima tahap
│   ├── __init__.py               peta urutan tahap
│   ├── alur.py                   orkestrator — menjalankan tahap 1 sampai 5
│   ├── tahap1_parser/            kode
│   │   ├── struktur.py           pohon BAB › Pasal › ayat › huruf › angka
│   │   ├── definisi.py           daftar istilah Pasal 1
│   │   ├── rujukan.py            "sebagaimana dimaksud …" → pasal tujuannya
│   │   └── lampiran.py           bingkai lampiran + jenis tiap blok
│   ├── tahap2_persiapan/         kode, tanpa AI
│   │   ├── bahan.py              naskah utuh + fakta lampiran + ukur token
│   │   ├── mekanis_konsistensi.py  F2-001/003/004/007, langsung ke tahap 5
│   │   └── dasar_hukum.py        F3-002 — dasar hukum Mengingat dicek ke OpenSearch
│   ├── tahap3_cari_dugaan.py     AI · cari dugaan, fokus per jenis pemeriksaan
│   ├── tahap4_memastikan/        AI
│   │   ├── memastikan.py         uji tiap dugaan dengan naskah utuh
│   │   ├── alat.py               cari di naskah, buka tabel, jumlah kolom
│   │   ├── korpus_cari.py        F3-001 — cari peraturan pembanding
│   │   ├── korpus_pastikan.py    F3-001 — uji ulang dengan pembanding
│   │   └── korpus_rumusan.py     F3-003 — usulan dari peraturan berlaku
│   ├── tahap5_verifikasi.py      kode · gerbang terakhir, temuan lahir di sini
│   └── ekspor/                   alat pengembang — tahap1.py … tahap5.py
│
├── bersama/                   DIPAKAI LINTAS TAHAP — wajib tetap kecil
│   ├── prompt.py               PERAN + seluruh instruksi ke model — satu tempat
│   ├── llm.py                  SATU-SATUNYA pintu ke Azure OpenAI, termasuk alat
│   └── opensearch.py           SATU-SATUNYA pintu ke OpenSearch — HANYA MEMBACA
│
├── models/                  bentuk data, bukan aksi — temuan, satuan, pekerjaan
├── db/                      pekerjaan dan jawaban tahap 3; boleh tidak ada
├── rules/                   FASE 1, dan tabel rujukan KMK 527
├── api/                     analisis.py (Fase 1), analisis_lanjut.py (Fase 2/3 + ekspor)
└── core/config.py           + DATABASE_URL dan angka penyetelan

frontend/src/
├── lib/office.ts            pembacaan naskah dan seluruh penandaan
├── lib/aturan-fase2.ts      keterangan aturan untuk panel Pengaturan
├── lib/types.ts             disamakan dengan temuan.py
└── app/taskpane/page.tsx    kemajuan per tahap, penandaan per kelompok, ekspor
```

**Kenapa begini:**

| Berkas / folder | Kenapa begitu |
|---|---|
| `telaah/`, bukan `fase2/` + `fase3/` | OpenSearch kini bagian dari tahap persiapan (F3-002) dan memastikan (F3-001, F3-003), bukan fase tersendiri. Alasan pemisahannya dulu — Fase 3 di balik gerbang — cukup dijaga panel Pengaturan: pemeriksaan korpus mati secara bawaan |
| `tahap1_parser/` empat berkas, bukan satu parser | **Supaya gagalnya bisa sendiri-sendiri.** Kalau Pasal 1 tidak terbaca, pohonnya tetap sehat — yang diam cuma pemeriksaan definisi. Kalau disatukan, kegagalan kecil bisa disalahartikan sebagai kegagalan struktur, dan seluruh Fase 2 mati padahal tidak perlu |
| `mekanis_konsistensi.py` di `tahap2_persiapan/` | Ia tidak memanggil model: F2-0xx lahir di tahap 2 dan melompat langsung ke tahap 5 |
| `bersama/` | CLAUDE.md: panggilan ke layanan luar dikumpulkan di satu lapisan. **Aturan tegasnya:** hanya yang memanggil layanan luar atau mendefinisikan bentuk data boleh masuk sini. Tanpa aturan itu, `bersama/` jadi kode yang sebenarnya dan folder tahap cuma jadi kulit |
| `models/satuan.py`, bukan `telaah/satuan.py` | `Satuan` itu **bentuk data**, bukan aksi — sekelas dengan `temuan.py` |
| `db/simpanan.py`, bukan memanggil `sesi.py` langsung | Basis datanya **boleh tidak ada.** Kalau `DATABASE_URL` kosong, simpanan pindah ke memori dan Fase 2 tetap berjalan penuh — yang hilang cuma ketahanan terhadap restart. Penelaah yang mencoba add-in ini tidak perlu menyiapkan Postgres dulu, dan seluruh tes berjalan tanpa jaringan |
| `db/` menyimpan jawaban tahap 3, **bukan temuan** | Jawaban tahap 3 bagian yang mahal dan bisa dipakai ulang: kuncinya sidik pesan, jadi naskah yang sama tidak dibayar dua kali sesudah restart, sedangkan naskah yang berubah ditanyakan ulang. Temuan lahir di tahap 5 — kehilangannya cuma menuntut pemastian ulang |
| Penghitung token di `tahap2_persiapan/bahan.py` | Jumlah token sesungguhnya dikembalikan Azure di tiap jawaban dan dicatat `Ongkos`. Tetapi anggaran bahan dan Ekspor Tahap 2 butuh angkanya SEBELUM dikirim — jadi diukur dengan tokenizer gpt-4.1 (`tiktoken`) |
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
| `tiktoken` | mengukur bahan dengan tokenizer gpt-4.1 (o200k_base) sebelum dikirim; cadangannya huruf ÷ 3 kalau tidak tersedia |

**Yang sengaja TIDAK dipakai:**

| | Kenapa tidak |
|---|---|
| LangChain dsb. | alurnya sudah tetap lima tahap. Tidak ada yang perlu diputuskan model soal langkah mana berikutnya. Menambah lapisan berarti menambah tempat kesalahan bersembunyi |
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
FASE2_PASAL_PER_FOKUS         berapa pasal difokuskan dalam satu panggilan tahap 3
FASE2_ANGGARAN_TOKEN          di atas ini tabel data lampiran jadi kerangka
FASE2_PANGGILAN_BERBARENGAN   berapa panggilan jalan sekaligus
FASE2_AMBANG_SKOR             batas bawah temuan AI
```

Kelimanya **angka yang bisa diatur, bukan asumsi tertanam** — nilainya
ditetapkan setelah diukur pada dokumen nyata, dan ikut berubah kalau modelnya
diganti.

### 2.3 Basis data — Neon

Dipakai **Neon** (Postgres serverless), lewat SQLModel.

Yang disimpan cuma dua tabel:

```
Pekerjaan     id, dokumen, jenis, status, mulai, selesai, biaya
HasilPanggilan pekerjaan_id, kunci (sidik pesan), jawaban
```

**Yang TIDAK disimpan:** isi utuh naskah rancangan. Hanya jawaban model tiap
panggilan tahap 3 — yang memang bisa mengutip potongannya.

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

## 3. Alur — lima tahap

### 3.1 Alur utama

Dibangun 29 Sep 2026 (bug 7, C + D). Menggantikan tujuh langkah lama yang
menalar di atas peta ringkasan per satuan.

```
TAHAP 1  PARSER                                  kode · detik · gratis
         paragraf datar → pohon satuan berlabel: BAB › Pasal › (1) › a. › 1.
         label yang terpisah sel dari teksnya disatukan (naskah bertabel)
         lampiran → bingkai (kepala, penutup) + jenis fisik tiap blok:
                    teks / tabel / gambar / rumus / kerangka tabel raksasa
                    │
TAHAP 2  PERSIAPAN                               kode · detik · gratis
         ├─ BAHAN: SELURUH paragraf, satu baris per paragraf, bertanda id
         │   satuan — pembukaan dan batang tubuh SELALU utuh; tabel lampiran
         │   per baris sel; gambar dan rumus disebut tidak terbaca
         ├─ ukur token (tokenizer gpt-4.1): di atas anggaran ±100 rb, kelompok
         │   tabel DATA sejenis di lampiran jadi kerangka — teks tidak pernah
         ├─ fakta lampiran dikumpulkan kode: pasal yang menyebut "Lampiran",
         │   kata mirip "Lampiran", kepala dan penutup tiap lampiran
         └─ pemeriksaan kode, tanpa AI → langsung ke tahap 5:
            F2-001/003/004/007, dan F3-002 (korpus)
                    │
TAHAP 3  CARI DUGAAN                             model · beberapa panggilan
         tiap panggilan = NASKAH UTUH (sama persis, di depan) + tugasnya:
         ├─ per kelompok pasal (≤6 pasal) — F2-101, 102, 103
         │   tiap pasal fokus WAJIB dijawab; yang terlewat ditanya ulang
         ├─ lintas naskah — F2-104, 105, dan keberatan atas temuan Fase 1
         └─ lampiran — F2-106, dinilai dengan parameter tertulis
            KMK 527 butir 120–121 dan fakta dari kode
         keluar: DUGAAN — belum temuan
                    │
TAHAP 4  MEMASTIKAN                              model · satu per dugaan
         naskah utuh + satuan yang diuji, batang induknya, dan isi yang
         dirujuknya (dicari kode) + ALAT: cari teks di seluruh naskah,
         buka tabel, jumlah kolom
         klaim eksternal → korpus OpenSearch (F3-001), lalu usulan rumusan
         dari peraturan berlaku (F3-003)
                    │
TAHAP 5  VERIFIKASI                              kode · detik · gratis
         GERBANG TERAKHIR — satu-satunya tempat temuan lahir
         ✓ teks_asli ada di satuan itu (spasi saja yang dilonggarkan)
         ✓ nomor pasal yang disebut benar-benar ada
         ✓ istilah berdefinisi di usulan ditulis persis
         ✓ skor di atas ambang
         ✗ cuma menandai rujukan yang tujuannya ada?          → gugur
         ✗ menuduh istilah tak berdefinisi, padahal ada?      → gugur
         ✗ F2-101 tanpa dua tafsiran yang berbeda?            → gugur
         ✗ yang diklaim "tidak ada" ternyata ada di naskah?   → gugur
         ⇒ aturan + teks + tempat perbaikan sama di beberapa satuan
           → SATU temuan, sisanya di "Juga di"
```

Tahap 1, 2, dan 5 sengaja tanpa AI: hasilnya pasti, gratis, dan kalau salah
bisa ditunjukkan baris mana yang keliru. "Tidak ketemu di OpenSearch" tidak
pernah jadi temuan.

**Akurasi bahan di atas efisiensi (CLAUDE.md butir 13–15).** Salah tandai di
uji 27 Sep 2026 lahir dari teks yang tidak ikut terbawa ke model, bukan dari
model yang keliru menalar; pada PMK 119 seluruh definisi Pasal 1 tidak pernah
sampai. Karena itu bahan disusun dari seluruh paragraf, bukan dari teks
satuan hasil parser — paragraf yang tidak dikenali parser tetap terkirim,
mentah. Riwayatnya di `docs/perbaiki bug.md`.

**Harganya** tiap panggilan membawa naskah utuh: PMK 45 ±316 rb token masuk di
tahap 3 saja, jauh di atas peta lama. Kenopnya di `.env` —
`FASE2_PASAL_PER_FOKUS`, `FASE2_PANGGILAN_BERBARENGAN`, `FASE2_ANGGARAN_TOKEN`.

### 3.2 Di mana tiap fitur sekarang

Arti kode aturan yang disebut di bagian 2 — keterangan lengkapnya di panel
Pengaturan (`aturan-fase1.ts`, `aturan-fase2.ts`):

| Kode | Yang diperiksa | Oleh |
|---|---|---|
| F2-001 | Rujukan "sebagaimana dimaksud dalam Pasal N ayat (n)" menunjuk pasal/ayat yang ada | kode |
| F2-003 | Istilah yang didefinisikan di Pasal 1 benar dipakai di batang tubuh atau lampiran | kode |
| F2-004 | Nomor pasal dan ayat berurut, tidak melompat atau berulang | kode |
| F2-007 | Angka cocok dengan hurufnya — "30 (tiga puluh)" | kode |
| F2-101–105 | Makna ganda, pemikul kewajiban, wajib/dapat bertabrakan, dua ketentuan bertentangan, tujuan Menimbang tanpa ketentuan | AI |
| F2-106 | Lampiran dinyatakan di batang tubuh dan berformat baku (butir 120–121) | AI |
| F3-001 | Berpotensi bertentangan dengan peraturan lain | AI + OpenSearch |
| F3-002 | Dasar hukum di Mengingat sudah dicabut | kode + OpenSearch, tanpa AI |
| F3-003 | Usulan rumusan dicontoh dari peraturan yang masih berlaku | AI + OpenSearch |

**Fitur yang wajib tetap ada** — seluruhnya dipertahankan saat logika bug 7
dibangun dan saat dipindah ke `telaah/`:

| Fitur | Sebelum bug 7 | Sekarang |
|---|---|---|
| Pemeriksaan kode F2-001/003/004/007 | `mekanis_konsistensi` | `tahap2_persiapan/mekanis_konsistensi` |
| Pemeriksaan AI F2-101–105 | `tahap2_baca` → `tahap3_menalar` → `tahap4_*` | `tahap3_cari_dugaan` → `tahap4_memastikan/memastikan` |
| F3-001, F3-002, F3-003 | `fase3/tahap6_*` | `tahap2_persiapan/dasar_hukum`, `tahap4_memastikan/korpus_*` |
| Keberatan AI atas temuan Fase 1 ("Catatan AI" di komentar) | `tahap2_baca` | `tahap3_cari_dugaan`, panggilan lintas naskah |
| Temuan Fase 1 dilampirkan supaya AI tidak mengulangnya | `tahap2_baca` | di bahan tiap panggilan (`tahap2_persiapan/bahan`) |
| Batas 80 dugaan; id satuan/jenis karangan AI dibuang | `tahap3_menalar` | `tahap3_cari_dugaan` |
| Satu pasal tidak pernah dibelah antarpanggilan | `tahap2_baca` | `tahap3_cari_dugaan` (kelompok pasal fokus) |
| Aturan bisa dimatikan satu per satu di Pengaturan | `alur`, `tahap4_memastikan` | `alur`, tahap 3–4 — jenis yang mati tidak ditanyakan sama sekali |
| Kemajuan "x/y" di panel | per satuan, Langkah 2 | per panggilan (tahap 3) dan per dugaan (tahap 4) |
| Lanjut sesudah backend mati tanpa bayar ulang | tabel peta | tabel jawaban tahap 3, dikunci sidik pesan |
| Nomor Fase 2 melanjutkan Fase 1; batas 50 temuan | `alur` | `alur` |
| Naskah perubahan / KMK: pemeriksaan isi tidak jalan, alasannya disebut | `tahap0_struktur` | `tahap1_parser/struktur` |
| Seluruh verifikasi: kutipan persis, hijau berbukti, gabung kembar, dll. | `tahap5_verifikasi` | `tahap5_verifikasi` |

**Yang sengaja hilang:** peta ringkasan dan penalaran di atas peta (diganti
naskah utuh); penyaring Langkah 1 berikut daftar "dibuang penyaring" (tidak
ada lagi satuan yang dibuang); ekspor peta; cabang "satuan terlalu panjang".

### 3.3 Cabang — tabrakan antar-pasal

Terjadi di **tahap 3, panggilan lintas naskah** — pertanyaan yang memang
memandang seluruh naskah sekaligus.

Contoh: **Pasal 1 vs Pasal 17.**

> **Pasal 1 angka 8** — "Hari adalah hari kerja."
> **Pasal 17 ayat (1)** — "…diselesaikan paling lambat 30 (tiga puluh) hari
> kalender."

```
TAHAP 3     panggilan lintas naskah melihat dua satuan berbenturan:
            pasal-1-angka-8   mendefinisikan "Hari" = hari kerja
            pasal-17-ayat-1   memakai "hari kalender"
            → DUGAAN TABRAKAN, menyebut DUA alamat sekaligus
                    │
TAHAP 4     MEMASTIKAN VERSI TABRAKAN
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
TAHAP 4     MENENTUKAN SISI YANG MENYIMPANG
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
TAHAP 5     teks_asli = "30 (tiga puluh) hari kalender"
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

### 3.4 Cabang — bahan melewati anggaran

```
TAHAP 2     naskah + lampiran > ±100 rb token
                    │
            pembukaan, batang tubuh, teks lampiran, tabel kecil: TETAP UTUH
            kelompok tabel DATA sejenis di lampiran — kolomnya sama dan
            judul kolomnya sama — diringkas dari yang terbesar:
              judul kolom + jumlah baris + 3 baris contoh
            berhenti begitu bahan masuk anggaran; isinya tetap bisa
            dibuka model di tahap 4 lewat alat buka_tabel
```

Tabel di atas 1.000 baris (PMK 108/2024: 228 ribu baris) tidak dibaca panel
per paragraf — dikirim kerangkanya saja, dan isinya TIDAK bisa dibuka.
Paragraf sesudahnya bernomor urutan baca, bukan nomor Word, jadi temuan di
sana tampil di panel tanpa ditandai di naskah.

### 3.5 Cabang — rentang temuan tidak ketemu di naskah

```
TAHAP 5     teks_asli TIDAK ketemu persis
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

### 3.6 Cabang — pencarian korpus kosong

```
TAHAP 4     klaim eksternal, tapi pencarian korpus tidak menemukan apa pun
                    │
            TEMUAN TIDAK KELUAR SAMA SEKALI.
            Bukan "temuan tanpa rujukan" — brief 8.10: catatan hanya
            boleh menyebut yang ada di hasil pencarian.
```

### 3.7 Cabang — parser gagal

```
TAHAP 1     struktur tidak masuk akal (nol pasal padahal dokumen panjang,
            ayat di luar pasal, penomoran melompat belasan)
                    │
            SELURUH FASE 2 TIDAK DIJALANKAN, dan panel mengatakannya.
            Fase 1 tetap jalan seperti biasa.
            Diam lebih baik daripada memeriksa struktur yang salah baca.
```

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

**Tiga kelompok temuan — cara penelaah menilai hasil.** Milik penelaah
sendiri, bukan istilah teknis; pola temuan baru wajib masuk salah satunya.

| Kelompok | Di naskah |
|---|---|
| **1. Terbukti, bisa diperbaiki di sini** | merah dicoret + **hijau** di sebelahnya |
| **2. Terbukti, perbaikannya di tempat lain** | tetap ditandai, komentar + tombol Lompat ke Perbaikan (bentuk komentarnya masih pertanyaan terbuka di `fase4-merapikan-backend.md`) |
| **3. Sisanya** | blok kuning (kemungkinan), atau merah dicoret tanpa hijau (harus dihapus) |

Semua kartu punya Lompat ke Teks dan Terima/Tolak. Dua kejadian jarang di luar
tiga kelompok ini: *gagal ditandai* (rentang hilang saat mau ditandai — kartu
tetap ada, tanpa tanda di naskah) dan *keberatan AI* (model menempel catatan
pada temuan Fase 1 — nyaris tak pernah terjadi).

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

| Kode | Menemukan | Dibangun |
|---|---|---|
| F2-001 | Rujukan "sebagaimana dimaksud dalam Pasal N" ke pasal/ayat yang **tidak ada** | ✅ |
| F2-002 | Istilah berkapital yang **tidak ada** di daftar definisi Pasal 1 | ⏸ menunggu daftar pengecualian dari naskah nyata ("Menteri Keuangan", "Direktorat Jenderal") |
| F2-003 | Definisi di Pasal 1 yang **tidak pernah dipakai** | ✅ |
| F2-004 | Penomoran melompat atau berulang (Pasal 5 → Pasal 7; dua ayat (2)) | ✅ |
| F2-005 | Lampiran dirujuk tapi tidak ada, atau ada tapi tidak dirujuk | digantikan F2-106 — dinilai AI, karena bentuk lampiran terlalu beragam untuk regex |
| F2-006 | Urutan "Mengingat" tidak mengikuti hierarki | ⏸ |
| F2-007 | Bilangan yang angkanya tidak cocok dengan hurufnya — "30 (tiga belas)" | ✅ tambahan, tidak ada di rancangan awal |

### Fase 2 — penalaran, dengan AI

| Kode | Menemukan | Dibangun |
|---|---|---|
| F2-101 | Rumusan yang **bisa dibaca dua arah** | ✅ |
| F2-102 | Kewajiban **tanpa pemikul** yang jelas | ✅ |
| F2-103 | Kata operasional **bertabrakan** dalam satu ketentuan (wajib + dapat) | ✅ |
| F2-104 | **Dua ketentuan bertabrakan** — tidak bisa berlaku bersamaan. Keduanya dibaca utuh dalam satu panggilan | ✅ |
| F2-105 | Tujuan di Menimbang yang **tidak tercakup** batang tubuh | ✅ |
| F2-106 | **Lampiran** tidak dinyatakan di batang tubuh, atau kepala dan penutupnya tidak baku (butir 120–121) | ✅ bug 7 |

Urutan nomornya berubah dari rancangan awal: tabrakan dipindah ke F2-104
supaya ia bersebelahan dengan cabangnya sendiri (jalur tabrakan di
`tahap4_memastikan/memastikan.py`), dan
F2-101…103 jadi berisi penilaian atas SATU satuan saja. Tidak ada akibatnya
selain penomoran — tetapi kode, panel, dan tabel rujukan harus sepakat, dan
sekarang sepakat.

### Fase 3 — pembanding dari korpus

| Kode | Menemukan | Dibangun |
|---|---|---|
| F3-001 | **Berpotensi bertentangan** dengan peraturan lain yang masih berlaku. Butuh korpus + embedding + model | ✅ |
| F3-002 | Dasar hukum di Mengingat yang **sudah dicabut**. Butuh korpus saja — **tidak memanggil model, jadi gratis** | ✅ |

F3-002 berjalan **sebelum** penjaga struktur, dan itu disengaja: ia cuma
membutuhkan bagian Mengingat, yang terbaca utuh bahkan pada naskah yang batang
tubuhnya gagal diurai — KMK berdiktum, naskah perubahan, dan naskah
berpenomoran otomatis Word. Pada ketiganya Fase 2 diam, tetapi dasar hukumnya
tetap diperiksa.

Penomoran sengaja dibedakan: **`F2-0xx` deterministik, `F2-1xx` hasil
penalaran.** Penelaah berhak tahu mana yang pasti dan mana yang tebakan mesin —
dan itu terlihat dari kodenya sendiri.

### 4.3 Satu tombol, dan cara dua fase tidak bertabrakan

Ditetapkan penelaah 23 Sep 2026. **Satu tombol "Jalankan Analisis"**; panel
Pengaturan yang menentukan apa yang jalan. Penelaah tidak perlu tahu batas
fase untuk memakai alat ini — ia mencentang apa yang ingin diperiksa, alat
yang mengurus urutannya.

Paragraf dibaca sekali, lalu Fase 1 (detik) → ditandai segera → Fase 2/3
(menit) → ditandai per kelompok. Hasil Fase 1 tidak ditahan menunggu Fase 2.

Karena keduanya kini berjalan berurutan, keduanya bisa menemukan hal yang
sama. Penyelesaiannya: **AI membaca, kode yang memutuskan.**

| | Mekanisme | Siapa yang memutuskan |
|---|---|---|
| ① | Temuan Fase 1 ikut di bahan tiap panggilan, dengan larangan mengulang | model — duplikat tidak pernah lahir |
| ② | Calon yang rentangnya bertindihan dengan temuan yang sudah ada dibuang | **kode**, dengan perbandingan rentang |
| ③ | Model yang menilai sebuah temuan keliru menempelkan `catatan_ai` | penelaah membaca keduanya |

**Model tidak pernah menghapus temuan Fase 1.** Kesalahan Fase 1 bisa
dibuktikan baris demi baris; keyakinan model tidak bisa. Temuan yang hilang
diam-diam adalah kegagalan yang paling sulit diketahui penelaah.

### 4.4 Ekspor Tahap 1–5 — alat pengembang

Lima tombol di **paling bawah panel Pengaturan**, satu per tahap. Isinya apa
yang BENAR-BENAR dibaca atau diputuskan tahap itu — tanpa kepala, ringkasan,
atau penjelasan (ditetapkan penelaah 27–28 Sep 2026) — kecuali perkiraan
token di atas Tahap 2, yang memang diminta.

| | Isinya | Sumbernya |
|---|---|---|
| **Tahap 1** | pohon satuan, definisi Pasal 1, paragraf batang tubuh di luar teks satuan, dan lampiran berikut jenis tiap bloknya | disusun dari naskah saat itu — gratis, kapan saja |
| **Tahap 2** | perkiraan token per bagian, per panggilan tahap 3, dan per dugaan tahap 4; lalu bahan PERSIS yang ikut di tiap panggilan, dan fakta lampiran | idem |
| **Tahap 3** | pesan tiap panggilan cari dugaan, termasuk tanya ulang | disimpan saat analisis terakhir berjalan |
| **Tahap 4** | pesan tiap panggilan memastikan, **berikut tiap alat yang dipanggil model dan hasilnya** — hasil alat itu juga dibaca model | idem |
| **Tahap 5** | tiap dugaan tahap 3, hasil memastikannya, temuan yang lolos, dan yang gugur berikut alasannya | idem |

**Satu penyusun, jadi tidak bisa menyimpang.** Bahan Tahap 2 dirangkai fungsi
yang sama dengan yang mengirimnya ke model. Tesnya menuntut bahan di ekspor
SAMA PERSIS dengan yang ada di pesan tahap 3, bukan sekadar memuatnya.

**Tahap 3–5 tidak disusun ulang.** Sesudah ditandai, naskah di Word sudah
berisi coretan dan usulan hijau, jadi pesan yang disusun ulang dari naskah
sekarang bisa berbeda dari yang dulu dikirim. Pesannya disimpan di memori
backend saat tahapnya berjalan; sesudah backend dimulai ulang, ekspornya cuma
satu kalimat yang mengatakan pesannya tidak tercatat.

Juga tersedia tanpa Word: `cek_docx.py --tahap1`, `--tahap2`, dan
`--lanjut --tahap3`, `--tahap4`, `--tahap5`.

### 4.2 Hijau berarti terbukti, dan sumber penggantinya bisa ditunjuk

Ditetapkan penelaah 22 Sep 2026, **diperbarui 23 Sep 2026**. Yang berubah
bukan syarat buktinya, melainkan dari mana bukti penggantinya boleh datang:

> "kalo memang alat yakin itu salah rasanya aneh jika tidak memberikan saran
> perbaikan (karna itulah gunanya tahap 6 opensearch), kecuali kesalahannya
> mewajibkan itu di hapus baru boleh tidak memberikan saran perbaikan … tpi
> kalo memang benar benar tidak tau saran perbaikan lebih baik tidak perlu di
> munculkan"

| | Kapan dipakai | Yang terjadi di naskah |
|---|---|---|
| **Hijau** (`penggantian`) | salah terbukti, penggantinya bersumber jelas, **dan** penggantinya muat di tempat yang dicoret | teks lama merah dicoret, usulannya hijau di sebelahnya, sumbernya disebut di komentar |
| **Merah saja** (`penghapusan`) | salah terbukti, perbaikannya **membuang** | teks lama merah dicoret, tidak ada hijau |
| **Kuning** (`catatan`) | kemungkinan, atau penggantinya tidak diketahui | blok kuning saja, tidak ada yang dicoret |

Keputusan per aturan tertulis di `tahap5_verifikasi.py`, dan tidak seragam:
F2-001 terbukti tetapi penggantinya tidak bisa diketahui siapa pun; F2-003
perbaikannya membuang; F2-007 mana yang benar justru pertanyaan pokoknya;
F2-1xx boleh hijau **hanya** kalau rumusannya punya sumber — korpus (F3-003)
atau naskah itu sendiri; F2-106 selalu kuning;
F3-001 kemungkinan, bukan kesimpulan.

**Syaratnya ditegakkan kode, bukan niat baik.** Penilaian model atas dirinya
sendiri bukan bukti, jadi usulan F2-1xx tanpa `pembanding` turun jadi contoh
rumusan di komentar — persis seperti sebelum kebijakan ini berubah. Yang
dibuka bukan izin bagi model menulis ke naskah, melainkan izin bagi rumusan
yang sudah dipakai peraturan berlaku untuk masuk sebagai usulan.

Dan yang paling menentukan: empat pemeriksaan per-usulan di tahap 5 —
`periksa_usulan`, `cari_mirip`, `pasal_karangan`, dan rentang `lokasi` —
**tidak satu pun dilonggarkan**. Itulah yang sebenarnya mencegah naskah
rusak, bukan daftar aturan mana yang boleh hijau.

**Syarat terakhir: penggantinya wajib MUAT.** Ditetapkan 25 Sep 2026 sesudah
hijau pertama yang benar-benar dihasilkan korpus membuat ayatnya kehilangan
kata kerja:

```
dicoret : "penyelesaiannya dilakukan melalui rapat pembahasan"
usulan  : "rapat pembahasan yang diselenggarakan oleh unit kerja …"
jadinya : "… perbedaan pendapat …, rapat pembahasan yang …"   ← tanpa predikat
```

Panjangnya masuk akal dan ia tidak mengulang teks sebelumnya, jadi kedua
penjaga lama meloloskannya. Tandanya yang sebenarnya: **kata pertama yang
dicoret lenyap dari usulannya** — satu klausa diganti satu frasa. Berlaku
mulai coretan empat kata; di bawah itu frasa memang lazim diganti seluruhnya
("30 (tiga belas)" → "13 (tiga belas)").

Harganya diketahui dan diterima: usulan yang sengaja mengubah kalimat pasif
jadi aktif ikut tertahan, karena penjaga tidak bisa membedakannya dari yang
merusak. Yang tertahan **tidak hilang** — ia tetap ditulis di komentar sebagai
contoh rumusan. Pertukarannya: satu naskah rusak ditukar satu usulan bagus
yang pindah ke komentar.

Memeriksa satu contoh dengan tangan:
`python tools/cek_usulan.py --kalimat … --dicoret … --usulan …`

### 4.3 Tiap temuan menyebut ke mana perbaikannya

Muncul dari uji di Word: komentar menempel di Pasal 5 tempat frasanya
bermasalah, tetapi perbaikannya — menambah definisi — berada di Pasal 1, dan
penelaah tidak diberi tahu. Saran yang tidak menyebut tempatnya bukan saran,
melainkan keluhan.

Model mengisi `sasaran` dari **daftar tertutup**: `satuan ini`, `judul`,
`menimbang`, `mengingat`, `menetapkan`, `pasal-1`, atau id satuan mana pun.
Tahap 5 membuktikan tempat itu ada di pohon; yang tidak terbukti
**dikosongkan**, karena menunjuk Pasal 45 yang tidak ada lebih buruk daripada
diam soal tempat. Barisnya juga dilewati kalau sasarannya satuan tempat
komentar itu sendiri menempel.

Aturan mekanis tidak mengisinya sama sekali, dan itu kesimpulan: keempatnya
menandai persis tempat yang harus diperbaiki.

**Bentuk komentar di Word:**

```
Temuan:
Frasa 'analisis potensi' tidak dijelaskan ruang lingkupnya.

Perbaiki di: Pasal 1 (Ketentuan Umum)

Saran:
Tambahkan definisi 'analisis potensi' pada daftar istilah di Pasal 1.
Rumusan serupa: PMK 40 TAHUN 2024 (masih berlaku).

KMK 527/KMK.01/2022 Lampiran II (butir belum diisi) — https://jdih… (T2)
```

Tiga baris yang wajib ada, dan masing-masing menjawab pertanyaan penelaah
yang berbeda: **Perbaiki di** menjawab "di mana", **Saran** menjawab "apa",
dan **baris rujukan** paling bawah menjawab "atas dasar apa". Gunanya yang
terakhir disebut penelaah sendiri: supaya temuan bisa **ditimbang**, bukan
cuma dipercaya atau ditolak.

Baris `Saran` **dikosongkan** kalau penggantinya memang tidak diketahui.
Anjuran yang cuma mengulang masalahnya tidak menolong siapa pun.

### 4.6 Dasar KMK 527: kutipan, turunan, atau belum ada

Butir yang menopang tiap aturan ditelusuri 25 Sep 2026 dengan membaca **citra
halaman** KMK 527, bukan ekstraksi teksnya. Hasilnya membelah aturan Fase 2/3
jadi tiga, dan pembelahannya ditampilkan ke penelaah apa adanya:

| Keadaan | Penanda di panel | Contoh |
|---|---|---|
| Ada butir yang berbunyi persis demikian | tidak ada penanda | F2-003 (butir 61), F2-007 (butir 54j), F3-001 |
| Ada butir yang **akibatnya** demikian | "dasar turunan" | F2-001 (butir 54d hanya mengatur kapitalisasi acuan) |
| Tidak ada butirnya, sudah dicari | "rujukan belum diverifikasi" | F2-102, F2-103, F2-101 di luar Pasal 1 |

**Dasar F3-001 ternyata di Lampiran III, bukan Lampiran II** — itu sebabnya ia
tidak ketemu saat butir 1–132 ditelusuri. Huruf C angka 3 dan 4 mewajibkan
analisis terhadap peraturan yang lebih tinggi dan yang setingkat, dan angka 3b
serta 4b menegaskan analisisnya **tidak sebatas pada peraturan yang
mengamanatkan penyusunan**. Kalimat itulah pembenaran paling langsung untuk
pencarian korpus: syaratnya memang menuntut melihat di luar Mengingat, dan itu
tidak mungkin dituntaskan manual.

**Kenapa dibedakan.** Butir yang tertulis di komentar adalah dasar hukum yang
akan ditelusuri penelaah sendiri. Menuliskan `butir 54d` untuk aturan rujukan
menggantung berarti mengarang dasar — penelaah yang memeriksanya akan menemukan
butir tentang huruf kapital, dan kepercayaannya habis di situ. Maka butirnya
tetap disebut supaya bisa ditelusuri, tetapi statusnya mengatakan terang-terangan
bahwa ini turunan.

**Kekosongan dilaporkan, tidak ditambal.** F2-102 dan F2-103 sudah dicari di
Lampiran II dan tidak ketemu dasarnya. Keduanya tetap berjalan — aturannya
berguna — tetapi tidak mengaku bersumber KMK 527.

**F2-101 memakai dua dasar menurut letaknya** (sejak 27 Sep 2026). Butir 66
melarang pengertian ganda hanya pada **definisi** di Ketentuan Umum — untuk
temuan di Pasal 1 ia kutipan langsung. Di luar Pasal 1 dasarnya prioritas
penelaah: Lampiran II tidak punya bab ragam bahasa, dan butir 54a ("singkat,
jelas, dan lugas") cuma mirip. Dulu butir 66 tertulis di hampir setiap komentar
F2-101 di batang tubuh, sehingga penilaian model terbaca seperti kutipan.

### 4.1 Batasan

**Dari Word**

| | |
|---|---|
| **Penomoran otomatis tidak ikut terbaca** | lihat di bawah — batasan terbesar Fase 2 saat ini |
| **Naskah perubahan belum didukung** | lihat di bawah — dulu menghasilkan salah tandai |
| Tidak ada penghitung kata/karakter | dihitung sendiri dari teks yang sudah dibaca |
| `Word.search()` ~255 karakter | temuan lebih panjang tidak pernah ketemu → dipotong 120 karakter, warisan Fase 1 |
| Penandaan butuh teks **cocok persis** | keluaran model wajib diverifikasi kode (tahap 5) |
| Panel = halaman web di dalam Word | beban penggambaran jadi titik gagal |

**Dari model**

| | |
|---|---|
| Bentuk keluarannya tidak bisa dipercaya | prompt minta JSON ≠ dapat JSON. Validasi di kode |
| Bisa mengarang nomor peraturan | nomor wajib ada di pohon satuan atau di hasil pencarian |
| Hasilnya bisa berbeda tiap dijalankan | temuan AI wajib bisa dibedakan dari yang deterministik |
| Berbayar, dan modelnya akan diganti | ukuran potongan jadi angka yang bisa diatur |
| Ada kuota panggilan per menit | jumlah yang berbarengan dibatasi, dengan perlambatan otomatis |

**Dari korpus (Fase 3)** — diperiksa langsung 23 Sep 2026

Sampai tanggal itu isi indeks cuma diketahui dari keterangan lisan, dan
brief 8.12 menandai sendiri bahwa itu belum diverifikasi. Sesudah diperiksa,
**seluruh dugaan awal tentang bentuknya keliru.** Yang benar:

```
law_analyzer_emb3sm          18.543 dokumen peraturan
├── Judul, Nomor, Tahun, Bentuk, Status       ← PascalCase
└── Blocks[]                 nested — satu blok per pasal
    ├── Content              TEKS PASALNYA DI SINI
    ├── Pasal                "pasal-14"
    ├── Type                 "CONTENT_PASAL" | "DEFINISI" | …
    └── Chunks[]             nested — HANYA VEKTOR, tanpa teks
        └── MainVector       knn_vector 1536 dim
```

| | |
|---|---|
| **`index.knn` TIDAK menyala** | kueri `knn` biasa mengembalikan **nol hasil tanpa error** — diam yang tidak kelihatan. Jalan keluarnya `script_score` dengan `knn_score`: jarak dihitung persis, 0,5–1,7 detik untuk 18 ribu dokumen. Menyalakan `index.knn` berarti mengubah setelan indeks produksi yang sedang dipakai Law Analyzer — **dilarang** |
| Vektor di `Chunks`, teks di `Blocks` induknya | kuerinya bersarang dua tingkat, `inner_hits` diambil dari tingkat `Blocks`, supaya kutipan dan kecocokan makna menunjuk pasal yang **sama** |
| Teksnya hasil **OCR yang rusak** | kutipan wajib bawa penanda "belum diverifikasi" — mekanismenya sudah ada di `RujukanTemuan` |
| Memuat peraturan yang sudah dicabut | 2.466 dari 18.543 berstatus "Tidak Berlaku". Disaring **keras** di tingkat dokumen, bukan diturunkan skornya |
| Blok bukan-pasal ikut terambil | disaring `Blocks.Type = CONTENT_PASAL`; blok DEFINISI cocok secara makna tetapi tidak bisa dipertentangkan dengan ketentuan |
| Cakupannya | Peraturan Menteri Keuangan 6.243 · Peraturan Pemerintah 6.663 · Undang-Undang 2.555 · Peraturan Presiden 2.322, dan lainnya |
| Akses **baca saja** | hanya `_search`; tidak ada jalan ke `index`, `update`, `delete`, `_settings` |

**Naskah PERUBAHAN belum didukung**

PMK/KMK perubahan susunannya berbeda sama sekali: batang tubuhnya "Pasal I"
dan "Pasal II" (angka Romawi), dan di dalam Pasal I **dikutip pasal-pasal
milik peraturan induk** yang sedang diubah.

Akibatnya, sebelum ada penjaga, alat **salah tandai**: F2-001 menandai
"sebagaimana dimaksud dalam Pasal 18" sebagai rujukan menggantung, padahal
Pasal 18 memang ada — di peraturan induknya. Pohon satuannya juga keliru
(kutipan "Pasal 5" dibaca sebagai pasal dokumen ini), dan kekeliruan itu tidak
melaporkan dirinya.

Sejak 22 Sep 2026 naskah perubahan dikenali dari judul ("PERUBAHAN ATAS",
termasuk "PERUBAHAN KEDUA ATAS") atau dari "Pasal I" berangka Romawi, lalu
**Fase 2 menolak jalan sambil menyebut alasannya**. Fase 1 tetap berjalan
penuh — pembukaan naskah perubahan bentuknya sama saja.

**Rencana dukungannya — ditetapkan penelaah 23 Sep 2026, dikerjakan menyusul.**
Model wajib membaca pasal-pasal peraturan induk yang bersangkutan lewat
OpenSearch. Pondasinya sudah ada sejak Fase 3 jalan: indeks memuat `Blocks`
per pasal berikut teksnya, dan `PencariOpenSearch` sudah bisa menemukan sebuah
peraturan dari bentuk + nomor + tahun.

Yang perlu ditambahkan:

1. Baca nomor peraturan induk dari judul ("PERUBAHAN ATAS … Nomor 12 Tahun
   2024") — pembacanya sudah ada, `baca_kutipan`.
2. Ambil seluruh `Blocks` induknya dari korpus, susun jadi **pohon satuan
   kedua**.
3. Periksa rujukan terhadap **gabungan** kedua pohon: "Pasal 18" yang tidak
   ada di draf tetapi ada di induknya bukan rujukan menggantung.
4. Pasal yang diubah dibandingkan dengan bunyi lamanya, sehingga terlihat apa
   yang sebenarnya berubah.

Sampai itu ada, alat memilih diam — dengan suara.

**Penomoran otomatis Word — sudah diselesaikan 23 Sep 2026**

Dulu batasan terbesar Fase 2. Di naskah PMK yang ditulis dengan penomoran
otomatis Word, "BAB I", "Pasal 1", dan nomor ayat **bukan teks** — ketiganya
dihasilkan mesin penomoran, dan `paragraph.text` tidak memuatnya. Pada PMK 18
Tahun 2026: 585 dari 974 paragraf bernomor otomatis, 110 di antaranya teksnya
kosong sama sekali.

Akibatnya parser tidak menemukan satu pun Pasal, dan pada naskah yang Pasalnya
terbaca tetapi ayatnya tidak, F2-001 **salah tandai** — menuduh "Pasal 2
ayat (2) tidak ada" padahal jelas ada di layar.

**Jalan keluarnya:** `ListItem.listString` dan `ListItem.level` (WordApi 1.3)
dikirim sebagai **medan terpisah** `penanda`, bukan ditempel ke depan teks.
Alasannya menentukan: `lokasi.offset_mulai` dihitung terhadap teks paragraf,
dan Word tidak punya awalan "(2) " di teksnya — menempelkannya membuat seluruh
sorotan meleset sepanjang awalan itu. Parser membaca `ParagrafInput.utuh`
(penanda + teks); yang menghitung offset tetap membaca `teks`.

Hasilnya pada PMK 18: **599 satuan, 97 Pasal bernomor 1–97 berurutan, 123 ayat,
333 huruf**, nol salah tandai.

Satu akibat yang perlu diketahui: temuan yang teks aslinya seluruhnya berada di
dalam nomor otomatis — misalnya F2-004 yang menandai nomor pasal yang melompat
— tidak bisa ditandai, jadi aturannya memilih diam.

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
3. ~~**Bentuk index OpenSearch yang sebenarnya.**~~ **SUDAH DIJAWAB 23 Sep
   2026** — diperiksa langsung, hasilnya di bagian 4.1. Keterangan lisan
   "Dokumen → Blok, satu blok per pasal" ternyata benar, tetapi nama medannya
   dan letak vektornya sama sekali berbeda dari dugaan, dan `index.knn` yang
   mati membuat kueri baku diam-diam tidak menghasilkan apa pun.
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
dipikirkan apakah keterangan aturan sebaiknya dibangkitkan dari satu sumber.

**5. Temuan AI yang menyisipkan usulan hijau membalik penundaan Fase 1.**
`fase1 drafter.md` bagian 4 sengaja menunda keputusan itu sampai Fase 1
terbukti, dan uji Word Fase 1 belum dijalankan. Keputusannya sudah diambil dan
rancangan ini mengikutinya — dengan tiga syarat di tahap 4–5. Dicatat di sini
supaya jelas bahwa urutannya memang dibalik, bukan terlewat.

---

## 7. Istilah

Tujuh istilah yang dipakai berulang di dokumen ini.

| Istilah | Artinya |
|---|---|
| **Naskah datar** | Daftar paragraf apa adanya dari Word — potongan teks bernomor, tanpa hubungan antarbagian. Komputer tidak tahu paragraf mana isi pasal mana. Seperti buku tamu: nama berbaris, tidak ada yang tahu siapa keluarga siapa. **Cukup untuk seluruh Fase 1** |
| **Pohon satuan** dan **satuan** | Naskah yang sama sesudah diberi arti parser: BAB memuat Pasal, Pasal memuat ayat, ayat memuat huruf. Seperti silsilah keluarga. **Isi teksnya sama persis** — parser tidak mengubah satu huruf, ia cuma menambahkan pengetahuan tentang hubungannya. Satu kotak di pohon itu disebut **satuan** — bagian terkecil yang diperiksa, biasanya setingkat ayat. Istilahnya dari brief 8.9: *"Satuan pemeriksaan ayat/butir, bukan pasal"* |
| **Norma** | Aturan yang mengikat seseorang berbuat atau tidak berbuat. Punya subjek dan perbuatan. *"Pengguna Barang **wajib** melaporkan"* = norma. *"Barang Milik Negara adalah…"* = bukan, itu definisi. *"…mulai berlaku pada tanggal diundangkan"* = bukan, itu administratif |
| **Bahan** | Naskah utuh yang ikut di depan tiap panggilan tahap 3 dan 4, disusun dari SELURUH paragraf — satu baris per paragraf, bertanda id satuan. Menggantikan **peta** (satu baris ringkasan per satuan), yang dihapus 29 Sep 2026 karena ringkasannya kehilangan detail |
| **Dugaan** ≠ **Temuan** | **Dugaan** keluar dari tahap 3. Belum boleh menyentuh naskah. **Temuan** adalah dugaan yang sudah lolos tahap 4 (dipastikan dengan naskah utuh) dan tahap 5 (diverifikasi kode). Brief 8.9: *"kejanggalan pada tahap 2 masih berupa dugaan, belum temuan"* |
| **Klaim internal** ≠ **klaim eksternal** | Menentukan wajib-tidaknya pencarian. **Internal** = bisa dibuktikan dari dokumen ini saja (*"Pasal 47 tidak ada"*) → pencarian tidak perlu. **Eksternal** = menyentuh apa pun di luar dokumen (*"bertentangan dengan PMK 5/2023"*) → pencarian **wajib**, dan tanpa hasil pencarian temuannya tidak keluar |
| **Awalan tetap** | Bagian pesan yang **sama persis di setiap panggilan** untuk satu dokumen: aturan tetap lalu bahan. Ditaruh di paling depan supaya potongan harga awalan prompt berlaku, kalau deployment-nya mendukung; tugas tiap panggilan di belakangnya |
