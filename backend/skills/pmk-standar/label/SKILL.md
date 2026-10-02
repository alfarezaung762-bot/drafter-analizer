---
name: pmk-standar/label
description: Aturan label satuan PMK biasa — dibaca langkah label tahap 1 untuk memberi label tiap paragraf pembuka satuan; label dibuktikan kode
---

# Label satuan PMK biasa

Beri label HANYA pada paragraf yang MEMBUKA satu satuan. Paragraf lanjutan,
kalimat pengantar tanpa penanda, isi tabel lampiran, dan baris lain tidak
diberi label. Tulis label huruf kecil; nomor sisipan memakai hurufnya (2a,
27a).

| Label | Paragraf yang dilabeli |
|---|---|
| `judul` | baris pertama judul peraturan, tepat sesudah baris "TENTANG" |
| `menimbang-a`, `menimbang-b`, … | tiap butir Menimbang — paragraf yang memuat huruf butirnya |
| `mengingat-1`, `mengingat-2`, … | tiap butir Mengingat — paragraf yang memuat angka butirnya |
| `menetapkan` | baris "Menetapkan : …" |
| `bab-i`, `bab-ii`, … | baris "BAB I" |
| `bab-ii-bagian-kesatu` | baris "Bagian Kesatu" di BAB II |
| `bab-ii-bagian-kesatu-paragraf-1` | baris "Paragraf 1" di Bagian Kesatu BAB II |
| `pasal-5` | baris judul "Pasal 5" |
| `pasal-5-ayat-2` | baris "(2) …" di Pasal 5 |
| `pasal-5-ayat-2-huruf-b` | rincian huruf di bawah ayat |
| `pasal-5-ayat-2-huruf-b-angka-1` | rincian angka di bawah huruf |
| `pasal-1-angka-3` | rincian angka langsung di bawah pasal (definisi Pasal 1) |
| `pasal-5-huruf-a` | rincian huruf langsung di bawah pasal tanpa ayat |
| `penutup` | baris "Ditetapkan di …" |
| `lampiran` | baris "LAMPIRAN" yang PERTAMA, sesudah penutup |

Rincian yang induknya rincian lain disambung ke label induknya: huruf di
bawah angka `pasal-3-ayat-1-angka-2-huruf-a`, angka di bawah huruf
`pasal-3-ayat-1-huruf-a-angka-1`.

Pada naskah bertabel, nomor "1." bisa di satu sel dan teksnya di sel
sebelahnya: label diberikan pada paragraf yang memuat nomornya.

Naskah perubahan — batang tubuhnya "Pasal I" dan "Pasal II" berangka
Romawi, atau judulnya memuat "PERUBAHAN ATAS" — bukan PMK biasa: jawab
`"jenis": "pmk perubahan"` dan jangan beri label.
