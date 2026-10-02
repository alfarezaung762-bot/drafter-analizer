"""TAHAP 2 · LANGKAH 4 — penilai kedua: setuju / tolak tiap calon temuan.

Ditetapkan penelaah 2 Okt 2026. Kenapa: gerbang kode membuktikan kutipan,
letak, dan sumber kata, tetapi tidak bisa menilai apakah dua tafsiran
sama-sama masuk akal — di uji PMK 45, 4 temuan lemah lolos, 2 di antaranya
hijau, dan skornya (0,9) setara temuan yang benar.

  - jalan sesudah agen memanggil `selesai`, SATU request per putaran;
  - request BARU, bukan lanjutan percakapan agen — penilai hanya melihat
    klaimnya, tidak ikut terbawa penalaran agen;
  - isinya peran penilai yang skeptis, naskah utuh (CLAUDE.md butir 14),
    analisis yang dipakai, dan semua calon putaran itu;
  - ditolak → gugur, alasannya ke jejak. Calon yang tidak dijawab penilai
    diperlakukan sama dengan ditolak.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Callable, Optional

from app.bersama.llm import Blok, Ongkos, baca_json
from app.models.pekerjaan import CalonAgen
from app.telaah.tahap2_agen.langkah2_bagi_putaran import Putaran
from app.telaah.tahap2_agen.peran_agen_dan_penilai import PERAN_PENILAI


@dataclass
class HasilPenilai:
    putusan: dict[str, tuple[str, str]] = field(default_factory=dict)
    """nomor calon → (setuju | tolak | tidak dijawab, alasan)."""
    percakapan: list[Blok] = field(default_factory=list)
    token_masuk: int = 0
    token_keluar: int = 0
    terbaca: bool = False
    dari_simpanan: bool = False


def _baris_calon(c: CalonAgen) -> list[str]:
    b = [f"{c.nomor} · {c.analisis} · letak {c.letak} · bentuk {c.bentuk}"]
    b.append(f"  kutipan : {c.kutipan!r}")
    b.append(f"  temuan  : {c.temuan}")
    for i, x in enumerate(c.bacaan[:2], start=1):
        b.append(f"  bacaan {i}: {x}")
    if c.usulan:
        b.append(f"  usulan  : {c.usulan!r}")
    if c.saran:
        b.append(f"  saran   : {c.saran}")
    if c.sasaran:
        b.append(f"  perbaiki di: {c.sasaran}")
    if c.sisipan:
        b.append(f"  sisipan : {c.sisipan.get('bentuk', '')} baru di {c.sisipan.get('sasaran', '')}: {c.sisipan.get('teks', '')!r}")
    if c.tidak_ada:
        b.append(f"  diklaim tidak ada: {', '.join(c.tidak_ada)}")
    if c.pembanding:
        b.append(f"  pembanding: {c.pembanding}")
    if c.bukti_format:
        b.append(f"  bukti format: {c.bukti_format}")
    if c.status_peraturan:
        b.append(f"  status peraturan: {c.status_peraturan}")
    return b


def pesan_penilai(calon: list[CalonAgen], putaran: Putaran, naskah: str) -> str:
    dipakai = {c.analisis for c in calon}
    baris = [naskah, "", "---", "", f"== ANALISIS YANG DIPAKAI — {putaran.judul} =="]
    for a in putaran.analisis:
        if a.kode in dipakai:
            baris += [a.teks, ""]
    baris += ["---", "", f"== CALON TEMUAN — {putaran.judul} =="]
    for c in calon:
        baris += _baris_calon(c) + [""]
    baris.append("Putuskan tiap calon di atas.")
    return "\n".join(baris)


def nilai_calon(
    calon: list[CalonAgen],
    putaran: Putaran,
    naskah: str,
    klien,
    ongkos: Ongkos,
    tersimpan: Optional[dict[str, str]] = None,
    simpan: Optional[Callable[[str, str], None]] = None,
) -> HasilPenilai:
    hasil = HasilPenilai()
    if not calon:
        return hasil
    pesan = pesan_penilai(calon, putaran, naskah)
    kunci = "penilai:" + hashlib.sha1((PERAN_PENILAI + "\n" + pesan).encode("utf-8")).hexdigest()
    hasil.percakapan = [("system", PERAN_PENILAI), ("user", pesan)]
    teks = ""
    for coba in range(2):
        if coba == 0 and tersimpan and kunci in tersimpan:
            teks = tersimpan[kunci]
            hasil.dari_simpanan = True
        else:
            jawab = klien.tanya(PERAN_PENILAI, pesan)
            ongkos.catat(jawab)
            hasil.token_masuk += jawab.token_masuk
            hasil.token_keluar += jawab.token_keluar
            teks = jawab.teks
        isi = baca_json(teks)
        if isi and isinstance(isi.get("putusan"), list):
            hasil.terbaca = True
            if simpan is not None and not hasil.dari_simpanan:
                simpan(kunci, teks)
            break
        hasil.dari_simpanan = False
    hasil.percakapan.append(("jawaban penilai", teks))
    sah = {c.nomor for c in calon}
    if hasil.terbaca:
        for e in isi["putusan"]:  # type: ignore[index]
            if not isinstance(e, dict):
                continue
            nomor = str(e.get("calon", "")).strip().upper()
            putusan = str(e.get("putusan", "")).strip().lower()
            if nomor in sah and putusan in ("setuju", "tolak"):
                hasil.putusan[nomor] = (putusan, str(e.get("alasan", "") or "").strip())
    for n in sah:
        hasil.putusan.setdefault(n, ("tidak dijawab", "penilai kedua tidak menjawab calon ini — diperlakukan sama dengan ditolak"))
    for c in calon:
        c.penilai, c.alasan_penilai = hasil.putusan[c.nomor]
    return hasil
