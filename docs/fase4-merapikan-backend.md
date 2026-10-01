# Fase 4 — Agen penuh dengan skills

> **Rancangan, belum dikerjakan.** Dipilih penelaah 30 Sep 2026: agen penuh.
> Pemeriksaan dibagi dua: **yang hanya bisa dikerjakan program masuk Fase 1;
> sisanya dikerjakan agen**, ditulis di `skills/analisis/analisis.md`. Fase 4
> hanya memindahkan pemeriksaan yang **sudah ada**; pemeriksaan baru diambil
> dari bagian 6 setelah disetujui penelaah. Rujukan ke KMK 527 ditulis sebagai
> alamat lengkap — cara membacanya di awal bagian 6. Pertanyaan yang belum
> diputuskan ada di bagian terakhir.

## 0.1 Yang ditelaah Biro Hukum atas rancangan peraturan

Menurut KMK 527 Lampiran I BAB II angka 11 (hlm 21), penelaahan Biro Hukum
atas rancangan PMK dan KMK meliputi tiga hal: **(a) pengharmonisasian,
pemantapan, dan pembulatan konsepsi**; **(b) sinkronisasi**; dan **(c)
penyesuaian teknik perancangan** (*legal drafting*). Tabel di bawah merinci
(a) dan (b); (c) adalah Lampiran II dan III, yang dirinci di bagian 6.
Drafter Analiser membantu sebagian; sisanya penilaian kebijakan yang tetap
dikerjakan penelaah.

| Filter | Pertanyaan | Dasar di KMK 527 | Bantuan alat |
|---|---|---|---|
| **Kewenangan** | Apakah Menteri Keuangan memang berwenang mengatur? | Lampiran I BAB II angka 8 huruf b angka 1), hlm 20; Lampiran III huruf E Daftar I angka 2 huruf a, hlm 93 | K-04 — belum dibangun |
| **Hierarki** | Apakah tidak bertentangan dengan aturan yang lebih tinggi? | Lampiran I BAB II angka 8 huruf b angka 2), hlm 20; Lampiran III huruf C keterangan angka 3, hlm 89; Lampiran III huruf E Daftar I angka 2 huruf b, hlm 93 | F3-001 — sudah, mati bawaan |
| **Setingkat** | Apakah tidak bertabrakan dengan aturan setingkat? | Lampiran III huruf C keterangan angka 4, hlm 89 | F3-001 — sudah, mati bawaan |
| **Putusan pengadilan** | Apakah sesuai dengan putusan pengadilan yang relevan? | Lampiran I BAB II angka 8 huruf b angka 3), hlm 20; Lampiran III huruf C keterangan angka 5, hlm 89–90 | K-10 — korpus putusan belum ada |
| **Rekomendasi BPK** | Apakah sesuai dengan rekomendasi Badan Pemeriksa Keuangan? | Lampiran I BAB II angka 8 huruf b angka 3), hlm 20 | D-04 — korpus BPK belum ada |
| **Simplifikasi** | Apakah materinya bisa digabung dengan peraturan yang sudah ada? | Lampiran I BAB II angka 13 huruf c, hlm 21 | D-03 — belum dibangun |
| **Dampak** | Apa dampaknya kepada publik, usaha, ekonomi, hak warga, pelayanan? | Lampiran I BAB II angka 1 huruf a, hlm 16; Lampiran III huruf C keterangan angka 2, hlm 89 | D-01, D-06 — bahan pertimbangan |
| **Risiko & mitigasi** | Apa risiko/efek samping dan bagaimana mengatasinya? | Lampiran I BAB II angka 1 huruf a, hlm 16 | penilaian penelaah |
| **Cost-benefit & alternatif** | Apakah manfaatnya sebanding dengan biayanya dan apakah PMK memang instrumen yang tepat? | Lampiran I BAB II angka 1 huruf b–c, hlm 16 | D-07 — bahan pertimbangan |

## 1. Struktur folder sesudah Fase 4

```
backend/
├── app/
│   ├── aturan_deterministik/      HANYA yang AI tidak bisa — program · instan · gratis
│   │   ├── aturan.json            daftar pemeriksaan program: kode, judul, dasar, warna
│   │   ├── korpus_pasti.py        status dasar hukum di OpenSearch — F3-002, dipindah
│   │   └── (bila disetujui, bagian 6.1)  format_berkas.py · kapital_judul.py
│   │
│   ├── telaah/                    agen
│   │   ├── alur.py
│   │   ├── tahap1_bahan/          menyiapkan bacaan: peta letak pasal/ayat (parser) ·
│   │   │                          naskah berlabel untuk agen · peraturan lain yang
│   │   │                          dirujuk naskah, dari korpus (bila dibutuhkan)
│   │   ├── tahap2_agen/           pembagi kelompok pasal, putaran, alat, pemuat
│   │   │                          analisis dan skill, pengaman macet, peran dasar
│   │   ├── tahap3_verifikasi.py   gerbang — satu-satunya tempat temuan lahir
│   │   └── ekspor/                bahan · jejak agen · verifikasi
│   │
│   └── api/  bersama/  core/  db/  models/      tetap; db ikut menyimpan jejak agen
│
└── skills/                        teks saja, tanpa kode — bisa ditinjau penelaah
    ├── analisis/
    │   ├── analisis.md            APA yang diperiksa agen — semua analisis, satu per bagian
    │   └── _TEMPLATE.md           formulir: disalin untuk analisis baru
    ├── pmk-standar/               KAIDAH KMK 527 per bagian naskah, beralamat lengkap —
    │   │                          dimuat agen bila perlu
    │   ├── pembukaan/SKILL.md     judul, Menimbang, Mengingat, Menetapkan
    │   ├── batang-tubuh/SKILL.md  pasal, ayat, rincian, Ketentuan Umum, Peralihan, Penutup
    │   ├── lampiran/SKILL.md
    │   └── penutup/SKILL.md       Ditetapkan, Diundangkan, Berita Negara
    ├── korpus/SKILL.md            cara mencari dan menilai pembanding di OpenSearch
    └── (nanti) kmk/  pmk-perubahan/ …   — masing-masing berisi empat bagian yang sama

frontend/src/
├── lib/office.ts                  + sisipan satuan baru, sorotan tanpa komentar;
│                                  (bila format berkas disetujui) + membaca format dokumen
└── app/taskpane/page.tsx          daftar pemeriksaan dibaca dari backend
```

**Formulir analisis — `skills/analisis/_TEMPLATE.md`.** Menambah analisis
cukup menyalin formulir ini ke bagian baru di `analisis.md` lalu mengisinya:

```markdown
## Kode · Judul analisis

Berlaku untuk: pmk-standar     ← jenis naskah; boleh lebih dari satu, dipisah koma
Respons: otomatis              ← otomatis · usulan · catatan · dibuang (bagian 3)
Lingkup: per pasal             ← per pasal · seluruh naskah · lampiran (bagian 2)
Komentar: lengkap              ← lengkap · ringkas
Dasar: KMK 527 Lampiran II angka III huruf C.2 butir 72, hlm 46 (visual)
                               ← alamat lengkap; atau: prioritas penelaah;
                                  boleh kosong — agen mencarikan (bagian 3.2)
Butuh: —                       ← mis. korpus; bahan korpus; pembaca diktum KMK

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
```

Enam baris di atas dibaca kode: pemuat (jenis naskah, lingkup, prasyarat),
panel Pengaturan, dan gerbang (batas respons, bentuk komentar, rujukan). Bagian di
bawahnya dibaca agen; dua bagian pertama juga tampil di panel. Dasar yang
diisi manusia dicocokkan dulu ke citra halaman PDF KMK 527 — `(visual)`, atau
`(turunan)` bila aturannya akibat butir itu, bukan bunyinya.

Agen tidak bisa membuat alat baru. Analisis yang butuh bacaan yang belum ada —
mis. ukuran huruf atau marjin dari berkas Word — menunggu pembacanya dibuat di
kode; menulis barisnya saja di `analisis.md` tidak cukup.

**Yang hilang:** `rules/` — isi `format_baku.py` pindah ke `analisis.md`
(yang terbaca dari teks) dan ke bagian 6.1 (kapital dari gaya huruf), tabel
`rujukan_kmk527.py` pindah ke baris Dasar; `bersama/prompt.py` (isinya ke
`analisis.md` dan skills); `tahap3_cari_dugaan`, `tahap4_memastikan/`,
`mekanis_konsistensi`; keberatan AI atas temuan Fase 1 (`catatan_ai`);
`aturan-fase1.ts` dan `aturan-fase2.ts`.

**Sengaja belum dioptimalkan:** jenis naskah berikutnya mendapat empat skill
bagiannya sendiri walau sebagian kaidahnya sama — dirapikan kalau jenis kedua
sudah ada. Versi pertama PMK biasa saja, sesuai skop sekarang.

**Menambah jenis naskah = skill + pembaca struktur.** Skill (teks) memberi
agen kaidahnya. Label satuan — `[pasal-5-ayat-2]` — tetap butuh pembaca
struktur jenis itu di `tahap1_bahan/`: Pasal I naskah perubahan berisi
pasal-pasal milik peraturan induk, dan omnibus mengubah beberapa peraturan
sekaligus; tanpa label yang pasti, agen tidak bisa menunjuk tempat dan Word
tidak bisa ditandai. Pembacanya ditulis kode, atau diusulkan AI lalu
dibuktikan kode — dipilih saat jenis kedua digarap, diuji di naskah nyata.

## 2. Alur

**Yang tidak berubah dari sekarang:** cara panel membaca naskah dari Word,
gerbang verifikasi, dan arti warna. **Agen bebas memilih langkah, tetapi
tidak pernah bebas menandai naskah** — semua yang ditemukannya lewat gerbang
kode dulu. Model: versi OpenAI terbaru di Azure (Luna atau Terra), diatur di
`.env`. Biaya tidak dibatasi.

