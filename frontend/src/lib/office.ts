/**
 * Kumpulan fungsi wrapper Office.js untuk Drafter Analiser.
 *
 * Semua pemanggilan Office.js dikumpulkan di file ini.
 * Sumber kebenaran: frontend/node_modules/@types/office-js/index.d.ts
 *
 * ===========================================================================
 * REVISI BESAR 17 Sep 2026 — TRACK CHANGES DITINGGALKAN
 * ===========================================================================
 *
 * Sebelumnya usulan penggantian dipasang sebagai perubahan terlacak Word.
 * Itu ditinggalkan atas keputusan penelaah, karena dua alasan yang keduanya
 * terbukti di naskah sungguhan:
 *
 * 1. Warna revisi Track Changes TIDAK BISA diatur add-in. Sudah dicari ke
 *    seluruh index.d.ts: tidak ada insertedTextColor, deletedTextColor,
 *    revisionColor, maupun authorColor. RevisionsFilter cuma punya `markup`
 *    dan `view`. Warnanya ditentukan Word menurut penulis. Satu-satunya cara
 *    mengubahnya adalah Options Word masing-masing penelaah — dan syarat yang
 *    dipegang adalah penelaah tidak menyetel apa pun.
 *
 * 2. Memberi blok warna selagi pelacakan menyala membuat Word mencatat TIAP
 *    pewarnaan sebagai revisi "Formatted: Highlight". Pada RKMK 527, dua
 *    temuan menghasilkan tiga baris revisi format di margin — mengubur
 *    komentar yang justru perlu dibaca.
 *
 * Gantinya: alat menggambar tandanya sendiri dengan pelacakan DIMATIKAN.
 * Tiga warna, tiga arti yang berbeda:
 *
 *   MERAH + DICORET — teks yang salah DAN ada rumusan penggantinya
 *   HIJAU           — usulan penggantinya, disisipkan di sebelahnya
 *   BLOK KUNING     — catatan: ada yang perlu ditinjau, tetapi alat tidak tahu
 *                     rumusan benarnya. Peringatan, bukan usul penghapusan.
 *
 * Pembedaan kuning itu diminta penelaah 17 Sep 2026, dan alasannya benar:
 * memberi warna merah pada temuan yang tidak punya pengganti membuat alat
 * seolah mengusulkan teks itu dibuang, padahal yang dimaksud cuma "periksa
 * bagian ini". Merah dipakai hanya bila ada jawabannya.
 *
 * Satu komentar per temuan, tidak lebih.
 *
 * Font.color, Font.strikeThrough, dan Font.highlightColor semuanya WordApi 1.1
 * — himpunan paling dasar, tersedia di Word desktop mana pun.
 *
 * Yang harus disadari, dan sudah disetujui penelaah:
 * Word TIDAK tahu tanda ini usulan mesin. Tab Review menunjukkan 0 revisions,
 * Accept All/Reject All bawaan Word tidak melakukan apa-apa, dan tidak ada
 * nama pengusul maupun waktunya. Yang mengenali tandanya hanya add-in ini,
 * lewat content control bertag (WordApi 1.1) yang dipasangnya sendiri.
 * Naskah kerja merah-hijau inilah dokumen "coretan"; versi bersihnya dibuat
 * terpisah lewat ekspor.
 */

import { ParagrafInput, Temuan } from "./types";

/**
 * Cek apakah Office.js runtime tersedia.
 */
export function isOfficeAvailable(): boolean {
  return typeof Office !== "undefined" && typeof Word !== "undefined";
}

/**
 * Cek dukungan requirement set tertentu secara runtime.
 *
 * PERINGATAN: requirement set didukung TIDAK berarti fiturnya diizinkan.
 * Critique lolos pemeriksaan ini lalu tetap melempar NotImplemented karena
 * terkunci lisensi. Karena itu tiap pemanggilan tetap dibungkus try/catch.
 */
export function checkApiSupport(version: string, nama = "WordApi"): boolean {
  if (!isOfficeAvailable() || !Office.context?.requirements) {
    return false;
  }
  try {
    return Office.context.requirements.isSetSupported(nama, version);
  } catch {
    return false;
  }
}

/**
 * Membaca paragraf dokumen (seluruh dokumen atau teks terpilih).
 *
 * Catatan 17 Sep 2026: pembacaan font.allCaps DIHAPUS dari sini. Satu-satunya
 * pemakainya adalah aturan judul kapital (F1-001), dan aturan itu dimatikan
 * karena tidak bisa membuktikan kesalahannya — lihat AKTIFKAN_F1_001 di
 * backend/app/rules/format_baku.py. Membacanya berarti satu putaran sync
 * tambahan atas ratusan paragraf untuk data yang tidak dipakai siapa pun.
 */
/**
 * Apakah cakupan "Bagian Terpilih" bisa dipakai di Word ini.
 *
 * Mode itu bersandar pada `Range.intersectWithOrNullObject()`, yang sudah
 * diverifikasi ke index.d.ts sebagai **WordApi 1.3** — sementara seluruh
 * penandaan alat ini sengaja dijaga di 1.1 dan manifest mendeklarasikan 1.1.
 * Tanpa pemeriksaan ini, menekan Analisis dalam mode terpilih di Word yang
 * tidak punya 1.3 cuma menghasilkan "Gagal menjalankan analisis" tanpa
 * penjelasan. Panel memakainya untuk menonaktifkan tombolnya lebih dulu —
 * itulah jalur cadangan runtime yang diwajibkan CLAUDE.md butir 9.
 */
export function cakupanTerpilihTersedia(): boolean {
  return checkApiSupport("1.3");
}

