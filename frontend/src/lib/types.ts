/**
 * Tipe data Temuan — sinkron dengan backend app.models.temuan dan docs/kontrak-data.md.
 */

export type TingkatKeparahan = "tinggi" | "sedang" | "rendah";

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
  aturan_id: string;
  fase: number;
  tingkat_keparahan: TingkatKeparahan;
  lokasi: LokasiTemuan;
  catatan: string;
  usulan_rumusan: string | null;
  rujukan: RujukanTemuan;
  status: StatusTemuan;
}

export interface ParagrafInput {
  index: number;
  teks: string;
}

export interface AnalisisRequest {
  paragraf: ParagrafInput[];
}

export interface AnalisisResponse {
  temuan: Temuan[];
  jumlah_paragraf: number;
}