```
1. PENELAAH       memilih jenis naskah (PMK), lalu menekan Jalankan Analisis.
                  Panel membaca seluruh paragraf naskah dari Word; tabel
                  > 1.000 baris hanya dibaca 5 baris contohnya.
                       │
2. ATURAN         aturan_deterministik/                kode · instan · gratis
   DETERMINISTIK  Hanya pemeriksaan yang AI tidak bisa:
                  · status dasar hukum di Mengingat, dicek ke korpus
                  · bila disetujui (bagian 6.1): kapital judul dari gaya
                    huruf, marjin dan ukuran kertas
                  Temuannya LANGSUNG tampil di panel dan Word, lalu ikut
                  diberikan ke agen supaya tidak diulang.
                       │
3. TAHAP 1        telaah/tahap1_bahan/                 kode · detik · gratis
   BAHAN          · naskah bernomor — seluruh paragraf, satu baris per
                    paragraf, tiap satuan berlabel [pasal-5-ayat-2], tabel
                    lampiran per baris sel, gambar ditulis "tidak terbaca"
                  · bahan di atas ±100 rb token → tabel data sejenis di
                    lampiran diringkas jadi kerangka (judul kolom + 3 baris);
                    isinya tetap bisa dibuka agen dengan alat
                  · pohon satuan — letak tiap pasal, ayat, huruf, angka di
                    Word; dipakai gerbang untuk membuktikan letak
                  · bahan korpus, hanya bila ada analisis yang membutuhkannya:
                    peraturan yang disebut naskah, status dan teks pasal
                    yang dirujuknya
                       │
4. TAHAP 2        telaah/tahap2_agen/                  AI · menit
   AGEN           a. Kode memilih analisis dari analisis.md: berlaku untuk
                     PMK, dan prasyarat di baris Butuh tersedia.
                  b. Kode membagi kerja menjadi putaran, menurut baris Lingkup:
                       per pasal       satu putaran per kelompok ≤ 6 pasal
                                       atau ≤ 4.000 token teks pasal
                                       (PMK 45: 6 putaran). Pasal TIDAK
                                       PERNAH dibelah: pasal yang membuat
                                       kelompok lewat 4.000 pindah UTUH ke
                                       kelompok berikutnya; satu pasal yang
                                       sendirian > 4.000 jadi kelompok
                                       sendiri, tetap utuh. Angka ini hanya
                                       membagi TUGAS, tidak memotong bacaan.
                       seluruh naskah  satu putaran
                       lampiran        satu putaran, bila naskahnya berlampiran
                  c. Semua putaran berjalan bersamaan. Tiap putaran mulai dengan:
                       naskah bernomor UTUH · temuan langkah 2 · bahan korpus
                       (bila ada) · analisis putaran itu · pasal fokus ·
                       daftar skill
                     Yang dibatasi hanya pasal yang wajib DINILAI; yang
                     DIBACA tetap seluruh naskah.
                  d. Di tiap putaran agen memilih sendiri langkahnya, berulang:
                       muat_skill     membaca kaidah KMK 527 bagian naskah itu
                       cari_teks      mencari di seluruh naskah, termasuk tabel
                       buka_tabel     membuka baris tabel yang dikirim kerangkanya
                       jumlah_kolom   menjumlah angka satu kolom tabel
                       cari_korpus    mencari pembanding di peraturan lain;
                                      hanya ada di putaran yang analisisnya
                                      Butuh: korpus
                       catat_temuan   mencatat calon temuan; kutipan > 200
                                      huruf atau melewati satu paragraf
                                      ditolak saat itu juga, agen mengutip ulang
                  e. Agen menutup putaran dengan SELESAI: status tiap analisis
                     untuk tiap pasal fokus (diperiksa · tidak relevan). Yang
                     tidak dilaporkan ditagih sekali; tetap tidak → dicatat
                     "tidak diperiksa", tidak pernah dianggap bersih.
                  Kode menjaga: putaran macet dihentikan · kuota Azure penuh
                  (429) → menunggu, bukan gagal · tiap langkah disimpan, jadi
                  backend yang mati di tengah jalan melanjutkan tanpa bayar ulang.
                  KELUAR: calon temuan + laporan tiap pasal + jejak langkah.
                  Belum ada yang menyentuh Word.
                       │
5. TAHAP 3        telaah/tahap3_verifikasi.py          kode · detik · gratis
   VERIFIKASI     Satu-satunya tempat temuan lahir. Tiap calon temuan diuji.
                  GUGUR bila:
                  · kutipannya tidak persis ada di satuan yang disebut
                  · nomor pasal yang disebut tidak ada
                  · skornya di bawah ambang
                  · yang diklaim "tidak ada" ternyata ada di naskah
                  · pembanding korpusnya tidak ada di hasil cari_korpus
                  · tempat sisipan satuan barunya tidak ada di pohon
                  DITURUNKAN jadi kuning bila:
                  · bentuknya melewati baris Respons analisisnya
                  · usulan tidak muat di tempat yang dicoret, kata
                    tambahannya tidak bersumber, atau istilah berdefinisi
                    tidak dieja persis → usulannya jadi contoh di Saran
                  · dibuang bukan karena salah satu dari tiga alasan yang
                    bisa dibuktikan kode (bagian 3.1)
                  DILENGKAPI:
                  · rujukan dari baris Dasar; Dasar kosong → rujukan agen
                    yang terbukti ada di teks skill atau korpus; tidak
                    terbukti → tanpa rujukan
                  · isi sisipan cocok dengan korpus → Sumber usulan menyebut
                    peraturannya; tidak → "(prediksi AI)"
                  · calon kembar digabung ("+n tempat lain"); yang
                    bertindihan dengan temuan langkah 2 dibuang
                  · letak tidak pasti → hanya di panel, tidak ditandai
                  Calon yang gugur tidak tampil di panel maupun Word.
                       │
6. PANEL DAN WORD Penandaan, dengan pelacakan perubahan dimatikan selama
                  menandai: coret merah + hijau, kuning, komentar; sisipan
                  satuan baru dipasang paling akhir, dari bawah ke atas.
                  Kartu di panel; penelaah memutuskan lewat Terima / Tolak.
                  Rinciannya bagian 3.
```

**Kenapa kerja agen dibagi per kelompok pasal** (ditetapkan penelaah 1 Okt
2026). Diuji berbayar pada PMK 45: kalau seluruh pasal dinilai dalam satu
panggilan, AI tetap menjawab ke-29 pasal, tetapi penilaiannya dangkal —
rata-rata 3,5 kesalahan nyata per kali analisis, dan hanya 1 kalau semua
pemeriksaan digabung dalam satu panggilan. Dipecah per kelompok menemukan
5,5. Yang membagi kode, bukan agen: pekerjaannya hanya menghitung pasal dan
token, dan tiap pasal wajib masuk tepat satu kelompok.

Contoh satu kesalahan nyata ditelusuri dari tahap 1 sampai Word:
[`jelaskan.md`](jelaskan.md).

## 3. Daftar respons yang bisa diberikan agen

### 3.1 Bentuk tanda di Word — pilihan baris `Respons`

**Urutan pilihan agen** (ditetapkan penelaah 30 Sep 2026): **usulan** bila
ada rumusan pengganti yang benar → **dibuang** bila naskah sudah benar tanpa
teks itu → **catatan**.

| Respons | Di Word | Label kartu | Syarat di gerbang |
|---|---|---|---|
| `usulan` | teks salah merah dicoret, pengganti hijau disisipkan di sebelahnya | usulan | kutipan persis ada; pengganti muat di tempat yang dicoret; tiap kata tambahan bersumber dari naskah sendiri atau peraturan berlaku; istilah berdefinisi dieja persis. Gagal → turun jadi `catatan`, usulannya pindah ke Saran sebagai contoh rumusan |
| `dibuang` | merah dicoret, tanpa pengganti | dibuang | naskah benar tanpa teks itu, dan alasannya bisa dibuktikan kode: teks tidak dipakai / tidak ada (dicari di seluruh naskah), mengulang teks di tempat lain (dibandingkan), atau frasa yang dilarang kaidah. Hapus yang hanya berdasar penilaian agen tetap diusulkan, tetapi kuning dengan Saran "hapus …" (ditetapkan 30 Sep 2026) |
| `catatan` | sorot kuning, warna huruf tidak diubah | catatan | kutipan persis ada di satuannya |
| `otomatis` | agen memilih menurut urutan di atas untuk tiap temuan | — | sama dengan bentuk yang dipilih |

**Baris Respons adalah batas atas.** Gerbang boleh menurunkan (`usulan` →
`catatan`), tidak pernah menaikkan: tidak ada pengaturan yang bisa memaksa
hijau tanpa bukti.

**Perbaikan di tempat lain** (ditetapkan penelaah 30 Sep 2026, disarankan
mentornya). Kalau perbaikannya ada di satuan lain — mis. kata "RCA" di Pasal
5 belum didefinisikan, perbaikannya di Pasal 1 — perbaikannya **disisipkan
langsung di tempatnya sebagai satuan baru** yang sesuai: angka definisi baru
di Pasal 1, ayat baru, atau pasal baru. Komentar (Temuan, Saran, rujukan)
menempel di sisipan itu. Di tempat temuan, kata "RCA" cukup **disorot tanpa
komentar**; mengklik sorotan itu memusatkan kartunya di panel. Penelaah
tetap yang memutuskan lewat Terima dan Tolak.

**Isi sisipan** (ditetapkan penelaah 1 Okt 2026):
1. **Dicari dulu di korpus OpenSearch** — mis. arti "RCA" di peraturan lain
   yang masih berlaku. Definisi yang sama di peraturan yang dilaksanakan
   atau PMK sebidang memang wajib sama rumusannya (Lampiran II angka III
   huruf C.1 butir 62 dan 65, hlm 45). Ketemu → disalin persis, dan baris
   **Sumber usulan** menyebut peraturan dan pasalnya.
2. **Tidak ketemu → agen memperkirakan artinya dari isi naskah sendiri**,
   dan baris Sumber usulan tertulis **(prediksi AI)**.
3. Tidak bisa diperkirakan → tidak disisipkan; tempat temuan disorot kuning.

Sisipan 1 dan 2 sama-sama hijau; pembedanya di baris Sumber usulan.

Tiga keadaan lain ditentukan kode, bukan dipilih:

| Keadaan | Di Word | Di panel |
|---|---|---|
| Kesalahannya ketiadaan sesuatu yang tidak bisa disisipkan | komentar tanpa warna di satuan terdekat atau baris judul | kartu biasa |
| Rentang tidak ketemu, atau letak sesudah tabel raksasa | tidak ditandai | lencana "tidak ditandai di naskah" + tombol Alasan |
| Temuan tanpa lokasi sama sekali | tidak ditandai | pita peringatan di atas daftar |

### 3.2 Isi komentar Word

| Baris | Diisi | Boleh tidak muncul? |
|---|---|---|
| **Temuan:** kenapa salah | agen | tidak — selalu ada |
| **Perbaiki di:** | agen menunjuk, kode membuktikan tempatnya ada | ya — tidak muncul bila perbaikannya di tempat temuan itu, atau bila perbaikannya sudah disisipkan di tempatnya |
| **Juga di:** | kode, menggabung kesalahan kembar | ya |
| **Saran:** | agen | ya — dilewati pada `usulan`, dikosongkan bila tidak ada jalan keluar yang pasti |
| **Sumber usulan:** | kode, dari bukti yang lolos gerbang; sisipan yang isinya tidak ketemu di korpus: **(prediksi AI)** | wajib pada `usulan` dan sisipan |
| **Pembanding:** *(baru)* | agen mengutip, kode membuktikan ada di hasil pencarian korpus | wajib bila temuannya bersandar pada peraturan lain |
| Rujukan + **(T-n)** | baris Dasar — alamat lengkap KMK 527; bila Dasar kosong, dicarikan agen dan dibuktikan kode; (T-n) oleh kode | rujukan tidak muncul bila dasarnya prioritas penelaah, atau Dasar kosong dan agen tidak menemukannya; (T-n) selalu ada |

**Dasar kosong** (ditetapkan penelaah 30 Sep 2026): agen mencarikan
rujukannya sendiri, dari dua tempat saja —
- kaidah KMK 527: teks skill `pmk-standar/`, yang ditulis dari rangkuman
  yang sudah dicocokkan ke citra PDF, lengkap dengan alamatnya. Kode
  memeriksa alamat dan kutipan yang disebut agen benar-benar ada di teks
  skill itu;
- peraturan lain: hasil `cari_korpus`. Kode memeriksa peraturan dan pasalnya
  ada di hasil pencarian.

Rujukan yang dicarikan agen berlencana "rujukan belum diverifikasi" sampai
alamatnya disalin ke baris Dasar. Tidak ketemu → komentar tanpa baris
rujukan, tidak dikarang. KMK 527 sendiri tidak dicari di korpus: dicek 30 Sep
2026, KMK 527 tercatat di korpus tetapi isinya tidak terindeks per butir, dan
teks salinannya hasil OCR (CLAUDE.md butir 4).

`Komentar: ringkas` hanya membuang yang opsional — Saran. Temuan, Sumber
usulan, Pembanding, dan rujukan tetap, karena itulah bukti yang bisa
diperiksa penelaah.

Contoh komentar lengkap, dan yang ringkas:

```
Temuan:
Batas 30 hari berpotensi bertentangan dengan PMK 5/2023 Pasal 8 (14 hari).
Saran:
Selaraskan batas waktunya, atau sebutkan alasan perbedaannya.
Pembanding: PMK 5/2023 Pasal 8 (masih berlaku)
KMK 527/KMK.01/2022 Lampiran III huruf C keterangan angka 4 (hlm 89) (T21)
```

```
Temuan:
Kata "dapat" di ayat (2) bertabrakan dengan "wajib" di ayat (1) untuk
kewajiban yang sama.
(T7)
```

Komentar di sisipan definisi baru — isinya dari korpus, dan perkiraan agen:

