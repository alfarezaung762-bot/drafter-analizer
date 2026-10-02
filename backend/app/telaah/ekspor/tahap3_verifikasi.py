"""Ekspor Tahap 3 (Fase 4) — ALAT PENGEMBANG: lolos / gugur di gerbang, dan alasannya.

Tiga bagian: temuan yang LOLOS, calon yang gugur — ditolak penilai kedua,
gugur atau diturunkan di gerbang — beserta alasannya, dan KUNCI JAWABAN
peralihan: temuan pemeriksaan kode yang lama, ketemu atau terlewat oleh
agen (rancangan Fase 4 bagian 4 langkah 8). Tidak memanggil AI.
"""

from __future__ import annotations


def susun_ekspor_tahap3_verifikasi(hasil) -> str:
    if hasil is None:
        return (
            "Hasil gerbang tidak tercatat — analisis Fase 4 belum berjalan pada dokumen "
            "ini, atau backend sudah dimulai ulang sejak itu.\n"
        )
    if not hasil.berjalan:
        return f"Analisis tidak sampai gerbang: {hasil.tidak_dijalankan}\n"
    baris = [f"===== TAHAP 3 · LOLOS JADI TEMUAN ({len(hasil.temuan)}) ====="]
    for t in hasil.temuan:
        letak = (
            "tidak ditandai — letak tidak pasti" if t.lokasi.paragraf_index < 0 else f"¶{t.lokasi.paragraf_index}"
        )
        bentuk = {"penggantian": "usulan", "penghapusan": "dibuang"}.get(t.jenis_tanda.value, "catatan")
        isi = f"T{t.nomor} {t.aturan_id} [{t.satuan_id or '-'}] {letak} — {bentuk}: {t.lokasi.teks_asli!r}"
        if t.usulan_rumusan:
            isi += f" → {t.usulan_rumusan!r} (sumber: {t.sumber_usulan})"
        if t.sisipan:
            isi += (
                f" · sisipan {t.sisipan.bentuk} {t.sisipan.penanda or ''} sesudah ¶{t.sisipan.sesudah_paragraf}: "
                f"{t.sisipan.teks!r} (sumber: {t.sisipan.sumber})"
            )
        if t.tanpa_sorot:
            isi += " · komentar tanpa sorot"
        baris.append(isi)
        baris.append(f"    {t.catatan}")
        if t.pembanding:
            baris.append(f"    pembanding: {t.pembanding}")
        r = t.rujukan
        baris.append(
            "    rujukan: "
            + ({"prioritas": "prioritas penelaah — tanpa baris rujukan", "tanpa": "tidak ada (tidak dikarang)"}.get(
                r.status, f"{r.sumber} {r.butir} [{r.status}]"
            ))
        )
    baris += ["", f"===== TAHAP 3 · DITOLAK, GUGUR, ATAU DITURUNKAN ({len(hasil.gugur)}) ====="]
    baris += hasil.gugur
    if hasil.peringatan:
        baris += ["", f"===== PERINGATAN ({len(hasil.peringatan)}) ====="]
        baris += hasil.peringatan
    if hasil.kunci_jawaban:
        ketemu = sum(1 for k in hasil.kunci_jawaban if k.startswith("KETEMU"))
        baris += [
            "",
            f"===== KUNCI JAWABAN PERALIHAN — temuan pemeriksaan kode lama ({len(hasil.kunci_jawaban)}): "
            f"ketemu {ketemu}, terlewat {len(hasil.kunci_jawaban) - ketemu} =====",
        ]
        baris += hasil.kunci_jawaban
    return "\n".join(baris) + "\n"
