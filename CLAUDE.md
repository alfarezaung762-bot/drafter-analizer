# CLAUDE.md

Proyek **drafter-analiser** adalah Word Add-in (task pane) + FastAPI backend yang
membantu legal drafter di Kementerian Keuangan menganalisis draft PMK/KMK
terhadap kaidah penyusunan peraturan dan regulasi terkait yang tersimpan di
OpenSearch. Analisis dilakukan campuran: aturan deterministik (regex/logika)
untuk hal yang pasti, dan Azure OpenAI untuk hal yang memerlukan pemahaman
konteks.

## Dokumentasi

- [`docs/keputusan-ux-penelaahan-fase1.md`](docs/keputusan-ux-penelaahan-fase1.md) - acuan utama perilaku penelaahan Fase 1; diprioritaskan bila bertentangan dengan rancangan lama
- [`docs/rancangan-analisis-terima-ekspor.md`](docs/rancangan-analisis-terima-ekspor.md) - alur Analisis–Terima–Ekspor: Terima menyimpan jejak revisi dan Ekspor membuat DOCX bersih terpisah tanpa pengguna menyetel Word
- [`docs/README.md`](docs/README.md) - indeks dan urutan baca dokumentasi

- [`docs/panduan-vibe.md`](docs/panduan-vibe.md) — konvensi dan aturan kerja
  di repo ini
- [`docs/panduan-officejs.md`](docs/panduan-officejs.md) — sumber kebenaran
  Office.js API dan hal-hal yang mudah keliru
- [`docs/konteks-hukum.md`](docs/konteks-hukum.md) — anatomi dokumen peraturan,
  hierarki penomoran, dan aturan bahasa hukum
- [`docs/konteks-sistem-existing.md`](docs/konteks-sistem-existing.md) — alur
  data dari JDIH ke OpenSearch, skema index, dan cara kerja pencarian
- [`docs/kontrak-data.md`](docs/kontrak-data.md) — bentuk data Temuan yang
  menjadi penghubung semua modul
