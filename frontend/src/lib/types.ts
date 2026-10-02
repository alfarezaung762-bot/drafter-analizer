/**
 * Tipe data Temuan — sinkron dengan backend app.models.temuan dan
 * docs/kontrak-data.md.
 *
 * Revisi 17 Sep 2026: tingkat_keparahan dihapus, nomor dan jenis_tanda
 * ditambahkan, jenis_dokumen jadi bagian wajib AnalisisRequest.
 */

/** Dipilih penelaah di task pane — backend tidak menebaknya. */
export type JenisDokumen = "PMK" | "KMK";

/**
 * Cara temuan dipasang di dokumen.
 * - penggantian: teks lama merah dicoret, usulannya hijau di sebelahnya
 * - penghapusan: teks lama merah dicoret, TANPA sisipan hijau — perbaikannya
 *   membuang, bukan mengganti (ditetapkan penelaah 23 Sep 2026)
 * - catatan: blok kuning, warna huruf tidak disentuh
 *
 * Tidak satu pun menghapus teks penelaah; "penghapusan" cuma mewarnai dan
 * mencoret. Yang menghapus tetap penelaah.
 *
 * Keterangan lama menyebut "perubahan terlacak (Track Changes)". Jalur itu
 * ditinggalkan 17 Sep 2026 — alasannya di docs/fase1 drafter.md bagian 6.1.
 */
export type JenisTanda = "penggantian" | "penghapusan" | "catatan";

export type StatusTemuan = "belum_ditinjau" | "diterima" | "ditolak";

export interface LokasiTemuan {
  paragraf_index: number;
  offset_mulai: number;
  panjang: number;
  teks_asli: string;
}

export interface RujukanTemuan {
  sumber: string;
  butir: string;
  kutipan: string;
  pdf_url: string;
  /**
   * Halaman butirnya di PDF KMK 527. Dipakai komentar Word menggantikan
   * `pdf_url` — seluruh entri tabel rujukan menunjuk beranda jdih, dan beranda
   * bukan rujukan. Nomor halaman bisa langsung dibuka penelaah.
   */
  halaman?: string;
  /**
   * Keandalan rujukan:
   * - "placeholder" — belum diisi sama sekali
   * - "ekstraksi"   — dari teks OCR, belum dibaca manusia
   * - "turunan"     — butirnya SUDAH dibaca manusia, tetapi aturannya akibat
   *                   butir itu, bukan bunyinya (ditambahkan 25 Sep 2026)
   * - "visual"      — sudah diketik ulang manusia dari naskah
   *
   * Gate legal menyala untuk apa pun yang BUKAN "visual". Sebelum 18 Sep 2026
   * gate itu menilai dari keterisian butir — begitu butirnya diisi dari OCR,
   * gate-nya mati sendiri padahal tidak ada yang diverifikasi.
   *
   * "turunan" ikut menyalakan gate, tetapi penandanya berbunyi lain: butirnya
   * benar dan bisa ditelusuri, yang perlu ditimbang penelaah cuma apakah
   * turunannya sah. Menyamakannya dengan "belum diverifikasi" membuang
   * keterangan yang sudah susah payah diperiksa.
   *
   * Fase 4 menambah tiga:
   * - "agen"      — Dasar analisisnya kosong, agen yang mencarikan; alamat dan
   *                 kutipannya terbukti ada di teks skill atau hasil korpus,
   *                 tetapi belum disalin manusia ke baris Dasar
   * - "prioritas" — dasarnya prioritas penelaah: tanpa baris rujukan
   * - "tanpa"     — tidak ada rujukan yang terbukti: tidak dikarang
   *
   * Sejak Fase 4 `butir` berisi alamat lengkap berikut halamannya, mis.
   * "Lampiran II angka III huruf A butir 8, hlm 30".
   */
  status?: "placeholder" | "ekstraksi" | "turunan" | "visual" | "agen" | "prioritas" | "tanpa";
}