/**
 * Nomor otomatis Word tiap paragraf — "Pasal 5", "(2)", "a.", "BAB I".
 *
 * KENAPA INI ADA. `paragraph.text` TIDAK memuat nomor yang dibuat mesin
 * penomoran Word. Pada PMK 18 Tahun 2026 yang sudah diundangkan, 585 dari 974
 * paragrafnya bernomor otomatis dan 110 di antaranya teksnya kosong sama
 * sekali — seluruh isinya nomor. Tanpa fungsi ini, backend menerima dokumen
 * tanpa satu pun "Pasal", lalu menuduh ayat yang jelas-jelas ada sebagai tidak
 * ada. Itu salah tandai, dan salah tandai merusak kepercayaan penelaah.
 *
 * DIJALANKAN DI Word.run SENDIRI, bukan menumpang pembacaan teks. Kalau
 * pemuatannya gagal di tengah jalan, konteksnya tercemar — dan kegagalan di
 * sini tidak boleh ikut menjatuhkan pembacaan teks yang sudah pasti berhasil.
 *
 * CLAUDE.md butir 9: requirement set didukung ≠ fitur diizinkan. Karena itu
 * ada dua lapis penjagaan — pemeriksaan 1.3, DAN try/catch runtime. Kalau
 * keduanya jebol, hasilnya daftar kosong dan analisis tetap berjalan seperti
 * sebelum fitur ini ada.
 */
async function bacaPenanda(): Promise<{ penanda: string; tingkat: number }[]> {
  if (!checkApiSupport("1.3")) return [];
  try {
    return await Word.run(async (context) => {
      const paragraf = context.document.body.paragraphs;
      paragraf.load("items");
      await context.sync();

      const butir = paragraf.items.map((p) => p.listItemOrNullObject);
      butir.forEach((b) => b.load("isNullObject,listString,level"));
      await context.sync();

      return butir.map((b) =>
        b.isNullObject
          ? { penanda: "", tingkat: -1 }
          : { penanda: b.listString ?? "", tingkat: b.level ?? -1 }
      );
    });
  } catch (err) {
    console.warn(
      "Nomor otomatis Word tidak terbaca; analisis lanjut memakai teks apa adanya.",
      err
    );
    return [];
  }
}

export async function readParagraphs(
  scope: "all" | "selection" = "all"
): Promise<ParagrafInput[]> {
  if (!isOfficeAvailable()) {
    throw new Error("Office.js tidak tersedia dalam lingkungan ini.");
  }

  if (scope === "selection" && !cakupanTerpilihTersedia()) {
    throw new Error(
      "Word ini belum mendukung cakupan Bagian Terpilih (butuh WordApi 1.3). " +
        "Pakai Seluruh Naskah."
    );
  }

  // Dibaca untuk SELURUH badan dokumen, bukan cuma bagian terpilih: nomor
  // paragraf di bawah memang penomoran seluruh dokumen, jadi indeksnya cocok.
  const nomor = await bacaPenanda();
  const ambil = (idx: number) => ({
    penanda: nomor[idx]?.penanda ?? "",
    tingkat: nomor[idx]?.tingkat ?? -1,
  });

  return Word.run(async (context) => {
    const body = context.document.body.paragraphs;
    body.load("text");
    await context.sync();

    if (scope !== "selection") {
      return body.items.map((p, idx) => ({
        index: idx,
        teks: p.text,
        ...ambil(idx),
      }));
    }

    // Mode "Bagian Terpilih": nomor paragraf TETAP memakai penomoran seluruh
    // dokumen, bukan dihitung ulang dari nol di dalam seleksi. Sorotan dan
    // komentar dicari lewat body.paragraphs — nomor 0 di situ berarti paragraf
    // pertama dokumen, jadi penomoran ulang membuat tanda mendarat di paragraf
    // yang sama sekali lain.
    const seleksi = context.document.getSelection();
    const irisan = body.items.map((p) =>
      p.getRange().intersectWithOrNullObject(seleksi)
    );
    irisan.forEach((r) => r.load("isNullObject"));
    await context.sync();

    const hasil: ParagrafInput[] = [];
    body.items.forEach((p, idx) => {
      if (!irisan[idx].isNullObject) {
        hasil.push({ index: idx, teks: p.text, ...ambil(idx) });
      }
    });
    return hasil;
  });
}

// ---------------------------------------------------------------------------
// Warna dan penanda
// ---------------------------------------------------------------------------

/**
 * Merah tua — teks salah yang SUDAH ADA penggantinya. Dipakai bersama coretan.
 * Sama dengan "Dark Red" bawaan Word.
 */
const WARNA_SALAH = "#C00000";

/** Hijau tua — usulan rumusan pengganti. */
const WARNA_USULAN = "#00802B";

/**
 * Blok kuning — temuan yang perlu ditinjau tetapi tidak punya rumusan pengganti
 * tunggal. Warna latar, bukan warna huruf: huruf kuning tidak terbaca.
 *
 * Office untuk Windows Desktop hanya menerima warna bawaan bernama pada
 * highlightColor; dipakai namanya langsung supaya hasil di layar persis seperti
 * yang dimaksud.
 */
const WARNA_CATATAN = "Yellow";

/** Hitam, dipakai memulihkan warna bila warna asli tidak terbaca. */
const WARNA_NETRAL = "#000000";

/** Awalan tag content control. Dipakai menemukan kembali tanda milik alat. */
const TAG_ASLI = "DA-ASLI-";
const TAG_USUL = "DA-USUL-";

/**
 * Format asli tiap rentang sebelum ditimpa, agar Tolak bisa memulihkannya.
 * Kunci = NOMOR temuan.
 *
 * Kuncinya nomor, bukan id — diubah 18 Sep 2026. Tag content control di naskah
 * membawa nomor (`DA-ASLI-{nomor}`), jadi itulah satu-satunya jalan yang
 * tersedia saat tanda ditemukan kembali dari dokumen. Selama kuncinya id,
 * `bersihkanSemuaTanda()` tidak punya cara menemukan format aslinya dan
 * terpaksa memaksa semua warna jadi hitam — termasuk warna milik penyusun
 * pada temuan berblok kuning, yang warna hurufnya tidak pernah disentuh alat.
 * Nomor unik dalam satu sesi analisis, sama seperti id.
 *
 * Peta ini hanya hidup di memori tab selama panel terbuka. Kalau Word ditutup
 * sebelum temuan diputuskan, add-in tidak lagi tahu format aslinya — yang bisa
 * dilakukan tinggal mencabut warna yang persis sama dengan warna milik alat.
 * Ini keterbatasan yang sudah disepakati, bukan kelalaian; penelaah wajib
 * memeriksa ulang naskahnya.
 */
