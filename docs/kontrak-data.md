# Kontrak Data

## Bentuk Data Temuan — KONTRAK FINAL

> Bentuk ini menjadi penghubung semua modul, dan harus ditetapkan sebelum modul
> lain ditulis.

### Skema JSON

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

### Penjelasan field

| Field | Tipe | Keterangan |
|---|---|---|
| `id` | string | Identifier unik temuan dalam satu sesi analisis |
| `aturan_id` | string | Kunci ke tabel rujukan di kode (`F1-001`, dst.) |
| `fase` | integer | Selalu `1` untuk Fase 1 |
| `tingkat_keparahan` | enum string | `"tinggi"` \| `"sedang"` \| `"rendah"` |
| `lokasi.paragraf_index` | integer | Indeks paragraf dalam daftar yang dikirim |
| `lokasi.offset_mulai` | integer | Posisi karakter awal di dalam paragraf |
| `lokasi.panjang` | integer | Panjang karakter yang disorot |
| `lokasi.teks_asli` | string | Teks asli yang bermasalah |
| `catatan` | string | Penjelasan temuan untuk penelaah |
| `usulan_rumusan` | string \| null | Saran perbaikan (opsional) |
| `rujukan.sumber` | string | Nama peraturan sumber |
| `rujukan.butir` | string | Nomor butir spesifik |
| `rujukan.kutipan` | string | Kutipan isi butir |
| `rujukan.pdf_url` | string | URL PDF di JDIH |
| `status` | enum string | `"belum_ditinjau"` \| `"diterima"` \| `"ditolak"` |

### Catatan penting

- `offset_mulai` dan `panjang` diperlukan untuk `Critique.start` / `.length`
  supaya sorotan presisi di dalam paragraf, bukan menyorot satu paragraf penuh.
- Selama `rujukan.butir` atau `rujukan.kutipan` masih placeholder (`"..."`),
  temuan wajib ditandai "rujukan belum diverifikasi" di UI. Tidak boleh
  ditampilkan seolah punya dasar hukum final.

### Tingkat keparahan ↔ warna Critique

| Tingkat | Warna Critique |
|---|---|
| `tinggi` | Red |
| `sedang` | Berry |
| `rendah` | Lavender |

Green **tidak dipakai** — dalam konteks telaah, hijau terbaca sebagai
"sudah benar", kebalikan dari maksud temuan.