/**
 * Satuan baru yang disisipkan di tempat perbaikannya (Fase 4) — hijau, satu
 * paragraf, sesudah paragraf `sesudah_paragraf`. Teks lama tidak disentuh;
 * Tolak mencabut paragrafnya bersih.
 */
export interface Sisipan {
  /** Id satuan tempat sisipan, mis. "pasal-1". */
  sasaran: string;
  /** Index paragraf terakhir satuan sasaran — paragraf baru SESUDAH ini. */
  sesudah_paragraf: number;
  /** angka · huruf · ayat */
  bentuk: string;
  /** Nomor satuan baru seperti tertulis, mis. "18." atau "(4)". Boleh kosong. */
  penanda: string;
  /** Isi satuan baru, tanpa penandanya. */
  teks: string;
  /** Peraturan asal rumusannya, atau "(prediksi AI)". */
  sumber: string;
  letak_ideal?: string;
  /** Index paragraf satuan sejenis terakhir — menjorok sisipan disamakan dengannya. -1 bila tidak ada. */
  format_dari?: number;
  /**
   * HANYA DI PANEL: nomor paragraf sisipan di naskah sesudah dipasang. Dipakai
   * menggeser nomor paragraf temuan lain saat sisipannya dicabut Tolak.
   */
  paragraf?: number;
}

/** Sepotong paragraf yang gayanya berbeda dari gaya utama paragrafnya. */
export interface BagianFormat {
  keterangan: string;
  kutipan: string;
}

/**
 * Format satu paragraf seperti dibaca Office.js. Medan yang kosong berarti
 * TIDAK TERBACA, bukan bernilai bawaan — backend menuliskannya apa adanya ke
 * naskah berformat, dan tidak menilai satu pun di antaranya.
 */
export interface FormatParagraf {
  huruf?: string | null;
  ukuran?: number | null;
  tebal?: boolean | null;
  miring?: boolean | null;
  garis_bawah?: boolean | null;
  kapital_gaya?: boolean | null;
  warna?: string | null;
  /** "rata kiri" · "tengah" · "rata kanan" · "rata kiri-kanan" — sama dengan tools/baca_format.py. */
  rata?: string | null;
  kiri_cm?: number | null;
  kanan_cm?: number | null;
  /** Negatif berarti menggantung. */
  baris_pertama_cm?: number | null;
  /** Kelipatan baris, mis. 1 atau 1,5. */
  spasi_baris?: number | null;
  spasi_sebelum_pt?: number | null;
  spasi_sesudah_pt?: number | null;
  /** Potongan teks bergaya hidden — tidak tampil di Word. */
  tersembunyi?: string[];
  bagian_beda?: BagianFormat[];
}

/** Format satu bagian (section) Word — kertas, marjin, kepala halaman. */
export interface FormatHalaman {
  bagian: number;
  lebar_cm?: number | null;
  tinggi_cm?: number | null;
  marjin_atas_cm?: number | null;
  marjin_bawah_cm?: number | null;
  marjin_kiri_cm?: number | null;
  marjin_kanan_cm?: number | null;
  halaman_pertama_beda?: boolean | null;
  kepala_pertama?: string;
  kepala_berikut?: string;
  gambar_kepala_pertama?: number;
  nomor_halaman?: boolean | null;
}