type FormatAsli = {
  color: string | null;
  strikeThrough: boolean | null;
  highlightColor: string | null;
};
const formatAsliTemuan = new Map<number, FormatAsli>();

/** Nomor temuan yang tersimpan di dalam sebuah tag `DA-ASLI-12` / `DA-USUL-3`. */
function nomorDariTag(tag: string | undefined): number | null {
  const m = /-(\d+)$/.exec(tag ?? "");
  if (!m) return null;
  const n = Number(m[1]);
  return Number.isFinite(n) ? n : null;
}

/** Apakah sebuah warna sama dengan warna yang dipasang alat ini sendiri. */
function samaDenganWarnaAlat(nilai: string | null, warna: string): boolean {
  return (nilai ?? "").trim().toUpperCase() === warna.toUpperCase();
}

/**
 * Kuning bawaan Word terbaca kembali sebagai `#FFFF00`, bukan sebagai nama
 * warnanya. Keduanya diperiksa supaya pencabutan tetap mengenai sasaran.
 */
const KUNING_TERBACA = ["#FFFF00", "YELLOW"];

/** Panjang aman untuk Word.search() — batas Word sendiri ada di sekitar 255. */
const AMAN_UNTUK_SEARCH = 200;

/** Apakah teks_asli temuan layak dipakai sebagai kata kunci pencarian presisi. */
function layakDicari(temuan: Temuan): boolean {
  const teks = temuan.lokasi.teks_asli?.trim();
  return (
    !!teks &&
    teks.length > 0 &&
    teks.length <= AMAN_UNTUK_SEARCH &&
    !/[\^*?[\]]/.test(teks)
  );
}

/** Kata kunci pencarian sebuah temuan, beserta posisinya di paragraf. */
function kunciTemuan(temuan: Temuan): { kunci: string; offset: number } {
  const asli = temuan.lokasi.teks_asli ?? "";
  const spasiAwal = asli.length - asli.trimStart().length;
  return {
    kunci: asli.trim(),
    offset: temuan.lokasi.offset_mulai + spasiAwal,
  };
}

/**
 * Kemunculan KE-BERAPA (0-based) kata kunci itu di dalam paragraf.
 *
 * Word.search() mengembalikan SEMUA kemunculan di paragraf, sedangkan backend
 * menunjuk satu posisi lewat offset_mulai. Tanpa perhitungan ini, temuan pada
 * kata yang berulang — "PERATURAN" di judul pencabutan, misalnya — selalu
 * mendarat di kemunculan pertama, bukan di kata yang sebenarnya dipersoalkan.
 *
 * Perhitungannya memakai teks paragraf yang dikirim ke backend, jadi nomor
 * urutnya sepadan dengan yang dipakai backend saat menghitung offset.
 */
function ordinalKemunculan(
  teksParagraf: string,
  kunci: string,
  offset: number
): number {
  if (!kunci) return 0;
  let n = 0;
  let i = teksParagraf.indexOf(kunci);
  while (i !== -1 && i < offset) {
    n++;
    i = teksParagraf.indexOf(kunci, i + 1);
  }
  return n;
}

/**
 * Isi komentar Word untuk sebuah temuan — tiga bagian bernama.
 *
 *     Temuan:
 *     <apa yang ditemukan>
 *     Saran:
 *     <apa yang sebaiknya dilakukan>
 *     <rujukan> — <tautan> (Tn)
 *
 * Bentuk ini ditetapkan penelaah, 22 Sep 2026. Alasannya disebut sendiri:
 * baris rujukan di bawah ada "agar penelaah ngerti ini bukan asal klaim dan
 * bisa dipertimbangkan". Jadi rujukannya bukan hiasan — ia yang membuat
 * temuan bisa ditimbang, bukan cuma dipercaya atau ditolak.
 *
 * "Saran" dibedakan dari "Temuan" karena keduanya memang beda jenis: yang
 * satu pernyataan tentang naskah, yang satu anjuran. Dilem jadi satu paragraf,
 * penelaah harus memilahnya sendiri tiap kali.
 *
 * Nama produk sengaja TIDAK ditulis: ruang komentar sempit, dan nomor temuan
 * sudah cukup jadi penanda.
 */
