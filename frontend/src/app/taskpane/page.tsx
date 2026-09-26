"use client";

import { useState, useEffect, useMemo, useCallback } from "react";
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
} from "@/lib/types";
import {
  readParagraphs,
  selectFindingLocation,
  tandaiSemuaTemuan,
  perbaruiKomentarTemuan,
  tolakTemuan,
  bersihkanSemuaTanda,
  cakupanTerpilihTersedia,
  type HasilPenandaan,
} from "@/lib/office";
import {
  ATURAN_FASE1,
  ATURAN_BISA_DIPILIH,
  SEMUA_ID_AKTIF,
} from "@/lib/aturan-fase1";
import {
  ATURAN_FASE2,
  ATURAN_FASE2_MEKANIS,
  ATURAN_FASE2_MODEL,
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

// Panjang alasan yang masih muat tiga baris di lebar panel Word. Di atasnya
// tombol "selengkapnya" muncul; di bawahnya tidak, karena tombol yang tidak
// pernah mengubah apa pun cuma mengajak penelaah menekan sia-sia.
const BATAS_ALASAN_RINGKAS = 160;

// Jarak antar-pengambilan kemajuan Fase 2. Dua detik: cukup rapat supaya
// angkanya terasa hidup, cukup renggang supaya panel tidak sibuk sendiri.
const JEDA_TANYA_MS = 2000;

// Berapa kali bertanya sebelum menyerah. 2 detik x 450 = 15 menit — jauh di
// atas dokumen 175 satuan, tetapi tetap berujung. Panel yang berputar
// selamanya tidak bisa dibedakan penelaah dari analisis yang memang lama.
const BATAS_TANYA = 450;

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
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [showDiagnostics, setShowDiagnostics] = useState(false);
  const [showPengaturan, setShowPengaturan] = useState(false);
  // Aturan mana saja yang dijalankan. Semula semuanya. Penelaah bisa mematikan
  // satu aturan yang salah tandai tanpa menunggu kodenya diperbaiki — dan bisa
  // memeriksa manual apa yang sebenarnya diperiksa tiap aturan.
  const [aturanAktif, setAturanAktif] = useState<Set<string>>(
    () => new Set(SEMUA_ID_AKTIF)
  );
  const [aturanTerbuka, setAturanTerbuka] = useState<string | null>(null);
  const [infoPenandaan, setInfoPenandaan] = useState<string | null>(null);
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
  const [fase2Kemajuan, setFase2Kemajuan] = useState<{
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

  // Alat pengembang — ekspor Tahap 0 dan Tahap 3.
  const [mengekspor, setMengekspor] = useState(false);
  const [pesanEkspor, setPesanEkspor] = useState<string | null>(null);
  const [mengekspor3, setMengekspor3] = useState(false);
  const [pesanEkspor3, setPesanEkspor3] = useState<string | null>(null);
  const [namaDokumen, setNamaDokumen] = useState("");

  // Nomor pekerjaan Fase 2 terakhir di sesi ini. Dipakai Ekspor Tahap 3 untuk
  // mengambil peta yang BENAR-BENAR dipakai. Kosong bukan halangan: backend
  // jatuh ke pekerjaan terbaru untuk dokumen ini, supaya panel yang dimuat
  // ulang tetap bisa mengekspor.
  const [nomorPekerjaan, setNomorPekerjaan] = useState<number | null>(null);

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

  /** Tidak ada satu pun pemeriksaan dicentang — tombolnya tidak punya kerja. */
  const tidakAdaYangDicentang =
    aturanAktif.size === 0 && aturanFase2Aktif.size === 0;

  const adaYangBelumDiputuskan = useMemo(
    () =>
      temuanBerlokasi.some(
        (t) => t.status === "belum_ditinjau" && !tidakTertandai(t)
      ),
    [temuanBerlokasi, tidakTertandai]
  );

  // Mengosongkan daftar panel SEKALIGUS mencabut seluruh tanda alat dari
  // naskah. Sejak tandanya digambar sendiri (bukan revisi Word), meninggalkan
  // tanda tanpa daftar berarti naskah berisi teks merah-hijau yang tidak ada
  // lagi yang bisa mencabutnya. Yang dicabut hanya yang bertag DA-* — warna
  // dan sorotan milik penyusun sendiri tidak disentuh.
  const handleBersihkanDaftar = async () => {
    let hasil = { tanda: 0, komentar: 0 };
    if (inWord) {
      hasil = await bersihkanSemuaTanda();
    }
    setTemuanList([]);
    setSelectedTemuanId(null);
    setInfoPenandaan(null);
    setFase2Pesan(null);
    setFase2Kemajuan(null);
    setBatasTampil(BATAS_KARTU_AWAL);
    // Ikut dikosongkan — tanpa ini, daftar id dari analisis sebelumnya
    // bertahan dan bisa membuat kartu analisis berikutnya salah dilabeli
    // "tidak ditandai di naskah".
    setIdTidakDitandai(new Set());
    setStatusMessage(
      inWord
        ? `Daftar dikosongkan, ${hasil.tanda} tanda dan ${hasil.komentar}` +
          " komentar dicabut dari naskah. Warna dan sorotan milik penyusun" +
          " sendiri tidak disentuh."
        : "Daftar dikosongkan."
    );
  };

  // Gate legal: periksa apakah ada temuan dengan rujukan placeholder
  const adaRujukanBelumVerifikasi = useMemo(() => {
    return temuanList.some(
      (t) => t.rujukan.status !== "visual"
    );
  }, [temuanList]);

  // ---------------------------------------------------------------------
  // SATU TOMBOL untuk seluruh fase
  // ---------------------------------------------------------------------
  //
  // Panel Pengaturan yang menentukan apa yang jalan: aturan F1 yang dicentang
  // menjalankan Fase 1, aturan F2/F3 yang dicentang menjalankan Fase 2/3.
  // Penelaah tidak perlu tahu batas fase untuk memakai alat ini — ia cuma
  // mencentang apa yang ingin diperiksa, lalu menekan sekali.
  //
  // Paragrafnya dibaca SEKALI dan dipakai kedua fase.

  const bacaParagrafSekali = async (): Promise<ParagrafInput[]> => {
    if (inWord) return readParagraphs(scope);
    return webInputText
      .split("\n")
      .map((line, idx) => ({ index: idx, teks: line }));
  };

  /** Ringkas hasil penandaan jadi kalimat yang dibaca penelaah. */
  const ringkasPenandaan = (hasil: HasilPenandaan): string => {
    const bagian: string[] = [];
    if (hasil.dicoretMerah > 0) bagian.push(`${hasil.dicoretMerah} dicoret merah`);
    if (hasil.diusulkan > 0) bagian.push(`${hasil.diusulkan} usulan hijau disisipkan`);
    if (hasil.diblokKuning > 0) bagian.push(`${hasil.diblokKuning} diberi blok kuning`);
    if (hasil.dikomentari > 0) bagian.push(`${hasil.dikomentari} komentar`);

    let pesan = bagian.length > 0 ? bagian.join(", ") + "." : "";
    if (hasil.idTidakDitandai.length > 0) {
      pesan +=
        ` ${hasil.idTidakDitandai.length} temuan TIDAK ditandai di naskah` +
        " karena letak persisnya tidak ketemu — alasannya ada di kartunya" +
        " masing-masing di bawah.";
    }
    // Balon komentar kosong tidak menjelaskan apa-apa tetapi tetap menyorot
    // naskah, jadi penelaah melihat tanda yang bisu. Disebut terang-terangan
    // daripada dibiarkan ditemukan sendiri.
    if (hasil.komentarKosong > 0) {
      pesan +=
        ` ${hasil.komentarKosong} komentar terpasang tetapi isinya kosong —` +
        " Word menolak menuliskannya. Isi temuannya tetap terbaca di kartu" +
        " di bawah. Laporkan ini ke pengembang bila berulang.";
    }
    if (!hasil.pelacakanMati) {
      pesan +=
        " Pelacakan perubahan tidak bisa dimatikan, jadi tanda-tanda ini" +
        " ikut tercatat Word sebagai revisi format. Matikan Track Changes" +
        " di tab Review lalu jalankan ulang bila margin jadi penuh.";
    }
    return pesan.trim();
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
      setInfoPenandaan(ringkasPenandaan(hasil) || null);
    } else {
      setInfoPenandaan(null);
      setIdTidakDitandai(new Set());
    }

    setStatusMessage(
      data.temuan.length === 0
        ? "Fase 1 selesai: tidak ditemukan ketidaksesuaian format baku."
        : `Fase 1 selesai: ${data.temuan.length} temuan pada ${data.jumlah_paragraf} baris.`
    );
    return data.temuan;
  };

  /** Fase 2/3 — menit, sebagian berbayar. MENAMBAH temuan, tidak mengganti. */
  const jalankanFase2 = async (
    paragraf: ParagrafInput[],
    temuanFase1: Temuan[]
  ): Promise<void> => {
    setFase2Kemajuan(null);

    // Nomor Fase 2 MELANJUTKAN nomor terbesar yang sudah terpakai — (T3) sudah
    // tertulis di komentar Word, jadi menomori ulang membuat komentar itu
    // menunjuk temuan yang berbeda.
    const nomorTerakhir = temuanFase1.reduce((maks, t) => Math.max(maks, t.nomor), 0);

    const body: AnalisisLanjutRequest = {
      paragraf,
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

    // Bertanya BERBATAS, bukan selamanya. Backend yang tergantung akan membuat
    // panel berputar tanpa akhir, dan penelaah tidak punya cara membedakannya
    // dari analisis yang memang lama.
    let kemajuan: KemajuanResponse | null = null;
    let mandek = false;
    for (let ke = 0; ; ke++) {
      if (ke >= BATAS_TANYA) {
        mandek = true;
        break;
      }
      await new Promise((r) => setTimeout(r, JEDA_TANYA_MS));
      const res = await fetch(`${API_BASE}/analisis/lanjut/${pekerjaan}`);
      if (!res.ok) throw new Error(`Gagal membaca kemajuan (${res.status})`);
      kemajuan = await res.json();
      if (!kemajuan) break;
      setFase2Kemajuan({
        selesai: kemajuan.satuan_selesai,
        total: kemajuan.satuan_total,
      });
      if (kemajuan.status === "selesai" || kemajuan.status === "gagal") break;
    }

    if (mandek) {
      setFase2Pesan(
        `Menyerah menunggu sesudah ${Math.round(
          (BATAS_TANYA * JEDA_TANYA_MS) / 60000
        )} menit. Pekerjaan #${pekerjaan} mungkin masih berjalan di backend —` +
          ` periksa ${API_BASE}/analisis/lanjut/${pekerjaan}. Peta yang sudah` +
          " selesai tetap tersimpan, jadi analisis ulang tidak mengulang dari nol."
      );
      return;
    }
    if (!kemajuan) {
      setFase2Pesan("Tidak ada jawaban dari backend.");
      return;
    }
    if (kemajuan.status === "gagal") {
      setFase2Pesan(`Fase 2 gagal: ${kemajuan.pesan}`);
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
    // sendiri.
    if (kemajuan.temuan.length === 0 && kemajuan.pesan) {
      setFase2Pesan(kemajuan.pesan);
      return;
    }

    // Ditandai PER KELOMPOK, bukan sekaligus — syarat ke-4 dari brief 8.7.
    if (inWord && kemajuan.temuan.length > 0) {
      const tidakDitandai: string[] = [];
      for (let i = 0; i < kemajuan.temuan.length; i += 10) {
        const kelompok = kemajuan.temuan.slice(i, i + 10);
        const hasil = await tandaiSemuaTemuan(kelompok);
        tidakDitandai.push(...hasil.idTidakDitandai);
        setTemuanList((prev) => [...prev, ...kelompok]);
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
  };

  const handleAnalisis = async () => {
    // Jenis dokumen wajib dipilih dulu. Tanpa itu backend tidak tahu bunyi
    // baku mana yang dituntut pada butir Menimbang terakhir — "Peraturan
    // Menteri Keuangan" atau "Keputusan Menteri Keuangan".
    if (!jenisDokumen) {
      setGoyangJenis(true);
      setStatusMessage("Pilih dulu PMK atau KMK sebelum menganalisis.");
      window.setTimeout(() => setGoyangJenis(false), 600);
      return;
    }

    const adaFase1 = aturanAktif.size > 0;
    const adaFase2 = aturanFase2Aktif.size > 0;
    if (!adaFase1 && !adaFase2) {
      setStatusMessage(
        "Semua pemeriksaan dimatikan di Pengaturan — tidak ada yang bisa" +
          " diperiksa. Nyalakan setidaknya satu."
      );
      setShowPengaturan(true);
      return;
    }

    setAnalyzing(true);
    setStatusMessage(null);
    setFase2Pesan(null);

    try {
      const paragraf = await bacaParagrafSekali();
      if (paragraf.length === 0) {
        setStatusMessage("Tidak ada teks atau paragraf yang dapat dibaca.");
        return;
      }

      const temuanFase1 = adaFase1
        ? await jalankanFase1(paragraf, jenisDokumen)
        : [];
      if (adaFase2) {
        setFase2Berjalan(true);
        try {
          await jalankanFase2(paragraf, temuanFase1);
        } finally {
          setFase2Berjalan(false);
        }
      }
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setStatusMessage(`Gagal menjalankan analisis: ${errorMsg}`);
    } finally {
      setAnalyzing(false);
    }
  };

  // ---------------------------------------------------------------------
  // ALAT PENGEMBANG — Ekspor Tahap 0 dan Tahap 3
  // ---------------------------------------------------------------------
  //
  // Bukan fitur penelaah. Alat ini masih dalam pengembangan, dan kedua ekspor
  // ini dipakai melihat apa yang benar-benar sampai ke model. Keduanya
  // menjawab pertanyaan yang berbeda:
  //
  //   Tahap 0   apa yang DIBACA model   — gratis, kapan saja
  //   Tahap 3   apa yang DITALAR model  — peta dari analisis yang sudah jalan
  //
  // Jalur unduhannya satu dan dipakai bersama: Blob + <a download>, dengan
  // jendela baru sebagai cadangan karena WebView2 Word kadang memblokir
  // unduhan. CLAUDE.md butir 9: didukung bukan berarti diizinkan.
  const unduhTeks = (teks: string, berkas: string, petunjuk: string): string => {
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
      return (
        `${berkas} diunduh — ${teks.length.toLocaleString("id-ID")} huruf. ` +
        petunjuk
      );
    } catch {
      window.open(url, "_blank");
      return "Unduhan diblokir Word, jadi dibuka di jendela baru. Salin dari sana.";
    } finally {
      window.setTimeout(() => URL.revokeObjectURL(url), 60_000);
    }
  };

  const namaBerkas = (awalan: string) =>
    `${awalan}-${(namaDokumen || "naskah").replace(/\W+/g, "-")}.txt`;

  // Yang paling penting di sini: daftar satuan yang DIBUANG penyaring Langkah
  // 1. Satuan itu tidak pernah sampai ke model dan tidak meninggalkan jejak
  // apa pun di panel, jadi ini satu-satunya cara memeriksanya.
  const handleEksporTahap0 = async () => {
    setMengekspor(true);
    setPesanEkspor(null);
    try {
      const paragraf = await bacaParagrafSekali();
      if (paragraf.length === 0) {
        setPesanEkspor("Tidak ada paragraf yang dapat dibaca.");
        return;
      }

      const res = await fetch(`${API_BASE}/analisis/tahap0`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          paragraf,
          dokumen: namaDokumen,
          temuan_fase1: temuanList.filter((t) => t.fase === 1),
        }),
      });
      if (!res.ok) throw new Error(`Server merespons status ${res.status}`);
      const teks = await res.text();

      setPesanEkspor(
        unduhTeks(
          teks,
          namaBerkas("tahap0"),
          "Baca bagian YANG DIBUANG paling atas."
        )
      );
    } catch (err: unknown) {
      setPesanEkspor(
        `Gagal mengekspor: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setMengekspor(false);
    }
  };

  // Memperlihatkan peta yang BENAR-BENAR dipakai analisis terakhir, bukan peta
  // baru. Model tidak deterministik: menjalankan ulang Langkah 2 menghasilkan
  // ringkasan yang berbeda, dan ekspor yang memperlihatkan peta lain daripada
  // yang dipakai justru menyesatkan orang yang sedang mencari bug. Karena itu
  // tombol ini TIDAK menjalankan apa pun dan tidak berbiaya — dan karena itu
  // pula ia kosong sampai analisis Fase 2 penalaran pernah dijalankan.
  const handleEksporTahap3 = async () => {
    setMengekspor3(true);
    setPesanEkspor3(null);
    try {
      const paragraf = await bacaParagrafSekali();
      if (paragraf.length === 0) {
        setPesanEkspor3("Tidak ada paragraf yang dapat dibaca.");
        return;
      }

      const res = await fetch(`${API_BASE}/analisis/tahap3`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          paragraf,
          dokumen: namaDokumen,
          pekerjaan: nomorPekerjaan,
        }),
      });
      if (!res.ok) throw new Error(`Server merespons status ${res.status}`);
      const teks = await res.text();

      setPesanEkspor3(
        unduhTeks(
          teks,
          namaBerkas("tahap3"),
          teks.includes("PETA KOSONG")
            ? "Petanya masih kosong — jalankan analisis dengan aturan F2-1xx dulu."
            : "Baca bagian PETA paling atas, satu ringkasan per satuan."
        )
      );
    } catch (err: unknown) {
      setPesanEkspor3(
        `Gagal mengekspor: ${err instanceof Error ? err.message : String(err)}`
      );
    } finally {
      setMengekspor3(false);
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
    setStatusMessage(
      `T${temuan.nomor} diterima. Coretan dan usulannya tetap di naskah kerja` +
        " — akan diterapkan saat ekspor versi bersih."
    );
  };

  // Tolak temuan: usulan hijaunya dibuang, teks aslinya dipulihkan persis
  // seperti sebelum ditandai, komentarnya dihapus. Tidak boleh ada bekas.
  const handleTolak = async (temuan: Temuan) => {
    updateStatus(temuan.id, "ditolak");
    if (!inWord) {
      setStatusMessage(`Status temuan T${temuan.nomor} diubah menjadi 'Ditolak'.`);
      return;
    }
    const berhasil = await tolakTemuan(temuan);
    setStatusMessage(
      berhasil
        ? `T${temuan.nomor} ditolak. Naskah kembali seperti sebelum ditandai.`
        : `T${temuan.nomor} ditolak di daftar, tetapi tandanya tidak ditemukan` +
          " lagi di naskah — mungkin sudah diubah manual. Periksa sendiri."
    );
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
        @media (prefers-reduced-motion: reduce) {
          .da-goyang { animation: none; }
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
                Kemenkeu &bull; Kaidah Format Baku (Fase 1)
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

        {/* Panel Pengaturan — daftar pemeriksaan Fase 1.
            Dua gunanya sekaligus: mematikan aturan yang salah tandai tanpa
            menunggu kode diperbaiki, DAN memperlihatkan apa yang sebenarnya
            diperiksa tiap aturan supaya penelaah bisa mengecek manual. */}
        {showPengaturan && (
          <div className="mt-2.5 p-2 bg-slate-100 rounded border border-slate-200 space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-700 text-[11px]">
                Fase 1 — Koreksi Format Baku
              </span>
              <div className="flex items-center gap-2 text-[10px]">
                <button
                  onClick={() => setAturanAktif(new Set(SEMUA_ID_AKTIF))}
                  className="text-blue-700 hover:underline"
                >
                  Pilih semua
                </button>
                <button
                  onClick={() => setAturanAktif(new Set())}
                  className="text-slate-500 hover:underline"
                >
                  Kosongkan
                </button>
              </div>
            </div>

            <p className="text-[10px] text-slate-500 leading-snug">
              Seluruh pemeriksaan di bawah deterministik — tanpa AI. Klik nama
              pemeriksaan untuk melihat rinciannya.
            </p>

            {ATURAN_FASE1.map((aturan) => {
              const mati = !!aturan.dimatikan;
              const dipilih = aturanAktif.has(aturan.id);
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
                      checked={dipilih && !mati}
                      disabled={mati}
                      onChange={(e) =>
                        setAturanAktif((prev) => {
                          const next = new Set(prev);
                          if (e.target.checked) next.add(aturan.id);
                          else next.delete(aturan.id);
                          return next;
                        })
                      }
                      className="mt-0.5 accent-blue-700"
                    />
                    <button
                      onClick={() =>
                        setAturanTerbuka(terbuka ? null : aturan.id)
                      }
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
                      <span className="block text-[9px] text-slate-400">
                        {terbuka ? "sembunyikan rincian" : "lihat rincian"}
                      </span>
                    </button>
                  </div>

                  {terbuka && (
                    <div className="px-2 pb-2 pt-0.5 space-y-1.5 text-[10px] leading-snug border-t border-slate-100">
                      {mati && (
                        <p className="text-rose-800 bg-rose-50 border border-rose-200 rounded px-1.5 py-1">
                          <span className="font-semibold">
                            Kenapa dimatikan:{" "}
                          </span>
                          {aturan.dimatikan}
                        </p>
                      )}
                      <div>
                        <p className="font-semibold text-slate-700">
                          Yang diperiksa
                        </p>
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
                            Dasar aturannya belum pasti:{" "}
                          </span>
                          {aturan.catatanSumber}
                        </p>
                      )}
                    </div>
                  )}
                </div>
              );
            })}

            <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
              {aturanAktif.size} dari {ATURAN_BISA_DIPILIH.length} pemeriksaan
              dinyalakan.
              {aturanAktif.size === 0 && " Analisis tidak akan menemukan apa pun."}
            </p>

            {/* Fase 2 dan 3 — dipisah dari Fase 1 dengan pembatas tebal.
                Bukan kerapian: yang di bawah ini berbeda sifatnya. Sebagian
                memanggil model, berjalan menit, dan berbiaya. */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-semibold text-slate-700 text-[11px]">
                  Fase 2 &amp; 3 — Pemeriksaan Isi
                </span>
                <div className="flex items-center gap-2 text-[10px]">
                  <button
                    onClick={() => setAturanFase2Aktif(new Set(ID_AKTIF_BAWAAN))}
                    className="text-blue-700 hover:underline"
                  >
                    Bawaan
                  </button>
                  <button
                    onClick={() => setAturanFase2Aktif(new Set())}
                    className="text-slate-500 hover:underline"
                  >
                    Kosongkan
                  </button>
                </div>
              </div>

              <p className="text-[10px] text-slate-500 leading-snug">
                Empat pemeriksaan pertama deterministik seperti Fase 1 — gratis
                dan hasilnya pasti. Sisanya memakai AI: berjalan beberapa menit
                dan berbiaya. Fase 3 mati secara bawaan karena bergantung pada
                korpus peraturan yang isinya belum diverifikasi langsung.
              </p>

              {[
                { judul: "Tanpa AI — gratis, hasilnya pasti", daftar: ATURAN_FASE2_MEKANIS },
                { judul: "Dengan AI — berjalan menit, berbiaya", daftar: ATURAN_FASE2_MODEL },
              ].map((kelompok) => (
                <div key={kelompok.judul} className="space-y-1.5">
                  <p className="text-[9px] uppercase tracking-wide text-slate-400 font-semibold">
                    {kelompok.judul}
                  </p>
                  {kelompok.daftar.map((aturan) => {
                    const dipilih = aturanFase2Aktif.has(aturan.id);
                    const terbuka = aturanTerbuka === aturan.id;
                    return (
                      <div
                        key={aturan.id}
                        className="rounded border border-slate-300 bg-white"
                      >
                        <div className="flex items-start gap-1.5 px-1.5 py-1.5">
                          <input
                            type="checkbox"
                            id={`aturan-${aturan.id}`}
                            checked={dipilih}
                            onChange={(e) =>
                              setAturanFase2Aktif((prev) => {
                                const next = new Set(prev);
                                if (e.target.checked) next.add(aturan.id);
                                else next.delete(aturan.id);
                                return next;
                              })
                            }
                            className="mt-0.5 accent-blue-700"
                          />
                          <button
                            onClick={() =>
                              setAturanTerbuka(terbuka ? null : aturan.id)
                            }
                            className="flex-1 text-left"
                            aria-expanded={terbuka}
                          >
                            <span className="text-[11px] text-slate-800 leading-snug">
                              {aturan.judul}
                            </span>
                            {aturan.fase === 3 && (
                              <span className="ml-1 text-[8px] bg-violet-200 text-violet-900 px-1 rounded font-bold align-middle">
                                Fase 3
                              </span>
                            )}
                            <span className="block text-[9px] text-slate-400">
                              {terbuka ? "sembunyikan rincian" : "lihat rincian"}
                            </span>
                          </button>
                        </div>

                        {terbuka && (
                          <div className="px-2 pb-2 pt-0.5 space-y-1.5 text-[10px] leading-snug border-t border-slate-100">
                            <div>
                              <p className="font-semibold text-slate-700">
                                Yang diperiksa
                              </p>
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
                                    : "Dasar aturannya belum pasti: "}
                                </span>
                                {aturan.catatanSumber}
                              </p>
                            )}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ))}

              <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                {aturanFase2Aktif.size} dari {ATURAN_FASE2.length} pemeriksaan
                Fase 2/3 dinyalakan.
                {aturanFase2Aktif.size === 0 &&
                  " Tidak ada pemeriksaan isi yang akan dijalankan."}
              </p>
            </div>

            {/* ---------------------------------------------------------
                ALAT PENGEMBANG — paling bawah, dipisah garis tebal.
                Bukan fitur penelaah: alat ini masih dalam pengembangan, dan
                ekspor ini dipakai programer melihat apa yang benar-benar
                dibaca model sebagai acuan memperbaiki bug.
                --------------------------------------------------------- */}
            <div className="pt-2 mt-1 border-t-2 border-slate-300 space-y-1.5">
              <span className="font-semibold text-slate-700 text-[11px]">
                Alat pengembang
              </span>
              <p className="text-[10px] text-slate-500 leading-snug">
                <strong>Tahap 0 — apa yang dibaca AI.</strong> Paragraf apa
                adanya, pohon satuan, dan muatan tiap panggilan. Di paling atas
                ada daftar satuan yang <strong>dibuang penyaring</strong>{" "}
                berikut teks utuhnya — itulah yang perlu dibaca dulu untuk
                memastikan tidak ada bagian penting yang terlewat. Tidak
                memanggil AI, tidak berbiaya.
              </p>
              <button
                onClick={handleEksporTahap0}
                disabled={mengekspor}
                className={`w-full py-1.5 px-2 rounded text-[11px] font-medium border transition ${
                  mengekspor
                    ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                }`}
              >
                {mengekspor ? "Menyiapkan…" : "Ekspor Tahap 0 (.txt)"}
              </button>
              {pesanEkspor && (
                <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                  {pesanEkspor}
                </p>
              )}

              <p className="text-[10px] text-slate-500 leading-snug pt-1.5">
                <strong>Tahap 3 — apa yang ditalar AI.</strong> Langkah 2
                meringkas tiap satuan jadi <strong>satu baris</strong>, dan
                Langkah 3 menalar di atas kumpulan baris itu — bukan di atas
                teks penuh. Ringkasan yang meleset membuat seluruh penalaran
                bertumpu pada gambaran yang salah, dan tidak ada langkah
                sesudahnya yang bisa mengetahuinya. Ekspor ini memperlihatkan
                peta yang <strong>benar-benar dipakai</strong> analisis
                terakhir, jadi ia kosong sampai analisis Fase 2 dengan aturan
                F2-1xx pernah dijalankan. Tidak memanggil AI, tidak berbiaya.
              </p>
              <button
                onClick={handleEksporTahap3}
                disabled={mengekspor3}
                className={`w-full py-1.5 px-2 rounded text-[11px] font-medium border transition ${
                  mengekspor3
                    ? "bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed"
                    : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                }`}
              >
                {mengekspor3 ? "Menyiapkan…" : "Ekspor Tahap 3 (.txt)"}
              </button>
              {pesanEkspor3 && (
                <p className="text-[10px] text-slate-600 bg-white border border-slate-200 rounded px-1.5 py-1">
                  {pesanEkspor3}
                </p>
              )}
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
                  onClick={() => setJenisDokumen(jenis)}
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

              Analisis ulang ditolak selama masih ada temuan yang belum
              diputuskan: tiap analisis memasang komentar baru, dan pada
              pengujian 17 Sep 2026 dokumen contoh berakhir dengan ~18 komentar
              untuk 5 temuan. Lihat docs/fase1 drafter.md bagian 6.5. */}
          <button
            onClick={handleAnalisis}
            disabled={analyzing || adaYangBelumDiputuskan || tidakAdaYangDicentang}
            title={
              tidakAdaYangDicentang
                ? "Tidak ada pemeriksaan yang dicentang di Pengaturan"
                : adaYangBelumDiputuskan
                  ? "Selesaikan dulu temuan yang belum diputuskan — analisis ulang akan menumpuk komentar"
                  : undefined
            }
            className={`w-full py-2 px-3 rounded font-semibold text-white transition flex items-center justify-center gap-1.5 shadow-xs ${
              analyzing || adaYangBelumDiputuskan || tidakAdaYangDicentang
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
                  {!fase2Berjalan
                    ? "Memeriksa format baku…"
                    : fase2Kemajuan && fase2Kemajuan.total > 0
                      ? `Membaca ${fase2Kemajuan.selesai}/${fase2Kemajuan.total} satuan…`
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

          {/* Angka kemajuan tetap terlihat sesudah selesai. Penelaah berhak
              tahu berapa satuan yang benar-benar dibaca — bukan cuma berapa
              temuan yang keluar. */}
          {fase2Kemajuan && fase2Kemajuan.total > 0 && (
            <div className="space-y-1">
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
              <div className="text-[10px] text-slate-500">
                {fase2Kemajuan.selesai} dari {fase2Kemajuan.total} satuan dibaca
              </div>
            </div>
          )}

          {fase2Pesan && (
            <div className="text-[10px] text-blue-900 bg-blue-50 px-2 py-1.5 rounded border border-blue-200">
              {fase2Pesan}
            </div>
          )}

          {adaYangBelumDiputuskan && (
            <div className="text-[10px] text-amber-900 bg-amber-50 px-2 py-1.5 rounded border border-amber-200 space-y-1">
              <div>
                Masih ada temuan yang belum diputuskan. Selesaikan dulu sebelum
                menganalisis ulang, supaya komentarnya tidak menumpuk.
              </div>
              <button
                onClick={handleBersihkanDaftar}
                className="underline font-medium hover:text-amber-950"
              >
                Bersihkan daftar dan mulai dari awal
              </button>
            </div>
          )}

          {statusMessage && (
            <div className="text-[10px] text-slate-600 bg-slate-50 px-2 py-1.5 rounded border border-slate-200">
              {statusMessage}
            </div>
          )}
        </div>

        {/* Gate Legal Warning Banner */}
        {adaRujukanBelumVerifikasi && (
          <div className="bg-amber-50 border border-amber-300 text-amber-900 px-2.5 py-2 rounded-lg flex items-start gap-1.5 text-[11px] leading-snug">
            <span className="text-amber-600 font-bold text-sm leading-none">&#9888;</span>
            <div>
              <span className="font-bold">Penanda Gate Legal:</span> Sebagian rujukan butir KMK 527 belum dibaca dan diketik ulang manusia dari naskah aslinya — isinya berasal dari ekstraksi teks yang OCR-nya rusak. Periksa butirnya sendiri sebelum memakai temuan ini sebagai dasar koreksi.
            </div>
          </div>
        )}

        {/* Catatan keterbatasan penandaan di dokumen (mis. Critique terkunci lisensi) */}
        {infoPenandaan && (
          <div className="bg-sky-50 border border-sky-300 text-sky-900 px-2.5 py-2 rounded-lg flex items-start gap-1.5 text-[11px] leading-snug">
            <span className="text-sky-600 font-bold text-sm leading-none">&#9432;</span>
            <div>{infoPenandaan}</div>
          </div>
        )}

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
                <span>{t.catatan}</span>
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
            const isPlaceholderRujukan =
              temuan.rujukan.status !== "visual" && !rujukanTurunan;
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
                className={`bg-white rounded border border-slate-200 px-2.5 py-2 space-y-1.5 transition ${
                  isSelected ? "ring-2 ring-blue-500/40" : ""
                } ${temuan.status !== "belum_ditinjau" ? "opacity-60" : ""}`}
              >
                <div className="flex items-center gap-1.5">
                  <span className="font-mono font-bold text-slate-800 text-[11px] bg-slate-100 px-1.5 py-0.5 rounded">
                    T{temuan.nomor}
                  </span>
                  <span
                    className={`text-[9px] font-medium px-1.5 py-0.5 rounded border ${
                      temuan.jenis_tanda === "penggantian"
                        ? "bg-sky-50 text-sky-700 border-sky-200"
                        : "bg-amber-50 text-amber-800 border-amber-200"
                    }`}
                    title={
                      temuan.jenis_tanda === "penggantian"
                        ? "Teks lama merah dicoret, usulan penggantinya hijau di sebelahnya"
                        : "Diberi blok kuning sebagai peringatan — perbaikannya ditentukan penelaah"
                    }
                  >
                    {temuan.jenis_tanda === "penggantian" ? "usulan" : "catatan"}
                  </span>
                  {/* Fase ditunjukkan, bukan dipakai menomori ulang. Penelaah
                      berhak tahu temuan mana yang kesalahannya bisa dibuktikan
                      baris demi baris (Fase 1) dan mana yang hasil penalaran
                      model (Fase 2/3) — cara memeriksanya memang berbeda. */}
                  {temuan.fase > 1 && (
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

                {/* Alasan HANYA muncul di kartu temuan yang tidak tertandai.
                    Bagi temuan itu tidak ada komentar di naskah yang bisa
                    dibaca, jadi kalau kartunya juga bisu penelaah cuma melihat
                    cuplikan tanpa tahu apa yang dipersoalkan — persis kartu
                    hampa yang dilaporkan pada PMK 119. Temuan yang tertandai
                    tetap tidak mengulang penjelasan komentarnya (bagian 6.9). */}
                {tanpaTanda && (
                  <div className="text-[10px] text-slate-700 bg-slate-50 border border-slate-200 rounded px-1.5 py-1 leading-snug">
                    {/* Dipotong tiga baris supaya satu alasan panjang tidak
                        mendorong kartu-kartu berikutnya keluar layar. Yang
                        dipotong cuma TAMPILANNYA — teksnya utuh, sekali klik. */}
                    <p
                      className={
                        alasanTerbuka.has(temuan.id) ? "" : "line-clamp-3"
                      }
                    >
                      {temuan.catatan}
                    </p>
                    {temuan.catatan.length > BATAS_ALASAN_RINGKAS && (
                      <button
                        onClick={() => bentangkanAlasan(temuan.id)}
                        className="mt-0.5 text-slate-500 hover:text-slate-800 underline underline-offset-2"
                      >
                        {alasanTerbuka.has(temuan.id)
                          ? "ringkas"
                          : "selengkapnya"}
                      </button>
                    )}
                  </div>
                )}

                <div className="flex items-center justify-between gap-1">
                  <button
                    onClick={() => handleLompatKeLokasi(temuan)}
                    className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                    title="Arahkan kursor dokumen ke paragraf ini"
                  >
                    Lompat ke Teks
                  </button>

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
    </div>
  );
}