export interface Temuan {
  id: string;
  /** Nomor urut menurut posisi di dokumen. Ditampilkan sebagai (T1), (T2). */
  nomor: number;
  /** Kunci tabel rujukan. INTERNAL — jangan pernah ditampilkan ke penelaah. */
  aturan_id: string;
  /**
   * 1 format baku, 2 konsistensi dan kejelasan, 3 pertentangan dengan
   * peraturan lain. Dipakai panel untuk MENGELOMPOKKAN secara visual, tidak
   * pernah untuk menomori ulang — (T3) sudah tertulis di komentar Word.
   */
  fase: number;
  /**
   * Alamat satuan asalnya, mis. "pasal-12-ayat-2". Kosong untuk Fase 1, yang
   * bekerja di atas paragraf datar dan tidak mengenal satuan.
   */
  satuan_id?: string | null;
  /**
   * Keyakinan model, 0.0–1.0. Kosong untuk temuan deterministik, dan
   * kekosongan itu BERARTI: temuan tanpa skor kesalahannya bisa dibuktikan
   * baris demi baris, temuan berskor hasil penalaran.
   */
  skor?: number | null;
  jenis_tanda: JenisTanda;
  lokasi: LokasiTemuan;
  /** Alasan temuan, bukan pengulangan apa yang sudah terlihat di naskah. */
  catatan: string;
  /**
   * Apa yang sebaiknya DILAKUKAN penelaah. Dipisah dari `catatan` supaya
   * komentar Word bisa ditata "Temuan:" lalu "Saran:". Boleh kosong.
   */
  saran?: string;
  /**
   * DARI MANA rumusan hijau itu datang — "istilah berdefinisi Pasal 1: Pengguna
   * Barang", atau "PMK 40 TAHUN 2024 (masih berlaku)".
   *
   * Medan sendiri, bukan bagian `saran`: komentar temuan hijau sengaja
   * melewati blok Saran (penggantinya sudah terbaca hijau di naskah), tetapi
   * sumbernya WAJIB tetap terbaca — itu syarat kebijakan hijau, bukan hiasan.
   * Hanya terisi pada temuan `penggantian`.
   */
  sumber_usulan?: string;
  /**
   * Tempat LAIN yang memuat kesalahan yang sama persis ("Pasal 13 ayat (2)").
   * Satu kesalahan yang terulang jadi satu kartu dan satu komentar di
   * kemunculan pertamanya; sisanya cuma disebut di sini, tidak disorot.
   */
  juga_di?: string[];
  /**
   * DI MANA perbaikannya dikerjakan, sudah dalam bentuk yang dibaca manusia —
   * "Pasal 1 (Ketentuan Umum)", "bagian Menimbang". Muncul sebagai baris
   * "Perbaiki di:" di komentar Word.
   *
   * Kosong berarti tempatnya tidak bisa dibuktikan ada di naskah, ATAU
   * tempatnya satuan temuan ini sendiri. Keduanya berakhir sama: barisnya
   * tidak ditulis. Backend yang memutuskan, panel tidak menebak.
   */
  sasaran?: string;
  /**
   * Nomor paragraf tempat `sasaran` berada — dipakai tombol "Lompat ke
   * Perbaikan" di kartu panel.
   *
   * Nomor paragraf, bukan id satuan: panel tidak memegang pohon satuan, dan
   * Word mengalamati isinya dengan nomor paragraf. Kosong berarti sasarannya
   * bukan satuan yang bisa ditunjuk (mis. bagian Menimbang) — tombolnya tidak
   * digambar sama sekali, bukan digambar lalu tidak mengerjakan apa-apa.
   */
  sasaran_paragraf?: number | null;
  /**
   * Teks pengganti harfiah untuk lokasi.teks_asli — HANYA terisi pada temuan
   * `penggantian`, dan penggantian hanya dipakai ketika kesalahannya terbukti
   * dan penggantinya satu dan pasti. Pada temuan `catatan` selalu null;
   * contoh rumusan dari model ikut ke dalam `saran`, bukan ke naskah.
   */
  usulan_rumusan: string | null;
  /**
   * Keberatan model atas temuan ini — dan HANYA keberatan, bukan pembatalan.
   * Model membaca temuan Fase 1 saat menyusun peta; kalau menurutnya sebuah
   * temuan keliru karena konteks yang lebih luas, catatannya muncul di sini
   * dan temuannya TETAP ADA. Penelaah yang memutuskan.
   */
  catatan_ai?: string;
  /**
   * True HANYA untuk temuan yang kesalahannya adalah KETIADAAN sesuatu (bagian
   * wajib hilang, atau frasa hilang dari judul Menetapkan) — bukan kata
   * tertentu yang salah. `lokasi` di sini menunjuk anchor NETRAL (baris judul
   * pembuka dokumen), dipilih hanya karena selalu ada dan aman disentuh —
   * BUKAN klaim bahwa teks di situ salah.
   *
   * Panel tetap memasang komentar dan content control seperti temuan lain
   * (Terima/Tolak berfungsi normal), tetapi MELEWATI pewarnaan sorot/highlight
   * supaya anchor netral itu tidak terlihat seolah teksnya sendiri yang
   * bermasalah. Ditambahkan 27 Sep 2026.
   */
  tanpa_sorot?: boolean;
  rujukan: RujukanTemuan;
  /**
   * Peraturan lain yang jadi sandaran temuan, mis. "PMK 5 Tahun 2023 Pasal 8
   * (masih berlaku)" — terbukti ada di hasil pencarian korpus (Fase 4).
   */
  pembanding?: string;
  /**
   * Perbaikannya disisipkan di satuan lain sebagai satuan baru (Fase 4).
   * Komentarnya menempel di sisipan itu; di tempat temuan teksnya cuma
   * disorot, tanpa komentar.
   */
  sisipan?: Sisipan | null;
  status: StatusTemuan;
}

