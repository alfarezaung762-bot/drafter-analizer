# Penjelasan: alur Fase 4 dengan contoh nyata

Pelengkap `fase4-merapikan-backend.md` bagian 2. Contohnya dari PMK 45 Tahun
2026 dan uji berbayar 1–2 Okt 2026.

## Alurnya

```
PENELAAH              menekan Jalankan Analisis; panel membaca teks dan format naskah
TAHAP 1  BAHAN        AI     label satuan, dibuktikan kode
                      kode   naskah berlabel · naskah berformat · peta letak · bahan korpus
TAHAP 2  AGEN         AI     kode membagi putaran — per kelompok pasal · lintas naskah ·
                             lampiran · format — semuanya berjalan bersamaan
         2a  agen mencari, membuktikan, mencatat calon temuan
         2b  penilai kedua menyaring calon temuan
TAHAP 3  GERBANG      kode   membuktikan kutipan, letak, sumber
PANEL DAN WORD               penelaah memutuskan: Terima / Tolak
```

Tidak ada daftar dugaan di tengah jalan: agen mencari dan membuktikan sendiri
di putarannya, lalu yang keluar langsung calon temuan.

## Contoh 1 — putaran Pasal 1–6, dari awal sampai Word

Dua calon temuan asli dari uji PMK 45 (1 Okt 2026), sama-sama "rumusan dua
arah":

- **Pasal 6 ayat (4) huruf b** — kuat;
- **Pasal 2 ayat (4)** — lemah, tetapi di uji itu lolos gerbang dan tampil
  **hijau**.

### 1. Tahap 1 — bahan (kode)

Kode menyusun naskah berlabel — seluruh naskah, ±38 rb token. Pembagi di
tahap 2 lalu menaruh Pasal 1–6 dalam satu putaran. Potongan yang relevan:

```
[pasal-2-ayat-3] (3) Pembebasan bea masuk sebagaimana dimaksud pada ayat (1) juga dapat
                 diberikan terhadap: a. pengeluaran barang dari: … b. penyelesaian barang …
[pasal-2-ayat-4] (4) Bea masuk sebagaimana dimaksud pada ayat (1) dan ayat (2) termasuk: …
[pasal-6-ayat-2] (2) Untuk mendapatkan pembebasan bea masuk dalam hal barang … yang TIDAK
                 tercantum dalam Lampiran I …, Kementerian/Lembaga/Badan mengajukan permohonan …
[pasal-6-ayat-4] (4) Permohonan sebagaimana dimaksud pada ayat (1) atau ayat (2) minimal
                 memuat informasi mengenai:
[pasal-6-ayat-4-huruf-b] b. uraian barang dan nomor pada daftar barang yang tercantum
                 dalam Lampiran I sebagaimana dimaksud dalam Pasal 3 ayat (3);
```

### 2. Tahap 2a — agen (AI)

Agen membaca naskah utuh, menilai Pasal 1–6, memakai alat bila perlu, lalu
mencatat dua calon temuan — teks di bawah jawaban asli Terra di uji:

```
calon 1   pasal-6-ayat-4-huruf-b · rumusan dua arah · skor 0,98
  kutipan : "uraian barang dan nomor pada daftar barang yang tercantum dalam Lampiran I …"
  bacaan 1: pemohon ayat (1) ATAU ayat (2) wajib mencantumkan nomor daftar Lampiran I —
            termasuk permohonan atas barang yang tidak tercantum di Lampiran I
  bacaan 2: nomor itu hanya wajib bila barangnya tercantum di Lampiran I

calon 2   pasal-2-ayat-4 · rumusan dua arah · skor 0,9
  kutipan : "Bea masuk sebagaimana dimaksud pada ayat (1) dan ayat (2)"
  bacaan 1: mencakup pengeluaran barang ayat (3), karena ayat (3) menyatakan pembebasan
            "sebagaimana dimaksud pada ayat (1)" juga diberikan atasnya
  bacaan 2: tidak mencakup ayat (3), karena ayat (4) hanya menyebut ayat (1) dan ayat (2)
```

lalu `selesai` — Pasal 1–6 diperiksa.

**Yang tidak bisa membedakan keduanya:** skornya (sama-sama di atas ambang
0,7), dan gerbang kode — kutipannya ada, letaknya ada, dua bacaannya
tertulis. Padahal bacaan 1 calon 2 sendiri sudah menjawab pertanyaannya:
ayat (3) merujuk ayat (1), jadi ayat (4) ikut mencakupnya.

