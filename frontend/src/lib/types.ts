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
}

export interface AnalisisResponse {
  temuan: Temuan[];
  jumlah_paragraf: number;
}
