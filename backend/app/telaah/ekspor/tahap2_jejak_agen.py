"""Ekspor Tahap 2 (Fase 4) — ALAT PENGEMBANG: jejak agen, per putaran, tiap request.

Disusun per putaran ("Putaran 1/8 · Pasal 1–6"):

  - kepala ekspor: jumlah putaran, request, dan token seluruh analisis;
  - kepala tiap putaran: jumlah request agen + penilai, jumlah pemakaian tiap
    alat, token (masuk · keluar · dari cache), waktu, dan cara berakhir —
    selesai · ditagih · macet · dibatalkan;
  - tiap request berurutan: alat yang diminta beserta argumennya, hasil
    alatnya, kutipan yang ditolak `catat_temuan`, laporan `selesai`; lalu
    putusan penilai kedua — tidak ada yang dibuang diam-diam.

Alat dijalankan kode di antara dua request, bukan request ke AI — tidak
menambah jumlah request. Naskah di depan pesan tiap putaran tidak diulang di
sini (sudah di Ekspor Tahap 1); yang ditulis bagian TUGAS-nya.
"""

from __future__ import annotations

from collections import Counter

from app.telaah.tahap2_persiapan.bahan import angka


def _tugas(pesan_awal: str) -> str:
    """Bagian sesudah naskah — tugas putaran, persis."""
    return pesan_awal.rsplit("\n\n---\n\n", 1)[-1]


def susun_ekspor_tahap2_jejak(hasil) -> str:
    if hasil is None:
        return (
            "Jejak agen tidak tercatat — analisis Fase 4 belum berjalan pada dokumen "
            "ini, atau backend sudah dimulai ulang sejak itu.\n"
        )
    req_agen = sum(1 for h in hasil.putaran for x in h.langkah if not x.dari_simpanan)
    req_penilai = sum(1 for n in hasil.penilai.values() if not n.dari_simpanan and n.percakapan)
    req_label = 1 if hasil.label is not None else 0
    o = hasil.ongkos
    baris = [
        "===== TAHAP 2 · JEJAK AGEN =====",
        f"Putaran: {len(hasil.putaran)} · request: {req_agen + req_penilai + req_label} "
        f"(agen {req_agen} + penilai {req_penilai} + label {req_label}) · token masuk "
        f"{angka(o.token_masuk)} (dari cache {angka(o.token_cache)}) · keluar {angka(o.token_keluar)}",
    ]
    if hasil.pilihan is not None:
        baris.append("Analisis dikirim: " + ", ".join(a.kode for a in hasil.pilihan.dikirim))
        for kode, alasan in hasil.pilihan.tidak_dikirim:
            baris.append(f"Tidak dikirim: {kode} — {alasan}")
    if hasil.tidak_dijalankan:
        baris.append(f"TIDAK DIJALANKAN: {hasil.tidak_dijalankan}")

    for h in hasil.putaran:
        alat = Counter(nama for x in h.langkah for nama, _, _ in x.alat)
        masuk = sum(x.token_masuk for x in h.langkah)
        keluar = sum(x.token_keluar for x in h.langkah)
        cache = sum(x.token_cache for x in h.langkah)
        n = h.penilai
        baris += [
            "",
            f"===== {h.putaran.judul} =====",
            f"berakhir: {h.berakhir or '?'} · {len(h.langkah)} request agen"
            + (" + 1 penilai" if n is not None and n.percakapan else "")
            + f" · alat: {', '.join(f'{k} ×{v}' for k, v in alat.most_common()) or '-'}"
            + f" · token masuk {angka(masuk)} (cache {angka(cache)}) · keluar {angka(keluar)}"
            + f" · {h.detik:g} dtk",
            f"analisis: {', '.join(a.kode for a in h.putaran.analisis)}"
            + (f" · pasal fokus: {', '.join(h.putaran.fokus)}" if h.putaran.fokus else ""),
            "--- tugas putaran (persis, sesudah naskah) ---",
            _tugas(h.pesan_awal),
        ]
        for x in h.langkah:
            kepala = (
                f"--- request {x.nomor} · masuk {angka(x.token_masuk)} · cache {angka(x.token_cache)}"
                f" · keluar {angka(x.token_keluar)}"
                + (" · dari simpanan (tidak dibayar ulang)" if x.dari_simpanan else "")
                + " ---"
            )
            baris.append(kepala)
            for c in x.catatan:
                baris.append(f"[kode] {c}")
            if x.teks.strip():
                baris.append("teks agen: " + x.teks.strip())
            for nama, argumen, hasil_alat in x.alat:
                baris.append(f"> {nama}({argumen})")
                baris.append("< " + hasil_alat.replace("\n", "\n  "))
        if h.catatan.ditolak_catat:
            baris.append(f"catat_temuan ditolak saat itu juga ({len(h.catatan.ditolak_catat)}):")
            baris += [f"  - {x}" for x in h.catatan.ditolak_catat]
        if h.catatan.laporan:
            baris.append("laporan selesai:")
            baris += [
                f"  {p} × {k}: {s}" + (f" — {a}" if a else "")
                for (p, k), (s, a) in sorted(h.catatan.laporan.items())
            ]
        if h.tidak_diperiksa:
            baris.append("TIDAK DIPERIKSA: " + ", ".join(f"{p} × {k}" for p, k in h.tidak_diperiksa))
        if n is not None and n.percakapan:
            baris.append(
                f"--- penilai kedua · masuk {angka(n.token_masuk)} · keluar {angka(n.token_keluar)}"
                + (" · dari simpanan" if n.dari_simpanan else "")
                + (" · jawaban TIDAK terbaca" if not n.terbaca else "")
                + " ---"
            )
            for c in h.catatan.calon:
                putusan, alasan = n.putusan.get(c.nomor, ("?", ""))
                baris.append(f"  {c.nomor} {c.analisis} [{c.letak}] {c.kutipan!r}: {putusan.upper()} — {alasan}")
    return "\n".join(baris) + "\n"