### 3. Tahap 2b — penilai kedua (AI) — ditetapkan 2 Okt 2026

Sesudah agen menutup putaran: satu request baru, **terpisah dari percakapan
agen** — penilai tidak ikut terbawa alasan agen, hanya melihat klaimnya.

```
[peran: penilai kedua yang skeptis]
[naskah berlabel UTUH]                        ← sama dengan putaran
[calon temuan putaran ini: satuan, kutipan, temuan, bacaan 1 dan 2]
[tugas: untuk tiap calon, setuju HANYA bila kesalahannya nyata menurut naskah.
 Rumusan dua arah: kedua bacaan harus sama-sama masuk akal bagi pembaca
 hukum yang membaca seluruh pasal, dan akibat hukumnya berbeda.]
```

Jawaban yang diharapkan — **contoh untuk menggambarkan alur, belum dijalankan**:

```
calon 1  SETUJU — ayat (2) justru untuk barang yang tidak tercantum di Lampiran I,
         jadi kewajiban nomor Lampiran I tak bisa dipenuhi; dua bacaan nyata.
calon 2  TOLAK  — ayat (3) memberikan pembebasan "sebagaimana dimaksud pada ayat (1)",
         jadi ayat (4) yang menyebut ayat (1) sudah mencakupnya; bacaan 2 tidak
         masuk akal.
```

- **Ditolak → gugur**: tidak tampil di panel maupun Word; alasan penilai
  tercatat di ekspor jejak.
- **Disetujui → lanjut ke gerbang.**
- Tambahannya satu request per putaran — PMK 45: 8, atau 9 dengan putaran
  format.

### 4. Tahap 3 — gerbang (kode)

Calon 1 diuji satu per satu:

| Diuji | Calon 1 | Gagal → |
|---|---|---|
| Kutipan persis ada di satuan yang disebut | ✓ | gugur |
| Nomor pasal yang disebut ada; istilah berdefinisi dieja persis | ✓ Pasal 3 ayat (3) ada | gugur |
| Skor di atas ambang; klaim "tidak ada" memang tidak ada di naskah | ✓ | gugur |
| Bentuk tidak melewati baris Respons analisisnya | ✓ | diturunkan |
| `usulan`: pengganti muat di tempat yang dicoret, kata tambahannya bersumber | ✓ | turun jadi `catatan` |
| Pembanding korpus ada di hasil `cari_korpus` yang tercatat | — | gugur |
| Rujukan dari baris Dasar; Dasar kosong → rujukan agen terbukti | — prioritas penelaah, tanpa baris rujukan | rujukan dibuang |
| Calon kembar | — | digabung |

→ lolos sebagai **usulan hijau**.

### 5. Panel dan Word

Di Word, kutipan dicoret merah dan rumusan pengganti dari agen disisipkan
hijau di sebelahnya, dengan komentar ringkas:

```
Temuan:
Rumusan ini dapat dibaca mewajibkan nomor daftar barang bagi seluruh permohonan
sebagaimana dimaksud pada ayat (1) atau ayat (2), atau hanya bagi permohonan atas
barang yang tercantum dalam Lampiran I.
(T1)
```

Di panel: kartu T1 berlabel usulan, dengan Lompat ke Teks, Terima, Tolak.
Penelaah yang memutuskan. Calon 2 tidak muncul di mana pun.

## Contoh 2 — putaran format

Nomor paragraf, label, dan format di bawah dibaca dari berkas asli PMK 45; di
add-in, Office.js yang membacanya.

### 1. Yang dikirim ke agen

**Bahan** — sama untuk PMK, KMK, atau jenis naskah lain; tidak ada penilaian
di dalamnya:

