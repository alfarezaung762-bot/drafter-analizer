"""TAHAP 4 — alat yang boleh dipakai model saat memastikan dugaan.

Tiga alat, semuanya kode biasa di atas bahan yang sama dengan yang dibaca
model — tidak ada yang menyentuh jaringan:

    cari_teks     mencari di SELURUH naskah, termasuk lampiran dan isi tabel,
                  tidak peka huruf besar-kecil dan jarak spasi
    buka_tabel    membuka baris-baris sebuah tabel, termasuk tabel yang di
                  bahan hanya dikirim kerangkanya
    jumlah_kolom  menjumlah angka di satu kolom tabel

Kenapa ada. Salah tandai di uji 27 Sep 2026 lahir dari model yang menyimpulkan
sesuatu TIDAK ADA tanpa pernah mencarinya ("Pasal 3 ayat (1) tidak memiliki
huruf b"). Dengan naskah utuh di tangannya pun, mencari dengan mata di teks
puluhan ribu token tidak bisa diandalkan — kode bisa. Model juga buruk
menjumlah; kode tidak.

Hasil tiap alat ditulis apa adanya ke Ekspor Tahap 4 — itu bagian dari yang
dibaca model.
"""

from __future__ import annotations

import re

from app.telaah.tahap2_persiapan.bahan import Bahan, angka, baris_tabel

# Batas kewajaran supaya satu panggilan alat tidak membanjiri percakapan.
_HASIL_CARI_MAKS = 20
_BARIS_TABEL_MAKS = 60
_POTONGAN = 90  # huruf di kiri-kanan kecocokan

ALAT_CARI = {
    "type": "function",
    "function": {
        "name": "cari_teks",
        "description": (
            "Cari teks di SELURUH naskah, termasuk lampiran dan isi tabel. Tidak "
            "peka huruf besar-kecil dan jarak spasi. Pakai sebelum menyatakan "
            "sesuatu tidak ada di naskah."
        ),
        "parameters": {
            "type": "object",
            "properties": {"teks": {"type": "string", "description": "Teks yang dicari."}},
            "required": ["teks"],
        },
    },
}

ALAT_TABEL = {
    "type": "function",
    "function": {
        "name": "buka_tabel",
        "description": (
            "Buka baris-baris tabel menurut nomornya — nomor yang tertulis di "
            "[TABEL n …] pada naskah. Berguna untuk tabel yang hanya dikirim "
            "kerangkanya."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "nomor": {"type": "integer", "description": "Nomor tabel."},
                "dari_baris": {"type": "integer", "description": "Baris pertama, mulai 1."},
                "sampai_baris": {"type": "integer", "description": "Baris terakhir."},
            },
            "required": ["nomor"],
        },
    },
}

ALAT_JUMLAH = {
    "type": "function",
    "function": {
        "name": "jumlah_kolom",
        "description": "Jumlahkan angka di satu kolom tabel. Sel yang bukan angka dilewati dan dihitung.",
        "parameters": {
            "type": "object",
            "properties": {
                "nomor": {"type": "integer", "description": "Nomor tabel."},
                "kolom": {"type": "integer", "description": "Nomor kolom, mulai 1."},
            },
            "required": ["nomor", "kolom"],
        },
    },
}


def daftar_alat(bahan: Bahan) -> list[dict]:
    """Alat yang ditawarkan untuk naskah ini. Tanpa tabel, alat tabel tidak ditawarkan."""
    if bahan.tabel:
        return [ALAT_CARI, ALAT_TABEL, ALAT_JUMLAH]
    return [ALAT_CARI]


def _rapat(teks: str) -> str:
    return re.sub(r"\s+", "", teks).lower()


def _rapi(teks: str) -> str:
    return re.sub(r"\s+", " ", teks).strip()


def _potong(teks: str, dicari: str) -> str:
    """Potongan teks di sekitar kecocokan pertama, supaya hasil cari terbaca."""
    pola = r"\s*".join(re.escape(h) for h in re.sub(r"\s+", "", dicari))
    m = re.search(pola, teks, re.IGNORECASE) if pola else None
    if m is None or len(teks) <= 2 * _POTONGAN:
        return teks
    awal, akhir = max(0, m.start() - _POTONGAN), min(len(teks), m.end() + _POTONGAN)
    return ("…" if awal else "") + teks[awal:akhir] + ("…" if akhir < len(teks) else "")


