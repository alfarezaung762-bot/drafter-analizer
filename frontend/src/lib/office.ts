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
 *   - Teks yang salah  : merah (+ dicoret bila ada usulan penggantinya)
 *   - Usulan penggantinya: hijau, disisipkan di sebelahnya
 *   - Satu komentar per temuan, tidak lebih
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
export async function readParagraphs(
  scope: "all" | "selection" = "all"
): Promise<ParagrafInput[]> {
  if (!isOfficeAvailable()) {
    throw new Error("Office.js tidak tersedia dalam lingkungan ini.");
  }

  return Word.run(async (context) => {
    const body = context.document.body.paragraphs;
    body.load("text");
    await context.sync();

    if (scope !== "selection") {
      return body.items.map((p, idx) => ({ index: idx, teks: p.text }));
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
        hasil.push({ index: idx, teks: p.text });
      }
    });
    return hasil;
  });
}

// ---------------------------------------------------------------------------
// Warna dan penanda
// ---------------------------------------------------------------------------

/** Merah tua — teks yang kurang tepat. Sama dengan "Dark Red" bawaan Word. */
const WARNA_SALAH = "#C00000";

/** Hijau tua — usulan rumusan pengganti. */
const WARNA_USULAN = "#00802B";

/** Hitam, dipakai memulihkan warna bila warna asli tidak terbaca. */
const WARNA_NETRAL = "#000000";

/** Awalan tag content control. Dipakai menemukan kembali tanda milik alat. */
const TAG_ASLI = "DA-ASLI-";
const TAG_USUL = "DA-USUL-";

/**
 * Format asli tiap rentang sebelum ditimpa, agar Tolak bisa memulihkannya.
 * Kunci = id temuan.
 *
 * Peta ini hanya hidup di memori tab selama panel terbuka. Kalau Word ditutup
 * sebelum temuan diputuskan, warna merah/hijaunya ikut tersimpan di berkas dan
 * add-in tidak lagi tahu warna aslinya — yang bisa dilakukan tinggal
 * mengembalikannya ke hitam. Ini keterbatasan yang sudah disepakati, bukan
 * kelalaian; penelaah wajib memeriksa ulang naskahnya.
 */
type FormatAsli = {
  color: string | null;
  strikeThrough: boolean | null;
  highlightColor: string | null;
};
const formatAsliTemuan = new Map<string, FormatAsli>();

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
 * Isi komentar Word untuk sebuah temuan — dua baris.
 *
 * Baris pertama ALASAN, bukan pengulangan apa yang sudah terlihat di naskah.
 * Baris kedua rujukan, ditutup nomor temuan.
 *
 * Nama produk sengaja TIDAK ditulis: ruang komentar sempit, dan nomor temuan
 * sudah cukup jadi penanda.
 */
function susunIsiKomentar(temuan: Temuan): string {
  const butir = temuan.rujukan.butir;
  const rujukanStr =
    butir && butir !== "..."
      ? `${temuan.rujukan.sumber} butir ${butir}`
      : `${temuan.rujukan.sumber} (butir belum diverifikasi)`;

  return (
    `${temuan.catatan}\n` +
    `${rujukanStr} — ${temuan.rujukan.pdf_url} ${penandaKomentar(temuan)}`
  );
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
  /** Jumlah temuan yang tandanya benar-benar terpasang di naskah. */
  ditandai: number;
  /** Jumlah usulan hijau yang ikut tersisip. */
  diusulkan: number;
  /** Jumlah komentar yang terpasang. */
  dikomentari: number;
  /**
   * Jumlah temuan yang letak persisnya TIDAK ketemu, jadi tidak ditandai sama
   * sekali. Wajib disampaikan: ada temuan yang tidak kelihatan di naskah.
   */
  tidakKetemu: number;
  /** Pelacakan perubahan berhasil dimatikan selama penandaan. */
  pelacakanMati: boolean;
};

