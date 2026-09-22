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
 * - catatan: blok kuning, warna huruf tidak disentuh
 *
 * Keterangan lama menyebut "perubahan terlacak (Track Changes)". Jalur itu
 * ditinggalkan 17 Sep 2026 — alasannya di docs/fase1 drafter.md bagian 6.1.
 */
export type JenisTanda = "penggantian" | "catatan";

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
   * Keandalan rujukan: "placeholder" (belum diisi), "ekstraksi" (dari teks
   * OCR, belum dibaca manusia), "visual" (sudah diketik ulang manusia dari
   * naskah).
   *
   * Gate legal menyala untuk apa pun yang BUKAN "visual". Sebelum 18 Sep 2026
   * gate itu menilai dari keterisian butir — begitu butirnya diisi dari OCR,
   * gate-nya mati sendiri padahal tidak ada yang diverifikasi.
   */
  status?: "placeholder" | "ekstraksi" | "visual";
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
  usulan_rumusan: string | null;
  rujukan: RujukanTemuan;
  status: StatusTemuan;
}

export interface ParagrafInput {
  index: number;
  teks: string;
  /**
   * Dulu diisi dari font.allCaps untuk menandai paragraf yang DITAMPILKAN
   * kapital meski hurufnya tersimpan campur. Tidak lagi dikirim frontend:
   * satu-satunya pemakainya adalah aturan judul kapital (F1-001), dan aturan
   * itu dimatikan karena tidak bisa membuktikan kesalahannya. Field-nya
   * dibiarkan opsional supaya kontrak lamanya tidak pecah.
   */
  tampil_kapital?: boolean;
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
  /** Nomor pekerjaan lama yang petanya dipakai ulang, supaya tidak dibayar dua kali. */
  lanjutkan?: number;
}

export interface MulaiResponse {
  pekerjaan: number;
  status: StatusPekerjaan;
  pesan?: string;
}

export interface KemajuanResponse {
  pekerjaan: number;
  status: StatusPekerjaan;
  satuan_total: number;
  satuan_selesai: number;
  panggilan: number;
  token_masuk: number;
  token_keluar: number;
  /** Alasan gagal, atau keterangan kenapa Fase 2 tidak dijalankan (mis. naskah KMK). */
  pesan: string;
  temuan: Temuan[];
}
