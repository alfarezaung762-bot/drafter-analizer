"use client";

import { useCallback, useEffect, useRef, useState } from "react";

/* ─────────────── types ─────────────── */

interface VariabelInfo {
  nama: string;
  terisi: boolean;
  nilai_samaran: string;
}

interface LayananResult {
  layanan: string;
  terhubung: boolean;
  pesan: string;
  variabel: VariabelInfo[];
  detail?: Record<string, unknown>;
}

interface CekEnvResponse {
  semua_terhubung: boolean;
  layanan: LayananResult[];
}

interface ProxyResponse {
  backend_ok: boolean;
  backend_pesan: string;
  cek_env: CekEnvResponse | null;
}

/* ─────────────── icons (inline SVG) ─────────────── */

function IconCheck() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="10" fill="#10b981" />
      <path d="M6 10.5l2.5 2.5 5.5-5.5" stroke="#fff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

function IconCross() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <circle cx="10" cy="10" r="10" fill="#ef4444" />
      <path d="M7 7l6 6M13 7l-6 6" stroke="#fff" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function IconSpinner() {
  return (
    <svg className="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3" strokeDasharray="31.4 31.4" strokeLinecap="round" />
    </svg>
  );
}

function IconRefresh() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 4 23 10 17 10" />
      <polyline points="1 20 1 14 7 14" />
      <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </svg>
  );
}

function IconServer() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="20" height="8" rx="2" ry="2" />
      <rect x="2" y="14" width="20" height="8" rx="2" ry="2" />
      <line x1="6" y1="6" x2="6.01" y2="6" />
      <line x1="6" y1="18" x2="6.01" y2="18" />
    </svg>
  );
}

/* ─────────────── service icons ─────────────── */

function IconDatabase() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  );
}

function IconBrain() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2a7 7 0 0 1 7 7c0 2.38-1.19 4.47-3 5.74V17a2 2 0 0 1-2 2h-4a2 2 0 0 1-2-2v-2.26C6.19 13.47 5 11.38 5 9a7 7 0 0 1 7-7z" />
      <line x1="9" y1="21" x2="15" y2="21" />
      <line x1="10" y1="23" x2="14" y2="23" />
    </svg>
  );
}

function IconVector() {
  return (
    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="3" />
      <circle cx="4" cy="4" r="2" />
      <circle cx="20" cy="4" r="2" />
      <circle cx="4" cy="20" r="2" />
      <circle cx="20" cy="20" r="2" />
      <line x1="6" y1="6" x2="9.5" y2="9.5" />
      <line x1="18" y1="6" x2="14.5" y2="9.5" />
      <line x1="6" y1="18" x2="9.5" y2="14.5" />
      <line x1="18" y1="18" x2="14.5" y2="14.5" />
    </svg>
  );
}

const SERVICE_ICONS: Record<string, () => React.JSX.Element> = {
  OpenSearch: IconDatabase,
  "Azure OpenAI - Chat": IconBrain,
  "Azure OpenAI - Embedding": IconVector,
};

/* ─────────────── page ─────────────── */

