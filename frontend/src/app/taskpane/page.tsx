"use client";

import { useState, useEffect } from "react";

interface ApiCheck {
  version: string;
  supported: boolean | null;
}

const API_VERSIONS = ["1.1", "1.4", "1.7", "1.8", "1.9"];

export default function TaskpanePage() {
  const [ready, setReady] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [checks, setChecks] = useState<ApiCheck[]>(
    API_VERSIONS.map((v) => ({ version: v, supported: null }))
  );

  useEffect(() => {
    Office.onReady((info) => {
      if (info.host === Office.HostType.Word) {
        setReady(true);
        const results = API_VERSIONS.map((v) => ({
          version: v,
          supported: Office.context.requirements.isSetSupported("WordApi", v),
        }));
        setChecks(results);
      } else {
        setError(
          `Host bukan Word (terdeteksi: ${info.host ?? "tidak diketahui"})`
        );
      }
    });
  }, []);

  if (error) {
    return (
      <main className="p-6 font-sans">
        <h1 className="text-xl font-bold text-red-600 mb-4">Error</h1>
        <p>{error}</p>
      </main>
    );
  }

  if (!ready) {
    return (
      <main className="p-6 font-sans">
        <p className="text-gray-500">Menunggu Office.onReady&hellip;</p>
      </main>
    );
  }

  return (
    <main className="p-6 font-sans">
      <h1 className="text-xl font-bold mb-4">
        Uji Kelayakan &mdash; WordApi Support
      </h1>
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="bg-gray-100">
            <th className="border px-3 py-2 text-left">WordApi Version</th>
            <th className="border px-3 py-2 text-left">Didukung?</th>
          </tr>
        </thead>
        <tbody>
          {checks.map(({ version, supported }) => (
            <tr key={version}>
              <td className="border px-3 py-2 font-mono">{version}</td>
              <td
                className={`border px-3 py-2 font-semibold ${
                  supported === null
                    ? "text-gray-400"
                    : supported
                    ? "text-green-600"
                    : "text-red-600"
                }`}
              >
                {supported === null
                  ? "—"
                  : supported
                  ? "✅ Ya"
                  : "❌ Tidak"}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
