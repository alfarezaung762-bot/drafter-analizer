"""TAHAP 4 — MEMASTIKAN tiap dugaan, dengan naskah utuh dan alat.

Ini gerbang yang membuat seluruh jalur AI bisa dipertanggungjawabkan. Tahap 3
mencari; di sini tiap dugaan diuji satu per satu, dan yang tidak terbukti
DIGUGURKAN.

    Dugaan yang gugur adalah hasil yang baik, bukan kegagalan.

Tiap panggilan membawa bahan yang SAMA dengan tahap 3 — naskah utuh, di depan
pesan — ditambah satuan yang diuji, batang kalimat induknya, dan isi yang
dirujuknya (dicari KODE, CLAUDE.md butir 14). Model boleh memakai alat:
mencari di seluruh naskah, membuka tabel, menjumlah kolom (`alat.py`).
Klaim "X tidak ada" wajib ditulis di `tidak_ada`, dan tahap 5 membuktikannya.

Tiga jalur, bedanya bukan sekadar teknis:

    tunggal    satu satuan diuji. F2-101, F2-102, F2-103, F2-105.
    tabrakan   DUA satuan diuji DALAM SATU PANGGILAN (F2-104). Wajib begitu:
               pengecualian yang sah ("kecuali sebagaimana dimaksud dalam
               Pasal 12") menyerupai tabrakan kalau cuma satu sisinya dibaca.
               Model juga harus memilih SATUAN MANA yang menyimpang, karena
               hanya satu yang akan ditandai.
    lampiran   F2-106 — fakta lampiran dari kode ikut dilampirkan.

Keluarannya CalonTemuan — masih belum menyentuh naskah. Tahap 5 yang
membuktikan kutipannya benar-benar ada, dan tahap 5 yang memutuskan.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

from app.bersama import prompt as P
from app.bersama.llm import Blok, Klien, Ongkos, baca_jawaban, skor_sah, tanya_dengan_alat
from app.models.pekerjaan import CalonTemuan, Dugaan
from app.models.satuan import PohonSatuan
from app.telaah.tahap1_parser.rujukan import blok_dirujuk
from app.telaah.tahap2_persiapan.bahan import Bahan
from app.telaah.tahap4_memastikan.alat import daftar_alat, jalankan_alat

# Jenis dugaan → aturan yang tertulis di temuan. Dipisah begini supaya penelaah
# bisa mematikan satu jenis penalaran saja lewat panel Pengaturan.
ATURAN: dict[str, str] = {jenis: aturan for jenis, (aturan, _) in P.JENIS.items()}

Lapor = Callable[[str, int, int], None]


@dataclass
class HasilPastikan:
    calon: list[CalonTemuan] = field(default_factory=list)
    # (judul, blok percakapan) tiap panggilan, urut — untuk Ekspor Tahap 4.
    rekaman: list[tuple[str, list[Blok]]] = field(default_factory=list)
    # Nasib tiap dugaan di tahap ini — untuk Ekspor Tahap 5.
    jejak: list[str] = field(default_factory=list)


def _nama(d: Dugaan) -> str:
    kode = ATURAN.get(d.jenis, "?")
    lain = f" × [{d.satuan_lain}]" if d.satuan_lain else ""
    return f"{kode} [{d.satuan_id}]{lain}"


def _blok_satuan(pohon: PohonSatuan, sid: str) -> Optional[list[str]]:
    """Teks utuh satuan yang diuji berikut batang induknya, atau None kalau kosong.

    Batang induk DIPISAH, bukan ditempel di depan teksnya: model wajib
    membacanya (tanpa itu ia mengarang konteks — PohonSatuan.batang_induk),
    tetapi `teks_asli` wajib berada di rentang paragraf satuannya sendiri,
    karena itulah yang dicari tahap 5.
    """
    satuan = pohon.cari(sid)
    if satuan is None:
        return None
    if sid == "lampiran":
        return [
            "== SATUAN YANG DIUJI: LAMPIRAN (dari sini 'teks_asli' disalin) ==",
            "Seluruh bagian == LAMPIRAN == pada naskah di atas. Kutip dari sana.",
        ]
    isi = pohon.teks_lengkap(sid, berlabel=True) or satuan.teks
    if not isi.strip():
        return None
    blok: list[str] = []
    batang = pohon.batang_induk(sid)
    if batang:
        blok += [
            "== BATANG KALIMAT INDUKNYA (konteks — JANGAN dikutip) ==",
            batang,
            "",
            "Satuan di bawah ini lanjutan kalimat itu. Baca keduanya sebagai satu",
            "kalimat utuh sebelum menilai — tetapi 'teks_asli' wajib kamu salin dari",
            "SATUAN-nya saja, bukan dari batang ini.",
            "",
        ]
    blok += [
        "== TEKS UTUH SATUAN (dari sini 'teks_asli' disalin) ==",
        f"[{sid}] {isi}",
    ]
    return blok


def pesan_memastikan(d: Dugaan, pohon: PohonSatuan, bahan: Bahan) -> Optional[str]:
    """Pesan user untuk satu dugaan, persis seperti dikirim. None kalau tak bisa diuji."""
    kode, keterangan = P.JENIS.get(d.jenis, ("?", ""))
    if d.tabrakan:
        satu, dua = pohon.cari(d.satuan_id), pohon.cari(d.satuan_lain)
        blok_satu, blok_dua = _blok_satuan(pohon, d.satuan_id), _blok_satuan(pohon, d.satuan_lain)
        if not (satu and dua and blok_satu and blok_dua):
            return None
        bagian = [
            P.TAHAP4_TABRAKAN,
            "",
            "== DUGAAN TABRAKAN ==",
            f"Satuan : [{d.satuan_id}] dan [{d.satuan_lain}]",
            f"Alasan : {d.alasan}",
            "",
        ]
        bagian += blok_dirujuk([satu, dua], pohon)
        bagian += blok_satu + [""] + blok_dua
        return P.susun_dengan_bahan(bahan.teks, "\n".join(bagian).rstrip())

    satuan = pohon.cari(d.satuan_id)
    blok = _blok_satuan(pohon, d.satuan_id)
    if satuan is None or blok is None:
        return None
    bagian = [
        P.TAHAP4_MEMASTIKAN,
        "",
        "== DUGAAN YANG DIUJI ==",
        f"Jenis  : {d.jenis} ({kode}) — {keterangan}",
        f"Alasan : {d.alasan}",
        "",
    ]
    if d.jenis == "lampiran":
        bagian += [
            "== PARAMETER LAMPIRAN (KMK 527 butir 120–121) ==",
            P.PARAMETER_LAMPIRAN,
            "",
            bahan.fakta_lampiran,
            "",
        ]
    if d.satuan_id != "lampiran":
        bagian += blok_dirujuk([satuan], pohon)
    bagian += blok
    return P.susun_dengan_bahan(bahan.teks, "\n".join(bagian).rstrip())


def _daftar(nilai: object) -> list[str]:
    """Daftar teks dari jawaban model; apa pun yang bukan daftar → kosong."""
    if not isinstance(nilai, list):
        return []
    return [str(b).strip() for b in nilai if str(b).strip()]


def _calon(d: Dugaan, isi: dict) -> tuple[Optional[CalonTemuan], str]:
    """Calon dari jawaban yang terbaca, atau None berikut alasannya."""
    if not isi.get("terbukti"):
        return None, "tidak terbukti — " + (str(isi.get("alasan", "")).strip() or "tanpa alasan")
    teks_asli = str(isi.get("teks_asli", "")).strip()
    if not teks_asli:
        # Terbukti tetapi tidak menunjuk letaknya. Tidak bisa ditandai, dan
        # temuan tanpa letak tidak berguna bagi penelaah.
        return None, "terbukti tetapi tanpa teks_asli — tidak bisa ditandai"

    satuan_id, satuan_lain = d.satuan_id, ""
    if d.tabrakan:
        ditandai = str(isi.get("satuan_ditandai", "")).strip()
        if ditandai not in (d.satuan_id, d.satuan_lain):
            # Menunjuk satuan di luar dua yang dikirimkan: jawabannya tidak
            # nyambung dengan pertanyaannya.
            return None, f"menunjuk satuan di luar keduanya: {ditandai!r}"
        satuan_id = ditandai
        satuan_lain = d.satuan_lain if ditandai == d.satuan_id else d.satuan_id

    return (
        CalonTemuan(
            aturan_id=ATURAN.get(d.jenis, "F2-101"),
            satuan_id=satuan_id,
            satuan_lain=satuan_lain,
            alasan=str(isi.get("alasan", "")).strip(),
            teks_asli=teks_asli,
            saran=str(isi.get("saran", "")).strip(),
            sasaran=str(isi.get("sasaran", "")).strip(),
            usulan_rumusan=str(isi.get("usulan_rumusan", "")).strip(),
            bacaan=_daftar(isi.get("bacaan")),
            tidak_ada=_daftar(isi.get("tidak_ada")),
            skor=skor_sah(isi.get("skor")),
            eksternal=d.eksternal,
        ),
        "terbukti",
    )


def memastikan(
    dugaan: list[Dugaan],
    pohon: PohonSatuan,
    bahan: Bahan,
    klien: Klien,
    ongkos: Ongkos,
    aturan_aktif: Optional[set[str]] = None,
    lapor: Optional[Lapor] = None,
    berbarengan: int = 1,
) -> HasilPastikan:
    """Jalankan tahap 4 untuk seluruh dugaan. Urutan hasil = urutan dugaan."""
    hasil = HasilPastikan()
    diuji: list[tuple[Dugaan, str]] = []
    for d in dugaan:
        kode = ATURAN.get(d.jenis, "")
        if aturan_aktif is not None and kode not in aturan_aktif:
            hasil.jejak.append(f"{_nama(d)}: dilewati — {kode} dimatikan penelaah")
            continue
        pesan = pesan_memastikan(d, pohon, bahan)
        if pesan is None:
            hasil.jejak.append(f"{_nama(d)}: dilewati — satuannya tidak ada atau tanpa teks")
            continue
        diuji.append((d, pesan))

    alat = daftar_alat(bahan)
    total = len(diuji)

    def satu(i: int):
        d, pesan = diuji[i]
        jawab = tanya_dengan_alat(
            klien, P.PERAN, pesan, alat, lambda nama, arg: jalankan_alat(bahan, nama, arg)
        )
        ongkos.catat(jawab)
        return i, jawab

    jawaban: list = [None] * total
    if berbarengan <= 1 or total <= 1:
        for i in range(total):
            _, jawaban[i] = satu(i)
            if lapor:
                lapor("4 memastikan", i + 1, total)
    else:
        with ThreadPoolExecutor(max_workers=berbarengan) as pelaksana:
            for selesai, (i, jawab) in enumerate(pelaksana.map(satu, range(total)), start=1):
                jawaban[i] = jawab
                if lapor:
                    lapor("4 memastikan", selesai, total)

    for i, ((d, _), jawab) in enumerate(zip(diuji, jawaban), start=1):
        hasil.rekaman.append((f"TAHAP 4 · DUGAAN {i}/{total} · {_nama(d)}", jawab.percakapan))
        isi = baca_jawaban(jawab.teks, ongkos)
        if isi is None:
            hasil.jejak.append(f"{_nama(d)}: jawaban model tidak terbaca")
            continue
        calon, alasan = _calon(d, isi)
        hasil.jejak.append(f"{_nama(d)}: {alasan}")
        if calon is not None:
            hasil.calon.append(calon)
    return hasil
