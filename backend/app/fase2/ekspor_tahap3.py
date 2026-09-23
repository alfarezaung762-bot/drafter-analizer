"""Ekspor Tahap 3 — ALAT PENGEMBANG, bukan fitur penelaah.

Pasangan Ekspor Tahap 0, dan menjawab pertanyaan yang berbeda.

    Tahap 0   apa yang DIBACA model      — gratis, kapan saja
    Tahap 3   apa yang DITALAR model     — hasil analisis yang sudah berjalan

Langkah 2 meringkas tiap satuan jadi SATU BARIS. Kumpulan baris itulah yang
disebut PETA, dan Langkah 3 menalar di atas peta — bukan di atas teks penuh.
Harganya: peta kehilangan detail. Kalau ringkasan sebuah pasal meleset, Langkah
3 menalar di atas gambaran yang salah, dan tidak ada satu pun langkah
sesudahnya yang bisa mengetahuinya — Langkah 4 cuma menguji dugaan yang
terlanjur lahir, tidak pernah dugaan yang seharusnya lahir tetapi tidak.

Itulah yang membuat ekspor ini perlu ada: **satu-satunya cara memeriksa apakah
ringkasannya jujur adalah membacanya sendiri.**

=========================================================================
TIDAK MENJALANKAN APA PUN, DAN ITU DISENGAJA
=========================================================================

Ekspor ini membaca peta dan dugaan yang SUDAH tersimpan dari analisis yang
sudah berjalan. Ia tidak memanggil model, jadi tidak berbiaya — dan yang lebih
penting, ia memperlihatkan peta yang BENAR-BENAR dipakai, bukan peta baru yang
kebetulan mirip. Model tidak deterministik: menjalankan ulang Langkah 2
menghasilkan ringkasan yang berbeda, dan ekspor yang memperlihatkan peta lain
daripada yang dipakai akan menyesatkan orang yang sedang mencari bug.

Akibat yang perlu diketahui: tanpa analisis Fase 2 yang sudah pernah berjalan,
ekspor ini memang kosong. Itu keadaan yang benar, bukan kegagalan.

=========================================================================
WAJIB MEMANGGIL KODE YANG SAMA
=========================================================================

`susun_konteks_tetap` dan `tahap3_menalar.susun_bahan` dipanggil apa adanya.
Bagian "BAHAN LANGKAH 3" karena itu PERSIS muatan yang dikirim ke model, bukan
susunan ulang yang bisa menyimpang diam-diam.
"""

from __future__ import annotations

from typing import Optional

from app.fase2 import tahap2_baca, tahap3_menalar
from app.fase2.ekspor_tahap0 import identitas_naskah
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import saring
from app.models.pekerjaan import BarisPeta, Dugaan
from app.models.temuan import ParagrafInput

_GARIS = "=" * 78


def _judul(teks: str) -> list[str]:
    return ["", _GARIS, teks, _GARIS]


def _ya(nilai: bool) -> str:
    return "ya" if nilai else "tidak"