function susunIsiKomentar(temuan: Temuan): string {
  // Keandalan dibaca dari `status`, BUKAN dari keterisian butirnya. Butir yang
  // sudah terisi dari ekstraksi OCR tetap belum diverifikasi siapa pun, dan
  // komentar di naskah orang tidak boleh menampilkannya seolah final.
  const butir = temuan.rujukan.butir;
  const status = temuan.rujukan.status;
  // Tiga keadaan, dan masing-masing berbunyi lain di komentar. "turunan"
  // berarti butirnya sudah dibaca manusia dari naskah KMK 527 tetapi aturannya
  // AKIBAT butir itu, bukan bunyinya — penelaah berhak tahu bedanya sebelum
  // memakainya sebagai dasar mengubah naskah.
  const penanda =
    status === "visual"
      ? ""
      : status === "turunan"
        ? " (dasar turunan — butirnya mengatur hal lain yang berakibat ini)"
        : " (belum diverifikasi visual)";
  const rujukanStr =
    butir && butir !== "..."
      ? `${temuan.rujukan.sumber} butir ${butir}${penanda}`
      : `${temuan.rujukan.sumber} (butir belum diisi)`;

  const baris = [`Temuan:`, temuan.catatan];

  // DI MANA perbaikannya dikerjakan. Ada karena komentar yang menempel di
  // Pasal 5 bisa menyuruh menambah definisi, padahal definisinya harus
  // ditulis di Pasal 1 — dan penelaah tidak punya cara menebaknya.
  //
  // Backend sudah mengosongkannya kalau tempatnya tidak terbukti ada di
  // naskah, atau kalau tempatnya satuan temuan ini sendiri.
  const sasaran = temuan.sasaran?.trim();
  if (sasaran) baris.push(`Perbaiki di: ${sasaran}`);

  // Temuan lama (dan temuan Fase 1 yang belum dipisah medannya) bisa datang
  // tanpa `saran`. Blok Saran ditinggalkan kosong-melompong lebih buruk
  // daripada tidak ada blok sama sekali — dan sejak 23 Sep 2026 backend
  // sengaja mengosongkannya ketika penggantinya memang tidak diketahui,
  // daripada mengisinya dengan anjuran hampa.
  const saran = temuan.saran?.trim();
  if (saran) baris.push(`Saran:`, saran);

  // Keberatan model atas temuan ini. Ditempelkan, BUKAN menggantikan temuannya
  // — AI tidak pernah menghapus temuan yang kesalahannya sudah terbukti
  // (ditetapkan penelaah, 23 Sep 2026). Penelaah yang menimbang keduanya.
  const catatanAi = temuan.catatan_ai?.trim();
  if (catatanAi) baris.push(`Catatan AI:`, catatanAi);

  baris.push(
    `${rujukanStr} — ${temuan.rujukan.pdf_url} ${penandaKomentar(temuan)}`
  );
  return baris.join("\n");
}

/**
 * Penanda pengenal di dalam isi komentar, dipakai saat mencari untuk dihapus.
 *
 * Nomor temuan, bukan aturan_id: inilah yang dibaca penelaah. Konsekuensinya,
 * dua kali analisis pada dokumen yang sama menghasilkan komentar bernomor sama
 * — karena itu panel menolak analisis ulang selama masih ada temuan yang belum
 * diputuskan.
 */
function penandaKomentar(temuan: Temuan): string {
  return `(T${temuan.nomor})`;
}

// ---------------------------------------------------------------------------
// Mengatur pelacakan perubahan
// ---------------------------------------------------------------------------

/**
 * Mematikan pelacakan perubahan sementara, mengembalikan mode semula.
 *
 * SELURUH penandaan alat ini wajib berjalan dengan pelacakan mati. Kalau tidak,
 * tiap pewarnaan dan tiap penyisipan tercatat Word sebagai revisi — persis
 * keluhan "ajat — Formatted: Highlight" yang memenuhi margin pada RKMK 527.
 *
 * Mengembalikan mode semula supaya setelan Word penelaah tidak diam-diam
 * berubah gara-gara memakai alat ini.
 */
async function matikanPelacakan(
  context: Word.RequestContext
): Promise<{ modeAwal: string | null; berhasilMati: boolean }> {
  if (!checkApiSupport("1.4")) {
    return { modeAwal: null, berhasilMati: false };
  }
  const doc = context.document;
  doc.load("changeTrackingMode");
  await context.sync();

  const modeAwal = doc.changeTrackingMode as unknown as string;
  if (modeAwal === "Off") {
    return { modeAwal, berhasilMati: true };
  }
  try {
    doc.changeTrackingMode = "Off";
    await context.sync();
    doc.load("changeTrackingMode");
    await context.sync();
    return {
      modeAwal,
      berhasilMati: (doc.changeTrackingMode as unknown as string) === "Off",
    };
  } catch (err) {
    console.warn("Pelacakan perubahan tidak bisa dimatikan:", err);
    return { modeAwal, berhasilMati: false };
  }
}

async function kembalikanPelacakan(
  context: Word.RequestContext,
  modeAwal: string | null
): Promise<void> {
  if (modeAwal === null || modeAwal === "Off") return;
  try {
    context.document.changeTrackingMode =
      modeAwal as unknown as Word.ChangeTrackingMode;
    await context.sync();
  } catch (err) {
    console.warn("Mode pelacakan gagal dikembalikan:", err);
  }
}

// ---------------------------------------------------------------------------
// Penandaan temuan
// ---------------------------------------------------------------------------

/** Hasil satu kali penandaan, untuk ditampilkan di panel. */
export type HasilPenandaan = {
  /** Temuan bercoretan merah — yang salah DAN ada penggantinya. */
  dicoretMerah: number;
  /** Temuan berblok kuning — perlu ditinjau, tanpa rumusan pengganti. */
  diblokKuning: number;
  /** Jumlah usulan hijau yang ikut tersisip. */
  diusulkan: number;
  /** Jumlah komentar yang terpasang. */
  dikomentari: number;
  /**
   * Komentar yang terpasang tetapi isinya KOSONG sesudah dibaca ulang.
   *
   * Dilaporkan pada 25 Sep 2026: balon komentar muncul di margin dengan nama
   * penulis saja, tanpa satu huruf pun di dalamnya — jadi penelaah melihat
   * sorotan di naskah yang tidak menjelaskan apa-apa. Alat yang menempelkan
   * balon kosong tidak bisa dibedakan dari alat yang rusak, jadi kalau angka
   * ini bukan nol panel wajib menyebutnya.
   */
  komentarKosong: number;
  /**
   * Id temuan yang TIDAK tertandai di naskah — letak persisnya tidak ketemu,
   * atau pemasangannya gagal. Wajib disampaikan per temuan, bukan cuma
   * jumlahnya: kartunya di panel harus memuat alasannya sendiri, karena bagi
   * temuan ini tidak ada komentar di naskah yang bisa dibaca. Sebelum ini,
   * penelaah melihat kartu hampa bertombol Terima/Tolak yang tidak mengerjakan
   * apa pun (PMK 119, 18 Sep 2026).
   */
  idTidakDitandai: string[];
  /** Pelacakan perubahan berhasil dimatikan selama penandaan. */
  pelacakanMati: boolean;
};