```
== FORMAT DOKUMEN ==
Kertas 21,0 × 33,0 cm · marjin halaman pertama: atas 8,0 · bawah 2,5 · kiri 2,5 · kanan 2,5 cm
Kepala halaman: nomor halaman (kolom PAGE)

== NASKAH UTUH BERFORMAT ==
¶0   PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA   ⟨Bookman Old Style 12 · tengah⟩
¶3   [judul] PEMBEBASAN BEA MASUK ATAS IMPOR …       ⟨Bookman Old Style 12 · tengah⟩
¶5   DENGAN RAHMAT TUHAN YANG MAHA ESA               ⟨… · tengah · 1 baris kosong sebelumnya⟩
¶10  [menimbang-a] Menimbang : a. bahwa ketentuan …  ⟨… · rata kiri-kanan · kiri 5,1 cm · baris pertama -5,1 cm · 2 baris kosong sebelumnya⟩
¶11  [menimbang-b] b. bahwa untuk menunjang …        ⟨… · rata kiri-kanan · kiri 5,0 cm · baris pertama -1,3 cm⟩
¶13  [menimbang-c] c. bahwa berdasarkan …            ⟨… · rata kiri-kanan · kiri 4,4 cm · baris pertama -1,3 cm⟩
¶23  MEMUTUSKAN:                                     ⟨… · tengah · 3 baris kosong sebelumnya⟩
¶24  [menetapkan] Menetapkan : PERATURAN MENTERI …   ⟨… · rata kiri-kanan · kiri 3,8 cm · baris pertama -3,8 cm⟩
¶36  [pasal-1-angka-6] Sistem Indonesia National Single Window …
                                                     ⟨… · rata kiri-kanan · miring: "National Single Window"⟩
…
¶483 [penutup] Ditetapkan di Jakarta                 ⟨… · kiri 5,1 cm · 2 baris kosong sebelumnya⟩
```

(`…` di dalam ⟨⟩ = "Bookman Old Style 12"; di bahan sungguhan ditulis utuh.
Seluruhnya 537 paragraf, ±17 rb token tambahan.)

**Tugas putaran** — analisis dari `analisisformat.md`, mis.:

```
## F-11 · Jarak antarblok pembukaan
Berlaku untuk: pmk-standar
Respons: catatan
Lingkup: format
Dasar: KMK 527 Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85 (visual)
### Yang diperiksa
- jumlah baris kosong di antara blok pembukaan
### Cara memeriksa
Ambil jarak yang benar dari skill format. Bandingkan dengan "n baris kosong
sebelumnya" dan spasi paragraf pada baris pembuka tiap blok.
```

**Skill** — `pmk-standar/format/SKILL.md`. Untuk KMK, skill inilah yang
diganti; bahannya tetap sama:

```
- Huruf Bookman Old Style, ukuran 12 — Lampiran III huruf A keterangan angka 1 huruf a angka 1)–2), hlm 87
- Kertas F4, 21 × 33 cm — … huruf b angka 1)–2), hlm 87
- Marjin atas halaman pertama 8 cm; bawah, kiri, kanan 2,5 cm — … angka 3), hlm 87
- Judul → Dengan Rahmat → jabatan pembentuk: 1 enter; jabatan pembentuk → Menimbang: 2 enter;
  Menimbang → Mengingat → MEMUTUSKAN → Menetapkan → BAB I: masing-masing 1 enter
  — Lampiran III huruf A angka I–VIII, hlm 74–85
```

**Alat:** `muat_skill`, `cari_teks`, `cari_format`, `ringkas_menjorok`, `catat_temuan`,
`selesai` — tanpa `cari_korpus`, karena tidak ada analisis ber-`Butuh: korpus`
di putaran ini.

### 2. Yang dikerjakan agen

```
1. muat_skill pmk-standar/format
2. FORMAT DOKUMEN: kertas 21 × 33 ✓ · marjin atas 8,0 ✓ · bawah, kiri, kanan 2,5 ✓
3. cari_format(huruf="Bookman Old Style", ukuran=12)
   → 8 paragraf berbeda: "Ditandatangani secara elektronik" (ukuran 10), kepala
     Lampiran II (ukuran 9), dua judul contoh format di Lampiran II (ukuran 10)
4. Jarak antarblok, dibandingkan dengan skill:
   ¶5 Dengan Rahmat 1 ✓ · ¶10 Menimbang 2 ✓ · ¶23 MEMUTUSKAN 3 ✗ (kaidah 1) ·
   ¶24 Menetapkan 0 ✗ (kaidah 1)
5. catat_temuan untuk yang menyimpang, lalu selesai
```

### 3. Penilai kedua, gerbang, lalu Word

Gerbang tidak tahu kaidahnya; ia hanya mencocokkan bukti dengan bacaan: ¶23
memang tercatat "3 baris kosong sebelumnya" ✓, kutipan "MEMUTUSKAN:" ada di
¶23 ✓ → lolos sebagai kuning:

```
Temuan:
Di atas "MEMUTUSKAN:" ada 3 baris kosong; kaidahnya 1.
KMK 527/KMK.01/2022 Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85 (T3)
```

Temuan jarak di atas berasal dari data asli PMK 45, tetapi **belum
dicocokkan dengan tampilan di Word** — jarak bisa juga dibuat dengan spasi
paragraf, dan bacaan contoh ini belum memuat spasi.
