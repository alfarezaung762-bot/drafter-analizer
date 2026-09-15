"""Aturan pemeriksaan format baku — Fase 1.

Setiap fungsi di modul ini adalah fungsi murni:
- Menerima daftar paragraf (list[ParagrafInput])
- Mengembalikan daftar Temuan
- Tanpa objek Request/Response
- Tanpa state global
- Bisa dites tanpa server
"""

from __future__ import annotations

import re
import uuid
from typing import Optional

from app.models.temuan import (
    AnalisisRequest,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
    TingkatKeparahan,
)
from app.rules.rujukan_kmk527 import ambil_rujukan


# ---------------------------------------------------------------------------
# Utilitas: buat Temuan
# ---------------------------------------------------------------------------

def _buat_temuan(
    aturan_id: str,
    tingkat_keparahan: TingkatKeparahan,
    paragraf: ParagrafInput,
    offset_mulai: int,
    panjang: int,
    catatan: str,
    usulan_rumusan: Optional[str] = None,
) -> Temuan:
    """Helper untuk membuat objek Temuan dengan rujukan dari tabel."""
    rujukan_dict = ambil_rujukan(aturan_id)
    return Temuan(
        id=f"f-{uuid.uuid4().hex[:8]}",
        aturan_id=aturan_id,
        fase=1,
        tingkat_keparahan=tingkat_keparahan,
        lokasi=LokasiTemuan(
            paragraf_index=paragraf.index,
            offset_mulai=offset_mulai,
            panjang=panjang,
            teks_asli=paragraf.teks[offset_mulai : offset_mulai + panjang],
        ),
        catatan=catatan,
        usulan_rumusan=usulan_rumusan,
        rujukan=RujukanTemuan(**rujukan_dict),
        status=StatusTemuan.BELUM_DITINJAU,
    )


# ---------------------------------------------------------------------------
# Utilitas: parser struktur dokumen
# ---------------------------------------------------------------------------

# Anchor-anchor di awal blok pembuka
_ANCHOR_PMK = "PERATURAN MENTERI KEUANGAN"
_ANCHOR_KMK = "KEPUTUSAN MENTERI KEUANGAN"

# Penutup judul PMK — sesudah judul, sebelum pejabat
_PENUTUP_JUDUL_PMK = "DENGAN RAHMAT TUHAN YANG MAHA ESA"

# Penutup judul KMK — langsung setelah judul
_PENUTUP_JUDUL_KMK = "MENTERI KEUANGAN REPUBLIK INDONESIA,"


def _trim(teks: str) -> str:
    """Strip dan rapatkan spasi ganda."""
    return re.sub(r"\s+", " ", teks.strip())


def _cari_index_anchor(
    paragraf: list[ParagrafInput], anchor: str, mulai: int = 0
) -> Optional[int]:
    """Cari indeks paragraf yang isinya PERSIS sama dengan anchor (case-insensitive, trimmed)."""
    for i in range(mulai, len(paragraf)):
        if _trim(paragraf[i].teks).upper() == anchor.upper():
            return i
    return None


def _cari_index_mengandung(
    paragraf: list[ParagrafInput], kata_kunci: str, mulai: int = 0
) -> Optional[int]:
    """Cari indeks paragraf yang mengandung kata kunci (case-insensitive)."""
    kata_upper = kata_kunci.upper()
    for i in range(mulai, len(paragraf)):
        if kata_upper in _trim(paragraf[i].teks).upper():
            return i
    return None


def _tentukan_jenis_dokumen(paragraf: list[ParagrafInput]) -> Optional[str]:
    """Tentukan jenis dokumen: 'PMK' atau 'KMK' dari baris pertama blok pembuka."""
    for p in paragraf:
        teks_upper = _trim(p.teks).upper()
        if _ANCHOR_PMK in teks_upper:
            return "PMK"
        if _ANCHOR_KMK in teks_upper:
            return "KMK"
    return None