/** Hasil sekali Bersihkan Daftar, untuk dilaporkan ke penelaah. */
export type HasilPembersihan = {
  /** Jumlah content control bertag DA-* yang dicabut. */
  tanda: number;
  /** Jumlah komentar milik alat yang ikut dihapus. */
  komentar: number;
};

const HASIL_KOSONG: HasilPenandaan = {
  dicoretMerah: 0,
  diblokKuning: 0,
  diusulkan: 0,
  dikomentari: 0,
  komentarKosong: 0,
  idTidakDitandai: [],
  pelacakanMati: false,
};

/**
 * Menandai SELURUH temuan sekaligus, dalam satu kali Word.run.
 *
 * Alurnya:
 *   1. Matikan pelacakan perubahan, ingat mode semula.
 *   2. Cari rentang presisi tiap temuan (sekali batch, bukan satu per satu).
 *   3. Rekam format asli tiap rentang, supaya Tolak bisa memulihkannya.
 *   4. Pasang tanda dari BAWAH ke ATAS — menyisipkan usulan menggeser posisi
 *      karakter sesudahnya, jadi yang di bawah dikerjakan lebih dulu.
 *   5. Kembalikan mode pelacakan.
 *
 * Temuan yang rentang presisinya tidak ketemu TIDAK ditandai sama sekali.
 * Menandai satu paragraf penuh karena pencarian meleset pernah terjadi di
 * proyek ini dan berakhir menutupi naskah yang tidak bersalah.
 *
 * Dua kelas tanda, sesuai ada-tidaknya rumusan pengganti:
 *   punya usulan  -> teks lama MERAH + DICORET, usulannya HIJAU di sebelahnya
 *   tanpa usulan  -> BLOK KUNING, warna huruf tidak disentuh
 */