```
Temuan:
"RCA" dipakai di Pasal 5 ayat (2) tetapi belum didefinisikan di Pasal 1.
Sumber usulan: PMK 12/2024 Pasal 1 angka 9 (masih berlaku)
KMK 527/KMK.01/2022 Lampiran II angka III huruf C.1 butir 58 huruf b, hlm 44 (T9)
```

```
Temuan:
"RCA" dipakai di Pasal 5 ayat (2) tetapi belum didefinisikan di Pasal 1.
Sumber usulan: (prediksi AI)
KMK 527/KMK.01/2022 Lampiran II angka III huruf C.1 butir 58 huruf b, hlm 44 (T9)
```

### 3.3 Kartu di panel

| Bagian kartu | Muncul bila |
|---|---|
| Nomor T-n, label (usulan · dibuang · catatan), lencana Fase | selalu |
| Cuplikan teks yang ditandai | selalu |
| Tombol **Lompat ke Teks**, **Terima**, **Tolak** | selalu |
| Tombol **Lihat sorotan** | perbaikannya disisipkan di satuan lain — melompat ke kata yang disorot di tempat temuan |
| Lencana "+n tempat lain" | ada kesalahan kembar |
| Lencana "tidak ditandai di naskah" + tombol **Alasan** | temuan hanya di panel |
| Lencana "rujukan belum diverifikasi" · "dasar turunan" | status rujukannya bukan visual — termasuk rujukan yang dicarikan agen |

Calon temuan yang tidak lolos gerbang tidak punya kartu (ditetapkan penelaah
30 Sep 2026): temuan tanpa bukti dianggap halusinasi, jadi tidak tampil di panel
maupun di Word.

## 4. Urutan pengerjaan

0. **Uji berbayar alur sekarang** pada PMK 17, 45, 104, 119 — angka
   pembanding untuk langkah 7.
1. **Formulir dan pemuat:** `_TEMPLATE.md`, pembaca `analisis.md` berikut
   validasinya, dan daftar pemeriksaan untuk panel.
2. **Tulis `analisis.md` dan skills PMK biasa dari pemeriksaan yang sudah
   ada:** aturan Fase 1 yang aktif, F2-001/003/004/007, F2-101…106,
   F3-001/003; kaidah KMK 527 beralamat lengkap ke `pmk-standar/` dan
   `korpus/`. Pemeriksaan baru dari bagian 6 hanya bila disetujui.
3. **Bangun tahap 2 agen** — termasuk bahan korpus dan aturan kutipan; diuji
   dengan klien palsu, tanpa biaya.
4. **Gerbang:** batas dan urutan respons, rujukan, pembanding, sisipan satuan
   baru.
5. **Aturan deterministik:** F3-002 dipindah ke `korpus_pasti.py`.
6. **Panel dan Word:** daftar pemeriksaan dari backend, sisipan satuan baru
   dan sorotan tanpa komentar, tombol Lihat sorotan, kemajuan per langkah
   agen, ekspor jejak agen.
7. **Alur lama tetap ada di balik saklar `.env` sampai agen terbukti.** Uji
   berbayar yang sama: temuan benar tidak berkurang, salah tandai tidak
   bertambah, tidak ada analisis yang gagal karena kuota atau gagal ditandai
   karena kutipan terlalu panjang. Temuan lemah (pertanyaan 1) dan beda hasil
   antar-run (pertanyaan 2) dihitung terpisah. Empat pemeriksaan yang sekarang
   dikerjakan kode — rujukan ada, nomor berurut, angka dan huruf bilangan
   cocok, istilah Pasal 1 dipakai — jadi kunci jawaban: agen wajib menemukan
   semua yang ditemukan kode.
8. **Hapus alur lama dan aturan kode lama;** CLAUDE.md dan dokumen disamakan.

## 5. Rincian pengerjaan — untuk model yang mengerjakan

Bagian yang bergantung pada pertanyaan terbuka ditandai, dan tidak dikerjakan
sebelum pertanyaannya dijawab.

### 5.1 `analisis.md` dan formulirnya

- `backend/skills/analisis/analisis.md` memuat semua analisis; tiap analisis
  satu bagian `## Kode · Judul`. `_TEMPLATE.md` di folder yang sama, tidak
  dimuat sebagai analisis.
- Kepala tiap bagian berupa baris `Kunci: nilai` persis seperti formulir.
  Wajib: Kode, Judul, Berlaku untuk, Respons, Lingkup. Opsional: Komentar (bawaan
  `lengkap`), Dasar (boleh kosong — agen mencarikan, bagian 3.2), Butuh.
- Dasar ditulis sebagai alamat lengkap: Lampiran → angka → huruf/subbagian →
  butir → huruf/angka di dalam butir → halaman PDF.
- Nilai di luar pilihan, kunci wajib kosong, atau kode kembar → backend
  **menolak menyala** dan menyebut analisisnya. Tidak pernah dilewati
  diam-diam.
- Kode lama dipertahankan (F1-…, F2-…, F3-…) supaya penelaah mengenalinya;
  analisis baru memakai kode di bagian 6.

### 5.2 Pemilihan dan bahan sebelum agen jalan

- Dikirim ke agen bila: Berlaku untuk memuat jenis naskah yang dipilih
  penelaah; tiap isi Butuh tersedia (korpus: Fase 3 dinyalakan dan
  OpenSearch terhubung; pembaca struktur jenis naskah ada).
- Yang tidak memenuhi tidak dikirim; panel menyebut alasannya — "belum
  tersedia untuk KMK", "korpus tidak terhubung".
