/**
 * Keterangan tiap aturan Fase 2 dan 3, untuk panel Pengaturan.
 *
 * Kembaran `aturan-fase1.ts`, dengan satu tambahan yang tidak ada di Fase 1:
 * `denganModel`. Penelaah berhak tahu temuan mana yang kesalahannya bisa
 * dibuktikan baris demi baris, dan mana yang hasil penalaran model — karena
 * cara memeriksanya memang berbeda.
 *
 *   F2-0xx  dibuktikan kode. Kalau salah, barisnya bisa ditunjuk.
 *   F2-1xx  hasil penalaran model yang membaca naskah UTUH, sudah lewat
 *           tahap 4 (dugaan diuji ulang) dan tahap 5 (kutipannya dibuktikan
 *           ada di naskah, klaim "tidak ada" dicari kode).
 *   F3-001  perlu korpus peraturan. Kutipan pembandingnya dari pemindaian,
 *           jadi selalu berpenanda "belum diverifikasi".
 *
 * KEBIJAKAN HIJAU DAN KUNING, ditetapkan penelaah 22 Sep 2026 dan diperbarui
 * 23 Sep 2026. Yang berubah bukan syarat buktinya, melainkan dari mana bukti
 * penggantinya boleh datang:
 *
 *   HIJAU (penggantian) — kesalahannya TERBUKTI, penggantinya didapat DENGAN
 *                         SUMBER YANG BISA DITUNJUK, DAN penggantinya
 *                         benar-benar MUAT di tempat yang dicoret. Teks lama
 *                         dicoret merah, usulannya hijau di sebelahnya,
 *                         sumbernya disebut di komentar.
 *   MERAH (penghapusan) — kesalahannya terbukti dan perbaikannya MEMBUANG.
 *                         Dicoret merah tanpa sisipan hijau. Teksnya tetap
 *                         tidak dihapus alat — yang menghapus penelaah.
 *   KUNING (catatan)    — kemungkinan, atau penggantinya tidak diketahui.
 *                         Tidak ada yang dicoret. Contoh rumusan ikut ke
 *                         komentar, tetapi tidak pernah masuk ke naskah.
 *
 * Aturan penalaran (F2-1xx) boleh hijau HANYA kalau rumusannya punya sumber
 * yang bisa ditunjuk — penilaian model atas dirinya sendiri bukan bukti. Sejak
 * 26 Sep 2026 ada DUA sumber yang diterima, dan keduanya sama sahnya:
 *
 *   DARI LUAR  — F3-003: rumusan dicontoh dari peraturan yang masih berlaku di
 *                korpus JDIH. Butuh OpenSearch. Peraturannya disebut di
 *                komentar sebagai "Rumusan serupa: …".
 *   DARI DALAM — naskah itu sendiri: tiap kata yang DITAMBAHKAN usulan sudah
 *                ada di pasal yang sama, atau sudah berdefinisi di Pasal 1.
 *                Tidak butuh jaringan. Disebut di komentar sebagai
 *                "Sumber usulan: …".
 *
 * Satu kata yang tidak ketemu di keduanya sudah membatalkan seluruh usulan —
 * bukan mayoritas kata, satu kata. Keputusan per aturan ada di
 * `backend/app/telaah/tahap5_verifikasi.py`, fungsi `sumber_internal()` dan
 * `boleh_menyisipkan()`.
 *
 * SYARAT TERAKHIR, ditetapkan penelaah 25 Sep 2026: penggantinya wajib
 * benar-benar MUAT di tempat yang dicoret. Usulan yang mengganti satu klausa
 * dengan satu frasa membuat kalimatnya kehilangan predikat — terbukti pada
 * hijau pertama yang dihasilkan korpus. Usulan begitu turun jadi kuning dan
 * tetap terbaca di komentar sebagai contoh rumusan. Periksa satu contoh
 * dengan tangan: `python tools/cek_usulan.py --kalimat … --dicoret … --usulan …`
 *
 * ATURAN PEMELIHARAAN: berkas ini WAJIB sama dengan
 * `backend/app/telaah/tahap2_persiapan/mekanis_konsistensi.py` dan `JENIS` di
 * `backend/app/bersama/prompt.py`.
 * Kalau aturannya berubah, keterangannya ikut diubah di commit yang sama.
 * Keterangan yang bohong lebih buruk daripada tidak ada keterangan.
 */

