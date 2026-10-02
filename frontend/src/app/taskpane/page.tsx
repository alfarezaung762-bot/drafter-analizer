"use client";

import { useState, useEffect, useMemo, useCallback, useRef } from "react";
import {
  Temuan,
  ParagrafInput,
  AnalisisRequest,
  AnalisisResponse,
  JenisDokumen,
  StatusTemuan,
  AnalisisLanjutRequest,
  MulaiResponse,
  KemajuanResponse,
  KeteranganAturan,
  NaskahTerbaca,
  AlurAnalisis,
  AnalisisPanel,
  DaftarAnalisisResponse,
  AnalisisAgenRequest,
  KemajuanAgenResponse,
  KeadaanPutaran,
} from "@/lib/types";
import {
  bacaNaskah,
  selectFindingLocation,
  lompatKeSasaran,
  tandaiSemuaTemuan,
  perbaruiKomentarTemuan,
  tolakTemuan,
  bersihkanSemuaTanda,
  cakupanTerpilihTersedia,
  pasangPemantauSeleksi,
  lepasPemantauSeleksi,
  hitungTandaAlat,
  simpanDaftarDiNaskah,
  bacaDaftarDariNaskah,
  pulihkanFormatAsli,
  pasangSisipan,
  lihatSorotan,
  bacaNaskahSesudahKeputusan,
  keKoordinatNaskah,
  type HasilPenandaan,
  type PetaPeriksaUlang,
} from "@/lib/office";
import {
  ATURAN_FASE1,
  ATURAN_BISA_DIPILIH,
  SEMUA_ID_AKTIF,
} from "@/lib/aturan-fase1";
import {
  ATURAN_FASE2,
  ATURAN_STRUKTURAL_LANJUT,
  ATURAN_INTERNAL,
  ATURAN_EKSTERNAL,
  ID_AKTIF_BAWAAN,
} from "@/lib/aturan-fase2";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Berapa kartu yang digambar sekaligus.
//
// Brief 8.7: Law Analyzer berhenti merespons di 68/175 satuan, dan titik
// berhentinya selalu sama — jadi sebabnya beban penggambaran, bukan kegagalan
// acak. Batas ini yang menahannya. Sisanya tetap ada di daftar dan bisa
// ditampilkan penelaah, cuma tidak digambar sekaligus.
const BATAS_KARTU_AWAL = 40;
const TAMBAH_KARTU = 40;

// Jarak antar-pengambilan kemajuan Fase 2. Dua detik: cukup rapat supaya
// angkanya terasa hidup, cukup renggang supaya panel tidak sibuk sendiri.
const JEDA_TANYA_MS = 2000;

// Kapan panel menyerah menunggu. Sejak bug 7 tiap panggilan membawa naskah
// utuh, jadi naskah besar bisa berjalan lebih dari 15 menit — apalagi kalau
// kuota token per menit Azure tersentuh dan panggilannya diulang. Yang
// menandakan macet bukan lamanya, melainkan kemajuan yang DIAM: tidak ada
// tahap, angka, atau panggilan yang bergerak selama 10 menit. Batas mutlaknya
// tetap ada, karena panel yang berputar selamanya tidak bisa dibedakan
// penelaah dari analisis yang memang lama.
const BATAS_DIAM_MS = 10 * 60_000;
const BATAS_TOTAL_MS = 90 * 60_000;

/** Ekspor alat pengembang — satu per tahap (bug 7). */
const EKSPOR_TAHAP: { tahap: number; keterangan: string }[] = [
  {
    tahap: 1,
    keterangan:
      "hasil parser: pohon satuan, definisi Pasal 1, paragraf di luar satuan, dan lampiran berikut jenis bloknya. Gratis.",
  },
  {
    tahap: 2,
    keterangan: "perkiraan token, lalu bahan persis yang ikut di tiap panggilan AI. Gratis.",
  },
  {
    tahap: 3,
    keterangan: "pesan cari dugaan persis seperti dikirim ke AI pada analisis terakhir, termasuk tanya ulang.",
  },
  {
    tahap: 4,
    keterangan: "pesan memastikan tiap dugaan — tempat temuan lahir — berikut hasil alat yang dibaca AI.",
  },
  {
    tahap: 5,
    keterangan: "nasib tiap dugaan: lolos jadi temuan atau gugur, berikut alasannya.",
  },
];

/** "tahap 3 cari dugaan · 4/12 panggilan" — satuan hitungnya menurut tahap. */
function uraiKemajuan(k: { tahap: string; selesai: number; total: number }): string {
  const nomor = k.tahap.split(" ")[0];
  const satuan = nomor === "3" ? " panggilan" : nomor === "4" ? " dugaan" : "";
  return `tahap ${k.tahap} · ${k.selesai}/${k.total}${satuan}`;
}

// ---------------------------------------------------------------------------
// Fase 4 — agen penuh (saklar FASE2_ALUR=agen di backend)
// ---------------------------------------------------------------------------

/** Ekspor alat pengembang alur agen — menggantikan ekspor tahap 1–5. */
const EKSPOR_AGEN: { tahap: number; keterangan: string }[] = [
  {
    tahap: 1,
    keterangan:
      "label satuan, peta letak, naskah berlabel dan naskah berformat persis yang dibaca agen. Gratis bila belum ada analisis.",
  },
  {
    tahap: 2,
    keterangan:
      "jejak agen per putaran: tiap request, alat dan hasilnya, token, laporan selesai, dan putusan penilai kedua.",
  },
  {
    tahap: 3,
    keterangan:
      "gerbang: calon yang lolos jadi temuan, yang ditolak penilai, gugur, atau diturunkan — berikut alasannya.",
  },
];

/** Tulisan tombol Analisis selama alur agen berjalan. */
function uraiTahapAgen(tahap: string, putaran: KeadaanPutaran[], berjalan: boolean): string {
  if (!berjalan) return "Membaca naskah dan formatnya…";
  if (tahap.startsWith("2")) {
    const rampung = putaran.filter(
      (p) => !["menunggu", "berjalan", "menilai"].includes(p.keadaan)
    ).length;
    return `Tahap 2 · agen ${rampung}/${putaran.length} putaran…`;
  }
  if (tahap.startsWith("3")) return "Tahap 3 · gerbang memeriksa bukti…";
  return "Tahap 1 · menyiapkan bahan…";
}

/** Keadaan putaran dalam kalimat panel. */
const KEADAAN_PUTARAN: Record<string, string> = {
  menunggu: "menunggu",
  berjalan: "berjalan",
  menilai: "dinilai penilai kedua",
  selesai: "selesai",
  macet: "macet — dihentikan",
  dibatalkan: "dibatalkan",
  gagal: "gagal",
};

/** Cara tanda muncul di naskah, menurut baris Respons analisis. */
const TANDA_RESPONS: Record<string, string> = {
  otomatis:
    "AI memilih per temuan: usulan hijau di sebelah coretan merah, dicoret merah tanpa pengganti, atau blok kuning — gerbang kode yang memastikan buktinya; yang tidak terbukti turun jadi blok kuning.",
  usulan:
    "Usulan hijau di sebelah coretan merah bila penggantinya terbukti; bila tidak, blok kuning dengan contoh rumusan di Saran.",
  dibuang:
    "Dicoret merah tanpa pengganti bila alasannya terbukti kode; bila tidak, blok kuning dengan saran hapus.",
  catatan: "Blok kuning dan komentar. Warna huruf tidak disentuh.",
};

/** Satu baris daftar backend → kartu Pengaturan yang sudah ada bentuknya. */
function keteranganDariPanel(a: AnalisisPanel): KeteranganAturan & { denganModel?: boolean } {
  const sumber =
    a.dasar_status === "visual"
      ? `KMK 527/KMK.01/2022 ${a.dasar}.`
      : a.dasar_status === "turunan"
        ? `KMK 527/KMK.01/2022 ${a.dasar} — dasar turunan: aturan ini akibat butir itu, bukan bunyinya.`
        : a.dasar_status === "prioritas"
          ? "Prioritas penelaah — tidak ada butir KMK 527 yang dikutip."
          : "Dasar kosong — AI mencarikan rujukannya; yang tidak terbukti ditulis tanpa rujukan, tidak dikarang.";
  return {
    id: a.id,
    judul: `${a.id} · ${a.judul}`,
    diperiksa: a.diperiksa,
    tidakDiperiksa: a.tidakDiperiksa,
    tanda: TANDA_RESPONS[a.respons] ?? TANDA_RESPONS.catatan,
    catatanSumber: sumber,
    dimatikan: a.tersedia ? undefined : a.alasan || "tidak tersedia",
    // Seluruh analisis alur agen memakai AI — lencana "pakai AI" di tiap
    // kartu tidak membedakan apa pun, dan label "Perlu diperiksa sendiri"
    // keliru di depan alamat Dasar. Kartunya memakai label "Dasar aturannya".
    denganModel: false,
  };
}

/**
 * Geser nomor paragraf temuan yang letaknya SESUDAH paragraf `sesudah` —
 * paragraf sisipan baru dipasang (+1) atau dicabut (−1). Nomor paragraf
 * dipakai Lompat ke Teks, Lompat ke Perbaikan, dan Periksa ulang; tanpa
 * pergeseran ini semuanya meleset satu baris per sisipan.
 */
function geserParagraf(daftar: Temuan[], sesudah: number, delta: number): Temuan[] {
  const geser = (i: number) => (i > sesudah ? i + delta : i);
  return daftar.map((t) => ({
    ...t,
    lokasi: { ...t.lokasi, paragraf_index: geser(t.lokasi.paragraf_index) },
    sasaran_paragraf: t.sasaran_paragraf == null ? t.sasaran_paragraf : geser(t.sasaran_paragraf),
    sisipan: t.sisipan
      ? {
          ...t.sisipan,
          sesudah_paragraf: geser(t.sisipan.sesudah_paragraf),
          format_dari:
            t.sisipan.format_dari == null || t.sisipan.format_dari < 0
              ? t.sisipan.format_dari
              : geser(t.sisipan.format_dari),
          paragraf: t.sisipan.paragraf == null ? t.sisipan.paragraf : geser(t.sisipan.paragraf),
        }
      : t.sisipan,
  }));
}

// Sesudah Track Changes ditinggalkan (17 Sep 2026), seluruh penandaan berjalan
// di atas WordApi 1.1 — Font.color, Font.strikeThrough, Range.insertText,
// Range.insertContentControl, ContentControlCollection.getByTag. Hanya komentar
// yang butuh 1.4. Tidak ada lagi ketergantungan pada WordApiDesktop, jadi
// versinya tidak lagi ditampilkan di diagnostik.
//
// 1.3 ditambahkan 18 Sep 2026: cakupan "Bagian Terpilih" memanggil
// Range.intersectWithOrNullObject() yang ada di himpunan itu. Selama 1.3 tidak
// ikut ditampilkan, satu-satunya gejala kalau ia tidak tersedia adalah pesan
// "Gagal menjalankan analisis" tanpa sebab yang bisa ditelusuri penelaah.
const API_VERSIONS = ["1.1", "1.3", "1.4", "1.7", "1.8", "1.9"];

// Teks contoh untuk pengujian di luar Word (web mode)
const CONTOH_DRAFT_PMK = `PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
NOMOR 99/PMK.01/2024
TENTANG
Tata Cara Penyusunan Anggaran dan Standar Biaya Masukan Tahun Anggaran 2025
DENGAN RAHMAT TUHAN YANG MAHA ESA
MENTERI KEUANGAN REPUBLIK INDONESIA,

Menimbang :
a. bahwa untuk melaksanakan ketentuan peraturan perundang-undangan;
b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, dipandang perlu menetapkan peraturan;

Mengingat :
1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara;
2. Peraturan Pemerintah Pengganti Undang-undang Nomor 1 Tahun 2020;

MEMUTUSKAN:
Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA PENYUSUNAN ANGGARAN DAN STANDAR BIAYA KELUARAN TAHUN ANGGARAN 2025.

Pasal 1
Ketentuan dalam peraturan ini berlaku bagi seluruh satuan kerja.`;