- **Bahan korpus** hanya disusun bila ada analisis terpilih ber-`Butuh:
  bahan korpus`: kode mengumpulkan semua peraturan yang disebut naskah —
  Mengingat, Menimbang, dan pasal ("sebagaimana dimaksud dalam Pasal 25 ayat
  (1) Undang-Undang Nomor …") — lalu mengambil statusnya dan teks pasal yang
  dirujuk dari korpus. Hasilnya dilampirkan sebagai pembanding, bukan temuan.
  Korpus dibaca saat analisis berjalan, jadi selalu mutakhir; teksnya hasil
  pemindaian, jadi kutipannya berpenanda "belum diverifikasi visual".
- **Pembagian putaran** menurut baris Lingkup (bagian 2): `per pasal` →
  satu putaran per kelompok pasal, dibentuk `kelompok_fokus` yang sekarang
  (≤ 6 pasal atau ≤ 4.000 token teks pasal). Pasal tidak pernah dibelah;
  tes penjaganya ikut dipindah: `test_pasal_dikelompokkan_tanpa_dibelah` dan
  `test_satu_pasal_panjang_tetap_satu_kelompok`. Angka 6 sudah di `.env`
  (`FASE2_PASAL_PER_FOKUS`); 4.000 masih tertanam di kode
  (`TOKEN_PER_FOKUS`) dan dipindah ke `.env`. `seluruh naskah` → satu
  putaran; `lampiran` → satu
  putaran bila naskahnya berlampiran.
- **Teks analisis dikirim di awal tiap putaran** — hanya analisis yang
  lingkupnya cocok dengan putaran itu, bukan dimuat sesuai kebutuhan: agen
  harus tahu semua pesanannya sejak langkah pertama. Skills (kaidah) yang
  dimuat sesuai kebutuhan.

### 5.3 Agen

- **Mesin:** putaran sendiri di `bersama/llm.py`, lanjutan alat tahap 4
  sekarang — tanpa dependensi baru, dan bisa dites tanpa biaya dengan klien
  palsu.
- **Model:** deployment di `.env` (Luna atau Terra). Keduanya model penalaran
  yang menolak `temperature=0`; `llm.py` sudah menanganinya.
- Urutan pesan awal: peran dasar → naskah (awalan sama persis di tiap
  langkah dan di tiap putaran) → hasil Fase 1 → bahan korpus (bila ada) →
  analisis putaran itu → pasal fokus → daftar skill (nama + deskripsi).
- Alat:

  | Alat | Gunanya |
  |---|---|
  | `muat_skill` | membaca `SKILL.md` sebuah skill |
  | `cari_teks`, `buka_tabel`, `jumlah_kolom` | seperti `tahap4_memastikan/alat.py` sekarang |
  | `cari_korpus` | pembanding di OpenSearch, hanya membaca. Hanya ditawarkan di putaran yang analisisnya `Butuh: korpus`. Hasilnya ≤ 5 peraturan yang masih berlaku, satu pasal paling mirip masing-masing — potongan, bukan peraturan utuh; dicatat kode untuk gerbang. "Tidak ketemu" tidak pernah jadi temuan |
  | `catat_temuan` | kode analisis, satuan, kutipan persis, bentuk, temuan, saran, usulan, sasaran, pembanding, rujukan (bila Dasar kosong), skor — bentuknya dicek saat itu juga |
  | `selesai` | status tiap analisis untuk tiap pasal fokus: diperiksa · tidak relevan, dengan alasan singkat |

- **Kutipan wajib bisa ditandai di Word.** Kutipan (`teks_asli`) adalah
  bagian terpendek yang benar-benar salah, paling panjang 200 huruf, di dalam
  satu paragraf — pencarian Word berhenti di sekitar 255 huruf, dan satu
  temuan hanya bisa menandai satu paragraf. Kutipan yang melanggar ditolak
  `catat_temuan` saat itu juga, dan agen diminta mengutip ulang. Bahan yang
  **dibaca** agen tetap utuh; yang dibatasi hanya yang **ditandai**.
- **Satu putaran = beberapa request.** AI tidak punya ingatan: tiap langkah
  mengirim ulang naskah + riwayat putaran itu. Yang dihemat jumlah
  langkahnya — agen boleh memanggil beberapa alat dan mencatat beberapa
  temuan dalam satu langkah.
- **Tanpa batas biaya, token, atau jumlah langkah.** Yang dijaga hanya
  **putaran macet**: alat yang sama dengan argumen yang sama berulang, atau
  sekian langkah tanpa temuan maupun status baru → agen dihentikan dan panel
  menyebut "analisis macet". Angkanya di `.env`.
- 429 → tunggu sesuai Retry-After, lalu lanjut.
- Jejak tiap langkah disimpan; backend yang mati di tengah jalan
  melanjutkan dari langkah terakhir tanpa bayar ulang.

### 5.4 Gerbang — `tahap3_verifikasi.py`, dari `tahap5_verifikasi.py`

- Seluruh pemeriksaan tahap 5 sekarang tetap: kutipan persis, nomor pasal
  ada, istilah dieja persis, skor di atas ambang, klaim "tidak ada"
  dibuktikan, kesalahan kembar digabung, letak tidak pasti.
- `_ATURAN_BOLEH_HIJAU` diganti baris Respons dan urutan bentuk: `catatan` →
  tidak pernah hijau; `usulan` dan `otomatis` → hijau hanya bila syarat bukti
  lolos; `dibuang` → hanya untuk tiga alasan yang bisa dibuktikan kode (bagian 3.1); selain itu turun jadi `catatan`.
- Rujukan dari baris Dasar, ditulis di komentar sebagai alamat lengkap; Dasar
  "prioritas penelaah" → tanpa baris rujukan. Dasar kosong → rujukan yang
  dicarikan agen (medan `rujukan` di `catat_temuan`: alamat + kutipan) wajib
  ditemukan kode di teks skill `pmk-standar/` atau di hasil `cari_korpus`
  yang tercatat; tidak ketemu → rujukannya dibuang, temuannya tetap.
- Pembanding yang tidak ada di hasil `cari_korpus` tercatat → temuan gugur.
- **Perbaikan di satuan lain:** sasaran wajib satuan yang terbukti ada di
  pohon; bentuk sisipannya mengikuti tempatnya (angka definisi, ayat, pasal);
  isinya dicocokkan dulu ke hasil korpus (definisi yang wajib sama menurut
  Lampiran II angka III huruf C.1 butir 62 dan 65, hlm 45) — cocok berarti
  bersumber, Sumber usulan menyebut peraturannya; tidak cocok berarti
  perkiraan agen dari naskah, Sumber usulan "(prediksi AI)" (bagian 3.1).
- Temuan ketiadaan yang tidak bisa disisipkan dipasang tanpa sorot; klaim
  "tidak ada"-nya dibuktikan pencarian kode.
- Calon temuan yang tidak lolos — kurang bukti (mis. skor di bawah ambang) atau
  terbantah (kutipannya tidak ada, atau klaim "tidak ada" ternyata ada) —
  **gugur**: tidak tampil di panel maupun Word. Alasannya gugur hanya
  tercatat di ekspor jejak agen, untuk diagnosa pengembang.

### 5.5 Aturan deterministik — `app/aturan_deterministik/`

- Fase 4: `korpus_pasti.py` = F3-002, dipindah dari
  `tahap2_persiapan/dasar_hukum.py` tanpa mengubah perilakunya.
- Bila bagian 6.1 disetujui:
  - `kapital_judul.py`: `font.allCaps` (WordApiDesktop 1.3) sudah pernah
    tidak menolong di Word penelaah; kandidatnya membaca `<w:caps/>` dari
    `getOoxml()` (WordApi 1.1) — dibuktikan di Word penelaah dulu.
  - `format_berkas.py`: marjin dan kertas dari `Word.PageSetup`
    (WordApiDesktop 1.3), cadangannya OOXML.
  - Tiap method Office.js diverifikasi ke `index.d.ts` dan punya jalur
    cadangan runtime (CLAUDE.md butir 8–9).

### 5.6 Panel, Word, dan migrasi

- **Sisipan satuan baru** (CLAUDE.md butir 5 sudah diubah 30 Sep 2026):
  - disisipkan **sebagai satuan terakhir** di tempat sasaran — angka definisi
    terakhir Pasal 1, ayat terakhir pasal — supaya nomor satuan yang sudah
    ada tidak bergeser; letak idealnya (mis. urutan definisi menurut
    Lampiran II angka III huruf C.1 butir 68, hlm 46) disebut di komentar;
  - disisipkan **paling akhir**, sesudah seluruh tanda lain terpasang, dari
    bawah ke atas — supaya nomor paragraf temuan lain tidak bergeser;
  - dibungkus penanda seperti tanda lain; **Tolak** dan **Kosongkan daftar**
    mencabutnya bersih, teks lama tidak tersentuh;
  - method Office.js penyisipan paragraf diverifikasi ke `index.d.ts` dulu
    (CLAUDE.md butir 8).
- **Sorotan tanpa komentar** di tempat temuan, dibungkus penanda bertag
  supaya kartu yang mengikuti kursor tetap menemukannya; tombol **Lihat
  sorotan** di kartu melompat ke sana.
- Daftar Pengaturan dibaca dari backend: `analisis.md` +
  `aturan_deterministik/aturan.json`, bentuknya seperti daftar sekarang.
  Kartu tetap ringkas.
- Ekspor jejak agen menggantikan ekspor tahap 3 dan 4. Isinya tiap langkah
  dan hasil alatnya, kutipan yang ditolak `catat_temuan`, laporan `selesai`
  per pasal, dan calon yang gugur di gerbang beserta alasannya — tidak ada
  yang dibuang diam-diam.
- Isi `analisis.md` pertama diambil dari `aturan-fase1.ts`,
  `aturan-fase2.ts` (diperiksa / tidak diperiksa), `prompt.py` (instruksi),
  `rujukan_kmk527.py` (Dasar, diubah ke alamat lengkap), dan
  `PARAMETER_LAMPIRAN` (F2-106).
- Keberatan AI atas temuan Fase 1 dihapus: medan `catatan_ai`, baris
  "Catatan AI:" di komentar, dan permintaan keberatan di panggilan lintas
  naskah.
- Saklar `.env`: `FASE2_ALUR = lama | agen`.
- Tes tanpa biaya: pemuat menolak formulir cacat; klien palsu memerankan
  agen (memanggil alat, mencatat temuan, kutipan terlalu panjang, status
  tidak lengkap, putaran macet, 429); gerbang menurunkan `usulan` pada
  analisis `Respons: catatan`; sisipan satuan baru tidak menggeser nomor
  satuan lain.

## 6. Fitur yang bisa dianalisis

Seluruh pemeriksaan yang bisa diturunkan dari KMK 527 — PDF-nya dibaca utuh
(batang tubuh, Lampiran I, II, III) beserta rangkumannya. Tiap butir ditulis
bersama kaidahnya, supaya bisa dipahami tanpa membuka KMK 527. **Tidak
dikerjakan di Fase 4**, kecuali yang sudah dibangun (✓, dipindah) atau yang
nanti disetujui penelaah. Kode mengikuti katalog rangkuman
(`tata-cara-penulisan-pmk-kmk527.md` Lampiran D); D-… berasal dari Lampiran I
dan III.

**Cara membaca alamat.** KMK 527 diktum KEDUAPULUHSATU (hlm 11) menyatakan
teknik penyusunan PMK dan KMK ada di **Lampiran II** dan bentuk serta
formatnya di **Lampiran III**; tahapan pembentukan ada di **Lampiran I**.
Alamat *Lampiran II angka III huruf C.2 butir 72, hlm 46* dibaca: Lampiran II
→ angka III (teknik penyusunan PMK dan KMK) → huruf C.2 (Batang Tubuh —
Materi Pokok) → butir 72 → halaman 46 PDF salinan JDIH. Nomor butir berjalan
terus dari 1 sampai 132 di seluruh Lampiran II. Susunan dan halamannya dicek
ke citra PDF 30 Sep 2026.

| Alamat | Isinya |
|---|---|
| Lampiran I BAB I–IV | tahapan: perencanaan, penyusunan (termasuk penelaahan Biro Hukum), penetapan, pengundangan dan salinan |
| Lampiran II angka I–II | jenis dan bentuk peraturan |
| Lampiran II angka III butir 1–2 | halaman pertama dan kerangka |
| … huruf A | Judul — butir 3–12 |
| … huruf B, B.1–B.5 | Pembukaan: frasa Dengan Rahmat, jabatan pembentuk, konsiderans, dasar hukum, diktum — butir 13–39 |
| … huruf C | Batang tubuh: umum, pasal dan ayat, tabulasi, diktum KMK — butir 40–55 |
| … huruf C.1–C.5 | Ketentuan Umum, Materi Pokok, Sanksi Administratif, Ketentuan Peralihan, Ketentuan Penutup — butir 56–108 |
| … huruf D | Penutup — butir 109–119 |
| … huruf E | Lampiran — butir 120–121 |
| Lampiran II angka IV | Peraturan Pimpinan Unit Organisasi Eselon I — butir 122 |
| Lampiran II angka V | Hal-hal khusus: pendelegasian, perubahan, pencabutan, salinan, nomor halaman — butir 123–132 |
| Lampiran III huruf A | bentuk dan format: bagan angka I–IX, keterangan angka 1–3 |
| Lampiran III huruf C | lembar analisis dampak dan kesesuaian |
| Lampiran III huruf E | daftar periksa penelaahan — Daftar I PMK, Daftar II KMK |

✓ sudah dibangun · ½ sebagian · *baru* belum ada di katalog

### 6.1 Deterministik — AI tidak bisa (35)

*Pembagian ini sedang ditinjau — pertanyaan 4.*

**Format berkas dan tata letak** — AI hanya membaca teks; ukuran, jarak, dan
letak dibaca program dari berkasnya.
- **F-01** Seluruh teks memakai huruf Bookman Old Style. *(Lampiran III huruf A keterangan angka 1 huruf a angka 1), hlm 87)*
- **F-02** Ukuran huruf 12. *(Lampiran III huruf A keterangan angka 1 huruf a angka 2), hlm 87)*
- **F-03** Kertas F4, 21 × 33 cm. *(Lampiran III huruf A keterangan angka 1 huruf b angka 1)–2), hlm 87)*
- **F-04** Marjin atas halaman pertama 8 cm untuk PMK dan KMK — ruang bagi lambang dan kepala halaman; 4 cm untuk peraturan pimpinan unit. *(Lampiran III huruf A keterangan angka 1 huruf b angka 3) huruf a), hlm 87)*
- **F-05** Marjin atas halaman kedua dan seterusnya 2,5 cm. *(Lampiran III huruf A keterangan angka 1 huruf b angka 3) huruf a), hlm 87)*
- **F-06** Marjin bawah, kiri, dan kanan masing-masing 2,5 cm. *(Lampiran III huruf A keterangan angka 1 huruf b angka 3) huruf b)–d), hlm 87)*
- **F-07** Spasi baris 1; jarak sebelum dan sesudah paragraf 0 pt. *(Lampiran III huruf A keterangan angka 1 huruf c, hlm 87)*
- **F-08** Halaman pertama tidak diberi nomor halaman. *(Lampiran II angka V butir 132 huruf a, hlm 73)*
- **F-09** Halaman kedua dan seterusnya bernomor di tengah atas, berbentuk `- 4 -`: diapit tanda hubung dan satu spasi. *(Lampiran II angka V butir 132 huruf a, hlm 73; Lampiran III huruf A keterangan angka 2, hlm 87)*
- **F-10** Nomor halaman lampiran melanjutkan nomor batang tubuh, tidak mulai lagi dari 1. *(Lampiran II angka V butir 132 huruf a, hlm 73)*
- **F-11** Jarak antarblok pembukaan: judul → Dengan Rahmat → jabatan pembentuk masing-masing 1 enter; jabatan pembentuk → Menimbang 2 enter; Menimbang → Mengingat → MEMUTUSKAN → Menetapkan → BAB I masing-masing 1 enter. *(Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85)*
- **F-17** Jarak antarblok batang tubuh: BAB dan judulnya tanpa baris kosong; judul bab → Bagian, Bagian → Paragraf, dan judul → Pasal masing-masing 1 enter; Pasal → teksnya tanpa baris kosong; akhir pasal → pasal berikutnya 1 enter. *(Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85)* — *baru*
- **F-12** Jarak di penutup: perintah pengundangan → "Ditetapkan di" 2 enter; nama jabatan → nama pejabat (ruang tanda tangan) 3 enter; nama pejabat pengundang → baris Berita Negara 2 enter. *(Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85)*
- **F-18** Akhir tiap lampiran diberi garis penanda; nama jabatan 1 enter di bawahnya dan nama pejabat 3 enter di bawah nama jabatan. *(Lampiran III huruf A angka IX, hlm 86)* — *baru*
- **F-13** Rincian bertabulasi masuk 1 cm tiap turun satu tingkat; unsur yang lebih kecil ditulis menjorok ke dalam. *(Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85; Lampiran II angka III huruf C butir 54 huruf k angka 5, hlm 41)*
- **F-14** Teks badan pasal dan frasa pembuka Ketentuan Umum mulai 3,5 cm dari margin kiri. *(Lampiran III huruf A angka I dan VI (bagan), hlm 74 dan 83)*
- **F-15** Butir Menimbang berindentasi menggantung: huruf abjad di 3 cm, teks baris pertama di 4 cm, baris lanjutannya di 3,5 cm. *(Lampiran III huruf A angka I dan VI (bagan), hlm 74 dan 83)*
- **F-16** Label Menimbang, Mengingat, dan Menetapkan rata margin kiri; isinya berjarak 0,5 cm dari akhir label. *(Lampiran III huruf A angka I–VIII (bagan tata letak), hlm 74–85)*
- **S-16** Kata "Menetapkan" rata kiri, sejajar ke bawah dengan "Menimbang" dan "Mengingat" — bukan di tengah. *(Lampiran II angka III huruf B.5 butir 38, hlm 37)* — ½ F1-011 memeriksa penulisan katanya
- **S-37** Blok "Ditetapkan di … pada tanggal …" di sebelah kanan; blok "Diundangkan di …" di sebelah kiri, di bawah blok penetapan. *(Lampiran II angka III huruf D butir 113 dan 116, hlm 55–56)*
- **S-57** Judul, kata TENTANG, frasa Dengan Rahmat, jabatan pembentuk, dan MEMUTUSKAN: terletak di tengah margin. *(Lampiran II angka III huruf A butir 6 dan 8, hlm 30; Lampiran II angka III huruf B.1 butir 14, hlm 33; Lampiran II angka III huruf B.2 butir 15, hlm 33; Lampiran II angka III huruf B.5 butir 37, hlm 37)* — *baru*
- **S-61** Tata letak lampiran: dimulai di halaman sesudah penutup; kata "LAMPIRAN" di kanan margin dan hanya di halaman awal tiap lampiran; judul lampiran di tengah margin. *(Lampiran II angka III huruf E butir 121 huruf a, b, d, dan f, hlm 57)* — *baru*