export default function TestEnvPage() {
  const [loading, setLoading] = useState(false);
  const [backendOk, setBackendOk] = useState<boolean | null>(null);
  const [result, setResult] = useState<CekEnvResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [expanded, setExpanded] = useState<Set<string>>(new Set());
  const mountedRef = useRef(false);

  const toggleExpand = (nama: string) => {
    setExpanded((prev) => {
      const next = new Set(prev);
      if (next.has(nama)) next.delete(nama);
      else next.add(nama);
      return next;
    });
  };

  const runCheck = useCallback(async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    setBackendOk(null);

    try {
      // Fetch lewat proxy Next.js (server-side) untuk menghindari mixed content
      const res = await fetch("/api/cek-env", { signal: AbortSignal.timeout(40000) });
      if (!res.ok) throw new Error(`Proxy status ${res.status}`);
      const data: ProxyResponse = await res.json();

      setBackendOk(data.backend_ok);

      if (!data.backend_ok) {
        setError(data.backend_pesan);
      } else if (data.cek_env) {
        setResult(data.cek_env);
      } else if (data.backend_pesan) {
        setError(data.backend_pesan);
      }
    } catch (e: unknown) {
      setBackendOk(false);
      setError(`Gagal menghubungi proxy: ${e instanceof Error ? e.message : String(e)}`);
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-run on mount — hanya sekali setelah komponen benar-benar terpasang
  useEffect(() => {
    if (!mountedRef.current) {
      mountedRef.current = true;
      runCheck();
    }
  }, [runCheck]);

  const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
  const terhubung = result?.layanan.filter((l) => l.terhubung).length ?? 0;
  const total = result?.layanan.length ?? 0;

  return (
    <div style={styles.wrapper}>
      {/* ─── animated gradient background ─── */}
      <div style={styles.bgGlow} />

      <div style={styles.container}>
        {/* ─── header ─── */}
        <header style={styles.header}>
          <div style={styles.headerIcon}>
            <IconServer />
          </div>
          <div>
            <h1 style={styles.title}>Diagnostik Environment</h1>
            <p style={styles.subtitle}>
              Drafter Analiser — cek koneksi layanan Fase 2 &amp; 3
            </p>
          </div>
        </header>

        {/* ─── summary pill ─── */}
        {result && (
          <div
            style={{
              ...styles.summaryPill,
              background: result.semua_terhubung
                ? "linear-gradient(135deg, #065f46, #047857)"
                : "linear-gradient(135deg, #7f1d1d, #991b1b)",
            }}
          >
            <span style={styles.summaryEmoji}>
              {result.semua_terhubung ? "✅" : "⚠️"}
            </span>
            <span>
              {result.semua_terhubung
                ? "Semua layanan terhubung"
                : `${terhubung} dari ${total} layanan terhubung`}
            </span>
          </div>
        )}

        {/* ─── backend card ─── */}
        <div
          style={{
            ...styles.card,
            borderLeftColor:
              backendOk === null ? "#6b7280" : backendOk ? "#10b981" : "#ef4444",
          }}
        >
          <div style={styles.cardHeader}>
            <div style={styles.cardLeft}>
              <div style={{ ...styles.serviceIcon, color: backendOk ? "#10b981" : "#ef4444" }}>
                <IconServer />
              </div>
              <div>
                <h2 style={styles.cardTitle}>Backend FastAPI</h2>
                <p style={styles.cardMeta}>{API_BASE}</p>
              </div>
            </div>
            {loading && backendOk === null ? (
              <span style={styles.statusBadge}><IconSpinner /> Menghubungi…</span>
            ) : backendOk ? (
              <span style={{ ...styles.statusBadge, background: "rgba(16,185,129,.15)", color: "#10b981" }}>
                <IconCheck /> Terhubung
              </span>
            ) : backendOk === false ? (
              <span style={{ ...styles.statusBadge, background: "rgba(239,68,68,.15)", color: "#ef4444" }}>
                <IconCross /> Gagal
              </span>
            ) : null}
          </div>
          <div style={styles.varRow}>
            <span style={styles.varName}>NEXT_PUBLIC_API_BASE_URL</span>
            <code style={styles.varValue}>{API_BASE}</code>
            <span style={{ ...styles.dot, background: "#10b981" }} />
          </div>
        </div>

        {/* ─── service cards ─── */}
        {result?.layanan.map((svc) => {
          const SvcIcon = SERVICE_ICONS[svc.layanan] ?? IconServer;
          const isExpanded = expanded.has(svc.layanan);
          return (
            <div
              key={svc.layanan}
              style={{
                ...styles.card,
                borderLeftColor: svc.terhubung ? "#10b981" : "#ef4444",
              }}
            >
              <div
                style={styles.cardHeader}
                onClick={() => toggleExpand(svc.layanan)}
                role="button"
                tabIndex={0}
              >
                <div style={styles.cardLeft}>
                  <div style={{ ...styles.serviceIcon, color: svc.terhubung ? "#10b981" : "#ef4444" }}>
                    <SvcIcon />
                  </div>
                  <div>
                    <h2 style={styles.cardTitle}>{svc.layanan}</h2>
                    <p style={styles.cardMeta}>{svc.pesan}</p>
                  </div>
                </div>
                <div style={styles.headerRight}>
                  {svc.terhubung ? (
                    <span style={{ ...styles.statusBadge, background: "rgba(16,185,129,.15)", color: "#10b981" }}>
                      <IconCheck /> Terhubung
                    </span>
                  ) : (
                    <span style={{ ...styles.statusBadge, background: "rgba(239,68,68,.15)", color: "#ef4444" }}>
                      <IconCross /> Gagal
                    </span>
                  )}
                  <span
                    style={{
                      ...styles.chevron,
                      transform: isExpanded ? "rotate(180deg)" : "rotate(0deg)",
                    }}
                  >
                    ▾
                  </span>
                </div>
              </div>

              {/* expandable detail */}
              <div
                style={{
                  ...styles.expandArea,
                  maxHeight: isExpanded ? "600px" : "0px",
                  opacity: isExpanded ? 1 : 0,
                  padding: isExpanded ? "12px 20px 16px" : "0 20px",
                }}
              >
                <p style={styles.sectionLabel}>Variabel .env</p>
                {svc.variabel.map((v) => (
                  <div key={v.nama} style={styles.varRow}>
                    <span style={styles.varName}>{v.nama}</span>
                    <code style={styles.varValue}>{v.nilai_samaran}</code>
                    <span
                      style={{
                        ...styles.dot,
                        background: v.terisi ? "#10b981" : "#ef4444",
                      }}
                    />
                  </div>
                ))}

                {svc.detail && (
                  <>
                    <p style={{ ...styles.sectionLabel, marginTop: 16 }}>Detail</p>
                    <pre style={styles.detailPre}>
                      {JSON.stringify(svc.detail, null, 2)}
                    </pre>
                  </>
                )}
              </div>
            </div>
          );
        })}

        {/* ─── error banner ─── */}
        {error && (
          <div style={styles.errorBanner}>
            <strong>Error:</strong> {error}
          </div>
        )}

        {/* ─── refresh button ─── */}
        <button
          style={styles.refreshBtn}
          onClick={runCheck}
          disabled={loading}
        >
          {loading ? <IconSpinner /> : <IconRefresh />}
          {loading ? "Memeriksa…" : "Periksa Ulang"}
        </button>

        {/* ─── footer ─── */}
        <footer style={styles.footer}>
          Halaman ini hanya untuk diagnostik pengembangan. Tidak ditampilkan ke pengguna akhir.
        </footer>
      </div>
    </div>
  );
}

/* ─────────────── inline styles (no external CSS) ─────────────── */

const styles: Record<string, React.CSSProperties> = {
  wrapper: {
    position: "relative",
    minHeight: "100vh",
    background: "#0c0c14",
    color: "#e5e7eb",
    fontFamily: "'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif",
    overflow: "hidden",
  },
  bgGlow: {
    position: "fixed",
    top: "-40%",
    left: "-20%",
    width: "140%",
    height: "140%",
    background:
      "radial-gradient(ellipse at 30% 20%, rgba(59,130,246,.08) 0%, transparent 60%), " +
      "radial-gradient(ellipse at 70% 80%, rgba(139,92,246,.06) 0%, transparent 60%)",
    pointerEvents: "none",
    zIndex: 0,
  },
  container: {
    position: "relative",
    zIndex: 1,
    maxWidth: 680,
    margin: "0 auto",
    padding: "48px 20px 64px",
  },
  header: {
    display: "flex",
    alignItems: "center",
    gap: 16,
    marginBottom: 32,
  },
  headerIcon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: 48,
    height: 48,
    borderRadius: 12,
    background: "linear-gradient(135deg, #1e3a5f, #312e81)",
    color: "#93c5fd",
    flexShrink: 0,
  },
  title: {
    margin: 0,
    fontSize: 24,
    fontWeight: 700,
    letterSpacing: "-0.02em",
    background: "linear-gradient(135deg, #93c5fd, #c4b5fd)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },
  subtitle: {
    margin: "4px 0 0",
    fontSize: 13,
    color: "#9ca3af",
    fontWeight: 400,
  },
  summaryPill: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "12px 20px",
    borderRadius: 12,
    fontSize: 14,
    fontWeight: 600,
    color: "#fff",
    marginBottom: 24,
    boxShadow: "0 2px 12px rgba(0,0,0,.3)",
  },
  summaryEmoji: {
    fontSize: 20,
  },
  card: {
    background: "rgba(255,255,255,.04)",
    border: "1px solid rgba(255,255,255,.08)",
    borderLeft: "3px solid #6b7280",
    borderRadius: 12,
    marginBottom: 16,
    backdropFilter: "blur(12px)",
    overflow: "hidden",
    transition: "border-color .3s, box-shadow .3s",
    boxShadow: "0 1px 4px rgba(0,0,0,.2)",
  },
  cardHeader: {
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "16px 20px",
    cursor: "pointer",
    userSelect: "none" as const,
  },
  cardLeft: {
    display: "flex",
    alignItems: "center",
    gap: 14,
    minWidth: 0,
  },
  serviceIcon: {
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    width: 44,
    height: 44,
    borderRadius: 10,
    background: "rgba(255,255,255,.05)",
    flexShrink: 0,
  },
  cardTitle: {
    margin: 0,
    fontSize: 15,
    fontWeight: 600,
    color: "#f3f4f6",
  },
  cardMeta: {
    margin: "3px 0 0",
    fontSize: 12,
    color: "#9ca3af",
    wordBreak: "break-all" as const,
  },
  headerRight: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    flexShrink: 0,
  },
  statusBadge: {
    display: "inline-flex",
    alignItems: "center",
    gap: 6,
    padding: "4px 12px",
    borderRadius: 20,
    fontSize: 12,
    fontWeight: 600,
    background: "rgba(255,255,255,.08)",
    color: "#d1d5db",
    whiteSpace: "nowrap" as const,
  },
  chevron: {
    fontSize: 16,
    color: "#6b7280",
    transition: "transform .25s ease",
  },
  expandArea: {
    overflow: "hidden",
    transition: "max-height .35s ease, opacity .3s ease, padding .3s ease",
    borderTop: "1px solid rgba(255,255,255,.06)",
  },
  sectionLabel: {
    margin: "0 0 8px",
    fontSize: 11,
    fontWeight: 700,
    textTransform: "uppercase" as const,
    letterSpacing: "0.08em",
    color: "#6b7280",
  },
  varRow: {
    display: "flex",
    alignItems: "center",
    gap: 10,
    padding: "6px 0",
    fontSize: 13,
    borderBottom: "1px solid rgba(255,255,255,.04)",
  },
  varName: {
    fontWeight: 500,
    color: "#d1d5db",
    flexShrink: 0,
  },
  varValue: {
    flex: 1,
    textAlign: "right" as const,
    color: "#9ca3af",
    fontFamily: "'Geist Mono', 'Fira Code', monospace",
    fontSize: 12,
    overflow: "hidden",
    textOverflow: "ellipsis",
    whiteSpace: "nowrap" as const,
  },
  dot: {
    width: 8,
    height: 8,
    borderRadius: "50%",
    flexShrink: 0,
  },
  detailPre: {
    background: "rgba(0,0,0,.3)",
    border: "1px solid rgba(255,255,255,.06)",
    borderRadius: 8,
    padding: "12px 16px",
    fontSize: 12,
    lineHeight: 1.6,
    color: "#a5b4fc",
    fontFamily: "'Geist Mono', 'Fira Code', monospace",
    overflowX: "auto" as const,
    margin: 0,
  },
  errorBanner: {
    background: "rgba(239,68,68,.12)",
    border: "1px solid rgba(239,68,68,.3)",
    color: "#fca5a5",
    borderRadius: 12,
    padding: "14px 20px",
    fontSize: 13,
    lineHeight: 1.6,
    marginBottom: 20,
  },
  refreshBtn: {
    display: "inline-flex",
    alignItems: "center",
    gap: 8,
    padding: "10px 24px",
    borderRadius: 10,
    border: "1px solid rgba(255,255,255,.12)",
    background: "linear-gradient(135deg, rgba(59,130,246,.15), rgba(139,92,246,.15))",
    color: "#c4b5fd",
    fontSize: 14,
    fontWeight: 600,
    cursor: "pointer",
    transition: "all .2s",
    marginTop: 8,
  },
  footer: {
    marginTop: 40,
    textAlign: "center" as const,
    fontSize: 12,
    color: "#4b5563",
    fontStyle: "italic",
  },
};