export async function tandaiSemuaTemuan(
  daftar: Temuan[]
): Promise<HasilPenandaan> {
  if (!isOfficeAvailable() || daftar.length === 0) {
    return { ...HASIL_KOSONG };
  }

  const bisaKomentar = checkApiSupport("1.4");
  const hasil: HasilPenandaan = { ...HASIL_KOSONG, idTidakDitandai: [] };

  try {
    await Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load("items/text");
      await context.sync();

      const teksParagraf = paragraphs.items.map((p) => p.text ?? "");

      const { modeAwal, berhasilMati } = await matikanPelacakan(context);
      hasil.pelacakanMati = berhasilMati;

      // --- Tahap 1: cari rentang presisi seluruh temuan sekaligus ---
      const pencarian = daftar.map((t) => {
        const p = paragraphs.items[t.lokasi.paragraf_index];
        if (!p || !layakDicari(t)) return null;
        const r = p.search(kunciTemuan(t).kunci, { matchCase: true });
        r.load("items");
        return r;
      });
      await context.sync();

      const rentang = daftar.map((t, i) => {
        const hasilCari = pencarian[i];
        if (!hasilCari || hasilCari.items.length === 0) return null;
        const { kunci, offset } = kunciTemuan(t);
        const n = ordinalKemunculan(
          teksParagraf[t.lokasi.paragraf_index] ?? "",
          kunci,
          offset
        );
        return hasilCari.items[Math.min(n, hasilCari.items.length - 1)];
      });

      // --- Tahap 2: rekam format asli ---
      const fonts = rentang.map((r) => {
        if (!r) return null;
        const f = r.font;
        f.load("color,strikeThrough,highlightColor");
        return f;
      });
      await context.sync();

      // --- Tahap 3: pasang tanda, dari BAWAH ke ATAS ---
      const antrean = daftar
        .map((t, i) => ({ t, i }))
        .filter((x) => rentang[x.i] !== null)
        .sort(
          (a, b) =>
            b.t.lokasi.paragraf_index - a.t.lokasi.paragraf_index ||
            b.t.lokasi.offset_mulai - a.t.lokasi.offset_mulai
        );

      const ketemu = new Set(antrean.map((x) => x.t.id));
      hasil.idTidakDitandai = daftar
        .filter((t) => !ketemu.has(t.id))
        .map((t) => t.id);

      // Dua tanda tidak boleh berbagi atau bersarang di satu rentang.
      //
      // Ditambahkan 18 Sep 2026. Dua aturan yang berbeda kadang berimpit —
      // F1-002 mempersoalkan kata terakhir judul Menetapkan karena berbeda dari
      // judul pembuka, F1-012 mempersoalkan kata yang sama karena titik
      // penutupnya hilang; F1-004 mempersoalkan bunyi satu butir Menimbang,
      // F1-008 mempersoalkan karakter terakhir butir yang sama. Semuanya benar.
      // Tapi kalau dua-duanya digambar, Word menyarangkan content control yang
      // satu di dalam yang lain, dua komentar menumpuk di satu tempat, dan
      // menolak yang luar ikut menghapus tanda yang di dalam tanpa ada yang
      // memberi tahu panel.
      //
      // Pemenangnya ditentukan menurut URUTAN DOKUMEN, bukan urutan
      // penggambaran. Penggambaran sengaja berjalan dari bawah ke atas supaya
      // penyisipan usulan tidak menggeser rentang di bawahnya; kalau pemenang
      // ditentukan di situ juga, temuan yang lebih bawah dan lebih sempit selalu
      // mengalahkan temuan yang lebih atas dan lebih luas — padahal yang luas
      // justru yang alasannya lebih lengkap.
      //
      // Yang kalah TIDAK digambar dan dilaporkan lewat idTidakDitandai, supaya
      // kartunya di panel memuat alasannya sendiri. Temuannya tidak dibuang —
      // menyembunyikan temuan yang benar lebih buruk daripada satu tanda yang
      // tidak tergambar.
      const bolehDigambar = new Set<string>();
      const terpakai = new Map<number, [number, number][]>();
      for (const { t } of [...antrean].sort(
        (a, b) =>
          a.t.lokasi.paragraf_index - b.t.lokasi.paragraf_index ||
          a.t.lokasi.offset_mulai - b.t.lokasi.offset_mulai
      )) {
        const mulai = t.lokasi.offset_mulai;
        const akhir = mulai + t.lokasi.panjang;
        const sudah = terpakai.get(t.lokasi.paragraf_index) ?? [];
        if (sudah.some(([m, a]) => mulai < a && m < akhir)) continue;
        sudah.push([mulai, akhir]);
        terpakai.set(t.lokasi.paragraf_index, sudah);
        bolehDigambar.add(t.id);
      }

      // Komentar yang baru dipasang, disimpan supaya isinya bisa dibaca ulang
      // sesudah sync — lihat Tahap 4 di bawah.
      const komentarBaru: [Temuan, Word.Comment][] = [];

      for (const { t, i } of antrean) {
        if (!bolehDigambar.has(t.id)) {
          hasil.idTidakDitandai.push(t.id);
          continue;
        }

        const r = rentang[i] as Word.Range;
        const f = fonts[i] as Word.Font;

        formatAsliTemuan.set(t.nomor, {
          color: f.color ?? null,
          strikeThrough: f.strikeThrough ?? null,
          highlightColor: f.highlightColor ?? null,
        });

        const punyaUsulan =
          t.jenis_tanda === "penggantian" && !!t.usulan_rumusan;
        // Kesalahan yang perbaikannya MEMBUANG: dicoret merah, tanpa sisipan
        // hijau. Teksnya tetap tidak dihapus kode — yang menghapus penelaah.
        const usulHapus = t.jenis_tanda === "penghapusan";

        try {
          // Urutannya penting. Warna dulu, lalu sisipkan usulan di sebelahnya,
          // baru dibungkus content control. Kalau dibungkus lebih dulu,
          // penyisipan "After" bisa mendarat DI DALAM bungkusnya.
          if (punyaUsulan) {
            // Ada jawabannya: teks lama merah dan dicoret, penggantinya hijau.
            r.font.color = WARNA_SALAH;
            r.font.strikeThrough = true;

            const usulan = r.insertText(` ${t.usulan_rumusan}`, "After");
            usulan.font.color = WARNA_USULAN;
            usulan.font.strikeThrough = false;
            usulan.font.highlightColor = null as unknown as string;
            bungkusContentControl(usulan, `${TAG_USUL}${t.nomor}`, t.nomor);
            hasil.diusulkan++;
            hasil.dicoretMerah++;
          } else if (usulHapus) {
            // Diusulkan dibuang. Merah dan dicoret sama seperti penggantian,
            // tetapi TIDAK ADA yang disisipkan — memang tidak ada rumusan
            // pengganti yang masuk akal untuk definisi yang tidak terpakai.
            r.font.color = WARNA_SALAH;
            r.font.strikeThrough = true;
            hasil.dicoretMerah++;
          } else {
            // Tidak ada rumusan pengganti tunggal — ini peringatan, bukan usul
            // penghapusan. Blok kuning, warna hurufnya TIDAK disentuh: merah
            // membuat alat seolah menyuruh membuang teks itu.
            r.font.highlightColor = WARNA_CATATAN;
            hasil.diblokKuning++;
          }

          // Satu komentar per temuan. Tidak lebih.
          //
          // DIPASANG SEBELUM PEMBUNGKUSAN, dan itu disengaja. Alasannya sama
          // dengan yang sudah berlaku untuk penyisipan usulan hijau di atas:
          // `insertContentControl()` membungkus ulang rentangnya, dan apa pun
          // yang dikerjakan pada `r` sesudah itu bisa mendarat di tempat yang
          // bukan lagi rentang semula. Diduga inilah sebab balon komentar
          // kosong yang dilaporkan 25 Sep 2026.
          if (bisaKomentar) {
            komentarBaru.push([t, r.insertComment(susunIsiKomentar(t))]);
            hasil.dikomentari++;
          }

          bungkusContentControl(r, `${TAG_ASLI}${t.nomor}`, t.nomor);
        } catch (err) {
          console.warn(`Tanda T${t.nomor} gagal dipasang:`, err);
          hasil.idTidakDitandai.push(t.id);
        }
      }
      await context.sync();

      // --- Tahap 4: buktikan komentarnya benar-benar berisi ---------------
      //
      // Menulis lalu percaya sudah terjadi bukan pembuktian. Yang kosong
      // dihitung supaya panel bisa mengatakannya; kegagalan yang diam tidak
      // bisa dibedakan dari alat yang rusak.
      if (komentarBaru.length > 0) {
        try {
          komentarBaru.forEach(([, k]) => k.load("content"));
          await context.sync();
          for (const [t, k] of komentarBaru) {
            if ((k.content ?? "").trim() !== "") continue;
            hasil.komentarKosong++;
            console.warn(`Komentar T${t.nomor} terpasang tetapi kosong.`);
          }
        } catch (err) {
          // Gagal membaca ulang bukan alasan menggagalkan penandaan yang
          // sudah terlanjur benar. Cukup dicatat.
          console.warn("Gagal memeriksa isi komentar:", err);
        }
      }

      await kembalikanPelacakan(context, modeAwal);
    });
  } catch (err) {
    console.warn("Gagal menandai temuan di dokumen:", err);
  }

  return hasil;
}

/**
 * Membungkus rentang dengan content control bertag, penampilannya disembunyikan.
 *
 * Inilah satu-satunya cara add-in mengenali kembali tandanya sendiri: Word
 * tidak menyimpan apa pun tentang "usulan mesin". Kegagalan di sini tidak
 * menggagalkan penandaan — tandanya tetap terpasang, hanya lebih sulit dicabut
 * otomatis nanti.
 */
