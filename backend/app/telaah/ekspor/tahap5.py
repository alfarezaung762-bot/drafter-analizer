"""Ekspor Tahap 5 — ALAT PENGEMBANG: nasib tiap dugaan, lolos atau gugur, berikut alasannya.

Empat bagian, mengikuti jalannya dugaan:

    tahap 3   dugaan yang lahir, dari panggilan mana, dan catatan (pasal yang
              tidak dijawab, jawaban yang tidak terbaca, batas dugaan)
    tahap 4   tiap dugaan terbukti atau tidak, menurut model
    tahap 5   temuan yang LOLOS, dan yang GUGUR atau DITURUNKAN oleh kode

Alat yang cuma bilang "tidak ada temuan" tidak bisa dibedakan dari alat yang
rusak. Di sini tiap dugaan bisa ditelusuri sampai ke nasibnya. Tidak memanggil
AI — disusun dari hasil analisis yang baru berjalan.
"""

from __future__ import annotations

from app.telaah.alur import HasilLanjut
from app.telaah.tahap4_memastikan.memastikan import ATURAN


def susun_ekspor_tahap5(hasil: HasilLanjut) -> str:
    if not hasil.berjalan:
        return f"Fase 2 tidak dijalankan: {hasil.tidak_dijalankan}\n"

    baris = [f"===== TAHAP 3 · DUGAAN ({len(hasil.dugaan)}) ====="]
    for d in hasil.dugaan:
        lain = f" × [{d.satuan_lain}]" if d.satuan_lain else ""
        luar = " · eksternal" if d.eksternal else ""
        baris.append(
            f"{ATURAN.get(d.jenis, '?')} [{d.satuan_id}]{lain}{luar} — {d.alasan} ({d.asal})"
        )
    if hasil.jejak_tahap3:
        baris += ["", "Catatan tahap 3:"] + [f"  {c}" for c in hasil.jejak_tahap3]

    baris += ["", f"===== TAHAP 4 · MEMASTIKAN ({len(hasil.jejak_tahap4)}) ====="]
    baris += hasil.jejak_tahap4

    fase2 = [t for t in hasil.temuan if t.fase in (2, 3)]
    baris += ["", f"===== TAHAP 5 · LOLOS JADI TEMUAN ({len(fase2)}) ====="]
    for t in fase2:
        oleh = "AI" if t.skor is not None else "kode"
        letak = (
            "tidak ditandai — letak tidak pasti"
            if t.lokasi.paragraf_index < 0
            else f"paragraf {t.lokasi.paragraf_index}"
        )
        baris.append(
            f"T{t.nomor} {t.aturan_id} ({oleh}) [{t.satuan_id}] {letak} — "
            f"{t.jenis_tanda.value}: {t.lokasi.teks_asli!r} — {t.catatan}"
        )

    baris += ["", f"===== TAHAP 5 · GUGUR ATAU DITURUNKAN ({len(hasil.gugur)}) ====="]
    baris += hasil.gugur
    return "\n".join(baris) + "\n"