export interface ParagrafInput {
  index: number;
  /** Isi paragraf PERSIS seperti Word menyimpannya. Offset penandaan memakai ini. */
  teks: string;
  /**
   * Nomor otomatis Word apa adanya seperti tampil — "Pasal 5", "(2)", "a.",
   * "BAB I". Kosong untuk paragraf yang tidak bernomor otomatis.
   *
   * Dipisah dari `teks` dan TIDAK ditempel ke depannya: offset penandaan
   * dihitung terhadap `teks`, dan Word tidak punya awalan itu di teksnya.
   * Menempelkannya membuat seluruh sorotan meleset sepanjang awalannya.
   */
  penanda?: string;
  /** Tingkat kedalaman penomoran (ilvl Word), 0 paling luar. -1 bila bukan butir. */
  tingkat?: number;
  /**
   * Dulu diisi dari font.allCaps untuk menandai paragraf yang DITAMPILKAN
   * kapital meski hurufnya tersimpan campur. Tidak lagi dikirim frontend:
   * satu-satunya pemakainya adalah aturan judul kapital (F1-001), dan aturan
   * itu dimatikan karena tidak bisa membuktikan kesalahannya. Field-nya
   * dibiarkan opsional supaya kontrak lamanya tidak pecah.
   */
  tampil_kapital?: boolean;
  /**
   * Letak fisik di Word (bug 7 dan 11). Tabel tidak selalu berarti data:
   * PMK 119 menulis batang tubuhnya di tabel tata letak, nomor "1." di satu
   * sel dan teksnya di sel sebelahnya — tanpa letak ini parser tidak tahu
   * keduanya satu butir. `tabel` nomor urut tabel terdalam, -1 bila bukan di
   * tabel.
   */
  tabel?: number;
  baris?: number;
  sel?: number;
  /** Jumlah gambar sebaris — isinya tidak terbaca model, dan bahan menyebutnya. */
  gambar?: number;
  /**
   * False untuk paragraf SESUDAH tabel raksasa: panel tidak membaca isi
   * tabel itu, jadi `index` di sini urutan baca, bukan nomor paragraf Word.
   * Temuan di paragraf begini tidak pernah ditandai di naskah.
   */
  letak_pasti?: boolean;
  /** Format paragraf (Fase 4) — hanya dibaca bila alur agen menyala. */
  format?: FormatParagraf;
}

/**
 * Tabel raksasa (di atas BATAS_BARIS_RAKSASA baris) yang TIDAK dibaca per
 * paragraf — cukup kerangkanya. PMK 108/2024 memuat 228 ribu baris tabel.
 */
export interface KerangkaTabel {
  tabel: number;
  /** index paragraf terakhir SEBELUM tabel ini; -1 bila di awal naskah. */
  sesudah_paragraf: number;
  jumlah_baris: number;
  jumlah_kolom: number;
  /** Beberapa baris pertama, teks tiap sel. */
  contoh: string[][];
}

