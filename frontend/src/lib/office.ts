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

import { KerangkaTabel, NaskahTerbaca, ParagrafInput, Temuan } from "./types";

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

// ---------------------------------------------------------------------------
// Membaca naskah
// ---------------------------------------------------------------------------

/**
 * Tabel tingkat teratas yang barisnya lebih dari ini TIDAK dibaca per
 * paragraf — cukup kerangkanya. PMK 108/2024 memuat 228 ribu baris tabel (609
 * ribu paragraf); membacanya paragraf demi paragraf membuat Word macet.
 * Ditetapkan penelaah 29 Sep 2026.
 *
 * WAJIB SAMA dengan BATAS_BARIS_RAKSASA dan BARIS_CONTOH di
 * backend/tools/baca_docx.py — alat uji meniru panel.
 */
const BATAS_BARIS_RAKSASA = 1000;
const BARIS_CONTOH = 5;

interface Potongan {
  /**
   * Paragraf yang dibaca, per potongan naskah di antara tabel raksasa. null
   * untuk potongan kosong (tabel raksasa di awal/akhir naskah, atau dua tabel
   * raksasa berdempetan).
   */
  bagian: (Word.ParagraphCollection | null)[];
  /** Tabel raksasa, urut dokumen — satu di antara tiap dua potongan. */
  raksasa: Word.Table[];
}

/**
 * Potongan naskah yang dibaca per paragraf.
 *
 * Tanpa tabel raksasa: seluruh badan dokumen, satu potongan — persis seperti
 * sebelum fitur ini ada. Dengan tabel raksasa: potongan-potongan DI ANTARA
 * tabel itu, dicari lewat paragraf tepat sebelum dan sesudah tiap tabel.
 *
 * Dipanggil ulang di tiap Word.run pembacaan. Navigasinya pasti, jadi
 * potongannya sama di tiap putaran selama naskahnya tidak disunting.
 * Seluruh API-nya WordApi 1.3; tanpa 1.3 naskah dibaca utuh seperti dulu.
 */
async function susunPotongan(context: Word.RequestContext): Promise<Potongan> {
  const body = context.document.body;
  if (!checkApiSupport("1.3")) return { bagian: [body.paragraphs], raksasa: [] };

  const tabel = body.tables;
  tabel.load("items/rowCount,items/nestingLevel");
  await context.sync();
  const raksasa = tabel.items.filter(
    (t) => t.nestingLevel === 1 && t.rowCount > BATAS_BARIS_RAKSASA
  );
  if (raksasa.length === 0) return { bagian: [body.paragraphs], raksasa };

  const batas = raksasa.map((t) => {
    const isi = t.getRange("Whole").paragraphs;
    return {
      sebelum: isi.getFirst().getPreviousOrNullObject(),
      sesudah: isi.getLast().getNextOrNullObject(),
    };
  });
  batas.forEach((b) => {
    b.sebelum.load("isNullObject");
    b.sesudah.load("isNullObject");
  });
  await context.sync();

  const bagian: (Word.ParagraphCollection | null)[] = [];
  bagian.push(
    batas[0].sebelum.isNullObject
      ? null
      : body.getRange("Start").expandTo(batas[0].sebelum.getRange("Whole")).paragraphs
  );
  for (let k = 1; k < batas.length; k++) {
    const dari = batas[k - 1].sesudah;
    const sampai = batas[k].sebelum;
    bagian.push(
      dari.isNullObject || sampai.isNullObject
        ? null
        : dari.getRange("Whole").expandTo(sampai.getRange("Whole")).paragraphs
    );
  }
  const terakhir = batas[batas.length - 1].sesudah;
  bagian.push(
    terakhir.isNullObject
      ? null
      : terakhir.getRange("Whole").expandTo(body.getRange("End")).paragraphs
  );
  return { bagian, raksasa };
}

/** Isi pembaca tambahan dipakai hanya kalau panjangnya cocok dengan potongannya. */
function selaras<T>(isi: T[] | undefined, panjang: number): T[] | undefined {
  return isi && isi.length === panjang ? isi : undefined;
}

type Penanda = { penanda: string; tingkat: number };

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
async function bacaPenanda(): Promise<Penanda[][]> {
  if (!checkApiSupport("1.3")) return [];
  try {
    return await Word.run(async (context) => {
      const { bagian } = await susunPotongan(context);
      bagian.forEach((b) => b?.load("items/tableNestingLevel"));
      await context.sync();

      const butir = bagian.map((b) => (b ? b.items.map((p) => p.listItemOrNullObject) : []));
      butir.flat().forEach((x) => x.load("isNullObject,listString,level"));
      await context.sync();

      return butir.map((isi) =>
        isi.map((b) =>
          b.isNullObject
            ? { penanda: "", tingkat: -1 }
            : { penanda: b.listString ?? "", tingkat: b.level ?? -1 }
        )
      );
    });
  } catch (err) {
    console.warn("Nomor otomatis Word tidak terbaca; analisis memakai teks apa adanya.", err);
    return [];
  }
}

type Letak = { tabel: number; baris: number; sel: number };
const TANPA_LETAK: Letak = { tabel: -1, baris: -1, sel: -1 };

