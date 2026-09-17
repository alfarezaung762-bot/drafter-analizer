"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Temuan,
  ParagrafInput,
  AnalisisRequest,
  AnalisisResponse,
  JenisDokumen,
  StatusTemuan,
} from "@/lib/types";
import {
  readParagraphs,
  selectFindingLocation,
  tandaiSemuaTemuan,
  tolakTemuan,
  bersihkanSemuaTanda,
} from "@/lib/office";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

// Sesudah Track Changes ditinggalkan (17 Sep 2026), seluruh penandaan berjalan
// di atas WordApi 1.1 — Font.color, Font.strikeThrough, Range.insertText,
// Range.insertContentControl, ContentControlCollection.getByTag. Hanya komentar
// yang butuh 1.4. Tidak ada lagi ketergantungan pada WordApiDesktop, jadi
// versinya tidak lagi ditampilkan di diagnostik.
const API_VERSIONS = ["1.1", "1.4", "1.7", "1.8", "1.9"];

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
  const [infoPenandaan, setInfoPenandaan] = useState<string | null>(null);

  // Web mode fallback state
  const [webInputText, setWebInputText] = useState(CONTOH_DRAFT_PMK);
  const [useWebCustomText, setUseWebCustomText] = useState(false);

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
  const adaYangBelumDiputuskan = useMemo(
    () => temuanList.some((t) => t.status === "belum_ditinjau"),
    [temuanList]
  );

  // Mengosongkan daftar panel SEKALIGUS mencabut seluruh tanda alat dari
  // naskah. Sejak tandanya digambar sendiri (bukan revisi Word), meninggalkan
  // tanda tanpa daftar berarti naskah berisi teks merah-hijau yang tidak ada
  // lagi yang bisa mencabutnya. Yang dicabut hanya yang bertag DA-* — warna
  // dan sorotan milik penyusun sendiri tidak disentuh.
  const handleBersihkanDaftar = async () => {
    let dicabut = 0;
    if (inWord) {
      dicabut = await bersihkanSemuaTanda();
    }
    setTemuanList([]);
    setSelectedTemuanId(null);
    setInfoPenandaan(null);
    setStatusMessage(
      inWord
        ? `Daftar dikosongkan dan ${dicabut} tanda dicabut dari naskah.` +
          " Komentar yang sudah terpasang tidak ikut terhapus — hapus lewat" +
          " panel komentar Word bila perlu."
        : "Daftar dikosongkan."
    );
  };

  // Gate legal: periksa apakah ada temuan dengan rujukan placeholder
  const adaRujukanBelumVerifikasi = useMemo(() => {
    return temuanList.some(
      (t) => t.rujukan.butir === "..." || t.rujukan.kutipan === "..."
    );
  }, [temuanList]);

  // Jalankan Analisis
  const handleJalankanAnalisis = async () => {
    // Jenis dokumen wajib dipilih dulu. Tanpa itu backend tidak tahu bunyi
    // baku mana yang dituntut pada butir Menimbang terakhir — "Peraturan
    // Menteri Keuangan" atau "Keputusan Menteri Keuangan".
    if (!jenisDokumen) {
      setGoyangJenis(true);
      setStatusMessage("Pilih dulu PMK atau KMK sebelum menganalisis.");
      window.setTimeout(() => setGoyangJenis(false), 600);
      return;
    }

    setAnalyzing(true);
    setStatusMessage(null);

    try {
      let paragraphs: ParagrafInput[] = [];

      if (inWord) {
        paragraphs = await readParagraphs(scope);
      } else {
        // Fallback web input
        const lines = webInputText
          .split("\n")
          .map((line, idx) => ({ index: idx, teks: line }));
        paragraphs = lines;
      }

      if (paragraphs.length === 0) {
        setStatusMessage("Tidak ada teks atau paragraf yang dapat dibaca.");
        setAnalyzing(false);
        return;
      }

      const reqBody: AnalisisRequest = {
        jenis_dokumen: jenisDokumen,
        paragraf: paragraphs,
      };
      const res = await fetch(`${API_BASE}/analisis/jalankan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(reqBody),
      });

      if (!res.ok) {
        throw new Error(`Server merespons status ${res.status}: ${res.statusText}`);
      }

      const data: AnalisisResponse = await res.json();
      setTemuanList(data.temuan);
      setParagrafCount(data.jumlah_paragraf);

      // Langsung tandai seluruh temuan di dokumen: bagian bermasalah terblok
      // warna DAN komentarnya sudah terpasang, tanpa menunggu penelaah menekan
      // Terima. Penelaah tinggal mengklik teks bersorot untuk membaca
      // komentarnya lewat panel komentar bawaan Word.
      //
      // Naskahnya sendiri tidak berubah sama sekali — sorotan bersifat
      // sementara, komentar adalah lampiran, bukan isi.
      if (inWord && data.temuan.length > 0) {
        const hasil = await tandaiSemuaTemuan(data.temuan);
        const bagian: string[] = [];
        if (hasil.dicoretMerah > 0) {
          bagian.push(`${hasil.dicoretMerah} dicoret merah`);
        }
        if (hasil.diusulkan > 0) {
          bagian.push(`${hasil.diusulkan} usulan hijau disisipkan`);
        }
        if (hasil.diblokKuning > 0) {
          bagian.push(`${hasil.diblokKuning} diberi blok kuning`);
        }
        if (hasil.dikomentari > 0) {
          bagian.push(`${hasil.dikomentari} komentar`);
        }

        let pesan = bagian.length > 0 ? bagian.join(", ") + "." : "";

        if (hasil.tidakKetemu > 0) {
          pesan +=
            ` ${hasil.tidakKetemu} temuan TIDAK ditandai di naskah karena` +
            " letak persisnya tidak ketemu — periksa sendiri lewat daftar" +
            " di bawah.";
        }

        if (!hasil.pelacakanMati) {
          pesan +=
            " Pelacakan perubahan tidak bisa dimatikan, jadi tanda-tanda ini" +
            " ikut tercatat Word sebagai revisi format. Matikan Track Changes" +
            " di tab Review lalu jalankan ulang bila margin jadi penuh.";
        }

        setInfoPenandaan(pesan.trim() || null);
      } else {
        setInfoPenandaan(null);
      }

      setStatusMessage(
        data.temuan.length === 0
          ? "Selesai! Tidak ditemukan ketidaksesuaian format baku pada draf."
          : `Analisis selesai. Ditemukan ${data.temuan.length} catatan pada ${data.jumlah_paragraf} baris.`
      );
    } catch (err: unknown) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setStatusMessage(`Gagal menjalankan analisis: ${errorMsg}`);
    } finally {
      setAnalyzing(false);
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
          <button
            onClick={() => setShowDiagnostics(!showDiagnostics)}
            className="text-[10px] px-2 py-0.5 rounded border border-slate-200 text-slate-600 hover:bg-slate-100 transition"
            title="Info Lingkungan & WordApi"
          >
            {inWord ? "Word Connected" : "Web Preview"}
          </button>
        </div>

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
              <div className="grid grid-cols-5 gap-1 text-center font-mono text-[10px]">
                {/* v… = WordApi, D… = WordApiDesktop */}
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
                <button
                  type="button"
                  onClick={() => setScope("selection")}
                  className={`px-2.5 py-1 text-[10px] font-medium rounded-r border-t border-b border-r ${
                    scope === "selection"
                      ? "bg-blue-600 text-white border-blue-600"
                      : "bg-white text-slate-700 border-slate-300 hover:bg-slate-50"
                  }`}
                >
                  Bagian Terpilih
                </button>
              </div>
            </div>
          )}

          {/* Analisis ulang ditolak selama masih ada temuan yang belum
              diputuskan: tiap analisis memasang komentar baru, dan pada
              pengujian 17 Sep 2026 dokumen contoh berakhir dengan ~18 komentar
              untuk 5 temuan. Lihat docs/fase1 drafter.md bagian 6.5. */}
          <button
            onClick={handleJalankanAnalisis}
            disabled={analyzing || adaYangBelumDiputuskan}
            title={
              adaYangBelumDiputuskan
                ? "Selesaikan dulu temuan yang belum diputuskan — analisis ulang akan menumpuk komentar"
                : undefined
            }
            className={`w-full py-2 px-3 rounded font-semibold text-white transition flex items-center justify-center gap-1.5 shadow-xs ${
              analyzing || adaYangBelumDiputuskan
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
                <span>Sedang Memeriksa Kaidah...</span>
              </>
            ) : (
              <>
                <svg className="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
                <span>Jalankan Analisis Format Baku</span>
              </>
            )}
          </button>

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
              <span className="font-bold">Penanda Gate Legal:</span> Beberapa dasar hukum rujukan masih bertanda placeholder (&quot;...&quot;) dan belum diverifikasi secara visual oleh penelaah hukum.
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
        <div className="space-y-1.5">
          {temuanList.map((temuan) => {
            const isSelected = selectedTemuanId === temuan.id;
            const isPlaceholderRujukan =
              temuan.rujukan.butir === "..." || temuan.rujukan.kutipan === "...";
            // Penjelasan temuan TIDAK diulang di sini — tempatnya di komentar
            // Word, di titik kesalahannya (bagian 6.6). Panel hanya navigasi.
            const cuplikan = temuan.lokasi.teks_asli.trim();
            const ringkas =
              cuplikan.length > 70 ? cuplikan.slice(0, 70) + "\u2026" : cuplikan;

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
                  {isPlaceholderRujukan && (
                    <span className="text-[8px] bg-amber-200 text-amber-900 px-1 rounded font-bold">
                      rujukan belum diverifikasi
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

        {/* Empty state when no findings yet */}
        {temuanList.length === 0 && !analyzing && (
          <div className="bg-white rounded-lg border border-slate-200 p-6 text-center space-y-2 text-slate-500">
            <div className="w-10 h-10 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-400 text-base font-bold">
              ⚖
            </div>
            <p className="font-semibold text-slate-700 text-xs">Belum Ada Pemeriksaan</p>
            <p className="text-[10px] text-slate-500 max-w-xs mx-auto leading-relaxed">
              Klik tombol &ldquo;Jalankan Analisis Format Baku&rdquo; untuk memeriksa kepatuhan draf peraturan terhadap KMK 527/KMK.01/2022.
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
