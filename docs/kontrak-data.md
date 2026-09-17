# Kontrak Data

## Bentuk Data Temuan — KONTRAK

> Harus selalu sama dengan `docs/fase1 drafter.md` bagian 11. Kalau salah satu
> diubah, yang lain ikut diubah di commit yang sama.
>
> Revisi 17 Sep 2026 (kedua): `tingkat_keparahan` dihapus, `nomor` dan
> `jenis_tanda` ditambahkan. Cara `jenis_tanda` dipasang di dokumen BERUBAH
> TOTAL — Track Changes ditinggalkan, alat menggambar tandanya sendiri.
> Lihat `docs/fase1 drafter.md` bagian 6.

### Skema JSON

```json
{
  "id": "f-001",
  "nomor": 1,
  "aturan_id": "F1-001",
  "fase": 1,
  "jenis_tanda": "penggantian",
  "lokasi": {
    "paragraf_index": 3,
    "offset_mulai": 0,
    "panjang": 48,
    "teks_asli": "Tata Cara Uji Coba Penelaahan Rancangan Peraturan"
  },
  "catatan": "Judul peraturan ditulis kapital seluruhnya.",
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
| `nomor` | integer | Nomor urut temuan menurut posisinya di dokumen, mulai dari 1 |
| `aturan_id` | string | Kunci ke tabel rujukan di kode (`F1-001`, dst.) — tidak pernah ditampilkan ke penelaah |
| `fase` | integer | Selalu `1` untuk Fase 1 |
| `jenis_tanda` | enum string | `"penggantian"` \| `"catatan"` — lihat di bawah |
| `lokasi.paragraf_index` | integer | Indeks paragraf dalam daftar yang dikirim |
| `lokasi.offset_mulai` | integer | Posisi karakter awal di dalam paragraf |
| `lokasi.panjang` | integer | Panjang karakter yang ditandai |
| `lokasi.teks_asli` | string | Teks asli yang bermasalah |
| `catatan` | string | **Alasan** temuan, bukan pengulangan apa yang sudah terlihat di naskah |
| `usulan_rumusan` | string \| null | Rumusan pengganti — lihat aturan di bawah |
| `rujukan.sumber` | string | Nama peraturan sumber |
| `rujukan.butir` | string | Nomor butir spesifik |
| `rujukan.kutipan` | string | Kutipan isi butir — dipasang sebagai balasan komentar, bukan di komentar utama |
| `rujukan.pdf_url` | string | URL PDF di JDIH |
| `status` | enum string | `"belum_ditinjau"` \| `"diterima"` \| `"ditolak"` |

### Yang dihapus dan kenapa

**`tingkat_keparahan` sudah tidak ada.** Dulu dipakai untuk dua hal: memilih
warna sorotan (merah/kuning/toska) dan menyaring daftar di panel. Sesudah warna
tinggal satu (kuning, hanya untuk temuan `catatan`) dan panel diringkas jadi
daftar navigasi, tingkat itu tidak dibaca siapa pun. Menyimpan field yang tidak
dipakai hanya menyisakan pertanyaan bagi orang berikutnya yang membaca kode.

### `nomor` — penomoran temuan

Nomor urut menurut posisi di dokumen: temuan paling atas `1`, berikutnya `2`,
dan seterusnya. Ditetapkan **backend**, sesudah seluruh aturan dijalankan dan
temuannya diurutkan menurut `paragraf_index` lalu `offset_mulai`.

Nomor inilah yang ditampilkan sebagai `(T1)`, `(T2)` di ujung komentar dan
sebagai nomor di daftar panel — supaya penelaah bisa melompat bolak-balik antara
naskah dan panel tanpa menerjemahkan apa pun. `aturan_id` tidak pernah muncul di
antarmuka.

### `jenis_tanda` — cara temuan dipasang di dokumen

| Nilai | Dipakai bila | Cara dipasang |
|---|---|---|
| `penggantian` | Ada satu rumusan pengganti yang deterministik untuk `lokasi.teks_asli` | Teks lama MERAH `#C00000` + dicoret; `usulan_rumusan` disisipkan di sebelahnya, HIJAU `#00802B` |
| `catatan` | Tidak ada pengganti tunggal — yang salah adalah ketiadaan sesuatu, atau alat tidak tahu mana dari dua kemungkinan yang benar | BLOK KUNING (`font.highlightColor = "Yellow"`); warna huruf TIDAK disentuh |

Keduanya diberi tepat satu komentar, dan diputuskan dari **task pane**.

Seluruh penandaan berjalan dengan `changeTrackingMode = "Off"`, lalu mode semula
dikembalikan. Tiap tanda dibungkus content control bertag `DA-ASLI-{nomor}` atau
`DA-USUL-{nomor}` supaya add-in bisa menemukannya kembali.

**Terima** tidak mengubah naskah sama sekali — hanya status kartu di panel.
**Tolak** membuang usulan hijau, memulihkan format asli, dan menghapus komentar.

**Aturan yang mengikat:**

- Bila `jenis_tanda` = `"penggantian"`, `usulan_rumusan` **wajib terisi** dan
  harus berupa teks pengganti harfiah untuk `lokasi.teks_asli` — bukan contoh
  bunyi, bukan penjelasan. Isi field inilah yang benar-benar disisipkan ke
  naskah orang.
- Bila `jenis_tanda` = `"catatan"`, `usulan_rumusan` boleh `null` atau berisi
  contoh bunyi yang hanya ditampilkan, tidak pernah disisipkan.
