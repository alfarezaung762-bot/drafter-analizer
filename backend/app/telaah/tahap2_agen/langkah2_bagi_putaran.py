"""TAHAP 2 · LANGKAH 2 — membagi kerja agen menjadi putaran, menurut baris Lingkup.

Yang membagi KODE, bukan agen: pekerjaannya hanya menghitung pasal dan token,
dan tiap pasal wajib masuk tepat satu kelompok (ditetapkan penelaah 1 Okt
2026 — uji PMK 45: dipecah per kelompok menemukan ±2 kali lipat kesalahan
nyata dibanding sekali panggil).

    per pasal       satu putaran per kelompok ≤ FASE2_PASAL_PER_FOKUS pasal
                    atau ≤ FASE2_TOKEN_PER_FOKUS token teks pasal. Pasal TIDAK
                    PERNAH dibelah: yang membuat kelompok lewat batas pindah
                    UTUH ke kelompok berikutnya; satu pasal yang sendirian
                    melewati batas jadi kelompok sendiri, tetap utuh.
    seluruh naskah  satu putaran
    lampiran        satu putaran, bila naskahnya berlampiran atau menyebut
                    lampiran
    format          satu putaran, membaca naskah berformat

Angka per kelompok hanya membagi TUGAS; yang DIBACA tiap putaran tetap
seluruh naskah.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.models.satuan import JenisSatuan, PohonSatuan
from app.telaah.tahap2_agen.langkah1_pilih_analisis import Analisis
from app.telaah.tahap2_persiapan.bahan import hitung_token

PASAL_PER_FOKUS = 6
TOKEN_PER_FOKUS = 4000


@dataclass
class Putaran:
    kode: str
    """Kunci pendek, mis. 'pasal-1', 'naskah', 'lampiran', 'format'."""
    judul: str
    """Judul untuk panel dan jejak, mis. 'Putaran 1/8 · Pasal 1–6'."""
    lingkup: str
    analisis: list[Analisis] = field(default_factory=list)
    fokus: list[str] = field(default_factory=list)

    @property
    def berformat(self) -> bool:
        return self.lingkup == "format"


def kelompok_fokus(
    pohon: PohonSatuan, per_fokus: int = PASAL_PER_FOKUS, batas_token: int = TOKEN_PER_FOKUS
) -> list[list[str]]:
    """Pasal dikelompokkan untuk difokuskan bergilir. Satu pasal tidak pernah dibelah."""
    per_fokus = max(1, per_fokus)
    hasil: list[list[str]] = []
    kini: list[str] = []
    token = 0
    for p in pohon.semua(JenisSatuan.PASAL):
        t = hitung_token(pohon.teks_lengkap(p.id, berlabel=True))
        if kini and (len(kini) >= per_fokus or token + t > batas_token):
            hasil.append(kini)
            kini, token = [], 0
        kini.append(p.id)
        token += t
    if kini:
        hasil.append(kini)
    return hasil


def _nama_pasal(pid: str) -> str:
    return "Pasal " + pid.split("-", 1)[1].upper() if pid.startswith("pasal-") else pid


@dataclass
class Pembagian:
    putaran: list[Putaran] = field(default_factory=list)
    tidak_dijalankan: list[tuple[str, str]] = field(default_factory=list)
    """(kode analisis, alasan)."""


def bagi_putaran(
    analisis: list[Analisis],
    pohon: PohonSatuan,
    ada_urusan_lampiran: bool,
    per_fokus: int = PASAL_PER_FOKUS,
    token_per_fokus: int = TOKEN_PER_FOKUS,
) -> Pembagian:
    hasil = Pembagian()
    per_pasal = [a for a in analisis if a.lingkup == "per pasal"]
    naskah = [a for a in analisis if a.lingkup == "seluruh naskah"]
    lampiran = [a for a in analisis if a.lingkup == "lampiran"]
    format_ = [a for a in analisis if a.lingkup == "format"]

    daftar: list[Putaran] = []
    if per_pasal:
        kelompok = kelompok_fokus(pohon, per_fokus, token_per_fokus) if pohon.gagal is None else []
        if not kelompok:
            for a in per_pasal:
                hasil.tidak_dijalankan.append((a.kode, "tidak ada pasal yang terbaca di peta letak"))
        for fokus in kelompok:
            rentang = _nama_pasal(fokus[0]) + (f"–{_nama_pasal(fokus[-1]).split(' ', 1)[1]}" if len(fokus) > 1 else "")
            daftar.append(Putaran(kode=fokus[0], judul=rentang, lingkup="per pasal", analisis=per_pasal, fokus=fokus))
    if naskah:
        daftar.append(Putaran(kode="naskah", judul="Lintas naskah", lingkup="seluruh naskah", analisis=naskah))
    if lampiran:
        if ada_urusan_lampiran:
            daftar.append(Putaran(kode="lampiran", judul="Lampiran", lingkup="lampiran", analisis=lampiran))
        else:
            for a in lampiran:
                hasil.tidak_dijalankan.append((a.kode, "naskah tidak berlampiran dan tidak menyebut lampiran"))
    if format_:
        daftar.append(Putaran(kode="format", judul="Format", lingkup="format", analisis=format_))

    total = len(daftar)
    for i, p in enumerate(daftar, start=1):
        p.judul = f"Putaran {i}/{total} · {p.judul}"
    hasil.putaran = daftar
    return hasil
