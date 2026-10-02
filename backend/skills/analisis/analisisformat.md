# Analisis format naskah

Dinilai di putaran format: agen membaca naskah berformat — tiap paragraf
bernomor ¶ beserta formatnya — bukan naskah berlabel. Semua bagian di sini
ber-`Lingkup: format`.

## F-19 · Teks tersembunyi

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: format
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: bacaan format

### Yang diperiksa
- Teks yang disembunyikan (hidden) — tidak tampil di Word, tetapi ikut tersimpan di berkas

### Yang tidak diperiksa
- Kode kolom (field), komentar, dan isi kotak teks

### Cara memeriksa
Naskah berformat menyebut ⟨tersembunyi: "…"⟩ pada paragrafnya. Letak = ¶
paragraf itu; kutipan = teks tersembunyinya persis; `bukti_format` =
tersembunyi: "…" persis seperti di naskah berformat.

### Bukan kesalahan
- Paragraf kosong yang tidak memuat teks tersembunyi

### Contoh
PMK 4 Tahun 2025: "jJ jJ" tersembunyi tepat sebelum "Mengingat".

## F-20 · Butir bernomor kosong

Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: format
Komentar: lengkap
Dasar: prioritas penelaah
Butuh: —

### Yang diperiksa
- Paragraf kosong yang ikut daftar bernomor — nomornya tampil, mis. "d.", tanpa isi

### Yang tidak diperiksa
- Paragraf kosong yang tidak bernomor — itu baris kosong biasa

### Cara memeriksa
Naskah berformat menyebut ⟨butir bernomor tanpa isi⟩ pada paragrafnya.
Letak = ¶ paragraf itu; kutipan = nomornya, mis. "d."; `bukti_format` =
butir bernomor tanpa isi. Temuan ini ketiadaan isi: `ketiadaan: true`.

### Bukan kesalahan
- Butir bernomor yang isinya ada di sel tabel sebelahnya

### Contoh
PMK 4 Tahun 2025: paragraf kosong ikut daftar Menimbang, terbaca "d." sesudah
huruf c.
