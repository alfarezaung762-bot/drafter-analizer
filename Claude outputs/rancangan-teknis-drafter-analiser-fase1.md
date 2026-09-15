# Rancangan Teknis — Drafter Analiser (Build Pertama: Fase 1)

> Dokumen ini untuk ditempel ke agen coding (Antigravity / Claude Code) sebagai
> instruksi kerja. Disusun dari `project-brief.md`, `pemahaman-jdih-law-analyzer.md`,
> berkas env Law Analyzer/JDIH, dan kerangka repo `drafter-analiser` yang sudah ada.

## 0. Asumsi yang diambil (tolong dikoreksi bila keliru)

Beberapa keputusan di bawah ini aku ambil sendiri berdasarkan bukti di dokumen,
bukan konfirmasi langsung darimu. Ditandai di sini supaya jelas mana yang perlu
dicek ulang:

| Keputusan | Dasar | Status |
|---|---|---|
| Build pertama ini **cuma Fase 1** (pemeriksaan format baku, tanpa AI sama sekali) | `project-brief.md` bagian 7 "Urutan pengerjaan" eksplisit menyarankan urutan ini | Sesuai dokumen |
| UI pakai **Tailwind polos** (bukan Bootstrap) | Frontend kerangka sudah terpasang Tailwind v4 (`package.json`); `panduan-vibe.md`: "sebelum menambah dependency baru, periksa dulu apakah kebutuhannya bisa dipenuhi yang sudah ada" | **Koreksi atas permintaanmu** — Bootstrap tidak dipakai, lihat §10 |
| Target skala: **puluhan pengguna internal**, bukan ratusan | `project-brief.md` §8.12: cakupan pengguna saat ini dibatasi ke satu bagian (Bagian Hukum Kekayaan Negara dan Informasi Hukum) | **Koreksi atas permintaanmu** — lihat §10 |
| Fase 1 **tidak memakai model LLM apa pun** (bukan ChatGPT, bukan Azure OpenAI) | Semua item Fase 1 adalah aturan pasti (kapital/tidak, ada/tidak) — `project-brief.md` §8.8 dan prinsip "sederhana dahulu" | **Koreksi atas contohmu ("model llm - chatgpt")** — lihat §5 |

Kalau salah satu asumsi ini tidak sesuai maksudmu, bilang saja — tinggal ganti
bagian yang relevan.

---

## 1. Judul

**Drafter Analiser — Fase 1: Pemeriksaan Format Baku**

## 2. Apa yang dibangun & tujuan

Add-in Word (task pane) yang membaca rancangan PMK/KMK yang sedang terbuka di
Word, memeriksa kelengkapan dan kebenaran format bakunya secara otomatis
(tanpa AI, aturan pasti), lalu menyorot bagian bermasalah langsung di dokumen
disertai catatan penjelas — tanpa mengubah satu karakter pun isi dokumen.

Tujuannya bukan "selesai dibangun", tapi benar-benar dipakai penelaah Biro
Hukum untuk mempercepat kesalahan yang selama ini paling sering lolos dari
mata manusia: judul tidak konsisten, struktur Menimbang/Mengingat/Menetapkan
tidak lengkap, frasa baku yang hilang.

## 3. Fitur Fase 1 & masalah yang diselesaikan

