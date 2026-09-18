# Panduan Office.js

Peringatan utama: dokumentasi Office.js jarang muncul di data latih model, jadi
model cenderung mengarang method yang tidak ada atau memakai pola dari versi API
yang berbeda. **Selalu verifikasi sebelum menulis kode.**

## Sumber kebenaran

Urut prioritas:

1. `frontend/node_modules/@types/office-js/index.d.ts` — definisi TypeScript
   resmi. Tiap method punya anotasi `[Api set: ...]` yang menyebut requirement
   set-nya. Cara cek: `grep -n "namaMethod" -B 8 index.d.ts`
2. Repo dokumentasi resmi `OfficeDev/office-js-docs-pr` di GitHub.
3. Referensi Word JavaScript API di Microsoft Learn.

## API yang dipakai Fase 1 — sudah diverifikasi ke `index.d.ts`

Seluruh penandaan sengaja dijaga di **WordApi 1.1**, himpunan paling dasar, agar
jalan di Word desktop mana pun termasuk lisensi beli-putus.

| API | Requirement set | Dipakai untuk |
|---|---|---|
| `Font.color` | WordApi 1.1 | merah `#C00000` untuk teks salah, hijau `#00802B` untuk usulan |
| `Font.strikeThrough` | WordApi 1.1 | coretan pada teks yang ada penggantinya |
| `Font.highlightColor` | WordApi 1.1 | blok kuning untuk temuan tanpa pengganti |
| `Range.insertText(..., "After")` | WordApi 1.1 | menyisipkan usulan di sebelah teks aslinya |
| `Range.insertContentControl()` | WordApi 1.1 | membungkus tanda agar bisa ditemukan kembali |
| `ContentControl.tag` / `.title` / `.appearance` | WordApi 1.1 | penanda `DA-ASLI-{n}` dan `DA-USUL-{n}`, tampilan `Hidden` |
| `ContentControl.font` | WordApi 1.1 | memulihkan format saat Tolak — **bukan** `getRange().font`, yang butuh 1.3 |
| `ContentControl.delete(keepContent)` | WordApi 1.1 | `false` membuang usulan berikut isinya, `true` melepas bungkus saja |
| `ContentControlCollection.getByTag()` | WordApi 1.1 | menemukan kembali tanda milik alat |
| `Range.search()` | WordApi 1.1 | mencari letak temuan dari `lokasi.teks_asli` |
| `Range.insertComment` | WordApi 1.4 | komentar permanen, tersimpan di berkas |
| `Document.changeTrackingMode` | WordApi 1.4 | **dimatikan** selama penandaan, lalu dikembalikan |
| `Comment.replies` | WordApi 1.4 | rencana tempat kutipan utuh butir — belum dipakai |

## Jebakan yang sudah terbukti

- **Requirement set didukung ≠ fitur diizinkan.** `isSetSupported("WordApi",
  "1.7")` melaporkan `true` di Word 2024 LTSC, tetapi `insertAnnotations` tetap
  melempar `RichApi.Error: NotImplemented` — Annotation mensyaratkan langganan
  Microsoft 365 aktif, bukan cuma versi Word. Tiap fitur baru wajib punya jalur
  cadangan runtime.
- **Tidak ada API warna revisi sama sekali.** Sudah dicari ke seluruh
  `index.d.ts`: tidak ada `insertedTextColor`, `deletedTextColor`,
  `revisionColor`, maupun `authorColor`. `RevisionsFilter` hanya punya `markup`
  dan `view`. Warna revisi ditentukan Word menurut penulisnya. Inilah sebab
  Track Changes ditinggalkan — lihat `fase1 drafter.md` bagian 6.1.
- **`Word.search()` dibatasi sekitar 255 karakter.** Temuan yang teksnya lebih
  panjang tidak akan pernah ketemu, jadi tidak pernah tertandai. Backend
  memotong rentang `catatan` di 120 karakter untuk ini.
- **`search()` mengembalikan SEMUA kemunculan** di paragraf, bukan yang ada di
  `offset_mulai`. Perlu dihitung kemunculan keberapa, kalau tidak temuan pada
  kata yang berulang selalu mendarat di kemunculan pertama.
- **`getTrackedChanges()` melapor kurang** — satu penggantian muncul sebagai satu
  item bertipe `Added` saja, padahal di dokumen ada sisipan *dan* penghapusan.
  Jangan dipakai sebagai bukti keberhasilan. (Sudah tidak dipakai sejak Track
  Changes ditinggalkan.)
- **Memberi warna selagi pelacakan menyala** membuat Word mencatat tiap
  pewarnaan sebagai revisi `Formatted: Highlight` di margin. Matikan pelacakan
  dulu, kembalikan sesudahnya.
- **`font.allCaps` (WordApiDesktop 1.3)** tidak menolong mengenali judul yang
  tampil kapital lewat gaya paragraf — belum jelas apakah requirement set-nya
  tidak tersedia atau propertinya buta terhadap gaya. Aturan yang bergantung
  padanya (F1-001) dimatikan. Kandidat penggantinya: `Range.getOoxml()`
  (WordApi 1.1) lalu cari penanda `<w:caps/>` — **belum diuji.**
- **Warna komentar Word tidak deterministik antar-komputer**, dan rentang yang
  punya komentar diberi naungan warna penulisnya — bisa menutupi blok kuning.
  Jangan mengandalkan warna komentar untuk menyampaikan apa pun.
- **Deklarasikan di manifest versi minimum yang benar-benar dipakai.** Versi
  lebih tinggi tidak memberi keuntungan, justru memblokir Word versi lama.

## Catatan historis — jangan diikuti

Dua rancangan penandaan sudah gugur di Word penelaah: `Critique` + popup
(terkunci langganan Microsoft 365) dan Track Changes bawaan Word (warna revisi
tidak bisa diatur, dan pewarnaan menghasilkan spam `Formatted: Highlight`).
Pernah juga dipakai `font.highlightColor` berdasarkan tingkat keparahan
tinggi/sedang/rendah; tingkat keparahan sudah dihapus dari seluruh rancangan.

Riwayat lengkapnya beserta buktinya ada di `fase1 drafter.md` bagian 6.1–6.2.
