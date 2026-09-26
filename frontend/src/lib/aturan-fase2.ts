/**
 * Keterangan tiap aturan Fase 2 dan 3, untuk panel Pengaturan.
 *
 * Kembaran `aturan-fase1.ts`, dengan satu tambahan yang tidak ada di Fase 1:
 * `denganModel`. Penelaah berhak tahu temuan mana yang kesalahannya bisa
 * dibuktikan baris demi baris, dan mana yang hasil penalaran model — karena
 * cara memeriksanya memang berbeda.
 *
 *   F2-0xx  dibuktikan kode. Kalau salah, barisnya bisa ditunjuk.
 *   F2-1xx  hasil penalaran model, sudah lewat Langkah 4 (dibaca pada teks
 *           utuh) dan Langkah 5 (kutipannya dibuktikan ada di naskah).
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
 * Aturan penalaran (F2-1xx) boleh hijau HANYA kalau rumusannya datang dari
 * F3-003, yaitu dicontoh dari peraturan yang masih berlaku: penilaian model
 * atas dirinya sendiri bukan bukti. Keputusan per aturan ada di
 * `backend/app/fase2/tahap5_verifikasi.py`.
 *
 * SYARAT TERAKHIR, ditetapkan penelaah 25 Sep 2026: penggantinya wajib
 * benar-benar MUAT di tempat yang dicoret. Usulan yang mengganti satu klausa
 * dengan satu frasa membuat kalimatnya kehilangan predikat — terbukti pada
 * hijau pertama yang dihasilkan korpus. Usulan begitu turun jadi kuning dan
 * tetap terbaca di komentar sebagai contoh rumusan. Periksa satu contoh
 * dengan tangan: `python tools/cek_usulan.py --kalimat … --dicoret … --usulan …`
 *
 * ATURAN PEMELIHARAAN: berkas ini WAJIB sama dengan
 * `backend/app/fase2/mekanis_konsistensi.py` dan `tahap4_memastikan.py`.
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
  // -----------------------------------------------------------------------
  // F2-0xx — dibuktikan kode, gratis, hasilnya pasti
  // -----------------------------------------------------------------------
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
    id: "F2-003",
    fase: 2,
    denganModel: false,
    judul: "Definisi di Pasal 1 dipakai di batang tubuh",
    diperiksa: [
      "Tiap istilah berdefinisi dicari kemunculannya di SELURUH batang tubuh, termasuk Pasal 10 sampai Pasal 19",
      "Istilah yang tidak pernah muncul sama sekali di luar Pasal 1 ditandai",
      "Pencarian tidak peduli huruf besar-kecil",
    ],
    tidakDiperiksa: [
      "Lampiran — belum dibaca parser sama sekali, padahal butir 67 menghitung kemunculan di lampiran juga",
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
    id: "F2-101",
    fase: 2,
    denganModel: true,
    judul: "Rumusan yang bisa dibaca dua arah",
    diperiksa: [
      "Ketentuan yang memuat norma, dibaca utuh berikut definisi dan konsiderans",
      "Dugaan dari Langkah 3 diuji ulang pada teks utuh sebelum jadi temuan",
    ],
    tidakDiperiksa: [
      "Kebijakannya — apakah ketentuannya tepat atau tidak bukan urusan alat ini",
      "Temuan yang kutipannya tidak ketemu persis di naskah DIGUGURKAN, bukan diperlebar",
    ],
    tanda:
      "Blok kuning berikut saran. Hijau HANYA kalau F3-003 dinyalakan dan " +
      "rumusan penggantinya dicontoh dari peraturan yang masih berlaku — " +
      "penilaian model atas dirinya sendiri tidak pernah cukup untuk mencoret",
    catatanSumber:
      "DASAR TURUNAN. Butir 66 KMK 527 (halaman 46, dibaca visual 25 Sep " +
      "2026) melarang pengertian ganda, tetapi HANYA untuk definisi di " +
      "ketentuan umum; di luar Pasal 1 aturan ini turunan. TEMUAN HASIL " +
      "PENALARAN MODEL: sudah lewat Langkah 4 dan Langkah 5, tetapi penilaian " +
      "“bisa dibaca dua arah” tetap penilaian. Periksa sendiri sebelum menerima.",
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
      "Blok kuning berikut saran. Hijau hanya lewat F3-003, dengan " +
      "peraturan sumbernya disebut di komentar",
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
      "Blok kuning berikut saran. Hijau hanya lewat F3-003, dengan " +
      "peraturan sumbernya disebut di komentar",
    catatanSumber:
      "BELUM ADA DASARNYA DI KMK 527. Dicari 25 Sep 2026: Lampiran II " +
      "mengatur kata penghubung dalam tabulasi (butir 54l-o) dan " +
      "melarang beberapa frasa tertentu, tetapi tidak mengatur benturan " +
      "wajib/harus/dapat/dilarang di dalam satu ketentuan. TEMUAN HASIL " +
      "PENALARAN MODEL.",
  },
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
      "pasalnya. Hijau hanya lewat F3-003",
    catatanSumber:
      "DASAR TURUNAN. Butir 54a dan 54g KMK 527 (halaman 39-40, dibaca " +
      "visual 25 Sep 2026) menuntut satu norma per satuan; tidak satu pun " +
      "berkata dua ketentuan tidak boleh saling meniadakan. TEMUAN HASIL " +
      "PENALARAN MODEL.",
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
      "Blok kuning pada butir Menimbang yang bersangkutan. Hijau hanya " +
      "lewat F3-003",
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
  {
    id: "F3-003",
    fase: 3,
    denganModel: true,
    judul: "Usulan rumusan dari peraturan yang masih berlaku",
    diperiksa: [
      "BUKAN aturan yang mencari temuan sendiri — ia melengkapi temuan penalaran yang sudah ada",
      "Rumusan dicontoh dari peraturan yang masih berlaku di korpus JDIH, lalu peraturannya disebut di komentar",
      "SATU-SATUNYA jalan temuan F2-1xx bisa jadi hijau: tanpa peraturan sumber, usulannya tetap kuning",
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
];

/** Aturan mekanis — gratis, hasilnya pasti. Dinyalakan secara bawaan. */
export const ATURAN_FASE2_MEKANIS = ATURAN_FASE2.filter((a) => !a.denganModel);

/** Aturan yang memanggil model — berbiaya dan berjalan menit, bukan detik. */
export const ATURAN_FASE2_MODEL = ATURAN_FASE2.filter((a) => a.denganModel);

export const SEMUA_ID_FASE2 = ATURAN_FASE2.map((a) => a.id);

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
