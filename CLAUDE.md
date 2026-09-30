# CLAUDE.md

**Drafter Analiser** — Word Add-in (task pane, Next.js) + backend FastAPI yang
membantu penelaah di Biro Hukum Kementerian Keuangan memeriksa rancangan PMK/KMK
terhadap kaidah penyusunan peraturan (KMK 527/KMK.01/2022 Lampiran II).

**Fase 1 tidak memakai AI sama sekali.** Seluruh pemeriksaannya deterministik —
regex dan logika Python biasa.

**Fase 2 terbagi dua, dan pembagiannya menentukan.** F2-0xx deterministik
seperti Fase 1; F2-1xx dan F3-001 memakai Azure OpenAI dan OpenSearch. Apa pun
yang dihasilkan model tetap harus lewat tahap 5
(`backend/app/telaah/tahap5_verifikasi.py`) sebelum menyentuh naskah — itu
satu-satunya tempat Temuan lahir, dan tidak punya jalan pintas.

## Skop dan siapa penggunanya

**Skop saat ini: PMK biasa saja — bukan PMK perubahan/pencabutan, dan KMK
belum digarap.** Ditetapkan penelaah. Naskah perubahan pasalnya tidak berurut
dan menuntut dasar yang jauh lebih kuat sebelum diperlakukan seperti naskah
utuh; itu pekerjaan tersendiri, belum sekarang.

**Penggunanya penelaah Biro Hukum — bukan staf IT.** Mereka administrasi
perkantoran biasa, dan itu menentukan bentuk apa pun yang dibangun di sini.
Empat syarat yang wajib dipenuhi tiap kali menambah fitur atau aturan baru:

1. **Mudah dibaca** tanpa penjelasan tambahan dari siapa pun.
2. **Berbukti konkret** — dari dalam naskah sendiri, atau dari korpus eksternal
   (OpenSearch, peraturan lain yang berlaku). Tidak pernah tebakan model
   semata; lihat butir 3 di bawah.
3. **Mudah dinavigasi** — berpindah panel ↔ naskah wajib satu klik, tidak ada
   langkah tersembunyi yang harus dihafal orang yang bukan IT.
4. **Responsif** — penelaah tidak akan menunggu alat yang lambat. Tetapi
   kecepatan tidak pernah dibeli dengan ketepatan: yang didahulukan selalu
   akurasi AI membaca konteks. Lihat butir 13–15.

Kerangka tiga kelompok temuan yang dipakai penelaah sendiri untuk menilai hasil
(terbukti-bisa-diperbaiki-di-sini / terbukti-tapi-perbaikannya-di-tempat-lain /
sisanya) ada di `docs/fase-2dan-3drafter.md` bagian 3.8.

## Baca ini dulu

[`docs/fase-2dan-3drafter.md`](docs/fase-2dan-3drafter.md) — **acuan rancangan
Fase 2 dan 3.** Alur lima tahap, cabang-cabangnya, dan alasan tiap keputusan.
Baca sebelum menyentuh `app/telaah/`.

[`docs/fase1 drafter.md`](docs/fase1%20drafter.md) — **satu-satunya acuan
rancangan Fase 1.** Memuat apa yang dibangun, cara temuan ditampilkan di dokumen,
kontrak data, dan definisi selesai. Baca sampai habis sebelum mengubah kode.

[`docs/panduan-officejs.md`](docs/panduan-officejs.md) — API Word yang sudah
diverifikasi, dan jebakan yang sudah terbukti secara empiris.

[`docs/perbaiki bug.md`](docs/perbaiki%20bug.md) — **catatan bug**: yang
belum selesai berikut pilihan perbaikannya, dan tes penjaga bug yang sudah
selesai. Baca sebelum menyentuh parser
(`telaah/tahap1_parser/`), penyusun bahan untuk model
(`tahap2_persiapan/bahan.py`, `tahap3_cari_dugaan.py`, `tahap4_memastikan/`),
atau pembacaan dan penandaan di `office.ts` — bug di sana selalu kambuh
sesudah pembaruan.

[`docs/README.md`](docs/README.md) — indeks dan daftar berkas yang sudah dihapus
(jangan dicari, jangan dibuat lagi).

## Aturan yang tidak boleh dilanggar

### Ketepatan

1. **Apa pun yang ditandai alat ini wajib benar-benar salah.** Aturan yang tidak
   bisa membuktikan kesalahannya harus **dimatikan**, bukan diperhalus. Satu
   salah tandai merusak kepercayaan penelaah lebih cepat daripada sepuluh temuan
   benar membangunnya. Empat salah tandai sudah pernah terjadi di naskah nyata —
   riwayatnya di `fase1 drafter.md` bagian 6.10.
2. **Tiap aturan yang bisa kebablasan wajib punya batas kewajaran, dan di luar
   batas itu memilih diam.** Contoh yang sudah dipasang: judul Menetapkan lebih
   dari 60 kata → aturan diam; butir Menimbang tidak ketemu → diam.