export default function TaskpanePage() {
  const [inWord, setInWord] = useState<boolean | null>(null);
  const [apiChecks, setApiChecks] = useState<{ version: string; supported: boolean }[]>([]);
  const [scope, setScope] = useState<"all" | "selection">("all");
  // Cakupan "Bagian Terpilih" butuh WordApi 1.3 (intersectWithOrNullObject).
  // Dimulai false dan baru dinyalakan kalau Word-nya benar-benar melaporkan
  // dukungan — menolak lebih dulu lebih baik daripada gagal di tengah analisis.
  const [bisaCakupanTerpilih, setBisaCakupanTerpilih] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [temuanList, setTemuanList] = useState<Temuan[]>([]);
  const [paragrafCount, setParagrafCount] = useState<number>(0);
  // Jenis dokumen dipilih penelaah, tidak ditebak alat — lihat
  // docs/fase1 drafter.md bagian 6.7.
  //
  // Sengaja dimulai TANPA pilihan. Kalau salah satunya jadi bawaan, penelaah
  // yang lupa memilih tetap dapat hasil analisis — hasil yang diperiksa
  // memakai kaidah jenis dokumen yang keliru, tanpa ada apa pun yang memberi
  // tahu. Lebih baik menolak berjalan daripada diam-diam salah.
  const [jenisDokumen, setJenisDokumen] = useState<JenisDokumen | null>(null);
  const [goyangJenis, setGoyangJenis] = useState(false);
  const [selectedTemuanId, setSelectedTemuanId] = useState<string | null>(null);

  // --- Pesan ke penelaah, dipisah menurut WATAKNYA -------------------------
  //
  // Sampai 27 Sep 2026 semuanya tercetak sebagai kotak yang bertumpuk di atas
  // daftar kartu — enam kotak sekaligus pada satu analisis, dan kartu yang
  // sedang ditelaah terdorong ke bawah layar. Satu `statusMessage` dulu
  // dipakai untuk tiga hal yang wataknya berlawanan: konfirmasi aksi, ringkasan
  // tahap, dan GALAT. Menyamakan ketiganya berarti galat ikut diperlakukan
  // seperti konfirmasi, atau konfirmasi ikut menetap seperti galat.
  //
  // Pembagiannya sekarang:
  //   pesanGalat   — ada yang GAGAL atau terhalang. Menetap sampai ditutup
  //                  penelaah atau analisis berikutnya dimulai. Tidak pernah
  //                  hilang sendiri: galat yang lenyap dalam tiga detik sama
  //                  saja dengan galat yang tidak dilaporkan.
  //   peringatan   — tidak gagal, tetapi menuntut perhatian atau tindakan
  //                  (komentar kosong, Track Changes menyala, Fase 2 dilewati).
  //                  Menetap, bisa ditutup satu per satu.
  //   toast        — konfirmasi sekali pakai sesudah sebuah aksi. Hilang
  //                  sendiri, dan TIDAK menggeser tata letak panel.
  //   Rincian proses — ringkasan tiap tahap analisis. Tertutup secara bawaan;
  //                  kepalanya tetap menyebut hasil tiap tahap, jadi hasilnya
  //                  terbaca tanpa membukanya.
  const [pesanGalat, setPesanGalat] = useState<{
    teks: string;
    // "jenis" = galat karena jenis dokumen belum dipilih — dibersihkan sendiri
    // begitu penelaah memilihnya, supaya tidak menetap sebagai galat basi.
    kunci?: "jenis";
  } | null>(null);
  const [peringatan, setPeringatan] = useState<string[]>([]);
  const [toast, setToast] = useState<{ id: number; teks: string } | null>(null);
  const [hasilFase1, setHasilFase1] = useState<{
    jumlah: number;
    baris: number;
  } | null>(null);
  const [jumlahFase2, setJumlahFase2] = useState<number | null>(null);
  const [rincianTerbuka, setRincianTerbuka] = useState(false);

  // --- Naskah yang diperiksa, bukan daftar kartu ---------------------------
  //
  // Jumlah tanda dan komentar alat yang MASIH ADA di naskah. null = belum
  // dihitung. Inilah yang mengunci analisis ulang, bukan daftar kartu: daftar
  // hilang tiap kali panel ditutup atau Word dimulai ulang, tandanya tidak.
  // Dulu yang diperiksa daftarnya, dan analisis berikutnya menomori ulang dari
  // T1 di atas tanda lama — komentar ganda, dan Tolak mencabut tanda milik
  // temuan lain (PMK 45, 27 Sep 2026; docs/perbaiki bug.md bug 3).
  const [tandaDiNaskah, setTandaDiNaskah] = useState<number | null>(null);
  // Daftar yang tersimpan di berkas sudah dicoba dipulihkan. Sebelum itu
  // daftar panel masih kosong, dan menyimpannya berarti MENGHAPUS simpanan
  // yang belum sempat dibaca.
  const [pulihSelesai, setPulihSelesai] = useState(false);
  // Bersihkan dua langkah — lihat `perluYakin` di dekat tombolnya.
  const [yakinBersihkan, setYakinBersihkan] = useState(false);

  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [showPengaturan, setShowPengaturan] = useState(false);
  // Aturan mana saja yang dijalankan. Semula semuanya. Penelaah bisa mematikan
  // satu aturan yang salah tandai tanpa menunggu kodenya diperbaiki — dan bisa
  // memeriksa manual apa yang sebenarnya diperiksa tiap aturan.
  const [aturanAktif, setAturanAktif] = useState<Set<string>>(
    () => new Set(SEMUA_ID_AKTIF)
  );
  const [aturanTerbuka, setAturanTerbuka] = useState<string | null>(null);
  // Hitungan netral hasil penandaan Fase 1 ("3 dicoret merah, 2 komentar") —
  // masuk Rincian proses. Peringatan yang dulu ikut tercampur di sini (komentar
  // kosong, Track Changes menyala) dipindah ke `peringatan`, karena itu menuntut
  // tindakan dan tidak boleh ikut tertutup.
  const [ringkasanPenandaan, setRingkasanPenandaan] = useState<string | null>(null);
  // Temuan yang TIDAK tertandai di naskah. Kartunya harus memuat alasannya
  // sendiri — bagi temuan ini tidak ada komentar di naskah yang bisa dibaca,
  // dan tombol Terima/Tolak tidak punya apa pun untuk dikerjakan.
  const [idTidakDitandai, setIdTidakDitandai] = useState<Set<string>>(
    () => new Set()
  );

  // Web mode fallback state
  const [webInputText, setWebInputText] = useState(CONTOH_DRAFT_PMK);
  const [useWebCustomText, setUseWebCustomText] = useState(false);

  // --- Fase 2/3 -----------------------------------------------------------
  //
  // Dipisah dari state Fase 1, bukan digabung. Penelaah harus bisa membaca
  // dan memutuskan temuan Fase 1 SEMENTARA Fase 2 masih berjalan — kalau
  // keduanya berbagi satu bendera `analyzing`, seluruh panel terkunci selama
  // beberapa menit dan itu persis keluhan terhadap Law Analyzer.
  const [fase2Berjalan, setFase2Berjalan] = useState(false);
  // Kemajuan per tahap: "3 cari dugaan" menghitung panggilan, "4 memastikan"
  // menghitung dugaan yang diuji.
  const [fase2Kemajuan, setFase2Kemajuan] = useState<{
    tahap: string;
    selesai: number;
    total: number;
  } | null>(null);
  const [fase2Pesan, setFase2Pesan] = useState<string | null>(null);
  const [aturanFase2Aktif, setAturanFase2Aktif] = useState<Set<string>>(
    () => new Set(ID_AKTIF_BAWAAN)
  );
  // Berapa kartu yang boleh digambar. Naik kalau penelaah menekan
  // "Tampilkan lebih banyak".
  const [batasTampil, setBatasTampil] = useState(BATAS_KARTU_AWAL);

  // Kartu mana yang alasannya sedang dibentangkan. Per kartu, bukan satu
  // saklar untuk semua — penelaah membentangkan yang sedang ditimbangnya saja.
  const [alasanTerbuka, setAlasanTerbuka] = useState<Set<string>>(new Set());
  const bentangkanAlasan = (id: string) =>
    setAlasanTerbuka((prev) => {
      const baru = new Set(prev);
      if (baru.has(id)) baru.delete(id);
      else baru.add(id);
      return baru;
    });

  // Alat pengembang — ekspor Tahap 1 sampai 5. Satu yang disiapkan sekali
  // waktu; pesan hasilnya per tahap.
  const [mengeksporTahap, setMengeksporTahap] = useState<number | null>(null);
  const [pesanEkspor, setPesanEkspor] = useState<Record<number, string>>({});
  const [namaDokumen, setNamaDokumen] = useState("");

  // Nomor pekerjaan Fase 2 terakhir di sesi ini. Dipakai Ekspor Tahap 3–5
  // untuk mengambil pesan yang BENAR-BENAR dikirim. Kosong bukan halangan:
  // backend jatuh ke pekerjaan terbaru untuk dokumen ini, supaya panel yang
  // dimuat ulang tetap bisa mengekspor.
  const [nomorPekerjaan, setNomorPekerjaan] = useState<number | null>(null);

  // --- Fase 4: alur agen ---------------------------------------------------
  //
  // Saklarnya di backend (FASE2_ALUR), dibaca lewat GET /analisis/daftar —
  // panel tidak menebak. null = belum terbaca: panel berlaku seperti alur
  // lama, persis seperti sebelum Fase 4 ada.
  const [alur, setAlur] = useState<AlurAnalisis | null>(null);
  // Daftar Pengaturan alur agen — dibaca dari analisis.md dan
  // analisisformat.md, bukan dari berkas keterangan di frontend.
  const [daftarAgen, setDaftarAgen] = useState<AnalisisPanel[]>([]);
  const [aturanAgenAktif, setAturanAgenAktif] = useState<Set<string>>(() => new Set());
  const centangAgenAwal = useRef(false);
  // Kemajuan per putaran — supaya penelaah tahu apa yang sedang berjalan, dan
  // apa yang dibatalkan bila ia menekan Batal.
  const [putaranAgen, setPutaranAgen] = useState<KeadaanPutaran[]>([]);
  const [tahapAgen, setTahapAgen] = useState("");
  // Pekerjaan agen yang SEDANG berjalan — dipakai tombol Batal.
  const [pekerjaanAgen, setPekerjaanAgen] = useState<number | null>(null);
  const [membatalkan, setMembatalkan] = useState(false);
  const pakaiAgen = alur === "agen";

  useEffect(() => {
    let aktif = true;
    void (async () => {
      try {
        const res = await fetch(
          `${API_BASE}/analisis/daftar?jenis=${encodeURIComponent(jenisDokumen ?? "PMK")}`
        );
        if (!res.ok) return;
        const data: DaftarAnalisisResponse = await res.json();
        if (!aktif) return;
        setAlur(data.alur);
        setDaftarAgen(data.analisis);
        if (!centangAgenAwal.current) {
          centangAgenAwal.current = true;
          // Bawaannya semua menyala KECUALI yang butuh korpus — sama dengan
          // Kategori 3 alur lama: isi korpus belum diverifikasi langsung,
          // jadi menyalakannya keputusan sadar penelaah.
          setAturanAgenAktif(
            new Set(
              data.analisis
                .filter((a) => !a.butuh.some((b) => b.includes("korpus")))
                .map((a) => a.id)
            )
          );
        }
      } catch (err) {
        console.warn("Daftar pemeriksaan backend tidak terbaca; panel memakai alur lama.", err);
      }
    })();
    return () => {
      aktif = false;
    };
  }, [jenisDokumen]);

  /**
   * Kosongkan SELURUH jejak analisis sebelumnya dari Rincian proses dan kotak
   * pesan — dipanggil tiap kali analisis baru dimulai dan tiap kali daftar
   * dibersihkan.
   *
   * Semuanya sekaligus, di satu tempat, karena sebelumnya tidak: `fase2Kemajuan`
   * hanya dikosongkan kalau Fase 2 ikut jalan, dan `infoPenandaan` hanya kalau
   * Fase 1 ikut jalan. Analisis yang cuma menjalankan salah satunya
   * meninggalkan angka milik analisis SEBELUMNYA di panel — terbaca seolah
   * milik yang baru. Rincian proses menampilkan tahap-tahap satu analisis;
   * sisa analisis lain di dalamnya adalah keterangan yang bohong.
   */
  const kosongkanTahapan = () => {
    setPesanGalat(null);
    setPeringatan([]);
    setHasilFase1(null);
    setRingkasanPenandaan(null);
    setFase2Kemajuan(null);
    setFase2Pesan(null);
    setJumlahFase2(null);
    setPutaranAgen([]);
    setTahapAgen("");
  };

  /** Konfirmasi sekali pakai. Hilang sendiri — lihat efek di bawah. */
  const tampilkanToast = (teks: string) => {
    setToast({ id: Date.now() + Math.random(), teks });
  };

  // Lama tampil mengikuti panjang kalimatnya: konfirmasi pendek tidak perlu
  // menunggu lama, kalimat panjang tidak boleh hilang sebelum selesai dibaca.
  // Toast baru menggantikan yang lama, dan pewaktunya ikut diganti — tanpa
  // `clearTimeout` di sini, pewaktu toast lama bisa menghapus toast baru.
  useEffect(() => {
    if (!toast) return;
    const lama = Math.min(7000, 2500 + toast.teks.length * 35);
    const pewaktu = window.setTimeout(() => setToast(null), lama);
    return () => window.clearTimeout(pewaktu);
  }, [toast]);

  useEffect(() => {
    // Office.onReady bisa memanggil balik segera — termasuk sebelum komponen
    // ini selesai mount, dan di luar Word perilakunya tidak sama. Tanpa
    // penjaga ini React mengeluh "state update on a component that hasn't
    // mounted yet". Bendera `aktif` juga mencegah setState sesudah unmount.
    let aktif = true;

    const tetapkan = (
      diDalamWord: boolean,
      hasilCek: { version: string; supported: boolean }[] = []
    ) => {
      if (!aktif) return;
      setInWord(diDalamWord);
      if (hasilCek.length > 0) setApiChecks(hasilCek);
      if (diDalamWord) {
        setBisaCakupanTerpilih(cakupanTerpilihTersedia());
        // Nama berkas, dipakai menamai hasil Ekspor Tahap 0. Dibaca dari URL
        // dokumen — gagal membacanya bukan masalah, namanya cuma hiasan.
        try {
          const url = Office.context?.document?.url ?? "";
          const nama = url.split(/[\\/]/).pop() ?? "";
          if (nama) setNamaDokumen(nama.replace(/\.docx?$/i, ""));
        } catch {
          /* nama dokumen tidak wajib */
        }
      }
    };

    if (typeof Office !== "undefined" && Office.onReady) {
      Office.onReady((info) => {
        // Di browser biasa, `info` bisa kosong — jangan diakses langsung.
        if (info?.host === Office.HostType.Word) {
          tetapkan(
            true,
            API_VERSIONS.map((v) => ({
              version: v,
              supported:
                Office.context?.requirements?.isSetSupported("WordApi", v) ??
                false,
            }))
          );
        } else {
          tetapkan(false);
        }
      });
    } else {
      tetapkan(false);
    }

    return () => {
      aktif = false;
    };
  }, []);

  // --- Daftar temuan ikut tersimpan di dalam berkas Word -------------------
  //
  // Ditetapkan penelaah 27 Sep 2026 (K2 di docs/perbaiki bug.md). Saat panel
  // dibuka, daftar yang tersimpan di berkas dipulihkan — tetapi HANYA kalau
  // naskahnya masih memuat tanda alat. Simpanan tanpa tanda berarti tandanya
  // sudah dicabut dengan tangan; kartunya tidak lagi menunjuk apa pun, dan
  // efek penyimpan di bawah akan menghapusnya.
  useEffect(() => {
    if (inWord !== true) return;
    let aktif = true;
    void (async () => {
      const simpanan = bacaDaftarDariNaskah();
      const { tanda, komentar } = await hitungTandaAlat();
      if (!aktif) return;
      const ada = tanda + komentar;
      if (simpanan && simpanan.temuan.length > 0 && ada > 0) {
        pulihkanFormatAsli(simpanan.formatAsli);
        setTemuanList(simpanan.temuan);
        setIdTidakDitandai(new Set(simpanan.idTidakDitandai));
        if (simpanan.jenisDokumen === "PMK" || simpanan.jenisDokumen === "KMK") {
          setJenisDokumen(simpanan.jenisDokumen);
        }
        setToast({
          id: Date.now(),
          teks: `${simpanan.temuan.length} temuan dari analisis sebelumnya dipulihkan dari berkas ini.`,
        });
      }
      setTandaDiNaskah(ada);
      setPulihSelesai(true);
    })();
    return () => {
      aktif = false;
    };
  }, [inWord]);

  // Tiap perubahan daftar ikut disimpan: hasil analisis, Terima, Tolak,
  // Bersihkan. Ditunda sebentar supaya penandaan Fase 2 per kelompok tidak
  // memicu belasan penyimpanan beruntun.
  useEffect(() => {
    if (inWord !== true || !pulihSelesai) return;
    const pewaktu = window.setTimeout(() => {
      void simpanDaftarDiNaskah({
        temuan: temuanList,
        idTidakDitandai: [...idTidakDitandai],
        jenisDokumen,
      });
    }, 500);
    return () => window.clearTimeout(pewaktu);
  }, [inWord, pulihSelesai, temuanList, idTidakDitandai, jenisDokumen]);

  // Kepastian Bersihkan kedaluwarsa sendiri: klik kedua yang datang jauh
  // kemudian bukan lagi jawaban atas pertanyaan yang sama.
  useEffect(() => {
    if (!yakinBersihkan) return;
    const pewaktu = window.setTimeout(() => setYakinBersihkan(false), 6000);
    return () => window.clearTimeout(pewaktu);
  }, [yakinBersihkan]);

  /** Hitung ulang tanda alat di naskah. Mengembalikan jumlahnya. */
  const periksaNaskah = async (): Promise<number> => {
    if (inWord !== true) return 0;
    const { tanda, komentar } = await hitungTandaAlat();
    setTandaDiNaskah(tanda + komentar);
    return tanda + komentar;
  };

  // Tidak ada penyaringan menurut tingkat keparahan lagi — tingkat itu dihapus
  // dari rancangan. Temuan tampil urut posisi dokumen, dibaca dari atas ke
  // bawah, sama dengan urutan nomornya.
  const stats = useMemo(() => {
    return {
      total: temuanList.length,
      diterima: temuanList.filter((t) => t.status === "diterima").length,
      ditolak: temuanList.filter((t) => t.status === "ditolak").length,
      belum: temuanList.filter((t) => t.status === "belum_ditinjau").length,
    };
  }, [temuanList]);

  // Pengaman analisis berulang: komentar menumpuk kalau analisis dijalankan
  // lagi sementara temuan lama belum diputuskan (bagian 6.5).
  //
  // Sejak semua keputusan pindah ke panel, SELURUH temuan dihitung — tidak ada
  // lagi temuan yang statusnya tidak terpantau. Tombol Bersihkan Daftar tetap
  // ada untuk keluar dari keadaan yang terlanjur kacau.
  // Temuan yang tidak punya tanda di naskah tidak bisa diputuskan — tidak ada
  // apa pun untuk diterima atau ditolak di sana. Memasukkannya ke hitungan ini
  // berarti mengunci tombol Analisis selamanya.
  // useCallback supaya identitasnya stabil selama idTidakDitandai tidak
  // berubah — tanpa itu useMemo di bawah kehilangan satu dependensinya dan
  // lint melaporkannya.
  const tidakTertandai = useCallback(
    (t: Temuan) => idTidakDitandai.has(t.id) || !t.lokasi.teks_asli.trim(),
    [idTidakDitandai]
  );

  // Temuan yang punya teks untuk ditunjuk — inilah yang jadi kartu.
  const temuanBerlokasi = useMemo(
    () => temuanList.filter((t) => t.lokasi.teks_asli.trim()),
    [temuanList]
  );

  // Temuan tanpa lokasi (F1-003: sebuah bagian wajib tidak ada). Bukan kartu —
  // tidak ada yang bisa dilompati dan tidak ada yang bisa diterima/ditolak.
  // Ditampilkan sebagai peringatan dokumen, sebaris, di atas daftar.
  const peringatanDokumen = useMemo(
    () => temuanList.filter((t) => !t.lokasi.teks_asli.trim()),
    [temuanList]
  );

  // --- Kartu menyala mengikuti kursor di naskah --------------------------
  //
  // Kebalikan "Lompat ke Teks". Word TIDAK punya event gulir sama sekali
  // (alasannya di office.ts), jadi yang dipakai perpindahan SELEKSI — klik,
  // tombol panah, mengetik.
  //
  // Daftarnya dipegang lewat ref, bukan lewat dependency effect: memasang dan
  // melepas handler Word tiap kali daftar temuan berubah jauh lebih mahal
  // daripada membaca satu ref, dan pemasangan yang berulang itulah yang paling
  // mungkin meninggalkan handler yatim di Word.
  const temuanRef = useRef<Temuan[]>([]);
  useEffect(() => {
    temuanRef.current = temuanBerlokasi;
  }, [temuanBerlokasi]);

  useEffect(() => {
    if (inWord !== true) return;
    let aktif = true;

    void pasangPemantauSeleksi((nomor) => {
      if (!aktif) return;
      const daftar = temuanRef.current;
      const urutan = daftar.findIndex((t) => t.nomor === nomor);
      if (urutan === -1) return;
      const t = daftar[urutan];

      setSelectedTemuanId(t.id);
      // Kartu yang belum digambar tidak bisa digulir ke layar. Batasnya
      // dinaikkan SECUKUPNYA, tidak dibuka semua — batas itu ada karena Law
      // Analyzer berhenti merespons di 68 kartu (brief 8.7).
      setBatasTampil((n) => (urutan < n ? n : urutan + TAMBAH_KARTU));

      // Ditunda sebentar: kartunya mungkin baru digambar pada render
      // berikutnya, dan elemen yang belum ada tidak bisa digulir.
      //
      // `block: "center"`, BUKAN "nearest". "nearest" menggulir sesedikit
      // mungkin, jadi kartunya mendarat menempel di tepi bawah panel —
      // penelaah melihatnya muncul di paling bawah dan tidak yakin yang mana
      // yang sedang disorot. Dilaporkan 27 Sep 2026.
      setTimeout(() => {
        if (!aktif) return;
        document
          .getElementById(`kartu-${t.id}`)
          ?.scrollIntoView({ block: "center", behavior: "smooth" });
      }, 60);
    });

    return () => {
      aktif = false;
      lepasPemantauSeleksi();
    };
  }, [inWord]);

  /** Analisis alur agen yang menyala DAN tersedia untuk jenis naskah ini. */
  const kodeAgenAktif = daftarAgen
    .filter((a) => a.tersedia && aturanAgenAktif.has(a.id))
    .map((a) => a.id);

  /** Tidak ada satu pun pemeriksaan dicentang — tombolnya tidak punya kerja. */
  const tidakAdaYangDicentang = pakaiAgen
    ? kodeAgenAktif.length === 0
    : aturanAktif.size === 0 && aturanFase2Aktif.size === 0;

  const adaYangBelumDiputuskan = useMemo(
    () =>
      temuanBerlokasi.some(
        (t) => t.status === "belum_ditinjau" && !tidakTertandai(t)
      ),
    [temuanBerlokasi, tidakTertandai]
  );

  // ANALISIS ULANG TERKUNCI selama naskah masih memuat tanda alat — dihitung
  // dari NASKAHNYA (`tandaDiNaskah`), bukan dari daftar kartu. Termasuk tanda
  // temuan yang sudah diterima: analisis di atas teks yang masih berisi coretan
  // merah dan usulan hijau membaca keduanya sebagai naskah, lalu menandai
  // ulang semuanya. Selama naskahnya belum dihitung, terkunci juga — lebih baik
  // menunggu sepersekian detik daripada menganalisis di atas tanda lama.
  //
  // Di luar Word (pratinjau web) tidak ada naskah bertanda; yang dipakai daftar.
  const naskahBertanda =
    inWord === true ? tandaDiNaskah === null || tandaDiNaskah > 0 : adaYangBelumDiputuskan;
  // Tombol Bersihkan hanya kalau tandanya SUDAH terhitung ada — bukan selama
  // hitungannya belum selesai, supaya ia tidak berkedip saat panel dibuka.
  const tampilBersihkan =
    inWord === true ? (tandaDiNaskah ?? 0) > 0 : adaYangBelumDiputuskan;

  // Bersihkan juga mencabut usulan yang SUDAH diterima — keputusan penelaah
  // sendiri. Kalau ada yang bisa hilang begitu, klik pertama cuma meminta
  // kepastian. Tanda tanpa daftar (daftar belum/tidak terpulihkan) diperlakukan
  // sama: isinya tidak diketahui, jadi bisa saja memuat yang sudah diterima.
  const perluYakin =
    temuanList.some((t) => t.status === "diterima") ||
    (inWord === true && temuanList.length === 0);

  // Mengosongkan daftar panel SEKALIGUS mencabut seluruh tanda alat dari
  // naskah. Sejak tandanya digambar sendiri (bukan revisi Word), meninggalkan
  // tanda tanpa daftar berarti naskah berisi teks merah-hijau yang tidak ada
  // lagi yang bisa mencabutnya. Yang dicabut hanya yang bertag DA-* — warna
  // dan sorotan milik penyusun sendiri tidak disentuh.
  const handleBersihkanDaftar = async () => {
    if (perluYakin && !yakinBersihkan) {
      setYakinBersihkan(true);
      return;
    }
    setYakinBersihkan(false);
    let hasil = { tanda: 0, komentar: 0 };
    if (inWord) {
      hasil = await bersihkanSemuaTanda();
      // Simpanan di berkas ikut dihapus di sini, tidak menunggu efek penyimpan:
      // kalau daftarnya memang sudah kosong, efek itu tidak terpicu.
      await simpanDaftarDiNaskah({ temuan: [], idTidakDitandai: [], jenisDokumen: null });
      await periksaNaskah();
    }
    setTemuanList([]);
    setSelectedTemuanId(null);
    kosongkanTahapan();
    setBatasTampil(BATAS_KARTU_AWAL);
    // Ikut dikosongkan — tanpa ini, daftar id dari analisis sebelumnya
    // bertahan dan bisa membuat kartu analisis berikutnya salah dilabeli
    // "tidak ditandai di naskah".
    setIdTidakDitandai(new Set());
    tampilkanToast(
      inWord
        ? `Daftar dikosongkan, ${hasil.tanda} tanda dan ${hasil.komentar}` +
          " komentar dicabut dari naskah. Warna dan sorotan milik penyusun" +
          " sendiri tidak disentuh."
        : "Daftar dikosongkan."
    );
  };

  // --- Rincian proses -------------------------------------------------------
  //
  // Kepalanya menyebut HASIL tiap tahap, bukan sekadar "Rincian proses".
  // Rinciannya tertutup secara bawaan, dan tanpa ringkasan di kepalanya
  // analisis yang selesai tanpa temuan tidak meninggalkan bekas yang terbaca
  // sama sekali — padahal "sudah diperiksa, tidak ada temuan" adalah hasil,
  // bukan ketiadaan hasil. Tahap Fase 2 yang sedang berjalan ikut disebut:
  // penelaah berhak tahu analisisnya sampai di mana, bukan cuma berapa temuan
  // yang keluar.
  const adaFase2Kemajuan = !!fase2Kemajuan && fase2Kemajuan.total > 0;
  const adaRincian =
    !!hasilFase1 ||
    !!ringkasanPenandaan ||
    adaFase2Kemajuan ||
    !!fase2Pesan ||
    putaranAgen.length > 0;
  const ringkasTahap = [
    hasilFase1 ? `Fase 1: ${hasilFase1.jumlah} temuan` : null,
    jumlahFase2 !== null
      ? pakaiAgen
        ? `${jumlahFase2} temuan`
        : `Fase 2: ${jumlahFase2} temuan`
      : adaFase2Kemajuan && fase2Kemajuan
        ? fase2Berjalan
          ? `Fase 2: ${uraiKemajuan(fase2Kemajuan)}`
          : // Tidak berjalan dan tidak punya jumlah = berhenti sebelum
            // selesai. Disebut "berhenti", bukan angka kemajuan telanjang
            // yang terbaca seolah masih berjalan.
            `Fase 2: berhenti di ${uraiKemajuan(fase2Kemajuan)}`
        : null,
  ]
    .filter(Boolean)
    .join(" · ");

  // ---------------------------------------------------------------------
  // SATU TOMBOL untuk seluruh fase
  // ---------------------------------------------------------------------
  //
  // Panel Pengaturan yang menentukan apa yang jalan: aturan F1 yang dicentang
  // menjalankan Fase 1, aturan F2/F3 yang dicentang menjalankan Fase 2/3.
  // Penelaah tidak perlu tahu batas fase untuk memakai alat ini — ia cuma
  // mencentang apa yang ingin diperiksa, lalu menekan sekali.
  //
  // Naskahnya dibaca SEKALI dan dipakai kedua fase.

  const bacaNaskahSekali = async (
    opsi: { format?: boolean } = {}
  ): Promise<NaskahTerbaca> => {
    if (inWord) return bacaNaskah(scope, opsi);
    return {
      paragraf: webInputText.split("\n").map((line, idx) => ({ index: idx, teks: line })),
      tabel_raksasa: [],
    };
  };

  /**
   * Paragraf untuk Fase 1: yang letaknya PASTI saja. Sesudah tabel raksasa,
   * nomor paragraf bukan nomor Word, dan temuan Fase 1 di sana akan ditandai
   * di paragraf yang salah. Fase 2 menerima semuanya — backend yang menahan
   * penandaannya.
   */
  const paragrafPasti = (naskah: NaskahTerbaca): ParagrafInput[] =>
    naskah.paragraf.filter((p) => p.letak_pasti !== false);

  /**
   * Nyalakan atau matikan satu kelompok aturan Fase 2/3 sekaligus.
   *
   * Hanya menyentuh id yang ada di `daftar` — sisa centangnya dibiarkan apa
   * adanya. Itu yang membuat "Kosongkan" pada satu kategori tidak ikut
   * mematikan kategori lain, padahal ketiganya berbagi satu himpunan state.
   */
  const setKelompokFase2 = (daftar: { id: string }[], nyala: boolean) =>
    setAturanFase2Aktif((prev) => {
      const next = new Set(prev);
      daftar.forEach((a) => (nyala ? next.add(a.id) : next.delete(a.id)));
      return next;
    });

  /**
   * Berapa pemeriksaan Kategori 1 yang menyala — dua himpunan state dijumlah.
   *
   * F1-001 tidak pernah ikut terhitung karena `dimatikan` di kode, dan
   * ATURAN_BISA_DIPILIH memang sudah mengeluarkannya dari penyebut.
   */
  const jumlahStrukturalAktif =
    aturanAktif.size +
    ATURAN_STRUKTURAL_LANJUT.filter((a) => aturanFase2Aktif.has(a.id)).length;

  /**
   * Satu kartu aturan di panel Pengaturan.
   *
   * Dipakai KETIGA kategori. Sebelum 26 Sep 2026 kode ini disalin dua kali —
   * sekali untuk blok Fase 1, sekali untuk blok Fase 2/3 — dan keduanya sudah
   * sempat berbeda diam-diam: yang satu bisa menampilkan penanda "dimatikan",
   * yang lain penanda "Fase 3", dan judul catatan sumbernya pun beda kalimat.
   * Disatukan supaya perubahan tampilan cukup dikerjakan sekali.
   *
   * `aktif` dan `onToggle` sengaja dioper dari luar, bukan dibaca sendiri di
   * dalam: Kategori 1 memakai DUA himpunan state yang berbeda — jalur cepat
   * yang tidak butuh pohon satuan, dan jalur yang menunggu pohonnya berhasil
   * diurai — jadi kartu tidak boleh menebak sendiri ia milik state yang mana.
   */
  const kartuAturan = (
    aturan: KeteranganAturan & { fase?: 2 | 3; denganModel?: boolean },
    aktif: boolean,
    onToggle: (nyala: boolean) => void
  ) => {
    const mati = !!aturan.dimatikan;
    const terbuka = aturanTerbuka === aturan.id;

    return (
      <div
        key={aturan.id}
        className={`rounded border bg-white ${
          mati ? "border-slate-200 opacity-60" : "border-slate-300"
        }`}
      >
        <div className="flex items-start gap-1.5 px-1.5 py-1.5">
          <input
            type="checkbox"
            id={`aturan-${aturan.id}`}
            checked={aktif && !mati}
            disabled={mati}
            onChange={(e) => onToggle(e.target.checked)}
            className="mt-0.5 accent-blue-700"
          />
          <button
            onClick={() => setAturanTerbuka(terbuka ? null : aturan.id)}
            className="flex-1 text-left"
            aria-expanded={terbuka}
          >
            <span className="text-[11px] text-slate-800 leading-snug">
              {aturan.judul}
            </span>
            {mati && (
              <span className="ml-1 text-[8px] bg-slate-300 text-slate-700 px-1 rounded font-bold align-middle">
                dimatikan
              </span>
            )}
            {aturan.denganModel && (
              <span className="ml-1 text-[8px] bg-blue-100 text-blue-800 px-1 rounded font-bold align-middle">
                pakai AI
              </span>
            )}
            <span className="block text-[9px] text-slate-400">
              {terbuka ? "sembunyikan rincian" : "lihat rincian"}
            </span>
          </button>
        </div>

        {terbuka && (
          <div className="px-2 pb-2 pt-0.5 space-y-1.5 text-[10px] leading-snug border-t border-slate-100">
            {mati && (
              <p className="text-rose-800 bg-rose-50 border border-rose-200 rounded px-1.5 py-1">
                <span className="font-semibold">Kenapa dimatikan: </span>
                {aturan.dimatikan}
              </p>
            )}
            <div>
              <p className="font-semibold text-slate-700">Yang diperiksa</p>
              <ul className="list-disc ml-3.5 text-slate-600 space-y-0.5">
                {aturan.diperiksa.map((baris, i) => (
                  <li key={i}>{baris}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="font-semibold text-slate-700">
                Yang TIDAK diperiksa
              </p>
              <ul className="list-disc ml-3.5 text-slate-500 space-y-0.5">
                {aturan.tidakDiperiksa.map((baris, i) => (
                  <li key={i}>{baris}</li>
                ))}
              </ul>
            </div>
            <p className="text-slate-600">
              <span className="font-semibold text-slate-700">
                Tandanya di naskah:{" "}
              </span>
              {aturan.tanda}
            </p>
            {aturan.catatanSumber && (
              <p className="text-amber-900 bg-amber-50 border border-amber-200 rounded px-1.5 py-1">
                <span className="font-semibold">
                  {aturan.denganModel
                    ? "Perlu diperiksa sendiri: "
                    : "Dasar aturannya: "}
                </span>
                {aturan.catatanSumber}
              </p>
            )}
          </div>
        )}
      </div>
    );
  };

  /**
   * Ringkas hasil penandaan jadi dua bagian yang wataknya berbeda:
   *
   *   ringkasan  — hitungan netral, masuk Rincian proses (tertutup).
   *   peringatan — hal yang menuntut tindakan penelaah; tampil terbuka.
   *
   * Dipisah 27 Sep 2026. Sebelumnya keduanya dirangkai jadi satu kalimat di
   * satu kotak; memasukkan kotak itu utuh ke Rincian yang tertutup berarti
   * peringatan Track Changes dan komentar kosong ikut tersembunyi.
   */
  const ringkasPenandaan = (
    hasil: HasilPenandaan
  ): { ringkasan: string; peringatan: string[] } => {
    const bagian: string[] = [];
    if (hasil.dicoretMerah > 0) bagian.push(`${hasil.dicoretMerah} dicoret merah`);
    if (hasil.diusulkan > 0) bagian.push(`${hasil.diusulkan} usulan hijau disisipkan`);
    if (hasil.diblokKuning > 0) bagian.push(`${hasil.diblokKuning} diberi blok kuning`);
    if (hasil.dikomentari > 0) bagian.push(`${hasil.dikomentari} komentar`);

    let ringkasan = bagian.length > 0 ? bagian.join(", ") + "." : "";
    // Tetap di ringkasan, bukan peringatan: tiap kartunya sendiri sudah
    // berlencana "tidak ditandai di naskah" berikut tombol Alasan, jadi
    // penelaah tidak kehilangan apa pun kalau baris ini tertutup.
    if (hasil.idTidakDitandai.length > 0) {
      ringkasan +=
        ` ${hasil.idTidakDitandai.length} temuan TIDAK ditandai di naskah` +
        " karena letak persisnya tidak ketemu — alasannya ada di kartunya" +
        " masing-masing di bawah.";
    }

    const peringatan: string[] = [];
    // Balon komentar kosong tidak menjelaskan apa-apa tetapi tetap menyorot
    // naskah, jadi penelaah melihat tanda yang bisu. Disebut terang-terangan
    // daripada dibiarkan ditemukan sendiri.
    if (hasil.komentarKosong > 0) {
      peringatan.push(
        `${hasil.komentarKosong} komentar terpasang tetapi isinya kosong —` +
          " Word menolak menuliskannya. Isi temuannya tetap terbaca di kartu" +
          " di bawah. Laporkan ini ke pengembang bila berulang."
      );
    }
    if (!hasil.pelacakanMati) {
      peringatan.push(
        "Pelacakan perubahan tidak bisa dimatikan, jadi tanda-tanda ini" +
          " ikut tercatat Word sebagai revisi format. Matikan Track Changes" +
          " di tab Review lalu jalankan ulang bila margin jadi penuh."
      );
    }
    return { ringkasan: ringkasan.trim(), peringatan };
  };

  /** Fase 1 — detik, gratis. Mengembalikan temuannya untuk dipakai Fase 2. */
  const jalankanFase1 = async (
    paragraf: ParagrafInput[],
    jenis: JenisDokumen
  ): Promise<Temuan[]> => {
    const body: AnalisisRequest = {
      jenis_dokumen: jenis,
      paragraf,
      aturan_aktif: [...aturanAktif],
    };
    const res = await fetch(`${API_BASE}/analisis/jalankan`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!res.ok) {
      throw new Error(`Server merespons status ${res.status}: ${res.statusText}`);
    }

    const data: AnalisisResponse = await res.json();
    setTemuanList(data.temuan);
    setParagrafCount(data.jumlah_paragraf);

    // Ditandai SEGERA, tidak menunggu Fase 2 selesai. Fase 2 berjalan menit;
    // menahan hasil Fase 1 selama itu membuat penelaah menunggu tanpa sebab.
    if (inWord && data.temuan.length > 0) {
      const hasil = await tandaiSemuaTemuan(data.temuan);
      setIdTidakDitandai(new Set(hasil.idTidakDitandai));
      const { ringkasan, peringatan: perlu } = ringkasPenandaan(hasil);
      setRingkasanPenandaan(ringkasan || null);
      if (perlu.length > 0) setPeringatan((prev) => [...prev, ...perlu]);
    } else {
      setRingkasanPenandaan(null);
      setIdTidakDitandai(new Set());
    }

    setHasilFase1({ jumlah: data.temuan.length, baris: data.jumlah_paragraf });
    return data.temuan;
  };

  /** Fase 2/3 — menit, sebagian berbayar. MENAMBAH temuan, tidak mengganti. */
  const jalankanFase2 = async (
    naskah: NaskahTerbaca,
    temuanFase1: Temuan[]
  ): Promise<void> => {
    setFase2Kemajuan(null);

    // Nomor Fase 2 MELANJUTKAN nomor terbesar yang sudah terpakai — (T3) sudah
    // tertulis di komentar Word, jadi menomori ulang membuat komentar itu
    // menunjuk temuan yang berbeda.
    const nomorTerakhir = temuanFase1.reduce((maks, t) => Math.max(maks, t.nomor), 0);

    const body: AnalisisLanjutRequest = {
      paragraf: naskah.paragraf,
      tabel_raksasa: naskah.tabel_raksasa,
      dokumen: namaDokumen,
      // Jawaban tahap 3 pekerjaan terakhir dipakai ulang HANYA untuk pesan
      // yang sama persis — naskah yang sudah berubah ditanyakan ulang. Yang
      // terputus di tengah jalan tidak dibayar dua kali.
      lanjutkan: nomorPekerjaan ?? undefined,
      aturan_aktif: [...aturanFase2Aktif],
      mulai_nomor: nomorTerakhir + 1,
      fase3:
        aturanFase2Aktif.has("F3-001") ||
        aturanFase2Aktif.has("F3-002") ||
        aturanFase2Aktif.has("F3-003"),
      temuan_fase1: temuanFase1,
    };

    const mulai = await fetch(`${API_BASE}/analisis/lanjut`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!mulai.ok) throw new Error(`Server merespons status ${mulai.status}`);
    const { pekerjaan }: MulaiResponse = await mulai.json();
    setNomorPekerjaan(pekerjaan);

    // Bertanya BERBATAS, bukan selamanya. Yang dianggap macet: kemajuan yang
    // DIAM selama BATAS_DIAM_MS — tahap, angka, dan jumlah panggilan tidak
    // bergerak sama sekali. Analisis yang lama tetapi bergerak ditunggu.
    let kemajuan: KemajuanResponse | null = null;
    let mandek = false;
    const mulaiTunggu = Date.now();
    let terakhirBergerak = Date.now();
    let jejakTerakhir = "";
    for (;;) {
      const kini = Date.now();
      if (kini - terakhirBergerak > BATAS_DIAM_MS || kini - mulaiTunggu > BATAS_TOTAL_MS) {
        mandek = true;
        break;
      }
      await new Promise((r) => setTimeout(r, JEDA_TANYA_MS));
      const res = await fetch(`${API_BASE}/analisis/lanjut/${pekerjaan}`);
      if (!res.ok) throw new Error(`Gagal membaca kemajuan (${res.status})`);
      kemajuan = await res.json();
      if (!kemajuan) break;
      const jejak = `${kemajuan.tahap}|${kemajuan.selesai}|${kemajuan.total}|${kemajuan.panggilan}`;
      if (jejak !== jejakTerakhir) {
        jejakTerakhir = jejak;
        terakhirBergerak = Date.now();
      }
      setFase2Kemajuan({
        tahap: kemajuan.tahap,
        selesai: kemajuan.selesai,
        total: kemajuan.total,
      });
      if (kemajuan.status === "selesai" || kemajuan.status === "gagal") break;
    }

    // Kegagalan Fase 2 masuk `pesanGalat`, BUKAN Rincian proses: Rincian
    // tertutup secara bawaan, dan kegagalan yang tersimpan di balik tombol
    // tertutup terbaca seolah analisisnya selesai dengan bersih.
    if (mandek) {
      setPesanGalat({
        teks:
          `Fase 2 macet — kemajuannya tidak bergerak ${Math.round(
            BATAS_DIAM_MS / 60000
          )} menit. Pekerjaan #${pekerjaan} mungkin masih berjalan di backend —` +
          ` periksa ${API_BASE}/analisis/lanjut/${pekerjaan}. Jawaban tahap 3 yang` +
          " sudah dibayar tetap tersimpan, jadi analisis ulang tidak mengulang dari nol.",
      });
      return;
    }
    if (!kemajuan) {
      setPesanGalat({ teks: "Fase 2 gagal: tidak ada jawaban dari backend." });
      return;
    }
    if (kemajuan.status === "gagal") {
      setPesanGalat({ teks: `Fase 2 gagal: ${kemajuan.pesan}` });
      return;
    }

    // Keberatan model atas temuan Fase 1. Temuannya TIDAK dihapus — yang
    // berubah cuma isi komentarnya, kini bertambah baris "Catatan AI:".
    const keberatan = kemajuan.keberatan ?? [];
    if (keberatan.length > 0) {
      const menurutId = new Map(keberatan.map((t) => [t.id, t.catatan_ai ?? ""]));
      setTemuanList((prev) =>
        prev.map((t) =>
          menurutId.has(t.id) ? { ...t, catatan_ai: menurutId.get(t.id) } : t
        )
      );
      if (inWord) {
        for (const t of keberatan) await perbaruiKomentarTemuan(t);
      }
    }

    // Fase 2 memilih diam — naskah KMK, naskah perubahan, atau strukturnya
    // tidak terbaca. Itu keadaan yang sah, dan alasannya disampaikan apa
    // adanya supaya penelaah tahu bagian mana yang tetap perlu diperiksa
    // sendiri. Sebagai PERINGATAN yang terbuka, bukan isi Rincian: Fase 2 yang
    // diam tanpa kabar terbaca sama dengan Fase 2 yang tidak menemukan apa-apa.
    if (kemajuan.temuan.length === 0 && kemajuan.pesan) {
      const alasanDiam = kemajuan.pesan;
      setPeringatan((prev) => [...prev, alasanDiam]);
      return;
    }

    // Ditandai PER KELOMPOK, bukan sekaligus — syarat ke-4 dari brief 8.7.
    if (inWord && kemajuan.temuan.length > 0) {
      const tidakDitandai: string[] = [];
      // Kelompoknya dipasang dari BAWAH naskah ke atas — sama dengan urutan di
      // dalam satu kelompok. Dari atas ke bawah, usulan hijau yang sudah
      // disisipkan kelompok sebelumnya menggeser letak temuan kelompok
      // berikutnya bila keduanya jatuh di paragraf yang sama, dan tandanya
      // bisa mendarat di kemunculan kata yang salah.
      const urut = [...kemajuan.temuan].sort(
        (a, b) =>
          a.lokasi.paragraf_index - b.lokasi.paragraf_index ||
          a.lokasi.offset_mulai - b.lokasi.offset_mulai
      );
      const kelompokan: Temuan[][] = [];
      for (let i = 0; i < urut.length; i += 10) kelompokan.push(urut.slice(i, i + 10));
      for (const kelompok of kelompokan.reverse()) {
        const hasil = await tandaiSemuaTemuan(kelompok);
        tidakDitandai.push(...hasil.idTidakDitandai);
        // Diurutkan menurut nomor supaya kartu tetap urut dokumen walaupun
        // kelompoknya tiba dari bawah.
        setTemuanList((prev) =>
          [...prev, ...kelompok].sort((a, b) => a.nomor - b.nomor)
        );
      }
      if (tidakDitandai.length > 0) {
        setIdTidakDitandai((prev) => new Set([...prev, ...tidakDitandai]));
      }
    } else {
      setTemuanList((prev) => [...prev, ...kemajuan!.temuan]);
    }

    const biaya =
      kemajuan.panggilan > 0
        ? ` ${kemajuan.panggilan} panggilan model, ${kemajuan.token_masuk}` +
          ` token masuk dan ${kemajuan.token_keluar} keluar.`
        : "";
    const catatanKeberatan =
      keberatan.length > 0
        ? ` ${keberatan.length} temuan Fase 1 dapat catatan keberatan dari AI.`
        : "";
    setFase2Pesan(
      (kemajuan.temuan.length === 0
        ? `Fase 2 selesai, tidak ada temuan.${biaya}`
        : `Fase 2 selesai: ${kemajuan.temuan.length} temuan ditambahkan.${biaya}`) +
        catatanKeberatan
    );
    // Angka terpisah untuk kepala Rincian proses — kalimat di atas terlalu
    // panjang untuk satu baris, tetapi jumlahnya wajib tetap terbaca walau
    // Rinciannya tertutup.
    setJumlahFase2(kemajuan.temuan.length);
  };

  /**
   * Fase 4 — SATU pekerjaan untuk seluruh pemeriksaan: bahan → agen →
   * gerbang. Semua tanda dipasang SESUDAH gerbang, di akhir; itu yang membuat
   * Batal bersih — sebelum gerbang selesai, naskah belum disentuh sama sekali.
   *
   * `ulang` terisi untuk Periksa ulang: temuan lama berikut keputusannya ikut
   * dikirim, nomor temuan baru melanjutkan nomor terakhir, dan offset temuan
   * baru dikembalikan ke teks sebenarnya di Word sebelum ditandai.
   */
  const jalankanAgen = async (
    naskah: NaskahTerbaca,
    jenis: JenisDokumen,
    ulang: { peta: PetaPeriksaUlang; temuanLama: Temuan[] } | null
  ): Promise<void> => {
    setPutaranAgen([]);
    setTahapAgen("");
    setMembatalkan(false);
    const lama = ulang?.temuanLama ?? [];
    const nomorTerakhir = lama.reduce((maks, t) => Math.max(maks, t.nomor), 0);
    const body: AnalisisAgenRequest = {
      paragraf: naskah.paragraf,
      halaman: naskah.halaman ?? [],
      tabel_raksasa: naskah.tabel_raksasa,
      dokumen: namaDokumen,
      jenis_dokumen: jenis,
      aturan_aktif: kodeAgenAktif,
      mulai_nomor: nomorTerakhir + 1,
      temuan_lama: lama,
      // Jawaban pekerjaan terakhir dipakai ulang HANYA untuk pesan yang sama
      // persis — yang terputus di tengah jalan tidak dibayar dua kali.
      lanjutkan: nomorPekerjaan ?? undefined,
    };
    const mulai = await fetch(`${API_BASE}/analisis/agen`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!mulai.ok) throw new Error(`Server merespons status ${mulai.status}`);
    const { pekerjaan }: MulaiResponse = await mulai.json();
    setNomorPekerjaan(pekerjaan);
    setPekerjaanAgen(pekerjaan);

    // Bertanya BERBATAS — yang dianggap macet: kemajuan yang DIAM selama
    // BATAS_DIAM_MS, sama dengan alur lama.
    let kemajuan: KemajuanAgenResponse | null = null;
    let mandek = false;
    try {
      const mulaiTunggu = Date.now();
      let terakhirBergerak = Date.now();
      let jejakTerakhir = "";
      for (;;) {
        const kini = Date.now();
        if (kini - terakhirBergerak > BATAS_DIAM_MS || kini - mulaiTunggu > BATAS_TOTAL_MS) {
          mandek = true;
          break;
        }
        await new Promise((r) => setTimeout(r, JEDA_TANYA_MS));
        const res = await fetch(`${API_BASE}/analisis/agen/${pekerjaan}`);
        if (!res.ok) throw new Error(`Gagal membaca kemajuan (${res.status})`);
        kemajuan = (await res.json()) as KemajuanAgenResponse;
        const jejak = [
          kemajuan.tahap,
          kemajuan.panggilan,
          ...kemajuan.putaran.map((p) => `${p.keadaan}:${p.langkah}:${p.calon}`),
        ].join("|");
        if (jejak !== jejakTerakhir) {
          jejakTerakhir = jejak;
          terakhirBergerak = Date.now();
        }
        setTahapAgen(kemajuan.tahap);
        setPutaranAgen(kemajuan.putaran);
        if (kemajuan.status === "selesai" || kemajuan.status === "gagal") break;
      }
    } finally {
      setPekerjaanAgen(null);
      setMembatalkan(false);
    }

    if (mandek) {
      setPesanGalat({
        teks:
          `Analisis macet — kemajuannya tidak bergerak ${Math.round(BATAS_DIAM_MS / 60000)} menit.` +
          ` Pekerjaan #${pekerjaan} mungkin masih berjalan di backend. Jawaban yang sudah` +
          " dibayar tersimpan, jadi analisis ulang tidak mengulang dari nol.",
      });
      return;
    }
    if (!kemajuan) {
      setPesanGalat({ teks: "Analisis gagal: tidak ada jawaban dari backend." });
      return;
    }
    if (kemajuan.status === "gagal") {
      setPesanGalat({ teks: `Analisis gagal: ${kemajuan.pesan}` });
      return;
    }
    const akhir = kemajuan;
    if (akhir.peringatan.length > 0) setPeringatan((prev) => [...prev, ...akhir.peringatan]);
    const biaya =
      akhir.panggilan > 0
        ? ` ${akhir.panggilan} request model, ${akhir.token_masuk.toLocaleString("id-ID")}` +
          ` token masuk dan ${akhir.token_keluar.toLocaleString("id-ID")} keluar.`
        : "";
    if (akhir.tahap === "dibatalkan") {
      setFase2Pesan(`Analisis dibatalkan penelaah — naskah tidak disentuh.${biaya}`);
      tampilkanToast("Analisis dibatalkan. Naskah tidak disentuh.");
      return;
    }
    if (akhir.temuan.length === 0) {
      // Diam yang sah (naskah perubahan, KMK, label gagal) disampaikan apa
      // adanya, supaya penelaah tahu bagian mana yang tetap diperiksa sendiri.
      if (akhir.pesan) setPeringatan((prev) => [...prev, akhir.pesan]);
      setFase2Pesan(`Analisis selesai, tidak ada temuan.${biaya}`);
      setJumlahFase2(0);
      return;
    }

    // Periksa ulang: offset dikembalikan ke teks sebenarnya di Word. Yang
    // rentangnya tidak bisa dipastikan tidak ditandai (CLAUDE.md butir 6).
    const tidakPasti = new Set<string>();
    let baru: Temuan[] = akhir.temuan.map((t) => {
      if (!ulang) return t;
      const k = keKoordinatNaskah(t, ulang.peta);
      if (k) return k;
      tidakPasti.add(t.id);
      return {
        ...t,
        catatan:
          `${t.catatan} (Letaknya di naskah yang sudah bertanda tidak bisa dipastikan —` +
          " tidak ditandai.)",
      };
    });

    const tidakDitandai = new Set<string>(tidakPasti);
    const terpasang: { id: string; sesudah: number }[] = [];
    if (inWord) {
      const dapatDitandai = baru.filter((t) => !tidakPasti.has(t.id));
      const hasil = await tandaiSemuaTemuan(dapatDitandai);
      hasil.idTidakDitandai.forEach((id) => tidakDitandai.add(id));
      // Sisipan PALING AKHIR, sesudah seluruh tanda lain terpasang —
      // paragraf baru menggeser nomor paragraf sesudahnya.
      const s = await pasangSisipan(
        dapatDitandai.filter((t) => t.sisipan && !tidakDitandai.has(t.id))
      );
      const pengganti = new Map(s.gagal.map((t) => [t.id, t]));
      baru = baru.map((t) => pengganti.get(t.id) ?? t);
      terpasang.push(...s.terpasang);

      const { ringkasan, peringatan: perlu } = ringkasPenandaan({
        ...hasil,
        komentarKosong: hasil.komentarKosong + s.komentarKosong,
      });
      const bagianSisipan = [
        s.terpasang.length > 0 ? `${s.terpasang.length} satuan baru disisipkan hijau` : "",
        s.gagal.length > 0
          ? `${s.gagal.length} sisipan gagal dipasang — komentarnya di tempat temuan, isinya di Saran`
          : "",
      ].filter(Boolean);
      setRingkasanPenandaan(
        [ringkasan, bagianSisipan.length > 0 ? bagianSisipan.join("; ") + "." : ""]
          .filter(Boolean)
          .join(" ") || null
      );
      if (perlu.length > 0) setPeringatan((prev) => [...prev, ...perlu]);
    }

    setTemuanList((prev) => {
      let semua = ulang ? [...prev, ...baru] : baru;
      // Tiap sisipan menggeser paragraf sesudahnya, URUT seperti dipasang
      // (dari bawah ke atas) — urutan itu yang membuat hitungannya benar.
      for (const { id, sesudah } of terpasang) {
        semua = geserParagraf(semua, sesudah, 1).map((t) =>
          t.id === id && t.sisipan ? { ...t, sisipan: { ...t.sisipan, paragraf: sesudah + 1 } } : t
        );
      }
      return [...semua].sort((a, b) => a.nomor - b.nomor);
    });
    setIdTidakDitandai((prev) => (ulang ? new Set([...prev, ...tidakDitandai]) : tidakDitandai));
    setFase2Pesan(
      `${ulang ? "Periksa ulang" : "Analisis"} selesai: ${akhir.temuan.length} temuan` +
        `${ulang ? " baru" : ""}.${biaya}`
    );
    setJumlahFase2(akhir.temuan.length);
  };

  /** Analisis agen dari awal — naskah belum bertanda. */
  const handleAnalisisAgen = async (jenis: JenisDokumen) => {
    if (inWord === true && (await periksaNaskah()) > 0) {
      tampilkanToast(
        "Naskah ini masih memuat tanda dari analisis sebelumnya. Bersihkan dulu," +
          " atau pakai Periksa ulang sesudah semua temuan diputuskan."
      );
      return;
    }
    setAnalyzing(true);
    kosongkanTahapan();
    try {
      const naskah = await bacaNaskahSekali({ format: true });
      if (naskah.paragraf.length === 0) {
        setPesanGalat({ teks: "Tidak ada teks atau paragraf yang dapat dibaca." });
        return;
      }
      if (naskah.tabel_raksasa.length > 0) {
        tampilkanToast(
          `${naskah.tabel_raksasa.length} tabel lebih dari 1.000 baris hanya dibaca` +
            " kerangkanya. Temuan sesudah tabel itu tampil di panel tanpa ditandai di naskah."
        );
      }
      setParagrafCount(naskah.paragraf.length);
      setFase2Berjalan(true);
      try {
        await jalankanAgen(naskah, jenis, null);
      } finally {
        setFase2Berjalan(false);
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setPesanGalat({ teks: `Gagal menjalankan analisis: ${errorMsg}` });
    } finally {
      setAnalyzing(false);
      await periksaNaskah();
    }
  };

  /**
   * Periksa ulang (Fase 4) — aktif bila SEMUA temuan sudah diputuskan. Naskah
   * dibaca sesudah keputusan (usulan yang diterima dianggap berlaku), temuan
   * lama berikut keputusannya dibaca agen, dan gerbang membuang calon yang
   * bertindihan dengan temuan lama. Tanda lama tidak disentuh.
   */
  const belumDiputuskan = temuanBerlokasi.filter((t) => t.status === "belum_ditinjau").length;
  const semuaDiputuskan = temuanBerlokasi.length > 0 && belumDiputuskan === 0;

  const handlePeriksaUlang = async () => {
    if (!jenisDokumen) {
      setGoyangJenis(true);
      setPesanGalat({ teks: "Pilih dulu PMK atau KMK sebelum menganalisis.", kunci: "jenis" });
      window.setTimeout(() => setGoyangJenis(false), 600);
      return;
    }
    if (!semuaDiputuskan || tidakAdaYangDicentang) return;
    setAnalyzing(true);
    kosongkanTahapan();
    try {
      const lama = temuanList;
      const { naskah, peta } = inWord
        ? await bacaNaskahSesudahKeputusan(lama)
        : { naskah: await bacaNaskahSekali({ format: true }), peta: new Map() as PetaPeriksaUlang };
      setParagrafCount(naskah.paragraf.length);
      setFase2Berjalan(true);
      try {
        await jalankanAgen(naskah, jenisDokumen, { peta, temuanLama: lama });
      } finally {
        setFase2Berjalan(false);
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setPesanGalat({ teks: `Gagal menjalankan Periksa ulang: ${errorMsg}` });
    } finally {
      setAnalyzing(false);
      await periksaNaskah();
    }
  };

  /**
   * Tombol Batal. Backend berhenti mengirim request baru; request yang sedang
   * berjalan selesai dulu. Naskah tidak tersentuh — belum ada tanda yang
   * dipasang sebelum gerbang selesai.
   */
  const handleBatal = async () => {
    if (pekerjaanAgen === null || membatalkan) return;
    setMembatalkan(true);
    try {
      const res = await fetch(`${API_BASE}/analisis/agen/${pekerjaanAgen}/batal`, {
        method: "POST",
      });
      if (!res.ok) throw new Error(`Server merespons status ${res.status}`);
      tampilkanToast(
        "Membatalkan — request yang sedang berjalan diselesaikan dulu, tidak ada request baru."
      );
    } catch (err: unknown) {
      setMembatalkan(false);
      setPesanGalat({
        teks: `Gagal membatalkan: ${err instanceof Error ? err.message : String(err)}`,
      });
    }
  };

  const handleAnalisis = async () => {
    // Jenis dokumen wajib dipilih dulu. Tanpa itu backend tidak tahu bunyi
    // baku mana yang dituntut pada butir Menimbang terakhir — "Peraturan
    // Menteri Keuangan" atau "Keputusan Menteri Keuangan".
    if (!jenisDokumen) {
      setGoyangJenis(true);
      setPesanGalat({
        teks: "Pilih dulu PMK atau KMK sebelum menganalisis.",
        kunci: "jenis",
      });
      window.setTimeout(() => setGoyangJenis(false), 600);
      return;
    }

    if (pakaiAgen) {
      if (tidakAdaYangDicentang) {
        setPesanGalat({
          teks:
            "Tidak ada analisis yang dinyalakan untuk jenis naskah ini — tidak ada yang" +
            " bisa diperiksa. Nyalakan setidaknya satu di Pengaturan.",
        });
        setShowPengaturan(true);
        return;
      }
      await handleAnalisisAgen(jenisDokumen);
      return;
    }

    const adaFase1 = aturanAktif.size > 0;
    const adaFase2 = aturanFase2Aktif.size > 0;
    if (!adaFase1 && !adaFase2) {
      setPesanGalat({
        teks:
          "Semua pemeriksaan dimatikan di Pengaturan — tidak ada yang bisa" +
          " diperiksa. Nyalakan setidaknya satu.",
      });
      setShowPengaturan(true);
      return;
    }

    // Naskahnya dihitung ULANG di sini, tidak cukup percaya hitungan terakhir:
    // penelaah bisa saja mencabut atau menambah tanda dengan tangan sejak itu.
    if (inWord === true && (await periksaNaskah()) > 0) {
      tampilkanToast(
        "Naskah ini masih memuat tanda dari analisis sebelumnya. Bersihkan dulu," +
          " supaya komentarnya tidak menumpuk."
      );
      return;
    }

    setAnalyzing(true);
    kosongkanTahapan();

    try {
      const naskah = await bacaNaskahSekali();
      if (naskah.paragraf.length === 0) {
        setPesanGalat({ teks: "Tidak ada teks atau paragraf yang dapat dibaca." });
        return;
      }
      if (naskah.tabel_raksasa.length > 0) {
        tampilkanToast(
          `${naskah.tabel_raksasa.length} tabel lebih dari 1.000 baris hanya dibaca` +
            " kerangkanya. Temuan sesudah tabel itu tampil di panel tanpa ditandai di naskah."
        );
      }

      const temuanFase1 = adaFase1
        ? await jalankanFase1(paragrafPasti(naskah), jenisDokumen)
        : [];
      if (adaFase2) {
        setFase2Berjalan(true);
        try {
          await jalankanFase2(naskah, temuanFase1);
        } finally {
          setFase2Berjalan(false);
        }
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setPesanGalat({ teks: `Gagal menjalankan analisis: ${errorMsg}` });
    } finally {
      setAnalyzing(false);
      await periksaNaskah();
    }
  };

  // ---------------------------------------------------------------------
  // ALAT PENGEMBANG — Ekspor Tahap 1 sampai 5
  // ---------------------------------------------------------------------
  //
  // Bukan fitur penelaah. Isinya apa yang BENAR-BENAR dibaca dan diputuskan
  // tiap tahap, tanpa tambahan (ditetapkan penelaah 27–28 Sep 2026):
  //
  //   Tahap 1   hasil parser — disusun dari naskah saat ini, gratis
  //   Tahap 2   perkiraan token, lalu bahan persis untuk AI — idem
  //   Tahap 3   pesan cari dugaan — yang disimpan analisis terakhir
  //   Tahap 4   pesan memastikan, berikut hasil alat — idem
  //   Tahap 5   nasib tiap dugaan, lolos atau gugur — idem
  //
  // Jalur unduhannya satu dan dipakai bersama: Blob + <a download>, dengan
  // jendela baru sebagai cadangan karena WebView2 Word kadang memblokir
  // unduhan. CLAUDE.md butir 9: didukung bukan berarti diizinkan.
  const unduhTeks = (teks: string, berkas: string): string => {
    const url = URL.createObjectURL(
      new Blob([teks], { type: "text/plain;charset=utf-8" })
    );
    try {
      const a = document.createElement("a");
      a.href = url;
      a.download = berkas;
      document.body.appendChild(a);
      a.click();
      a.remove();
      return `${berkas} diunduh — ${teks.length.toLocaleString("id-ID")} huruf.`;
    } catch {
      window.open(url, "_blank");
      return "Unduhan diblokir Word, jadi dibuka di jendela baru. Salin dari sana.";
    } finally {
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    }
  };

  const namaBerkas = (awalan: string) =>
    `${awalan}-${(namaDokumen || "naskah").replace(/\W+/g, "-")}.txt`;

  const eksporTahap = async (tahap: number) => {
    const catat = (pesan: string) =>
      setPesanEkspor((prev) => ({ ...prev, [tahap]: pesan }));
    setMengeksporTahap(tahap);
    setPesanEkspor((prev) => {
      const baru = { ...prev };
      delete baru[tahap];
      return baru;
    });
    try {
      let body: object;
      if (tahap <= 2) {
        // Tahap 1–2 disusun dari naskah SAAT INI.
        const naskah = await bacaNaskahSekali();
        if (naskah.paragraf.length === 0) {
          catat("Tidak ada paragraf yang dapat dibaca.");
          return;
        }
        body = {
          paragraf: naskah.paragraf,
          tabel_raksasa: naskah.tabel_raksasa,
          dokumen: namaDokumen,
          temuan_fase1: temuanList.filter((t) => t.fase === 1),
          aturan_aktif: [...aturanFase2Aktif],
        };
      } else {
        // Tahap 3–5: yang DISIMPAN backend saat analisis terakhir berjalan —
        // tidak disusun ulang dari naskah, yang sesudah ditandai sudah berisi
        // coretan dan usulan hijau. Karena itu naskahnya tidak dibaca di sini.
        body = { dokumen: namaDokumen, pekerjaan: nomorPekerjaan };
      }
      const res = await fetch(`${API_BASE}/analisis/tahap${tahap}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Server merespons status ${res.status}`);
      const teks = await res.text();
      // Jawaban yang bukan ekspor (tidak diawali garis "=====") adalah satu
      // kalimat keterangan — ditampilkan, tidak diunduh.
      catat(
        teks.startsWith("=====") ? unduhTeks(teks, namaBerkas(`tahap${tahap}`)) : teks.trim()
      );
    } catch (err: unknown) {
      catat(`Gagal mengekspor: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setMengeksporTahap(null);
    }
  };

  /**
   * Ekspor alat pengembang alur agen (Fase 4): bahan, jejak agen, gerbang.
   * Tahap 1 membawa naskah saat ini — dipakai backend bila belum ada analisis
   * untuk dokumen ini; selainnya backend memakai yang disimpan analisis
   * terakhir.
   */
  const eksporAgen = async (tahap: number) => {
    const catat = (pesan: string) => setPesanEkspor((prev) => ({ ...prev, [tahap]: pesan }));
    setMengeksporTahap(tahap);
    setPesanEkspor((prev) => {
      const baru = { ...prev };
      delete baru[tahap];
      return baru;
    });
    try {
      let body: object = { dokumen: namaDokumen, pekerjaan: nomorPekerjaan };
      if (tahap === 1) {
        const naskah = await bacaNaskahSekali({ format: true });
        body = {
          ...body,
          paragraf: naskah.paragraf,
          halaman: naskah.halaman ?? [],
          tabel_raksasa: naskah.tabel_raksasa,
        };
      }
      const res = await fetch(`${API_BASE}/analisis/agen/ekspor${tahap}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(`Server merespons status ${res.status}`);
      const teks = await res.text();
      catat(
        teks.startsWith("=====")
          ? unduhTeks(teks, namaBerkas(`agen-tahap${tahap}`))
          : teks.trim()
      );
    } catch (err: unknown) {
      catat(`Gagal mengekspor: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setMengeksporTahap(null);
    }
  };

  // Navigasi ke lokasi di dokumen
  const handleLompatKeLokasi = async (temuan: Temuan) => {
    setSelectedTemuanId(temuan.id);
    if (inWord) {
      await selectFindingLocation(temuan);
    }
  };

  // Terima temuan.
  //
  // NASKAHNYA SENGAJA TIDAK DISENTUH. Naskah kerja ini adalah dokumen
  // "coretan" yang dibawa ke rapat pembahasan bersama unit pemrakarsa —
  // coretan merah dan usulan hijaunya justru harus tetap terbaca di situ.
  // Versi bersih dibuat terpisah lewat ekspor, yang menerapkan hanya temuan
  // berstatus diterima. Yang membedakan sudah-diputuskan dari belum cukup
  // dari kartu di panel ini; itu keputusan penelaah, 17 Sep 2026.
  const handleTerima = async (temuan: Temuan) => {
    updateStatus(temuan.id, "diterima");
    tampilkanToast(
      `T${temuan.nomor} diterima. Coretan dan usulannya tetap di naskah kerja` +
        " — akan diterapkan saat ekspor versi bersih."
    );
  };

  // Tolak temuan: usulan hijaunya dibuang, teks aslinya dipulihkan persis
  // seperti sebelum ditandai, komentarnya dihapus. Tidak boleh ada bekas.
  const handleTolak = async (temuan: Temuan) => {
    updateStatus(temuan.id, "ditolak");
    if (!inWord) {
      tampilkanToast(`Status temuan T${temuan.nomor} diubah menjadi 'Ditolak'.`);
      return;
    }
    const { berhasil, sisipanDicabut } = await tolakTemuan(temuan);
    // Paragraf sisipan yang dicabut menggeser paragraf sesudahnya satu
    // langkah ke atas — nomor paragraf temuan lain ikut digeser.
    const letakSisipan = temuan.sisipan?.paragraf;
    if (sisipanDicabut && letakSisipan != null) {
      setTemuanList((prev) => geserParagraf(prev, letakSisipan, -1));
    }
    // Toast, BUKAN kotak peringatan yang menetap. Ditetapkan penelaah 27 Sep
    // 2026: kotak "tandanya tidak ditemukan" yang bertumpuk menenggelamkan
    // kartu. Penyebab utamanya — analisis di atas tanda lama — sudah ditutup
    // oleh kunci `naskahBertanda`, jadi kalimat ini mestinya nyaris tak pernah
    // muncul lagi.
    tampilkanToast(
      berhasil
        ? `T${temuan.nomor} ditolak. Naskah kembali seperti sebelum ditandai.`
        : `T${temuan.nomor} ditolak, tetapi tandanya tidak ketemu lagi di naskah — periksa sendiri.`
    );
    await periksaNaskah();
  };

  // Ubah status temuan
  const updateStatus = (id: string, newStatus: StatusTemuan) => {
    setTemuanList((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t))
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans antialiased text-xs">
      {/* Goyangan penanda "pilih jenis dokumen dulu". Ditulis sebagai CSS biasa
          supaya tidak bergantung pada konfigurasi animasi Tailwind. */}
      <style>{`
        @keyframes da-goyang {
          0%, 100% { transform: translateX(0); }
          20%      { transform: translateX(-5px); }
          40%      { transform: translateX(5px); }
          60%      { transform: translateX(-3px); }
          80%      { transform: translateX(3px); }
        }
        .da-goyang { animation: da-goyang 0.45s ease-in-out; }
        @keyframes da-muncul {
          from { opacity: 0; transform: translateY(4px); }
          to   { opacity: 1; transform: translateY(0); }
        }
        .da-muncul { animation: da-muncul 0.18s ease-out; }
        @media (prefers-reduced-motion: reduce) {
          .da-goyang, .da-muncul { animation: none; }
        }
      `}</style>

      {/* Top Header */}
      <header className="sticky top-0 z-30 bg-white border-b border-slate-200 px-3 py-2.5 shadow-xs">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-gradient-to-br from-blue-700 to-slate-900 flex items-center justify-center text-white font-bold text-[11px] shadow-xs">
              DA
            </div>
            <div>
              <h1 className="font-bold text-slate-800 text-[13px] tracking-tight leading-tight">
                Drafter Analiser
              </h1>
              <p className="text-[10px] text-slate-500 leading-none">
                {pakaiAgen
                  ? "Kemenkeu • Agen AI dengan skills (Fase 4)"
                  : "Kemenkeu • Kaidah Format Baku (Fase 1)"}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <button
              onClick={() => {
                setShowPengaturan(!showPengaturan);
                setShowDiagnostics(false);
              }}
              aria-expanded={showPengaturan}
              className={`p-1 rounded border transition ${
                showPengaturan
                  ? "bg-slate-800 border-slate-800 text-white"
                  : "border-slate-200 text-slate-600 hover:bg-slate-100"
              }`}
              title="Pengaturan — pilih pemeriksaan yang dijalankan"
            >
              <svg
                className="w-3.5 h-3.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                />
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                />
              </svg>
            </button>
            <button
              onClick={() => {
                setShowDiagnostics(!showDiagnostics);
                setShowPengaturan(false);
              }}
              className="text-[10px] px-2 py-0.5 rounded border border-slate-200 text-slate-600 hover:bg-slate-100 transition"
              title="Info Lingkungan & WordApi"
            >
              {inWord ? "Word Connected" : "Web Preview"}
            </button>
          </div>
        </div>

        {/* Panel Pengaturan — TIGA KATEGORI, disusun menurut urutan KMK 527.

            Dua gunanya sekaligus: mematikan aturan yang salah tandai tanpa
            menunggu kode diperbaiki, DAN memperlihatkan apa yang sebenarnya
            diperiksa tiap aturan supaya penelaah bisa mengeceknya manual.

            URUTANNYA MENGIKUTI NASKAH DARI ATAS KE BAWAH — judul, Menimbang,
            Mengingat, Menetapkan, baru batang tubuh — karena itulah urutan
            nomor butir KMK 527. Penelaah menelaah naskah dari atas ke bawah
            juga, jadi daftar ini bisa diikuti sambil membaca. */}
        {showPengaturan && pakaiAgen && (
          <div className="mt-2.5 p-2 bg-slate-100 rounded border border-slate-200 space-y-2">
            {/* ALUR AGEN (Fase 4) — daftarnya dibaca dari backend
                (analisis.md dan analisisformat.md), bukan dari berkas
                keterangan di frontend: formulir itulah yang dikirim ke agen,
                jadi yang tertulis di sini persis yang diperiksa. */}
            {(
              [
                ["isi", "Pemeriksaan isi naskah"],
                ["format", "Pemeriksaan format"],
              ] as const
            ).map(([kelompok, judul]) => {
              const daftar = daftarAgen.filter((a) => a.kelompok === kelompok);
              if (daftar.length === 0) return null;
              return (
                <div key={kelompok} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-slate-700 text-[11px]">{judul}</span>
                    <div className="flex items-center gap-2 text-[10px]">
                      <button
                        onClick={() =>
                          setAturanAgenAktif((prev) => {
                            const next = new Set(prev);
                            daftar.forEach((a) => next.add(a.id));
                            return next;
                          })
                        }
                        className="text-blue-700 hover:underline"
                      >
                        Pilih semua
                      </button>
                      <button
                        onClick={() =>
                          setAturanAgenAktif((prev) => {
                            const next = new Set(prev);
                            daftar.forEach((a) => next.delete(a.id));
                            return next;
                          })
                        }
                        className="text-slate-500 hover:underline"
                      >
                        Kosongkan
                      </button>
                    </div>
                  </div>
                  {daftar.map((a) =>
                    kartuAturan(keteranganDariPanel(a), aturanAgenAktif.has(a.id), (nyala) =>
                      setAturanAgenAktif((prev) => {
                        const next = new Set(prev);
                        if (nyala) next.add(a.id);
                        else next.delete(a.id);
                        return next;
                      })
                    )
                  )}
                </div>
              );
            })}

            <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
              {kodeAgenAktif.length} dari {daftarAgen.filter((a) => a.tersedia).length} analisis
              dinyalakan. Seluruhnya dikerjakan agen AI — berjalan beberapa menit dan
              berbiaya; tiap temuan lewat penilai kedua dan gerbang kode sebelum
              menyentuh naskah.
            </p>

            {/* ALAT PENGEMBANG alur agen — menggantikan ekspor tahap 1–5. */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-1.5">
              <span className="font-semibold text-slate-700 text-[11px]">Alat pengembang</span>
              {EKSPOR_AGEN.map(({ tahap, keterangan }) => (
                <div key={tahap} className="space-y-1 pt-1">
                  <p className="text-[10px] text-slate-500 leading-snug">
                    <strong>Tahap {tahap}</strong> — {keterangan}
                  </p>
                  <button
                    onClick={() => eksporAgen(tahap)}
                    disabled={mengeksporTahap !== null}
                    className={`w-full py-1.5 px-2 rounded text-[11px] font-medium border transition ${
                      mengeksporTahap !== null
                        ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                        : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                    }`}
                  >
                    {mengeksporTahap === tahap ? "Menyiapkan…" : `Ekspor Tahap ${tahap} (.txt)`}
                  </button>
                  {pesanEkspor[tahap] && (
                    <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                      {pesanEkspor[tahap]}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {showPengaturan && !pakaiAgen && (
          <div className="mt-2.5 p-2 bg-slate-100 rounded border border-slate-200 space-y-2">
            {/* KATEGORI 1 — Format Struktural.

                Berada di DUA himpunan state, dan itu disengaja. F1-001 s/d
                F1-012 lewat jalur cepat yang tidak butuh pohon satuan, jadi
                tetap berjalan pada KMK berdiktum dan naskah perubahan yang
                pohonnya gagal diurai. Empat sisanya menunggu pohon berhasil.
                Penelaah melihatnya sebagai SATU kategori; jalur pemanggilan
                di belakang layar tetap dua. */}
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-700 text-[11px]">
                Kategori 1 — Format Struktural
              </span>
              <div className="flex items-center gap-2 text-[10px]">
                <button
                  onClick={() => {
                    setAturanAktif(new Set(SEMUA_ID_AKTIF));
                    setKelompokFase2(ATURAN_STRUKTURAL_LANJUT, true);
                  }}
                  className="text-blue-700 hover:underline"
                >
                  Pilih semua
                </button>
                <button
                  onClick={() => {
                    setAturanAktif(new Set());
                    setKelompokFase2(ATURAN_STRUKTURAL_LANJUT, false);
                  }}
                  className="text-slate-500 hover:underline"
                >
                  Kosongkan
                </button>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 leading-snug">
              Deterministik — tanpa AI, gratis, dan hasilnya pasti. Klik nama
              pemeriksaan untuk melihat rinciannya.
            </p>

            {ATURAN_FASE1.map((aturan) =>
              kartuAturan(aturan, aturanAktif.has(aturan.id), (nyala) =>
                setAturanAktif((prev) => {
                  const next = new Set(prev);
                  if (nyala) next.add(aturan.id);
                  else next.delete(aturan.id);
                  return next;
                })
              )
            )}

            {ATURAN_STRUKTURAL_LANJUT.map((aturan) =>
              kartuAturan(aturan, aturanFase2Aktif.has(aturan.id), (nyala) =>
                setAturanFase2Aktif((prev) => {
                  const next = new Set(prev);
                  if (nyala) next.add(aturan.id);
                  else next.delete(aturan.id);
                  return next;
                })
              )
            )}

            <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
              {jumlahStrukturalAktif} dari{" "}
              {ATURAN_BISA_DIPILIH.length + ATURAN_STRUKTURAL_LANJUT.length}{" "}
              pemeriksaan format struktural dinyalakan.
              {jumlahStrukturalAktif === 0 &&
                " Tidak ada pemeriksaan format yang akan dijalankan."}
            </p>

            {/* KATEGORI 2 — Analisis Antar-Pasal (internal).
                Dipisah garis tebal karena sifatnya berbeda: memanggil model,
                berjalan menit, dan berbiaya. */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-[11px]">
                  Kategori 2 — Analisis Antar-Pasal
                </span>
                <div className="flex items-center gap-2 text-[10px]">
                  <button
                    onClick={() => setKelompokFase2(ATURAN_INTERNAL, true)}
                    className="text-blue-700 hover:underline"
                  >
                    Pilih semua
                  </button>
                  <button
                    onClick={() => setKelompokFase2(ATURAN_INTERNAL, false)}
                    className="text-slate-500 hover:underline"
                  >
                    Kosongkan
                  </button>
                </div>
              </div>

              <p className="text-[10px] text-slate-500 leading-snug">
                Makna kalimatnya harus dibaca, tidak bisa dibuktikan pola —
                jadi seluruhnya memakai AI: berjalan beberapa menit dan
                berbiaya. Temuannya penilaian, bukan kesalahan yang bisa
                ditunjuk barisnya; periksa sendiri sebelum menerima.
              </p>

              {ATURAN_INTERNAL.map((aturan) =>
                kartuAturan(aturan, aturanFase2Aktif.has(aturan.id), (nyala) =>
                  setAturanFase2Aktif((prev) => {
                    const next = new Set(prev);
                    if (nyala) next.add(aturan.id);
                    else next.delete(aturan.id);
                    return next;
                  })
                )
              )}
            </div>

            {/* KATEGORI 3 — Analisis Eksternal.
                Pembedanya SUMBER DATA, bukan mekanisme — F3-002 ada di sini
                walau tidak memakai AI sama sekali, karena yang ditanyainya
                tetap korpus di luar naskah. */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-[11px]">
                  Kategori 3 — Analisis Eksternal
                </span>
                <div className="flex items-center gap-2 text-[10px]">
                  <button
                    onClick={() => setKelompokFase2(ATURAN_EKSTERNAL, true)}
                    className="text-blue-700 hover:underline"
                  >
                    Pilih semua
                  </button>
                  <button
                    onClick={() => setKelompokFase2(ATURAN_EKSTERNAL, false)}
                    className="text-slate-500 hover:underline"
                  >
                    Kosongkan
                  </button>
                </div>
              </div>

              <p className="text-[10px] text-slate-500 leading-snug">
                Dibandingkan ke korpus peraturan JDIH. MATI secara bawaan
                karena isi korpusnya belum diverifikasi langsung —
                menyalakannya keputusan sadar penelaah, bukan bawaan yang
                tidak disadari.
              </p>

              {ATURAN_EKSTERNAL.map((aturan) =>
                kartuAturan(aturan, aturanFase2Aktif.has(aturan.id), (nyala) =>
                  setAturanFase2Aktif((prev) => {
                    const next = new Set(prev);
                    if (nyala) next.add(aturan.id);
                    else next.delete(aturan.id);
                    return next;
                  })
                )
              )}

              <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                {aturanFase2Aktif.size} dari {ATURAN_FASE2.length} pemeriksaan
                Kategori 1 lanjutan, 2, dan 3 dinyalakan.
                {aturanFase2Aktif.size === 0 &&
                  " Tidak ada pemeriksaan isi yang akan dijalankan."}
              </p>
            </div>

            {/* ---------------------------------------------------------
                ALAT PENGEMBANG — paling bawah, dipisah garis tebal.
                Bukan fitur penelaah: alat ini masih dalam pengembangan, dan
                ekspor ini dipakai programer melihat apa yang benar-benar
                dibaca dan diputuskan tiap tahap, sebagai acuan memperbaiki bug.
                --------------------------------------------------------- */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-1.5">
              <span className="font-semibold text-slate-700 text-[11px]">
                Alat pengembang
              </span>
              {EKSPOR_TAHAP.map(({ tahap, keterangan }) => (
                <div key={tahap} className="space-y-1 pt-1">
                  <p className="text-[10px] text-slate-500 leading-snug">
                    <strong>Tahap {tahap}</strong> — {keterangan}
                  </p>
                  <button
                    onClick={() => eksporTahap(tahap)}
                    disabled={mengeksporTahap !== null}
                    className={`w-full py-1.5 px-2 rounded text-[11px] font-medium border transition ${
                      mengeksporTahap !== null
                        ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                        : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                    }`}
                  >
                    {mengeksporTahap === tahap ? "Menyiapkan…" : `Ekspor Tahap ${tahap} (.txt)`}
                  </button>
                  {pesanEkspor[tahap] && (
                    <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                      {pesanEkspor[tahap]}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* WordApi Diagnostic Accordion */}
        {showDiagnostics && (
          <div className="mt-2.5 p-2 bg-slate-100 rounded border border-slate-200 text-[11px]">
            <div className="font-semibold text-slate-700 mb-1 flex items-center justify-between">
              <span>Status Kompatibilitas WordApi:</span>
              <span className="text-[10px] text-slate-500">
                {inWord ? "Host: Microsoft Word" : "Host: Web Browser"}
              </span>
            </div>
            {inWord ? (
              <div className="grid grid-cols-3 gap-1 text-center font-mono text-[10px]">
                {/* Seluruhnya WordApi. 1.1 = penandaan, 1.3 = cakupan
                    terpilih, 1.4 = komentar dan changeTrackingMode. */}
                {apiChecks.map(({ version, supported }) => (
                  <div
                    key={version}
                    className={`py-1 rounded border ${
                      supported
                        ? "bg-emerald-50 border-emerald-300 text-emerald-800"
                        : "bg-rose-50 border-rose-300 text-rose-800"
                    }`}
                  >
                    <div>v{version}</div>
                    <div className="font-bold">{supported ? "✓" : "✗"}</div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-amber-800 bg-amber-50 p-1.5 rounded border border-amber-200 text-[10px]">
                Menjalankan dalam mode pratinjau web. Anda dapat menguji seluruh fungsi telaah draf dengan teks simulasi di bawah.
              </p>
            )}
          </div>
        )}
      </header>

      {/* Main Container */}
      <main className="flex-1 p-3 space-y-3">
        {/* Web Mode Input Card */}
        {!inWord && (
          <div className="bg-white p-2.5 rounded-lg border border-blue-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-blue-900 text-[11px] flex items-center gap-1">
                <span className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></span>
                Draf Uji Coba (Simulasi Paragraf Dokumen)
              </span>
              <button
                onClick={() => setUseWebCustomText(!useWebCustomText)}
                className="text-[10px] text-blue-600 hover:underline"
              >
                {useWebCustomText ? "Gunakan Draf Standar" : "Ketik Naskah Sendiri"}
              </button>
            </div>
            {useWebCustomText ? (
              <textarea
                value={webInputText}
                onChange={(e) => setWebInputText(e.target.value)}
                rows={5}
                className="w-full p-2 border border-slate-300 rounded font-mono text-[10px] text-slate-800 focus:outline-blue-500"
                placeholder="Tempelkan draf peraturan per baris di sini..."
              />
            ) : (
              <div className="text-[10px] text-slate-600 bg-slate-50 p-2 rounded border border-slate-200 font-mono max-h-24 overflow-y-auto whitespace-pre-wrap">
                {webInputText}
              </div>
            )}
          </div>
        )}

        {/* Action & Controls Bar */}
        <div className="bg-white p-2.5 rounded-lg border border-slate-200 shadow-xs space-y-2">
          {/* Jenis dokumen dipilih penelaah. Alat tidak menebaknya: bagian
              Mengingat sebuah KMK lazim menyebut "Peraturan Menteri Keuangan",
              sehingga tebakan bisa keliru lalu menuntut bunyi frasa yang salah.
              Lihat docs/fase1 drafter.md bagian 6.7. */}
          <div
            className={`flex items-center justify-between pb-2 border-b text-[11px] rounded px-1 -mx-1 transition-colors ${
              goyangJenis
                ? "da-goyang border-rose-300 bg-rose-50"
                : "border-slate-100"
            }`}
          >
            <span
              className={`font-medium ${
                jenisDokumen ? "text-slate-600" : "text-rose-700"
              }`}
            >
              Jenis Dokumen:{!jenisDokumen && " pilih dulu"}
            </span>
            <div className="inline-flex rounded-md shadow-2xs">
              {(["PMK", "KMK"] as const).map((jenis, i) => (
                <button
                  key={jenis}
                  type="button"
                  onClick={() => {
                    setJenisDokumen(jenis);
                    // Galat "pilih dulu PMK atau KMK" sudah terjawab — jangan
                    // biarkan menetap sebagai galat basi. Galat lain tidak
                    // disentuh.
                    setPesanGalat((g) => (g?.kunci === "jenis" ? null : g));
                  }}
                  className={`px-3 py-1 text-[10px] font-semibold border ${
                    i === 0 ? "rounded-l" : "rounded-r border-l-0"
                  } ${
                    jenisDokumen === jenis
                      ? "bg-slate-800 text-white border-slate-800"
                      : jenisDokumen === null
                      ? "bg-white text-slate-700 border-rose-300 hover:bg-rose-50"
                      : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  {jenis}
                </button>
              ))}
            </div>
          </div>

          {inWord && (
            <div className="flex items-center justify-between pb-2 border-b border-slate-100 text-[11px]">
              <span className="text-slate-600 font-medium">Cakupan Dokumen:</span>
              <div className="inline-flex rounded-md shadow-2xs">
                <button
                  type="button"
                  onClick={() => setScope("all")}
                  className={`px-2.5 py-1 text-[10px] font-medium rounded-l border ${
                    scope === "all"
                      ? "bg-blue-600 text-white border-blue-600"
                      : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  Seluruh Naskah
                </button>
                {/* Dinonaktifkan bila Word-nya tidak punya WordApi 1.3.
                    Cakupan ini memanggil Range.intersectWithOrNullObject(),
                    dan requirement set didukung tidak sama dengan fitur
                    diizinkan — jalur cadangannya menolak lebih dulu, bukan
                    gagal di tengah jalan. */}
                <button
                  type="button"
                  disabled={!bisaCakupanTerpilih}
                  onClick={() => setScope("selection")}
                  title={
                    bisaCakupanTerpilih
                      ? undefined
                      : "Word ini belum mendukung cakupan terpilih (butuh WordApi 1.3)"
                  }
                  className={`px-2.5 py-1 text-[10px] font-medium rounded-r border-t border-b border-r ${
                    !bisaCakupanTerpilih
                      ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                      : scope === "selection"
                      ? "bg-blue-600 text-white border-blue-600"
                      : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  Bagian Terpilih
                </button>
              </div>
            </div>
          )}

          {/* SATU TOMBOL. Apa yang dijalankan ditentukan panel Pengaturan —
              penelaah mencentang apa yang ingin diperiksa, alat yang mengurus
              urutan fasenya.

              Analisis ulang ditolak selama NASKAHNYA masih memuat tanda alat:
              tiap analisis memasang komentar baru, dan pada pengujian 17 Sep
              2026 dokumen contoh berakhir dengan ~18 komentar untuk 5 temuan.
              Lihat docs/fase1 drafter.md bagian 6.5 dan `naskahBertanda`. */}
          <button
            onClick={handleAnalisis}
            disabled={analyzing || naskahBertanda || tidakAdaYangDicentang}
            title={
              tidakAdaYangDicentang
                ? "Tidak ada pemeriksaan yang dicentang di Pengaturan"
                : naskahBertanda
                  ? "Naskah masih memuat tanda dari analisis sebelumnya — bersihkan dulu, supaya komentarnya tidak menumpuk"
                  : undefined
            }
            className={`w-full py-2 px-3 rounded font-semibold text-white transition flex items-center justify-center gap-1.5 shadow-xs ${
              analyzing || naskahBertanda || tidakAdaYangDicentang
                ? "bg-blue-400 cursor-not-allowed"
                : "bg-blue-700 hover:bg-blue-800 active:scale-[0.99]"
            }`}
          >
            {analyzing ? (
              <>
                <svg className="animate-spin h-3.5 w-3.5 text-white" viewBox="0 0 24 24" fill="none">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z" />
                </svg>
                <span>
                  {pakaiAgen
                    ? uraiTahapAgen(tahapAgen, putaranAgen, fase2Berjalan)
                    : !fase2Berjalan
                      ? "Memeriksa format baku…"
                      : fase2Kemajuan && fase2Kemajuan.total > 0
                        ? `Tahap ${uraiKemajuan(fase2Kemajuan).replace(/^tahap /, "")}…`
                        : "Membaca struktur naskah…"}
                </span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <span>Jalankan Analisis</span>
              </>
            )}
          </button>

          {/* Apa yang akan dijalankan, dibaca dari Pengaturan. Tanpa baris ini
              penelaah tidak punya cara tahu isi tombolnya tanpa membuka
              Pengaturan dulu. */}
          <div className="text-[10px] text-slate-500 px-0.5">
            {tidakAdaYangDicentang ? (
              <span className="text-amber-800">
                Tidak ada pemeriksaan yang dicentang.{" "}
                <button
                  onClick={() => setShowPengaturan(true)}
                  className="underline font-medium hover:text-amber-950"
                >
                  Buka Pengaturan
                </button>
              </span>
            ) : pakaiAgen ? (
              <>
                Akan dijalankan: {kodeAgenAktif.length} analisis oleh agen AI
                <span className="text-slate-400"> &middot; berjalan beberapa menit</span>
              </>
            ) : (
              <>
                Akan dijalankan:{" "}
                {[
                  aturanAktif.size > 0 ? `${aturanAktif.size} format baku` : null,
                  aturanFase2Aktif.size > 0
                    ? `${aturanFase2Aktif.size} pemeriksaan isi`
                    : null,
                ]
                  .filter(Boolean)
                  .join(" + ")}
                {aturanFase2Aktif.size > 0 && (
                  <span className="text-slate-400"> &middot; berjalan beberapa menit</span>
                )}
              </>
            )}
          </div>

          {/* KEMAJUAN PER PUTARAN dan tombol BATAL (Fase 4) — terlihat selama
              analisis berjalan, supaya penelaah tahu apa yang sedang
              dikerjakan dan apa yang dibatalkan bila ia menekan Batal. Batal
              bersih: belum ada tanda yang dipasang sebelum gerbang selesai. */}
          {pakaiAgen && analyzing && (putaranAgen.length > 0 || pekerjaanAgen !== null) && (
            <div className="space-y-1">
              {putaranAgen.length > 0 && (
                <ol className="text-[10px] text-slate-600 space-y-0.5 border-l-2 border-slate-200 pl-2">
                  {putaranAgen.map((p) => (
                    <li key={p.kode} className="flex items-baseline justify-between gap-2">
                      <span className="truncate">{p.judul}</span>
                      <span
                        className={`shrink-0 ${
                          p.keadaan === "selesai"
                            ? "text-emerald-700"
                            : p.keadaan === "macet" || p.keadaan === "gagal"
                              ? "text-rose-700"
                              : "text-slate-500"
                        }`}
                      >
                        {KEADAAN_PUTARAN[p.keadaan] ?? p.keadaan}
                        {p.langkah > 0 ? ` · ${p.langkah} langkah` : ""}
                        {p.calon > 0 ? ` · ${p.calon} calon` : ""}
                      </span>
                    </li>
                  ))}
                </ol>
              )}
              {pekerjaanAgen !== null && (
                <button
                  type="button"
                  onClick={handleBatal}
                  disabled={membatalkan}
                  className={`w-full text-[10px] py-1 px-2 rounded border font-medium transition ${
                    membatalkan
                      ? "border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed"
                      : "border-rose-300 bg-rose-50 text-rose-800 hover:bg-rose-100"
                  }`}
                  title="Berhenti mengirim request baru. Naskah tidak disentuh."
                >
                  {membatalkan ? "Membatalkan…" : "Batal"}
                </button>
              )}
            </div>
          )}

          {/* RINCIAN PROSES — tertutup secara bawaan (ditetapkan penelaah
              27 Sep 2026). Tahap yang sedang berjalan sudah terbaca di tombol
              Analisis; yang di sini cuma rinciannya. Kepalanya tetap menyebut
              hasil tiap tahap, jadi rinciannya boleh tertutup tanpa ada hasil
              yang hilang dari pandangan. */}
          {adaRincian && (
            <div className="text-[10px]">
              <button
                type="button"
                onClick={() => setRincianTerbuka((v) => !v)}
                aria-expanded={rincianTerbuka}
                aria-controls="rincian-proses"
                className="w-full text-left text-slate-500 hover:text-slate-800 leading-snug"
              >
                <span aria-hidden="true" className="inline-block w-2.5">
                  {rincianTerbuka ? "▾" : "▸"}
                </span>
                <span className="font-medium">Rincian proses</span>
                {ringkasTahap && (
                  <span className="text-slate-400"> &middot; {ringkasTahap}</span>
                )}
              </button>

              {rincianTerbuka && (
                <ol
                  id="rincian-proses"
                  className="mt-1.5 ml-1 space-y-1.5 border-l-2 border-slate-200 pl-2 text-slate-600 leading-snug"
                >
                  {hasilFase1 && (
                    <li>
                      <span className="font-medium text-slate-700">
                        Format baku (Fase 1):
                      </span>{" "}
                      {hasilFase1.jumlah === 0
                        ? `tidak ditemukan ketidaksesuaian pada ${hasilFase1.baris} baris.`
                        : `${hasilFase1.jumlah} temuan pada ${hasilFase1.baris} baris.`}
                    </li>
                  )}
                  {ringkasanPenandaan && (
                    <li>
                      <span className="font-medium text-slate-700">
                        {pakaiAgen ? "Penandaan di naskah:" : "Penandaan di naskah (Fase 1):"}
                      </span>{" "}
                      {ringkasanPenandaan}
                    </li>
                  )}
                  {adaFase2Kemajuan && fase2Kemajuan && (
                    <li className="space-y-1">
                      <div>
                        <span className="font-medium text-slate-700">
                          Pemeriksaan isi (Fase 2):
                        </span>{" "}
                        {uraiKemajuan(fase2Kemajuan)}.
                      </div>
                      <div className="h-1 w-full bg-slate-200 rounded overflow-hidden">
                        <div
                          className="h-full bg-blue-600 transition-all"
                          style={{
                            width: `${Math.min(
                              100,
                              Math.round(
                                (fase2Kemajuan.selesai / fase2Kemajuan.total) * 100
                              )
                            )}%`,
                          }}
                        />
                      </div>
                    </li>
                  )}
                  {pakaiAgen && !analyzing && putaranAgen.length > 0 && (
                    <li className="space-y-0.5">
                      <span className="font-medium text-slate-700">Putaran agen:</span>
                      <ul className="ml-1 space-y-0.5">
                        {putaranAgen.map((p) => (
                          <li key={p.kode}>
                            {p.judul} — {KEADAAN_PUTARAN[p.keadaan] ?? p.keadaan}
                            {p.langkah > 0 ? `, ${p.langkah} langkah` : ""}
                            {p.calon > 0 ? `, ${p.calon} calon` : ""}
                          </li>
                        ))}
                      </ul>
                    </li>
                  )}
                  {fase2Pesan && <li className="wrap-break-word">{fase2Pesan}</li>}
                </ol>
              )}
            </div>
          )}

          {/* GALAT — tidak pernah hilang sendiri. Ditutup penelaah, atau
              dikosongkan saat analisis berikutnya dimulai. */}
          {pesanGalat && (
            <div
              role="alert"
              className="text-[10px] text-rose-900 bg-rose-50 px-2 py-1.5 rounded border border-rose-200 flex items-start gap-1.5"
            >
              <span className="flex-1 min-w-0 wrap-break-word">{pesanGalat.teks}</span>
              <button
                type="button"
                onClick={() => setPesanGalat(null)}
                aria-label="Tutup pesan galat"
                title="Tutup"
                className="shrink-0 text-rose-400 hover:text-rose-700 leading-none text-sm -mt-0.5"
              >
                &times;
              </button>
            </div>
          )}

          {/* PERINGATAN — hal yang menuntut tindakan. Menetap, bisa ditutup
              satu per satu. */}
          {peringatan.map((teks, i) => (
            <div
              key={`${i}:${teks}`}
              role="status"
              className="text-[10px] text-amber-900 bg-amber-50 px-2 py-1.5 rounded border border-amber-200 flex items-start gap-1.5"
            >
              <span aria-hidden="true" className="text-amber-600 font-bold leading-none">
                &#9888;
              </span>
              <span className="flex-1 min-w-0 wrap-break-word">{teks}</span>
              <button
                type="button"
                onClick={() =>
                  setPeringatan((prev) => prev.filter((_, j) => j !== i))
                }
                aria-label="Tutup peringatan"
                title="Tutup"
                className="shrink-0 text-amber-500 hover:text-amber-800 leading-none text-sm -mt-0.5"
              >
                &times;
              </button>
            </div>
          ))}

          {/* Cukup TOMBOLNYA — ditetapkan penelaah 27 Sep 2026. Kalimat
              penjelasnya dulu ikut menumpuk di atas kartu; alasan kuncinya
              kini dibaca di tooltip tombol Analisis. Tampil selama naskah
              masih bertanda, juga ketika daftarnya kosong (panel baru dibuka
              di atas naskah bertanda) — dulu justru saat itu tombol ini
              hilang, dan tanda lama tidak bisa dicabut dari panel. */}
          {/* PERIKSA ULANG (Fase 4) — aktif bila semua temuan sudah
              diputuskan. Naskah dibaca sesudah keputusan; agen membaca temuan
              lama berikut keputusannya dan mencari yang terlewat. Tanda lama
              tidak disentuh. */}
          {pakaiAgen && temuanBerlokasi.length > 0 && !analyzing && (
            <button
              type="button"
              onClick={handlePeriksaUlang}
              disabled={!semuaDiputuskan || tidakAdaYangDicentang}
              title={
                semuaDiputuskan
                  ? "Analisis lagi naskah sesudah keputusan — mencari yang terlewat, tanpa mengulang temuan lama"
                  : "Aktif bila semua temuan sudah diputuskan (Terima / Tolak)"
              }
              className={`w-full text-[10px] py-1 px-2 rounded border font-medium transition ${
                !semuaDiputuskan || tidakAdaYangDicentang
                  ? "border-slate-200 bg-slate-100 text-slate-400 cursor-not-allowed"
                  : "border-blue-300 bg-blue-50 text-blue-800 hover:bg-blue-100"
              }`}
            >
              {semuaDiputuskan
                ? "Periksa ulang"
                : `Periksa ulang — ${belumDiputuskan} temuan belum diputuskan`}
            </button>
          )}

          {tampilBersihkan && !analyzing && (
            <button
              type="button"
              onClick={handleBersihkanDaftar}
              className={`w-full text-[10px] py-1 px-2 rounded border font-medium transition ${
                yakinBersihkan
                  ? "border-rose-300 bg-rose-50 text-rose-800 hover:bg-rose-100"
                  : "border-amber-300 bg-amber-50 text-amber-900 hover:bg-amber-100"
              }`}
            >
              {yakinBersihkan
                ? temuanList.length === 0
                  ? "Semua tanda alat di naskah ikut dicabut — klik sekali lagi"
                  : "Usulan yang sudah diterima ikut dicabut — klik sekali lagi"
                : "Bersihkan daftar dan mulai dari awal"}
            </button>
          )}
        </div>

        {/* Kotak Gate Legal dibuang 27 Sep 2026 atas permintaan penelaah —
            ia ikut menenggelamkan kartu, dan uraiannya keliru menyebut OCR.
            CLAUDE.md butir 3 tetap terpenuhi lewat lencana "rujukan belum
            diverifikasi" dan "dasar turunan" di TIAP kartu yang bersangkutan. */}

        {/* Ringkasan hasil */}
        {temuanList.length > 0 && (
          <div className="flex items-center justify-between text-[10px] text-slate-500 px-1">
            <span>
              {stats.total} temuan &bull; {paragrafCount} paragraf diperiksa
            </span>
            <span>
              {stats.diterima > 0 && (
                <span className="text-emerald-700 font-semibold">
                  {stats.diterima} diterima{" "}
                </span>
              )}
              {stats.ditolak > 0 && (
                <span className="text-slate-500 line-through">
                  {stats.ditolak} ditolak
                </span>
              )}
            </span>
          </div>
        )}

        {/* Finding Cards List */}
        {/* Peringatan dokumen — temuan yang tidak punya lokasi di naskah.
            Sebaris, bukan kartu: tidak ada yang bisa dilompati maupun
            diputuskan. */}
        {peringatanDokumen.length > 0 && (
          <div className="bg-rose-50 border border-rose-300 text-rose-900 px-2.5 py-2 rounded-lg text-[11px] leading-snug space-y-1">
            {peringatanDokumen.map((t) => (
              <div key={t.id} className="flex items-start gap-1.5">
                <span className="text-rose-600 font-bold leading-none">
                  &#9888;
                </span>
                {/* Dipotong dua baris, dibentangkan lewat tombol.

                    Blok ini menggambar `catatan` apa adanya, dan pada
                    27 Sep 2026 sebuah F1-002 yang pengambilan judulnya
                    kebablasan mengisinya dengan SEMBILAN HALAMAN peraturan.
                    Akarnya sudah ditambal di backend (batas 60 kata pada
                    judul pembuka), tetapi jalur gambarnya sendiri tetap tidak
                    boleh tak berbatas — aturan lain bisa meledak dengan cara
                    yang sama, dan panel tidak boleh ikut hancur karenanya. */}
                <span className="min-w-0">
                  <span
                    className={
                      alasanTerbuka.has(t.id) ? "" : "line-clamp-2 block"
                    }
                  >
                    {t.catatan}
                  </span>
                  <button
                    onClick={() => bentangkanAlasan(t.id)}
                    className="mt-0.5 text-rose-700 hover:text-rose-900 underline underline-offset-2"
                  >
                    {alasanTerbuka.has(t.id) ? "ringkas" : "selengkapnya"}
                  </button>
                </span>
              </div>
            ))}
          </div>
        )}

        <div className="space-y-1.5">
          {temuanBerlokasi.slice(0, batasTampil).map((temuan) => {
            const isSelected = selectedTemuanId === temuan.id;
            // Tiga keadaan, bukan dua. "turunan" berarti butirnya SUDAH
            // dibaca manusia dari naskah KMK 527 — yang perlu ditimbang cuma
            // apakah aturannya memang akibat wajar butir itu. Menyamakannya
            // dengan "belum diverifikasi" membuang keterangan yang sudah
            // diperiksa, dan membuat penelaah mengabaikan keduanya sekaligus.
            const rujukanTurunan = temuan.rujukan.status === "turunan";
            // Fase 4: dasar prioritas penelaah dan rujukan yang tidak terbukti
            // ("tanpa") tidak punya baris rujukan — tidak ada yang perlu
            // diverifikasi, jadi tidak berlencana. Rujukan yang dicarikan agen
            // ("agen") tetap "belum diverifikasi" sampai disalin ke Dasar.
            const isPlaceholderRujukan = !["visual", "turunan", "prioritas", "tanpa"].includes(
              temuan.rujukan.status ?? "placeholder"
            );
            // Penjelasan temuan TIDAK diulang di sini — tempatnya di komentar
            // Word, di titik kesalahannya (bagian 6.6). Panel hanya navigasi.
            const cuplikan = temuan.lokasi.teks_asli.trim();
            const ringkas =
              cuplikan.length > 70 ? cuplikan.slice(0, 70) + "\u2026" : cuplikan;
            // Temuan tanpa tanda di naskah: tidak ada komentar yang bisa dibaca
            // di sana, jadi alasannya HARUS muncul di kartu ini. Tombol
            // Terima/Tolak TETAP ditampilkan \u2014 kartu yang bentuknya
            // berubah-ubah membuat daftar sulit dibaca sekilas, dan itu sudah
            // ditolak penelaah sekali (bagian 6.13).
            const tanpaTanda = tidakTertandai(temuan);

            return (
              <div
                key={temuan.id}
                // Dipakai pemantau seleksi untuk menggulir kartunya ke layar.
                id={`kartu-${temuan.id}`}
                className={`bg-white rounded border border-slate-200 px-2.5 py-2 space-y-1.5 transition ${
                  isSelected ? "ring-2 ring-blue-500/40" : ""
                } ${temuan.status !== "belum_ditinjau" ? "opacity-60" : ""}`}
              >
                <div className="flex items-center gap-1.5">
                  <span className="font-mono font-bold text-slate-800 text-[11px] bg-slate-100 px-1.5 py-0.5 rounded">
                    T{temuan.nomor}
                  </span>
                  {/* TIGA label, bukan dua. Sampai 27 Sep 2026 kartunya cuma
                      mengenal "usulan" dan "catatan", sehingga temuan
                      `penghapusan` — merah dicoret TANPA sisipan hijau —
                      dilabeli "catatan" berikut keterangan "diberi blok
                      kuning". Keterangan yang bohong: penelaah membaca kartu
                      yang menjanjikan sorotan kuning lalu menemukan coretan
                      merah di naskahnya. */}
                  <span
                    className={`text-[9px] font-medium px-1.5 py-0.5 rounded border ${
                      temuan.jenis_tanda === "penggantian"
                        ? "bg-sky-50 text-sky-700 border-sky-200"
                        : temuan.jenis_tanda === "penghapusan"
                          ? "bg-rose-50 text-rose-700 border-rose-200"
                          : "bg-amber-50 text-amber-800 border-amber-200"
                    }`}
                    title={
                      temuan.sisipan
                        ? `Perbaikannya satuan baru yang disisipkan hijau di ${temuan.sisipan.sasaran}` +
                          ` (sumber: ${temuan.sisipan.sumber}); di tempat temuan teksnya cuma disorot, tanpa komentar`
                        : temuan.jenis_tanda === "penggantian"
                          ? "Teks lama merah dicoret, usulan penggantinya hijau di sebelahnya"
                          : temuan.jenis_tanda === "penghapusan"
                            ? "Teks lama merah dicoret TANPA pengganti — perbaikannya membuang. Yang menghapus tetap penelaah."
                            : temuan.tanpa_sorot
                              ? "Komentar menempel di kata terdekat yang terlihat, TIDAK diberi warna sorot — yang dipersoalkan tidak bisa disorot (ketiadaan, teks tersembunyi, atau butir kosong)"
                              : "Diberi blok kuning sebagai peringatan — perbaikannya ditentukan penelaah"
                    }
                  >
                    {temuan.sisipan || temuan.jenis_tanda === "penggantian"
                      ? "usulan"
                      : temuan.jenis_tanda === "penghapusan"
                        ? "dibuang"
                        : "catatan"}
                  </span>
                  {/* Kode analisisnya — rancangan Fase 4 bagian 3.3: penelaah
                      membaca rinciannya di Pengaturan dengan kode yang sama. */}
                  {pakaiAgen && (
                    <span className="text-[8px] font-mono bg-slate-100 text-slate-600 px-1 rounded">
                      {temuan.aturan_id}
                    </span>
                  )}
                  {/* Fase ditunjukkan, bukan dipakai menomori ulang. Penelaah
                      berhak tahu temuan mana yang kesalahannya bisa dibuktikan
                      baris demi baris (Fase 1) dan mana yang hasil penalaran
                      model (Fase 2/3) — cara memeriksanya memang berbeda. */}
                  {!pakaiAgen && temuan.fase > 1 && (
                    <span
                      className={`text-[8px] px-1 rounded font-bold ${
                        temuan.fase === 3
                          ? "bg-violet-200 text-violet-900"
                          : "bg-blue-100 text-blue-800"
                      }`}
                      title={
                        temuan.fase === 3
                          ? "Fase 3 — dibandingkan dengan peraturan lain dari korpus"
                          : "Fase 2 — pemeriksaan isi"
                      }
                    >
                      Fase {temuan.fase}
                    </span>
                  )}
                  {tanpaTanda && (
                    <span className="text-[8px] bg-slate-200 text-slate-700 px-1 rounded font-bold">
                      tidak ditandai di naskah
                    </span>
                  )}
                  {/* Satu kesalahan yang terulang = satu kartu (27 Sep 2026).
                      Cukup lencana; daftar tempatnya ada di tooltip dan di
                      baris "Juga di" komentar Word — kartu tetap ringkas. */}
                  {(temuan.juga_di?.length ?? 0) > 0 && (
                    <span
                      className="text-[8px] bg-sky-100 text-sky-800 px-1 rounded font-bold"
                      title={`Kesalahan yang sama juga di: ${temuan.juga_di!.join("; ")}`}
                    >
                      +{temuan.juga_di!.length} tempat lain
                    </span>
                  )}
                  {isPlaceholderRujukan && (
                    <span className="text-[8px] bg-amber-200 text-amber-900 px-1 rounded font-bold">
                      rujukan belum diverifikasi
                    </span>
                  )}
                  {rujukanTurunan && (
                    <span
                      className="text-[8px] bg-slate-200 text-slate-700 px-1 rounded font-bold"
                      title={
                        `${temuan.rujukan.sumber} butir ${temuan.rujukan.butir}` +
                        " sudah dibaca dari naskah KMK 527, tetapi aturan ini" +
                        " akibat butir itu — bukan bunyinya. Timbang sendiri" +
                        " apakah turunannya sah."
                      }
                    >
                      dasar turunan
                    </span>
                  )}
                  {temuan.status === "diterima" && (
                    <span className="ml-auto text-emerald-700 text-[9px] font-medium">
                      diterima
                    </span>
                  )}
                  {temuan.status === "ditolak" && (
                    <span className="ml-auto text-slate-500 text-[9px] line-through">
                      ditolak
                    </span>
                  )}
                </div>

                <div className="text-[10px] text-slate-600 font-mono truncate">
                  <span className="text-slate-400 select-none">
                    #{temuan.lokasi.paragraf_index + 1}{" "}
                  </span>
                  &ldquo;{ringkas}&rdquo;
                </div>

                {/* Alasan TERTUTUP secara bawaan, dan hanya ada pada temuan
                    yang tidak tertandai — temuan itu tidak punya komentar di
                    naskah yang bisa dibaca, jadi kartunya satu-satunya tempat.

                    Ditutup karena kartu panel wajib ringkas: kartu dan tombol,
                    bukan tempat menaruh paragraf (ditetapkan penelaah, ditegur
                    dua kali). Percobaan sebelumnya memotongnya tiga baris
                    dengan line-clamp, dan itu pun ditolak — tiga baris kali
                    empat puluh kartu tetap mendorong kartu berikutnya keluar
                    layar, dan kartu yang sebagian bertumpuk teks sebagian
                    tidak terbaca sebagai daftar yang rusak. */}
                {tanpaTanda && alasanTerbuka.has(temuan.id) && (
                  <div className="text-[10px] text-slate-700 bg-slate-50 border border-slate-200 rounded px-1.5 py-1 leading-snug">
                    {temuan.catatan}
                    {/* Usulan satuan baru ikut terbaca di sini: temuan yang
                        tidak ditandai juga tidak disisipkan, jadi kartu ini
                        satu-satunya tempat isinya. */}
                    {temuan.sisipan && (
                      <span className="block mt-1 text-slate-600">
                        Usulan {temuan.sisipan.bentuk} baru di {temuan.sisipan.sasaran}:{" "}
                        &ldquo;
                        {[temuan.sisipan.penanda, temuan.sisipan.teks].filter(Boolean).join(" ")}
                        &rdquo; — sumber: {temuan.sisipan.sumber}
                      </span>
                    )}
                  </div>
                )}

                {/* Tombol kedua muncul HANYA kalau perbaikannya ada di tempat
                    lain — mis. temuan di Pasal 2, tetapi definisinya harus
                    ditulis di Pasal 1. Kalau perbaikannya di tempat temuan itu
                    sendiri, backend mengosongkan sasarannya dan tombol ini
                    tidak digambar: tombol yang melompat ke tempat yang sedang
                    dibaca cuma membingungkan. */}
                {/* Sasarannya ditulis sebagai KETERANGAN, bukan di dalam
                    tombolnya. Sebelum 26 Sep 2026 seluruh kalimat panjang itu
                    jadi isi tombol, dan hasilnya tidak terbaca sebagai tombol
                    sama sekali — melebar sebaris penuh, beda bentuk dari
                    "Lompat ke Teks" di sebelahnya. */}
                {temuan.sasaran && temuan.sasaran_paragraf != null && (
                  <p className="text-[10px] text-slate-600 leading-snug">
                    <span className="font-semibold text-slate-700">
                      Perbaiki di:{" "}
                    </span>
                    {temuan.sasaran}
                  </p>
                )}

                {/* flex-wrap, bukan satu baris: lebar panel Word cuma ~320 px
                    dan sebuah kartu bisa memuat empat tombol. Tanpa ini yang
                    paling kanan terpotong. */}
                <div className="flex flex-wrap items-center justify-between gap-1">
                  <button
                    onClick={() => handleLompatKeLokasi(temuan)}
                    className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                    title="Arahkan kursor dokumen ke paragraf ini"
                  >
                    Lompat ke Teks
                  </button>

                  {temuan.sasaran && temuan.sasaran_paragraf != null && (
                    <button
                      onClick={() => lompatKeSasaran(temuan)}
                      className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                      title={`Arahkan kursor dokumen ke ${temuan.sasaran}`}
                    >
                      Lompat ke Perbaikan
                    </button>
                  )}

                  {/* Fase 4: perbaikannya disisipkan di satuan lain — "Lompat ke
                      Teks" membawa ke sisipan (tempat komentarnya), tombol ini
                      ke kata yang disorot di tempat temuan. */}
                  {temuan.sisipan && !tanpaTanda && (
                    <button
                      onClick={async () => {
                        setSelectedTemuanId(temuan.id);
                        if (inWord && !(await lihatSorotan(temuan))) {
                          tampilkanToast(`Sorotan T${temuan.nomor} tidak ketemu lagi di naskah.`);
                        }
                      }}
                      className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                      title="Arahkan kursor ke kata yang disorot di tempat temuan"
                    >
                      Lihat sorotan
                    </button>
                  )}

                  {/* Satu-satunya jalan membaca alasan temuan yang tidak
                      tertandai. Berupa tombol, bukan teks yang tergelar, supaya
                      kartunya tetap setinggi kartu lain sampai penelaah memang
                      memintanya. */}
                  {tanpaTanda && (
                    <button
                      onClick={() => bentangkanAlasan(temuan.id)}
                      className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                      title="Kenapa ini ditemukan — temuan ini tidak punya komentar di naskah"
                    >
                      {alasanTerbuka.has(temuan.id) ? "Tutup" : "Alasan"}
                    </button>
                  )}

                  {/* Semua temuan diputuskan dari sini — termasuk yang berupa
                      usulan penggantian. Daftar yang separuh kartunya bisa
                      ditekan dan separuhnya menyuruh pindah ke tab Review
                      membingungkan penelaah. */}
                  {/* Tombol keputusan SELALU ada. Menyembunyikannya pernah
                      dicoba dan langsung dilaporkan penelaah sebagai janggal —
                      kartu yang bentuknya berubah-ubah membuat daftar sulit
                      dibaca sekilas. */}
                  <div className="flex items-center gap-1">
                      <button
                        onClick={() => handleTerima(temuan)}
                        className={`px-2.5 py-1 rounded text-[10px] font-medium transition ${
                          temuan.status === "diterima"
                            ? "bg-emerald-600 text-white"
                            : "bg-slate-100 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700"
                        }`}
                        title="Ditandai diterima. Naskah kerja tidak berubah — usulannya baru diterapkan saat ekspor versi bersih."
                      >
                        Terima
                      </button>
                      <button
                        onClick={() => handleTolak(temuan)}
                        className={`px-2.5 py-1 rounded text-[10px] font-medium transition ${
                          temuan.status === "ditolak"
                            ? "bg-rose-600 text-white"
                            : "bg-slate-100 hover:bg-rose-50 text-slate-600 hover:text-rose-700"
                        }`}
                        title="Usulan hijau dibuang, coretan merah atau blok kuningnya dilepas, komentarnya dihapus — tanpa bekas"
                      >
                        Tolak
                      </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Sisanya tetap ADA di daftar, cuma belum digambar. Brief 8.7:
            Law Analyzer berhenti merespons di 68/175, dan titik berhentinya
            selalu sama — bebannya penggambaran. Yang dibatasi jumlah kartu
            yang digambar, bukan jumlah temuan yang dilaporkan. */}
        {temuanBerlokasi.length > batasTampil && (
          <button
            onClick={() => setBatasTampil((n) => n + TAMBAH_KARTU)}
            className="w-full py-1.5 text-[10px] text-blue-700 bg-white border border-blue-200 rounded hover:bg-blue-50"
          >
            Tampilkan {Math.min(TAMBAH_KARTU, temuanBerlokasi.length - batasTampil)}{" "}
            temuan lagi &mdash; {temuanBerlokasi.length - batasTampil} belum
            ditampilkan
          </button>
        )}

        {/* Empty state when no findings yet */}
        {temuanList.length === 0 && !analyzing && (
          <div className="bg-white rounded-lg border border-slate-200 p-6 text-center space-y-2 text-slate-500">
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 text-base font-bold">
              ⚖
            </div>
            <p className="font-semibold text-slate-700 text-xs">Belum Ada Pemeriksaan</p>
            <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">
              Klik tombol &ldquo;Jalankan Analisis&rdquo; untuk memeriksa draf
              peraturan. Apa saja yang diperiksa ditentukan di Pengaturan —
              tombol gerigi di atas.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-slate-200 bg-white px-3 py-2 text-[10px] text-slate-400 flex items-center justify-between">
        <span>Biro Bantuan Hukum &bull; Kemenkeu</span>
        <span>Drafter Analiser v0.1</span>
      </footer>

      {/* TOAST — konfirmasi sekali pakai, hilang sendiri.

          `fixed`, BUKAN bagian dari aliran halaman. Toast yang muncul di atas
          daftar kartu mendorong seluruh daftar turun, lalu menariknya naik
          lagi beberapa detik kemudian — dan penelaah yang sedang menekan
          Terima berturut-turut akan menekan tombol kartu yang SALAH karena
          kartunya bergeser di bawah jarinya.

          `pointer-events-none`: toast menutupi sepotong bawah panel, jadi klik
          wajib tembus ke tombol di bawahnya — kalau tidak, tombol Terima/Tolak
          kartu paling bawah mati selama toast tampil.

          Wadah `aria-live` selalu ada di DOM, isinya saja yang berganti —
          pembaca layar hanya mengumumkan perubahan di dalam wadah yang sudah
          ada sejak awal. */}
      <div
        role="status"
        aria-live="polite"
        className="fixed bottom-3 left-3 right-3 z-40 pointer-events-none flex justify-center"
      >
        {toast && (
          <div
            key={toast.id}
            className="da-muncul max-w-sm bg-slate-800 text-white text-[11px] leading-snug px-3 py-2 rounded-lg shadow-lg wrap-break-word"
          >
            {toast.teks}
          </div>
        )}
      </div>
    </div>
  );
}