| Fitur | Masalah yang diselesaikan | Cara kerja |
|---|---|---|
| Baca paragraf dokumen yang sedang terbuka di Word | Sekarang penelaah membaca manual satu-satu; gampang lolos di dokumen panjang (PMK 124/2024 = 175 satuan pasal/ayat) | Office.js membaca paragraf langsung dari dokumen aktif, tanpa upload berkas |
| Cek judul pembuka = judul di "Menetapkan" | Kesalahan paling sering terjadi (`project-brief.md` §8.6) — beda satu kata saja lolos | Bandingkan teks judul di dua lokasi, string match |
| Cek kelengkapan Menimbang / Mengingat / Menetapkan | Struktur wajib yang kadang terlewat | Cari heading/pola baku tiap bagian |
| Cek frasa baku pada butir Menimbang terakhir ("perlu menetapkan … tentang …") | Sering hilang atau salah bentuk | Pencocokan pola teks pada butir terakhir Menimbang |
| Cek ejaan | Typo lolos saat buru-buru | Pemeriksa ejaan bahasa Indonesia (regex/kamus, bukan AI) |
| Tandai bagian bermasalah dengan warna sesuai keparahan | Hasil analisis Law Analyzer sekarang terputus dari dokumen kerja — harus disalin manual (`project-brief.md` §2) | Office.js: `Word.run` + `range.font.highlightColor` |
| Tampilkan catatan penjelas saat bagian yang disorot ditunjuk | Penelaah perlu tahu *kenapa* ditandai | Task pane menampilkan detail temuan saat sorotan diklik |
| Terima / tolak tiap temuan | Prinsip proyek: alat memberi rekomendasi, tidak pernah mengubah naskah sendiri | Tombol terima/tolak per temuan di task pane |
| Ubah temuan yang diterima jadi komentar permanen | Supaya bisa dibawa ke rapat pembahasan | Office.js: `range.insertComment()` |
| Pilih cakupan: seluruh dokumen atau bagian terpilih | Fleksibilitas penelaah | Office.js: cek `document.getSelection()` vs seluruh body |

## 4. Di luar cakupan build ini (jangan dikerjakan agen coding)

Eksplisit dari `project-brief.md` bagian "Di Luar Lingkup" dan cakupan Fase 2/3:

- Mengubah teks dokumen secara otomatis
- Validasi gambar logo Garuda
- Deteksi "kelaziman" bahasa
- Versi untuk masyarakat umum (di luar Biro Hukum)
- Menulis apa pun ke basis data produksi JDIH/Law Analyzer
- Pencarian pembanding ke OpenSearch (itu Fase 3)
- Pemeriksaan yang butuh penalaran AI (itu Fase 2) — definisi konsisten,
  potensi multitafsir, dll.

Kalau agen coding mengusulkan salah satu di atas, itu di luar scope — tolak.

## 5. Arsitektur & environment

```
Word (dokumen terbuka)
  └── Task pane (Next.js)  ──baca/tulis paragraf via Office.js──┐
                                                                  ▼
                                                          Backend (FastAPI)
                                                          aturan deterministik saja
                                                          (regex / logika Python murni)
                                                                  ▼
                                                          daftar temuan (JSON)
                                                                  ▼
                                          Task pane menyisipkan sorotan via Office.js
```

- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind v4 (sudah
  terpasang di kerangka — jangan diganti). Office.js untuk integrasi Word.
- **Backend**: FastAPI (Python), aturan Fase 1 ditulis sebagai fungsi murni,
  bebas framework, sesuai `docs/panduan-vibe.md`.
- **Model AI**: **tidak dipakai sama sekali di Fase 1.** Semua pemeriksaan di
  §3 punya jawaban pasti, jadi tidak butuh LLM. (Kalau nanti masuk Fase 2,
  yang dipakai adalah **Azure OpenAI** — deployment `gpt-4.1` untuk penjawab
  dan `gpt-4o-mini`/embedding model untuk pencarian, sesuai env Law Analyzer
  di §9 — bukan ChatGPT konsumen.)
- **OpenSearch**: tidak dipakai di Fase 1. Baru relevan di Fase 3 (pencarian
  pembanding peraturan).
- **Penyimpanan**: tidak ada database produksi yang ditulis. State cukup
  disimpan di memori/sesi task pane selama dokumen terbuka (lihat catatan
  "Yang masih perlu dipastikan" di §11 soal riwayat temuan lintas sesi).

## 6. Susunan file (kondisi kerangka repo saat ini)

```
drafter-analiser/
├── backend/
│   ├── app/
│   │   ├── main.py            ← sudah ada: FastAPI app + CORS + /health
│   │   ├── core/config.py     ← sudah ada: Settings (OpenSearch, Azure OpenAI)
│   │   ├── api/                ← KOSONG, isi di sini (lihat §7)
│   │   ├── rules/               ← KOSONG, isi aturan Fase 1 di sini
│   │   ├── models/              ← KOSONG, isi skema Temuan di sini (§8)
│   │   ├── services/            ← KOSONG (belum dipakai di Fase 1)
│   │   ├── parser/              ← KOSONG (belum dipakai di Fase 1)
│   │   ├── llm/                 ← KOSONG (belum dipakai di Fase 1)
│   │   └── retrieval/           ← KOSONG (belum dipakai di Fase 1)
│   ├── requirements.txt
│   └── tests/
└── frontend/
    └── src/app/
        ├── page.tsx
        ├── layout.tsx
        └── taskpane/page.tsx   ← sudah ada, kerangka kosong — isi UI di sini
```

