# Drafter Analiser

Word Add-in + backend untuk menganalisis draft peraturan (PMK/KMK) terhadap
kaidah penyusunan dan regulasi terkait.

## Menjalankan Proyek

Buka dua terminal terpisah:

### Backend (Terminal 1)

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # isi nilai yang sesuai

uvicorn app.main:app --reload --port 8000
```

### Frontend (Terminal 2)

```bash
cd frontend
cp .env.example .env.local  # sesuaikan jika perlu

npm install
npm run dev -- -p 3000
```

Backend berjalan di `http://localhost:8000`, frontend di `http://localhost:3000`.

## Struktur Proyek

Mulai dari [indeks dokumentasi](docs/README.md). Untuk keputusan perilaku
penelaahan Fase 1 yang terbaru, baca
[Keputusan UX Penelaahan](docs/keputusan-ux-penelaahan-fase1.md) dan
[Rancangan Analisis–Terima–Ekspor](docs/rancangan-analisis-terima-ekspor.md).