**Kepala halaman dan gambar** — gambar tidak terbaca AI.
- **S-45** Halaman pertama diawali lambang Garuda Pancasila di tengah margin, lalu dua baris "MENTERI KEUANGAN" dan "REPUBLIK INDONESIA" berurutan. *(Lampiran II angka III butir 1, hlm 29)* — *baru*
- **S-46** Kepala halaman hanya di halaman pertama; halaman berikutnya tidak mengulangnya. *(Lampiran II angka III butir 1, hlm 29; Lampiran II angka V butir 132 huruf a, hlm 73)* — *baru*
- **S-47** Lambang dan dua baris kepala halaman berwarna kuning emas, bukan hitam. *(Lampiran II angka III butir 1, hlm 29)* — *baru*

**Huruf kapital dari gaya huruf** — tampil kapital lewat gaya huruf, padahal
teksnya huruf kecil; hanya program yang bisa membedakan.
- **S-02** Seluruh judul — keempat barisnya — ditulis huruf kapital dan tidak diakhiri tanda baca. *(Lampiran II angka III huruf A butir 8, hlm 30)* — ½ F1-006 memeriksa tanda baca; F1-001 (kapital) dimatikan karena salah tandai
- **S-15** "MEMUTUSKAN:" ditulis kapital, tanpa spasi antarhuruf dan tanpa spasi sebelum titik dua. *(Lampiran II angka III huruf B.5 butir 37, hlm 37)*
- **S-19** Bab bernomor angka Romawi ("BAB I", bukan "BAB 1") dan judul bab ditulis kapital seluruhnya. *(Lampiran II angka III huruf C butir 51, hlm 39)*
- **S-40** Baris akhir penutup "BERITA NEGARA REPUBLIK INDONESIA TAHUN … NOMOR …" ditulis kapital seluruhnya. *(Lampiran II angka III huruf D butir 118 dan 119, hlm 56)*
- **S-48** Frasa DENGAN RAHMAT TUHAN YANG MAHA ESA dan jabatan pembentuk MENTERI KEUANGAN REPUBLIK INDONESIA ditulis kapital seluruhnya. *(Lampiran II angka III huruf B.1 butir 14, hlm 33; Lampiran II angka III huruf B.2 butir 15, hlm 33)* — *baru*
- **S-60** Nama jabatan dan nama pejabat pada blok penetapan dan pengundangan ditulis kapital. *(Lampiran II angka III huruf D butir 114 dan 117, hlm 55–56)* — *baru*

**Pencocokan persis ke basis data korpus** — jawabannya satu data; AI tidak
menambah apa pun.
- **K-03** Peraturan di Mengingat sudah berlaku saat rancangan disusun — bukan yang sudah ditetapkan atau diundangkan tetapi belum berlaku. *(Lampiran II angka III huruf B.4 butir 28 huruf b dan 29, hlm 36)*
- **K-03b** Peraturan di Mengingat belum dicabut. KMK 527 tidak menyebutnya; larangannya dari asas umum. *(KMK 527 tidak mengaturnya — larangannya dari asas umum)* — ✓ F3-002
- **K-05** Nomor Lembaran Negara, Tambahan Lembaran Negara, atau Berita Negara di Mengingat cocok dengan data peraturannya di korpus. *(Lampiran II angka III huruf B.4 butir 34 dan 35, hlm 36–37)*
- **K-12** Status peraturan yang dicabut — sudah berlaku atau belum — diambil dari korpus; penentu rumusan R-09. *(Lampiran II angka III huruf C.5 butir 96 dan 99, hlm 51–52)*

### 6.2 AI (158)

**Judul**
- **S-01** Judul terdiri atas empat baris berurutan: jenis peraturan, nomor dan tahun, kata TENTANG, nama. Baris pertama PMK "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA"; KMK "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA". *(Lampiran II angka III huruf A butir 3, 4, dan 8, hlm 30)*
- **S-03** Nomor ditulis "NOMOR 54 TAHUN 2026" — angka Arab saja, tanpa huruf, angka Romawi, atau tanda baca; format lama "54/PMK.06/2015" ditandai. *(Lampiran II angka III huruf A butir 5, hlm 30)*
- **S-56** Kata TENTANG tidak direnggangkan antarhuruf — "TENTANG", bukan "T E N T A N G". *(Lampiran II angka III huruf A butir 6, hlm 30)* — *baru*
- **S-04** Nama judul memuat tanda kurung berisi huruf kapital, mis. "(LP2P)" — tanda akronim buatan; ditandai untuk ditinjau. *(Lampiran II angka III huruf A butir 8, hlm 30)*
- **P-10** Nama judul singkat — satu kata atau frasa — tetapi maknanya mencerminkan isi peraturan. *(Lampiran II angka III huruf A butir 7, hlm 30)*
- **P-11** Akronim di judul hanya boleh bila belum ada padanannya dalam bahasa Indonesia, merupakan istilah teknis baku, maknanya berubah bila tidak disingkat, atau istilah baku internasional. *(Lampiran II angka III huruf A butir 8, hlm 30)*

**Pembukaan**
- **S-05** Pembukaan memuat lima unsur berurutan — frasa Dengan Rahmat (khusus PMK), jabatan pembentuk, Menimbang, Mengingat, diktum — tanpa ditukar atau dihilangkan. *(Lampiran II angka III huruf B butir 13, hlm 33)* — ½ F1-003 memeriksa ada tidaknya Menimbang, Mengingat, dan Menetapkan
- **S-06** PMK memuat frasa DENGAN RAHMAT TUHAN YANG MAHA ESA; KMK tidak memuatnya. *(Lampiran II angka III huruf B.1 butir 14, hlm 33)* — ✓ F1-003 untuk sisi PMK
- **R-01** Frasa itu tertulis persis "DENGAN RAHMAT TUHAN YANG MAHA ESA" dalam satu baris, sesudah judul dan sebelum jabatan pembentuk. *(Lampiran II angka III huruf B.1 butir 14, hlm 33)* — ½ F1-003 memeriksa keberadaannya
- **S-07** Jabatan pembentuk diakhiri koma: "MENTERI KEUANGAN REPUBLIK INDONESIA,". *(Lampiran II angka III huruf B.2 butir 15, hlm 33)*

**Menimbang**
- **S-08** Kata "Menimbang" berhuruf awal kapital — bukan "MENIMBANG" — dan diakhiri titik dua. *(Lampiran II angka III huruf B.3 butir 16, hlm 34)* — ✓ F1-007
- **S-09** Tiap butir Menimbang berpenanda huruf a., b., c. (bukan angka), satu kalimat yang diawali "bahwa" dan diakhiri titik koma. *(Lampiran II angka III huruf B.3 butir 21, hlm 34)* — ½ F1-008 memeriksa "bahwa" dan titik koma
- **R-03** Bila butirnya lebih dari satu, butir terakhir berbunyi "bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf …, perlu menetapkan Peraturan Menteri Keuangan tentang …;". Menimbang satu butir tidak berhuruf dan tidak memakai rumusan ini. *(Lampiran II angka III huruf B.3 butir 22, hlm 35)* — ✓ F1-004
- **I-09** Nama peraturan di butir terakhir Menimbang sama dengan nama pada judul. *(Lampiran II angka III huruf B.3 butir 22, hlm 35)*
- **I-11** Peraturan yang pasalnya disebut di Menimbang ("Pasal … Peraturan Pemerintah Nomor …") tercantum di Mengingat. *(Lampiran II angka III huruf B.3 butir 19, hlm 34; Lampiran II angka III huruf B.4 butir 24 huruf b, hlm 35)*
- **P-22** Menimbang PMK pelaksanaan cukup satu pertimbangan yang menunjuk pasal peraturan lebih tinggi yang memerintahkan pembentukannya. *(Lampiran II angka III huruf B.3 butir 19, hlm 34)* — *baru*
- **P-09** Menimbang PMK kewenangan sendiri, perubahan, atau pencabutan memuat unsur sosiologis dan yuridis — "seyogianya", jadi anjuran. *(Lampiran II angka III huruf B.3 butir 20, hlm 34)*
- **P-08** Menimbang memuat alasan pembentukan, bukan norma terselubung — norma hanya di batang tubuh. *(Lampiran II angka III huruf B.3 butir 17, hlm 34)*
- **F2-105** Tujuan yang disebut di Menimbang ada ketentuannya di batang tubuh. *(turunan Lampiran II angka III huruf B.3 butir 17 dan 19, hlm 34)* — ✓

**Mengingat**
- **S-10** Kata "Mengingat" berhuruf awal kapital dan diakhiri titik dua; tiap dasar hukum bernomor 1., 2., 3. dan diakhiri titik koma. *(Lampiran II angka III huruf B.4 butir 23 dan 31, hlm 35–36)* — ½ F1-009, F1-010
- **S-11** "Undang-Undang" dengan kedua huruf u kapital, bukan "Undang-undang". *(Lampiran II angka III huruf B.4 butir 33, hlm 36)* — ✓ F1-005
- **S-12** Judul peraturan di Mengingat berhuruf awal kapital, kecuali kata "tentang" dan kata penghubung. *(Lampiran II angka III huruf B.4 butir 32, hlm 36)* — ✓ F1-005 untuk kata "tentang"
- **S-13** UU, PP, dan Perpres diikuti Lembaran Negara dan Tambahan Lembaran Negara dalam kurung; PMK diikuti Berita Negara dalam kurung. *(Lampiran II angka III huruf B.4 butir 34 dan 35, hlm 36–37)*
- **S-14** Urutan dasar hukum mengikuti hierarki — UUD, UU, PP, Perpres, PMK — dan yang setingkat diurutkan menurut tanggal pengundangan atau penetapan. *(Lampiran II angka III huruf B.4 butir 30, hlm 36)*
- **I-20** Mengingat tidak kosong — PMK atas kewenangan Menteri sendiri pun perlu dasar kewenangan. *(Lampiran II angka III huruf B.4 butir 24 dan 25, hlm 35)* — ½ F1-003 memeriksa bagiannya ada
- **I-33** Mengingat memuat dasar kewenangan pembentukan: peraturan tentang kedudukan, tugas, dan fungsi Kementerian. *(Lampiran II angka III huruf B.4 butir 25, hlm 35)* — *baru*
- **I-21** Mengingat hanya memuat peraturan yang lebih tinggi atau setingkat di bidang tugas Kementerian Keuangan — tidak memuat peraturan menteri lain. *(Lampiran II angka III huruf B.4 butir 26, hlm 35)*
- **I-22** PMK tidak memuat bagian "Memperhatikan"; bagian itu hanya boleh ada pada KMK. *(Lampiran II angka III huruf B.4 butir 36, hlm 37)*
- **I-13** Peraturan yang dicabut di ketentuan penutup tidak dicantumkan di Mengingat. *(Lampiran II angka III huruf B.4 butir 28 huruf a, hlm 36)*

**Diktum**
- **S-17** Isi Menetapkan mengulang jenis dan nama pada judul tanpa frasa "REPUBLIK INDONESIA", kapital, dan diakhiri titik: "PERATURAN MENTERI KEUANGAN TENTANG … .". *(Lampiran II angka III huruf B.5 butir 39, hlm 37)* — ✓ F1-012
- **I-10** Nama sesudah TENTANG pada Menetapkan sama persis dengan nama pada judul. *(Lampiran II angka III huruf B.5 butir 39, hlm 37)* — ✓ F1-002
- **S-18** Batang tubuh PMK berupa pasal, KMK berupa diktum (KESATU, KEDUA); PMK yang memakai diktum atau KMK yang memakai pasal ditandai. *(Lampiran II angka III huruf C butir 42, hlm 38)*