/** Hasil membaca naskah: paragraf, dan kerangka tabel yang terlalu besar dibaca. */
export interface NaskahTerbaca {
  paragraf: ParagrafInput[];
  tabel_raksasa: KerangkaTabel[];
  /** Format tiap bagian (section) — hanya dibaca bila alur agen menyala. */
  halaman?: FormatHalaman[];
}

export interface AnalisisRequest {
  jenis_dokumen: JenisDokumen;
  paragraf: ParagrafInput[];
  /**
   * Daftar aturan_id yang dijalankan, dipilih penelaah lewat panel Pengaturan.
   * Dihilangkan (undefined) berarti jalankan semua aturan bawaan.
   */
  aturan_aktif?: string[];
}

/** Satu baris di panel Pengaturan — apa yang diperiksa sebuah aturan. */
export interface KeteranganAturan {
  id: string;
  judul: string;
  /** Yang benar-benar diperiksa, dirinci supaya bisa dicek manual penelaah. */
  diperiksa: string[];
  /** Yang sengaja TIDAK diperiksa. Sama pentingnya untuk diketahui. */
  tidakDiperiksa: string[];
  /** Cara temuannya muncul di naskah. */
  tanda: string;
  /**
   * Terisi bila dasar aturannya sendiri belum dipastikan. Wajib ditampilkan:
   * penelaah berhak tahu aturan mana yang berdiri di atas rujukan yang belum
   * diverifikasi, supaya bisa menimbangnya sendiri.
   */
  catatanSumber?: string;
  /** Terisi bila aturannya dimatikan di kode — tidak bisa dinyalakan panel. */
  dimatikan?: string;
}

export interface AnalisisResponse {
  temuan: Temuan[];
  jumlah_paragraf: number;
}

// ---------------------------------------------------------------------------
// Fase 2 dan 3 — analisis panjang
// ---------------------------------------------------------------------------
//
// Bedanya dengan Fase 1 bukan cuma isi, melainkan BENTUK PERCAKAPANNYA. Fase 1
// satu permintaan satu jawaban. Fase 2 berjalan menit, jadi permintaannya
// dijawab segera dengan nomor pekerjaan dan hasilnya diambil berkala.
//
// Kenapa begitu: panel yang menunggu satu permintaan selama tiga menit
// dianggap macet oleh Word, dan penelaah tidak bisa membaca temuan Fase 1
// sementara Fase 2 berjalan.

export type StatusPekerjaan = "menunggu" | "berjalan" | "selesai" | "gagal";

export interface AnalisisLanjutRequest {
  paragraf: ParagrafInput[];
  /** Kerangka tabel raksasa yang tidak dibaca per paragraf. */
  tabel_raksasa?: KerangkaTabel[];
  dokumen?: string;
  /** Kode aturan yang dicentang penelaah. Dihilangkan berarti semua. */
  aturan_aktif?: string[];
  /**
   * Nomor temuan pertama Fase 2 — MELANJUTKAN nomor terakhir Fase 1.
   * Nomor tidak pernah diurutkan ulang: (T3) sudah tertulis di komentar Word,
   * dan menomori ulang membuat komentar itu menunjuk temuan yang berbeda.
   */
  mulai_nomor?: number;
  /** Batas ATAS jumlah temuan, bukan target yang harus dipenuhi model. */
  batas_temuan?: number;
  ambang?: number;
  /** Cari pembanding di korpus peraturan. Mati secara bawaan. */
  fase3?: boolean;
  /** Nomor pekerjaan lama yang jawaban tahap 3-nya dipakai ulang, supaya tidak dibayar dua kali. */
  lanjutkan?: number;
  /**
   * Temuan Fase 1 yang SUDAH terpasang di naskah. Dikirim supaya model tidak
   * mengulangnya, dan supaya Langkah 5 bisa membuang calon yang rentangnya
   * bertindihan.
   */
  temuan_fase1?: Temuan[];
}

export interface MulaiResponse {
  pekerjaan: number;
  status: StatusPekerjaan;
  pesan?: string;
}

