/**
 * Kumpulan fungsi wrapper Office.js untuk Drafter Analiser.
 *
 * Semua pemanggilan Office.js dikumpulkan di file ini.
 * Sumber kebenaran: docs/panduan-officejs.md & frontend/node_modules/@types/office-js/index.d.ts
 */

import { ParagrafInput, Temuan } from "./types";

/**
 * Cek apakah Office.js runtime tersedia.
 */
export function isOfficeAvailable(): boolean {
  return typeof Office !== "undefined" && typeof Word !== "undefined";
}

/**
 * Cek dukungan requirement set WordApi tertentu secara runtime.
 */
export function checkApiSupport(version: string): boolean {
  if (!isOfficeAvailable() || !Office.context?.requirements) {
    return false;
  }
  try {
    return Office.context.requirements.isSetSupported("WordApi", version);
  } catch {
    return false;
  }
}

/**
 * Membaca paragraf dokumen (seluruh dokumen atau teks terpilih).
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
    // dokumen, bukan dihitung ulang dari nol di dalam seleksi.
    //
    // Sebelumnya paragraf diambil langsung dari getSelection().paragraphs,
    // sehingga paragraf pertama seleksi bernomor 0. Padahal sorotan dan
    // komentar dicari lewat body.paragraphs — nomor 0 di situ berarti paragraf
    // pertama dokumen. Akibatnya, memblok bagian tengah naskah lalu menganalisis
    // membuat tanda mendarat di paragraf yang sama sekali lain.
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

/**
 * Warna asli tiap paragraf sebelum ditimpa font.highlightColor, agar bisa
 * dipulihkan saat temuannya diterima atau ditolak. Kunci = id temuan.
 */
const warnaAsliTemuan = new Map<string, string | null>();

/**
 * Warna sorotan menurut tingkat keparahan.
 *
 * Office untuk Windows Desktop HANYA menerima 15 warna bawaan; nilai lain
 * dibulatkan ke warna terdekat. Karena itu dipakai namanya langsung, bukan
 * hex — supaya hasil di layar persis seperti yang dimaksud.
 *
 * Hijau sengaja dihindari untuk tingkat mana pun: dalam konteks telaah, hijau
 * terbaca sebagai "sudah benar" — kebalikan dari maksud sebuah temuan.
 */
function warnaKeparahan(tingkat: string): string {
  if (tingkat === "tinggi") return "Red";
  if (tingkat === "sedang") return "Yellow";
  return "Turquoise";
}

/** Panjang aman untuk Word.search() — lihat catatan di cariRangeTemuan(). */
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

/** Isi komentar Word untuk sebuah temuan. */
function susunIsiKomentar(temuan: Temuan): string {
  const butir = temuan.rujukan.butir;
  const rujukanStr =
    butir && butir !== "..."
      ? `${temuan.rujukan.sumber} butir ${butir}`
      : `${temuan.rujukan.sumber} (rujukan belum diverifikasi)`;

  // aturan_id ikut dicantumkan supaya komentar ini bisa ditemukan kembali dan
  // dihapus saat temuannya ditolak. Tanpa penanda itu, komentar yang sudah
  // masuk dokumen tidak bisa dibedakan satu sama lain.
  return (
    `[Drafter Analiser — ${temuan.tingkat_keparahan.toUpperCase()} · ${temuan.aturan_id}]\n` +
    `${temuan.catatan}\n\n` +
    `Rujukan: ${rujukanStr}\n` +
    `${temuan.rujukan.pdf_url}`
  );
}

/** Penanda pengenal di dalam isi komentar, dipakai saat mencari untuk dihapus. */
function penandaKomentar(temuan: Temuan): string {
  return `· ${temuan.aturan_id}]`;
}

/**
 * Menandai SELURUH temuan sekaligus: sorotan sementara + komentar, dalam satu
 * kali Word.run.
 *
 * Dipanggil tepat sesudah analisis, sehingga penelaah langsung melihat bagian
 * bermasalah terblok warna dan bisa mengklik teksnya untuk membaca komentar
 * lewat panel komentar bawaan Word — tanpa menekan Terima lebih dulu.
 *
 * Komentar yang ditolak dihapus kembali lewat hapusKomentarTemuan().
 *
 * Sengaja dibuat satu Word.run dengan tiga sinkronisasi, bukan satu panggilan
 * per temuan: pada dokumen dengan puluhan temuan, cara lama berarti puluhan
 * perjalanan bolak-balik ke Word.
 */