def susun_ekspor_tahap3(
    paragraf: list[ParagrafInput],
    peta: list[BarisPeta],
    dugaan: Optional[list[Dugaan]] = None,
    dokumen: str = "",
    pekerjaan: Optional[int] = None,
    keterangan: str = "",
    per_panggilan: int = 6,
) -> str:
    """Rangkai isi Ekspor Tahap 3 jadi satu teks. Fungsi murni.

    `dugaan` None berarti Langkah 3 BELUM PERNAH tercatat untuk pekerjaan ini —
    berbeda dari daftar kosong, yang berarti Langkah 3 berjalan dan memang
    tidak menemukan apa-apa. Keduanya dibedakan di keluaran.
    """
    baris: list[str] = [
        _GARIS,
        "EKSPOR TAHAP 3 — peta, dan apa yang ditalar di atasnya",
        _GARIS,
        f"Pekerjaan : {('#' + str(pekerjaan)) if pekerjaan else '(tidak diketahui)'}"
        + (f"  {keterangan}" if keterangan else ""),
        f"Baris peta: {len(peta)}",
    ]

    if not peta:
        baris.insert(3, f"Berkas    : {dokumen or '(tanpa nama)'}")
        baris += _judul("PETA KOSONG — TIDAK ADA YANG BISA DIEKSPOR")
        baris += [
            "  Ekspor ini membaca peta dari analisis Fase 2 yang SUDAH berjalan;",
            "  ia tidak menjalankan apa pun sendiri.",
            "",
            "  Kemungkinan sebabnya:",
            "    - Analisis Fase 2 belum pernah dijalankan pada dokumen ini.",
            "    - Yang dijalankan hanya pemeriksaan mekanis F2-0xx. Aturan itu",
            "      tidak memanggil model dan tidak menghasilkan peta.",
            "    - Naskahnya ditolak Langkah 0, jadi Langkah 2 tidak pernah mulai.",
            "",
            "  Nyalakan aturan penalaran (F2-1xx) di Pengaturan, jalankan analisis,",
            "  lalu ekspor lagi.",
            "",
        ]
        return "\n".join(baris)

    pohon = bangun_pohon(paragraf)
    daftar = ambil_definisi(pohon)
    disaring = saring(pohon)

    # Identitas naskah disisipkan di bawah garis kepala, memakai penyusun yang
    # sama dengan Ekspor Tahap 0 — supaya ekspor dari berkas yang keliru
    # ketahuan sebelum isinya dibaca panjang-panjang.
    baris[3:3] = identitas_naskah(paragraf, pohon, dokumen, per_panggilan, disaring)

    # --- Peta terurai: inilah yang perlu dibaca satu per satu -------------
    baris += _judul(f"PETA — SATU BARIS PER SATUAN ({len(peta)}). PERIKSA INI DULU.")
    baris += [
        "  Langkah 3 menalar HANYA di atas ringkasan di bawah, tidak pernah di",
        "  atas teks penuh. Ringkasan yang meleset membuat Langkah 3 menalar di",
        "  atas gambaran yang salah, dan tidak ada langkah sesudahnya yang bisa",
        "  mengetahuinya. Bandingkan tiap ringkasan dengan teks aslinya.",
        "",
        "  `merujuk` diisi PARSER, bukan model — isinya tidak bisa dikarang.",
    ]
    for b in peta:
        baris.append("")
        baris.append(f"  [{b.satuan_id}]")
        baris.append(f"      ringkasan    : {b.ringkasan!r}")
        baris.append(f"      memuat norma : {_ya(b.memuat_norma)}")
        baris.append(f"      merujuk      : {', '.join(b.merujuk) or '-'}")
        baris.append(f"      istilah      : {', '.join(b.istilah_dipakai) or '-'}")
        baris.append(f"      dugaan awal  : {b.dugaan or '-'}")

    # --- Satuan yang tidak sampai ke peta ---------------------------------
    #
    # Dua sebab yang berbeda jauh, dan keduanya perlu terlihat: dibuang
    # penyaring Langkah 1 (disengaja), atau lolos penyaring tetapi tidak
    # muncul di peta (Langkah 2 gagal membacanya — itu bug).
    di_peta = {b.satuan_id for b in peta}
    dibuang = {s.id for s, _ in disaring.dilewati}
    hilang = [s.id for s in disaring.dibaca if s.id not in di_peta]

    baris += _judul("SATUAN YANG TIDAK MASUK PETA")
    baris.append(f"  Dibuang penyaring Langkah 1 : {len(dibuang)}")
    baris.append("      (teks utuhnya ada di Ekspor Tahap 0)")
    for sid, alasan in [(s.id, a) for s, a in disaring.dilewati]:
        baris.append(f"      {sid}   {alasan}")
    baris.append("")
    baris.append(f"  LOLOS penyaring tetapi hilang dari peta : {len(hilang)}")
    if hilang:
        baris.append("      INI BUG kalau tidak nol — satuan lolos Langkah 1 tetapi")
        baris.append("      Langkah 2 tidak menghasilkan barisnya.")
        for sid in hilang:
            baris.append(f"      {sid}")
    else:
        baris.append("      (nihil — seperti yang seharusnya)")

    # --- Bahan yang dikirim ke Langkah 3 ----------------------------------
    konteks = tahap2_baca.susun_konteks_tetap(pohon, daftar)
    bahan = tahap3_menalar.susun_bahan(peta, konteks)
    baris += _judul(f"BAHAN LANGKAH 3 — PERSIS yang dikirim ({len(bahan)} huruf)")
    baris.append("  Satu panggilan untuk seluruh dokumen. Konteks tetap ikut di dalamnya.")
    baris.append("")
    baris.append(bahan)

    # --- Hasil Langkah 3 --------------------------------------------------
    if dugaan is None:
        baris += _judul("HASIL LANGKAH 3 — TIDAK TERCATAT")
        baris += [
            "  Petanya ada, tetapi dugaannya tidak. Dugaan disimpan di memori",
            "  backend, jadi ia hilang saat backend restart sementara peta tetap",
            "  bertahan di basis data.",
            "",
            "  Jalankan analisis lagi untuk mencatatnya. Petanya dipakai ulang,",
            "  jadi Langkah 2 tidak dibayar dua kali.",
        ]
    elif not dugaan:
        baris += _judul("HASIL LANGKAH 3 — DUGAAN (0)")
        baris += [
            "  Langkah 3 berjalan dan tidak menemukan apa pun. Itu hasil yang sah.",
            "",
            "  Tetapi periksa dulu peta di atas: dugaan yang tidak lahir karena",
            "  ringkasannya terlalu miskin tidak bisa dibedakan dari dugaan yang",
            "  tidak lahir karena naskahnya memang bersih.",
        ]
    else:
        baris += _judul(f"HASIL LANGKAH 3 — DUGAAN ({len(dugaan)})")
        baris.append("  BELUM temuan. Semuanya masih harus lolos Langkah 4 pada teks")
        baris.append("  utuhnya, lalu Langkah 5, sebelum boleh menyentuh naskah.")
        for ke, d in enumerate(dugaan, start=1):
            baris.append("")
            baris.append(
                f"  {ke}. [{d.satuan_id}]  jenis={d.jenis}  eksternal={_ya(d.eksternal)}"
            )
            if d.satuan_lain:
                baris.append(f"      bertabrakan dengan : {d.satuan_lain}")
            baris.append(f"      alasan : {d.alasan}")
        luar = sum(1 for d in dugaan if d.eksternal)
        baris.append("")
        baris.append(
            f"  {luar} dari {len(dugaan)} bertanda eksternal — hanya yang bertanda"
        )
        baris.append("  itulah yang dicarikan pembanding ke OpenSearch di Langkah 6.")

    baris.append("")
    return "\n".join(baris)