**Susunan batang tubuh**
- **S-35** Batang tubuh berurutan: ketentuan umum, materi pokok, ketentuan peralihan (bila ada), ketentuan penutup; materi pokok langsung sesudah ketentuan umum. *(Lampiran II angka III huruf C butir 41, hlm 38; Lampiran II angka III huruf C.1 butir 56, hlm 44; Lampiran II angka III huruf C.2 butir 71, hlm 46; Lampiran II angka III huruf C.5 butir 86, hlm 49)*
- **P-26** Materi yang tidak masuk kelompok mana pun dimuat di Bab Ketentuan Lain-Lain, atau di pasal terakhir sebelum bab, bagian, atau paragraf berikutnya. *(Lampiran II angka III huruf C butir 43 dan 49, hlm 38–39)* — *baru*
- **S-22** Susunan berlapis tanpa lompatan: bagian hanya di dalam bab, paragraf hanya di dalam bagian. *(Lampiran II angka III huruf C butir 50, hlm 39)*
- **S-20** Bagian bernomor bilangan tingkat berhuruf — "Bagian Kesatu", bukan "Bagian 1". *(Lampiran II angka III huruf C butir 52, hlm 39)*
- **S-21** Paragraf bernomor angka Arab — "Paragraf 1", bukan "Paragraf Kesatu". *(Lampiran II angka III huruf C butir 53, hlm 39)*
- **S-50** Judul bagian dan paragraf berhuruf awal kapital tiap kata, kecuali partikel yang tidak di awal frasa. *(Lampiran II angka III huruf C butir 52 dan 53, hlm 39)* — *baru*
- **P-23** Pengelompokan ke bab, bagian, dan paragraf dipakai hanya bila materinya luas dan pasalnya banyak. *(Lampiran II angka III huruf C butir 46 dan 47, hlm 38)* — *baru*
- **P-14** Bab, bagian, dan paragraf dikelompokkan menurut kesamaan materi, dan pasal di dalamnya saling berkaitan. *(Lampiran II angka III huruf C butir 43 dan 48, hlm 38; Lampiran II angka III huruf C.2 butir 73, hlm 47)*
- **P-15** Pembagian materi pokok memakai satu kriteria yang jelas dan konsisten — mis. menurut tujuan, seperti "pemeriksaan untuk menguji kepatuhan" dan "pemeriksaan untuk tujuan lain". *(Lampiran II angka III huruf C.2 butir 72, hlm 46)*

**Pasal dan ayat**
- **S-49** Pasal bernomor angka Arab dengan huruf awal kapital — "Pasal 5". *(Lampiran II angka III huruf C butir 54 huruf c, hlm 40)* — *baru*
- **S-23** Nomor pasal berurut naik dan berjalan terus menembus bab — tidak melompat, berulang, atau dimulai ulang. *(Lampiran II angka III huruf C butir 54 huruf c, hlm 40)* — ✓ F2-004
- **S-24** Ayat bernomor angka Arab dalam kurung tanpa titik — "(1)", bukan "(1)." atau "1.". *(Lampiran II angka III huruf C butir 54 huruf f, hlm 40)*
- **S-25** Sebagai acuan, "Pasal" berhuruf awal kapital dan "ayat" huruf kecil — "sebagaimana dimaksud dalam Pasal 2 ayat (2)". *(Lampiran II angka III huruf C butir 54 huruf d dan h, hlm 40)*
- **R-22** Acuan ke pasal memakai "dalam", ke ayat memakai "pada" — pola contoh KMK 527, bukan kaidah tertulis; peringatan lunak saja. *(bukan kaidah tertulis — pola contoh di Lampiran II angka III huruf C butir 54 huruf h, hlm 40)* — *baru*
- **S-26** Bilangan ditulis angka lalu kata dalam kurung — "3 (tiga) hari"; kecuali nomor peraturan, tahun, nomor Lembaran/Berita Negara, dan acuan pasal atau ayat. *(Lampiran II angka III huruf C butir 54 huruf j, hlm 41)* — ½ F2-007 memeriksa angka cocok dengan katanya
- **I-01** Acuan "Pasal N" menunjuk pasal yang benar-benar ada di naskah. *(akibat Lampiran II angka III huruf C butir 54 huruf d, hlm 40)* — ✓ F2-001
- **I-02** Acuan "ayat (n)" menunjuk ayat yang ada pada pasal yang dimaksud. *(akibat Lampiran II angka III huruf C butir 54 huruf h, hlm 40)* — ✓ F2-001
- **P-01** Satu pasal memuat satu norma dalam satu kalimat yang singkat, jelas, dan lugas. *(Lampiran II angka III huruf C butir 54 huruf a, hlm 39)*
- **P-02** Satu ayat memuat satu norma dalam satu kalimat utuh. *(Lampiran II angka III huruf C butir 54 huruf g, hlm 40)*
- **P-03** Materi lebih baik dirumuskan dalam banyak pasal singkat daripada sedikit pasal berayat banyak, kecuali satu rangkaian yang tidak dapat dipisahkan. *(Lampiran II angka III huruf C butir 54 huruf b, hlm 40)*
- **F2-102** Kewajiban menyebut tegas siapa yang memikulnya. *(prioritas penelaah — KMK 527 tidak mengaturnya)* — ✓
- **F2-103** Kata wajib, harus, dapat, dan dilarang tidak bertabrakan dalam satu ketentuan. *(prioritas penelaah — KMK 527 tidak mengaturnya)* — ✓
- **F2-104** Tidak ada dua ketentuan yang tidak bisa berlaku bersamaan. *(turunan Lampiran II angka III huruf C butir 54 huruf a dan g, hlm 39–40)* — ✓

**Rincian (tabulasi)**
- **S-27** Tangga rincian berurutan: a. → 1. → a) → 1). *(Lampiran II angka III huruf C butir 54 huruf k angka 7, hlm 41)*
- **S-28** Rincian paling dalam empat tingkat; lebih dari itu, pasalnya dipecah ke pasal atau ayat lain. *(Lampiran II angka III huruf C butir 54 huruf k angka 8 dan huruf k angka 9, hlm 41)*
- **S-29** Tiap rincian diawali huruf kecil. *(Lampiran II angka III huruf C butir 54 huruf k angka 3, hlm 41)*
- **S-30** Rincian selain yang terakhir diakhiri titik koma. Tanda baca rincian terakhir tidak seragam di contoh KMK 527, jadi hanya peringatan lunak. *(Lampiran II angka III huruf C butir 54 huruf k angka 4, hlm 41)*
- **S-31** Rincian yang masih punya rincian lanjutan diakhiri titik dua. *(Lampiran II angka III huruf C butir 54 huruf k angka 6, hlm 41)*
- **S-32** Kata "dan", "atau", atau "dan/atau" hanya sekali, di belakang rincian kedua dari terakhir — tidak diulang di tiap rincian. *(Lampiran II angka III huruf C butir 54 huruf l–o, hlm 41–42)*
- **S-33** Daftar berincian lebih dari satu tanpa kata penghubung sama sekali — sifat kumulatif atau alternatifnya tidak dinyatakan. *(Lampiran II angka III huruf C butir 54 huruf l–n, hlm 41–42)*
- **P-04** Tiap rincian terbaca sebagai satu kesatuan dengan frasa pembukanya. *(Lampiran II angka III huruf C butir 54 huruf k angka 1, hlm 41)*
- **P-05** "dan" dipakai untuk rincian kumulatif, "atau" untuk alternatif, "dan/atau" untuk keduanya — sesuai maksudnya. *(Lampiran II angka III huruf C butir 54 huruf l–n, hlm 41–42)*

**Ketentuan Umum**
- **R-02** Pasal 1 dibuka dengan "Dalam Peraturan Menteri ini yang dimaksud dengan:". *(Lampiran II angka III huruf C.1 butir 59, hlm 44)*
- **S-34** Tiap definisi bernomor angka Arab, diawali huruf kapital, dan diakhiri titik — bukan titik koma. *(Lampiran II angka III huruf C.1 butir 60, hlm 45)*
- **I-08** Singkatan yang dipakai diperkenalkan dalam definisi dengan pola "… yang selanjutnya disingkat X adalah …". *(Lampiran II angka III huruf C.1 butir 58 huruf b, hlm 44)*
- **I-05** Istilah yang didefinisikan ditulis berhuruf awal kapital di setiap kemunculannya — di pasal, penjelasan, maupun lampiran. *(Lampiran II angka III huruf C.1 butir 67, hlm 46)*
- **I-06** Kata berhuruf kapital yang dipakai berulang tetapi tidak pernah didefinisikan. *(Lampiran II angka III huruf C.1 butir 61 dan 67, hlm 45–46)*
- **I-07** Istilah yang didefinisikan tetapi dipakai hanya sekali — kecuali pengertiannya diperlukan untuk satu bab, bagian, atau paragraf. *(Lampiran II angka III huruf C.1 butir 61 dan 64, hlm 45)* — ½ F2-003 memeriksa istilah yang tidak dipakai sama sekali
- **P-06** Definisi dirumuskan lengkap dan jelas sehingga tidak bermakna ganda; definisi tidak diberi penjelasan lagi. *(Lampiran II angka III huruf C.1 butir 66, hlm 46)* — ✓ F2-101
- **P-07** Urutan definisi: yang berlingkup umum sebelum yang khusus; yang lebih dahulu muncul di materi pokok ditempatkan lebih dahulu; definisi yang saling berkaitan diletakkan berdekatan. *(Lampiran II angka III huruf C.1 butir 68, hlm 46)*
- **I-28** Nama jabatan atau instansi diurutkan dari hierarki tertinggi; organisasi profesi, asosiasi, dan lembaga bentukan masyarakat ditempatkan di bawah instansi pemerintah. *(Lampiran II angka III huruf C.1 butir 69, hlm 46)* — *baru*

**Sanksi**
- **I-23** PMK hanya memuat sanksi administratif — dan keperdataan bila perlu — tidak memuat sanksi pidana, kurungan, atau penjara. *(Lampiran II angka III huruf C.3 butir 74, hlm 47)*
- **I-16** Pasal sanksi ditempatkan sesudah pasal kewajiban atau larangan yang dirujuknya, tidak mendahuluinya. *(Lampiran II angka III huruf C butir 45, hlm 38)*
- **I-34** Sanksi administratif dirumuskan satu pasal dengan norma yang dikenai sanksi; bila normanya beberapa pasal, di pasal terakhir bagian itu; bila banyak, boleh di bab atau pasal tersendiri. *(Lampiran II angka III huruf C butir 44, hlm 38; Lampiran II angka III huruf C.3 butir 75 dan 76, hlm 47)* — *baru*
- **P-13** Kewajiban atau larangan yang perlu bersanksi sudah punya sanksi, dan tidak ada sanksi tanpa kewajiban yang jelas. *(Lampiran II angka III huruf C butir 45, hlm 38)*

**Ketentuan Peralihan**
- **S-36** Ketentuan Peralihan ditempatkan sebelum Ketentuan Penutup. *(Lampiran II angka III huruf C.4 butir 80, hlm 48)*
- **P-18** PMK yang mengubah tindakan atau hubungan hukum yang sudah berjalan memuat Ketentuan Peralihan — supaya tidak ada kekosongan hukum, ada kepastian, dan pihak terdampak terlindungi. *(Lampiran II angka III huruf C.4 butir 79, hlm 47)*
- **I-18** PMK yang berlaku surut memuat, di Ketentuan Peralihan, status tindakan atau hubungan hukum di antara tanggal berlaku surut dan tanggal pengundangan. *(Lampiran II angka III huruf C.4 butir 83, hlm 48; Lampiran II angka III huruf C.5 butir 106 huruf a, hlm 54)*
- **I-19** Penundaan sementara menyebut tegas tindakan atau hubungan hukum yang ditunda, serta jangka waktu atau syarat berakhirnya. *(Lampiran II angka III huruf C.4 butir 84, hlm 49)*
- **P-12** Ketentuan Peralihan tidak diam-diam mengubah makna ketentuan PMK lain — perubahan begitu lewat definisi baru atau PMK perubahan. *(Lampiran II angka III huruf C.4 butir 85, hlm 49)*

