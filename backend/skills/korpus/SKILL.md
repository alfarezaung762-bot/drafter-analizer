---
name: korpus
description: Cara mencari dan menilai pembanding di korpus peraturan OpenSearch (JDIH) — cari_korpus untuk pasal pembanding, cek_peraturan untuk status berlaku dan nomor Lembaran/Berita Negara
---

# Korpus peraturan

Dua alat, keduanya hanya MEMBACA korpus peraturan JDIH di OpenSearch:

- `cari_korpus(teks)` — mencari pasal pembanding di peraturan lain yang
  MASIH BERLAKU. Hasilnya paling banyak 5 peraturan, satu pasal paling mirip
  masing-masing — potongan, bukan peraturan utuh. Peraturan yang dicabut
  sudah dibuang kode.
- `cek_peraturan(sebutan)` — status berlaku sebuah peraturan menurut jenis,
  nomor, dan tahunnya, mis. "Undang-Undang Nomor 17 Tahun 2003".

## Kaidah menilai

1. Sebut HANYA peraturan yang muncul di hasil alat — salin namanya persis.
   Kode mencocokkannya ke hasil yang tercatat; nama dari ingatanmu
   menggugurkan temuannya.
2. Teks korpus hasil pemindaian; OCR-nya bisa rusak ("clan" untuk "dan").
   Kalau kutipannya terbaca janggal, jangan dijadikan dasar.
3. Pertentangan dengan peraturan lain ditulis "berpotensi bertentangan",
   tidak pernah "bertentangan" — temuan itu kemungkinan, bukan kesimpulan.
4. "Tidak ketemu di korpus" tidak pernah jadi temuan. Korpus tidak memuat
   segalanya.
5. Status dari `cek_peraturan` hanya dipakai bila jawabannya pasti: satu
   dokumen cocok, status "Berlaku" atau "Tidak Berlaku". "Tidak tahu" berarti
   diam.

## Rumusan pengganti dan definisi baru

- Definisi yang dirumuskan kembali wajib sama dengan definisi di peraturan
  berlaku yang sejenis atau yang dilaksanakan (Lampiran II angka III huruf
  C.1 butir 62 dan 65, hlm 45). Untuk definisi baru — mis. istilah yang
  dipakai tetapi belum didefinisikan — cari dulu di korpus; ketemu → salin
  persis dan sebut peraturan serta pasalnya di `sisipan.sumber`.
- Tidak ketemu → perkirakan artinya dari isi naskah sendiri, dan tulis
  `sisipan.sumber: "prediksi AI"`.
- Tidak bisa diperkirakan → jangan disisipkan; catat temuannya saja.
