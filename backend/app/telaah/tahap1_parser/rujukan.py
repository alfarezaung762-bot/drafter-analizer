"""TAHAP 1 (parser) — rujukan internal: "sebagaimana dimaksud …" → satuan yang dituju.

Kode biasa, tanpa AI. Rujukan dibaca dengan pola, bukan ditanyakan ke model:
kalau model yang menentukan apa yang dirujuk, ia bisa menyebut Pasal yang
tidak ada dan kita ikut mengarang bersamanya.

Dipakai tiga langkah:
  Langkah 2  melampirkan teks yang dirujuk di samping satuan yang dibaca
  Langkah 4  melampirkan teks yang dirujuk saat MEMASTIKAN dugaan — langkah
             tempat temuan lahir
  Langkah 5  menggugurkan temuan AI yang cuma menandai sebuah rujukan yang
             tujuannya ada

Dulu rujukan hanya dicocokkan sampai tingkat ayat, dan hanya yang diawali
"Pasal N". Rujukan "Pasal 3 ayat (1) huruf b" dilampirkan sebagai seluruh
ayat (1) tanpa label hurufnya, dan "pada ayat (1) huruf b" di pasal yang
sama tidak dilampirkan sama sekali. Langkah 4 tidak menerima apa pun. Model
lalu menyimpulkan huruf b tidak ada — salah tandai pada PMK 45, 27 Sep 2026.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

from app.models.satuan import PohonSatuan, Satuan

# "sebagaimana dimaksud dalam" / "sebagaimana dimaksud pada"
_PEMBUKA = re.compile(r"sebagaimana\s+dimaksud\s+(?:dalam|pada)\s+", re.IGNORECASE)

# Satu unsur alamat. Huruf dibatasi satu huruf kecil — "huruf a", bukan
# "huruf kapital".
_UNSUR = re.compile(
    r"(Pasal)\s+(\d+[A-Z]?)\b"
    r"|(ayat)\s+\((\d+)\)"
    r"|(huruf)\s+([a-z])\b"
    r"|(angka)\s+(\d+)\b",
    re.IGNORECASE,
)

# Penyambung antar-unsur: spasi saja ("Pasal 3 ayat (1)"), atau daftar
# ("ayat (4) dan ayat (5)", "Pasal 6, Pasal 7, dan Pasal 8").
_PENYAMBUNG = re.compile(
    r"\s*(?:,\s*)?(?:(?:dan/atau|dan|atau|sampai\s+dengan)\s+)?", re.IGNORECASE
)

# Sesudah alamatnya menyusul nama peraturan lain → bukan rujukan internal.
# "Peraturan Menteri ini" justru menunjuk dokumen ini sendiri.
_PERATURAN_LAIN = re.compile(
    r"^[\s,]*(?:(?:dan|atau|dan/atau)\s+[a-z0-9]{1,3}\s+)?"
    r"(?:Undang-Undang|UU|Peraturan|Keputusan|Instruksi)\b",
    re.IGNORECASE,
)
_DOKUMEN_INI = re.compile(
    r"^[\s,]*(?:Peraturan|Keputusan)\s+Menteri\s+ini\b", re.IGNORECASE
)

_TINGKAT = {"pasal": 0, "ayat": 1, "huruf": 2, "angka": 3}


@dataclass(frozen=True)
class Rujukan:
    """Satu alamat yang disebut naskah, dan apa yang benar-benar ada di sana."""

    id_sasaran: str
    """Alamat yang DIMAKSUD naskah, mis. 'pasal-3-ayat-1-huruf-b'."""

    satuan: Optional[Satuan]
    """Satuan terdalam yang ADA di sepanjang alamat itu. Kalau huruf b tidak
    ada, ini ayat (1)-nya — supaya model melihat sendiri huruf apa saja yang
    ada. None kalau pasalnya pun tidak ada."""

    @property
    def tepat(self) -> bool:
        """Alamatnya ada persis di pohon."""
        return self.satuan is not None and self.satuan.id == self.id_sasaran


def _segmen(id_satuan: str) -> list[tuple[str, str]]:
    """'pasal-3-ayat-1-huruf-a' → [('pasal','3'), ('ayat','1'), ('huruf','a')]."""
    bagian = id_satuan.split("-")
    if len(bagian) < 2 or bagian[0] != "pasal":
        return []
    return [(bagian[i], bagian[i + 1]) for i in range(0, len(bagian) - 1, 2)]


def _susun_id(segmen: list[tuple[str, str]]) -> str:
    return "-".join(f"{j}-{n.lower()}" for j, n in segmen)


def _urai(teks: str, pos: int) -> tuple[list[list[tuple[str, str]]], int]:
    """Uraikan satu frasa alamat mulai `pos`. Kembalikan alamat-alamatnya.

    "ayat (4) dan ayat (5)" → dua alamat. Unsur yang tingkatnya sama atau
    lebih tinggi dari unsur terakhir membuka alamat baru, dengan unsur yang
    lebih tinggi diwarisi: "Pasal 6 ayat (1) dan ayat (2)" → pasal 6 ayat 1,
    pasal 6 ayat 2.
    """
    hasil: list[list[tuple[str, str]]] = []
    kini: dict[int, tuple[str, str]] = {}
    while True:
        m = _UNSUR.match(teks, pos)
        if not m:
            break
        jenis = next(g for g in (m.group(1), m.group(3), m.group(5), m.group(7)) if g).lower()
        nilai = next(g for g in (m.group(2), m.group(4), m.group(6), m.group(8)) if g)
        tingkat = _TINGKAT[jenis]
        if kini and max(kini) >= tingkat:
            hasil.append([kini[k] for k in sorted(kini)])
            kini = {k: v for k, v in kini.items() if k < tingkat}
        kini[tingkat] = (jenis, nilai)
        pos = m.end()
        s = _PENYAMBUNG.match(teks, pos)
        if s and _UNSUR.match(teks, s.end()):
            pos = s.end()
            continue
        break
    if kini:
        hasil.append([kini[k] for k in sorted(kini)])
    return hasil, pos


def _lengkapi(alamat: list[tuple[str, str]], asal_id: str) -> list[tuple[str, str]]:
    """Alamat tanpa "Pasal N" melengkapi dirinya dari letak satuan asalnya.

    "pada ayat (1) huruf b" di Pasal 4 ayat (3) → Pasal 4 ayat (1) huruf b.
    "pada angka 1" di Pasal 3 ayat (1) huruf a angka 3 → … huruf a angka 1.
    """
    if not alamat or alamat[0][0] == "pasal":
        return alamat
    tingkat_awal = _TINGKAT[alamat[0][0]]
    awalan: list[tuple[str, str]] = []
    for jenis, nilai in _segmen(asal_id):
        if jenis != "pasal" and _TINGKAT.get(jenis, 9) >= tingkat_awal:
            break
        awalan.append((jenis, nilai))
    if not awalan:
        return []
    return awalan + alamat


def _cari_terdalam(id_sasaran: str, pohon: PohonSatuan) -> Optional[Satuan]:
    """Satuan terdalam yang ada di sepanjang alamat ini."""
    segmen = _segmen(id_sasaran)
    while segmen:
        s = pohon.cari(_susun_id(segmen))
        if s is not None:
            return s
        segmen = segmen[:-1]
    return None


def _jadi_rujukan(
    alamat: list[list[tuple[str, str]]], asal_id: str, pohon: PohonSatuan
) -> list[Rujukan]:
    hasil: list[Rujukan] = []
    for a in alamat:
        lengkap = _lengkapi(a, asal_id)
        if not lengkap:
            continue
        id_sasaran = _susun_id(lengkap)
        hasil.append(Rujukan(id_sasaran, _cari_terdalam(id_sasaran, pohon)))
    return hasil


def baca_rujukan(teks: str, asal_id: str, pohon: PohonSatuan) -> list[Rujukan]:
    """Seluruh rujukan internal "sebagaimana dimaksud …" di dalam `teks`.

    `asal_id` satuan tempat teks itu berada — dipakai melengkapi alamat yang
    tidak menyebut pasalnya.
    """
    hasil: list[Rujukan] = []
    for m in _PEMBUKA.finditer(teks):
        alamat, akhir = _urai(teks, m.end())
        if not alamat:
            continue
        ekor = teks[akhir : akhir + 120]
        if _PERATURAN_LAIN.match(ekor) and not _DOKUMEN_INI.match(ekor):
            continue
        hasil += _jadi_rujukan(alamat, asal_id, pohon)
    return hasil


def frasa_rujukan_saja(frasa: str, asal_id: str, pohon: PohonSatuan) -> list[Rujukan]:
    """Kalau `frasa` SELURUHNYA alamat rujukan, kembalikan rujukannya.

    "Pasal 3 ayat (1) huruf b" dan "sebagaimana dimaksud dalam Pasal 3 ayat
    (1) huruf b" lolos; "Impor barang sebagaimana dimaksud dalam Pasal 3"
    tidak — ada kata lain di luar alamatnya. Kembalikan daftar kosong kalau
    tidak seluruhnya alamat.
    """
    teks = frasa.strip().rstrip(".,;:").strip()
    pos = 0
    m = _PEMBUKA.match(teks)
    if m:
        pos = m.end()
    alamat, akhir = _urai(teks, pos)
    if not alamat or teks[akhir:].strip():
        return []
    return _jadi_rujukan(alamat, asal_id, pohon)


def baris_dirujuk(r: Rujukan, pohon: PohonSatuan) -> str:
    """Satu baris lampiran untuk model: id, lalu teks berlabel berikut batangnya.

    Kalau alamat yang disebut naskah tidak ada, itu DIKATAKAN — model tidak
    dibiarkan menyimpulkannya sendiri dari teks induknya.
    """
    if r.satuan is None:
        return f"[{r.id_sasaran}] TIDAK ADA di naskah."
    isi = pohon.teks_dengan_induk(r.satuan.id) or r.satuan.teks
    if r.tepat:
        return f"[{r.satuan.id}] {isi}"
    return (
        f"[{r.id_sasaran}] TIDAK ADA di naskah — yang ada, induk terdekatnya "
        f"[{r.satuan.id}]: {isi}"
    )


def rujukan_satuan(
    satuan: Satuan, pohon: PohonSatuan, dengan_anak: bool = False
) -> list[Rujukan]:
    """Rujukan internal yang disebut satuan ini — dicari pola, bukan ditanya ke model.

    `dengan_anak` ikut membaca rujukan di anak-cucunya: tahap 4 membaca satuan
    berikut seluruh isinya, jadi rujukan di huruf c ayat (2) juga harus
    terlampir. Yang dibuang: rujukan ke dirinya sendiri, ke induknya, dan ke
    anak-cucunya — ketiganya sudah terbaca di teks yang dikirim.
    """
    sumber = [satuan]
    if dengan_anak:
        sumber += [s for s in pohon.satuan if s.id.startswith(satuan.id + "-")]
    hasil: list[Rujukan] = []
    terlihat: set[str] = set()
    for s in sumber:
        for r in baca_rujukan(s.teks, s.id, pohon):
            tid = r.satuan.id if r.satuan else r.id_sasaran
            if (
                tid == satuan.id
                or satuan.id.startswith(tid + "-")
                or tid.startswith(satuan.id + "-")
                or tid in terlihat
            ):
                continue
            terlihat.add(tid)
            hasil.append(r)
    return hasil


def satuan_dirujuk(
    satuan: Satuan, pohon: PohonSatuan, dengan_anak: bool = False
) -> list[Satuan]:
    """Satuan yang ADA dan disebut oleh satuan ini — lihat `rujukan_satuan`."""
    return [r.satuan for r in rujukan_satuan(satuan, pohon, dengan_anak) if r.satuan]


def blok_dirujuk(diuji: list[Satuan], pohon: PohonSatuan) -> list[str]:
    """Blok "SATUAN YANG DIRUJUK" untuk tahap 4. Kosong kalau tidak ada.

    Tahap 4 tempat temuan LAHIR, dan dulu tidak menerima blok ini sama sekali:
    rujukan "Pasal 3 ayat (1) huruf b" dinilai tanpa pernah membaca Pasal 3,
    lalu dituduh menunjuk huruf yang tidak ada (PMK 45, 27 Sep 2026). Naskah
    utuh kini ikut di bahan, tetapi blok ini tetap dipasang: isinya dicari
    KODE, dan ia menyatakan terang-terangan alamat mana yang tidak ada.
    """
    ids = {s.id for s in diuji}
    baris: list[str] = []
    terlihat: set[str] = set()
    for s in diuji:
        for r in rujukan_satuan(s, pohon, dengan_anak=True):
            tid = r.satuan.id if r.satuan else r.id_sasaran
            if tid in terlihat or tid in ids:
                continue
            terlihat.add(tid)
            baris.append(baris_dirujuk(r, pohon))
    if not baris:
        return []
    return [
        "== SATUAN YANG DIRUJUK (konteks — JANGAN dikutip) ==",
        "Isi yang disebut \"sebagaimana dimaksud …\" di satuan yang diuji,",
        "diambil kode dari naskah. Rujukan yang tujuannya tercantum di sini ADA",
        "di naskah — keberadaannya bukan temuan.",
        *baris,
        "",
    ]