3. **Setiap temuan wajib membawa rujukan yang bisa diperiksa**, diambil dari
   tabel tetap di `rules/rujukan_kmk527.py`. **Tidak boleh dikarang.** Selama
   butirnya masih `"..."`, panel menampilkan penanda "belum diverifikasi".
4. **Jangan menurunkan aturan dari hasil ekstraksi teks PDF KMK 527.**
   Salinannya hasil pemindaian dan OCR-nya rusak ("clan" untuk "dan", "MENTER!"
   untuk "MENTERI"). Aturan wajib diverifikasi manual dari naskah yang dibaca
   visual oleh manusia.

### Naskah orang

5. **Alat mengusulkan, penelaah yang memutuskan.** Usulan disisipkan sebagai
   teks hijau **di sebelah** teks aslinya; teks lama **tidak dihapus**, cuma
   diberi warna merah dan coretan. Dilarang: menghapus teks penelaah atas
   inisiatif kode, membuat tombol "terapkan semua", dan menyentuh rentang di
   luar `lokasi` temuan — **kecuali satu hal** (ditetapkan penelaah 30 Sep
   2026, berlaku sejak Fase 4): perbaikan yang tempatnya di satuan lain boleh
   disisipkan sebagai **satuan baru** — angka definisi, ayat, atau pasal — di
   tempat perbaikan yang terbukti ada. Teks lama tetap tidak disentuh, dan
   Tolak mencabut sisipannya bersih. Rinciannya di
   `docs/fase4-merapikan-backend.md` bagian 3.1 dan 5.6.
6. **Temuan yang rentang presisinya tidak ketemu tidak ditandai sama sekali** —
   bukan diperlebar ke satu paragraf. Pelanggarannya pernah terjadi sekali dan
   berakhir menimpa naskah.
7. **Seluruh penandaan berjalan dengan `changeTrackingMode = "Off"`**, lalu mode
   semula dikembalikan. Menandai selagi pelacakan menyala membuat tiap warna
   tercatat Word sebagai revisi `Formatted: Highlight` dan mengubur komentarnya.

### Office.js

8. **Office.js jarang muncul di data latih model** — model cenderung mengarang
   method yang tidak ada. Verifikasi tiap method ke
   `frontend/node_modules/@types/office-js/index.d.ts` sebelum menulis kode:
   `grep -n "namaMethod" -B 8 index.d.ts`.
9. **Requirement set didukung ≠ fitur diizinkan.** `isSetSupported` bisa
   melaporkan `true` sementara pemanggilannya melempar `NotImplemented` karena
   terkunci lisensi — sudah terbukti pada Critique. Tiap fitur baru wajib punya
   jalur cadangan runtime, bukan cuma pengecekan requirement set.

### Keamanan dan kebersihan

10. **Dilarang membaca isi `.env`.** Kalau perlu tahu variabel apa saja yang
    tersedia, baca `core/config.py`. Kredensial hanya hidup di backend, tidak
    pernah sampai ke browser.
11. **Jangan menulis apa pun ke basis data produksi JDIH/Law Analyzer.**
12. **Utamakan AI lewat alur `app/telaah/`; deterministik hanya kalau AI
    sama sekali tidak bisa.** Ini prinsip proyek, ditetapkan penelaah 29 Sep
    2026. **Urutan pilihannya**: kalau sebuah pemeriksaan bisa dikerjakan AI
    lewat proses di `telaah/` (cari dugaan → memastikan → verifikasi),
    kerjakan dengan AI. Regex dan logika biasa dipakai hanya untuk yang sama
    sekali tidak bisa dikerjakan AI. Hasil AI tetap wajib lolos tahap 5
    sebelum menyentuh naskah — butir 1–6 tetap berlaku.

### Konteks yang dibaca AI

Model menilai benar atas apa yang dikirim kepadanya. Tiga salah tandai di uji
27 Sep 2026 lahir dari teks yang **tidak ikut terbawa**, bukan dari model yang
keliru menalar — penjaganya di `docs/perbaiki bug.md`.

13. **Akurasi membaca konteks didahulukan di atas efisiensi.** Memangkas,
    meringkas, membuang label, atau membatasi panjang teks yang dikirim ke
    model hanya boleh kalau sudah terbukti tidak menghilangkan makna pada
    naskah nyata (`tools/contoh/tempat pmk/`). Begitu satu salah tandai terbukti
    lahir dari penyingkatan, penyingkatannya yang dicabut — bukan ditambal di
    prompt.