export interface KemajuanResponse {
  pekerjaan: number;
  status: StatusPekerjaan;
  /** Tahap yang sedang berjalan: "3 cari dugaan", "4 memastikan", "5 verifikasi". */
  tahap: string;
  /** Kemajuan tahap itu: panggilan (tahap 3) atau dugaan (tahap 4). */
  selesai: number;
  total: number;
  panggilan: number;
  token_masuk: number;
  token_keluar: number;
  /** Alasan gagal, atau keterangan kenapa Fase 2 tidak dijalankan (mis. naskah KMK). */
  pesan: string;
  temuan: Temuan[];
  /**
   * Temuan Fase 1 yang dapat catatan keberatan dari model. Panel memperbarui
   * komentarnya di naskah; temuannya sendiri tidak dihapus.
   */
  keberatan?: Temuan[];
}

// ---------------------------------------------------------------------------
// Fase 4 — agen penuh dengan skills (saklar FASE2_ALUR=agen di backend)
// ---------------------------------------------------------------------------
//
// Satu pekerjaan untuk SELURUH pemeriksaan: tidak ada lagi Fase 1 yang
// ditandai lebih dulu. Semua tanda dipasang sesudah gerbang, di akhir — itu
// yang membuat tombol Batal bisa bersih.

/** Alur yang menyala di backend: "lama" (Fase 1–3) atau "agen" (Fase 4). */
export type AlurAnalisis = "lama" | "agen";

/** Satu baris daftar Pengaturan, dibaca dari analisis.md / analisisformat.md. */
export interface AnalisisPanel {
  id: string;
  judul: string;
  /** "isi" atau "format". */
  kelompok: string;
  /** Batas atas bentuk tanda: otomatis · usulan · dibuang · catatan. */
  respons: string;
  lingkup: string;
  butuh: string[];
  /** Alamat KMK 527 lengkap, "prioritas penelaah", atau kosong. */
  dasar: string;
  /** visual · turunan · prioritas · "" (Dasar kosong). */
  dasar_status: string;
  diperiksa: string[];
  tidakDiperiksa: string[];
  tersedia: boolean;
  /** Kenapa tidak tersedia — mis. "belum tersedia untuk KMK". */
  alasan: string;
}

export interface DaftarAnalisisResponse {
  alur: AlurAnalisis;
  jenis: string;
  analisis: AnalisisPanel[];
}

export interface AnalisisAgenRequest {
  paragraf: ParagrafInput[];
  halaman?: FormatHalaman[];
  tabel_raksasa?: KerangkaTabel[];
  dokumen?: string;
  jenis_dokumen: JenisDokumen;
  /** Kode analisis yang dicentang. Dihilangkan berarti semua. */
  aturan_aktif?: string[];
  /** Nomor temuan pertama — Periksa ulang melanjutkan nomor terakhir. */
  mulai_nomor?: number;
  /** Periksa ulang: temuan sebelumnya berikut keputusan penelaah. */
  temuan_lama?: Temuan[];
  /** Nomor pekerjaan lama yang jawabannya dipakai ulang — tidak dibayar dua kali. */
  lanjutkan?: number;
}

/** Keadaan satu putaran agen, untuk kemajuan per putaran di panel. */
export interface KeadaanPutaran {
  kode: string;
  /** "Putaran 1/6 · Pasal 1–6", "Lintas naskah", "Lampiran", "Format". */
  judul: string;
  /** menunggu · berjalan · menilai · selesai · macet · dibatalkan · gagal */
  keadaan: string;
  langkah: number;
  calon: number;
}

export interface KemajuanAgenResponse {
  pekerjaan: number;
  status: StatusPekerjaan;
  /** "1 bahan" · "2 agen" · "3 gerbang" · "selesai" · "dibatalkan". */
  tahap: string;
  putaran: KeadaanPutaran[];
  panggilan: number;
  token_masuk: number;
  token_keluar: number;
  /** Alasan gagal, atau kenapa analisis tidak dijalankan. */
  pesan: string;
  /** Analisis yang tidak dikirim, putaran macet, pasal tidak diperiksa. */
  peringatan: string[];
  temuan: Temuan[];
}
