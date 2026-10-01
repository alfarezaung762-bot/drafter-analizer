# Penjelasan: tiga tahap `telaah/` di rancangan Fase 4

Pelengkap `fase4-merapikan-backend.md` bagian 1 dan 2: apa yang dikerjakan
tiap tahap, apa yang masuk, dan apa yang keluar. Contohnya kesalahan nyata
dari PMK 45 Tahun 2026.

```
FASE 1   aturan_deterministik/     kode     pemeriksaan yang AI tidak bisa
            │
TAHAP 1  tahap1_bahan/             kode     menyiapkan bacaan untuk agen
            │
TAHAP 2  tahap2_agen/              AI       mencari DAN membuktikan, lalu mencatat calon temuan
            │
TAHAP 3  tahap3_verifikasi.py      kode     gerbang: yang lolos ditandai di Word
```

Dibanding alur sekarang (5 tahap): parser dan persiapan digabung jadi tahap
1; cari dugaan dan memastikan digabung jadi tahap 2, karena agen mencari dan
membuktikan sendiri dalam satu putaran. **Tidak ada lagi daftar dugaan** —
yang keluar dari agen langsung calon temuan.

## Tahap 1 — bahan (kode, tanpa AI)

| Masuk | Keluar |
|---|---|
| Paragraf naskah dari Word | **Naskah bernomor** — seluruh naskah sebagai teks, satu baris per paragraf, tiap satuan berlabel `[pasal-18-ayat-5]`, tabel lampiran per baris sel |
| Hasil Fase 1 | **Pohon satuan** — daftar Pasal, ayat, huruf, angka beserta letaknya di Word; dipakai tahap 3 untuk membuktikan letak |
| | **Kelompok pasal** — ≤ 6 pasal atau ≤ 4.000 token per kelompok. PMK 45: Pasal 1–6, 7–10, 11–16, 17–22, 23–28, 29 |
| | **Bahan korpus**, hanya bila ada analisis yang membutuhkannya — peraturan yang disebut naskah, status dan teks pasal yang dirujuk |

Ini bacaan, bukan perintah dan bukan catatan dugaan.

## Tahap 2 — agen (AI)

Kode menjalankan beberapa putaran agen **bersamaan**, satu per kelompok
pasal, satu lintas naskah, satu lampiran (menurut baris `Lingkup` tiap
analisis). PMK 45: 6 + 1 + 1 = 8 putaran.

**Yang dibaca agen di awal tiap putaran:**

```
peran dasar
naskah bernomor UTUH                 ← sama di semua putaran
hasil Fase 1                         ← supaya tidak diulang
bahan korpus (bila ada)
analisis yang lingkupnya cocok       ← dari analisis.md
pasal fokus: pasal-17 … pasal-22     ← yang wajib dinilai putaran ini
daftar skill                         ← kaidah KMK 527, dimuat bila perlu
```

**Yang dikerjakan agen** — memilih sendiri langkahnya, berulang sampai
selesai. Contoh putaran Pasal 17–22:

```
1. membaca Pasal 18 ayat (5): "… tidak memenuhi persyaratan untuk dapat
   diberikan persetujuan ekspor, …"
2. cari_teks "persetujuan ekspor kembali atau pengembalian"
   → ketemu di Pasal 18 ayat (4)
3. muat_skill pmk-standar/batang-tubuh   (kaidah konsistensi rumusan)
4. catat_temuan
     analisis : rumusan tidak konsisten
     satuan   : pasal-18-ayat-5
     kutipan  : "persetujuan ekspor"            ← persis, ≤ 200 huruf
     bentuk   : usulan
     usulan   : "persetujuan ekspor kembali atau pengembalian"
     temuan   : ayat (4) menyebut ekspor kembali atau pengembalian,
                ayat (5) hanya ekspor
     skor     : 0,9
5. … pasal lain …
6. selesai — tiap analisis × tiap pasal fokus: diperiksa / tidak relevan
```

Kutipan yang lebih dari 200 huruf, atau melewati satu paragraf, ditolak saat
itu juga dan agen mengutip ulang. Pasal fokus yang tidak dilaporkan di
`selesai` ditagih sekali; yang tetap tidak dilaporkan dicatat "tidak
diperiksa".

**Yang keluar dari tahap 2:**

| Keluar | Isinya |
|---|---|
| **Calon temuan** | dari tiap `catat_temuan`: analisis, satuan, kutipan persis, bentuk (usulan · dibuang · catatan), temuan, saran, usulan, tempat sisipan bila perbaikannya di satuan lain, pembanding korpus, rujukan bila Dasar kosong, skor |
| **Laporan selesai** | status tiap analisis untuk tiap pasal fokus |
| **Jejak** | tiap langkah dan hasil alatnya — termasuk hasil `cari_korpus`, yang dipakai tahap 3 sebagai bukti |

Belum ada yang menyentuh Word.

## Tahap 3 — verifikasi (kode, satu berkas)

Satu-satunya tempat temuan lahir. Masuknya calon temuan dan jejak dari tahap
2, pohon satuan dari tahap 1, serta baris Respons dan Dasar tiap analisis dari
`analisis.md`. Tiap calon diuji satu per satu:

| Diuji | Gagal → |
|---|---|
| Kutipan persis ada di satuan yang disebut | gugur |
| Nomor pasal yang disebut ada; istilah berdefinisi dieja persis | gugur |
| Skor di atas ambang; klaim "tidak ada" memang tidak ada di naskah | gugur |
| Bentuk tidak melewati baris Respons analisisnya | diturunkan |
| `usulan`: pengganti muat di tempat yang dicoret, tiap kata tambahannya bersumber dari naskah sendiri atau peraturan berlaku | turun jadi `catatan`, usulannya pindah ke Saran |
| `dibuang`: alasannya salah satu dari tiga yang bisa dibuktikan kode | turun jadi `catatan` |
| Pembanding korpus ada di hasil `cari_korpus` yang tercatat di jejak | gugur |
| Rujukan dari baris Dasar; kalau Dasar kosong, rujukan agen terbukti ada di teks skill atau hasil korpus | rujukannya dibuang, temuan tetap |
| Sisipan satuan baru: tempatnya ada di pohon | gugur |
| Dua calon yang sama letak dan isinya | digabung |

Contoh tadi: kutipan "persetujuan ekspor" ada di Pasal 18 ayat (5) ✓;
pengganti muat ✓; kata tambahan "kembali", "atau", "pengembalian" ada di
Pasal 18 ayat (4) ✓ → lolos sebagai **usulan hijau**.

**Yang keluar dari tahap 3:** daftar temuan — bentuk, letak persis di Word,
dan isi komentar (Temuan, Saran, Sumber usulan, Pembanding, rujukan, nomor
T-n) — diteruskan ke panel dan penandaan Word. Calon yang gugur tidak tampil
di panel maupun Word; alasannya hanya tercatat di ekspor jejak untuk
pengembang.
