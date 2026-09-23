"""SATU-SATUNYA pintu ke OpenSearch. HANYA MEMBACA.

CLAUDE.md butir 11: dilarang menulis apa pun ke basis data produksi JDIH/Law
Analyzer. Di berkas ini larangan itu bukan niat baik melainkan bentuk kode —
yang tersedia cuma `_search`, dan tidak ada satu pun jalan ke PUT/POST dokumen,
_bulk, _update, _settings, atau _delete.

=========================================================================
BENTUK INDEKS YANG SEBENARNYA — diperiksa langsung 23 Sep 2026
=========================================================================

Sampai tanggal itu isi indeks cuma diketahui dari keterangan lisan, dan
brief 8.12 menandai sendiri bahwa itu belum diverifikasi. Sesudah diperiksa,
ternyata SELURUH tebakan awal keliru. Yang benar:

    law_analyzer_emb3sm          18.543 dokumen peraturan
    ├── Judul, Nomor, Tahun, Bentuk, Status      ← PascalCase, bukan huruf kecil
    └── Blocks[]                 nested — satu blok per pasal
        ├── Content              TEKS PASALNYA ADA DI SINI
        ├── Pasal                "pasal-14"
        ├── Type                 "CONTENT_PASAL" | "DEFINISI" | …
        └── Chunks[]             nested — CUMA VEKTOR, tanpa teks
            └── MainVector       knn_vector 1536 dim (emb3small)

Dua akibat yang menentukan bentuk kueri di bawah:

1. **Vektornya di `Chunks`, teksnya di `Blocks` induknya.** Jadi kecocokan
   makna dihitung di satu tempat dan kutipannya diambil dari tempat lain.
   Supaya keduanya menunjuk pasal yang SAMA, kuerinya bersarang dua tingkat:
   nested `Blocks` yang di dalamnya nested `Blocks.Chunks`, dan `inner_hits`
   diambil dari tingkat `Blocks`.

2. **`index.knn` TIDAK MENYALA di indeks itu.** Kueri `knn` biasa (HNSW)
   karena itu mengembalikan NOL HASIL — tanpa error, tanpa peringatan. Itu
   kegagalan paling berbahaya menurut ukuran proyek ini: diam yang tidak
   kelihatan. Jalan keluarnya `script_score` dengan `knn_score`, yang
   menghitung jarak persis tanpa menuntut indeksnya disiapkan. Ternyata cepat
   juga — 0,5–1,7 detik untuk 18 ribu dokumen.

   Menyalakan `index.knn` berarti mengubah setelan indeks produksi. DILARANG,
   dan bukan cuma karena aturan: indeks itu dipakai Law Analyzer yang sedang
   berjalan.

=========================================================================
DUA HAL YANG SUDAH DIKETAHUI TENTANG KORPUS INI, DAN KEDUANYA MENGIKAT
=========================================================================

1. TEKSNYA HASIL PEMINDAIAN. Masalah yang sama dengan salinan KMK 527:
   OCR-nya rusak ("clan" untuk "dan"). Karena itu kutipan dari korpus TIDAK
   PERNAH berstatus "visual" — penanda "belum diverifikasi" di panel memang
   harus menyala untuk tiap temuan Fase 3.

2. KORPUS MEMUAT PERATURAN YANG SUDAH DICABUT — 2.466 dari 18.543 berstatus
   "Tidak Berlaku". Menyodorkan peraturan cabut sebagai pembanding bukan
   temuan lemah, melainkan temuan SALAH. Karena itu status berlaku dipakai
   sebagai PENYARING KERAS di tingkat dokumen, bukan penurun skor.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

# --- nama medan, apa adanya dari indeks -----------------------------------
_MEDAN_DOKUMEN = ["Judul", "Nomor", "Tahun", "Bentuk", "Status"]
_JALUR_BLOK = "Blocks"
_JALUR_CHUNK = "Blocks.Chunks"
_MEDAN_VEKTOR = "Blocks.Chunks.MainVector"

# Hanya blok yang memang pasal. Tanpa ini, pembanding bisa berupa blok
# DEFINISI atau judul bab — benar secara makna, tetapi tidak bisa
# dipertentangkan dengan sebuah ketentuan.
_TIPE_PASAL = "CONTENT_PASAL"

# Nilai Status yang benar-benar ada di indeks (dihitung 23 Sep 2026):
#   law_analyzer_emb3sm : Berlaku 16.042 · Tidak Berlaku 2.466 · Dicabut 1
#   jdih                : Berlaku 10.247 · Tidak Berlaku 3.189 · (kosong) 2.065 · Tetap 211
_STATUS_BERLAKU = "Berlaku"

# Jarak yang dipakai. Mapping-nya "innerproduct", tetapi vektor OpenAI sudah
# ternormalkan sehingga cosinesimil memberi urutan yang sama — dan terukur
# lebih cepat (0,5 detik lawan 1,6 detik) pada percobaan 23 Sep 2026.
_RUANG_JARAK = "cosinesimil"

_PANJANG_KUTIPAN = 1500


class Pembanding(BaseModel):
    """Satu pasal dari peraturan lain, calon pembanding."""

    judul: str = ""
    nomor: str = ""
    bentuk: str = ""
    pasal: str = ""
    potongan: str = ""
    skor: float = 0.0
    status: str = ""

    @property
    def sebutan(self) -> str:
        """Nama yang boleh disebut model — dan yang diverifikasi Langkah 5."""
        bagian = [x for x in (self.bentuk, self.nomor) if x]
        return " ".join(bagian) if bagian else self.judul

    def baris(self) -> str:
        pasal = f" {self.pasal}" if self.pasal else ""
        return f"[{self.sebutan}{pasal}] {self.judul} — {self.potongan}"


class HasilCari(BaseModel):
    """Pembanding yang lolos, berikut yang dibuang dan alasannya."""

    pembanding: list[Pembanding] = Field(default_factory=list)
    dibuang_dicabut: int = 0
    dibuang_status_kosong: int = 0
    gagal: Optional[str] = None

    @property
    def nama_sah(self) -> set[str]:
        """Nama peraturan yang BOLEH disebut model. Ditegakkan di Langkah 5."""
        return {p.sebutan for p in self.pembanding}

    @property
    def ringkas(self) -> str:
        bagian = [f"{len(self.pembanding)} pembanding"]
        if self.dibuang_dicabut:
            bagian.append(f"{self.dibuang_dicabut} dibuang karena dicabut")
        if self.dibuang_status_kosong:
            bagian.append(
                f"{self.dibuang_status_kosong} dibuang karena status berlakunya tidak terbaca"
            )
        if self.gagal:
            bagian.append("GAGAL: " + self.gagal)
        return ", ".join(bagian)


class Korpus(Protocol):
    """Bentuk yang dipegang Fase 3. Aslinya maupun palsunya menuruti ini."""

    def cari(self, teks: str, vektor: list[float], jumlah: int) -> HasilCari: ...


def saring_status(status: str) -> Optional[bool]:
    """True berlaku, False tidak, None tidak terbaca.

    None DIPERLAKUKAN SAMA DENGAN dicabut oleh pemanggil. Dibedakan di sini
    supaya sebabnya bisa dihitung terpisah dan terlihat saat diagnosa: kalau
    suatu hari seluruh pembanding hilang, kita perlu tahu apakah korpusnya
    memang tidak memuat apa-apa atau medan statusnya yang berubah nama.
    """
    if not status or not status.strip():
        return None
    bersih = status.strip().lower()
    if bersih == "berlaku":
        return True
    if bersih in {"tidak berlaku", "dicabut"}:
        return False
    return None


def _teks(nilai: Any) -> str:
    return nilai.strip() if isinstance(nilai, str) and nilai.strip() else ""


class KorpusOpenSearch:
    """Pencarian ke indeks peraturan. GET dan _search saja."""

    def __init__(self, batas_waktu: float = 60.0) -> None:
        from app.core.config import settings

        self._url = settings.opensearch_url
        self._indeks = settings.OPENSEARCH_EMBEDDING_INDEX or settings.OPENSEARCH_INDEX
        self._auth = (
            (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD)
            if settings.OPENSEARCH_USER
            else None
        )
        self._batas_waktu = batas_waktu
        self._siap = bool(self._url and self._indeks)

    @property
    def siap(self) -> bool:
        return self._siap

    def _minta(self, badan: dict[str, Any]) -> dict[str, Any]:
        import httpx

        with httpx.Client(verify=False, timeout=self._batas_waktu) as klien:
            resp = klien.post(
                f"{self._url}/{self._indeks}/_search", json=badan, auth=self._auth
            )
            resp.raise_for_status()
            return resp.json()

    # -- bentuk kueri ------------------------------------------------------

    @staticmethod
    def _inti_vektor(vektor: list[float]) -> dict[str, Any]:
        """KNN persis lewat script_score — bukan kueri `knn` biasa.

        Kueri `knn` biasa menuntut `index.knn` menyala, dan di indeks ini ia
        TIDAK menyala: hasilnya nol tanpa error. Lihat catatan di kepala
        berkas.
        """
        return {
            "nested": {
                "path": _JALUR_CHUNK,
                "query": {
                    "script_score": {
                        "query": {"exists": {"field": _MEDAN_VEKTOR}},
                        "script": {
                            "source": "knn_score",
                            "lang": "knn",
                            "params": {
                                "field": _MEDAN_VEKTOR,
                                "query_value": vektor,
                                "space_type": _RUANG_JARAK,
                            },
                        },
                    }
                },
                "score_mode": "max",
            }
        }

    @staticmethod
    def _inti_teks(teks: str) -> dict[str, Any]:
        """Cadangan bila embedding gagal. Hasilnya lebih kasar, tetapi ada."""
        return {"match": {f"{_JALUR_BLOK}.Content": teks}}

    def _badan(self, inti: dict[str, Any], jumlah: int) -> dict[str, Any]:
        return {
            "size": jumlah,
            "_source": _MEDAN_DOKUMEN,
            "query": {
                "bool": {
                    # PENYARING KERAS di tingkat dokumen. Peraturan yang sudah
                    # dicabut tidak pernah ikut dihitung, bukan sekadar
                    # diturunkan skornya.
                    "filter": [{"term": {"Status": _STATUS_BERLAKU}}],
                    "must": [
                        {
                            "nested": {
                                "path": _JALUR_BLOK,
                                "query": {
                                    "bool": {
                                        "filter": [
                                            {
                                                "match_phrase": {
                                                    f"{_JALUR_BLOK}.Type": _TIPE_PASAL
                                                }
                                            }
                                        ],
                                        "must": [inti],
                                    }
                                },
                                "inner_hits": {
                                    "size": 1,
                                    "_source": {
                                        "includes": [
                                            f"{_JALUR_BLOK}.Content",
                                            f"{_JALUR_BLOK}.Pasal",
                                            f"{_JALUR_BLOK}.Status",
                                        ]
                                    },
                                },
                                "score_mode": "max",
                            }
                        }
                    ],
                }
            },
        }

    # -- pencarian ---------------------------------------------------------

    def cari(self, teks: str, vektor: list[float], jumlah: int = 5) -> HasilCari:
        if not self._siap:
            return HasilCari(
                gagal="OpenSearch belum terkonfigurasi. Periksa lewat GET /cek-env."
            )

        inti = self._inti_vektor(vektor) if vektor else self._inti_teks(teks)
        try:
            jawaban = self._minta(self._badan(inti, jumlah))
        except Exception as e:  # noqa: BLE001 — sengaja menangkap apa pun
            if not vektor:
                return HasilCari(gagal=f"{type(e).__name__}: {e}")
            # Pencarian vektor gagal. Dicoba sekali lagi dengan teks biasa
            # sebelum menyerah — pembanding kasar masih lebih baik daripada
            # tidak ada, dan hasilnya tetap diverifikasi Langkah 5.
            try:
                jawaban = self._minta(self._badan(self._inti_teks(teks), jumlah))
            except Exception as e2:  # noqa: BLE001
                return HasilCari(gagal=f"{type(e2).__name__}: {e2}")

        return baca_jawaban(jawaban, jumlah)


def baca_jawaban(jawaban: dict[str, Any], jumlah: int) -> HasilCari:
    """Ubah jawaban OpenSearch jadi daftar pembanding. Fungsi murni."""
    hasil = HasilCari()
    for h in (jawaban.get("hits") or {}).get("hits") or []:
        sumber = h.get("_source") or {}
        if not isinstance(sumber, dict):
            continue

        status = _teks(sumber.get("Status"))
        berlaku = saring_status(status)
        if berlaku is None:
            hasil.dibuang_status_kosong += 1
            continue
        if not berlaku:
            hasil.dibuang_dicabut += 1
            continue

        dalam = (
            ((h.get("inner_hits") or {}).get(_JALUR_BLOK) or {}).get("hits") or {}
        ).get("hits") or []
        isi_blok = dalam[0].get("_source") or {} if dalam else {}
        potongan = _teks(isi_blok.get("Content"))
        judul = _teks(sumber.get("Judul"))
        if not potongan or not judul:
            # Tanpa kutipan atau tanpa nama, pembandingnya tidak bisa
            # ditimbang penelaah — dan temuan yang tidak bisa ditimbang tidak
            # berguna.
            continue

        hasil.pembanding.append(
            Pembanding(
                judul=judul,
                nomor=_teks(sumber.get("Nomor")),
                bentuk=_teks(sumber.get("Bentuk")),
                pasal=_teks(isi_blok.get("Pasal")),
                potongan=potongan[:_PANJANG_KUTIPAN],
                skor=float(h.get("_score") or 0.0),
                status=status,
            )
        )
        if len(hasil.pembanding) >= jumlah:
            break
    return hasil


class KorpusPalsu:
    """Pembanding yang sudah disiapkan, supaya Fase 3 bisa dites tanpa jaringan."""

    def __init__(self, hasil: list[HasilCari]) -> None:
        self._antrean = list(hasil)
        self.diminta: list[str] = []

    @property
    def siap(self) -> bool:
        return True

    def cari(self, teks: str, vektor: list[float], jumlah: int = 5) -> HasilCari:
        self.diminta.append(teks)
        return self._antrean.pop(0) if self._antrean else HasilCari()


# ===========================================================================
# Pencarian peraturan MENURUT NOMORNYA — dipakai F3-002
# ===========================================================================
#
# Berbeda sama sekali dari pencarian pembanding di atas. Di sini kita sudah
# tahu peraturan mana yang dicari (disebut di Mengingat); yang ingin diketahui
# cuma satu: apakah ia masih berlaku.
#
# MASALAHNYA MEDAN `Nomor` BENTUKNYA KACAU. Diperiksa 23 Sep 2026, satu indeks
# yang sama memuat kelimanya:
#
#     'UU 1 TAHUN 2004'        'UU 17TAHUN2003'      (tanpa spasi)
#     '61/PMK.03/2022'         'PMK 246 /PMK.06/2014' (spasi nyasar)
#     'PMK 39 TAHUN 2023'
#
# dan `Tahun` kadang 2004, kadang 2004.0. `Nomor` juga medan `keyword`, jadi
# `match` tidak mengiris kata dan selalu nol hasil.
#
# Karena itu pencocokannya DUA TAHAP: OpenSearch menyaring kasar menurut
# Bentuk + Tahun (himpunan kecil, puluhan dokumen), lalu nomornya dicocokkan
# di sini dengan pembaca yang tahan segala bentuk di atas.
#
# Dan kalau hasilnya mendua — dua dokumen bernomor sama berstatus berbeda —
# jawabannya TIDAK TAHU, bukan salah satunya. Mengatakan dasar hukum penelaah
# sudah dicabut padahal masih berlaku adalah salah tandai yang paling mahal
# di seluruh alat ini.

import re as _re

_BENTUK_KUTIPAN: dict[str, tuple[str, str]] = {
    # kata di naskah          → (singkatan, nilai medan Bentuk di indeks)
    "undang-undang": ("UU", "Undang-Undang"),
    "peraturan pemerintah pengganti undang-undang": ("PERPPU", "Peraturan Pemerintah Pengganti Undang-Undang"),
    "peraturan pemerintah": ("PP", "Peraturan Pemerintah"),
    "peraturan presiden": ("PERPRES", "Peraturan Presiden"),
    "keputusan presiden": ("KEPPRES", "Keputusan Presiden"),
    "peraturan menteri keuangan": ("PMK", "Peraturan Menteri"),
    "keputusan menteri keuangan": ("KMK", "Keputusan Menteri"),
}

# Dua bentuk penulisan yang sama-sama lazim, dan keduanya harus terbaca:
#   "Undang-Undang Nomor 1 Tahun 2004 tentang …"        tahun terpisah
#   "Peraturan Menteri Keuangan Nomor 246/PMK.06/2014"  tahun di dalam nomornya
# Yang bergaris miring dicoba DULU: pada "246/PMK.06/2014" pola tahun-terpisah
# akan salah membaca "06" sebagai bagian nomor dan tahunnya tidak ketemu.
_POLA_KUTIPAN_GARIS = _re.compile(
    r"^\s*(?P<bentuk>[A-Za-z\- ]+?)\s+Nomor\s+(?P<nomor>\d+)\s*/[^/\s]+/\s*(?P<tahun>\d{4})",
    _re.IGNORECASE,
)
_POLA_KUTIPAN = _re.compile(
    r"^\s*(?P<bentuk>[A-Za-z\- ]+?)\s+Nomor\s+(?P<nomor>\d+)\b.*?Tahun\s+(?P<tahun>\d{4})",
    _re.IGNORECASE | _re.DOTALL,
)
_POLA_NOMOR_KORPUS = _re.compile(r"^(?:UU|PP|PERPPU|PERPRES|KEPPRES|PMK|KMK)?(\d+)")
_POLA_TAHUN_KORPUS = _re.compile(r"TAHUN(\d{4})|/(\d{4})\b|\b(\d{4})$")


class Kutipan(BaseModel):
    """Sebuah peraturan yang disebut di Mengingat, sesudah dibaca."""

    bentuk: str          # "UU", "PMK", …
    bentuk_indeks: str   # nilai medan `Bentuk` di korpus
    nomor: int
    tahun: int

    def __str__(self) -> str:
        return f"{self.bentuk} {self.nomor}/{self.tahun}"


def baca_kutipan(teks: str) -> Optional[Kutipan]:
    """"Undang-Undang Nomor 1 Tahun 2004 tentang …" → Kutipan(UU, 1, 2004).

    None kalau bentuknya tidak dikenali — dan itu sering, karena Mengingat
    juga memuat Ketetapan MPR, Peraturan Daerah, dan peraturan lembaga lain.
    Yang tidak dikenali DILEWATI, bukan ditebak.
    """
    bersih = teks.strip()
    m = _POLA_KUTIPAN_GARIS.match(bersih) or _POLA_KUTIPAN.match(bersih)
    if not m:
        return None
    nama = " ".join(m.group("bentuk").split()).lower().strip(" .,;")
    # Cocokkan yang TERPANJANG dulu: "peraturan pemerintah pengganti
    # undang-undang" tidak boleh terbaca sebagai "peraturan pemerintah".
    for kunci in sorted(_BENTUK_KUTIPAN, key=len, reverse=True):
        if nama.endswith(kunci):
            singkat, di_indeks = _BENTUK_KUTIPAN[kunci]
            return Kutipan(
                bentuk=singkat,
                bentuk_indeks=di_indeks,
                nomor=int(m.group("nomor")),
                tahun=int(m.group("tahun")),
            )
    return None


def baca_nomor_korpus(nomor: Any, tahun: Any) -> Optional[tuple[int, int]]:
    """Medan `Nomor` korpus yang kacau → (nomor, tahun). None kalau tak terbaca."""
    mentah = _teks(nomor).upper().replace(" ", "")
    if not mentah:
        return None
    m = _POLA_NOMOR_KORPUS.match(mentah)
    if not m:
        return None

    th: Optional[int] = None
    mt = _POLA_TAHUN_KORPUS.search(mentah)
    if mt:
        for g in mt.groups():
            if g and len(g) == 4:
                th = int(g)
                break
    if th is None and tahun is not None:
        try:
            th = int(float(tahun))
        except (TypeError, ValueError):
            th = None
    return (int(m.group(1)), th) if th is not None else None


class StatusPeraturan(BaseModel):
    """Keadaan sebuah peraturan yang disebut di Mengingat."""

    kutipan: str
    berlaku: Optional[bool] = Field(
        default=None,
        description=(
            "True masih berlaku, False sudah dicabut, None TIDAK TAHU. "
            "None wajib diperlakukan sebagai 'jangan tandai apa pun'."
        ),
    )
    judul: str = ""
    nomor: str = ""
    alasan: str = Field(default="", description="Kenapa jawabannya tidak tahu.")


class PencariPeraturan(Protocol):
    def status_peraturan(self, kutipan: Kutipan) -> StatusPeraturan: ...


class PencariOpenSearch:
    """Mencari satu peraturan menurut bentuk + nomor + tahun. Membaca saja.

    Memakai indeks JDIH (bukan indeks embedding): di situlah seluruh bentuk
    peraturan ada, termasuk Keputusan Menteri dan Peraturan Unit Eselon I.
    """

    def __init__(self, batas_waktu: float = 30.0) -> None:
        from app.core.config import settings

        self._url = settings.opensearch_url
        self._indeks = settings.OPENSEARCH_INDEX or settings.OPENSEARCH_EMBEDDING_INDEX
        self._auth = (
            (settings.OPENSEARCH_USER, settings.OPENSEARCH_PASSWORD)
            if settings.OPENSEARCH_USER
            else None
        )
        self._batas_waktu = batas_waktu
        self._siap = bool(self._url and self._indeks)

    @property
    def siap(self) -> bool:
        return self._siap

    def status_peraturan(self, kutipan: Kutipan) -> StatusPeraturan:
        if not self._siap:
            return StatusPeraturan(
                kutipan=str(kutipan), alasan="OpenSearch belum terkonfigurasi"
            )
        try:
            import httpx

            badan = {
                "size": 60,
                "_source": ["Judul", "Nomor", "Tahun", "Bentuk", "Status"],
                # Saringan KASAR saja. Nomornya dicocokkan di sisi kita, karena
                # medan `Nomor` bentuknya tidak seragam dan `keyword` sehingga
                # `match` tidak pernah mengiris katanya.
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"Bentuk": kutipan.bentuk_indeks}},
                            {"term": {"Tahun": kutipan.tahun}},
                        ]
                    }
                },
            }
            with httpx.Client(verify=False, timeout=self._batas_waktu) as klien:
                resp = klien.post(
                    f"{self._url}/{self._indeks}/_search", json=badan, auth=self._auth
                )
                resp.raise_for_status()
                jawaban = resp.json()
        except Exception as e:  # noqa: BLE001
            return StatusPeraturan(
                kutipan=str(kutipan), alasan=f"{type(e).__name__}: {e}"
            )
        return baca_status_peraturan(jawaban, kutipan)


def baca_status_peraturan(jawaban: dict[str, Any], kutipan: Kutipan) -> StatusPeraturan:
    """Cocokkan calon dari korpus ke kutipan. Fungsi murni.

    MENJAWAB "TIDAK TAHU" LEBIH SERING DARIPADA MENJAWAB. Itu disengaja:
    mengatakan dasar hukum penelaah sudah dicabut padahal masih berlaku
    adalah salah tandai yang paling mahal di seluruh alat ini — ia membuat
    penelaah mengubah bagian Mengingat yang sebenarnya sudah benar.
    """
    cocok: list[tuple[Optional[bool], str, str]] = []
    for h in (jawaban.get("hits") or {}).get("hits") or []:
        sumber = h.get("_source") or {}
        if not isinstance(sumber, dict):
            continue
        terbaca = baca_nomor_korpus(sumber.get("Nomor"), sumber.get("Tahun"))
        if terbaca != (kutipan.nomor, kutipan.tahun):
            continue
        cocok.append(
            (
                saring_status(_teks(sumber.get("Status"))),
                _teks(sumber.get("Judul")),
                _teks(sumber.get("Nomor")),
            )
        )

    if not cocok:
        return StatusPeraturan(
            kutipan=str(kutipan), alasan="tidak ditemukan di korpus"
        )

    jawab = {c[0] for c in cocok}
    if len(jawab) > 1:
        # Dua dokumen bernomor sama berstatus berbeda. Bisa jadi salinan
        # ganda, bisa jadi salah satunya keliru. Yang jelas kita tidak tahu.
        return StatusPeraturan(
            kutipan=str(kutipan),
            alasan=f"{len(cocok)} dokumen cocok tetapi statusnya berbeda-beda",
        )

    berlaku = cocok[0][0]
    return StatusPeraturan(
        kutipan=str(kutipan),
        berlaku=berlaku,
        judul=cocok[0][1],
        nomor=cocok[0][2],
        alasan="" if berlaku is not None else "status di korpus tidak terbaca",
    )


class PencariPalsu:
    """Jawaban yang sudah disiapkan, supaya F3-002 bisa dites tanpa jaringan."""

    def __init__(self, jawaban: dict[str, StatusPeraturan]) -> None:
        self._jawaban = jawaban
        self.diminta: list[str] = []

    @property
    def siap(self) -> bool:
        return True

    def status_peraturan(self, kutipan: Kutipan) -> StatusPeraturan:
        self.diminta.append(str(kutipan))
        return self._jawaban.get(
            str(kutipan),
            StatusPeraturan(kutipan=str(kutipan), alasan="tidak ditemukan di korpus"),
        )