import { KeteranganAturan } from "./types";

export interface KeteranganAturanLanjut extends KeteranganAturan {
  /** Fase asalnya — dipakai panel untuk mengelompokkan, bukan menomori ulang. */
  fase: 2 | 3;
  /** true bila temuannya lahir dari penalaran model, bukan dari kode. */
  denganModel: boolean;
}

export const ATURAN_FASE2: KeteranganAturanLanjut[] = [
  {
    id: "F2-004",
    fase: 2,
    denganModel: false,
    judul: "Penomoran bertingkat tidak melompat atau berulang",
    diperiksa: [
      "Deret nomor Pasal, ayat, huruf, dan angka diperiksa berurutan di tiap tingkat",
      "Nomor yang melompat atau muncul dua kali ditandai",
    ],
    tidakDiperiksa: [
      "Pasal sisipan bernomor huruf (Pasal 5A) diperlakukan sah, bukan lompatan",
      "Penomoran di dalam lampiran",
      "MEMILIH DIAM bila nomornya dibuat penomoran otomatis Word: nomornya terbaca untuk menyusun struktur, tetapi tidak bisa disorot di naskah",
    ],
    tanda:
      "Blok kuning pada nomornya saja. Tidak dicoret: perbaikannya bisa " +
      "menomori ulang atau menambah bagian yang hilang, dan keduanya berbeda akibat",
    catatanSumber:
      "Butir 54c, 54f, dan 54k-7 KMK 527 (halaman 40 dan 41, dibaca visual " +
      "25 Sep 2026). Kata kuncinya “nomor urut”: deret yang melompat atau " +
      "berulang bukan lagi urut. Berlaku sama untuk Pasal, ayat, dan rincian " +
      "bertingkat.",
  },
  {
    id: "F2-001",
    fase: 2,
    denganModel: false,
    judul: "Rujukan antar-pasal menunjuk pasal yang ada",
    diperiksa: [
      "Bentuk baku “sebagaimana dimaksud dalam/pada Pasal N”, termasuk “ayat (n)”",
      "Nomor pasal dan ayat yang dirujuk dicari di pohon satuan dokumen ini",
    ],
    tidakDiperiksa: [
      "Rujukan ke peraturan LAIN — “Pasal 12 Undang-Undang Nomor 1 Tahun 2004” tidak disentuh",
      "Kata “Pasal” tanpa frasa baku di depannya",
      "Apakah isi pasal yang dirujuk memang nyambung — itu urusan F2-101",
    ],
    tanda:
      "Blok kuning pada frasa rujukannya saja. Tidak ada yang dicoret — " +
      "kesalahannya terbukti, tetapi nomor penggantinya tidak bisa ditebak alat",
    catatanSumber:
      "DASAR TURUNAN. Butir 54d dan 54h KMK 527 (halaman 40, dibaca visual " +
      "25 Sep 2026) mengatur kapitalisasi acuan “Pasal” dan “ayat”, bukan " +
      "keberadaan yang diacu — tidak ada butir yang berbunyi “rujukan wajib " +
      "menunjuk pasal yang ada”. Kesalahannya tetap dibuktikan mutlak dari " +
      "struktur dokumen, tanpa penafsiran.",
  },
  {
    id: "F2-007",
    fase: 2,
    denganModel: false,
    judul: "Bilangan ditulis angka dan huruf yang cocok",
    diperiksa: [
      "Bentuk “30 (tiga puluh)” — angka Arab lalu hurufnya dalam kurung",
      "Angka dan hurufnya dibandingkan; yang tidak cocok ditandai",
    ],
    tidakDiperiksa: [
      "Kurung yang isinya bukan bilangan — “Pengguna Barang (PB)” tidak disentuh",
      "Bilangan di atas jangkauan pembacaan kata (ribuan ke atas)",
      "MEMILIH DIAM bila hurufnya tidak bisa dibaca jadi angka yang pasti",
    ],
    tanda:
      "Blok kuning pada bilangannya. Contoh rumusan yang cocok ikut di " +
      "komentar, tetapi TIDAK disisipkan ke naskah — mana yang benar, " +
      "angkanya atau hurufnya, justru pertanyaan pokoknya",
    catatanSumber:
      "Butir 54j KMK 527 (halaman 41, dibaca visual 25 Sep 2026): bilangan " +
      "ditulis angka Arab diikuti kata atau frasa di antara tanda kurung. " +
      "Butir itu TIDAK menentukan mana yang benar kalau keduanya berbeda, " +
      "jadi aturan ini tidak pernah menghasilkan hijau.",
  },

  // -----------------------------------------------------------------------
  // F2-1xx — hasil penalaran model
  // -----------------------------------------------------------------------
  {
    id: "F2-003",
    fase: 2,
    denganModel: false,
    judul: "Definisi di Pasal 1 dipakai di batang tubuh",
    diperiksa: [
      "Tiap istilah berdefinisi dicari kemunculannya di SELURUH batang tubuh dan LAMPIRAN, termasuk Pasal 10 sampai Pasal 19 dan paragraf yang tidak dikenali parser",
      "Istilah yang tidak pernah muncul sama sekali di luar Pasal 1 ditandai",
      "Pencarian tidak peduli huruf besar-kecil",
    ],
    tidakDiperiksa: [
      "Isi tabel lampiran lebih dari 1.000 baris — hanya kerangkanya yang dibaca, jadi istilah yang cuma dipakai di sana bisa terlewat",
      "Istilah bentuk panjang: pada “X yang selanjutnya disebut Y”, yang dicari di batang tubuh bentuk pendeknya (Y)",
      "Istilah yang dipakai SEKALI tetap dibiarkan, walau butir 61 menuntut pemakaian berulang — supaya pengecualian butir 64 tidak pernah salah tandai",
      "MEMILIH DIAM bila Pasal 1 tidak ditemukan atau tidak memuat satu pun definisi",
    ],
    tanda:
      "Istilahnya di Pasal 1 dicoret merah, TANPA usulan hijau — perbaikannya " +
      "membuang definisinya, bukan menggantinya. Teksnya tidak dihapus alat",
    catatanSumber:
      "Butir 61 KMK 527 Lampiran II (halaman 45, dibaca visual 25 Sep 2026): " +
      "hanya istilah yang dipakai berulang yang boleh dimuat di ketentuan " +
      "umum. Pengecualiannya butir 64 — istilah yang dipakai sekali tetapi " +
      "pengertiannya diperlukan untuk suatu bab — dan pengecualian itu tidak " +
      "bisa dinilai kode, jadi timbang sendiri sebelum menghapus.",
  },
  {
    id: "F2-105",
    fase: 2,
    denganModel: true,
    judul: "Tujuan di Menimbang yang tidak ada ketentuannya",
    diperiksa: [
      "Maksud yang dinyatakan konsiderans, dicari padanannya di batang tubuh",
    ],
    tidakDiperiksa: [
      "Ketentuan di batang tubuh yang tidak disebut Menimbang — arah sebaliknya tidak diperiksa",
    ],
    tanda:
      "Blok kuning pada butir Menimbang yang bersangkutan. Hijau kalau " +
      "penggantinya bisa ditunjuk sumbernya — dari naskah sendiri, atau dari " +
      "peraturan berlaku lewat F3-003",
    catatanSumber:
      "DASAR TURUNAN. Butir 17 dan 19 KMK 527 (halaman 34, dibaca visual " +
      "25 Sep 2026) mengatur ISI konsiderans; tidak satu pun mewajibkan tiap " +
      "maksud yang disebut di sana punya ketentuannya di batang tubuh. " +
      "TEMUAN HASIL PENALARAN MODEL.",
  },

  // -----------------------------------------------------------------------
  // F3-00x — perlu korpus peraturan
  // -----------------------------------------------------------------------
  {
    id: "F2-104",
    fase: 2,
    denganModel: true,
    judul: "Dua ketentuan yang tidak bisa berlaku bersamaan",
    diperiksa: [
      "KEDUA satuan dibaca utuh dalam satu pemeriksaan, tidak satu-satu",
      "Yang ditandai hanya satuan yang menyimpang; kalau tidak bisa ditentukan, yang letaknya lebih belakang",
    ],
    tidakDiperiksa: [
      "Pengecualian yang sah — “kecuali sebagaimana dimaksud dalam Pasal 12” bukan tabrakan",
      "Tabrakan dengan peraturan lain — itu F3-001",
    ],
    tanda:
      "Blok kuning pada satuan yang menyimpang, catatannya menyebut kedua " +
      "pasalnya. Hijau kalau penggantinya bisa ditunjuk sumbernya — dari " +
      "naskah sendiri, atau dari peraturan berlaku lewat F3-003",
    catatanSumber:
      "DASAR TURUNAN. Butir 54a dan 54g KMK 527 (halaman 39-40, dibaca " +
      "visual 25 Sep 2026) menuntut satu norma per satuan; tidak satu pun " +
      "berkata dua ketentuan tidak boleh saling meniadakan. TEMUAN HASIL " +
      "PENALARAN MODEL.",
  },
  {
    id: "F2-101",
    fase: 2,
    denganModel: true,
    judul: "Rumusan yang bisa dibaca dua arah",
    diperiksa: [
      "Tiap pasal dibaca dengan NASKAH UTUH sebagai konteksnya — definisi, konsiderans, pasal yang dirujuknya, dan lampiran",
      "Dugaannya diuji ulang di tahap 4 sebelum jadi temuan",
      "Model WAJIB menyebut dua tafsiran yang berbeda; keduanya tertulis di komentar",
    ],
    tidakDiperiksa: [
      "Kebijakannya — apakah ketentuannya tepat atau tidak bukan urusan alat ini",
      "Rumusan yang cuma “terlalu umum” atau “kurang rinci” — itu bukan dua tafsiran, dan digugurkan",
      "Keberadaan pasal/ayat/huruf yang dirujuk — itu F2-001, yang memeriksanya dengan kode",
      "Temuan yang kutipannya tidak ketemu persis di naskah DIGUGURKAN, bukan diperlebar",
    ],
    tanda:
      "Blok kuning berikut saran. Hijau HANYA kalau penggantinya bisa " +
      "ditunjuk sumbernya: istilah berdefinisi Pasal 1 atau rumusan di pasal " +
      "yang sama, atau peraturan yang masih berlaku lewat F3-003. Penilaian " +
      "model atas dirinya sendiri tidak pernah cukup untuk mencoret",
    catatanSumber:
      "DUA DASAR, MENURUT LETAKNYA. Di Pasal 1: butir 66 KMK 527 (halaman " +
      "46, dibaca visual 25 Sep 2026) — definisi tidak boleh menimbulkan " +
      "pengertian ganda, kutipan langsung. Di luar Pasal 1: PRIORITAS " +
      "PENELAAH — Lampiran II tidak punya bab ragam bahasa, dan butir 66 " +
      "tidak lagi dipakai di sana (dicari 27 Sep 2026). TEMUAN HASIL " +
      "PENALARAN MODEL: kedua tafsirannya tertulis di komentar supaya bisa " +
      "Anda timbang sendiri sebelum menerima.",
  },
  {
    id: "F2-102",
    fase: 2,
    denganModel: true,
    judul: "Kewajiban tanpa pemikul yang tegas",
    diperiksa: [
      "Ketentuan yang mewajibkan sesuatu tetapi tidak menyebut siapa yang memikulnya",
    ],
    tidakDiperiksa: [
      "Kewajiban yang subjeknya jelas dari pasal sebelumnya dalam satu rangkaian",
    ],
    tanda:
      "Blok kuning berikut saran. Hijau kalau penggantinya bisa ditunjuk " +
      "sumbernya — istilah berdefinisi Pasal 1 atau rumusan di pasal yang " +
      "sama, atau peraturan berlaku lewat F3-003. Sumbernya disebut di komentar",
    catatanSumber:
      "BELUM ADA DASARNYA DI KMK 527. Dicari 25 Sep 2026 di Lampiran II " +
      "dan tidak ketemu: tidak satu butir pun mewajibkan norma menyebut " +
      "subjek pemikulnya. Kekosongan itu dilaporkan apa adanya, tidak " +
      "ditambal butir yang kebetulan mirip. TEMUAN HASIL PENALARAN MODEL.",
  },
  {
    id: "F2-103",
    fase: 2,
    denganModel: true,
    judul: "Kata operasional yang saling bertabrakan",
    diperiksa: [
      "wajib / harus / dapat / dilarang yang bertemu dalam satu ketentuan",
      "Akibatnya: tidak jelas perbuatannya diwajibkan atau dibolehkan",
    ],
    tidakDiperiksa: [
      "Kata operasional berbeda di pasal yang berbeda — itu lazim dan sah",
    ],
    tanda:
      "Blok kuning berikut saran. Hijau kalau penggantinya bisa ditunjuk " +
      "sumbernya — istilah berdefinisi Pasal 1 atau rumusan di pasal yang " +
      "sama, atau peraturan berlaku lewat F3-003. Sumbernya disebut di komentar",
    catatanSumber:
      "BELUM ADA DASARNYA DI KMK 527. Dicari 25 Sep 2026: Lampiran II " +
      "mengatur kata penghubung dalam tabulasi (butir 54l-o) dan " +
      "melarang beberapa frasa tertentu, tetapi tidak mengatur benturan " +
      "wajib/harus/dapat/dilarang di dalam satu ketentuan. TEMUAN HASIL " +
      "PENALARAN MODEL.",
  },
  {
    id: "F2-106",
    fase: 2,
    denganModel: true,
    judul: "Lampiran dinyatakan di batang tubuh dan berformat baku",
    diperiksa: [
      "Tiap lampiran disebut pasal, berikut pernyataan bahwa lampiran merupakan bagian tidak terpisahkan dari Peraturan Menteri ini",
      "Lampiran yang disebut pasal memang ada, dan lampiran yang ada memang disebut pasal",
      "Salah ketik kata “Lampiran” di pasal atau di kepala lampiran",
      "Kepala lampiran: LAMPIRAN kapital, berangka Romawi bila lebih dari satu, judul PMK sama dengan halaman pertama",
      "Nama dan tanda tangan pejabat di akhir tiap lampiran",
      "Bilangan angka-huruf di lampiran cocok — “30 (tiga puluh)”",
    ],
    tidakDiperiksa: [
      "Tata letak — kanan dan tengah margin, nomor halaman — tidak terlihat di teks",
      "Isi dan kebijakan lampiran",
      "Jumlah lampiran lebih dari satu — butir 121 huruf i hanya anjuran",
      "Isi tabel lebih dari 1.000 baris — hanya kerangkanya yang dibaca",
    ],
    tanda:
      "Blok kuning berikut saran. Tidak pernah hijau: perbaikan lampiran jarang " +
      "berupa pengganti harfiah satu frasa",
    catatanSumber:
      "Butir 120 dan 121 huruf b, c, h KMK 527 (halaman 57, dibaca dari citra " +
      "halaman 29 Sep 2026). Dinilai MODEL dengan parameter tertulis, bukan " +
      "regex: bentuk lampiran terlalu beragam — PMK 119 memuat “Lampiran " +
      "Surat” di tengah contoh format surat. Kode mengumpulkan faktanya, model " +
      "menilai, dan kutipannya tetap dibuktikan kode. TEMUAN HASIL PENALARAN MODEL.",
  },
  {
    id: "F3-002",
    fase: 3,
    denganModel: false,
    judul: "Dasar hukum di Mengingat masih berlaku",
    diperiksa: [
      "Tiap butir Mengingat dibaca: bentuk, nomor, dan tahun peraturannya",
      "Peraturannya dicari di korpus JDIH, lalu status berlakunya dibaca",
      "TIDAK memanggil AI sama sekali — status dibaca langsung dari korpus",
    ],
    tidakDiperiksa: [
      "Bentuk di luar UU, Perppu, PP, Perpres, Keppres, PMK, dan KMK — Ketetapan MPR dan peraturan daerah dilewati",
      "MEMILIH DIAM bila peraturannya tidak ketemu di korpus: tidak ketemu BUKAN bukti sudah dicabut",
      "MEMILIH DIAM bila dua dokumen bernomor sama berstatus berbeda",
      "MEMILIH DIAM bila statusnya di luar Berlaku/Tidak Berlaku",
    ],
    tanda:
      "Blok kuning pada sebutan peraturannya saja, bukan seluruh butir " +
      "(butir Mengingat panjang karena memuat Lembaran Negara)",
    catatanSumber:
      "DASAR TURUNAN, dan koreksinya penting. Butir 28 dan 29 KMK 527 " +
      "(halaman 36, dibaca visual 25 Sep 2026) melarang mencantumkan " +
      "peraturan yang BELUM BERLAKU — bukan yang SUDAH DICABUT, padahal " +
      "itulah yang diperiksa aturan ini. Larangannya berdiri di atas asas " +
      "umum, bukan di atas KMK 527. Yang dilaporkan tetap FAKTA dari korpus, " +
      "bukan penilaian; tetapi status di korpus dapat tertinggal dari " +
      "keadaan sebenarnya — pastikan sendiri sebelum mengubah dasar hukum.",
  },
  {
    id: "F3-003",
    fase: 3,
    denganModel: true,
    judul: "Usulan rumusan dari peraturan yang masih berlaku",
    diperiksa: [
      "BUKAN aturan yang mencari temuan sendiri — ia melengkapi temuan penalaran yang sudah ada",
      "Rumusan dicontoh dari peraturan yang masih berlaku di korpus JDIH, lalu peraturannya disebut di komentar",
      "Jalan hijau DARI LUAR naskah. Sejak 26 Sep 2026 bukan lagi satu-satunya: usulan yang kata-katanya sudah ada di naskah sendiri juga boleh hijau, tanpa korpus",
    ],
    tidakDiperiksa: [
      "Temuan yang sudah punya usulan — tidak ada yang perlu dicari",
      "Kutipan lebih panjang dari 200 huruf — penggantinya pasti ditolak pemeriksaan rentang",
      "Lebih dari 15 temuan per dokumen — batas biaya, sisanya dilewati",
      "Usulan yang menyebut peraturan di luar hasil pencarian — dibuang kode",
    ],
    tanda:
      "Teks lama merah dan dicoret, usulannya hijau di sebelahnya. Komentarnya " +
      "menyebut peraturan mana yang jadi acuan",
    catatanSumber:
      "BERBIAYA — satu embedding, satu kueri korpus, dan satu panggilan AI per " +
      "temuan. Rumusan acuannya berasal dari pemindaian yang OCR-nya bisa " +
      "rusak, jadi periksa sendiri sebelum menerima usulannya.",
  },
  {
    id: "F3-001",
    fase: 3,
    denganModel: true,
    judul: "Berpotensi bertentangan dengan peraturan lain",
    diperiksa: [
      "Hanya ketentuan yang dugaannya memang menyangkut dokumen di luar rancangan ini",
      "Pembandingnya dicari di korpus JDIH, lalu disaring status berlakunya",
      "Nama peraturan yang disebut dicocokkan kode ke hasil pencarian",
    ],
    tidakDiperiksa: [
      "Peraturan yang sudah dicabut — dibuang sebagai penyaring keras",
      "Peraturan yang status berlakunya tidak terbaca — ikut dibuang, memilih diam",
      "Peraturan yang tidak muncul di hasil pencarian — model dilarang menyebutnya dari ingatan",
    ],
    tanda:
      "Blok kuning. Bahasanya selalu “berpotensi bertentangan”, tidak pernah " +
      "“bertentangan” — temuan ini kemungkinan, bukan kesimpulan",
    catatanSumber:
      "KMK 527 Lampiran III huruf C angka 3 dan 4 (halaman 89, dibaca visual " +
      "25 Sep 2026), dan huruf E Syarat Substantif 2b (halaman 93 untuk PMK, " +
      "halaman 95 untuk KMK). Huruf C angka 3b dan 4b justru menyuruh analisis " +
      "MELAMPAUI peraturan yang disebut di Mengingat — itulah sebabnya aturan " +
      "ini perlu korpus. Kutipan pembandingnya tetap berasal dari pemindaian " +
      "yang OCR-nya bisa rusak, dan cakupan korpusnya belum diverifikasi " +
      "langsung (brief 8.12) — periksa sendiri sebelum menerima.",
  },
];