14. **Empat hal yang wajib selalu ikut**, karena masing-masing sudah pernah
    hilang dan melahirkan salah tandai:
    - **seluruh paragraf naskah**, termasuk yang tidak dikenali parser dan isi
      lampiran — bahan disusun dari paragraf, bukan dari teks satuan hasil
      parser. Pada PMK 119 seluruh definisi Pasal 1 tidak pernah sampai ke
      model; penjaganya `test_tahap2_bahan.py`;
    - **label penomoran** tiap satuan — "(1)", "a.", "1." — tanpa itu "huruf b"
      tidak bisa ditemukan di dalam teks;
    - **teks satuan yang dirujuk**, sampai tingkat huruf/angka, di SETIAP
      tahap yang menilai — termasuk tahap 4, tempat temuan lahir;
    - **seluruh butir Pasal 1** — butir yang gagal dibaca parser tetap dikirim
      mentah, tidak dibuang.
15. **Batas kewajaran membuat ATURAN diam, tidak pernah membuat MASUKAN
    berkurang.** Butir 2 mengatur kapan alat boleh bicara. Ia bukan izin
    membuang teks dari bahan yang dibaca model.

## Konvensi kode

- Logika pemeriksaan ditulis sebagai **fungsi murni** bebas framework — tanpa
  objek Request/Response, tanpa state global. Harus bisa dites tanpa
  menjalankan server.
- Route handler FastAPI setipis mungkin: parse input → panggil fungsi →
  kembalikan JSON.
- Komponen UI ditulis sebagai React polos. Hindari server component dan server
  action **di dalam komponen** — proyek ini akan dimigrasikan ke React + Vite.
- **Seluruh panggilan Office.js dikumpulkan di `frontend/src/lib/office.ts`.**
  Tidak tersebar ke komponen.
- Semua panggilan ke layanan luar (OpenSearch, Azure OpenAI) dikumpulkan di satu
  lapisan, tidak tersebar.
- Sebelum menambah dependency, periksa apakah kebutuhannya bisa dipenuhi yang
  sudah terpasang. Tailwind sudah ada — jangan tambah Bootstrap.
- Jangan hardcode URL backend; pakai `NEXT_PUBLIC_API_BASE_URL`.
- **Berkas keterangan wajib sama dengan kodenya**, dan diubah di commit yang
  sama kalau aturannya berubah:
  - `frontend/src/lib/aturan-fase1.ts` ←→ `backend/app/rules/format_baku.py`
  - `frontend/src/lib/aturan-fase2.ts` ←→
    `backend/app/telaah/tahap2_persiapan/mekanis_konsistensi.py` dan `JENIS` di
    `backend/app/bersama/prompt.py`
  - `docs/cek list fase 1.md` ←→ ketiganya. Daftar per bagian naskah, dibaca
    penelaah sambil menelaah.

  Keterangan yang bohong lebih berbahaya daripada tidak ada keterangan:
  penelaah memakainya untuk memutuskan apa yang perlu diperiksa manual. Cara
  membuktikan keduanya masih benar ada di bagian akhir `cek list fase 1.md`.

## Menjalankan

```bash
# Terminal 1 — backend
cd backend && .venv/Scripts/python.exe -m uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend
cd frontend && npm run dev -- --experimental-https

# Tes
cd backend && python -m pytest tests/ -q

# Diagnosa aturan terhadap sebuah .docx, tanpa Word
cd backend && python tools/cek_docx.py <berkas.docx> --jenis PMK
cd backend && python tools/cek_docx.py <berkas.docx> --struktur   # pohon satuan
cd backend && python tools/cek_docx.py <berkas.docx> --fase2      # F2-0xx, gratis
cd backend && python tools/cek_docx.py <berkas.docx> --tahap1     # hasil parser + lampiran, gratis
cd backend && python tools/cek_docx.py <berkas.docx> --tahap2     # perkiraan token + bahan persis untuk AI, gratis
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut     # + jalur AI, BERBIAYA
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --tahap3   # + pesan cari dugaan, persis
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --tahap4   # + pesan memastikan berikut hasil alat
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --tahap5   # + nasib tiap dugaan: lolos/gugur
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --fase3    # + korpus OpenSearch
# Naskah uji: tools/contoh/tempat pmk/ — satu naskah per perintah; PMK 108
# (tabel 2,6 juta token) terlalu berat untuk laptop pengembang.

# Baca butir KMK 527 dari CITRA halaman, bukan dari ekstraksi teks (butir 4)
cd backend && python tools/halaman_pdf.py "tools/contoh/527KMK.012022Kep 1.pdf" 45-47

# Satu usulan hijau: disisipkan ke naskah, atau turun jadi kuning?
# Tanpa --pasal/--istilah hanya syarat "muat di kalimat" yang diuji; dengan
# keduanya, syarat "punya sumber di naskah sendiri" ikut diuji.
cd backend && python tools/cek_usulan.py --kalimat "<ayat utuh>" \
    --dicoret "<yang dicoret>" --usulan "<teks pengganti>" \
    --pasal "<teks pasal yang memuatnya>" --istilah "<istilah Pasal 1>"
```

Alat pengembangan dipasang terpisah: `pip install -r requirements-dev.txt`.
Tidak satu pun dipanggil backend saat berjalan.