function bungkusContentControl(
  rentang: Word.Range,
  tag: string,
  nomor: number
): void {
  try {
    const cc = rentang.insertContentControl();
    cc.tag = tag;
    cc.title = `Drafter Analiser T${nomor}`;
    cc.appearance = "Hidden";
    cc.cannotDelete = false;
    cc.cannotEdit = false;
  } catch (err) {
    console.warn(`Content control ${tag} gagal dipasang:`, err);
  }
}

// ---------------------------------------------------------------------------
// Keputusan atas temuan
// ---------------------------------------------------------------------------

/**
 * Menolak sebuah temuan: usulan hijaunya dibuang, teks aslinya dipulihkan
 * persis seperti sebelum ditandai, komentarnya dihapus.
 *
 * Sesudah ini tidak boleh ada bekas apa pun di naskah.
 */
export async function tolakTemuan(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable()) return false;

  try {
    return await Word.run(async (context) => {
      const { modeAwal } = await matikanPelacakan(context);
      const body = context.document.body;

      const ccUsul = body.contentControls.getByTag(`${TAG_USUL}${temuan.nomor}`);
      const ccAsli = body.contentControls.getByTag(`${TAG_ASLI}${temuan.nomor}`);
      ccUsul.load("items");
      ccAsli.load("items");
      await context.sync();

      // Usulan hijau dibuang berikut isinya — keepContent = false.
      ccUsul.items.forEach((cc) => cc.delete(false));

      // Teks asli: kembalikan formatnya, lalu bungkusnya saja yang dilepas —
      // keepContent = true, supaya naskahnya tidak ikut terhapus.
      const asli = formatAsliTemuan.get(temuan.nomor);
      ccAsli.items.forEach((cc) => {
        // ContentControl.font, bukan getRange().font: yang pertama WordApi 1.1,
        // yang kedua 1.3. Seluruh penandaan alat ini sengaja dijaga di 1.1.
        const f = cc.font;
        f.color = asli?.color ?? WARNA_NETRAL;
        f.strikeThrough = asli?.strikeThrough ?? false;
        f.highlightColor = (asli?.highlightColor ??
          null) as unknown as string;
        cc.delete(true);
      });
      await context.sync();

      const adaTanda = ccUsul.items.length > 0 || ccAsli.items.length > 0;
      formatAsliTemuan.delete(temuan.nomor);

      await hapusKomentarTemuanDi(context, temuan);
      await kembalikanPelacakan(context, modeAwal);
      return adaTanda;
    });
  } catch (err) {
    console.warn(`Gagal menolak temuan T${temuan.nomor}:`, err);
    return false;
  }
}

/**
 * Menghapus komentar milik sebuah temuan, dicari lewat penanda (T{n}) di isinya.
 */
async function hapusKomentarTemuanDi(
  context: Word.RequestContext,
  temuan: Temuan
): Promise<boolean> {
  if (!checkApiSupport("1.4")) return false;
  try {
    const paragraphs = context.document.body.paragraphs;
    paragraphs.load("items");
    await context.sync();

    const p = paragraphs.items[temuan.lokasi.paragraf_index];
    if (!p) return false;

    // Sengaja mencari di SELURUH paragraf, bukan di rentang presisi: rentang
    // sempit berisiko meleset kalau posisinya bergeser sedikit, sedangkan
    // paragraf pasti memuat jangkar komentarnya.
    const komentar = p.getRange().getComments();
    komentar.load("items/content");
    await context.sync();

    const penanda = penandaKomentar(temuan);
    let adaYangDihapus = false;
    komentar.items.forEach((k) => {
      if (k.content && k.content.includes(penanda)) {
        k.delete();
        adaYangDihapus = true;
      }
    });

    if (adaYangDihapus) await context.sync();
    return adaYangDihapus;
  } catch (err) {
    console.warn("Gagal menghapus komentar temuan:", err);
    return false;
  }
}

/**
 * Membersihkan SELURUH tanda milik alat dari naskah — jalan keluar darurat
 * ketika daftar panel terlanjur kacau.
 *
 * Yang dihapus hanya yang bertag DA-* berikut komentar milik alat. Sorotan dan
 * warna milik penyusun sendiri tidak disentuh: sebagian penyusun memakai warna
 * untuk menandai ketentuan baru, dan menghapusnya berarti membuang informasi
 * milik mereka.
 */
export async function bersihkanSemuaTanda(): Promise<HasilPembersihan> {
  if (!isOfficeAvailable()) return { tanda: 0, komentar: 0 };

  const hasil: HasilPembersihan = { tanda: 0, komentar: 0 };

  try {
    await Word.run(async (context) => {
      const { modeAwal } = await matikanPelacakan(context);
      const kontrol = context.document.body.contentControls;
      // Format tiap rentang ikut dibaca. Tanpa itu pemulihan hanya bisa
      // menebak, dan menebak di sini berarti menimpa warna milik penyusun.
      kontrol.load(
        "items/tag,items/font/color,items/font/strikeThrough," +
          "items/font/highlightColor"
      );
      await context.sync();

      const usul = kontrol.items.filter((cc) => cc.tag?.startsWith(TAG_USUL));
      const asli = kontrol.items.filter((cc) => cc.tag?.startsWith(TAG_ASLI));

      usul.forEach((cc) => cc.delete(false));

      asli.forEach((cc) => {
        const f = cc.font;
        const tersimpan = formatAsliTemuan.get(nomorDariTag(cc.tag) ?? -1);

        if (tersimpan) {
          // Jalur normal: sesi yang sama, formatnya masih diingat. Pulihkan
          // persis seperti sebelum ditandai.
          f.color = tersimpan.color ?? WARNA_NETRAL;
          f.strikeThrough = tersimpan.strikeThrough ?? false;
          f.highlightColor = (tersimpan.highlightColor ??
            null) as unknown as string;
        } else {
          // Word sempat ditutup, formatnya tidak lagi diingat.
          //
          // DIPERBAIKI 18 Sep 2026. Dulu baris ini memaksa SEMUA warna jadi
          // hitam. Pada temuan berblok kuning alat tidak pernah menyentuh
          // warna hurufnya sama sekali, jadi memaksanya hitam berarti membuang
          // warna milik penyusun — sebagian penyusun mewarnai teks untuk
          // menandai ketentuan baru. Docstring fungsi ini menjanjikan
          // kebalikannya, dan janji itu yang sekarang ditepati.
          //
          // Yang dicabut hanya yang PERSIS sama dengan warna milik alat.
          // Warna lain dibiarkan apa adanya.
          if (samaDenganWarnaAlat(cc.font.color, WARNA_SALAH)) {
            f.color = WARNA_NETRAL;
            f.strikeThrough = false;
          }
          if (
            KUNING_TERBACA.includes(
              (cc.font.highlightColor ?? "").trim().toUpperCase()
            )
          ) {
            f.highlightColor = null as unknown as string;
          }
        }

        cc.delete(true);
      });
      await context.sync();

      hasil.tanda = usul.length + asli.length;
      formatAsliTemuan.clear();

      hasil.komentar = await hapusSemuaKomentarAlat(context);

      await kembalikanPelacakan(context, modeAwal);
    });
  } catch (err) {
    console.warn("Gagal membersihkan tanda:", err);
  }

  return hasil;
}

