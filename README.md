# Drafter Analiser

Word Add-in (task pane) + backend FastAPI untuk memeriksa rancangan PMK/KMK
terhadap kaidah penyusunan peraturan KMK 527/KMK.01/2022 Lampiran II.

Penelaah membuka rancangannya di Word, memilih PMK atau KMK, menekan Analisis —
bagian yang perlu ditinjau langsung tertandai di dokumen itu juga, lengkap
dengan komentar dan rujukan butirnya. Fase 1 seluruhnya deterministik, tanpa AI.

## Menjalankan

Dua terminal terpisah.

**Backend**

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

**Frontend**

```bash
cd frontend
cp .env.example .env.local
npm install
npm run dev -- --experimental-https
```

Backend di `http://localhost:8000`, task pane di `https://localhost:3000`.

Add-in dipasang ke Word lewat registry — jalankan `pasang-addin.reg`, lalu
Word akan memuat `manifest.xml`.

## Tes dan diagnosa

```bash
cd backend
python -m pytest tests/ -q

# Menjalankan seluruh aturan terhadap sebuah .docx tanpa membuka Word
python tools/cek_docx.py tools/contoh/contoh-rancangan-uji.docx --jenis PMK
```

## Dokumentasi

Mulai dari [`docs/README.md`](docs/README.md).

Acuan rancangannya satu berkas: [`docs/fase1 drafter.md`](docs/fase1%20drafter.md).
Aturan kerja untuk agen coding ada di [`CLAUDE.md`](CLAUDE.md).