- Fungsi aturan di `rules/format_baku.py` **wajib menetapkan `jenis_tanda`
  secara eksplisit.** Jangan menyimpulkannya dari ada-tidaknya
  `usulan_rumusan` — suatu saat ada aturan yang usulannya cuma contoh, dan
  menebak di situ berarti salah menyunting naskah orang.
- Temuan `penggantian` **tidak** diberi blok kuning, dan temuan `catatan`
  **tidak** diberi warna merah. Merah berarti "ada penggantinya"; memberi merah
  pada temuan tanpa pengganti membuat alat seolah menyuruh membuang teks itu.

### Pemetaan aturan Fase 1

Diverifikasi terhadap `rules/format_baku.py` per 16 Sep 2026.

| Aturan | `jenis_tanda` | Alasan |
|---|---|---|
| F1-001 judul kapital | — | **DIMATIKAN** (`AKTIFKAN_F1_001 = False`). Tidak bisa membedakan judul berhuruf campur dari judul yang tampil kapital lewat gaya ALL CAPS — lihat `fase1 drafter.md` bagian 6.10 |
| F1-002 judul pembuka ≠ judul Menetapkan | `catatan` | Alat tidak tahu mana yang benar dari keduanya |
| F1-003 kelengkapan struktur | `catatan` | Yang salah adalah ketiadaan bagian |
| F1-004 frasa baku butir Menimbang terakhir | `catatan` | Bunyi bakunya perlu menyebut huruf mana saja yang dirujuk |
| F1-005 ejaan | `penggantian` | Substitusi kata |

Pada `backend/tools/contoh/contoh-rancangan-uji.docx` dengan F1-001 mati:
2 `penggantian`, 2 `catatan`.

### Bentuk teks `catatan`

Ditulis sebagai alasan, dua baris, tanpa nama produk dan tanpa tingkat
keparahan. Contoh untuk temuan `penggantian` — apa yang berubah sudah terlihat
dari coretan di naskah, jadi tidak diulang:

```
Nama jenis peraturan ditulis dengan huruf kapital pada kedua unsurnya.
KMK 527/KMK.01/2022 Lamp. II butir 33 — jdih.kemenkeu.go.id/... (T4)
```

Temuan `catatan` tidak menghasilkan coretan, jadi harus menyebut sendiri apa
yang bermasalah:

```
Judul pada Menetapkan harus sama persis dengan judul pembuka — di sini berbeda.
Mana yang benar ditentukan penelaah.
KMK 527/KMK.01/2022 Lamp. II butir ... — jdih.kemenkeu.go.id/... (T2)
```

Kutipan utuh butirnya (`rujukan.kutipan`) **tidak** ikut di komentar utama —
dipasang sebagai balasan komentar (`Comment.replies`, WordApi 1.4).

### Bentuk AnalisisRequest

```json
{
  "jenis_dokumen": "PMK",
  "paragraf": [
    { "index": 0, "teks": "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA" }
  ]
}
```

| Field | Tipe | Keterangan |
|---|---|---|
| `jenis_dokumen` | enum string | `"PMK"` \| `"KMK"` — **wajib**, dipilih penelaah di task pane sebelum menekan Analisis |
| `paragraf[].index` | integer | Indeks paragraf di dokumen |
| `paragraf[].teks` | string | Isi teks paragraf |
| `paragraf[].tampil_kapital` | boolean | Opsional, default `false`. **Tidak lagi dikirim frontend** — satu-satunya pemakainya F1-001, yang sudah dimatikan. Field-nya dibiarkan ada supaya kontrak lama tidak pecah. Lihat `docs/fase1 drafter.md` bagian 6.10 |

Backend **tidak menebak** jenis dokumen. Fungsi `_tentukan_jenis_dokumen()`
dihapus; jenisnya diteruskan sebagai parameter ke `_ekstrak_judul_pembuka()` dan
`cek_frasa_baku_menimbang()`. Alasan lengkapnya di `docs/fase1 drafter.md`
bagian 6.7.

### Catatan penting

- Selama `rujukan.butir` atau `rujukan.kutipan` masih placeholder (`"..."`),
  temuan wajib ditandai "rujukan belum diverifikasi" di antarmuka. Tidak boleh
  ditampilkan seolah punya dasar hukum final.
- `offset_mulai` dan `panjang` menandai rentang presisi di dalam paragraf, agar
  yang ditandai bukan satu paragraf penuh. Sejak 17 Sep 2026 seluruh aturan
  benar-benar mematuhinya sampai tingkat kata — lihat `fase1 drafter.md`
  bagian 6.5. Temuan yang rentangnya tidak ketemu di Word **tidak ditandai sama
  sekali**, bukan diperlebar.
- Nomor `(T1)`, `(T2)` juga dipakai kode untuk menemukan kembali komentarnya
  sendiri saat temuan ditolak. Karena nomornya melekat pada urutan dokumen,
  menjalankan analisis dua kali menghasilkan komentar bernomor sama — panel
  wajib menolak menganalisis ulang selama masih ada temuan yang belum
  diputuskan. Lihat `docs/fase1 drafter.md` bagian 6.5.

> Dua rancangan penandaan sebelumnya sudah dihapus dari dokumen ini: `Critique`
> (terkunci langganan Microsoft 365) dan Track Changes (warna revisinya tidak
> bisa diatur add-in, dan pewarnaan selagi pelacakan menyala menghasilkan revisi
> `Formatted: Highlight` yang menspam margin). Riwayat lengkapnya di
> `docs/fase1 drafter.md` bagian 6.1.