## 7. Penjelasan backend ↔ frontend (path ===> fungsi)

```
backend/app/main.py
  ===> daftarkan router di sini: app.include_router(analisis.router)

backend/app/api/analisis.py            [BARU]
  ===> endpoint POST /analisis/jalankan
       terima daftar paragraf dari task pane, panggil fungsi di rules/,
       kembalikan daftar Temuan (JSON, bentuk lihat §8)

backend/app/rules/format_baku.py       [BARU]
  ===> fungsi murni Python, satu fungsi per jenis pemeriksaan di §3:
       cek_judul_konsisten(), cek_kelengkapan_struktur(),
       cek_frasa_baku_menimbang(), cek_ejaan()
       tidak boleh ada objek Request/Response di sini (aturan panduan-vibe.md)

backend/app/models/temuan.py           [BARU]
  ===> skema Pydantic bentuk Temuan (§8) — ini yang jadi kontrak
       kontrak-data.md, harus ditetapkan sebelum rules/ ditulis

frontend/src/app/taskpane/page.tsx
  ===> UI task pane: tombol "Analisis", daftar temuan ringkas,
       panggil fetch("http://localhost:8000/analisis/jalankan")

frontend/src/lib/office.ts             [BARU, disarankan]
  ===> kumpulkan semua panggilan Office.js di satu tempat
       (baca paragraf, sisipkan highlight, sisipkan comment)
       — biar tidak tersebar di banyak komponen
```

## 8. Bentuk data Temuan (usulan — ini yang harus disepakati dulu sebelum kode lain ditulis)

`docs/kontrak-data.md` di kerangkamu masih kosong padahal menurut file itu
sendiri ini prasyarat sebelum modul lain ditulis. Ini usulan awal, disusun
dari field yang disebut berulang di `project-brief.md` (catatan, sitasi,
tautan JDIH, usulan rumusan, tingkat keparahan):

```json
{
  "id": "f-001",
  "jenis_pemeriksaan": "judul_konsisten",
  "fase": 1,
  "tingkat_keparahan": "tinggi",
  "lokasi": {
    "paragraf_index": 3,
    "teks_asli": "PERATURAN MENTERI KEUANGAN TENTANG ..."
  },
  "catatan": "Judul pembuka berbeda dengan judul pada bagian Menetapkan.",
  "usulan_rumusan": "PERATURAN MENTERI KEUANGAN NOMOR ... TENTANG ...",
  "rujukan": null,
  "status": "belum_ditinjau"
}
```

Catatan: field `rujukan` (nomor peraturan/pasal/tautan JDIH) baru terisi mulai
Fase 3 — di Fase 1 selalu `null` karena semua pemeriksaan format baku tidak
butuh pembanding peraturan lain. **Ini usulan, bukan keputusan final — perlu
kamu setujui atau ubah dulu sebelum agen coding mulai menulis `rules/`.**

## 9. Environment variables

**Peringatan penting:** nilai asli di bawah ini **tidak boleh** disalin ke
repo baru, ke chat manapun, atau ke agen coding. Yang boleh diketahui agen
coding hanya **nama variabelnya**, bukan isinya. Isi sebenarnya diminta
langsung ke admin/mentor lewat jalur aman saat deployment.

Fase 1 (build ini) **tidak butuh env tambahan** di luar yang sudah ada di
kerangka (`CORS origin`, port). Tabel di bawah untuk **Fase 2/3 nanti**,
disiapkan sejak awal supaya `core/config.py` tidak perlu dirombak ulang —
diambil dari env Law Analyzer (karena "memakai sumber daya yang sama"):

