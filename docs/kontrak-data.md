# Kontrak Data

## Bentuk Data Temuan — KONTRAK

> Bentuk ini menjadi penghubung semua modul. Harus selalu sama dengan
> `docs/fase1 drafter.md` bagian 11 — kalau salah satunya diubah, yang lain
> ikut diubah di commit yang sama.
>
> Revisi 16 Sep 2026: menambah `jenis_tanda`.

### Skema JSON

```json
{
  "id": "f-001",
  "aturan_id": "F1-001",
  "fase": 1,
  "tingkat_keparahan": "tinggi",
  "jenis_tanda": "penggantian",
  "lokasi": {
    "paragraf_index": 3,
    "offset_mulai": 0,
    "panjang": 48,
    "teks_asli": "Tata Cara Uji Coba Penelaahan Rancangan Peraturan"
  },
  "catatan": "Judul peraturan seharusnya ditulis kapital seluruhnya.",
  "usulan_rumusan": "TATA CARA UJI COBA PENELAAHAN RANCANGAN PERATURAN",
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
| `jenis_tanda` | enum string | `"penggantian"` \| `"catatan"` — lihat di bawah |
| `lokasi.paragraf_index` | integer | Indeks paragraf dalam daftar yang dikirim |
| `lokasi.offset_mulai` | integer | Posisi karakter awal di dalam paragraf |
| `lokasi.panjang` | integer | Panjang karakter yang ditandai |
| `lokasi.teks_asli` | string | Teks asli yang bermasalah |
| `catatan` | string | Penjelasan temuan untuk penelaah |
| `usulan_rumusan` | string \| null | Rumusan pengganti — lihat aturan di bawah |
| `rujukan.sumber` | string | Nama peraturan sumber |
| `rujukan.butir` | string | Nomor butir spesifik |
| `rujukan.kutipan` | string | Kutipan isi butir |
| `rujukan.pdf_url` | string | URL PDF di JDIH |
| `status` | enum string | `"belum_ditinjau"` \| `"diterima"` \| `"ditolak"` |

### `jenis_tanda` — menentukan cara temuan dipasang di dokumen

| Nilai | Dipakai bila | Cara dipasang | Cara diputuskan |
|---|---|---|---|
| `penggantian` | Ada satu rumusan pengganti yang deterministik untuk `lokasi.teks_asli` | Perubahan terlacak (Track Changes) | Accept / Reject bawaan Word, ribbon **Review** |
| `catatan` | Tidak ada pengganti tunggal — yang salah adalah ketiadaan sesuatu, atau alat tidak tahu mana dari dua kemungkinan yang benar | `insertComment` + `font.highlightColor` | Tombol Terima/Tolak di task pane |

**Aturan yang mengikat:**

- Bila `jenis_tanda` = `"penggantian"`, `usulan_rumusan` **wajib terisi** dan
  harus berupa teks pengganti harfiah untuk `lokasi.teks_asli` — bukan contoh
  bunyi, bukan penjelasan. Isi field inilah yang benar-benar disisipkan ke
  naskah orang.
- Bila `jenis_tanda` = `"catatan"`, `usulan_rumusan` boleh `null` atau berisi
  contoh bunyi yang hanya ditampilkan, tidak pernah disisipkan.
- Fungsi aturan di `rules/format_baku.py` **wajib menetapkan `jenis_tanda`
  secara eksplisit.** Jangan menyimpulkannya dari ada-tidaknya
  `usulan_rumusan` — suatu saat sebuah aturan bisa punya usulan yang sifatnya
  contoh, dan menebaknya akan salah menyunting naskah orang.

### Pemetaan aturan Fase 1

Diverifikasi terhadap `rules/format_baku.py` per 16 Sep 2026.

| Aturan | `jenis_tanda` | Alasan |
|---|---|---|
| F1-001 judul kapital | `penggantian` | Penggantinya `teks.upper()` |
| F1-002 judul pembuka ≠ judul Menetapkan | `catatan` | Alat tidak tahu mana yang benar dari keduanya |
| F1-003 kelengkapan struktur | `catatan` | Yang salah adalah ketiadaan bagian |
| F1-004 frasa baku butir Menimbang terakhir | `catatan` | Bunyi bakunya perlu menyebut huruf mana saja yang dirujuk |
| F1-005 ejaan | `penggantian` | Substitusi kata |

### Catatan penting

- Selama `rujukan.butir` atau `rujukan.kutipan` masih placeholder (`"..."`),
  temuan wajib ditandai "rujukan belum diverifikasi" di antarmuka. Tidak boleh
  ditampilkan seolah punya dasar hukum final.
- `offset_mulai` dan `panjang` menandai rentang presisi di dalam paragraf, agar
  yang diganti atau disorot bukan satu paragraf penuh.

### Tingkat keparahan ↔ warna sorotan

Hanya berlaku untuk temuan `jenis_tanda` = `"catatan"`. Temuan `penggantian`
tidak diberi sorotan warna — coretan revisinya sudah jadi penanda visual.

| Tingkat | Warna (`font.highlightColor`) |
|---|---|
| `tinggi` | Red |
| `sedang` | Yellow |
| `rendah` | Turquoise |

Green **tidak dipakai** — dalam konteks telaah, hijau terbaca sebagai
"sudah benar", kebalikan dari maksud temuan.

> Tabel warna `Critique` yang dulu tercatat di sini sudah dihapus: Critique
> tidak dapat dipakai karena mensyaratkan langganan Microsoft 365 yang tidak
> ada pada Word penelaah. Lihat `docs/fase1 drafter.md` bagian 6.1.