/**
 * TIGA KATEGORI, menggantikan pembagian mekanis/model yang lama.
 *
 * Pembedanya bukan cakupan melainkan MEKANISME — apakah kesalahannya bisa
 * dibuktikan kode, atau makna kalimatnya memang harus dibaca.
 *
 * Kategori 1 berada di DUA tempat, dan itu disengaja: F1-001 s/d F1-012 bekerja
 * dari paragraf mentah (jalur cepat, tetap jalan walau pohon satuan gagal
 * diurai), sementara keempat di bawah butuh pohonnya berhasil. Panel
 * menampilkan keduanya sebagai satu kategori; jalur pemanggilannya di belakang
 * layar tetap dua.
 */
export const ATURAN_STRUKTURAL_LANJUT = ATURAN_FASE2.filter(
  (a) => a.fase === 2 && !a.denganModel
);

/** Kategori 2 — makna kalimat harus dibaca, tidak bisa dibuktikan regex. */
export const ATURAN_INTERNAL = ATURAN_FASE2.filter(
  (a) => a.fase === 2 && a.denganModel
);

/**
 * Kategori 3 — dibandingkan ke korpus peraturan lain.
 *
 * Pembedanya SUMBER DATA, bukan mekanisme: F3-002 masuk sini walau tidak
 * memakai AI sama sekali, karena yang ditanyainya tetap korpus di luar naskah.
 */
export const ATURAN_EKSTERNAL = ATURAN_FASE2.filter((a) => a.fase === 3);

/**
 * Bawaan saat panel pertama dibuka: mekanis menyala, penalaran menyala,
 * Fase 3 MATI.
 *
 * Fase 3 mati secara bawaan karena ia satu-satunya yang bergantung pada
 * korpus yang isinya belum diverifikasi langsung. Menyalakannya keputusan
 * sadar penelaah, bukan bawaan yang tidak disadari.
 */
export const ID_AKTIF_BAWAAN = ATURAN_FASE2.filter((a) => a.fase === 2).map(
  (a) => a.id
);