export async function tandaiSemuaTemuan(
  daftar: Temuan[]
): Promise<{ disorot: number; dikomentari: number; memakaiWarnaFont: boolean }> {
  if (!isOfficeAvailable() || daftar.length === 0) {
    return { disorot: 0, dikomentari: 0, memakaiWarnaFont: false };
  }

  const bisaSorot = checkApiSupport("1.8");
  const bisaKomentar = checkApiSupport("1.4");
  if (!bisaSorot && !bisaKomentar) {
    return { disorot: 0, dikomentari: 0, memakaiWarnaFont: false };
  }

  try {
    return await Word.run(async (context) => {
      const body = context.document.body.paragraphs;
      body.load("items");
      await context.sync();

      // Antre semua pencarian presisi dulu, baru satu kali sinkronisasi.
      const pencarian = daftar.map((t) => {
        const p = body.items[t.lokasi.paragraf_index];
        if (!p || !layakDicari(t)) return null;
        const hasil = p.search(t.lokasi.teks_asli!.trim(), { matchCase: false });
        hasil.load("items");
        return hasil;
      });
      await context.sync();

      // Range sasaran tiap temuan, dipakai dua tahap berikutnya.
      const sasaran = daftar.map((t, i) => {
        const p = body.items[t.lokasi.paragraf_index];
        if (!p) return null;
        const hasil = pencarian[i];
        return hasil && hasil.items.length > 0 ? hasil.items[0] : p.getRange();
      });

      // Tahap 1: komentar.
      let dikomentari = 0;
      if (bisaKomentar) {
        daftar.forEach((t, i) => {
          const range = sasaran[i];
          if (!range) return;
          range.insertComment(susunIsiKomentar(t));
          dikomentari++;
        });
        await context.sync();
      }

      // Tahap 2: sorotan — SESUDAH komentar tersinkronisasi, bukan bersamaan.
      // Menyisipkan komentar menyentuh rentang yang sama, dan bila keduanya
      // diantre dalam satu sinkronisasi, sorotannya bisa tertimpa. Dipisah juga
      // supaya kegagalan sorotan tidak ikut membatalkan komentar yang sudah
      // berhasil — keduanya sekarang berdiri sendiri.
      let disorot = 0;
      if (bisaSorot) {
        try {
          sasaran.forEach((range) => {
            if (!range) return;
            range.highlight();
            disorot++;
          });
          await context.sync();
        } catch (err) {
          console.warn(
            "Range.highlight() ditolak Word; komentarnya tetap ada. Penyebab:",
            err
          );
          disorot = 0;
        }
      }

      // Tahap 3 — cadangan: kalau sorotan sementara tidak menghasilkan apa pun,
      // pakai font.highlightColor (WordApi 1.1, jalan di semua lisensi).
      //
      // Ini SATU-SATUNYA bagian alat yang mengubah format dokumen. Dipakai
      // hanya bila tidak ada jalan lain, warnanya dikembalikan saat temuan
      // diterima atau ditolak, dan warna asli paragraf dicatat dulu supaya
      // sorotan milik penyusun tidak ikut terhapus. Teks naskahnya sendiri
      // tetap tidak tersentuh.
      let memakaiWarnaFont = false;
      if (disorot === 0 && sasaran.some((r) => r !== null)) {
        try {
          const fonts = sasaran.map((r) => (r ? r.font : null));
          fonts.forEach((f) => f?.load("highlightColor"));
          await context.sync();

          daftar.forEach((t, i) => {
            const f = fonts[i];
            if (!f) return;
            warnaAsliTemuan.set(t.id, f.highlightColor ?? null);
            f.highlightColor = warnaKeparahan(t.tingkat_keparahan);
            disorot++;
          });
          await context.sync();
          memakaiWarnaFont = true;
        } catch (err) {
          console.warn("Pewarnaan cadangan juga gagal:", err);
          disorot = 0;
        }
      }

      return { disorot, dikomentari, memakaiWarnaFont };
    });
  } catch (err) {
    console.warn("Gagal menandai temuan di dokumen:", err);
    return { disorot: 0, dikomentari: 0, memakaiWarnaFont: false };
  }
}

/**
 * Menghapus komentar milik sebuah temuan — dipakai saat temuan ditolak, supaya
 * tidak ada jejak apa pun yang tertinggal di dokumen.
 */
export async function hapusKomentarTemuan(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable() || !checkApiSupport("1.4")) {
    return false;
  }
  try {
    return await Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load("items");
      await context.sync();

      const p = paragraphs.items[temuan.lokasi.paragraf_index];
      if (!p) return false;

      // Sengaja mencari di SELURUH paragraf, bukan di rentang presisi tempat
      // komentar tadi dipasang. Rentang sempit berisiko meleset kalau posisinya
      // bergeser sedikit; paragraf pasti memuat jangkar komentarnya.
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
    });
  } catch (err) {
    console.warn("Gagal menghapus komentar temuan:", err);
    return false;
  }
}

/**
 * Menavigasi dan menyorot posisi temuan di dalam dokumen Word.
 */