/**
 * Letak tiap paragraf di tabel — nomor tabel, baris, sel (bug 7 dan 11).
 *
 * Tabel tidak selalu berarti data: PMK 119 menulis batang tubuhnya di tabel
 * tata letak, nomor "1." di satu sel dan teksnya di sel sebelahnya. Tanpa
 * letak ini parser tidak tahu keduanya satu butir, dan seluruh definisi
 * Pasal 1 tidak pernah sampai ke model.
 *
 * Word tidak memberi nomor tabel, jadi nomornya diturunkan dari urutan: tabel
 * baru dimulai tiap kali tingkat tabel naik, atau nomor barisnya mundur di
 * tingkat yang sama. Tabel raksasa ikut mendapat nomor di tempatnya.
 * Urutannya sama dengan alat uji (backend/tools/baca_docx.py).
 *
 * Gagal membaca bukan alasan menggagalkan analisis — hasilnya null, dan naskah
 * dibaca tanpa letak seperti sebelum fitur ini ada.
 */
async function bacaLetak(): Promise<{ letak: Letak[][]; idRaksasa: number[] } | null> {
  if (!checkApiSupport("1.3")) return null;
  try {
    return await Word.run(async (context) => {
      const { bagian, raksasa } = await susunPotongan(context);
      bagian.forEach((b) => b?.load("items/tableNestingLevel"));
      await context.sync();

      const sel = bagian.map((b) =>
        b ? b.items.map((p) => (p.tableNestingLevel > 0 ? p.parentTableCellOrNullObject : null)) : []
      );
      sel.flat().forEach((c) => c?.load("isNullObject,rowIndex,cellIndex"));
      await context.sync();

      let tabelKe = -1;
      const idRaksasa: number[] = [];
      const letak: Letak[][] = bagian.map((b, k) => {
        const tumpuk: { id: number; baris: number }[] = [];
        const hasil = (b ? b.items : []).map((p, j) => {
          const tingkat = p.tableNestingLevel;
          if (!tingkat) {
            tumpuk.length = 0;
            return TANPA_LETAK;
          }
          const c = sel[k][j];
          const baris = c && !c.isNullObject ? c.rowIndex : -1;
          const kolom = c && !c.isNullObject ? c.cellIndex : -1;
          while (tumpuk.length > tingkat) tumpuk.pop();
          while (tumpuk.length < tingkat) tumpuk.push({ id: ++tabelKe, baris: -1 });
          const atas = tumpuk[tingkat - 1];
          // Nomor baris mundur di tingkat yang sama: tabel lain yang berdempetan.
          if (baris < atas.baris) atas.id = ++tabelKe;
          atas.baris = baris;
          return { tabel: atas.id, baris, sel: kolom };
        });
        if (k < raksasa.length) idRaksasa.push(++tabelKe);
        return hasil;
      });
      return { letak, idRaksasa };
    });
  } catch (err) {
    console.warn("Letak tabel tidak terbaca; naskah dibaca tanpa letak tabel.", err);
    return null;
  }
}

/**
 * Jumlah gambar sebaris tiap paragraf (WordApi 1.1). Isinya tidak terbaca
 * model, dan bahan menyebutnya terang-terangan — model tidak boleh mengira
 * tidak ada apa-apa di sana. Gagal membaca berarti daftar kosong.
 */
async function bacaGambar(): Promise<number[][]> {
  try {
    return await Word.run(async (context) => {
      const { bagian } = await susunPotongan(context);
      bagian.forEach((b) => b?.load("items/alignment"));
      await context.sync();

      const koleksi = bagian.map((b) =>
        b
          ? b.items.map((p) => {
              const c = p.inlinePictures;
              c.load("items/width");
              return c;
            })
          : []
      );
      await context.sync();
      return koleksi.map((isi) => isi.map((c) => c.items.length));
    });
  } catch (err) {
    console.warn("Gambar sebaris tidak terbaca.", err);
    return [];
  }
}

/**
 * Membaca naskah: paragrafnya, dan kerangka tabel yang terlalu besar dibaca.
 *
 * Naskah biasa dibaca utuh seperti sebelumnya, kini dengan letak tabel dan
 * jumlah gambar tiap paragraf. Naskah bertabel raksasa dibaca per potongan di
 * antara tabel itu; paragraf SESUDAH tabel raksasa pertama bernomor urutan
 * baca, bukan nomor paragraf Word (`letak_pasti: false`) — panel tidak
 * membaca isi tabelnya, jadi tidak bisa menghitung paragraf di dalamnya.
 * Temuan di paragraf begitu dilaporkan di panel tetapi tidak pernah ditandai.
 */