| Variabel | Dipakai untuk | Mulai fase |
|---|---|---|
| `OPENSEARCH_HOST`, `OPENSEARCH_PORT` | Alamat server pencarian | Fase 3 |
| `OPENSEARCH_USER`, `OPENSEARCH_PASSWORD` | Autentikasi OpenSearch | Fase 3 |
| `OPENSEARCH_INDEX` | Index teks pasal (leksikal) | Fase 3 |
| `OPENSEARCH_EMBEDDING_INDEX` | Index vektor (semantik) | Fase 3 |
| `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_API_VERSION` | Model penjawab (deployment task, mis. gpt-4.1) | Fase 2 |
| `AZURE_TASK_DEPLOYMENT` | Nama deployment model penjawab | Fase 2 |
| `AZURE_EMBEDDING_DEPLOYMENT` | Nama deployment model pengubah teks→vektor | Fase 3 |

Catatan jujur: nama variabel di `backend/app/core/config.py` kerangkamu
(`AZURE_TASK_DEPLOYMENT`) **tidak sama persis** dengan penamaan di env Law
Analyzer (`AZURE_OPENAI_TASK_DEPLOYMENT_NAME`). Ini perlu diselaraskan nanti
saat Fase 2 dimulai — belum masalah sekarang karena belum dipakai.

Tidak perlu `MINIO_*` sama sekali — tautan PDF (`pdf_url`) sudah ikut
terkirim dari OpenSearch (`pemahaman-jdih-law-analyzer.md` §1.4), jadi
Drafter Analiser tidak perlu mengambil berkas langsung dari MinIO.

## 10. Peraturan untuk agen coding

1. **Dilarang membaca isi file `.env`.** Kalau butuh tahu variabel apa saja
   yang tersedia, baca `core/config.py`, bukan `.env`.
2. **Kredensial hanya hidup di backend**, tidak pernah dikirim ke frontend/browser.
3. **Jangan pakai LLM untuk hal yang bisa diselesaikan regex/logika biasa** —
   ini prinsip proyek, bukan cuma saran (`panduan-vibe.md`).
4. **Alat memberi rekomendasi, tidak pernah mengubah naskah sendiri** —
   setiap fungsi yang menyentuh dokumen Word harus lewat jalur terima/tolak
   penelaah, tidak ada auto-apply.
5. **Setiap temuan yang punya rujukan wajib bisa diperiksa** (nomor
   peraturan, pasal, tautan JDIH) — dilarang mengarang.
6. **Jangan menulis ke basis data produksi JDIH/Law Analyzer.**
7. **Jangan menurunkan aturan dari hasil ekstraksi teks PDF KMK 527/PMK 164**
   — salinannya hasil OCR yang rusak. Aturan format harus diverifikasi
   manual dari naskah yang dibaca visual.
8. Sebelum menambah dependency baru, periksa dulu apakah kebutuhan itu bisa
   dipenuhi dengan yang sudah terpasang (Tailwind sudah ada — **jangan
   tambah Bootstrap**, itu kerja dua kali dan bertentangan dengan kerangka
   yang sudah berjalan).
9. Soal skala pengguna: cakupan resmi saat ini satu bagian internal
   (`project-brief.md` §8.12), bukan organisasi luas. Tulis kode yang wajar
   efisien (jangan proses paragraf berulang O(n²), jangan blocking UI
   thread saat analisis jalan) — tapi **jangan over-engineer** untuk skala
   ratusan pengguna simultan di build pertama ini; itu bertentangan dengan
   prinsip "sederhana dahulu".
10. Route handler FastAPI setipis mungkin: parse input → panggil fungsi di
    `rules/` → kembalikan JSON. Logika pemeriksaan sendiri harus jadi
    fungsi murni yang bisa dites tanpa menjalankan server.

## 11. Definisi selesai (build ini dianggap berhasil kalau)

- Task pane bisa dibuka di Word, membaca paragraf dokumen aktif
- Tombol "Analisis" memanggil backend, backend menjalankan 5 pemeriksaan di §3
- Hasilnya tersorot di dokumen dengan warna sesuai keparahan
- Klik sorotan menampilkan catatan + usulan rumusan di task pane
- Temuan bisa diterima (jadi comment permanen) atau ditolak (sorotan hilang)
- Berhasil diuji pada dokumen contoh yang panjang (bukan cuma dokumen pendek)

**Belum terjawab, jangan dianggap pasti** (`project-brief.md` §7 & §8.11):
daftar pemeriksaan Fase 1 di atas belum dikonfirmasi langsung ke penelaah
harian — sebagian masih dugaan dari logika dokumen. Rencanakan sesi validasi
dengan penelaah sebelum menganggap Fase 1 "selesai total".