const HASIL_KOSONG: HasilPenandaan = {
  ditandai: 0,
  diusulkan: 0,
  dikomentari: 0,
  tidakKetemu: 0,
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
 */
export async function tandaiSemuaTemuan(
  daftar: Temuan[]
): Promise<HasilPenandaan> {
  if (!isOfficeAvailable() || daftar.length === 0) {
    return { ...HASIL_KOSONG };
  }

  const bisaKomentar = checkApiSupport("1.4");
  const hasil: HasilPenandaan = { ...HASIL_KOSONG };

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

      hasil.tidakKetemu = daftar.length - antrean.length;

      for (const { t, i } of antrean) {
        const r = rentang[i] as Word.Range;
        const f = fonts[i] as Word.Font;

        formatAsliTemuan.set(t.id, {
          color: f.color ?? null,
          strikeThrough: f.strikeThrough ?? null,
          highlightColor: f.highlightColor ?? null,
        });

        const punyaUsulan =
          t.jenis_tanda === "penggantian" && !!t.usulan_rumusan;

        try {
          // Urutannya penting. Warna dulu, lalu sisipkan usulan di sebelahnya,
          // baru dibungkus content control. Kalau dibungkus lebih dulu,
          // penyisipan "After" bisa mendarat DI DALAM bungkusnya.
          r.font.color = WARNA_SALAH;
          // Dicoret HANYA kalau memang ada penggantinya. Temuan tanpa usulan
          // bukan usul penghapusan — mencoretnya berarti berbohong soal apa
          // yang dimaksud alat.
          if (punyaUsulan) r.font.strikeThrough = true;

          if (punyaUsulan) {
            const usulan = r.insertText(` ${t.usulan_rumusan}`, "After");
            usulan.font.color = WARNA_USULAN;
            usulan.font.strikeThrough = false;
            usulan.font.highlightColor = null as unknown as string;
            bungkusContentControl(usulan, `${TAG_USUL}${t.nomor}`, t.nomor);
            hasil.diusulkan++;
          }

          bungkusContentControl(r, `${TAG_ASLI}${t.nomor}`, t.nomor);
          hasil.ditandai++;

          // Satu komentar per temuan. Tidak lebih.
          if (bisaKomentar) {
            r.insertComment(susunIsiKomentar(t));
            hasil.dikomentari++;
          }
        } catch (err) {
          console.warn(`Tanda T${t.nomor} gagal dipasang:`, err);
        }
      }
      await context.sync();

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
      const asli = formatAsliTemuan.get(temuan.id);
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
      formatAsliTemuan.delete(temuan.id);

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
 * Yang dihapus hanya yang bertag DA-*. Sorotan dan warna milik penyusun
 * sendiri tidak disentuh: sebagian penyusun memakai warna untuk menandai
 * ketentuan baru, dan menghapusnya berarti membuang informasi milik mereka.
 */
export async function bersihkanSemuaTanda(): Promise<number> {
  if (!isOfficeAvailable()) return 0;

  try {
    return await Word.run(async (context) => {
      const { modeAwal } = await matikanPelacakan(context);
      const kontrol = context.document.body.contentControls;
      kontrol.load("items/tag");
      await context.sync();

      const usul = kontrol.items.filter((cc) => cc.tag?.startsWith(TAG_USUL));
      const asli = kontrol.items.filter((cc) => cc.tag?.startsWith(TAG_ASLI));

      usul.forEach((cc) => cc.delete(false));
      asli.forEach((cc) => {
        const f = cc.font;
        f.color = WARNA_NETRAL;
        f.strikeThrough = false;
        f.highlightColor = null as unknown as string;
        cc.delete(true);
      });
      await context.sync();

      formatAsliTemuan.clear();
      await kembalikanPelacakan(context, modeAwal);
      return usul.length + asli.length;
    });
  } catch (err) {
    console.warn("Gagal membersihkan tanda:", err);
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
