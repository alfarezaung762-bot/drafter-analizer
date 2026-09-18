/**
 * Keterangan tiap aturan Fase 1, untuk panel Pengaturan.
 *
 * Kenapa ada berkas ini: penelaah perlu bisa MEMERIKSA SENDIRI apa yang
 * diperiksa alat, bukan menebaknya dari temuan yang keluar. Selama daftar ini
 * cuma hidup di kode backend, satu-satunya cara tahu adalah membaca Python —
 * dan itu bukan pekerjaan penelaah.
 *
 * ATURAN PEMELIHARAAN: berkas ini WAJIB sama dengan
 * `backend/app/rules/format_baku.py`. Kalau aturannya berubah, keterangannya
 * ikut diubah di commit yang sama. Keterangan yang bohong lebih buruk daripada
 * tidak ada keterangan sama sekali — penelaah memakai daftar ini untuk
 * memutuskan mana yang perlu dia periksa manual.
 */

import { KeteranganAturan } from "./types";

export const ATURAN_FASE1: KeteranganAturan[] = [
  {
    id: "F1-001",
    judul: "Judul peraturan ditulis kapital seluruhnya",
    diperiksa: [
      "Judul sesudah anchor TENTANG di blok pembuka, sampai penutupnya",
      "Tiap deret kata beruntun yang masih memuat huruf kecil",
    ],
    tidakDiperiksa: ["Judul pada klausul Menetapkan — itu urusan F1-002"],
    tanda: "Blok kuning pada deret kata yang bersangkutan",
    dimatikan:
      "Tidak bisa membedakan judul yang hurufnya memang campur dari judul " +
      "yang tersimpan campur tetapi DITAMPILKAN kapital lewat gaya ALL CAPS. " +
      "Pada RKMK 527 sungguhan, gaya itulah yang dipakai — alat menandai " +
      "judul yang di mata penelaah sudah benar. Dimatikan sampai ada cara " +
      "deteksi yang terbukti.",
  },
  {
    id: "F1-002",
    judul: "Judul pembuka sama persis dengan judul pada Menetapkan",
    diperiksa: [
      "Judul sesudah TENTANG di blok pembuka, dibandingkan kata per kata dengan judul pada klausul Menetapkan",
      "Klausul Menetapkan dicari HANYA di antara MEMUTUSKAN dan batang tubuh (BAB/Pasal/diktum)",
      "Bentuk bertabel ikut terbaca: label “Menetapkan” dan isinya boleh di paragraf terpisah",
    ],
    tidakDiperiksa: [
      "Mana dari dua judul itu yang benar — itu keputusan penelaah",
      "Isi judulnya sendiri; yang dibandingkan cuma kesamaan keduanya",
      "MEMILIH DIAM bila MEMUTUSKAN tidak ada di dokumen — tanpa itu klausul Menetapkan tidak bisa dipastikan letaknya",
    ],
    tanda:
      "Blok kuning pada kata yang berbeda saja. Kalau yang salah justru kata " +
      "yang HILANG dari Menetapkan, tidak ada yang bisa ditunjuk di naskah: " +
      "temuannya muncul sebagai peringatan dokumen di atas daftar, tanpa " +
      "tanda dan tanpa komentar",
  },
  {
    id: "F1-003",
    judul: "Kelengkapan bagian wajib",
    diperiksa: [
      "Ada tidaknya bagian Menimbang",
      "Ada tidaknya bagian Mengingat",
      "Ada tidaknya klausul Menetapkan",
    ],
    tidakDiperiksa: [
      "Isi maupun urutan ketiganya",
      "Bagian lain seperti Dasar Hukum, Diktum, atau penutup",
    ],
    tanda:
      "Peringatan di panel, tanpa tanda di naskah — ketiadaan sebuah bagian " +
      "memang tidak punya lokasi untuk ditunjuk",
  },
  {
    id: "F1-004",
    judul: "Bunyi baku butir Menimbang terakhir",
    diperiksa: [
      "Frasa “berdasarkan pertimbangan sebagaimana dimaksud dalam huruf”",
      "Frasa “perlu menetapkan”",
      "Nama jenis peraturan sesuai pilihan PMK/KMK, diikuti kata “tentang”",
      "Butirnya diakhiri tanda titik koma",
    ],
    tidakDiperiksa: [
      "Berlaku HANYA bila Menimbang punya lebih dari satu butir (a, b, c). Satu butir tanpa huruf adalah bentuk yang sah",
      "Apakah huruf yang dirujuk benar-benar ada di butir sebelumnya",
      "Isi pertimbangannya sendiri",
      "Apakah penyimpangannya bisa diterima dalam konteksnya — itu pertimbangan penelaah, bukan alat",
    ],
    tanda: "Blok kuning pada awal butir terakhir, dipotong di 120 karakter",
    catatanSumber:
      "Butir 22 berbunyi rumusan itu dipakai “PADA UMUMNYA”, bukan wajib — " +
      "sudah diperiksa pada pindaian halaman 35, 18 Sep 2026. Artinya " +
      "penyimpangan dari rumusan ini BELUM TENTU kesalahan. Aturan ini satu-" +
      "satunya di Fase 1 yang tidak bersandar pada butir imperatif; kalau " +
      "penelaah menilai temuannya lebih mengganggu daripada berguna, " +
      "matikan saja lewat kotak centang di atas.",
  },
  {
    id: "F1-005",
    judul: "Ejaan baku penyusunan peraturan",
    diperiksa: [
      "“Undang-Undang” ditulis kapital pada kedua unsurnya — HANYA di bagian Mengingat",
      "“Peraturan Pemerintah Pengganti Undang-Undang” ditulis lengkap dengan kapital — juga hanya di Mengingat",
      "Kata “tentang” di dalam judul peraturan pada dasar hukum tetap huruf kecil — HANYA di bagian Mengingat",
    ],
    tidakDiperiksa: [
      "Typo biasa. Salah ketik seperti “bena” → “benar” TIDAK terdeteksi sama sekali, dan memang tidak akan. Ini bukan kamus bahasa Indonesia, cuma tiga pola di atas",
      "Nama jenis peraturan lain (Perpres, Perda, dsb.) — belum dimasukkan",
      "Apa pun di luar bagian Mengingat. Butir 32 dan 33 dua-duanya berbicara tentang DASAR HUKUM, jadi rujukan generik di dalam Lampiran tidak lagi dituduh",
      "Kata penghubung/konjungsi yang menurut butir 32 juga tetap huruf kecil — belum dibangun",
    ],
    tanda: "Teks lama merah dicoret, usulan penggantinya hijau di sebelahnya",
  },
  {
    id: "F1-006",
    judul: "Judul peraturan tidak diakhiri tanda baca",
    diperiksa: [
      "Paragraf judul TERAKHIR yang ada isinya, sesudah anchor TENTANG",
      "Diakhiri titik, koma, titik koma, atau titik dua \u2192 ditandai",
    ],
    tidakDiperiksa: [
      "Tanda kurung tutup. Butir 8 mempersoalkan akronimnya, bukan kurungnya \u2014 judul seperti “… PAJAK-PAJAK PRIBADI (LP2P)” tidak dituduh di sini",
      "Baris kosong di ujung blok judul, dilewati",
    ],
    tanda: "Kata terakhir beserta tanda bacanya dicoret merah, penggantinya hijau",
  },
  {
    id: "F1-007",
    judul: "Penulisan kata “Menimbang”",
    diperiksa: [
      "Huruf awal kapital, selebihnya huruf kecil — “MENIMBANG” dan “menimbang” dua-duanya menyimpang",
      "Diakhiri tanda baca titik dua (:)",
    ],
    tidakDiperiksa: [
      "MEMILIH DIAM bila paragrafnya cuma berisi kata “Menimbang” sendirian. Pada naskah bertabel titik duanya ada di sel sebelah dan tidak terbaca dari teks paragraf — tidak bisa dibuktikan hilang, jadi tidak dituduhkan",
      "Hanya kemunculan PERTAMA sebelum MEMUTUSKAN yang diperiksa. Kata yang sama di batang tubuh atau lampiran bukan label bagian",
      "MEMILIH DIAM bila MEMUTUSKAN tidak ada — tanpa itu batas pembukaan tidak bisa dipastikan",
      "Letaknya di kiri margin — itu tata letak, bukan teks",
    ],
    tanda: "Kata labelnya saja, bukan seluruh baris",
  },
  {
    id: "F1-008",
    judul: "Bentuk tiap butir Menimbang",
    diperiksa: [
      "Tiap butir diawali kata “bahwa”",
      "Tiap butir diakhiri tanda baca titik koma (;)",
    ],
    tidakDiperiksa: [
      "Potongan butir yang lebih pendek dari 15 karakter dilewati — hampir pasti hasil pemecahan yang gagal pada naskah bertabel, bukan butir yang cacat",
      "Butir yang paragrafnya tidak bisa ditemukan kembali, dilewati",
      "Titik komanya MEMILIH DIAM bila butirnya terpotong antarparagraf — ujung butirnya tidak bisa dipastikan dari satu paragraf saja",
      "Isi pertimbangannya sendiri",
    ],
    tanda:
      "Blok kuning pada awal butirnya bila kata “bahwa” tidak ada; pada satu " +
      "karakter terakhir BUTIR ITU SENDIRI bila titik komanya yang kurang — " +
      "bukan karakter terakhir paragraf, karena satu paragraf bisa memuat " +
      "beberapa butir sekaligus",
  },
  {
    id: "F1-009",
    judul: "Penulisan kata “Mengingat”",
    diperiksa: [
      "Huruf awal kapital, selebihnya huruf kecil",
      "Diakhiri tanda baca titik dua (:)",
    ],
    tidakDiperiksa: [
      "MEMILIH DIAM bila paragrafnya cuma berisi kata “Mengingat” sendirian — alasannya sama dengan F1-007",
      "Hanya kemunculan PERTAMA sebelum MEMUTUSKAN yang diperiksa, sama seperti F1-007",
      "MEMILIH DIAM bila MEMUTUSKAN tidak ada",
    ],
    tanda: "Kata labelnya saja",
  },
  {
    id: "F1-010",
    judul: "Tanda baca dasar hukum",
    diperiksa: [
      "Tiap dasar hukum diakhiri tanda baca titik koma (;)",
      "Paragraf dikelompokkan jadi butir lebih dahulu: sebuah butir dimulai di paragraf berangka dan berlanjut ke paragraf lanjutannya",
    ],
    tidakDiperiksa: [
      "PENOMORANNYA SENDIRI. Butir 31 mensyaratkan angka Arab 1, 2, 3, tetapi dasar hukum yang bernomor huruf (a, b, c) TIDAK ditandai — pada naskah bertabel nomornya sering ada di sel lain, sehingga ketiadaannya tidak bisa dibuktikan dari teks paragraf. Periksa penomorannya sendiri",
      "MEMILIH DIAM bila tidak ada satu pun paragraf yang diawali angka — bisa jadi nomornya ada di sel tabel yang lain, dan tidak bisa dibedakan dari dasar hukum tunggal yang memang tidak bernomor",
      "Urutan hierarkinya (butir 30) — belum dibangun",
      "Kelengkapan (Lembaran Negara …) pada UU/PP/Perpres (butir 34) — belum dibangun",
    ],
    tanda: "Blok kuning pada satu karakter terakhir butirnya",
  },
  {
    id: "F1-011",
    judul: "Penulisan kata “Menetapkan”",
    diperiksa: [
      "Huruf awal kapital, selebihnya huruf kecil",
      "Diakhiri tanda baca titik dua (:)",
    ],
    tidakDiperiksa: [
      "MEMILIH DIAM bila paragrafnya cuma berisi kata “Menetapkan” sendirian",
      "Hanya kemunculan PERTAMA di antara MEMUTUSKAN dan batang tubuh yang diperiksa. Isi diktum KMK yang kebetulan diawali kata “Menetapkan” bukan label bagian dan tidak ditandai",
      "MEMILIH DIAM bila MEMUTUSKAN tidak ada",
      "Ketentuan “disejajarkan ke bawah dengan Menimbang dan Mengingat” — itu tata letak, tidak bisa diperiksa dari daftar paragraf",
    ],
    tanda: "Kata labelnya saja",
  },
  {
    id: "F1-012",
    judul: "Bentuk judul pada Menetapkan",
    diperiksa: [
      "Judulnya diakhiri tanda baca titik (.)",
      "Ditulis tanpa frasa “Republik Indonesia” sesudah “Menteri Keuangan”",
    ],
    tidakDiperiksa: [
      "Apakah judulnya sama dengan judul pembuka — itu F1-002, butir yang sama tetapi bagian kalimat yang lain",
      "Bagian “ditulis seluruhnya dengan huruf kapital” — kendalanya sama dengan F1-001, yaitu gaya ALL CAPS",
      "Frasa “Republik Indonesia” HANYA diperiksa di posisi jenis peraturan, yaitu sebelum kata “TENTANG” pertama. Sesudah itu yang ada judul, dan judul boleh mengutip nama resmi peraturan lain berikut frasa itu — mencopotnya berarti mengubah nama resmi dokumen orang",
      "MEMILIH DIAM untuk pemeriksaan frasa itu bila kata “TENTANG” tidak ada di klausulnya",
    ],
    tanda: "Teks lama merah dicoret, penggantinya hijau",
  },
];

/** Aturan yang benar-benar bisa dipilih penelaah (yang dimatikan tidak). */
export const ATURAN_BISA_DIPILIH = ATURAN_FASE1.filter((a) => !a.dimatikan);

export const SEMUA_ID_AKTIF = ATURAN_BISA_DIPILIH.map((a) => a.id);
