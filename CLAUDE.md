# CLAUDE.md

**Drafter Analiser** — Word Add-in (task pane, Next.js) + backend FastAPI yang
membantu penelaah di Biro Hukum Kementerian Keuangan memeriksa rancangan PMK/KMK
terhadap kaidah penyusunan peraturan (KMK 527/KMK.01/2022 Lampiran II).

**Fase 1 tidak memakai AI sama sekali.** Seluruh pemeriksaannya deterministik —
regex dan logika Python biasa.

**Fase 2 terbagi dua, dan pembagiannya menentukan.** F2-0xx deterministik
seperti Fase 1; F2-1xx dan F3-001 memakai Azure OpenAI dan OpenSearch. Apa pun
yang dihasilkan model tetap harus lewat Langkah 5
(`backend/app/fase2/tahap5_verifikasi.py`) sebelum menyentuh naskah — itu
satu-satunya tempat Temuan lahir, dan tidak punya jalan pintas.

## Baca ini dulu

[`docs/fase-2dan-3drafter.md`](docs/fase-2dan-3drafter.md) — **acuan rancangan
Fase 2 dan 3.** Alur tujuh langkah, cabang-cabangnya, dan alasan tiap
keputusan. Baca sebelum menyentuh `app/fase2/` atau `app/fase3/`.

[`docs/fase1 drafter.md`](docs/fase1%20drafter.md) — **satu-satunya acuan
rancangan Fase 1.** Memuat apa yang dibangun, cara temuan ditampilkan di dokumen,
kontrak data, dan definisi selesai. Baca sampai habis sebelum mengubah kode.

[`docs/panduan-officejs.md`](docs/panduan-officejs.md) — API Word yang sudah
diverifikasi, dan jebakan yang sudah terbukti secara empiris.

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
   luar `lokasi` temuan.
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
12. **Jangan pakai LLM untuk hal yang bisa diselesaikan regex atau logika
    biasa.** Ini prinsip proyek, bukan saran.

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
    `backend/app/fase2/mekanis_konsistensi.py` dan
    `backend/app/fase2/tahap4_memastikan.py`
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
cd backend && python tools/cek_docx.py <berkas.docx> --tahap0     # apa yang dibaca AI
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut     # + jalur AI, BERBIAYA
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --tahap3   # + peta & dugaan
cd backend && python tools/cek_docx.py <berkas.docx> --lanjut --fase3    # + korpus OpenSearch

# Baca butir KMK 527 dari CITRA halaman, bukan dari ekstraksi teks (butir 4)
cd backend && python tools/halaman_pdf.py "tools/contoh/527KMK.012022Kep 1.pdf" 45-47

# Satu usulan hijau: disisipkan ke naskah, atau turun jadi kuning?
cd backend && python tools/cek_usulan.py --kalimat "<ayat utuh>" \
    --dicoret "<yang dicoret>" --usulan "<teks pengganti>"
```

Alat pengembangan dipasang terpisah: `pip install -r requirements-dev.txt`.
Tidak satu pun dipanggil backend saat berjalan.