export async function selectFindingLocation(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable()) {
    return false;
  }

  try {
    return await Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load("items");
      await context.sync();

      if (temuan.lokasi.paragraf_index >= paragraphs.items.length) {
        return false;
      }

      const p = paragraphs.items[temuan.lokasi.paragraf_index];

      // Jika teks asli tersedia, coba sorot bagian teks yang spesifik
      if (temuan.lokasi.teks_asli && temuan.lokasi.teks_asli.trim().length > 0) {
        const searchResults = p.search(temuan.lokasi.teks_asli.trim(), {
          matchCase: false,
        });
        searchResults.load("items");
        await context.sync();

        if (searchResults.items.length > 0) {
          searchResults.items[0].select();
          await context.sync();
          return true;
        }
      }

      // Fallback: pilih seluruh paragraf
      p.getRange().select();
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal memilih lokasi temuan:", err);
    return false;
  }
}

/**
 * Lapis 2: Menyisipkan komentar permanen Word (WordApi 1.4).
 *
 * Catatan penting: usulan_rumusan sengaja TIDAK disertakan dalam komentar
 * agar penelaah menyunting sendiri (sesuai dokumen kontrak & rancangan).
 */
export async function insertPermanentComment(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable() || !checkApiSupport("1.4")) {
    console.warn("WordApi 1.4 tidak didukung.");
    return false;
  }

  try {
    return await Word.run(async (context) => {
      // Memakai pencari range bersama — di dalamnya sudah ada pengaman terhadap
      // teks yang terlalu panjang atau memuat karakter khusus, yang sebelumnya
      // membuat sebagian temuan "diterima" tanpa pernah menghasilkan komentar.
      const targetRange = await cariRangeTemuan(context, temuan);
      if (!targetRange) {
        return false;
      }

      // Isi komentar disusun di satu tempat (susunIsiKomentar) supaya penanda
      // pengenalnya selalu sama — itu yang dipakai hapusKomentarTemuan() untuk
      // menemukan kembali komentar yang harus dihapus saat temuan ditolak.
      targetRange.insertComment(susunIsiKomentar(temuan));
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal menyisipkan komentar permanen:", err);
    return false;
  }
}

/**
 * Penanda bahwa Critique/insertAnnotations ditolak Word di lingkungan ini.
 *
 * Pemeriksaan isSetSupported("WordApi", "1.7") TIDAK cukup: requirement set-nya
 * bisa tersedia sementara insertAnnotations tetap melempar NotImplemented,
 * karena fitur Annotation mensyaratkan langganan Microsoft 365 — bukan sekadar
 * versi Word tertentu. Lisensi beli-putus (mis. Office LTSC 2024) melaporkan
 * 1.7/1.8 sebagai didukung namun menolak panggilannya.
 *
 * Tanpa penanda ini, tiap temuan memicu satu perjalanan bolak-balik ke Word
 * yang sudah pasti gagal. Sekali gagal, berhenti mencoba sampai halaman dimuat
 * ulang.
 */
let critiqueDitolakHost = false;

/** Apakah Critique sudah terbukti ditolak host di sesi ini. */
export function critiqueTersedia(): boolean {
  return !critiqueDitolakHost;
}

/**
 * Mencari range yang tepat untuk sebuah temuan di dalam dokumen.
 * Dipakai bersama oleh sorotan, komentar, dan navigasi.
 */
async function cariRangeTemuan(
  context: Word.RequestContext,
  temuan: Temuan
): Promise<Word.Range | null> {
  const paragraphs = context.document.body.paragraphs;
  paragraphs.load("items");
  await context.sync();

  if (temuan.lokasi.paragraf_index >= paragraphs.items.length) {
    return null;
  }

  const p = paragraphs.items[temuan.lokasi.paragraf_index];
  const teks = temuan.lokasi.teks_asli?.trim();

  // Word.search() mewarisi batasan Find bawaan Word: teks pencarian yang terlalu
  // panjang ditolak, dan sebagian karakter (^, *, ?, kurung siku) diperlakukan
  // khusus. Butir Menimbang di rancangan nyata mudah melewati 255 karakter —
  // contoh: butir "c. bahwa berdasarkan pertimbangan..." pada RPMK Wasdal
  // panjangnya sekitar 270 karakter. Kalau search() melempar, seluruh
  // pemanggilnya gagal dan komentar tidak jadi disisipkan.
  //
  // Karena itu pencarian presisi hanya dicoba untuk potongan pendek dan bersih.
  // Untuk sisanya, seluruh paragraf dipakai sebagai sasaran — komentarnya tetap
  // menempel di tempat yang benar, hanya cakupannya seluas paragraf.
  if (teks && layakDicari(temuan)) {
    try {
      const hasil = p.search(teks, { matchCase: false });
      hasil.load("items");
      await context.sync();
      if (hasil.items.length > 0) {
        return hasil.items[0];
      }
    } catch {
      // Pencarian gagal bukan alasan membatalkan — jatuh ke paragraf penuh.
    }
  }

  return p.getRange();
}

/**
 * Lapis 1 pengganti: sorotan sementara (WordApi 1.8).
 *
 * Range.highlight() menyoroti teks TANPA mengubah isi dokumen — berbeda dari
 * font.highlightColor yang permanen dan karenanya dilarang di proyek ini.
 * Dipakai saat Critique tidak tersedia.
 *
 * Batas yang perlu diketahui: highlight() tidak menerima parameter warna, jadi
 * seluruh temuan tersorot dengan satu gaya yang sama. Pewarnaan menurut tingkat
 * keparahan hanya mungkin lewat Critique.colorScheme, yang butuh langganan.
 */
export async function sorotSementara(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable() || !checkApiSupport("1.8")) {
    return false;
  }
  try {
    return await Word.run(async (context) => {
      const range = await cariRangeTemuan(context, temuan);
      if (!range) return false;
      range.highlight();
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal menyorot sementara:", err);
    return false;
  }
}

/** Menghapus sorotan sementara pada lokasi temuan (WordApi 1.8). */
export async function hapusSorotan(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable()) {
    return false;
  }
  try {
    return await Word.run(async (context) => {
      const range = await cariRangeTemuan(context, temuan);
      if (!range) return false;

      if (checkApiSupport("1.8")) {
        try {
          range.removeHighlight();
        } catch {
          // Tidak apa-apa — mungkin memang tidak ada sorotan sementara.
        }
      }

      // Kalau tadi terpaksa memakai font.highlightColor, kembalikan ke warna
      // ASLI paragraf itu, bukan sekadar dikosongkan. Sebagian penyusun
      // memakai sorotan sendiri untuk menandai ketentuan baru; mengosongkannya
      // begitu saja berarti menghapus informasi milik mereka.
      if (warnaAsliTemuan.has(temuan.id)) {
        const asli = warnaAsliTemuan.get(temuan.id) ?? null;
        range.font.highlightColor = asli as unknown as string;
        warnaAsliTemuan.delete(temuan.id);
      }

      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal menghapus sorotan:", err);
    return false;
  }
}

/**
 * Menandai temuan di dokumen: coba Critique dulu, jatuh ke sorotan sementara.
 * Inilah yang dipanggil task pane, bukan salah satunya langsung.
 */
export async function tandaiTemuan(temuan: Temuan): Promise<"critique" | "sorotan" | "gagal"> {
  if (critiqueTersedia()) {
    const ok = await insertCritiqueAnnotation(temuan);
    if (ok) return "critique";
  }
  const ok = await sorotSementara(temuan);
  return ok ? "sorotan" : "gagal";
}

/**
 * Lapis 1: Menyisipkan sorotan / Critique Annotation (WordApi 1.7/1.8).
 *
 * Warna sesuai tingkat keparahan:
 * - tinggi: Red
 * - sedang: Berry
 * - rendah: Lavender
 * (Green tidak dipakai)
 */
export async function insertCritiqueAnnotation(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable() || !checkApiSupport("1.7") || critiqueDitolakHost) {
    return false;
  }

  try {
    return await Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load("items");
      await context.sync();

      if (temuan.lokasi.paragraf_index >= paragraphs.items.length) {
        return false;
      }

      const p = paragraphs.items[temuan.lokasi.paragraf_index];

      let color: "Red" | "Berry" | "Lavender" = "Lavender";
      if (temuan.tingkat_keparahan === "tinggi") {
        color = "Red";
      } else if (temuan.tingkat_keparahan === "sedang") {
        color = "Berry";
      }

      const start = Math.max(0, temuan.lokasi.offset_mulai);
      const length = temuan.lokasi.panjang > 0 ? temuan.lokasi.panjang : 1;

      const critique: Word.Critique = {
        colorScheme: color,
        start,
        length,
      };

      p.insertAnnotations({
        critiques: [critique],
      });

      await context.sync();
      return true;
    });
  } catch (err) {
    // NotImplemented = fitur Annotation dikunci lisensi, bukan kesalahan sesaat.
    // Tandai sekali, lalu berhenti mencoba untuk seluruh temuan berikutnya.
    const kode = (err as { code?: string })?.code;
    if (kode === "NotImplemented") {
      critiqueDitolakHost = true;
      console.info(
        "Critique tidak didukung Word di sini (fitur Annotation mensyaratkan " +
          "langganan Microsoft 365). Beralih ke sorotan sementara."
      );
    } else {
      console.warn("Gagal menyisipkan critique annotation:", err);
    }
    return false;
  }
}
