"use client";

import { useState, useEffect, useMemo } from "react";
import {
  Temuan,
  ParagrafInput,
  AnalisisRequest,
  AnalisisResponse,
  TingkatKeparahan,
  StatusTemuan,
} from "@/lib/types";
import {
  readParagraphs,
  selectFindingLocation,
  tandaiSemuaTemuan,
  hapusSorotan,
  hapusKomentarTemuan,
} from "@/lib/office";

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";

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
  const [filterSeverity, setFilterSeverity] = useState<TingkatKeparahan | "semua">("semua");
  const [selectedTemuanId, setSelectedTemuanId] = useState<string | null>(null);
  const [statusMessage, setStatusMessage] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
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
                Office.context?.requirements?.isSetSupported("WordApi", v) ?? false,
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

  // Filter temuan
  const filteredTemuan = useMemo(() => {
    if (filterSeverity === "semua") return temuanList;
    return temuanList.filter((t) => t.tingkat_keparahan === filterSeverity);
  }, [temuanList, filterSeverity]);

  // Statistik temuan
  const stats = useMemo(() => {
    return {
      total: temuanList.length,
      tinggi: temuanList.filter((t) => t.tingkat_keparahan === "tinggi").length,
      sedang: temuanList.filter((t) => t.tingkat_keparahan === "sedang").length,
      rendah: temuanList.filter((t) => t.tingkat_keparahan === "rendah").length,
      diterima: temuanList.filter((t) => t.status === "diterima").length,
      ditolak: temuanList.filter((t) => t.status === "ditolak").length,
    };
  }, [temuanList]);

  // Gate legal: periksa apakah ada temuan dengan rujukan placeholder
  const adaRujukanBelumVerifikasi = useMemo(() => {
    return temuanList.some(
      (t) => t.rujukan.butir === "..." || t.rujukan.kutipan === "..."
    );
  }, [temuanList]);

  // Jalankan Analisis
  const handleJalankanAnalisis = async () => {
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

      const reqBody: AnalisisRequest = { paragraf: paragraphs };
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
        if (hasil.dikomentari > 0) {
          const bagianSorotan =
            hasil.disorot > 0
              ? hasil.memakaiWarnaFont
                ? `${hasil.disorot} bagian diwarnai menurut tingkat keparahan (merah/kuning/toska) dan `
                : `${hasil.disorot} bagian disorot dan `
              : "Sorotan warna tidak dapat dipasang di Word ini, tetapi ";
          setInfoPenandaan(
            `${bagianSorotan}${hasil.dikomentari} komentar dipasang di dokumen. ` +
              `Belum permanen — warna dan komentar temuan yang kamu Tolak akan ` +
              `dihapus kembali. Simpan dokumen hanya setelah semua temuan ditinjau.`
          );
        } else if (hasil.disorot > 0) {
          setInfoPenandaan(
            "Bagian bermasalah disorot, tetapi komentar tidak dapat dipasang " +
              "(WordApi 1.4 tidak tersedia di Word ini)."
          );
        } else {
          setInfoPenandaan(null);
        }
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

  // Terima temuan: ubah status jadi diterima & sematkan komentar permanen di Word (Lapis 2)
  const handleTerima = async (temuan: Temuan) => {
    updateStatus(temuan.id, "diterima");
    if (inWord) {
      // Komentarnya sudah terpasang sejak analisis, jadi Terima hanya melepas
      // sorotannya: yang tinggal di dokumen adalah komentar, dan itu memang
      // yang dibawa ke rapat pembahasan.
      await hapusSorotan(temuan);
      setStatusMessage(
        `Temuan ${temuan.aturan_id} diterima. Komentarnya tetap di dokumen.`
      );
    } else {
      setStatusMessage(`Status temuan ${temuan.aturan_id} diubah menjadi 'Diterima'.`);
    }
  };

  // Tolak temuan: ubah status jadi ditolak
  const handleTolak = async (temuan: Temuan) => {
    updateStatus(temuan.id, "ditolak");
    if (inWord) {
      // Ditolak berarti tidak ada jejak apa pun yang tertinggal di dokumen —
      // sorotan dilepas DAN komentarnya dihapus.
      await hapusSorotan(temuan);
      await hapusKomentarTemuan(temuan);
      setStatusMessage(
        `Temuan ${temuan.aturan_id} ditolak. Sorotan dan komentarnya dihapus dari dokumen.`
      );
      return;
    }
    setStatusMessage(`Status temuan ${temuan.aturan_id} diubah menjadi 'Ditolak'.`);
  };

  // Salin teks usulan ke clipboard
  const handleSalinUsulan = (temuanId: string, teks: string) => {
    navigator.clipboard.writeText(teks);
    setCopiedId(temuanId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  // Ubah status temuan
  const updateStatus = (id: string, newStatus: StatusTemuan) => {
    setTemuanList((prev) =>
      prev.map((t) => (t.id === id ? { ...t, status: newStatus } : t))
    );
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 text-slate-900 font-sans antialiased text-xs">
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

          <button
            onClick={handleJalankanAnalisis}
            disabled={analyzing}
            className={`w-full py-2 px-3 rounded font-semibold text-white transition flex items-center justify-center gap-1.5 shadow-xs ${
              analyzing
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

        {/* Results Summary & Filter Bar */}
        {temuanList.length > 0 && (
          <div className="space-y-1.5">
            <div className="grid grid-cols-4 gap-1 text-center font-medium text-[10px]">
              <button
                onClick={() => setFilterSeverity("semua")}
                className={`p-1.5 rounded border transition ${
                  filterSeverity === "semua"
                    ? "bg-slate-800 text-white border-slate-800"
                    : "bg-white text-slate-700 border-slate-200 hover:bg-slate-100"
                }`}
              >
                <div>Semua</div>
                <div className="font-bold text-[12px]">{stats.total}</div>
              </button>
              <button
                onClick={() => setFilterSeverity("tinggi")}
                className={`p-1.5 rounded border transition ${
                  filterSeverity === "tinggi"
                    ? "bg-rose-700 text-white border-rose-700"
                    : "bg-rose-50 text-rose-800 border-rose-200 hover:bg-rose-100"
                }`}
              >
                <div>Tinggi</div>
                <div className="font-bold text-[12px]">{stats.tinggi}</div>
              </button>
              <button
                onClick={() => setFilterSeverity("sedang")}
                className={`p-1.5 rounded border transition ${
                  filterSeverity === "sedang"
                    ? "bg-amber-600 text-white border-amber-600"
                    : "bg-amber-50 text-amber-800 border-amber-200 hover:bg-amber-100"
                }`}
              >
                <div>Sedang</div>
                <div className="font-bold text-[12px]">{stats.sedang}</div>
              </button>
              <button
                onClick={() => setFilterSeverity("rendah")}
                className={`p-1.5 rounded border transition ${
                  filterSeverity === "rendah"
                    ? "bg-indigo-700 text-white border-indigo-700"
                    : "bg-indigo-50 text-indigo-800 border-indigo-200 hover:bg-indigo-100"
                }`}
              >
                <div>Rendah</div>
                <div className="font-bold text-[12px]">{stats.rendah}</div>
              </button>
            </div>

            <div className="flex items-center justify-between text-[10px] text-slate-500 px-1">
              <span>{paragrafCount} paragraf diperiksa</span>
              <span>
                {stats.diterima > 0 && <span className="text-emerald-700 font-semibold">{stats.diterima} diterima &bull; </span>}
                {stats.ditolak > 0 && <span className="text-slate-500 line-through">{stats.ditolak} ditolak</span>}
              </span>
            </div>
          </div>
        )}

        {/* Finding Cards List */}
        <div className="space-y-2.5">
          {filteredTemuan.map((temuan) => {
            const isSelected = selectedTemuanId === temuan.id;
            const isPlaceholderRujukan =
              temuan.rujukan.butir === "..." || temuan.rujukan.kutipan === "...";

            // Border color by severity
            let severityBorder = "border-l-indigo-500";
            let severityBadgeBg = "bg-indigo-50 text-indigo-700 border-indigo-200";
            if (temuan.tingkat_keparahan === "tinggi") {
              severityBorder = "border-l-rose-500";
              severityBadgeBg = "bg-rose-50 text-rose-700 border-rose-200";
            } else if (temuan.tingkat_keparahan === "sedang") {
              severityBorder = "border-l-amber-500";
              severityBadgeBg = "bg-amber-50 text-amber-700 border-amber-200";
            }

            return (
              <div
                key={temuan.id}
                className={`bg-white rounded-lg border border-slate-200 shadow-2xs border-l-4 ${severityBorder} p-3 space-y-2 transition ${
                  isSelected ? "ring-2 ring-blue-500/40 bg-blue-50/20" : ""
                }`}
              >
                {/* Card Header */}
                <div className="flex items-center justify-between gap-1">
                  <div className="flex items-center gap-1.5">
                    <span className="font-mono font-bold text-slate-800 text-[11px] bg-slate-100 px-1.5 py-0.5 rounded">
                      {temuan.aturan_id}
                    </span>
                    <span
                      className={`text-[9px] font-semibold px-1.5 py-0.5 rounded border uppercase tracking-wider ${severityBadgeBg}`}
                    >
                      {temuan.tingkat_keparahan}
                    </span>
                  </div>
                  <div className="flex items-center gap-1">
                    {temuan.status === "diterima" && (
                      <span className="bg-emerald-100 text-emerald-800 font-medium px-1.5 py-0.5 rounded text-[9px]">
                        ✓ Diterima
                      </span>
                    )}
                    {temuan.status === "ditolak" && (
                      <span className="bg-slate-200 text-slate-600 font-medium px-1.5 py-0.5 rounded text-[9px] line-through">
                        Ditolak
                      </span>
                    )}
                    {temuan.status === "belum_ditinjau" && (
                      <span className="bg-slate-100 text-slate-500 px-1.5 py-0.5 rounded text-[9px]">
                        Belum Ditinjau
                      </span>
                    )}
                  </div>
                </div>

                {/* Excerpt / Teks Asli */}
                <div className="bg-slate-50 p-1.5 rounded border border-slate-100 text-[10px] text-slate-700 font-mono">
                  <span className="text-slate-400 select-none">
                    Paragraf #{temuan.lokasi.paragraf_index + 1}:{" "}
                  </span>
                  <span className="text-rose-900 bg-rose-50/60 font-semibold px-0.5 rounded">
                    &ldquo;{temuan.lokasi.teks_asli}&rdquo;
                  </span>
                </div>

                {/* Catatan Pelanggaran Kaidah */}
                <p className="text-slate-800 text-[11px] leading-relaxed">
                  {temuan.catatan}
                </p>

                {/* Usulan Rumusan (Jika Ada) */}
                {temuan.usulan_rumusan && (
                  <div className="bg-emerald-50/70 border border-emerald-200 rounded p-2 space-y-1.5">
                    <div className="flex items-center justify-between text-[10px] text-emerald-900 font-semibold">
                      <span>Usulan Rumusan Baku:</span>
                      <button
                        onClick={() =>
                          handleSalinUsulan(temuan.id, temuan.usulan_rumusan!)
                        }
                        className="text-emerald-700 hover:text-emerald-900 text-[9px] underline flex items-center gap-0.5"
                      >
                        {copiedId === temuan.id ? "Tersalin!" : "Salin Teks"}
                      </button>
                    </div>
                    <div className="font-mono text-[10px] text-emerald-950 bg-white/80 p-1.5 rounded border border-emerald-100 leading-snug">
                      {temuan.usulan_rumusan}
                    </div>
                  </div>
                )}

                {/* Detail Dasar Hukum (KMK 527) */}
                <details className="text-[10px] border border-slate-100 rounded bg-slate-50/50 p-1.5 group">
                  <summary className="cursor-pointer font-medium text-slate-600 flex items-center justify-between select-none">
                    <span className="flex items-center gap-1">
                      <span>Dasar Hukum: {temuan.rujukan.sumber}</span>
                      {isPlaceholderRujukan && (
                        <span className="text-[8px] bg-amber-200 text-amber-900 px-1 rounded font-bold">
                          Verifikasi Manual
                        </span>
                      )}
                    </span>
                    <span className="text-[9px] text-slate-400 group-open:rotate-180 transition-transform">
                      ▼
                    </span>
                  </summary>
                  <div className="mt-1.5 pt-1.5 border-t border-slate-200 space-y-1 text-slate-600">
                    <div>
                      <span className="font-semibold text-slate-700">Nomor Butir:</span>{" "}
                      {isPlaceholderRujukan ? (
                        <span className="italic text-amber-800">
                          Placeholder (belum diisi verifikasi visual Alfa)
                        </span>
                      ) : (
                        temuan.rujukan.butir
                      )}
                    </div>
                    <div>
                      <span className="font-semibold text-slate-700">Kutipan Kaidah:</span>{" "}
                      {isPlaceholderRujukan ? (
                        <span className="italic text-amber-800">
                          Kutipan visual belum diverifikasi
                        </span>
                      ) : (
                        `"${temuan.rujukan.kutipan}"`
                      )}
                    </div>
                    <div>
                      <a
                        href={temuan.rujukan.pdf_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-600 hover:underline flex items-center gap-0.5 font-medium"
                      >
                        Buka Dokumen di JDIH &rarr;
                      </a>
                    </div>
                  </div>
                </details>

                {/* Bottom Action Buttons */}
                <div className="pt-1.5 flex items-center justify-between border-t border-slate-100 gap-1">
                  <button
                    onClick={() => handleLompatKeLokasi(temuan)}
                    className="px-2 py-1 rounded bg-slate-100 hover:bg-slate-200 text-slate-700 font-medium text-[10px] transition"
                    title="Arahkan kursor dokumen ke paragraf ini"
                  >
                    Lompat ke Teks
                  </button>

                  <div className="flex items-center gap-1">
                    <button
                      onClick={() => handleTerima(temuan)}
                      className={`px-2.5 py-1 rounded text-[10px] font-medium transition ${
                        temuan.status === "diterima"
                          ? "bg-emerald-600 text-white"
                          : "bg-slate-100 hover:bg-emerald-50 text-slate-600 hover:text-emerald-700"
                      }`}
                      title="Terima temuan (menghasilkan komentar permanen di Word)"
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
                      title="Tolak temuan"
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
