# Formulir analisis

Salin bagian di bawah garis ke `analisis.md` — atau ke `analisisformat.md` bila
yang diperiksa format — lalu isi. Berkas ini sendiri tidak dimuat sebagai
analisis.

Enam baris kepala dibaca kode: pemuat (jenis naskah, lingkup, prasyarat),
panel Pengaturan, dan gerbang (batas respons, bentuk komentar, rujukan).
Nilai di luar pilihan, kunci wajib kosong, atau kode kembar membuat backend
menolak menyala dan menyebut analisisnya.

Bagian di bawah kepala dibaca agen; "Yang diperiksa" dan "Yang tidak
diperiksa" juga tampil di panel.

---

## Kode · Judul analisis

Berlaku untuk: pmk-standar
Respons: otomatis
Lingkup: per pasal
Komentar: lengkap
Dasar: KMK 527 Lampiran II angka III huruf C.2 butir 72, hlm 46 (visual)
Butuh: —

### Yang diperiksa
- butir singkat — tampil di panel Pengaturan

### Yang tidak diperiksa
- butir singkat — tampil di panel Pengaturan

### Cara memeriksa
Untuk agen: di bagian naskah mana, kaidah (skill) dan alat apa yang dipakai.
Boleh kosong — agen memilih sendiri dari alat yang ada; diisi supaya hasilnya
sama tiap kali dijalankan.

### Bukan kesalahan
Kapan agen harus diam — batas kewajaran.

### Contoh
Satu temuan yang benar, satu yang bukan. Boleh kosong.

---

Pilihan tiap baris kepala:

| Baris | Pilihan |
|---|---|
| Berlaku untuk | nama folder skill jenis naskah, mis. `pmk-standar`; boleh lebih dari satu, dipisah koma |
| Respons | `otomatis` · `usulan` · `catatan` · `dibuang` — batas atas; gerbang boleh menurunkan, tidak pernah menaikkan |
| Lingkup | `per pasal` · `seluruh naskah` · `lampiran` · `format` |
| Komentar | `lengkap` · `ringkas` (bawaan `lengkap`) |
| Dasar | alamat lengkap KMK 527 berakhiran `(visual)` atau `(turunan)`; atau `prioritas penelaah`; boleh kosong — agen mencarikan rujukannya dan kode membuktikannya |
| Butuh | `—` · `korpus` · `bahan korpus` · `bacaan format`; boleh lebih dari satu, dipisah koma |
