"""Ekspor Tahap 2 — ALAT PENGEMBANG: perkiraan token, lalu bahan PERSIS untuk AI.

Bagian atasnya perkiraan token — per bagian naskah, total bahan terhadap
anggaran, dan per panggilan tahap 3 yang direncanakan. Diminta penelaah
28 Sep 2026: biaya harus bisa diramalkan sebelum tombol berbayar ditekan.

Sesudahnya bahan itu sendiri, persis seperti ikut di depan tiap panggilan
tahap 3 dan 4, lalu fakta lampiran persis seperti ikut di panggilan F2-106.
Keduanya dirangkai fungsi yang sama dengan yang mengirimnya ke model, jadi
ekspornya tidak bisa menyimpang.

Tidak memanggil AI, tidak berbiaya.
"""

from __future__ import annotations

from typing import Optional

from app.models.temuan import KerangkaTabel, ParagrafInput, Temuan
from app.telaah import tahap3_cari_dugaan
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import angka, hitung_token, susun_bahan

# Perkiraan tambahan pesan tahap 4 di luar bahan: instruksi, dugaan, satuan
# yang diuji, dan yang dirujuknya.
_TAMBAHAN_TAHAP4 = 2500


def susun_ekspor_tahap2(
    paragraf: list[ParagrafInput],
    tabel_raksasa: Optional[list[KerangkaTabel]] = None,
    temuan_fase1: Optional[list[Temuan]] = None,
    anggaran: int = 100_000,
    aturan_aktif: Optional[list[str]] = None,
    pasal_per_fokus: int = tahap3_cari_dugaan.PASAL_PER_FOKUS,
) -> str:
    """Perkiraan token dan bahan naskah ini. Fungsi murni."""
    pohon = bangun_pohon(paragraf)
    if pohon.gagal:
        return f"Tidak ada yang dikirim ke AI — Fase 2 tidak dijalankan: {pohon.gagal}\n"

    fase1 = list(temuan_fase1 or [])
    bahan = susun_bahan(paragraf, pohon, fase1, tabel_raksasa, anggaran)
    dipakai = None if aturan_aktif is None else {a.strip().upper() for a in aturan_aktif}
    rencana = tahap3_cari_dugaan.rencana(
        pohon, bahan, dipakai, ada_fase1=bool(fase1), per_fokus=pasal_per_fokus
    )
    t = bahan.token
    total = bahan.total_token
    if bahan.kerangka:
        status = "melewati anggaran — tabel data sejenis di lampiran diringkas jadi kerangka"
    elif total > anggaran:
        status = "melewati anggaran, tetapi tidak ada tabel data yang bisa diringkas — dikirim utuh"
    else:
        status = "masuk anggaran — seluruhnya dikirim utuh"

    baris = [
        "===== TAHAP 2 · PERKIRAAN TOKEN =====",
        f"Cara hitung      : {bahan.cara_hitung}",
        f"Naskah           : {angka(t['naskah'])} token (pembukaan, batang tubuh, penutup)",
        f"Lampiran         : {angka(t['lampiran'])} token",
        f"Temuan Fase 1    : {angka(t['temuan fase 1'])} token",
        f"Bahan utuh       : {angka(total)} token — anggaran {angka(anggaran)}: {status}",
    ]
    baris += [f"Kerangka         : {k}" for k in bahan.kerangka]

    per_panggilan = [hitung_token(pg.peran) + hitung_token(pg.pesan) for pg in rencana]
    baris += ["", f"Tahap 3 — {len(rencana)} panggilan direncanakan (belum termasuk tanya ulang):"]
    baris += [f"  {pg.judul}: ±{angka(n)} token masuk" for pg, n in zip(rencana, per_panggilan)]
    baris.append(f"  Jumlah: ±{angka(sum(per_panggilan))} token masuk")
    baris.append(
        f"Tahap 4 — satu panggilan per dugaan, masing-masing ±"
        f"{angka(total + _TAMBAHAN_TAHAP4)} token masuk ditambah hasil alat; "
        "jumlah dugaannya baru diketahui sesudah tahap 3."
    )
    baris += [
        "",
        "===== TAHAP 2 · BAHAN — persis, ikut di depan tiap panggilan tahap 3 dan 4 =====",
        bahan.teks,
        "",
        "===== TAHAP 2 · FAKTA LAMPIRAN — persis, ikut di panggilan lampiran (F2-106) =====",
        bahan.fakta_lampiran,
    ]
    return "\n".join(baris) + "\n"
