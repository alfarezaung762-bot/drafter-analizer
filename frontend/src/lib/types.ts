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
 * - penggantian: perubahan terlacak (Track Changes)
 * - catatan: blok kuning + komentar
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
  fase: number;
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
