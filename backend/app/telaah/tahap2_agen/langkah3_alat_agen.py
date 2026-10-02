"""TAHAP 2 · LANGKAH 3 — alat yang boleh dipanggil agen (rancangan Fase 4 bagian 5.3).

Semua alat hanya MEMBACA, MENYARING, atau MERINGKAS — tidak satu pun tahu
aturan pemeriksaannya; yang menilai agen, dengan skill dan analisis.

    muat_skill        membaca SKILL.md sebuah skill
    cari_teks         mencari di SELURUH naskah, termasuk lampiran dan isi tabel
    buka_tabel        membuka baris tabel, termasuk yang dikirim kerangkanya
    jumlah_kolom      menjumlah angka satu kolom tabel
    cari_format       semua paragraf yang formatnya BERBEDA dari nilai yang
                      diberikan agen — putaran format
    ringkas_menjorok  menjorok tiap tingkat per pasal, diringkas — putaran format
    cari_korpus       pembanding di peraturan lain yang masih berlaku
    cek_peraturan     status berlaku sebuah peraturan — dua alat korpus ini
                      hanya di putaran yang analisisnya Butuh: korpus
    catat_temuan      mencatat calon temuan; bentuknya dicek SAAT ITU JUGA —
                      kutipan > 200 huruf, melewati satu paragraf, atau tidak
                      ketemu di letak yang ditunjuk ditolak, agen mengutip ulang
    selesai           status tiap analisis untuk tiap pasal fokus

Hasil cari_korpus dan cek_peraturan DICATAT kode: gerbang membuktikan
pembanding dan status yang disebut agen memang ada di catatan itu. Alat tidak
pernah melempar — kegagalan dikembalikan sebagai kalimat yang dibaca agen.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from typing import Optional

from app.bersama.llm import Perapal
from app.bersama.opensearch import Korpus, PencariPeraturan, baca_kutipan
from app.models.pekerjaan import CalonAgen
from app.models.satuan import JenisSatuan, PohonSatuan
from app.models.temuan import ParagrafInput
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import NaskahBerlabel
from app.telaah.tahap2_agen.langkah1_pilih_analisis import Katalog
from app.telaah.tahap2_agen.langkah2_bagi_putaran import Putaran
from app.telaah.tahap2_persiapan.bahan import angka, baris_tabel
from app.telaah.tahap4_memastikan.alat import jumlah_kolom

KUTIPAN_MAKS = 200
_HASIL_CARI_MAKS = 20
_BARIS_TABEL_MAKS = 60
_POTONGAN = 90
_PANJANG_KUERI = 1200
_TOLERANSI_CM = 0.05

_LETAK_PARAGRAF = re.compile(r"^¶\s*(\d+)(?:\s*[-–]\s*¶?\s*(\d+))?$")


def _rapat(t: str) -> str:
    return re.sub(r"\s+", "", t).lower()


def _rapi(t: str) -> str:
    return re.sub(r"\s+", " ", t).strip()


# ---------------------------------------------------------------------------
# Bahan yang dibaca alat — disusun tahap 1, sama untuk semua putaran
# ---------------------------------------------------------------------------


@dataclass
class BahanAlat:
    paragraf: list[ParagrafInput]
    pohon: PohonSatuan
    peta: dict[int, str]
    """index paragraf → id satuan terdalam yang memuatnya."""
    id_awal: dict[int, str]
    """index paragraf → id satuan yang DIBUKA paragraf itu."""
    berlabel: NaskahBerlabel
    anotasi_format: dict[int, str]
    katalog: Katalog
    korpus: Optional[Korpus] = None
    perapal: Optional[Perapal] = None
    pencari: Optional[PencariPeraturan] = None

    def __post_init__(self) -> None:
        self.menurut_index = {p.index: p for p in self.paragraf}


# ---------------------------------------------------------------------------
# Yang dicatat selama satu putaran
# ---------------------------------------------------------------------------


@dataclass
class CatatanPutaran:
    calon: list[CalonAgen] = field(default_factory=list)
    laporan: dict[tuple[str, str], tuple[str, str]] = field(default_factory=dict)
    """(pasal|naskah, kode analisis) → (status, alasan)."""
    korpus: list[dict] = field(default_factory=list)
    """Tiap pemanggilan cari_korpus: {teks, pembanding: [{sebutan, judul, pasal, potongan}]}."""
    peraturan: dict[str, dict] = field(default_factory=dict)
    """sebutan → {berlaku, judul, nomor, alasan} dari cek_peraturan."""
    skill_dimuat: list[str] = field(default_factory=list)
    ditolak_catat: list[str] = field(default_factory=list)
    """Alasan catat_temuan ditolak saat itu juga — untuk jejak."""
    selesai_dipanggil: bool = False


# ---------------------------------------------------------------------------
# Skema alat — bentuk function calling
# ---------------------------------------------------------------------------


def _fungsi(nama: str, deskripsi: str, properti: dict, wajib: list[str]) -> dict:
    return {
        "type": "function",
        "function": {
            "name": nama,
            "description": deskripsi,
            "parameters": {"type": "object", "properties": properti, "required": wajib},
        },
    }


ALAT_MUAT_SKILL = _fungsi(
    "muat_skill",
    "Baca kaidah sebuah skill (SKILL.md), lengkap dengan alamat dan kutipan KMK 527.",
    {"nama": {"type": "string", "description": "Nama skill persis dari daftar, mis. pmk-standar/pembukaan."}},
    ["nama"],
)
ALAT_CARI = _fungsi(
    "cari_teks",
    "Cari teks di SELURUH naskah, termasuk lampiran dan isi tabel. Tidak peka huruf "
    "besar-kecil dan jarak spasi. WAJIB dipakai sebelum menyatakan sesuatu tidak ada.",
    {"teks": {"type": "string", "description": "Teks yang dicari."}},
    ["teks"],
)
ALAT_TABEL = _fungsi(
    "buka_tabel",
    "Buka baris-baris tabel menurut nomornya — nomor yang tertulis di [TABEL n …] pada "
    "naskah. Berguna untuk tabel yang hanya dikirim kerangkanya.",
    {
        "nomor": {"type": "integer", "description": "Nomor tabel."},
        "dari_baris": {"type": "integer", "description": "Baris pertama, mulai 1."},
        "sampai_baris": {"type": "integer", "description": "Baris terakhir."},
    },
    ["nomor"],
)
ALAT_JUMLAH = _fungsi(
    "jumlah_kolom",
    "Jumlahkan angka di satu kolom tabel. Sel yang bukan angka dilewati dan dihitung.",
    {
        "nomor": {"type": "integer", "description": "Nomor tabel."},
        "kolom": {"type": "integer", "description": "Nomor kolom, mulai 1."},
    },
    ["nomor", "kolom"],
)
ALAT_CARI_FORMAT = _fungsi(
    "cari_format",
    "Daftar SEMUA paragraf yang formatnya BERBEDA dari nilai yang kamu berikan — isi hanya "
    "medan yang mau dibandingkan, dengan nilai yang benar menurut skill. Kode tidak tahu "
    "aturannya; ia hanya membandingkan.",
    {
        "huruf": {"type": "string"},
        "ukuran": {"type": "number"},
        "rata": {"type": "string", "description": "rata kiri · tengah · rata kanan · rata kiri-kanan"},
        "kiri_cm": {"type": "number"},
        "baris_pertama_cm": {"type": "number"},
        "spasi_baris": {"type": "number"},
        "spasi_sebelum_pt": {"type": "number"},
        "spasi_sesudah_pt": {"type": "number"},
        "dari_paragraf": {"type": "integer", "description": "Batasi mulai ¶ ini (boleh kosong)."},
        "sampai_paragraf": {"type": "integer", "description": "Batasi sampai ¶ ini (boleh kosong)."},
    },
    [],
)
ALAT_MENJOROK = _fungsi(
    "ringkas_menjorok",
    "Ringkas menjorok tiap tingkat satuan per pasal: menjorok kiri / baris pertama dan "
    "berapa kali muncul, supaya yang berbeda dari saudaranya langsung terlihat.",
    {"pasal": {"type": "string", "description": "Label pasal, mis. pasal-2. Kosong = semua pasal."}},
    [],
)
ALAT_KORPUS = _fungsi(
    "cari_korpus",
    "Cari pasal pembanding di peraturan lain yang MASIH BERLAKU (korpus JDIH). Hasilnya "
    "paling banyak 5 peraturan, satu pasal paling mirip masing-masing. Teksnya hasil "
    "pemindaian — OCR-nya bisa rusak.",
    {"teks": {"type": "string", "description": "Rumusan yang dicari pembandingnya."}},
    ["teks"],
)
ALAT_CEK_PERATURAN = _fungsi(
    "cek_peraturan",
    "Status berlaku sebuah peraturan menurut korpus, dari jenis, nomor, dan tahunnya, "
    "mis. 'Undang-Undang Nomor 17 Tahun 2003'. Jawaban 'tidak tahu' berarti diam.",
    {"sebutan": {"type": "string", "description": "Jenis, nomor, dan tahun peraturan."}},
    ["sebutan"],
)
ALAT_CATAT = _fungsi(
    "catat_temuan",
    "Catat SATU calon temuan. Bentuknya dicek saat itu juga; yang cacat ditolak dengan "
    "alasannya, dan kamu mencatat ulang.",
    {
        "analisis": {"type": "string", "description": "Kode analisis, mis. F2-101."},
        "letak": {"type": "string", "description": "Label satuan (pasal-5-ayat-2) atau ¶nomor (¶23)."},
        "kutipan": {
            "type": "string",
            "description": (
                "Bagian terpendek yang salah, persis, ≤ 200 huruf, satu paragraf, dan hanya SEKALI "
                "muncul di letaknya — bila kata yang sama muncul lagi di letak itu, sertakan kata "
                "sebelum atau sesudahnya."
            ),
        },
        "bentuk": {"type": "string", "enum": ["usulan", "dibuang", "catatan"]},
        "temuan": {"type": "string", "description": "Kenapa salah, satu-dua kalimat untuk penelaah."},
        "saran": {"type": "string", "description": "Jalan keluar; kosong bila tidak ada yang pasti."},
        "usulan": {"type": "string", "description": "Pengganti harfiah untuk kutipan saja (bentuk usulan)."},
        "sasaran": {"type": "string", "description": "Label satuan tempat perbaikan bila BUKAN di kutipan; kosong bila di sini."},
        "sisipan": {
            "type": "object",
            "description": "Satuan baru di tempat perbaikan (lihat aturan 7).",
            "properties": {
                "sasaran": {"type": "string"},
                "bentuk": {"type": "string", "enum": ["angka", "huruf", "ayat", "pasal"]},
                "teks": {"type": "string"},
                "sumber": {"type": "string"},
            },
        },
        "pembanding": {"type": "string", "description": "Peraturan pembanding, disalin persis dari hasil cari_korpus."},
        "bacaan": {"type": "array", "items": {"type": "string"}, "description": "Dua tafsiran — wajib untuk rumusan dua arah."},
        "tidak_ada": {"type": "array", "items": {"type": "string"}, "description": "Teks yang kamu klaim tidak ada di naskah."},
        "alasan_buang": {"type": "string", "enum": ["tidak_dipakai", "mengulang", "frasa_dilarang"]},
        "bukti_letak": {"type": "string", "description": "Bentuk dibuang/mengulang: letak teks kembarnya."},
        "bukti_format": {"type": "string", "description": "Putaran format: kutipan persis dari ⟨⟩ paragraf itu."},
        "status_peraturan": {"type": "string", "description": "Hasil cek_peraturan persis, mis. 'Tidak Berlaku'."},
        "rujukan": {
            "type": "object",
            "description": "Bila Dasar analisis kosong: alamat dan kutipan persis dari skill.",
            "properties": {"alamat": {"type": "string"}, "kutipan": {"type": "string"}},
        },
        "ketiadaan": {"type": "boolean", "description": "true bila kesalahannya ketiadaan sesuatu."},
        "skor": {"type": "number", "description": "Keyakinan 0–1."},
    },
    ["analisis", "letak", "kutipan", "bentuk", "temuan", "skor"],
)
ALAT_SELESAI = _fungsi(
    "selesai",
    "Tutup putaran: status tiap analisis untuk tiap pasal fokus (atau 'naskah').",
    {
        "laporan": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "pasal": {"type": "string", "description": "Label pasal fokus, atau 'naskah'."},
                    "analisis": {"type": "string"},
                    "status": {"type": "string", "enum": ["diperiksa", "tidak relevan"]},
                    "alasan": {"type": "string"},
                },
                "required": ["pasal", "analisis", "status"],
            },
        }
    },
    ["laporan"],
)


def alat_putaran(putaran: Putaran, bahan: BahanAlat) -> list[dict]:
    """Alat yang ditawarkan di putaran ini."""
    alat = [ALAT_MUAT_SKILL, ALAT_CARI]
    if bahan.berlabel.bahan and (bahan.berlabel.bahan.tabel or bahan.berlabel.bahan.tabel_raksasa):
        alat += [ALAT_TABEL, ALAT_JUMLAH]
    if putaran.berformat:
        alat += [ALAT_CARI_FORMAT, ALAT_MENJOROK]
    butuh_korpus = any("korpus" in a.butuh for a in putaran.analisis)
    if butuh_korpus and bahan.korpus is not None and bahan.perapal is not None:
        alat.append(ALAT_KORPUS)
    if butuh_korpus and bahan.pencari is not None:
        alat.append(ALAT_CEK_PERATURAN)
    return alat + [ALAT_CATAT, ALAT_SELESAI]


# ---------------------------------------------------------------------------
# Pelaksana
# ---------------------------------------------------------------------------


def paragraf_letak(letak: str, bahan: BahanAlat) -> Optional[list[ParagrafInput]]:
    """Paragraf di dalam letak (label satuan, atau ¶n / ¶a-b). None bila letaknya tidak ada."""
    letak = letak.strip()
    m = _LETAK_PARAGRAF.match(letak)
    if m:
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a or a not in bahan.menurut_index:
            return None
        return [p for p in bahan.paragraf if a <= p.index <= b]
    s = bahan.pohon.cari(letak.lower())
    if s is None or not s.bisa_ditandai:
        return None
    return [p for p in bahan.paragraf if s.paragraf_mulai <= p.index < s.paragraf_akhir]


def kutipan_di(kutipan: str, paragraf: list[ParagrafInput]) -> Optional[ParagrafInput]:
    """Paragraf pertama yang memuat kutipan — spasi dilonggarkan, huruf dan tanda baca persis."""
    potongan = kutipan.split()
    if not potongan:
        return None
    pola = re.compile(r"\s+".join(re.escape(k) for k in potongan))
    for p in paragraf:
        if pola.search(p.teks) or pola.search(p.utuh):
            return p
    return None


def _di_tersembunyi(kutipan: str, paragraf: list[ParagrafInput]) -> bool:
    """Kutipan ada di teks TERSEMBUNYI paragraf itu menurut bacaan format.

    Word bisa tidak menyertakan teks tersembunyi di teks paragraf (getText
    mengecualikannya secara bawaan), jadi kutipan F-19 dibuktikan juga dari
    bacaan formatnya — sama dengan gerbang.
    """
    kunci = "".join(kutipan.split())
    return bool(kunci) and any(
        kunci in "".join(t.split()) for p in paragraf if p.format for t in p.format.tersembunyi
    )


def jumlah_kemunculan(kutipan: str, paragraf: list[ParagrafInput]) -> int:
    """Berapa kali kutipan muncul di paragraf-paragraf itu — spasi dilonggarkan.

    Lebih dari sekali berarti tempat yang dimaksud TIDAK PASTI. Terbukti 2 Okt
    2026 pada PMK 45: "YANG DIPERGUNAKAN" muncul dua kali di baris Menetapkan,
    yang pertama benar dan yang kedua salah — penandaan mengenai yang pertama.
    """
    potongan = kutipan.split()
    if not potongan:
        return 0
    pola = re.compile(r"\s+".join(re.escape(k) for k in potongan))
    jumlah = 0
    for p in paragraf:
        n = len(pola.findall(p.teks))
        jumlah += n if n else len(pola.findall(p.utuh))
    return jumlah


class Alat:
    """Pelaksana alat untuk SATU putaran."""

    def __init__(self, putaran: Putaran, bahan: BahanAlat, catatan: CatatanPutaran) -> None:
        self.putaran = putaran
        self.bahan = bahan
        self.catatan = catatan
        self._kode = {a.kode for a in putaran.analisis}

    def jalankan(self, nama: str, argumen: dict) -> str:
        try:
            if nama == "muat_skill":
                return self.muat_skill(str(argumen.get("nama", "")))
            if nama == "cari_teks":
                return self.cari_teks(str(argumen.get("teks", "")))
            if nama == "buka_tabel":
                return self.buka_tabel(
                    int(argumen.get("nomor", -1)),
                    int(argumen.get("dari_baris", 1) or 1),
                    int(argumen.get("sampai_baris", 0) or 0),
                )
            if nama == "jumlah_kolom":
                if self.bahan.berlabel.bahan is None:
                    return "Naskah ini tidak memuat tabel."
                return jumlah_kolom(self.bahan.berlabel.bahan, int(argumen.get("nomor", -1)), int(argumen.get("kolom", 0)))
            if nama == "cari_format":
                return self.cari_format(argumen)
            if nama == "ringkas_menjorok":
                return self.ringkas_menjorok(str(argumen.get("pasal", "") or ""))
            if nama == "cari_korpus":
                return self.cari_korpus(str(argumen.get("teks", "")))
            if nama == "cek_peraturan":
                return self.cek_peraturan(str(argumen.get("sebutan", "")))
            if nama == "catat_temuan":
                return self.catat_temuan(argumen)
            if nama == "selesai":
                return self.selesai(argumen)
        except (TypeError, ValueError) as e:
            return f"Argumen alat {nama} tidak terbaca: {e}"
        return f"Alat {nama!r} tidak ada di putaran ini."

    # -- membaca ------------------------------------------------------------

    def muat_skill(self, nama: str) -> str:
        s = self.bahan.katalog.skill.get(nama.strip())
        if s is None or nama.strip().endswith("/label"):
            ada = ", ".join(x.nama for x in self.bahan.katalog.skill.values() if not x.nama.endswith("/label"))
            return f"Skill {nama!r} tidak ada. Yang ada: {ada}."
        if s.nama not in self.catatan.skill_dimuat:
            self.catatan.skill_dimuat.append(s.nama)
        return s.teks

    def _letak(self, index: int) -> str:
        return self.bahan.peta.get(index, "")

    def cari_teks(self, teks: str) -> str:
        kunci = _rapat(teks)
        if not kunci:
            return "Teks yang dicari kosong."
        ketemu: list[str] = []
        jumlah = 0
        for p in self.bahan.paragraf:
            isi = _rapi(p.utuh)
            if kunci not in _rapat(isi):
                continue
            jumlah += 1
            if len(ketemu) < _HASIL_CARI_MAKS:
                label = self._letak(p.index)
                ketemu.append(f"- ¶{p.index}{f' [{label}]' if label else ''} {_potong(isi, teks)}")
        bahan_lama = self.bahan.berlabel.bahan
        raksasa = bahan_lama.tabel_raksasa if bahan_lama else {}
        for k in raksasa.values():
            for b, sel in enumerate(k.contoh):
                isi = " | ".join(sel)
                if kunci in _rapat(isi):
                    jumlah += 1
                    if len(ketemu) < _HASIL_CARI_MAKS:
                        ketemu.append(f"- [tabel {k.tabel}, contoh baris {b + 1}] {_potong(isi, teks)}")
        catatan = ""
        if raksasa:
            catatan = (
                " Isi tabel raksasa yang hanya dikirim kerangkanya dari panel "
                f"(tabel {', '.join(str(n) for n in sorted(raksasa))}) tidak ikut diperiksa selain baris contohnya."
            )
        if not jumlah:
            return (
                f"TIDAK KETEMU: {teks!r} tidak ada di {angka(len(self.bahan.paragraf))} paragraf "
                f"naskah, termasuk lampiran dan isi tabel.{catatan}"
            )
        lebih = f" (ditampilkan {_HASIL_CARI_MAKS} pertama)" if jumlah > _HASIL_CARI_MAKS else ""
        return f"KETEMU di {jumlah} paragraf{lebih}:{catatan}\n" + "\n".join(ketemu)

    def buka_tabel(self, nomor: int, dari_baris: int = 1, sampai_baris: int = 0) -> str:
        bahan_lama = self.bahan.berlabel.bahan
        if bahan_lama is None:
            return "Naskah ini tidak memuat tabel."
        if nomor in bahan_lama.tabel_raksasa:
            k = bahan_lama.tabel_raksasa[nomor]
            return (
                f"Tabel {nomor} ({angka(k.jumlah_baris)} baris) terlalu besar untuk dibaca panel; "
                "isinya tidak pernah dikirim, jadi tidak bisa dibuka. Yang ada hanya baris "
                "contohnya:\n" + "\n".join(baris_tabel(b) for b in k.contoh)
            )
        t = bahan_lama.tabel.get(nomor)
        if t is None:
            ada = ", ".join(str(n) for n in sorted(bahan_lama.tabel)) or "-"
            return f"Tabel {nomor} tidak ada. Nomor tabel yang ada: {ada}."
        dari = max(1, dari_baris)
        sampai = sampai_baris if sampai_baris >= dari else dari + _BARIS_TABEL_MAKS - 1
        sampai = min(sampai, len(t.baris), dari + _BARIS_TABEL_MAKS - 1)
        if dari > len(t.baris):
            return f"Tabel {nomor} hanya {len(t.baris)} baris."
        rentang = self.bahan.berlabel.baris_tabel_paragraf
        baris = []
        for i in range(dari, sampai + 1):
            r = rentang.get((nomor, i - 1))
            letak = (f"¶{r[0]}" if r[0] == r[1] else f"¶{r[0]}–¶{r[1]}") + " " if r else ""
            baris.append(f"{i}. {letak}{baris_tabel(t.baris[i - 1])}")
        return f"Tabel {nomor}, baris {dari}–{sampai} dari {len(t.baris)}:\n" + "\n".join(baris)

    def cari_format(self, argumen: dict) -> str:
        diminta = {
            k: argumen[k]
            for k in (
                "huruf", "ukuran", "rata", "kiri_cm", "baris_pertama_cm",
                "spasi_baris", "spasi_sebelum_pt", "spasi_sesudah_pt",
            )
            if argumen.get(k) not in (None, "")
        }
        if not diminta:
            return "Berikan sekurang-kurangnya satu nilai yang mau dibandingkan, mis. huruf dan ukuran."
        dari = argumen.get("dari_paragraf")
        sampai = argumen.get("sampai_paragraf")
        beda: list[str] = []
        tanpa_format = 0
        for p in self.bahan.paragraf:
            if dari is not None and p.index < int(dari):
                continue
            if sampai is not None and p.index > int(sampai):
                continue
            if not _rapi(p.teks):
                continue
            f = p.format
            if f is None:
                tanpa_format += 1
                continue
            selisih = []
            for k, v in diminta.items():
                ada = getattr(f, k, None)
                if ada is None:
                    continue
                if isinstance(v, (int, float)) and isinstance(ada, (int, float)):
                    if abs(float(ada) - float(v)) > _TOLERANSI_CM:
                        selisih.append(f"{k} {ada:g}".replace(".", ","))
                elif str(ada).strip().lower() != str(v).strip().lower():
                    selisih.append(f"{k} {ada}")
            if selisih:
                label = self.bahan.id_awal.get(p.index, "")
                beda.append(
                    f"- ¶{p.index}{f' [{label}]' if label else ''} {_rapi(p.utuh)[:70]} — "
                    + " · ".join(selisih)
                )
        kepala = "Dibandingkan dengan: " + " · ".join(f"{k} {v}" for k, v in diminta.items())
        if tanpa_format:
            kepala += f". {tanpa_format} paragraf berisi tidak punya bacaan format dan tidak dibandingkan"
        if not beda:
            return kepala + ".\nTidak ada paragraf berisi yang berbeda."
        return kepala + f".\n{len(beda)} paragraf berbeda:\n" + "\n".join(beda)

    def ringkas_menjorok(self, pasal: str) -> str:
        pohon = self.bahan.pohon
        daftar = [pohon.cari(pasal.lower())] if pasal else pohon.semua(JenisSatuan.PASAL)
        daftar = [p for p in daftar if p is not None]
        if not daftar:
            return f"Pasal {pasal!r} tidak ada di peta letak."
        baris = []
        for p in daftar:
            grup: dict[str, Counter] = {}
            for s in pohon.satuan:
                if not s.id.startswith(p.id + "-"):
                    continue
                q = self.bahan.menurut_index.get(s.paragraf_mulai)
                if q is None or q.format is None:
                    continue
                bag = s.id[len(p.id) + 1 :].split("-")
                tingkat = "-".join(bag[i] for i in range(0, len(bag), 2))
                kiri = q.format.kiri_cm if q.format.kiri_cm is not None else 0.0
                awal = q.format.baris_pertama_cm if q.format.baris_pertama_cm is not None else 0.0
                grup.setdefault(tingkat, Counter())[(round(kiri, 1), round(awal, 1))] += 1
            if not grup:
                continue
            potong = []
            for tingkat, c in grup.items():
                isi = ", ".join(
                    f"{_cm(k)}/{_cm(a)} cm ×{n}" for (k, a), n in c.most_common()
                )
                potong.append(f"{tingkat}: {isi}")
            nama = "Pasal " + p.nomor
            baris.append(f"- {nama} [{p.id}] · " + " · ".join(potong))
        if not baris:
            return "Tidak ada bacaan menjorok untuk satuan di bawah pasal — format tidak terbaca."
        return "Menjorok kiri / baris pertama per tingkat:\n" + "\n".join(baris)

    # -- korpus ---------------------------------------------------------------

    def cari_korpus(self, teks: str) -> str:
        if self.bahan.korpus is None or self.bahan.perapal is None:
            return "Korpus tidak tersedia di putaran ini."
        kueri = teks.strip()[:_PANJANG_KUERI]
        if not kueri:
            return "Teks yang dicari kosong."
        try:
            vektor = self.bahan.perapal.rapalkan(kueri)
        except Exception as e:  # noqa: BLE001 — embedding gagal, pakai pencarian teks
            vektor = []
            gagal_vektor = f" (embedding gagal: {type(e).__name__}, dicari dengan teks biasa)"
        else:
            gagal_vektor = ""
        hasil = self.bahan.korpus.cari(kueri, vektor, 5)
        if hasil.gagal:
            return f"Pencarian korpus gagal: {hasil.gagal}"
        tercatat = [
            {"sebutan": p.sebutan, "judul": p.judul, "pasal": p.pasal, "potongan": p.potongan}
            for p in hasil.pembanding
        ]
        self.catatan.korpus.append({"teks": kueri, "pembanding": tercatat})
        if not tercatat:
            return (
                "Tidak ada pembanding berlaku yang ketemu" + gagal_vektor + ". "
                "'Tidak ketemu di korpus' bukan temuan."
            )
        baris = [
            f"{len(tercatat)} pembanding (peraturan masih berlaku; teks hasil pemindaian){gagal_vektor}. "
            "Salin nama peraturannya persis bila dipakai:"
        ]
        for p in hasil.pembanding:
            baris.append(f"- [{p.sebutan}{' ' + p.pasal if p.pasal else ''}] {p.judul} — {_rapi(p.potongan)[:700]}")
        return "\n".join(baris)

    def cek_peraturan(self, sebutan: str) -> str:
        if self.bahan.pencari is None:
            return "Korpus tidak tersedia di putaran ini."
        kutipan = baca_kutipan(sebutan.strip())
        if kutipan is None:
            return f"Bentuk peraturan {sebutan!r} tidak dikenali — tidak dicari. Diam."
        s = self.bahan.pencari.status_peraturan(kutipan)
        self.catatan.peraturan[_rapi(sebutan)] = {
            "kutipan": str(kutipan),
            "berlaku": s.berlaku,
            "judul": s.judul,
            "nomor": s.nomor,
            "alasan": s.alasan,
        }
        if s.berlaku is None:
            return f"{kutipan}: TIDAK TAHU — {s.alasan}. Diam."
        status = "Berlaku" if s.berlaku else "Tidak Berlaku"
        return f"{kutipan}: {status} menurut korpus — {s.judul} ({s.nomor})."

    # -- mencatat -----------------------------------------------------------

    def catat_temuan(self, a: dict) -> str:
        def tolak(alasan: str) -> str:
            self.catatan.ditolak_catat.append(alasan)
            return "DITOLAK — " + alasan + " Catat ulang."

        kode = str(a.get("analisis", "")).strip()
        if kode not in self._kode:
            return tolak(f"analisis {kode!r} bukan tugas putaran ini; yang ada: {', '.join(sorted(self._kode))}.")
        letak = str(a.get("letak", "")).strip()
        par = paragraf_letak(letak, self.bahan)
        if par is None:
            return tolak(f"letak {letak!r} tidak ada — pakai label satuan seperti di naskah, atau ¶nomor.")
        kutipan = str(a.get("kutipan", "")).strip()
        if not kutipan:
            return tolak("kutipan kosong.")
        if len(kutipan) > KUTIPAN_MAKS:
            return tolak(f"kutipan {len(kutipan)} huruf, lebih dari {KUTIPAN_MAKS} — kutip bagian terpendek yang salah.")
        if "\n" in kutipan:
            return tolak("kutipan melewati satu paragraf — kutip dari satu paragraf saja.")
        di_teks = kutipan_di(kutipan, par) is not None
        if not di_teks and not _di_tersembunyi(kutipan, par):
            contoh = " / ".join(_rapi(p.utuh)[:160] for p in par if _rapi(p.utuh))[:400]
            return tolak(
                f"kutipan tidak ketemu persis di {letak} — huruf dan tanda baca wajib persis "
                f"(spasi dilonggarkan). Isi {letak}: {contoh!r}."
            )
        if di_teks and (n := jumlah_kemunculan(kutipan, par)) > 1:
            return tolak(
                f"kutipan {kutipan!r} muncul {n} kali di {letak}, jadi tempat yang dimaksud tidak "
                "pasti — kutip lebih panjang, sertakan kata sebelum atau sesudahnya, supaya hanya "
                "satu yang cocok; atau sebut letak yang lebih sempit (label ayat/huruf, atau ¶nomor)."
            )
        bentuk = str(a.get("bentuk", "catatan")).strip().lower()
        if bentuk not in ("usulan", "dibuang", "catatan"):
            return tolak("bentuk wajib usulan, dibuang, atau catatan.")
        usulan = str(a.get("usulan", "") or "").strip()
        if bentuk == "usulan" and not usulan:
            return tolak("bentuk usulan tanpa isi usulan.")
        alasan_buang = str(a.get("alasan_buang", "") or "").strip()
        if bentuk == "dibuang" and alasan_buang not in ("tidak_dipakai", "mengulang", "frasa_dilarang"):
            return tolak("bentuk dibuang wajib menyebut alasan_buang: tidak_dipakai, mengulang, atau frasa_dilarang.")
        if self.putaran.berformat and not str(a.get("bukti_format", "") or "").strip():
            return tolak("putaran format: bukti_format wajib dikutip persis dari ⟨⟩ paragraf itu.")
        temuan = str(a.get("temuan", "")).strip()
        if not temuan:
            return tolak("temuan kosong — tulis kenapa salah.")
        try:
            skor = float(a.get("skor", 0) or 0)
        except (TypeError, ValueError):
            skor = 0.0
        sisipan = a.get("sisipan") if isinstance(a.get("sisipan"), dict) else None
        rujukan = a.get("rujukan") if isinstance(a.get("rujukan"), dict) else None
        calon = CalonAgen(
            nomor=f"C{len(self.catatan.calon) + 1}",
            putaran=self.putaran.judul,
            analisis=kode,
            letak=letak,
            kutipan=kutipan,
            bentuk=bentuk,
            temuan=temuan,
            saran=str(a.get("saran", "") or "").strip(),
            usulan=usulan,
            sasaran=str(a.get("sasaran", "") or "").strip(),
            sisipan=sisipan if sisipan and str(sisipan.get("teks", "")).strip() else None,
            pembanding=str(a.get("pembanding", "") or "").strip(),
            bacaan=_daftar(a.get("bacaan")),
            tidak_ada=_daftar(a.get("tidak_ada")),
            alasan_buang=alasan_buang,
            bukti_letak=str(a.get("bukti_letak", "") or "").strip(),
            bukti_format=str(a.get("bukti_format", "") or "").strip(),
            status_peraturan=str(a.get("status_peraturan", "") or "").strip(),
            rujukan=rujukan if rujukan and str(rujukan.get("alamat", "")).strip() else None,
            ketiadaan=bool(a.get("ketiadaan", False)),
            skor=min(1.0, max(0.0, skor)),
        )
        self.catatan.calon.append(calon)
        return f"Tercatat sebagai {calon.nomor}."

    def selesai(self, a: dict) -> str:
        laporan = a.get("laporan")
        if not isinstance(laporan, list):
            return "laporan wajib berupa daftar {pasal, analisis, status, alasan}."
        sah = set(self.putaran.fokus) or {"naskah"}
        diterima = 0
        abai: list[str] = []
        for e in laporan:
            if not isinstance(e, dict):
                continue
            pasal = str(e.get("pasal", "")).strip().lower()
            kode = str(e.get("analisis", "")).strip()
            status = str(e.get("status", "")).strip().lower()
            if pasal not in sah or kode not in self._kode or status not in ("diperiksa", "tidak relevan"):
                abai.append(f"{pasal or '?'} × {kode or '?'}")
                continue
            self.catatan.laporan[(pasal, kode)] = (status, str(e.get("alasan", "") or "").strip())
            diterima += 1
        self.catatan.selesai_dipanggil = True
        pesan = f"Laporan diterima: {diterima} butir."
        if abai:
            pesan += " Diabaikan (pasal atau analisis bukan tugas putaran ini, atau status di luar pilihan): " + ", ".join(abai[:10])
        return pesan

    def belum_dilaporkan(self) -> list[tuple[str, str]]:
        sasaran = self.putaran.fokus or ["naskah"]
        return [
            (p, k)
            for p in sasaran
            for k in sorted(self._kode)
            if (p, k) not in self.catatan.laporan
        ]


def _daftar(nilai: object) -> list[str]:
    if not isinstance(nilai, list):
        return []
    return [str(b).strip() for b in nilai if str(b).strip()]


def _cm(x: float) -> str:
    return f"{x:.1f}".replace(".", ",")


def _potong(teks: str, dicari: str) -> str:
    pola = r"\s*".join(re.escape(h) for h in re.sub(r"\s+", "", dicari))
    m = re.search(pola, teks, re.IGNORECASE) if pola else None
    if m is None or len(teks) <= 2 * _POTONGAN:
        return teks
    awal, akhir = max(0, m.start() - _POTONGAN), min(len(teks), m.end() + _POTONGAN)
    return ("…" if awal else "") + teks[awal:akhir] + ("…" if akhir < len(teks) else "")