def _ekstrak_judul_pembuka(paragraf: list[ParagrafInput]) -> Optional[dict]:
    """Ekstrak judul dari blok pembuka.

    Struktur:
        PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA
        NOMOR ... TAHUN ...
        TENTANG                           <- anchor
        <JUDUL, bisa >1 paragraf>
        DENGAN RAHMAT TUHAN YANG MAHA ESA <- penutup PMK
        MENTERI KEUANGAN REPUBLIK INDONESIA, <- penutup KMK

    Returns dict:
        - 'judul': teks gabungan judul
        - 'jenis': 'PMK' atau 'KMK'
        - 'paragraf_indeks': list indeks paragraf yang membentuk judul
        - 'tentang_index': indeks paragraf "TENTANG"
    """
    # Cari anchor TENTANG — harus PERSIS isinya "TENTANG", bukan sekadar mengandung
    tentang_idx = _cari_index_anchor(paragraf, "TENTANG")
    if tentang_idx is None:
        return None

    jenis = _tentukan_jenis_dokumen(paragraf)
    if jenis is None:
        return None

    # Tentukan penutup berdasarkan jenis dokumen
    penutup = _PENUTUP_JUDUL_PMK if jenis == "PMK" else _PENUTUP_JUDUL_KMK

    # Judul = semua paragraf sesudah TENTANG sampai penutup
    judul_parts: list[str] = []
    judul_indeks: list[int] = []
    for i in range(tentang_idx + 1, len(paragraf)):
        teks_trimmed = _trim(paragraf[i].teks)
        if teks_trimmed.upper() == penutup.upper():
            break
        # Cek juga penutup alternatif (KMK mungkin tanpa "REPUBLIK INDONESIA,")
        if penutup == _PENUTUP_JUDUL_KMK and teks_trimmed.upper().startswith(
            "MENTERI KEUANGAN"
        ):
            break
        judul_parts.append(teks_trimmed)
        judul_indeks.append(i)

    if not judul_parts:
        return None

    return {
        "judul": " ".join(judul_parts),
        "jenis": jenis,
        "paragraf_indeks": judul_indeks,
        "tentang_index": tentang_idx,
    }


