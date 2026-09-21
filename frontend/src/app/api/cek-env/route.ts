/**
 * Proxy server-side ke backend /health dan /cek-env.
 *
 * Menghindari masalah mixed content (HTTPS frontend → HTTP backend)
 * karena fetch terjadi di server Next.js, bukan di browser.
 */

import { NextResponse } from "next/server";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function GET() {
  const hasil: Record<string, unknown> = {
    backend_ok: false,
    backend_pesan: "",
    cek_env: null,
  };

  // 1) Cek backend health
  try {
    const healthRes = await fetch(`${API_BASE}/health`, {
      signal: AbortSignal.timeout(8000),
    });
    if (!healthRes.ok) throw new Error(`Status ${healthRes.status}`);
    hasil.backend_ok = true;
  } catch (e: unknown) {
    hasil.backend_pesan = `Backend tidak bisa dijangkau di ${API_BASE}: ${e instanceof Error ? e.message : String(e)}`;
    return NextResponse.json(hasil);
  }

  // 2) Cek env connections
  try {
    const envRes = await fetch(`${API_BASE}/cek-env`, {
      signal: AbortSignal.timeout(30000),
    });
    if (!envRes.ok) throw new Error(`Status ${envRes.status}`);
    hasil.cek_env = await envRes.json();
  } catch (e: unknown) {
    hasil.backend_pesan = `Gagal memanggil /cek-env: ${e instanceof Error ? e.message : String(e)}`;
  }

  return NextResponse.json(hasil);
}