export async function bacaNaskah(
  scope: "all" | "selection" = "all"
): Promise<NaskahTerbaca> {
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
  const penanda = await bacaPenanda();
  const letak = await bacaLetak();
  const gambar = await bacaGambar();

  return Word.run(async (context) => {
    const { bagian, raksasa } = await susunPotongan(context);
    if (scope === "selection" && raksasa.length > 0) {
      throw new Error(
        "Naskah ini memuat tabel lebih dari 1.000 baris, dan cakupan Bagian " +
          "Terpilih belum mendukungnya. Pakai Seluruh Naskah."
      );
    }
    bagian.forEach((b) => b?.load("items/text"));
    const contoh = raksasa.map((t) => {
      const baris = [t.rows.getFirst()];
      for (let i = 1; i < BARIS_CONTOH; i++) baris.push(baris[i - 1].getNextOrNullObject());
      baris.forEach((r) => r.load("values,cellCount"));
      return baris;
    });
    await context.sync();

    // Mode "Bagian Terpilih": nomor paragraf TETAP memakai penomoran seluruh
    // dokumen, bukan dihitung ulang dari nol di dalam seleksi. Sorotan dan
    // komentar dicari lewat body.paragraphs — nomor 0 di situ berarti paragraf
    // pertama dokumen, jadi penomoran ulang membuat tanda mendarat di paragraf
    // yang sama sekali lain.
    let terpilih: boolean[] | null = null;
    if (scope === "selection" && bagian[0]) {
      const seleksi = context.document.getSelection();
      const irisan = bagian[0].items.map((p) =>
        p.getRange().intersectWithOrNullObject(seleksi)
      );
      irisan.forEach((r) => r.load("isNullObject"));
      await context.sync();
      terpilih = irisan.map((r) => !r.isNullObject);
    }

    const paragraf: ParagrafInput[] = [];
    const tabel_raksasa: KerangkaTabel[] = [];
    let urut = 0;
    bagian.forEach((b, k) => {
      const items = b ? b.items : [];
      const pen = selaras(penanda[k], items.length);
      const let_ = selaras(letak?.letak[k], items.length);
      const gam = selaras(gambar[k], items.length);
      items.forEach((p, j) => {
        const l = let_?.[j] ?? TANPA_LETAK;
        const isi: ParagrafInput = {
          index: urut,
          teks: p.text,
          penanda: pen?.[j]?.penanda ?? "",
          tingkat: pen?.[j]?.tingkat ?? -1,
          tabel: l.tabel,
          baris: l.baris,
          sel: l.sel,
          gambar: gam?.[j] ?? 0,
          letak_pasti: k === 0,
        };
        if (!terpilih || terpilih[j]) paragraf.push(isi);
        urut++;
      });
      if (k < raksasa.length) {
        const baris = contoh[k];
        tabel_raksasa.push({
          tabel: letak?.idRaksasa[k] ?? k,
          sesudah_paragraf: urut - 1,
          jumlah_baris: raksasa[k].rowCount,
          jumlah_kolom: Math.max(0, ...baris.map((r) => r.cellCount ?? 0)),
          contoh: baris.map((r) => (r.values?.[0] ?? []).map((v) => String(v))),
        });
      }
    });
    return { paragraf, tabel_raksasa };
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
 * Sejak 27 Sep 2026 peta ini ikut tersimpan di dalam berkas bersama daftar
 * temuannya (`simpanDaftarDiNaskah`), jadi Tolak sesudah berkas dibuka ulang
 * tetap memulihkan persis. Kalau simpanannya tidak ada — berkas lama, atau
 * setelan dokumen tidak tersedia — yang bisa dilakukan tinggal mencabut
 * warna yang persis sama dengan warna milik alat.
 */
export type FormatAsli = {
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
        ? " (dasar turunan)"
        : " (belum diverifikasi)";

  // Baris rujukan hanya ditulis kalau ia benar-benar MEMBAWA sesuatu yang
  // bisa ditelusuri — yaitu nomor butirnya. Aturan yang tidak punya butir
  // tidak menulis baris rujukan sama sekali.
  //
  // Dua kali diperbaiki, 26 Sep 2026, keduanya atas laporan penelaah:
  //
  //   "Prioritas penelaah — cara mendefinisikan ketentuan (brief bagian 4)
  //    (butir belum diisi) — https://jdih.kemenkeu.go.id/ (T1)"
  //
  // Percobaan pertama memendekkannya jadi "Dasar: Prioritas penelaah — ...",
  // dan itu masih ditolak: baris yang tidak bisa ditelusuri ke mana pun tidak
  // menolong, sependek apa pun. Dasar aturannya tetap terbaca penelaah di
  // panel Pengaturan, tempat yang memang untuk itu.
  //
  // `pdf_url` juga dibuang SELURUHNYA — tiap entri tabel rujukan menunjuk
  // https://jdih.kemenkeu.go.id/, yaitu beranda, bukan peraturannya. Beranda
  // bukan rujukan. Penggantinya nomor halaman PDF KMK 527, yang memang bisa
  // langsung dibuka.
  const adaButir = !!butir && butir !== "...";
  const halaman = temuan.rujukan.halaman?.trim();
  const rujukanStr = adaButir
    ? `${temuan.rujukan.sumber} butir ${butir}` +
      (halaman ? ` (hlm ${halaman})` : "") +
      penanda
    : "";

  const baris = [`Temuan:`, temuan.catatan];

  // DI MANA perbaikannya dikerjakan. Ada karena komentar yang menempel di
  // Pasal 5 bisa menyuruh menambah definisi, padahal definisinya harus
  // ditulis di Pasal 1 — dan penelaah tidak punya cara menebaknya.
  //
  // Backend sudah mengosongkannya kalau tempatnya tidak terbukti ada di
  // naskah, atau kalau tempatnya satuan temuan ini sendiri.
  const sasaran = temuan.sasaran?.trim();
  if (sasaran) baris.push(`Perbaiki di: ${sasaran}`);

  // Kesalahan yang sama di tempat lain. Satu kesalahan yang terulang jadi
  // SATU komentar di kemunculan pertamanya (ditetapkan penelaah 27 Sep 2026,
  // sesudah PMK 104 mendapat satu komentar per baris "RPKBUNP SPAN") — dan
  // kemunculan lainnya tidak disorot, jadi baris inilah satu-satunya petunjuk
  // ke mana lagi penelaah harus melihat. Juga ditulis pada temuan hijau:
  // hijaunya hanya di sini, sisanya diperbaiki penelaah sendiri.
  const jugaDi = (temuan.juga_di ?? []).filter((x) => x.trim());
  if (jugaDi.length > 0) baris.push(`Juga di: ${jugaDi.join("; ")}`);

  // Temuan lama (dan temuan Fase 1 yang belum dipisah medannya) bisa datang
  // tanpa `saran`. Blok Saran ditinggalkan kosong-melompong lebih buruk
  // daripada tidak ada blok sama sekali — dan sejak 23 Sep 2026 backend
  // sengaja mengosongkannya ketika penggantinya memang tidak diketahui,
  // daripada mengisinya dengan anjuran hampa.
  //
  // TEMUAN HIJAU MELEWATI BLOK INI. Bentuk komentarnya ditetapkan penelaah
  // 27 Sep 2026: "komentar ringkas" — cukup Temuan dan rujukannya.
  //
  // Alasannya bukan penghematan ruang. Pada temuan hijau, penggantinya SUDAH
  // tertulis hijau di sebelah coretannya, jadi blok Saran mengulang kalimat
  // yang sedang dibaca penelaah pada baris yang sama. Yang TIDAK terbaca dari
  // naskah cuma dua: kenapa itu salah, dan atas dasar apa — dan dua itulah
  // yang tetap ditulis.
  //
  // Keputusan ini mengganti yang 26 Sep, waktu itu hijau tidak berkomentar
  // sama sekali. Yang berubah: penelaah bisa membaca APA yang diusulkan dari
  // naskah, tetapi tidak KENAPA.
  const saran = temuan.saran?.trim();
  const hijau = temuan.jenis_tanda === "penggantian" && !!temuan.usulan_rumusan;
  if (saran && !hijau) baris.push(`Saran:`, saran);

  // Sumber rumusan hijau. WAJIB ada kalau temuannya hijau — inilah yang
  // membuat penelaah bisa memeriksa sendiri bahwa usulan itu bukan asal
  // klaim, dan ia satu-satunya bagian blok Saran yang tetap ditulis.
  const sumber = temuan.sumber_usulan?.trim();
  if (hijau && sumber) baris.push(`Sumber usulan: ${sumber}`);

  // Keberatan model atas temuan ini. Ditempelkan, BUKAN menggantikan temuannya
  // — AI tidak pernah menghapus temuan yang kesalahannya sudah terbukti
  // (ditetapkan penelaah, 23 Sep 2026). Penelaah yang menimbang keduanya.
  const catatanAi = temuan.catatan_ai?.trim();
  if (catatanAi) baris.push(`Catatan AI:`, catatanAi);

  // Penanda (T-n) WAJIB ada di tiap komentar, juga yang tanpa rujukan: ia
  // yang dipakai mencari komentar ini kembali saat temuannya ditolak atau
  // naskahnya dibersihkan. Tanpa penanda, komentarnya jadi yatim di naskah
  // penelaah dan cuma bisa dihapus dengan tangan.
  baris.push(
    rujukanStr
      ? `${rujukanStr} ${penandaKomentar(temuan)}`
      : penandaKomentar(temuan)
  );
  return baris.join("\n");
}

/**
 * Penanda pengenal di dalam isi komentar, dipakai saat mencari untuk dihapus.
 *
 * Nomor temuan, bukan aturan_id: inilah yang dibaca penelaah. Konsekuensinya,
 * dua kali analisis pada dokumen yang sama menghasilkan komentar bernomor sama
 * — karena itu panel menolak analisis ulang selama NASKAHNYA masih memuat
 * tanda alat (`hitungTandaAlat`), bukan cuma selama daftar kartunya berisi.
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

      // Pelacakan WAJIB dikembalikan apa pun yang terjadi di bawah. Dulu
      // pengembaliannya di ujung blok, sehingga satu sync yang gagal di
      // tengah jalan meninggalkan Track Changes penelaah mati diam-diam.
      try {
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
          const asli: FormatAsli = {
            color: f.color ?? null,
            strikeThrough: f.strikeThrough ?? null,
            highlightColor: f.highlightColor ?? null,
          };

          const punyaUsulan =
            t.jenis_tanda === "penggantian" && !!t.usulan_rumusan;
          // Kesalahan yang perbaikannya MEMBUANG: dicoret merah, tanpa sisipan
          // hijau. Teksnya tetap tidak dihapus kode — yang menghapus penelaah.
          const usulHapus = t.jenis_tanda === "penghapusan";

          // Tiap temuan dipasang dan di-sync SENDIRI.
          //
          // Diubah 27 Sep 2026. Dulu satu kelompok di-sync sekali di ujung.
          // Office.js berhenti di operasi pertama yang gagal dan TIDAK
          // membatalkan yang sudah jalan: satu content control yang ditolak Word
          // meninggalkan komentar dan coretan merah TANPA bungkus bertag, sisa
          // kelompoknya tidak tergambar, dan tidak ada yang melaporkannya. Tolak
          // lalu tidak menemukan tandanya, dan teksnya tetap merah (PMK 45).
          // Sync per temuan mengurung kegagalan pada temuannya sendiri, dan
          // bekas setengah jadinya bisa dicabut di `cabutSisaGagal`.
          let komentar: Word.Comment | null = null;
          let usulan: Word.Range | null = null;
          try {
            // KOMENTAR DIPASANG PALING DULU, sebelum `r` disentuh sama sekali.
            //
            // Naik ke sini 27 Sep 2026 saat temuan hijau ikut diberi komentar.
            // Sebelumnya ia dipasang sesudah usulan hijau disisipkan dan usulan
            // itu dibungkus content control — dua operasi yang mengubah tetangga
            // `r`. Balon komentar kosong sudah pernah terjadi di proyek ini
            // (25 Sep 2026) justru karena komentar dipasang pada rentang yang
            // sudah bergeser. Memasangnya lebih dulu menghapus seluruh kelas
            // masalah itu, bukan cuma mengurangi peluangnya.
            if (bisaKomentar) komentar = r.insertComment(susunIsiKomentar(t));

            // Urutannya penting. Warna dulu, lalu sisipkan usulan di sebelahnya,
            // baru dibungkus content control. Kalau dibungkus lebih dulu,
            // penyisipan "After" bisa mendarat DI DALAM bungkusnya.
            if (punyaUsulan) {
              // Ada jawabannya: teks lama merah dan dicoret, penggantinya hijau.
              r.font.color = WARNA_SALAH;
              r.font.strikeThrough = true;

              usulan = r.insertText(` ${t.usulan_rumusan}`, "After");
              usulan.font.color = WARNA_USULAN;
              usulan.font.strikeThrough = false;
              usulan.font.highlightColor = null as unknown as string;
              bungkusContentControl(usulan, `${TAG_USUL}${t.nomor}`, t.nomor);
            } else if (usulHapus) {
              // Diusulkan dibuang. Merah dan dicoret sama seperti penggantian,
              // tetapi TIDAK ADA yang disisipkan — memang tidak ada rumusan
              // pengganti yang masuk akal untuk definisi yang tidak terpakai.
              r.font.color = WARNA_SALAH;
              r.font.strikeThrough = true;
            } else if (t.tanpa_sorot) {
              // Anchor netral (F1-002 jalur cadangan, F1-003) — lihat
              // `Temuan.tanpa_sorot`. Lokasinya cuma tempat komentar
              // menempel, BUKAN klaim bahwa teks di situ salah, jadi warnanya
              // sengaja TIDAK disentuh sama sekali. Komentar dan content
              // control di atas tetap terpasang seperti biasa — itu yang
              // membuat Terima/Tolak berfungsi normal untuk temuan ini,
              // ditambahkan 27 Sep 2026 supaya temuan begini tidak lagi
              // hilang begitu saja tanpa jejak di Word.
            } else {
              // Tidak ada rumusan pengganti tunggal — ini peringatan, bukan usul
              // penghapusan. Blok kuning, warna hurufnya TIDAK disentuh: merah
              // membuat alat seolah menyuruh membuang teks itu.
              r.font.highlightColor = WARNA_CATATAN;
            }

            bungkusContentControl(r, `${TAG_ASLI}${t.nomor}`, t.nomor);
            await context.sync();

            // Dihitung SESUDAH sync berhasil. Hitungan yang mendahului buktinya
            // bisa berbohong — dulu temuan yang gagal di tengah kelompok tetap
            // terhitung "dicoret merah".
            formatAsliTemuan.set(t.nomor, asli);
            if (komentar) {
              komentarBaru.push([t, komentar]);
              hasil.dikomentari++;
            }
            if (punyaUsulan) {
              hasil.diusulkan++;
              hasil.dicoretMerah++;
            } else if (usulHapus) {
              hasil.dicoretMerah++;
            } else if (!t.tanpa_sorot) {
              hasil.diblokKuning++;
            }
          } catch (err) {
            console.warn(`Tanda T${t.nomor} gagal dipasang:`, err);
            hasil.idTidakDitandai.push(t.id);
            await cabutSisaGagal(context, t, r, asli, komentar, usulan);
          }
        }

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
      } finally {
        await kembalikanPelacakan(context, modeAwal);
      }
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
 * tidak menyimpan apa pun tentang "usulan mesin".
 *
 * Kegagalan Word menolak pembungkusnya baru muncul saat `context.sync()` —
 * `try` di sini cuma menangkap galat yang terlempar seketika. Sejak 27 Sep
 * 2026 kegagalan itu TIDAK lagi dibiarkan: tanda tanpa bungkus tidak bisa
 * dicabut Tolak maupun Bersihkan, jadi `tandaiSemuaTemuan` mencabut seluruh
 * tanda temuan itu dan melaporkannya "tidak ditandai".
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

/**
 * Mencabut bekas setengah jadi sebuah tanda yang GAGAL dipasang.
 *
 * Office.js tidak membatalkan operasi yang sudah jalan sebelum operasi yang
 * gagal. Tanpa pencabutan ini, temuan yang gagal meninggalkan komentar dan
 * coretan merah tanpa bungkus bertag — tanda yatim yang tidak bisa dicabut
 * Tolak maupun Bersihkan, persis keadaan PMK 45 pada 27 Sep 2026.
 *
 * Tiap pencabutan di-sync sendiri-sendiri: proxy milik operasi yang tidak
 * sempat jalan tidak sah, dan gagal mencabut yang satu tidak boleh
 * menghalangi yang lain. Yang dipulihkan hanya sifat yang memang diubah alat
 * untuk jenis tanda itu — warna milik penyusun tidak disentuh.
 */
async function cabutSisaGagal(
  context: Word.RequestContext,
  t: Temuan,
  r: Word.Range,
  asli: FormatAsli,
  komentar: Word.Comment | null,
  usulan: Word.Range | null
): Promise<void> {
  const coba = async (apa: string, langkah: () => void | Promise<void>) => {
    try {
      await langkah();
      await context.sync();
    } catch (err) {
      console.warn(`Sisa T${t.nomor} (${apa}) gagal dicabut:`, err);
    }
  };

  if (komentar) await coba("komentar", () => komentar.delete());

  // Usulan hijau: kalau sempat dibungkus, dicabut berikut isinya lewat
  // tagnya; kalau belum sempat, lewat rentangnya sendiri.
  let usulanTercabut = false;
  await coba("usulan hijau", async () => {
    const cc = context.document.body.contentControls.getByTag(`${TAG_USUL}${t.nomor}`);
    cc.load("items");
    await context.sync();
    cc.items.forEach((c) => c.delete(false));
    usulanTercabut = cc.items.length > 0;
  });
  if (usulan && !usulanTercabut) await coba("usulan hijau", () => usulan.delete());

  // Bungkus teks asli, kalau ternyata sempat terpasang: dilepas, isinya tetap.
  await coba("bungkus", async () => {
    const cc = context.document.body.contentControls.getByTag(`${TAG_ASLI}${t.nomor}`);
    cc.load("items");
    await context.sync();
    cc.items.forEach((c) => c.delete(true));
  });

  const coret =
    (t.jenis_tanda === "penggantian" && !!t.usulan_rumusan) ||
    t.jenis_tanda === "penghapusan";
  await coba("warna", () => {
    if (coret) {
      if (asli.color) r.font.color = asli.color;
      r.font.strikeThrough = asli.strikeThrough ?? false;
    } else if (!t.tanpa_sorot) {
      r.font.highlightColor = (asli.highlightColor ?? null) as unknown as string;
    }
  });
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

/** Tanda dan komentar milik alat yang masih ada di naskah. */
export type TandaDiNaskah = { tanda: number; komentar: number };

/**
 * Menghitung tanda (content control `DA-*`) dan komentar milik alat yang
 * MASIH ADA di naskah — dari naskahnya sendiri, bukan dari daftar panel.
 *
 * Ditambahkan 27 Sep 2026. Sebelumnya pengaman analisis-berulang cuma
 * memeriksa daftar kartu, dan daftar itu hilang tiap kali panel ditutup, Word
 * dimulai ulang, atau berkas dibuka esok harinya — sementara tandanya tetap
 * di naskah. Analisis berikutnya lalu menomori ulang dari T1 di atas tanda
 * lama: komentar ganda, dan Tolak mencabut tanda milik temuan lain (PMK 45).
 *
 * Content control dibaca lewat WordApi 1.1; komentar lewat 1.4 dan di-sync
 * terpisah, supaya komentar yang terkunci lisensi (CLAUDE.md butir 9) tidak
 * ikut membutakan hitungan tandanya.
 */
export async function hitungTandaAlat(): Promise<TandaDiNaskah> {
  const kosong: TandaDiNaskah = { tanda: 0, komentar: 0 };
  if (!isOfficeAvailable()) return kosong;
  try {
    return await Word.run(async (context) => {
      const kontrol = context.document.body.contentControls;
      kontrol.load("items/tag");
      await context.sync();
      const tanda = kontrol.items.filter(
        (cc) => cc.tag?.startsWith(TAG_ASLI) || cc.tag?.startsWith(TAG_USUL)
      ).length;

      let komentar = 0;
      if (checkApiSupport("1.4")) {
        try {
          const semua = context.document.body.getComments();
          semua.load("items/content");
          await context.sync();
          komentar = semua.items.filter((k) =>
            /\(T\d+\)$/.test((k.content ?? "").trim())
          ).length;
        } catch (err) {
          console.warn("Komentar alat tidak bisa dihitung:", err);
        }
      }
      return { tanda, komentar };
    });
  } catch (err) {
    console.warn("Tanda alat di naskah tidak bisa dihitung:", err);
    return kosong;
  }
}

// ---------------------------------------------------------------------------
// Daftar temuan yang ikut tersimpan di dalam berkas Word
// ---------------------------------------------------------------------------
//
// Ditetapkan penelaah 27 Sep 2026 (K2 di docs/perbaiki bug.md). Tanda alat
// hidup di naskah; daftar kartunya dulu cuma hidup di memori panel. Menutup
// panel, memulai ulang Word, atau membuka berkas esok harinya menghapus
// daftarnya — keputusan yang belum diambil ikut hilang, dan Terima/Tolak tidak
// lagi bisa dikerjakan untuk tanda yang masih ada.
//
// Disimpan lewat Office.context.document.settings: ikut tersimpan DI DALAM
// berkasnya saat berkas disimpan, jadi pindah bersama berkasnya. `set` hanya
// mengubah salinan di memori — `saveAsync` yang menuliskannya ke dokumen.

const KUNCI_DAFTAR = "drafterAnaliser.daftarTemuan";

// Batas aman ukuran simpanan. Satu analisis wajar (≤50 temuan) jauh di bawah
// ini; yang melewatinya lebih baik tidak disimpan daripada menggagalkan
// penyimpanan seluruh setelan add-in.
const BATAS_UKURAN_SIMPANAN = 1_500_000;

/** Isi yang disimpan di dalam berkas. */
export type DaftarTersimpan = {
  versi: 1;
  temuan: Temuan[];
  idTidakDitandai: string[];
  jenisDokumen: string | null;
  /** Format asli tiap rentang — tanpa ini Tolak sesudah dibuka ulang hanya bisa menebak. */
  formatAsli: [number, FormatAsli][];
};

function setelanDokumen(): Office.Settings | null {
  try {
    return Office.context?.document?.settings ?? null;
  } catch {
    return null;
  }
}

/**
 * Menyimpan daftar temuan ke dalam berkas. Daftar kosong MENGHAPUS simpanannya.
 * Mengembalikan false kalau setelan dokumen tidak tersedia atau gagal disimpan —
 * pengaman 3a (hitungTandaAlat) tetap bekerja tanpanya.
 */
export async function simpanDaftarDiNaskah(data: {
  temuan: Temuan[];
  idTidakDitandai: string[];
  jenisDokumen: string | null;
}): Promise<boolean> {
  if (!isOfficeAvailable()) return false;
  const setelan = setelanDokumen();
  if (!setelan) return false;
  try {
    if (data.temuan.length === 0) {
      setelan.remove(KUNCI_DAFTAR);
    } else {
      const isi: DaftarTersimpan = {
        versi: 1,
        ...data,
        formatAsli: [...formatAsliTemuan.entries()],
      };
      if (JSON.stringify(isi).length > BATAS_UKURAN_SIMPANAN) {
        console.warn("Daftar temuan terlalu besar untuk disimpan di berkas.");
        return false;
      }
      setelan.set(KUNCI_DAFTAR, isi);
    }
    return await new Promise<boolean>((selesai) =>
      setelan.saveAsync((hasil) =>
        selesai(hasil.status === Office.AsyncResultStatus.Succeeded)
      )
    );
  } catch (err) {
    console.warn("Daftar temuan gagal disimpan di berkas:", err);
    return false;
  }
}

/** Daftar yang tersimpan di berkas ini, atau null. Tidak mengubah apa pun. */
export function bacaDaftarDariNaskah(): DaftarTersimpan | null {
  if (!isOfficeAvailable()) return null;
  try {
    const isi = setelanDokumen()?.get(KUNCI_DAFTAR) as DaftarTersimpan | null;
    if (!isi || isi.versi !== 1 || !Array.isArray(isi.temuan)) return null;
    return {
      ...isi,
      idTidakDitandai: Array.isArray(isi.idTidakDitandai) ? isi.idTidakDitandai : [],
      formatAsli: Array.isArray(isi.formatAsli) ? isi.formatAsli : [],
    };
  } catch (err) {
    console.warn("Daftar temuan di berkas tidak terbaca:", err);
    return null;
  }
}

/** Kembalikan format asli dari simpanan, supaya Tolak memulihkan persis. */
export function pulihkanFormatAsli(entri: [number, FormatAsli][]): void {
  formatAsliTemuan.clear();
  for (const [nomor, format] of entri) formatAsliTemuan.set(nomor, format);
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

/**
 * Melompat ke TEMPAT PERBAIKANNYA — bukan ke tempat temuannya.
 *
 * Dua tempat itu memang sering berbeda, dan itulah seluruh alasan medan
 * `sasaran` ada: komentar menempel di Pasal 2 tempat frasanya bermasalah,
 * sementara definisinya harus ditulis di Pasal 1. Sebelum ada tombol ini
 * penelaah membaca "Perbaiki di: Pasal 1 angka 5" lalu menggulir mencarinya
 * sendiri.
 *
 * Kenapa lewat tombol di kartu, BUKAN tautan di dalam komentar Word:
 * `CommentContentRange.hyperlink` memang ada (WordApi 1.4), tetapi ia
 * memasang tautan pada SELURUH isi komentar, bukan sepenggal kata — dan
 * sasarannya menuntut bookmark ditanam di naskah penelaah. Menambah tanda
 * permanen ke dokumen orang demi satu lompatan bukan pertukaran yang sepadan;
 * tombol di panel tidak menyentuh naskah sama sekali.
 */
export async function lompatKeSasaran(temuan: Temuan): Promise<boolean> {
  const index = temuan.sasaran_paragraf;
  if (!isOfficeAvailable() || index === null || index === undefined) {
    return false;
  }

  // Kursor yang berpindah sebentar lagi datang dari PANEL. Tanpa ini pemantau
  // seleksi membacanya sebagai perpindahan penelaah, dan sorotan kartunya
  // lepas tepat saat tombolnya ditekan.
  seleksiDigerakkanPanel();

  try {
    return await Word.run(async (context) => {
      const paragraphs = context.document.body.paragraphs;
      paragraphs.load("items");
      await context.sync();

      const p = paragraphs.items[index];
      if (!p) return false;

      p.getRange().select();
      await context.sync();
      return true;
    });
  } catch (err) {
    console.warn("Gagal melompat ke sasaran perbaikan:", err);
    return false;
  }
}

export async function selectFindingLocation(temuan: Temuan): Promise<boolean> {
  if (!isOfficeAvailable()) return false;

  // Sama alasannya dengan `lompatKeSasaran` — lihat catatan di sana.
  seleksiDigerakkanPanel();

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

// ---------------------------------------------------------------------------
// Menyorot kartu menurut posisi kursor di naskah
// ---------------------------------------------------------------------------
//
// Kebalikan "Lompat ke Teks": penelaah mengklik naskah, kartunya yang menyala.
//
// WORD TIDAK PUNYA EVENT GULIR. Seluruh API bernama `scroll*` di
// @types/office-js milik `Window` Excel — `scrollRow`, `scrollColumn`. Word
// tidak mengekspos posisi gulir maupun perubahannya, jadi "kartu mengikuti
// saat digulir" memang tidak bisa dibangun. Yang bisa: `DocumentSelectionChanged`,
// yang menyala saat SELEKSI berpindah — klik, tombol panah, mengetik.
//
// Praktiknya itu menjawab kebutuhannya: orang yang menelaah jarang menggulir
// tanpa menaruh kursor.
//
// Pemetaan ke kartu memakai mesin yang SUDAH ADA, bukan yang baru: tiap temuan
// yang tertandai dibungkus content control ber-tag `DA-ASLI-<nomor>`, jadi
// cukup ditanya content control apa yang ada di paragraf terpilih. Semuanya
// WordApi 1.1 (`Paragraph.contentControls`), satu `sync`, dan TIDAK menyentuh
// naskah sama sekali — pemantau ini cuma membaca.
//
// Jalur yang sengaja TIDAK dipakai: `Paragraph.uniqueLocalId` menuntut WordApi
// 1.6, dan CLAUDE.md butir 9 sudah mencatat bahwa requirement set yang
// dilaporkan didukung pun masih bisa melempar NotImplemented.

/**
 * Jeda tahan sebelum seleksi dibaca. Tiap tombol panah menyalakan event.
 *
 * 120 ms, diturunkan dari 200 pada 27 Sep 2026 — penelaah melaporkan kartunya
 * "baru tersorot sesudah beberapa detik". Cukup rapat untuk terasa seketika
 * pada satu klik, masih cukup renggang untuk menelan hujan event saat tombol
 * panah ditahan.
 */
const JEDA_PEMANTAU_MS = 120;

/** Berapa lama event diabaikan sesudah PANEL sendiri yang memindahkan kursor. */
const ABAIKAN_SELEKSI_SENDIRI_MS = 800;

let lepasPemantau: (() => void) | null = null;
let bacaanSedangJalan = false;
let seleksiSendiriSampai = 0;
let tundaPembacaan: ReturnType<typeof setTimeout> | null = null;

/**
 * Tandai bahwa perpindahan kursor berikutnya datang dari PANEL, bukan penelaah.
 *
 * Tanpa ini "Lompat ke Perbaikan" memantul: ia memindahkan kursor ke Pasal 1,
 * event menyala, pemantau membaca paragraf yang tidak punya tanda apa pun, dan
 * sorotan kartunya lepas tepat saat penelaah menekannya.
 */
export function seleksiDigerakkanPanel(): void {
  seleksiSendiriSampai = Date.now() + ABAIKAN_SELEKSI_SENDIRI_MS;
}

/** Nomor temuan yang tandanya ada di paragraf terpilih. Null berarti tidak ada. */
async function bacaNomorDiSeleksi(): Promise<number | null> {
  return await Word.run(async (context) => {
    // SATU `sync`, bukan dua. `getFirst()` adalah operasi yang DIANTRIKAN,
    // jadi paragrafnya tidak perlu dimuat lebih dulu sebelum content
    // control-nya diminta. Versi dua-sync terasa lambat oleh penelaah: tiap
    // klik menunggu dua perjalanan bolak-balik ke Word sebelum kartunya
    // menyala.
    //
    // Content control DI DALAM paragrafnya, bukan yang persis membungkus
    // kursor. Sengaja longgar: penelaah mengklik di mana saja pada baris yang
    // bermasalah, bukan tepat di atas kata yang disorot.
    const kontrol = context.document
      .getSelection()
      .paragraphs.getFirst()
      .contentControls;
    kontrol.load("items/tag");
    await context.sync();

    for (const k of kontrol.items) {
      if ((k.tag ?? "").startsWith(TAG_ASLI)) {
        const n = nomorDariTag(k.tag);
        if (n !== null) return n;
      }
    }
    return null;
  });
}

/**
 * Pasang pemantau seleksi. Mengembalikan false kalau tidak tersedia.
 *
 * `onSorot` dipanggil HANYA ketika sebuah temuan benar-benar ketemu. Paragraf
 * tanpa tanda tidak memanggil apa pun — kalau ia melepas sorotan, sorotannya
 * berkedip-kedip sepanjang penelaah mengetik, dan kartu yang sedang ditimbang
 * hilang dari pandangan justru saat naskahnya sedang diperbaiki.
 */
export async function pasangPemantauSeleksi(
  onSorot: (nomor: number) => void
): Promise<boolean> {
  if (!isOfficeAvailable()) return false;
  if (lepasPemantau) return true;

  const tangani = () => {
    if (Date.now() < seleksiSendiriSampai) return;
    if (tundaPembacaan) clearTimeout(tundaPembacaan);
    tundaPembacaan = setTimeout(() => {
      tundaPembacaan = null;
      if (bacaanSedangJalan) return;
      bacaanSedangJalan = true;
      bacaNomorDiSeleksi()
        .then((nomor) => {
          if (nomor !== null) onSorot(nomor);
        })
        .catch((err) => console.warn("Gagal membaca seleksi:", err))
        .finally(() => {
          bacaanSedangJalan = false;
        });
    }, JEDA_PEMANTAU_MS);
  };

  try {
    // JALUR CADANGAN RUNTIME, CLAUDE.md butir 9. Bukan cuma memeriksa
    // requirement set: pemasangannya sendiri ditunggu hasilnya, dan kegagalan
    // apa pun berakhir dengan fitur ini mati diam-diam — bukan panel rusak.
    const terpasang = await new Promise<boolean>((resolve) => {
      try {
        Office.context.document.addHandlerAsync(
          Office.EventType.DocumentSelectionChanged,
          tangani,
          (hasil) =>
            resolve(hasil.status === Office.AsyncResultStatus.Succeeded)
        );
      } catch {
        resolve(false);
      }
    });
    if (!terpasang) return false;

    lepasPemantau = () => {
      try {
        Office.context.document.removeHandlerAsync(
          Office.EventType.DocumentSelectionChanged,
          { handler: tangani }
        );
      } catch (err) {
        console.warn("Pemantau seleksi gagal dilepas:", err);
      }
    };
    return true;
  } catch (err) {
    console.warn("Pemantau seleksi tidak bisa dipasang:", err);
    return false;
  }
}

/** Lepas pemantau seleksi. Aman dipanggil walau belum pernah terpasang. */
export function lepasPemantauSeleksi(): void {
  if (tundaPembacaan) {
    clearTimeout(tundaPembacaan);
    tundaPembacaan = null;
  }
  const lepas = lepasPemantau;
  lepasPemantau = null;
  if (lepas) lepas();
}