/**
 * Menghapus SELURUH komentar milik alat dari naskah.
 *
 * Ditambahkan 18 Sep 2026. Sebelumnya Bersihkan Daftar hanya mencabut content
 * control, komentarnya ditinggal. Itu membuat pengaman analisis-berulang bocor:
 * sesudah Bersihkan Daftar penelaah boleh menganalisis lagi, komentar lama
 * masih ada, dan komentar baru memakai nomor (T1), (T2) yang sama persis —
 * yaitu keadaan "18 komentar untuk 5 temuan" yang justru jadi alasan pengaman
 * itu dipasang.
 *
 * Yang dikenali sebagai milik alat: komentar yang isinya DIAKHIRI penanda
 * `(T<angka>)`. Penanda itu memang selalu di ujung baris kedua, dan mengikatnya
 * ke ujung membuat komentar penelaah yang kebetulan menyebut "(T3)" di tengah
 * kalimat tidak ikut terhapus. Jumlahnya dikembalikan supaya panel bisa
 * menyebutkannya — penelaah berhak tahu persis apa yang dihapus dari naskahnya.
 */
async function hapusSemuaKomentarAlat(
  context: Word.RequestContext
): Promise<number> {
  if (!checkApiSupport("1.4")) return 0;
  try {
    const komentar = context.document.body.getComments();
    komentar.load("items/content");
    await context.sync();

    const milikAlat = komentar.items.filter((k) =>
      /\(T\d+\)$/.test((k.content ?? "").trim())
    );
    milikAlat.forEach((k) => k.delete());
    if (milikAlat.length > 0) await context.sync();
    return milikAlat.length;
  } catch (err) {
    console.warn("Gagal menghapus komentar alat:", err);
    return 0;
  }
}

/**
 * Menavigasi dan menyorot posisi temuan di dalam dokumen Word.
 *
 * Memakai content control kalau ada — itu penunjuk paling tepat sesudah naskah
 * bergeser oleh penyisipan usulan. Kalau tidak ada, jatuh ke pencarian teks
 * dengan perhitungan kemunculan keberapa.
 */
/**
 * Ganti komentar sebuah temuan yang SUDAH terpasang, tanpa menyentuh tandanya.
 *
 * Dipakai ketika model menempelkan keberatan pada temuan Fase 1: temuannya
 * tetap di tempatnya dengan sorotan dan nomor yang sama, yang berubah cuma isi
 * komentarnya — kini bertambah baris "Catatan AI:".
 *
 * Jangkarnya content control bertag `DA-ASLI-{n}` yang dipasang saat menandai.
 * Kalau jangkarnya tidak ada (temuan tidak tertandai di naskah), fungsi ini
 * tidak melakukan apa-apa dan mengembalikan false — catatan AI-nya tetap
 * terbaca di kartu panel.
 */
export async function perbaruiKomentarTemuan(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable() || !checkApiSupport("1.4")) return false;

  try {
    return await Word.run(async (context) => {
      const cc = context.document.body.contentControls.getByTag(
        `${TAG_ASLI}${temuan.nomor}`
      );
      cc.load("items");
      await context.sync();
      if (cc.items.length === 0) return false;

      await hapusKomentarTemuanDi(context, temuan);

      cc.items[0].getRange().insertComment(susunIsiKomentar(temuan));
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal memperbarui komentar temuan:", err);
    return false;
  }
}

export async function selectFindingLocation(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable()) return false;

  try {
    return await Word.run(async (context) => {
      const body = context.document.body;
      const cc = body.contentControls.getByTag(`${TAG_ASLI}${temuan.nomor}`);
      cc.load("items");
      await context.sync();

      if (cc.items.length > 0) {
        cc.items[0].getRange().select();
        await context.sync();
        return true;
      }

      const paragraphs = body.paragraphs;
      paragraphs.load("items/text");
      await context.sync();

      const p = paragraphs.items[temuan.lokasi.paragraf_index];
      if (!p) return false;

      if (layakDicari(temuan)) {
        const { kunci, offset } = kunciTemuan(temuan);
        const cari = p.search(kunci, { matchCase: true });
        cari.load("items");
        await context.sync();

        if (cari.items.length > 0) {
          const n = ordinalKemunculan(p.text ?? "", kunci, offset);
          cari.items[Math.min(n, cari.items.length - 1)].select();
          await context.sync();
          return true;
        }
      }

      p.getRange().select();
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal memilih lokasi temuan:", err);
    return false;
  }
}
