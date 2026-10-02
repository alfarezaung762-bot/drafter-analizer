"""TAHAP 2 · LANGKAH 1 — membaca analisis dan skills, menolak yang cacat, memilih.

Tiga pekerjaan, ketiganya kode biasa tanpa AI:

  1. MEMBACA `skills/analisis/analisis.md`, `analisisformat.md`, dan tiap
     `skills/**/SKILL.md`. Satu bagian `## Kode · Judul` = satu analisis.
  2. MENOLAK yang cacat — nilai di luar pilihan, kunci wajib kosong, kode
     kembar, skill tanpa nama. Backend MENOLAK MENYALA dan menyebut
     analisisnya (`FormulirCacat`); formulir cacat tidak pernah dilewati
     diam-diam, karena analisis yang hilang tanpa kabar terbaca sama dengan
     analisis yang tidak menemukan apa-apa.
  3. MEMILIH analisis yang dikirim ke agen: Berlaku untuk memuat jenis naskah
     yang dipilih penelaah, skill label jenis itu ada, dan tiap isi Butuh
     tersedia. Yang tidak memenuhi tidak dikirim, dan alasannya disebut —
     "belum tersedia untuk KMK", "korpus tidak terhubung".

Kode TIDAK tahu isi pemeriksaannya. Yang dibaca kode hanya enam baris kepala;
bagian di bawahnya dikirim apa adanya ke agen.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# backend/skills — di luar app/, karena isinya teks yang ditinjau penelaah,
# bukan kode.
FOLDER_SKILLS = Path(__file__).resolve().parents[3] / "skills"

BERKAS_ISI = "analisis.md"
BERKAS_FORMAT = "analisisformat.md"

RESPONS = ("otomatis", "usulan", "catatan", "dibuang")
LINGKUP = ("per pasal", "seluruh naskah", "lampiran", "format")
KOMENTAR = ("lengkap", "ringkas")
BUTUH = ("korpus", "bahan korpus", "bacaan format")

_KUNCI = ("Berlaku untuk", "Respons", "Lingkup", "Komentar", "Dasar", "Butuh")
_KUNCI_WAJIB = ("Berlaku untuk", "Respons", "Lingkup")
_SUBBAGIAN = (
    "Yang diperiksa",
    "Yang tidak diperiksa",
    "Cara memeriksa",
    "Bukan kesalahan",
    "Contoh",
)

_JUDUL = re.compile(r"^##\s+(?P<kode>\S+)\s+·\s+(?P<judul>.+?)\s*$")
_KODE = re.compile(r"^[A-Z][A-Z0-9]*-\d+[a-z]?$")
_JENIS = re.compile(r"^[a-z0-9][a-z0-9-]*$")
_KEPALA = re.compile(r"^(?P<kunci>[A-Za-z ]+?):\s*(?P<nilai>.*)$")
_SUB = re.compile(r"^###\s+(?P<nama>.+?)\s*$")
_STATUS_DASAR = re.compile(r"\((visual|turunan)\)\s*$")
_KOSONG = {"", "—", "-", "–"}

# Nama jenis naskah di panel → folder skill-nya.
JENIS_PANEL = {"PMK": "pmk-standar", "KMK": "kmk"}


class FormulirCacat(Exception):
    """Formulir analisis atau skill yang cacat. Backend menolak menyala."""

    def __init__(self, masalah: list[str]) -> None:
        self.masalah = masalah
        super().__init__(
            "Formulir analisis/skill cacat — backend tidak dinyalakan:\n"
            + "\n".join(f"  - {m}" for m in masalah)
        )


@dataclass
class Analisis:
    """Satu bagian `## Kode · Judul` dari analisis.md atau analisisformat.md."""

    kode: str
    judul: str
    berkas: str
    berlaku_untuk: list[str]
    respons: str
    lingkup: str
    komentar: str
    dasar: str
    """Baris Dasar apa adanya, tanpa penanda statusnya."""
    dasar_status: str
    """'visual' · 'turunan' · 'prioritas' · '' (kosong — agen mencarikan)."""
    butuh: list[str]
    diperiksa: list[str]
    tidak_diperiksa: list[str]
    cara: str
    bukan_kesalahan: str
    contoh: str
    teks: str
    """Seluruh bagian apa adanya — inilah yang dikirim ke agen."""

    @property
    def format(self) -> bool:
        return self.lingkup == "format"


@dataclass
class Skill:
    nama: str
    deskripsi: str
    teks: str
    jalur: Path


@dataclass
class Katalog:
    analisis: list[Analisis] = field(default_factory=list)
    skill: dict[str, Skill] = field(default_factory=dict)

    def cari(self, kode: str) -> Optional[Analisis]:
        for a in self.analisis:
            if a.kode == kode:
                return a
        return None

    def ada_label(self, jenis: str) -> bool:
        return f"{jenis}/label" in self.skill

    def skill_jenis(self, jenis: str) -> list[Skill]:
        """Skill yang ditawarkan ke agen untuk jenis ini: miliknya sendiri dan yang umum.

        Skill label tidak ditawarkan — dibaca langkah label tahap 1, bukan agen.
        """
        hasil = []
        for nama, s in sorted(self.skill.items()):
            if nama.endswith("/label"):
                continue
            if nama.startswith(jenis + "/") or "/" not in nama:
                hasil.append(s)
        return hasil


@dataclass
class Prasyarat:
    """Apa yang tersedia di analisis kali ini — menentukan isi Butuh yang terpenuhi."""

    korpus: bool = False
    alasan_korpus: str = "korpus tidak terhubung"
    bacaan_format: bool = True
    alasan_format: str = "format naskah tidak terbaca dari Word"


@dataclass
class Pilihan:
    dikirim: list[Analisis] = field(default_factory=list)
    tidak_dikirim: list[tuple[str, str]] = field(default_factory=list)
    """(kode, alasan) — disebut di panel dan di jejak."""


# ---------------------------------------------------------------------------
# Membaca
# ---------------------------------------------------------------------------


def _baca_analisis(teks: str, berkas: str, masalah: list[str]) -> list[Analisis]:
    baris = teks.splitlines()
    mulai = [i for i, b in enumerate(baris) if b.startswith("## ")]
    hasil: list[Analisis] = []
    for n, i in enumerate(mulai):
        akhir = mulai[n + 1] if n + 1 < len(mulai) else len(baris)
        isi = baris[i:akhir]
        a = _satu_analisis(isi, berkas, masalah)
        if a is not None:
            hasil.append(a)
    return hasil


def _satu_analisis(isi: list[str], berkas: str, masalah: list[str]) -> Optional[Analisis]:
    m = _JUDUL.match(isi[0])
    if not m:
        masalah.append(f"{berkas}: judul bagian tidak berbentuk '## Kode · Judul': {isi[0]!r}")
        return None
    kode, judul = m.group("kode"), m.group("judul")
    nama = f"{berkas} {kode}"
    if not _KODE.match(kode):
        masalah.append(f"{nama}: kode tidak berbentuk huruf-angka, mis. F2-101 atau I-37")

    kepala: dict[str, str] = {}
    sub: dict[str, list[str]] = {}
    kini: Optional[str] = None
    for b in isi[1:]:
        ms = _SUB.match(b)
        if ms:
            kini = ms.group("nama")
            if kini not in _SUBBAGIAN:
                masalah.append(f"{nama}: subbagian tidak dikenal '### {kini}'")
            sub.setdefault(kini, [])
            continue
        if kini is not None:
            sub[kini].append(b)
            continue
        if not b.strip():
            continue
        mk = _KEPALA.match(b)
        if not mk or mk.group("kunci").strip() not in _KUNCI:
            masalah.append(f"{nama}: baris kepala tidak dikenal {b.strip()!r}")
            continue
        k = mk.group("kunci").strip()
        if k in kepala:
            masalah.append(f"{nama}: baris kepala '{k}' ditulis dua kali")
        kepala[k] = mk.group("nilai").strip()

    for k in _KUNCI_WAJIB:
        if not kepala.get(k, "").strip():
            masalah.append(f"{nama}: '{k}' wajib diisi")

    berlaku = [x.strip() for x in kepala.get("Berlaku untuk", "").split(",") if x.strip()]
    for j in berlaku:
        if not _JENIS.match(j):
            masalah.append(f"{nama}: jenis naskah {j!r} tidak berbentuk nama folder skill, mis. pmk-standar")

    respons = kepala.get("Respons", "").strip().lower()
    if respons and respons not in RESPONS:
        masalah.append(f"{nama}: Respons {respons!r} di luar pilihan {', '.join(RESPONS)}")

    lingkup = kepala.get("Lingkup", "").strip().lower()
    if lingkup and lingkup not in LINGKUP:
        masalah.append(f"{nama}: Lingkup {lingkup!r} di luar pilihan {', '.join(LINGKUP)}")
    if berkas == BERKAS_FORMAT and lingkup and lingkup != "format":
        masalah.append(f"{nama}: analisis di {BERKAS_FORMAT} wajib ber-Lingkup format")
    if berkas == BERKAS_ISI and lingkup == "format":
        masalah.append(f"{nama}: Lingkup format ditulis di {BERKAS_FORMAT}, bukan {BERKAS_ISI}")

    komentar = kepala.get("Komentar", "").strip().lower() or "lengkap"
    if komentar not in KOMENTAR:
        masalah.append(f"{nama}: Komentar {komentar!r} di luar pilihan {', '.join(KOMENTAR)}")

    dasar_mentah = kepala.get("Dasar", "").strip()
    dasar, status = _baca_dasar(dasar_mentah)
    if status == "cacat":
        masalah.append(
            f"{nama}: Dasar wajib alamat lengkap ber-'hlm' dan berakhiran (visual) "
            f"atau (turunan), atau 'prioritas penelaah', atau kosong: {dasar_mentah!r}"
        )

    butuh_mentah = kepala.get("Butuh", "").strip()
    butuh = [] if butuh_mentah in _KOSONG else [x.strip().lower() for x in butuh_mentah.split(",") if x.strip()]
    for x in butuh:
        if x not in BUTUH:
            masalah.append(f"{nama}: Butuh {x!r} di luar pilihan {', '.join(BUTUH)}")

    diperiksa = _butir(sub.get("Yang diperiksa", []))
    if not diperiksa:
        masalah.append(f"{nama}: '### Yang diperiksa' wajib memuat sekurang-kurangnya satu butir")

    return Analisis(
        kode=kode,
        judul=judul,
        berkas=berkas,
        berlaku_untuk=berlaku,
        respons=respons,
        lingkup=lingkup,
        komentar=komentar,
        dasar=dasar,
        dasar_status=status if status != "cacat" else "",
        butuh=butuh,
        diperiksa=diperiksa,
        tidak_diperiksa=_butir(sub.get("Yang tidak diperiksa", [])),
        cara=_paragraf(sub.get("Cara memeriksa", [])),
        bukan_kesalahan=_paragraf(sub.get("Bukan kesalahan", [])),
        contoh=_paragraf(sub.get("Contoh", [])),
        teks="\n".join(isi).strip(),
    )


def _baca_dasar(teks: str) -> tuple[str, str]:
    """(alamat tanpa penanda, status). Status 'cacat' bila bentuknya salah."""
    if not teks:
        return "", ""
    if teks.strip().lower() == "prioritas penelaah":
        return "prioritas penelaah", "prioritas"
    m = _STATUS_DASAR.search(teks)
    if not m or "hlm" not in teks:
        return teks, "cacat"
    alamat = teks[: m.start()].strip().rstrip(",").strip()
    alamat = re.sub(r"^KMK\s+527(?:/KMK\.01/2022)?\s+", "", alamat)
    return alamat, m.group(1)


def _butir(baris: list[str]) -> list[str]:
    hasil = []
    for b in baris:
        b = b.strip()
        if b.startswith("- "):
            isi = b[2:].strip()
            if isi:
                hasil.append(isi)
        elif b and hasil:
            hasil[-1] = f"{hasil[-1]} {b}"
    return hasil


def _paragraf(baris: list[str]) -> str:
    return "\n".join(baris).strip()


def _baca_skill(jalur: Path, folder: Path, masalah: list[str]) -> Optional[Skill]:
    teks = jalur.read_text(encoding="utf-8")
    nama_folder = jalur.parent.relative_to(folder).as_posix()
    m = re.match(r"^---\n(?P<kepala>.*?)\n---\n", teks, re.DOTALL)
    if not m:
        masalah.append(f"skill {nama_folder}: SKILL.md wajib diawali kepala --- name/description ---")
        return None
    kepala = dict(
        (k.strip(), v.strip())
        for k, _, v in (b.partition(":") for b in m.group("kepala").splitlines())
        if k.strip()
    )
    nama, deskripsi = kepala.get("name", ""), kepala.get("description", "")
    if nama != nama_folder:
        masalah.append(f"skill {nama_folder}: name {nama!r} wajib sama dengan foldernya")
    if not deskripsi:
        masalah.append(f"skill {nama_folder}: description wajib diisi")
    return Skill(nama=nama_folder, deskripsi=deskripsi, teks=teks[m.end():].strip(), jalur=jalur)


def muat_katalog(folder: Path = FOLDER_SKILLS) -> Katalog:
    """Baca seluruh analisis dan skill. Melempar FormulirCacat bila ada yang cacat."""
    masalah: list[str] = []
    katalog = Katalog()

    folder_analisis = folder / "analisis"
    for berkas in (BERKAS_ISI, BERKAS_FORMAT):
        jalur = folder_analisis / berkas
        if not jalur.exists():
            masalah.append(f"{berkas} tidak ada di {folder_analisis}")
            continue
        katalog.analisis += _baca_analisis(jalur.read_text(encoding="utf-8"), berkas, masalah)

    terlihat: dict[str, str] = {}
    for a in katalog.analisis:
        if a.kode in terlihat:
            masalah.append(f"kode {a.kode} kembar — di {terlihat[a.kode]} dan {a.berkas}")
        terlihat[a.kode] = a.berkas

    for jalur in sorted(folder.rglob("SKILL.md")):
        if folder_analisis in jalur.parents:
            continue
        s = _baca_skill(jalur, folder, masalah)
        if s is not None:
            katalog.skill[s.nama] = s

    if masalah:
        raise FormulirCacat(masalah)
    return katalog


# ---------------------------------------------------------------------------
# Memilih
# ---------------------------------------------------------------------------


def pilih(
    katalog: Katalog,
    jenis: str,
    dipilih_penelaah: Optional[list[str]] = None,
    prasyarat: Optional[Prasyarat] = None,
) -> Pilihan:
    """Analisis yang dikirim ke agen untuk naskah ini, dan alasan yang lain tidak.

    `dipilih_penelaah` kode yang dicentang di panel Pengaturan; None = semua.
    Analisis yang tidak dicentang tidak disebut di `tidak_dikirim` — penelaah
    sendiri yang mematikannya.
    """
    prasyarat = prasyarat or Prasyarat()
    hasil = Pilihan()
    centang = None if dipilih_penelaah is None else {k.strip() for k in dipilih_penelaah}
    ada_label = katalog.ada_label(jenis)
    for a in katalog.analisis:
        if centang is not None and a.kode not in centang:
            continue
        if jenis not in a.berlaku_untuk or not ada_label:
            hasil.tidak_dikirim.append((a.kode, f"belum tersedia untuk {_sebut_jenis(jenis)}"))
            continue
        alasan = _butuh_kurang(a, prasyarat)
        if alasan:
            hasil.tidak_dikirim.append((a.kode, alasan))
            continue
        hasil.dikirim.append(a)
    return hasil


def _butuh_kurang(a: Analisis, p: Prasyarat) -> str:
    for b in a.butuh:
        if b in ("korpus", "bahan korpus") and not p.korpus:
            return p.alasan_korpus
        if b == "bacaan format" and not p.bacaan_format:
            return p.alasan_format
    return ""


def _sebut_jenis(jenis: str) -> str:
    for panel, folder in JENIS_PANEL.items():
        if folder == jenis:
            return panel
    return jenis


def daftar_panel(
    katalog: Katalog, jenis: str, prasyarat: Optional[Prasyarat] = None
) -> list[dict]:
    """Daftar pemeriksaan untuk panel Pengaturan — bentuknya seperti daftar lama."""
    prasyarat = prasyarat or Prasyarat()
    pilihan = pilih(katalog, jenis, None, prasyarat)
    alasan = dict(pilihan.tidak_dikirim)
    keluar = []
    for a in katalog.analisis:
        keluar.append(
            {
                "id": a.kode,
                "judul": a.judul,
                "kelompok": "format" if a.format else "isi",
                "respons": a.respons,
                "lingkup": a.lingkup,
                "butuh": a.butuh,
                "dasar": a.dasar,
                "dasar_status": a.dasar_status,
                "diperiksa": a.diperiksa,
                "tidakDiperiksa": a.tidak_diperiksa,
                "tersedia": a.kode not in alasan,
                "alasan": alasan.get(a.kode, ""),
            }
        )
    return keluar