**Ketentuan Penutup dan saat mulai berlaku**
- **S-51** Ketentuan Penutup memuat pasal saat mulai berlaku. *(Lampiran II angka III huruf C.5 butir 87 huruf d, hlm 50)* — *baru*
- **R-05** Rumusan saat mulai berlaku memakai salah satu bentuk baku: "mulai berlaku pada tanggal diundangkan"; pada tanggal tertentu; berlaku surut sejak tanggal tertentu; atau "setelah … terhitung sejak tanggal diundangkan". *(Lampiran II angka III huruf C.5 butir 100 dan 101, hlm 52)*
- **R-06** Tidak memakai "… mulai berlaku efektif pada tanggal …" — dilarang. *(Lampiran II angka III huruf C.5 butir 102, hlm 53)*
- **P-27** Saat mulai berlaku yang berbeda untuk bagian atau wilayah tertentu dinyatakan tegas. *(Lampiran II angka III huruf C.5 butir 103 dan 104, hlm 53)* — *baru*
- **P-20** Pemberlakuan surut sedapat mungkin tidak membebani para pihak atau memengaruhi penerimaan negara. *(Lampiran II angka III huruf C.5 butir 106 huruf c, hlm 54)*
- **R-19** Nama singkat, bila ada, tidak memuat nomor dan tahun, dan bukan singkatan atau akronim kecuali sudah sangat dikenal. *(Lampiran II angka III huruf C.5 butir 89, hlm 50)*
- **P-17** Nama singkat tidak menyimpang dari isi, tidak berupa sinonim, dan tidak diberikan pada nama yang sudah singkat. *(Lampiran II angka III huruf C.5 butir 90, 91, dan 92, hlm 50–51)*

**Pencabutan di ketentuan penutup**
- **R-08** Pasal pencabutan diawali "Pada saat Peraturan Menteri ini mulai berlaku, …" — kecuali PMK pencabutan tersendiri. *(Lampiran II angka III huruf C.5 butir 94, hlm 51)*
- **R-10** Peraturan yang dicabut disebut tegas — nomor, tahun, judul, Berita Negara — bukan rumusan umum seperti "peraturan lain yang bertentangan dinyatakan tidak berlaku". *(Lampiran II angka III huruf C.5 butir 95, hlm 51)*
- **R-09** Peraturan yang sudah berlaku "dicabut dan dinyatakan tidak berlaku"; yang sudah diundangkan tetapi belum berlaku "ditarik kembali dan dinyatakan tidak berlaku". Statusnya dari K-12. *(Lampiran II angka III huruf C.5 butir 96 dan 99, hlm 51–52)*
- **R-11** Lebih dari satu peraturan yang dicabut ditulis sebagai rincian bertabulasi, dengan frasa "dicabut dan dinyatakan tidak berlaku" sesudah daftar. *(Lampiran II angka III huruf C.5 butir 97, hlm 52)*
- **I-17** Pencabutan disertai keterangan status peraturan pelaksanaan atau keputusan yang dikeluarkan berdasarkan peraturan yang dicabut. *(Lampiran II angka III huruf C.5 butir 98, hlm 52)*

**Penutup (kaki), salinan, dan penjelasan**
- **S-58** Penutup PMK berurutan: perintah pengundangan, penandatanganan penetapan, pengundangan, lalu baris Berita Negara. *(Lampiran II angka III huruf D butir 109, hlm 54)* — *baru*
- **R-04** Perintah pengundangan berbunyi persis: "Agar setiap orang mengetahuinya, memerintahkan pengundangan Peraturan Menteri ini dengan penempatannya dalam Berita Negara Republik Indonesia." *(Lampiran II angka III huruf D butir 111, hlm 55)*
- **S-52** Perintah pengundangan berdiri sendiri — bukan bagian pasal di atasnya, dan tidak dijadikan pasal tersendiri. *(Lampiran II angka III huruf D butir 110, hlm 55)* — *baru*
- **S-59** Blok penetapan dan blok pengundangan lengkap: tempat dan tanggal, nama jabatan, ruang tanda tangan, dan nama pejabat. *(Lampiran II angka III huruf D butir 112 dan 115, hlm 55–56)* — *baru*
- **S-38** Nama jabatan pada blok penetapan dan pengundangan diakhiri koma. *(Lampiran II angka III huruf D butir 114 dan 117, hlm 55–56)*
- **S-39** Nama pejabat ditulis tanpa gelar, pangkat, golongan, atau NIP. *(Lampiran II angka III huruf D butir 112 huruf d dan 115 huruf d, hlm 55–56)*
- **R-20** Blok pengesahan salinan memuat "Salinan sesuai dengan aslinya,". *(Lampiran II angka V butir 131 huruf a, hlm 72)*
- **R-23** Nama pengesah salinan tanpa gelar, pangkat, atau NIP. *(Lampiran II angka V butir 131 huruf a, hlm 72)* — *baru*
- **R-21** Daftar penyampaian salinan tidak memakai "Yth.". *(Lampiran II angka V butir 131 huruf b, hlm 72)*
- **S-55** Bagian berjudul "PENJELASAN" ditandai untuk ditinjau penelaah — KMK 527 tidak mengatur teknik penjelasan. *(Lampiran II angka III butir 2 huruf E menyebut Penjelasan, tetapi tidak ada butir tekniknya, hlm 30)* — *baru*
- **I-27** Istilah terdefinisi tetap berhuruf awal kapital di dalam Penjelasan. *(Lampiran II angka III huruf C.1 butir 67, hlm 46)* — *baru*

**Lampiran**
- **I-03** Lampiran yang disebut pasal — mis. "Lampiran II" — benar-benar ada. *(Lampiran II angka III huruf E butir 120, hlm 57)* — ✓ F2-106
- **I-04** Lampiran yang ada disebut sekurang-kurangnya satu pasal di batang tubuh. *(Lampiran II angka III huruf E butir 120, hlm 57)* — ✓ F2-106
- **R-12** Kalimat yang menyebut lampiran memuat "… yang merupakan bagian tidak terpisahkan dari Peraturan Menteri ini". *(Lampiran II angka III huruf E butir 120, hlm 57)* — ✓ F2-106
- **S-54** Kata "LAMPIRAN" ditulis kapital; bila lampirannya lebih dari satu, diberi angka Romawi I, II, dan seterusnya. *(Lampiran II angka III huruf E butir 121 huruf b, hlm 57)* — *baru*; ✓ F2-106
- **S-42** Di bawah kata LAMPIRAN tercantum judul PMK — nomor, tahun, dan nama sama dengan halaman pertama — kapital dan tanpa tanda baca. *(Lampiran II angka III huruf E butir 121 huruf c, hlm 57)* — ✓ F2-106
- **S-62** Tiap lampiran punya judul atau nama lampiran, tanpa tanda baca. *(Lampiran II angka III huruf E butir 121 huruf d, hlm 57)* — *baru*
- **S-43** Akhir tiap lampiran memuat nama jabatan dan nama pejabat yang menetapkan PMK. *(Lampiran II angka III huruf E butir 121 huruf h, hlm 57)* — ✓ F2-106
- **S-41** Isi lampiran dinomori dengan huruf atau angka — tidak memakai "Pasal", karena pasal hanya milik batang tubuh. *(akibat Lampiran II angka III huruf C butir 42, hlm 38)*
- **S-44** Lampiran lebih dari satu ditandai — KMK 527 menganjurkan dihindari. *(Lampiran II angka III huruf E butir 121 huruf i, hlm 57)*
- **P-24** Bila lampirannya terpaksa lebih dari satu, dikelompokkan per tema atau topik. *(Lampiran II angka III huruf E butir 121 huruf j, hlm 57)* — *baru*

**Pendelegasian**
- **R-07** Tidak ada delegasi blangko seperti "Hal-hal yang belum cukup diatur … diatur lebih lanjut dengan …". *(Lampiran II angka V butir 123 huruf c, hlm 60)*
- **R-13** Kalimat delegasi menyebut tegas materi yang didelegasikan dan jenis peraturan pelaksananya. *(Lampiran II angka V butir 123 huruf b, hlm 60)*
- **R-14** "diatur dengan" (tidak boleh disubdelegasikan) dan "diatur dalam" (materi tersebar di beberapa pasal) dipakai sesuai maksudnya — akibat hukumnya berbeda. *(Lampiran II angka V butir 123 huruf f dan g, hlm 61)*
- **P-16** Delegasi ke Peraturan Pimpinan Unit Eselon I hanya untuk hal yang sangat teknis administratif, dan sepanjang diamanatkan peraturan yang lebih tinggi. *(Lampiran II angka V butir 123 huruf a, hlm 60)*

**Terhadap peraturan lain — butuh korpus**
- **K-01** Definisi yang dirumuskan kembali sama dengan definisi di PMK sebidang yang berlaku; boleh berbeda bila bidangnya berbeda. *(Lampiran II angka III huruf C.1 butir 62 dan 63, hlm 45)*
- **K-02** Definisi yang dikutip dari peraturan lebih tinggi yang dilaksanakan sama persis rumusannya. *(Lampiran II angka III huruf C.1 butir 65, hlm 45)*
- **K-04** Tiap peraturan di Mengingat memberi kewenangan atau memerintahkan pembentukan — bukan sekadar berkaitan topiknya. *(Lampiran II angka III huruf B.4 butir 24, hlm 35)*
- **K-06** Pasal peraturan lain yang dirujuk memang ada dan berbunyi seperti yang dimaksud. *(Lampiran II angka III huruf B.3 butir 19, hlm 34)*
- **K-07** PMK sebidang yang materinya diganti rancangan ini dicabut secara tegas. *(Lampiran II angka III huruf C.5 butir 93, hlm 51; Lampiran II angka V butir 130 huruf e, hlm 71)*
- **K-08** Tidak bertentangan dengan peraturan yang lebih tinggi. *(Lampiran I BAB II angka 8 huruf b angka 2), hlm 20; Lampiran III huruf C keterangan angka 3, hlm 89; Lampiran III huruf E Daftar I angka 2 huruf b, hlm 93)* — ✓ F3-001
- **K-09** Tidak bertentangan dengan peraturan setingkat. *(Lampiran III huruf C keterangan angka 4, hlm 89)* — ✓ F3-001
- **K-10** Tidak bersinggungan dengan putusan pengadilan — korpus putusan belum ada. *(Lampiran I BAB II angka 8 huruf b angka 3), hlm 20; Lampiran III huruf C keterangan angka 5, hlm 89–90)*
- **K-11** Norma tidak mengulang atau mengutip kembali norma peraturan yang mendelegasikan, kecuali sebagai pengantar. *(Lampiran II angka V butir 123 huruf d dan e, hlm 60–61)*
- **K-13** Saat berlaku PMK pelaksanaan tidak lebih awal dari saat berlaku peraturan yang dilaksanakannya. *(Lampiran II angka III huruf C.5 butir 107, hlm 54)* — *baru*
- **P-21** Usulan rumusan perbaikan dicontoh dari peraturan yang masih berlaku. *(turunan Lampiran II angka III huruf C.1 butir 62 dan 65, hlm 45)* — ½ F3-003

