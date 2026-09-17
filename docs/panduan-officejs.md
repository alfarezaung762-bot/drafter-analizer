# Panduan Office.js

Peringatan utama: dokumentasi Office.js jarang muncul di data latih model, jadi
model cenderung mengarang method yang tidak ada atau memakai pola dari versi API
yang berbeda. **Selalu verifikasi sebelum menulis kode.**

## Sumber Kebenaran

Urut prioritas:

1. `frontend/node_modules/@types/office-js/index.d.ts` — definisi TypeScript
   resmi. Setiap method punya anotasi `[Api set: ...]` yang menyebut requirement
   set-nya. Cara cek: `grep -n "namaMethod" -B 8 index.d.ts`
2. Repo dokumentasi resmi (open source, berisi tutorial dan contoh kode):
   `OfficeDev/office-js-docs-pr` di GitHub — cukup clone, tidak perlu scraping.
3. Referensi Word JavaScript API di situs Microsoft Learn.

## Versi yang Sudah Diverifikasi dari `index.d.ts`

| API | Requirement set | Catatan |
|---|---|---|
| `Range.insertComment` | WordApi 1.4 | komentar permanen, tersimpan di file |
| `Paragraph.insertAnnotations` | WordApi 1.7 | **wajib langganan Microsoft 365** |
| `Critique.colorScheme` / `.start` / `.length` | WordApi 1.7 | warna: Red, Green, Blue, Lavender, Berry |
| `Critique.popupOptions` | WordApi 1.8 | berisi daftar `suggestions` + tombol Accept/Reject |
| `Range.highlight()` | WordApi 1.8 | sorotan **sementara**, tidak mengubah dokumen |
| `font.highlightColor` | WordApi 1.1 | sorotan **permanen**, mengubah dokumen |

## Hal yang Mudah Keliru

- Annotation (critique) **tidak persisten** — hilang saat dokumen ditutup.
  Dokumen sama sekali tidak berubah. Untuk hasil yang perlu dibawa keluar,
  gunakan `insertComment`.
- Warna komentar Word tidak deterministik antar-komputer. Jangan mengandalkan
  warna komentar untuk menyampaikan tingkat keparahan — tulis di dalam teksnya.
- Deklarasikan di manifest versi minimum yang **benar-benar dipakai**. Versi
  lebih tinggi tidak memberi keuntungan, justru memblokir Word versi lama.
  Fitur di atas versi minimum dicek runtime dengan
  `Office.context.requirements.isSetSupported("WordApi", "1.8")`.
- Task pane adalah halaman web biasa yang dimuat Word lewat URL di manifest.
- `isSetSupported("WordApi", "1.7"/"1.8")` bisa melaporkan `true` padahal
  `insertAnnotations`/Critique tetap melempar `RichApi.Error: NotImplemented`
  saat dipanggil — dikonfirmasi empiris di Word 2024 LTSC (lisensi beli-putus,
  tanpa langganan Microsoft 365 aktif). Requirement set yang didukung ≠ fitur
  yang diizinkan; Annotation mensyaratkan langganan, bukan cuma versi Word.

## Status keputusan sorotan

> **Keputusan produk terbaru:** jangan memakai sorotan berdasarkan tingkat
> keparahan atau sorotan seluruh paragraf sebagai mekanisme utama. Lihat
> [`keputusan-ux-penelaahan-fase1.md`](keputusan-ux-penelaahan-fase1.md).
> Pengguna tidak perlu mengatur Word: penggantian yang pasti memakai tampilan
> revisi add-in pada rentang presisi. `font.color` dan `strikeThrough` boleh
> dipakai hanya bersama snapshot/pemulihan format dan content control bertag.
> Terima menyimpan tampilan tersebut di naskah kerja; Tolak memulihkannya;
> pembersihan terjadi pada salinan Ekspor versi bersih. Detail:
> [`rancangan-analisis-terima-ekspor.md`](rancangan-analisis-terima-ekspor.md).

### Catatan historis - rancangan sebelumnya (jangan diikuti)

`font.highlightColor` dipakai sebagai mekanisme UTAMA untuk mewarnai temuan
sesuai tingkat keparahan (tinggi/sedang/rendah) di `tandaiSemuaTemuan()`
(`frontend/src/lib/office.ts`) — bukan cuma cadangan darurat seperti rancangan
awal. Alasannya: Critique (mekanisme yang semula direncanakan untuk ini)
butuh langganan Microsoft 365 yang tidak tersedia di lingkungan penelaah, dan
`Range.highlight()` — pengganti amannya yang tidak mengubah dokumen — sama
sekali tidak punya parameter warna, jadi tidak pernah bisa membedakan tingkat
keparahan dalam kondisi apa pun.

Ini **satu-satunya bagian alat yang mengubah format dokumen** (bukan isi
teksnya). Warna asli tiap paragraf dicatat sebelum ditimpa dan dipulihkan
otomatis saat temuan diterima atau ditolak — lihat `hapusSorotan()` di berkas
yang sama. Rasional produknya dan hubungannya dengan prinsip "tidak mengubah
naskah" ada di `fase1 drafter.md` bagian 6.