def _ekstrak_judul_menetapkan(paragraf: list[ParagrafInput]) -> Optional[dict]:
    """Ekstrak judul dari bagian Menetapkan.

    Bentuk:
        MEMUTUSKAN:
        Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG
                     STANDAR BIAYA MASUKAN.

    Normalisasi:
        - Buang teks sampai "Menetapkan" + tanda titik dua
        - Buang awalan "PERATURAN/KEPUTUSAN MENTERI KEUANGAN TENTANG"
        - Buang titik di akhir
        - Rapatkan spasi

    Returns dict:
        - 'judul': teks judul yang sudah dinormalisasi
        - 'paragraf_indeks': list indeks paragraf
    """
    # Cari paragraf yang mengandung "Menetapkan"
    menetapkan_idx = None
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        if re.search(r"Menetapkan\s*:", teks, re.IGNORECASE):
            menetapkan_idx = i
            break

    if menetapkan_idx is None:
        return None

    # Ambil teks dari Menetapkan sampai akhir bagian
    # (sampai paragraf berikutnya yang memulai bagian baru, biasanya "BAB"/"Pasal")
    parts: list[str] = []
    indeks: list[int] = []
    for i in range(menetapkan_idx, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        # Berhenti di bagian berikutnya
        if i > menetapkan_idx and re.match(
            r"^(BAB|Pasal|PERTAMA|KEDUA|KETIGA)", teks
        ):
            break
        parts.append(teks)
        indeks.append(i)

    if not parts:
        return None

    gabungan = " ".join(parts)

    # Normalisasi: buang teks sampai "Menetapkan :"
    gabungan = re.sub(
        r"^.*?Menetapkan\s*:\s*", "", gabungan, flags=re.IGNORECASE
    )

    # Buang awalan "PERATURAN/KEPUTUSAN MENTERI KEUANGAN TENTANG"
    gabungan = re.sub(
        r"^(PERATURAN|KEPUTUSAN)\s+MENTERI\s+KEUANGAN\s+(REPUBLIK\s+INDONESIA\s+)?TENTANG\s+",
        "",
        gabungan,
        flags=re.IGNORECASE,
    )

    # Rapatkan spasi DULU, baru buang titik di akhir. Urutannya penting:
    # kalau ada paragraf kosong sesudah klausul Menetapkan — bentuk yang lazim
    # di naskah nyata — teks gabungan berakhir dengan spasi, sehingga
    # rstrip(".") tidak mengenai apa pun dan judulnya tetap berakhiran titik.
    # Akibatnya judul yang sebenarnya konsisten dilaporkan tidak konsisten.
    gabungan = _trim(gabungan)
    gabungan = gabungan.rstrip(".").strip()

    return {
        "judul": gabungan,
        "paragraf_indeks": indeks,
    }


def _normalisasi_judul_pembuka(judul: str) -> str:
    """Normalisasi judul pembuka untuk perbandingan."""
    return _trim(judul).upper()


# ---------------------------------------------------------------------------
# Utilitas: parser Menimbang/Mengingat
# ---------------------------------------------------------------------------

def _ekstrak_bagian(
    paragraf: list[ParagrafInput],
    kata_kunci_mulai: str,
    kata_kunci_akhir: str,
) -> Optional[dict]:
    """Ekstrak teks dari bagian tertentu.

    Menangani dua bentuk:
    - Bentuk A: "Menimbang" berdiri sendiri, butir di paragraf sesudahnya
    - Bentuk B: "Menimbang : a. bahwa ..." menyatu dalam satu paragraf

    Returns dict:
        - 'teks_gabungan': seluruh teks bagian digabung
        - 'paragraf_mulai': indeks paragraf pertama
        - 'paragraf_akhir': indeks paragraf terakhir (eksklusif)
    """
    # Cari posisi kata kunci mulai
    mulai_idx = None
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        # Bentuk A: paragraf isinya persis kata kunci (mungkin diikuti " :")
        # Bentuk B: paragraf dimulai dengan kata kunci
        if (
            teks.upper() == kata_kunci_mulai.upper()
            or teks.upper().startswith(kata_kunci_mulai.upper() + " ")
            or teks.upper().startswith(kata_kunci_mulai.upper() + ":")
            or re.match(
                rf"^{re.escape(kata_kunci_mulai)}\s*:",
                teks,
                re.IGNORECASE,
            )
        ):
            mulai_idx = i
            break

    if mulai_idx is None:
        return None

    # Cari posisi kata kunci akhir
    akhir_idx = len(paragraf)
    for i in range(mulai_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if (
            teks.upper() == kata_kunci_akhir.upper()
            or teks.upper().startswith(kata_kunci_akhir.upper() + " ")
            or teks.upper().startswith(kata_kunci_akhir.upper() + ":")
            or re.match(
                rf"^{re.escape(kata_kunci_akhir)}\s*:",
                teks,
                re.IGNORECASE,
            )
        ):
            akhir_idx = i
            break

    # Gabungkan teks
    parts = [_trim(paragraf[i].teks) for i in range(mulai_idx, akhir_idx)]
    return {
        "teks_gabungan": " ".join(parts),
        "paragraf_mulai": mulai_idx,
        "paragraf_akhir": akhir_idx,
    }


def _pecah_butir_menimbang(teks_gabungan: str) -> list[str]:
    """Pecah teks Menimbang menjadi butir-butir berdasarkan penanda huruf.

    Menangani pola: a. bahwa ... ; b. bahwa ... ;

    Tanda titik koma di akhir butir SENGAJA dipertahankan — butir 22 KMK 527
    mensyaratkan butir terakhir diakhiri titik koma, jadi tandanya perlu ikut
    terbawa supaya bisa diperiksa.
    """
    # Hapus awalan "Menimbang :"
    teks = re.sub(r"^Menimbang\s*:\s*", "", teks_gabungan, flags=re.IGNORECASE)
    teks = teks.strip()

    # Pecah berdasarkan penanda huruf: a. / b. / c. dst.
    # Pattern: huruf kecil diikuti titik dan spasi, di awal atau sesudah pemisah
    butir_list = re.split(r"(?:^|\s)([a-z])\.\s+", teks)

    if len(butir_list) <= 1:
        # Tidak ada penanda huruf = satu butir saja
        return [teks] if teks else []

    # re.split dengan group menghasilkan: ['', 'a', 'teks a', 'b', 'teks b', ...]
    butir_hasil: list[str] = []
    i = 1  # Lewati elemen kosong pertama
    while i < len(butir_list) - 1:
        huruf = butir_list[i]
        isi = butir_list[i + 1].strip()
        butir_hasil.append(f"{huruf}. {isi}")
        i += 2

    return butir_hasil


# ---------------------------------------------------------------------------
# Aturan 1: cek_judul_kapital (F1-001)
# ---------------------------------------------------------------------------

def cek_judul_kapital(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek apakah judul ditulis kapital seluruhnya.

    Judul = gabungan paragraf sesudah anchor TENTANG sampai penutup.
    """
    info_judul = _ekstrak_judul_pembuka(paragraf)
    if info_judul is None:
        return []

    temuan: list[Temuan] = []
    for idx in info_judul["paragraf_indeks"]:
        p = paragraf[idx]
        teks = p.teks.strip()
        if teks != teks.upper():
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-001",
                    tingkat_keparahan=TingkatKeparahan.TINGGI,
                    paragraf=p,
                    offset_mulai=0,
                    panjang=len(teks),
                    catatan="Judul peraturan seharusnya ditulis kapital seluruhnya.",
                    usulan_rumusan=teks.upper(),
                )
            )

    return temuan


# ---------------------------------------------------------------------------
# Aturan 2: cek_judul_konsisten (F1-002)
# ---------------------------------------------------------------------------

def cek_judul_konsisten(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek apakah judul di pembuka konsisten dengan judul pada Menetapkan.

    Dua sisi TIDAK simetris — perlu normalisasi:
    - Pembuka: judul berdiri sendiri tanpa awalan
    - Menetapkan: judul memakai awalan dan titik akhir
    """
    info_pembuka = _ekstrak_judul_pembuka(paragraf)
    info_menetapkan = _ekstrak_judul_menetapkan(paragraf)

    if info_pembuka is None or info_menetapkan is None:
        return []

    judul_pembuka = _normalisasi_judul_pembuka(info_pembuka["judul"])
    judul_menetapkan = _trim(info_menetapkan["judul"]).upper()

    if judul_pembuka == judul_menetapkan:
        return []

    # Temuan: laporkan di paragraf Menetapkan
    if info_menetapkan["paragraf_indeks"]:
        idx = info_menetapkan["paragraf_indeks"][0]
        p = paragraf[idx]
        return [
            _buat_temuan(
                aturan_id="F1-002",
                tingkat_keparahan=TingkatKeparahan.TINGGI,
                paragraf=p,
                offset_mulai=0,
                panjang=len(p.teks.strip()),
                catatan=(
                    f"Judul pada Menetapkan tidak konsisten dengan judul pembuka. "
                    f"Pembuka: \"{info_pembuka['judul']}\". "
                    f"Menetapkan: \"{info_menetapkan['judul']}\"."
                ),
            )
        ]

    return []


# ---------------------------------------------------------------------------
# Aturan 3: cek_kelengkapan_struktur (F1-003)
# ---------------------------------------------------------------------------

_BAGIAN_WAJIB = ["Menimbang", "Mengingat", "Menetapkan"]


def cek_kelengkapan_struktur(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek keberadaan bagian wajib: Menimbang, Mengingat, Menetapkan."""
    temuan: list[Temuan] = []

    for bagian in _BAGIAN_WAJIB:
        ditemukan = False
        for p in paragraf:
            teks = _trim(p.teks)
            if (
                teks.upper() == bagian.upper()
                or teks.upper().startswith(bagian.upper() + " ")
                or teks.upper().startswith(bagian.upper() + ":")
                or re.match(
                    rf"^{re.escape(bagian)}\s*:", teks, re.IGNORECASE
                )
            ):
                ditemukan = True
                break

        if not ditemukan:
            # Laporkan di paragraf pertama — tidak ada lokasi spesifik
            temuan.append(
                _buat_temuan(
                    aturan_id="F1-003",
                    tingkat_keparahan=TingkatKeparahan.TINGGI,
                    paragraf=paragraf[0] if paragraf else ParagrafInput(
                        index=0, teks=""
                    ),
                    offset_mulai=0,
                    panjang=0,
                    catatan=f"Bagian \"{bagian}\" tidak ditemukan dalam dokumen.",
                )
            )

    return temuan


# ---------------------------------------------------------------------------
# Aturan 4: cek_frasa_baku_menimbang (F1-004)
# ---------------------------------------------------------------------------

# Bunyi baku butir Menimbang terakhir (KMK 527 Lampiran II butir 22):
#   PMK: "bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf ...,
#         perlu menetapkan Peraturan Menteri Keuangan tentang ...;"
#   KMK: sama, dengan "Keputusan Menteri Keuangan"
# Bagian "huruf ..." dan judul sesudah "tentang" bebas isinya; yang wajib persis
# adalah kata-kata di sekitarnya, nama jenis peraturannya, dan titik komanya.

_FRASA_BERDASARKAN = "berdasarkan pertimbangan sebagaimana dimaksud dalam huruf"
_FRASA_PERLU_MENETAPKAN = "perlu menetapkan"

_FRASA_JENIS = {
    "PMK": "peraturan menteri keuangan tentang",
    "KMK": "keputusan menteri keuangan tentang",
}

_NAMA_JENIS = {
    "PMK": "Peraturan Menteri Keuangan",
    "KMK": "Keputusan Menteri Keuangan",
}


def cek_frasa_baku_menimbang(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek frasa baku butir Menimbang terakhir (KMK 527 butir 22).

    Berlaku HANYA kalau Menimbang punya lebih dari satu butir (ada huruf a/b/c).
    Kalau cuma satu butir tanpa huruf → lewati (bentuk sah, KMK 527 butir 19).

    Empat bagian yang diperiksa pada butir terakhir:
      1. frasa "bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf"
      2. frasa "perlu menetapkan"
      3. nama jenis peraturan sesuai dokumennya, diikuti kata "tentang"
      4. diakhiri tanda titik koma (;)
    """
    bagian = _ekstrak_bagian(paragraf, "Menimbang", "Mengingat")
    if bagian is None:
        return []

    butir_list = _pecah_butir_menimbang(bagian["teks_gabungan"])

    # Kalau <= 1 butir, bentuk sah — lewati
    if len(butir_list) <= 1:
        return []

    butir_terakhir_asli = butir_list[-1].strip()
    butir_terakhir = _trim(butir_terakhir_asli).lower()

    kekurangan: list[str] = []

    if _FRASA_BERDASARKAN not in butir_terakhir:
        kekurangan.append(
            "frasa \"bahwa berdasarkan pertimbangan sebagaimana dimaksud "
            "dalam huruf ...\""
        )

    if _FRASA_PERLU_MENETAPKAN not in butir_terakhir:
        kekurangan.append("frasa \"perlu menetapkan\"")

    jenis = _tentukan_jenis_dokumen(paragraf)
    if jenis in _FRASA_JENIS:
        if _FRASA_JENIS[jenis] not in butir_terakhir:
            kekurangan.append(
                f"nama jenis peraturan \"{_NAMA_JENIS[jenis]}\" sebelum kata "
                "\"tentang\" (dokumen ini berjenis " + jenis + ")"
            )
    elif "tentang" not in butir_terakhir:
        # Jenis dokumen tidak dapat ditentukan — cek minimal kata "tentang"
        kekurangan.append("kata \"tentang\"")

    if not butir_terakhir_asli.endswith(";"):
        kekurangan.append("tanda titik koma (;) di akhir butir")

    if not kekurangan:
        return []

    # Cari paragraf terdekat untuk lokasi temuan
    # Butir terakhir kemungkinan ada di paragraf menjelang akhir bagian Menimbang
    idx_temuan = bagian["paragraf_akhir"] - 1
    if idx_temuan < 0 or idx_temuan >= len(paragraf):
        idx_temuan = bagian["paragraf_mulai"]

    p = paragraf[idx_temuan]
    return [
        _buat_temuan(
            aturan_id="F1-004",
            tingkat_keparahan=TingkatKeparahan.SEDANG,
            paragraf=p,
            offset_mulai=0,
            panjang=len(p.teks.strip()),
            catatan=(
                "Butir Menimbang terakhir belum sesuai bunyi baku KMK 527 "
                "Lampiran II butir 22. Yang belum terpenuhi: "
                + "; ".join(kekurangan)
                + f". Ditemukan: \"{butir_terakhir_asli}\"."
            ),
        )
    ]


# ---------------------------------------------------------------------------
# Aturan 5: cek_ejaan (F1-005)
# ---------------------------------------------------------------------------

# Ejaan baku peraturan yang sering salah — bentuk paling sederhana dulu.
# Fokus pada ejaan khusus penyusunan peraturan, bukan typo umum.
# Urutan: frasa yang lebih panjang ditaruh lebih dulu.
_POLA_EJAAN: list[dict] = [
    {
        "salah": re.compile(r"\bperaturan\s+pemerintah\s+pengganti\s+undang-undang\b", re.IGNORECASE),
        "benar_cek": lambda m: m.group(0) != "Peraturan Pemerintah Pengganti Undang-Undang",
        "saran": "Peraturan Pemerintah Pengganti Undang-Undang",
        "catatan": "Penulisan nama jenis peraturan mengikuti ejaan baku.",
    },
    {
        "salah": re.compile(r"\bundang-undang\b", re.IGNORECASE),
        "benar_cek": lambda m: m.group(0) != "Undang-Undang",
        "saran": "Undang-Undang",
        "catatan": "\"Undang-Undang\" ditulis dengan dua huruf U kapital (KMK 527 butir 33).",
    },
]


def _ekstrak_rentang_mengingat(paragraf: list[ParagrafInput]) -> tuple[int, int]:
    """Cari rentang indeks paragraf untuk bagian Mengingat.

    Returns (mulai_idx, akhir_idx) dimana akhir_idx adalah eksklusif.
    Jika tidak ditemukan, return (-1, -1).
    """
    mulai_idx = -1
    for i, p in enumerate(paragraf):
        teks = _trim(p.teks)
        if (
            teks.upper() == "MENGINGAT"
            or teks.upper().startswith("MENGINGAT ")
            or teks.upper().startswith("MENGINGAT:")
            or re.match(r"^Mengingat\s*:", teks, re.IGNORECASE)
        ):
            mulai_idx = i
            break

    if mulai_idx == -1:
        return -1, -1

    akhir_idx = len(paragraf)
    for i in range(mulai_idx + 1, len(paragraf)):
        teks = _trim(paragraf[i].teks)
        if re.match(r"^(MEMUTUSKAN|Menetapkan|BAB\s|Pasal\s)", teks, re.IGNORECASE):
            akhir_idx = i
            break

    return mulai_idx, akhir_idx


def cek_ejaan(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Cek ejaan baku penyusunan peraturan.

    Bentuk paling sederhana: hanya ejaan khusus peraturan.
    BUKAN kamus besar bahasa Indonesia.
    """
    temuan: list[Temuan] = []

    # 1. Pola umum di seluruh dokumen (Undang-Undang, dsb.)
    for p in paragraf:
        teks = p.teks
        spans_tercatat: list[tuple[int, int]] = []
        for pola in _POLA_EJAAN:
            for match in pola["salah"].finditer(teks):
                start, end = match.start(), match.end()
                # Lewati jika span tumpang tindih dengan temuan frasa yang lebih panjang
                if any(not (end <= s or start >= e) for s, e in spans_tercatat):
                    continue
                if pola["benar_cek"](match):
                    spans_tercatat.append((start, end))
                    temuan.append(
                        _buat_temuan(
                            aturan_id="F1-005",
                            tingkat_keparahan=TingkatKeparahan.RENDAH,
                            paragraf=p,
                            offset_mulai=start,
                            panjang=end - start,
                            catatan=pola["catatan"],
                            usulan_rumusan=pola["saran"],
                        )
                    )

    # 2. Pola butir 32: kata "tentang" tetap huruf kecil di dalam judul peraturan pada dasar hukum.
    # Berlaku HANYA di dalam bagian Mengingat, bukan di seluruh dokumen.
    mulai_mengingat, akhir_mengingat = _ekstrak_rentang_mengingat(paragraf)
    if mulai_mengingat != -1:
        for i in range(mulai_mengingat, akhir_mengingat):
            p = paragraf[i]
            for match in re.finditer(r"\btentang\b", p.teks, re.IGNORECASE):
                if match.group(0) != "tentang":
                    temuan.append(
                        _buat_temuan(
                            aturan_id="F1-005",
                            tingkat_keparahan=TingkatKeparahan.RENDAH,
                            paragraf=p,
                            offset_mulai=match.start(),
                            panjang=match.end() - match.start(),
                            catatan=(
                                "Kata \"tentang\" dalam judul peraturan pada dasar hukum "
                                "tetap ditulis dengan huruf kecil (KMK 527 butir 32)."
                            ),
                            usulan_rumusan="tentang",
                        )
                    )

    return temuan


# ---------------------------------------------------------------------------
# Fungsi utama: jalankan semua pemeriksaan
# ---------------------------------------------------------------------------

def jalankan_semua(paragraf: list[ParagrafInput]) -> list[Temuan]:
    """Jalankan semua aturan Fase 1 pada daftar paragraf."""
    semua_temuan: list[Temuan] = []
    semua_temuan.extend(cek_judul_kapital(paragraf))
    semua_temuan.extend(cek_judul_konsisten(paragraf))
    semua_temuan.extend(cek_kelengkapan_struktur(paragraf))
    semua_temuan.extend(cek_frasa_baku_menimbang(paragraf))
    semua_temuan.extend(cek_ejaan(paragraf))
    return semua_temuan