def cari_teks(bahan: Bahan, teks: str) -> str:
    kunci = _rapat(teks)
    if not kunci:
        return "Teks yang dicari kosong."
    ketemu: list[str] = []
    jumlah = 0
    for p in bahan.paragraf:
        isi = _rapi(p.utuh)
        if kunci not in _rapat(isi):
            continue
        jumlah += 1
        if len(ketemu) < _HASIL_CARI_MAKS:
            letak = bahan.id_paragraf.get(p.index) or f"paragraf {p.index}"
            tabel = f" (tabel {p.tabel}, baris {p.baris + 1})" if p.tabel >= 0 else ""
            ketemu.append(f"- [{letak}]{tabel} {_potong(isi, teks)}")
    for k in bahan.tabel_raksasa.values():
        for b, sel in enumerate(k.contoh):
            isi = " | ".join(sel)
            if kunci in _rapat(isi):
                jumlah += 1
                if len(ketemu) < _HASIL_CARI_MAKS:
                    ketemu.append(f"- [tabel {k.tabel}, contoh baris {b + 1}] {_potong(isi, teks)}")

    catatan = ""
    if bahan.tabel_raksasa:
        catatan = (
            " Isi tabel raksasa yang hanya dikirim kerangkanya dari panel "
            f"(tabel {', '.join(str(n) for n in sorted(bahan.tabel_raksasa))}) "
            "tidak ikut diperiksa selain baris contohnya."
        )
    if not jumlah:
        return (
            f"TIDAK KETEMU: {teks!r} tidak ada di {angka(len(bahan.paragraf))} "
            f"paragraf naskah, termasuk lampiran dan isi tabel.{catatan}"
        )
    lebih = f" (ditampilkan {_HASIL_CARI_MAKS} pertama)" if jumlah > _HASIL_CARI_MAKS else ""
    return f"KETEMU di {jumlah} paragraf{lebih}:{catatan}\n" + "\n".join(ketemu)


def buka_tabel(bahan: Bahan, nomor: int, dari_baris: int = 1, sampai_baris: int = 0) -> str:
    if nomor in bahan.tabel_raksasa:
        k = bahan.tabel_raksasa[nomor]
        return (
            f"Tabel {nomor} ({angka(k.jumlah_baris)} baris) terlalu besar untuk dibaca "
            "panel; isinya tidak pernah dikirim, jadi tidak bisa dibuka. Yang ada "
            "hanya baris contohnya:\n" + "\n".join(baris_tabel(b) for b in k.contoh)
        )
    t = bahan.tabel.get(nomor)
    if t is None:
        return f"Tabel {nomor} tidak ada. Nomor tabel yang ada: {', '.join(str(n) for n in sorted(bahan.tabel)) or '-'}."
    dari = max(1, dari_baris)
    sampai = sampai_baris if sampai_baris >= dari else dari + _BARIS_TABEL_MAKS - 1
    sampai = min(sampai, len(t.baris), dari + _BARIS_TABEL_MAKS - 1)
    if dari > len(t.baris):
        return f"Tabel {nomor} hanya {len(t.baris)} baris."
    baris = [f"{i}. {baris_tabel(t.baris[i - 1])}" for i in range(dari, sampai + 1)]
    return f"Tabel {nomor}, baris {dari}–{sampai} dari {len(t.baris)}:\n" + "\n".join(baris)


# "1.234.567,89" (cara Indonesia) atau "1234567.89"; tanda Rp dan spasi dibuang.
_ANGKA = re.compile(r"^-?\d{1,3}(?:\.\d{3})+(?:,\d+)?$|^-?\d+(?:,\d+)?$|^-?\d+\.\d+$")


def _baca_angka(sel: str) -> float | None:
    s = re.sub(r"(?i)rp\.?|\s", "", sel).strip()
    if not s or not _ANGKA.match(s):
        return None
    if "," in s or re.match(r"^-?\d{1,3}(?:\.\d{3})+$", s):
        s = s.replace(".", "").replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def jumlah_kolom(bahan: Bahan, nomor: int, kolom: int) -> str:
    if nomor in bahan.tabel_raksasa:
        return (
            f"Tabel {nomor} terlalu besar untuk dibaca panel; isinya tidak pernah "
            "dikirim, jadi kolomnya tidak bisa dijumlah."
        )
    t = bahan.tabel.get(nomor)
    if t is None:
        return f"Tabel {nomor} tidak ada."
    if not 1 <= kolom <= t.kolom:
        return f"Tabel {nomor} hanya punya {t.kolom} kolom."
    total, dihitung, dilewati = 0.0, 0, 0
    for sel in t.baris:
        nilai = _baca_angka(sel[kolom - 1]) if kolom - 1 < len(sel) else None
        if nilai is None:
            dilewati += 1
        else:
            total += nilai
            dihitung += 1
    bulat = int(total) if total.is_integer() else total
    teks_total = angka(bulat) if isinstance(bulat, int) else f"{bulat:,.2f}".replace(",", "#").replace(".", ",").replace("#", ".")
    return (
        f"Tabel {nomor} kolom {kolom}: jumlah {teks_total} dari {dihitung} sel berangka; "
        f"{dilewati} sel bukan angka dilewati (termasuk baris judul)."
    )


def jalankan_alat(bahan: Bahan, nama: str, argumen: dict) -> str:
    """Pelaksana untuk `tanya_dengan_alat`. Tidak pernah melempar."""
    try:
        if nama == "cari_teks":
            return cari_teks(bahan, str(argumen.get("teks", "")))
        if nama == "buka_tabel":
            return buka_tabel(
                bahan,
                int(argumen.get("nomor", -1)),
                int(argumen.get("dari_baris", 1) or 1),
                int(argumen.get("sampai_baris", 0) or 0),
            )
        if nama == "jumlah_kolom":
            return jumlah_kolom(bahan, int(argumen.get("nomor", -1)), int(argumen.get("kolom", 0)))
    except (TypeError, ValueError) as e:
        return f"Argumen alat {nama} tidak terbaca: {e}"
    return f"Alat {nama!r} tidak ada. Yang ada: cari_teks, buka_tabel, jumlah_kolom."
