"""TAHAP 1 · LANGKAH 2 — kode membuktikan tiap label AI, lalu menyusun peta letak.

Bukti TANPA tahu jenis naskahnya — sama untuk PMK, KMK, atau naskah
perubahan:

  - penanda cocok dengan awal paragraf: `…-ayat-2a` → "(2a)", `…-huruf-b` →
    "b.", `pasal-i` → "Pasal I", `pasal-27a` → "Pasal 27A";
  - urutan naik di antara saudara — angka, sisipan (2 < 2a < 3), Romawi, kata
    urutan (Kesatu, Kedua); huruf diurutkan menurut abjad, BUKAN dibaca
    sebagai Romawi;
  - induk ada lebih dulu; satu label hanya satu paragraf;
  - di naskah perubahan, butir yang mengutip "Pasal X" memang menyebut Pasal X;
  - cakupan: paragraf batang tubuh yang diawali penanda satuan wajib berlabel.

Logikanya dipindah dari uji 2 Okt 2026 yang lebih dulu diuji dengan label
parser yang pasti benar — uji itu sempat salah dua kali, karena "Bagian
Kesatu" dibandingkan menurut abjad dan huruf i/v/x dibaca Romawi. Kedua
jebakan itu dijaga tes `test_tahap1_bukti_label.py`.

PETA LETAK — pohon satuan yang dipakai seluruh tahap sesudahnya:

  PMK biasa: label AI dipakai bila SELURUHNYA lolos bukti. Satu saja gagal →
  seluruh peta letak memakai parser cadangan (rancangan 5.2). Bila label AI
  sama persis dengan label parser, pohon parser yang dipakai — isinya identik,
  dan teks satuan parser sudah teruji bertahun-tahun naskah.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

from app.models.satuan import JenisSatuan, PohonSatuan, Satuan
from app.models.temuan import ParagrafInput
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import bangun_pohon, id_awal_satuan

_SATUAN = re.compile(r"(pasal|ayat|huruf|angka|bab|bagian|paragraf|menimbang|mengingat)-([0-9a-z]+)")
_ROMAWI = {
    "i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6, "vii": 7, "viii": 8, "ix": 9, "x": 10,
    "xi": 11, "xii": 12, "xiii": 13, "xiv": 14, "xv": 15, "xvi": 16, "xvii": 17, "xviii": 18,
    "xix": 19, "xx": 20,
}
ORDINAL = [
    "kesatu", "kedua", "ketiga", "keempat", "kelima", "keenam", "ketujuh", "kedelapan",
    "kesembilan", "kesepuluh",
]
_TUNGGAL = {"judul", "menetapkan", "penutup", "lampiran"}

# Paragraf yang diawali penanda satuan — dipakai memeriksa cakupan.
_BERPENANDA = re.compile(r"^(\(\d+[a-z]?\)\s|[a-z]\.\s|\d+\.\s|Pasal\s+\S+$)")


def _rapat(t: str) -> str:
    return " ".join(t.split())


def unit_akhir(label: str) -> tuple[str, str]:
    seg = label.split("/")[-1]
    hit = _SATUAN.findall(seg)
    return hit[-1] if hit else (seg, "")


def induk_label(label: str) -> Optional[str]:
    if "/" in label:
        kiri, kanan = label.rsplit("/", 1)
        bag = kanan.split("-")
        return kiri if len(bag) <= 2 else kiri + "/" + "-".join(bag[:-2])
    bag = label.split("-")
    if len(bag) <= 2:
        return None
    return "-".join(bag[:-2])


def _urut(v: str) -> tuple:
    m = re.fullmatch(r"(\d+)([a-z]?)", v)
    if m:
        return (int(m.group(1)), m.group(2))
    if v in _ROMAWI:
        return (_ROMAWI[v], "")
    if v in ORDINAL:
        return (ORDINAL.index(v) + 1, "")
    return (0, v)


def penanda_cocok(label: str, teks: str) -> bool:
    jenis, v = unit_akhir(label)
    t = teks.strip()
    tl = t.lower()
    if label == "judul":
        return t.upper() == t and len(t) > 5
    if label == "menetapkan":
        return tl.startswith("menetapkan")
    if label == "penutup":
        return tl.startswith("ditetapkan")
    if label == "lampiran":
        return tl.startswith("lampiran")
    if jenis == "pasal":
        return re.fullmatch(rf"pasal\s+{re.escape(v)}", tl) is not None
    if jenis == "ayat":
        return tl.startswith(f"({v})")
    if jenis in ("huruf", "angka"):
        return tl.startswith(f"{v}.")
    if jenis in ("menimbang", "mengingat"):
        return re.search(rf"(^|[\s:]){re.escape(v)}\.", tl[:40]) is not None
    if jenis == "bab":
        return re.fullmatch(rf"bab\s+{re.escape(v)}", tl) is not None
    if jenis == "bagian":
        return tl.startswith(f"bagian {v}")
    if jenis == "paragraf":
        return re.fullmatch(rf"paragraf\s+{re.escape(v)}", tl) is not None
    return False


@dataclass
class BuktiLabel:
    lolos: dict[int, str] = field(default_factory=dict)
    gagal: list[tuple[int, str, str]] = field(default_factory=list)
    """(¶, label, alasan) — label yang tidak dipakai."""
    tanpa_label: list[int] = field(default_factory=list)
    """¶ batang tubuh berpenanda yang tidak diberi label sama sekali."""

    @property
    def utuh(self) -> bool:
        return not self.gagal and not self.tanpa_label


def teks_label(paragraf: list[ParagrafInput]) -> dict[int, str]:
    """Teks pembanding tiap paragraf: penanda + teks, seperti dibaca AI.

    Label yang terpisah sel dari teksnya ("1." | "Pemerintah Pusat …") dibaca
    dari sel nomornya — di situlah labelnya ditaruh.
    """
    return {p.index: _rapat(p.utuh) for p in paragraf}


def buktikan(label: dict[int, str], paragraf: list[ParagrafInput]) -> BuktiLabel:
    teks = teks_label(paragraf)
    hasil = BuktiLabel()
    urutan = sorted(label.items())
    pertama: dict[str, int] = {}
    for p, lab in urutan:
        pertama.setdefault(lab, p)
    terakhir_saudara: dict[tuple, str] = {}
    for p, lab in urutan:
        alasan: list[str] = []
        if p not in teks:
            alasan.append("¶ tidak ada")
        elif not penanda_cocok(lab, teks[p]):
            alasan.append("penanda tidak cocok dengan awal paragraf")
        if pertama.get(lab) != p:
            alasan.append("label dobel")
        ind = induk_label(lab)
        if ind is not None and (ind not in pertama or pertama[ind] > p):
            alasan.append(f"induk {ind} tidak ada sebelumnya")
        jenis, v = unit_akhir(lab)
        kunci = (ind, jenis)
        if lab not in _TUNGGAL:
            banding = (lambda x: (0, x)) if jenis == "huruf" else _urut
            if kunci in terakhir_saudara and banding(v) <= banding(terakhir_saudara[kunci]):
                alasan.append(f"urutan mundur sesudah {jenis} {terakhir_saudara[kunci]}")
            terakhir_saudara[kunci] = v
        if "/" in lab and lab.split("/")[-1].count("-") == 1 and jenis == "pasal":
            butir = lab.split("/")[0]
            if butir in pertama and not re.search(
                rf"pasal\s+{re.escape(v)}\b", teks.get(pertama[butir], "").lower()
            ):
                alasan.append(f"butir {butir} tidak menyebut Pasal {v.upper()}")
        if alasan:
            hasil.gagal.append((p, lab, "; ".join(alasan)))
        else:
            hasil.lolos[p] = lab

    # Cakupan: dari label pasal pertama sampai penutup, paragraf di luar tabel
    # yang diawali penanda satuan wajib berlabel. Tanpa ini, satuan yang
    # terlewat AI menumpang ke satuan sebelumnya, dan alamatnya di panel salah.
    awal = min((p for p, lab in label.items() if unit_akhir(lab)[0] == "pasal"), default=None)
    akhir = min((p for p, lab in label.items() if lab in ("penutup", "lampiran")), default=None)
    if awal is not None:
        for q in paragraf:
            if q.index < awal or (akhir is not None and q.index >= akhir) or q.tabel >= 0:
                continue
            if q.index not in label and _BERPENANDA.match(teks.get(q.index, "")):
                hasil.tanpa_label.append(q.index)
    return hasil


# ---------------------------------------------------------------------------
# Pohon satuan dari label
# ---------------------------------------------------------------------------

_JENIS_LABEL = {
    "pasal": JenisSatuan.PASAL,
    "ayat": JenisSatuan.AYAT,
    "huruf": JenisSatuan.HURUF,
    "angka": JenisSatuan.ANGKA,
    "bab": JenisSatuan.BAB,
    "bagian": JenisSatuan.BAGIAN,
    "paragraf": JenisSatuan.PARAGRAF,
    "menimbang": JenisSatuan.MENIMBANG,
    "mengingat": JenisSatuan.MENGINGAT,
}
_JENIS_TUNGGAL = {
    "judul": JenisSatuan.JUDUL,
    "menetapkan": JenisSatuan.MENETAPKAN,
    "penutup": JenisSatuan.PENUTUP,
    "lampiran": JenisSatuan.LAMPIRAN,
}

# Penanda di depan teks paragraf yang dibuang dari teks satuan — sama dengan
# yang dibuang parser.
_DEPAN = re.compile(
    r"^(?:(?:Menimbang|Mengingat|Menetapkan)\b\s*:?\s*)?"
    r"(?:\(\d+[a-z]?\)|[a-z]\.|\d+\.)\s*",
    re.IGNORECASE,
)


def _nomor(jenis: str, v: str) -> str:
    if jenis == "pasal":
        return v.upper() if not v.isdigit() else v
    if jenis == "ayat":
        return f"({v})"
    if jenis == "bab":
        return v.upper()
    if jenis == "bagian":
        return v.capitalize()
    return v


def pohon_dari_label(label: dict[int, str], paragraf: list[ParagrafInput]) -> PohonSatuan:
    """Pohon satuan dari label yang SUDAH lolos bukti.

    Rentang satuan: dari paragraf labelnya sampai label berikutnya yang bukan
    keturunannya. Teks satuan: teks paragraf labelnya tanpa penanda; bila itu
    kosong (judul "Pasal 5", atau nomor di sel tabel), paragraf-paragraf
    sesudahnya sampai label berikutnya.
    """
    urut = sorted(label.items())
    posisi = {p.index: i for i, p in enumerate(paragraf)}
    hasil: list[Satuan] = []
    bab = bagian = par_hukum = None
    akhir_naskah = paragraf[-1].index + 1 if paragraf else 0

    for n, (p, lab) in enumerate(urut):
        if lab in _JENIS_TUNGGAL:
            jenis, nomor, induk = _JENIS_TUNGGAL[lab], "", None
        else:
            j, v = unit_akhir(lab)
            jenis = _JENIS_LABEL.get(j, JenisSatuan.PASAL)
            nomor = _nomor(j, v)
            induk = induk_label(lab)
            if jenis == JenisSatuan.BAB:
                bab, bagian, par_hukum = lab, None, None
            elif jenis == JenisSatuan.BAGIAN:
                bagian, par_hukum = lab, None
            elif jenis == JenisSatuan.PARAGRAF:
                par_hukum = lab
            elif jenis == JenisSatuan.PASAL and induk is None:
                induk = par_hukum or bagian or bab

        akhir = akhir_naskah
        for p2, lab2 in urut[n + 1 :]:
            if not lab2.startswith(lab + "-") and not lab2.startswith(lab + "/"):
                akhir = p2
                break
        # Paragraf kosong di ujung rentang tidak ikut — tidak ada yang bisa
        # dikutip di sana, dan parser pun berhenti di paragraf berisi terakhir.
        while akhir - 1 > p and (posisi.get(akhir - 1) is None or not _rapat(paragraf[posisi[akhir - 1]].utuh)):
            akhir -= 1

        i = posisi.get(p)
        teks = ""
        if i is not None:
            sendiri = _rapat(paragraf[i].utuh)
            if jenis == JenisSatuan.PASAL:
                teks = ""
            elif jenis == JenisSatuan.MENETAPKAN:
                teks = re.sub(r"^.*?Menetapkan\b\s*:?\s*", "", sendiri, flags=re.IGNORECASE)
            elif jenis in (
                JenisSatuan.BAB, JenisSatuan.BAGIAN, JenisSatuan.PARAGRAF,
                JenisSatuan.JUDUL, JenisSatuan.PENUTUP, JenisSatuan.LAMPIRAN,
            ):
                teks = sendiri
            else:
                teks = _DEPAN.sub("", sendiri, count=1).strip()

            # Paragraf tanpa label sesudah label ini, sampai label berikutnya.
            lanjut: list[str] = []
            batas = urut[n + 1][0] if n + 1 < len(urut) else akhir_naskah
            for q in paragraf[i + 1 :]:
                if q.index >= batas:
                    break
                t = _rapat(q.utuh)
                if t:
                    lanjut.append(t)
            if jenis == JenisSatuan.PASAL:
                # Pasal tanpa ayat, atau kalimat pengantar rinciannya — sama
                # dengan parser: paragraf pertama sesudah judul pasal.
                teks = lanjut[0] if lanjut else ""
            elif jenis in (JenisSatuan.BAB, JenisSatuan.BAGIAN, JenisSatuan.PARAGRAF):
                # Judul bab/bagian/paragraf di baris-baris berikutnya.
                teks = " ".join([teks] + lanjut[:3]).strip()
            elif not teks:
                # Nomor di sel tabel, isinya di sel sebelahnya (bug 11).
                teks = " ".join(lanjut)
        hasil.append(
            Satuan(
                id=lab,
                jenis=jenis,
                nomor=nomor,
                teks=teks,
                induk=induk,
                paragraf_mulai=p,
                paragraf_akhir=max(akhir, p + 1),
            )
        )
    return PohonSatuan(satuan=hasil)


# ---------------------------------------------------------------------------
# Peta letak — keputusan pohon mana yang dipakai
# ---------------------------------------------------------------------------


@dataclass
class PetaLetak:
    pohon: PohonSatuan
    sumber: str
    """'label AI' · 'parser cadangan' · 'label AI = parser' · 'tidak ada'"""
    bukti: Optional[BuktiLabel] = None
    catatan: list[str] = field(default_factory=list)
    beda_parser: list[tuple[int, str, str]] = field(default_factory=list)
    """(¶, label AI, label parser) yang berbeda — kunci jawaban langkah 8."""


def peta_letak(
    label: Optional[dict[int, str]],
    paragraf: list[ParagrafInput],
    pmk_biasa: bool = True,
) -> PetaLetak:
    """Pilih pohon satuan: label AI yang terbukti, atau parser cadangan."""
    parser = bangun_pohon(paragraf)
    if label is None:
        return PetaLetak(parser, "parser cadangan", catatan=["label AI tidak diminta"])

    bukti = buktikan(label, paragraf)
    label_parser = id_awal_satuan(parser) if parser.gagal is None else {}
    beda = sorted(
        (p, label.get(p, "—"), label_parser.get(p, "—"))
        for p in set(label) | set(label_parser)
        if label.get(p) != label_parser.get(p)
    )
    catatan = [f"label AI: {len(label)}, lolos bukti {len(bukti.lolos)}"]
    if bukti.gagal:
        catatan.append(f"{len(bukti.gagal)} label gagal bukti")
    if bukti.tanpa_label:
        catatan.append(f"{len(bukti.tanpa_label)} paragraf berpenanda tanpa label")

    if pmk_biasa and not bukti.utuh:
        if parser.gagal is None:
            catatan.append("PMK biasa: ada label yang gagal → seluruh peta letak memakai parser cadangan")
            return PetaLetak(parser, "parser cadangan", bukti, catatan, beda)
        catatan.append("label AI gagal bukti DAN parser cadangan menyerah: " + parser.gagal)
        return PetaLetak(PohonSatuan(satuan=[], gagal=parser.gagal), "tidak ada", bukti, catatan, beda)

    if parser.gagal is None and not beda:
        catatan.append("label AI sama persis dengan parser → pohon parser dipakai")
        return PetaLetak(parser, "label AI = parser", bukti, catatan, beda)

    pohon = pohon_dari_label(bukti.lolos, paragraf)
    if not pohon.satuan:
        if parser.gagal is None:
            return PetaLetak(parser, "parser cadangan", bukti, catatan + ["tidak ada label yang lolos"], beda)
        return PetaLetak(PohonSatuan(satuan=[], gagal="tidak ada label yang lolos bukti"), "tidak ada", bukti, catatan, beda)
    return PetaLetak(pohon, "label AI", bukti, catatan, beda)