**Substansi — bahan pertimbangan penelaah** (Lampiran I dan III; seluruhnya
*baru*)
- **D-01** Ketentuan yang membebani kewajiban baru atau berdampak finansial kepada masyarakat — ditunjukkan sebagai bahan analisis dampak. *(Lampiran I BAB II angka 1 huruf a, hlm 16; angka 8 huruf a angka 9) huruf a) angka 3, hlm 19)*
- **D-02** Tanda rancangan strategis atau sensitif — berdampak finansial kepada masyarakat, berdampak masif pada organisasi Kementerian Keuangan, kebijakan pokok, atau perlu persetujuan Presiden — lalu ingatkan syaratnya: nota dinas yang menyebut isu strategisnya, strategi komunikasi, dan persetujuan Presiden. *(Lampiran I BAB II angka 3, hlm 16; angka 7 huruf a, hlm 17; angka 8 huruf a angka 9)–10), hlm 19–20; angka 8 huruf b angka 4)–5), hlm 20; Lampiran III huruf E Daftar I angka 2 huruf c, hlm 93)*
- **D-03** Materi yang bisa digabung dengan peraturan yang sudah ditetapkan, dalam rangka simplifikasi regulasi — butuh korpus. *(Lampiran I BAB II angka 13 huruf c, hlm 21)*
- **D-04** Kesesuaian dengan rekomendasi Badan Pemeriksa Keuangan — korpus rekomendasi BPK belum ada. *(Lampiran I BAB II angka 8 huruf b angka 3), hlm 20)*
- **D-05** Materi yang menyangkut tugas unit lain di Kementerian Keuangan — ingatkan perlunya persetujuan unit itu. *(Lampiran I BAB II angka 8 huruf a angka 4), hlm 19; angka 13 huruf a–b, hlm 21; KMK 527 diktum KELIMA huruf c, hlm 4)*
- **D-06** Ketentuan yang berpotensi menghambat pelayanan publik, iklim usaha dan investasi, atau pertumbuhan ekonomi; melanggar hak warga negara; atau membuat perizinan berbelit. *(Lampiran III huruf C keterangan angka 2 huruf a, hlm 89)*
- **D-07** Pengaturannya memang perlu berbentuk PMK, atau cukup kebijakan lain. *(Lampiran I BAB II angka 1 huruf c, hlm 16)*

**Khusus PMK perubahan, pencabutan, KMK, dan peraturan pimpinan unit** — di
luar skop sekarang
- **R-15** Judul perubahan memakai "PERUBAHAN ATAS …"; perubahan kedua dan seterusnya menyebut hitungannya ("PERUBAHAN KEDUA ATAS …") tanpa merinci perubahan sebelumnya — tidak memuat "SEBAGAIMANA TELAH DIUBAH". *(Lampiran II angka III huruf A butir 9 dan 11, hlm 31–32)*
- **I-12** PMK yang diubah ("PERUBAHAN ATAS X") tercantum di Mengingat. *(Lampiran II angka III huruf B.4 butir 27, hlm 36)*
- **I-14** Batang tubuh PMK perubahan dua pasal berangka Romawi: Pasal I memuat seluruh materi perubahan, Pasal II saat mulai berlaku. *(Lampiran II angka V butir 124 huruf b, hlm 61)*
- **I-29** Pasal II memuat saat mulai berlaku; bila juga memuat peralihan atau penutup lebih dari satu materi, dirinci dengan angka Arab. *(Lampiran II angka V butir 124 huruf b dan 125, hlm 61–65)* — *baru*
- **R-16** Pasal I dibuka "Beberapa ketentuan dalam Peraturan Menteri Keuangan Nomor … tentang … (Berita Negara …), diubah sebagai berikut:", dengan rangkaian perubahan sebelumnya disebut bila ada. *(Lampiran II angka V butir 124 huruf c, hlm 62)*
- **I-31** Peraturan yang diubah disebut lengkap di Pasal I: nomor, judul, dan Berita Negara. *(Lampiran II angka V butir 124 huruf c, hlm 62)* — *baru*
- **I-30** Tiap butir perubahan di Pasal I bernomor angka Arab dan berbunyi "Ketentuan Pasal … diubah sehingga berbunyi sebagai berikut:". *(Lampiran II angka V butir 124 huruf c, hlm 62)* — *baru*
- **R-17** Penyisipan dan penambahan memakai kalimat baku dan penanda yang benar: pasal dan bab sisipan berhuruf kapital ("Pasal 1A", "BAB IVA"), ayat sisipan berhuruf kecil dalam kurung ("ayat (1a)"). *(Lampiran II angka V butir 124 huruf d–g, hlm 62–64)*
- **R-18** Bab, bagian, paragraf, pasal, atau ayat yang dihapus tetap tercantum dengan keterangan "Dihapus"; nomornya tidak digeser. *(Lampiran II angka V butir 124 huruf h, hlm 64)*
- **I-35** Perubahan lampiran dituangkan dalam pasal dan cukup memuat bagian yang diubah; nama PMK tetap "Perubahan atas …". *(Lampiran II angka V butir 124 huruf i, 127 huruf b, dan 129, hlm 64–69)* — *baru*
- **I-24** Lampiran PMK perubahan dinomori baru mulai dari I, tidak meniru nomor lampiran lama. *(Lampiran II angka V butir 128, hlm 68)*
- **I-25** Pasal yang diubah lebih dari 50% peraturan asal — sebaiknya dicabut dan disusun ulang; butuh korpus. *(Lampiran II angka V butir 127 huruf a, hlm 67)*
- **I-26** PMK perubahan tidak mengubah sistematika peraturan asal; butuh korpus. *(Lampiran II angka V butir 127, hlm 67)*
- **P-19** Esensi peraturan berubah sehingga lebih baik dicabut dan disusun kembali. *(Lampiran II angka V butir 127 huruf a, hlm 67)*
- **R-24** Judul PMK pencabutan diawali kata "PENCABUTAN" di depan nama peraturan yang dicabut. *(Lampiran II angka III huruf A butir 12, hlm 32)* — *baru*
- **I-15** PMK pencabutan tersendiri terdiri atas dua pasal berangka Arab: Pasal 1 pencabutan, Pasal 2 saat mulai berlaku. *(Lampiran II angka V butir 130 huruf m, hlm 72)*
- **P-25** Materi PMK lama yang dicabut benar-benar ditampung kembali dalam peraturan yang mencabutnya. *(Lampiran II angka V butir 130 huruf c, hlm 71)* — *baru*
- **I-32** PMK hanya dicabut dengan PMK atau peraturan yang lebih tinggi; Peraturan Pimpinan Unit Eselon I tidak dapat mencabut PMK. *(Lampiran II angka III huruf C.5 butir 108, hlm 54; Lampiran II angka V butir 130 huruf a dan i, hlm 70–71)* — *baru*
- **S-53** KMK tidak memuat perintah pengundangan maupun blok pengundangan — keduanya khusus PMK. *(Lampiran II angka III huruf D butir 110 dan 115, hlm 55–56)* — *baru*
- **S-63** KMK yang ditandatangani atas nama Menteri memakai "a.n." sebelum nama jabatan. *(Lampiran II angka III huruf D butir 114, hlm 55)* — *baru*
- **I-36** Peraturan dan Keputusan Pimpinan Unit Eselon I memakai kerangka PMK/KMK dengan lima pengecualian: kop, judul bernomor kodering pengusul, jabatan pembentuk unit, isi yang teknis, dan penutup tanpa akronim. *(Lampiran II angka IV butir 122, hlm 59)* — *baru*

**Di luar naskah — tidak bisa diperiksa dari berkas .docx:** kelengkapan
dokumen pendukung (penjelasan singkat, matriks persandingan dan
kesesuaiannya dengan Pasal I, surat harmonisasi, surat penyelarasan, lembar
analisis dampak, strategi komunikasi, persetujuan Presiden); program
perencanaan; konsultasi publik; berlaku surut yang tidak boleh lebih dahulu
daripada saat rancangan diketahui masyarakat (Lampiran II angka III huruf C.5 butir 106 huruf b, hlm 54); penyampaian dan
cap dinas salinan (Lampiran II angka V butir 131 huruf c–d, hlm 73); serta proses penetapan, pengundangan, dan
penyebarluasan — Lampiran I BAB I–IV, Lampiran III huruf B, D, dan syarat
administratif huruf E.

## 7. Pertanyaan yang belum diputuskan

Yang sudah dijawab dihapus dari sini, dan keputusannya ditulis ke bagian
terkait. Pertanyaan 1–3 lahir dari uji berbayar PMK 45 (1 Okt 2026).

1. **Temuan lemah yang lolos gerbang.** Gerbang membuktikan kutipan, letak,
   dan sumber kata — tetapi tidak bisa menilai apakah dua tafsiran sebuah
   rumusan sama-sama masuk akal. Di PMK 45, 4 temuan seperti itu lolos, 2 di
   antaranya hijau (Pasal 1 angka 3, Pasal 2 ayat (4)). Padahal yang
   ditandai wajib benar-benar salah (CLAUDE.md butir 1).
   - (a) Dibiarkan — penelaah menolaknya lewat Tolak.
   - (b) Temuan "rumusan dua arah" selalu kuning, tidak pernah hijau. Ikut
     mengorbankan 8 usulan hijau yang benar di uji itu.
   - (c) Penilai kedua: sebelum gerbang, satu request per putaran menilai
     ulang calon temuan yang berdasar penilaian (dua arah, pemikul,
     tabrakan); yang tidak disetujui gugur.

   **Rekomendasi:** (c) — tambahannya satu request per putaran; hasilnya
   diukur di langkah 7.
2. **Hasil berbeda tiap kali dijalankan.** Dua run dengan cara yang sama di
   PMK 45 hanya sama di 4 dari 8 temuan. Penelaah yang menjalankan ulang
   naskah yang sama akan melihat hasil berbeda. Satu run menemukan rata-rata
   7,5 kesalahan nyata; gabungan dua run 11.
   - (a) Diterima; panel menyebut hasil AI bisa berbeda tiap kali dijalankan.
   - (b) Tiap putaran dijalankan dua kali bersamaan, hasilnya digabung.
     Biaya 2×; temuan lemah juga bisa bertambah (pertanyaan 1).
   - (c) Hasil disimpan per naskah: naskah yang tidak berubah memakai hasil
     tersimpan — selalu sama, tetapi tidak menambah temuan.

   **Rekomendasi:** (b) dan (c) — lebih lengkap sekali jalan, dan tetap sama
   bila dijalankan ulang.
3. **Rujukan yang menunjuk pasal yang salah belum diperiksa.** Pemeriksaan
   rujukan yang ada hanya memastikan pasal atau ayat yang dirujuk ADA.
   Contoh yang lolos di PMK 45, Pasal 10 ayat (2) huruf b: "jangka waktu
   pengimporan sebagaimana dimaksud dalam Pasal 9 ayat (11)" — ayat (11)
   mengatur jangka waktu penelitian; jangka waktu impor ada di ayat (13). AI
   sempat menduganya, tetapi gugur karena dicatat sebagai "rumusan dua arah".

   **Rekomendasi:** tambah analisis baru (AI, lingkup per pasal): acuan
   "sebagaimana dimaksud dalam …" menunjuk ketentuan yang isinya sesuai
   dengan yang dimaksud kalimatnya. Dasar (turunan): akibat Lampiran II angka
   III huruf C butir 54 huruf d dan h, hlm 40 — sama dengan dua pemeriksaan
   rujukan yang ada.
4. **Judul bagian 6.1 "AI tidak bisa" tidak sepenuhnya benar.** Yang AI tidak
   bisa hanya MEMBACA format, gaya huruf, dan gambar — semuanya tidak ada di
   teks. MENILAI-nya bisa AI kalau kode menuliskan hasil bacaannya ke bahan,
   mis. `[rata kanan · menjorok 3,5 cm · 2 baris kosong sebelumnya]`.
   - (a) Tetap — 31 pemeriksaan format ditulis sebagai program.
   - (b) Satu pembaca format (kode) menuliskan format tiap paragraf ke bahan.
     Angka pasti — huruf, ukuran, kertas, marjin, spasi, nomor halaman (10) —
     tetap kode, ditulis sebagai baris data di `aturan.json`. Sisanya — tata
     letak, kapital dari gaya huruf, kepala halaman (21) — jadi analisis AI.
     Aturan baru cukup menambah baris.

   **Rekomendasi:** (b) — sesuai CLAUDE.md butir 12. Cara membaca formatnya
   dibuktikan dulu di Word penelaah (CLAUDE.md butir 9).
