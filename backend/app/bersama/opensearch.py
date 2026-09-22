"""SATU-SATUNYA pintu ke OpenSearch. HANYA MEMBACA.

CLAUDE.md butir 11: dilarang menulis apa pun ke basis data produksi JDIH/Law
Analyzer. Di berkas ini larangan itu bukan niat baik melainkan bentuk kode —
yang tersedia cuma `_search`, dan tidak ada satu pun jalan ke PUT/POST dokumen,
_bulk, _update, atau _delete.

DUA HAL YANG SUDAH DIKETAHUI TENTANG KORPUS INI, DAN KEDUANYA MENGIKAT:

  1. TEKSNYA HASIL PEMINDAIAN. Masalah yang sama dengan salinan KMK 527:
     OCR-nya rusak ("clan" untuk "dan"). Karena itu kutipan dari korpus TIDAK
     PERNAH berstatus "visual" — penanda "belum diverifikasi" di panel memang
     harus menyala untuk tiap temuan Fase 3.
  2. KORPUS MEMUAT PERATURAN YANG SUDAH DICABUT. Menyodorkan peraturan cabut
     sebagai pembanding bukan temuan lemah, melainkan temuan SALAH. Karena itu
     status berlaku dipakai sebagai PENYARING KERAS, bukan penurun skor.

     Akibatnya yang perlu diputuskan penelaah: dokumen yang status berlakunya
     TIDAK BISA DIBACA ikut dibuang. Pilihan itu memihak diam — sesuai kaidah
     proyek — tetapi kalau ternyata indeksnya memang tidak menyimpan status,
     Fase 3 akan selalu kosong. Supaya itu tidak terjadi diam-diam, jumlah
     yang dibuang ikut dilaporkan di `HasilCari.dibuang`.
"""

from __future__ import annotations

from typing import Any, Optional, Protocol

from pydantic import BaseModel, Field

# Nama medan berbeda-beda antar-skema indeks. Dicoba berurutan, yang pertama
# ada itu yang dipakai. Menebak satu nama lalu gagal diam-diam jauh lebih buruk
# daripada mencoba beberapa dan melaporkan kalau tidak satu pun ketemu.
_MEDAN_JUDUL = ("judul", "title", "nama_peraturan", "tentang", "peraturan")
_MEDAN_ISI = ("teks", "isi", "content", "body", "konten", "potongan", "chunk")
_MEDAN_STATUS = ("status", "status_berlaku", "keberlakuan", "is_active")
_MEDAN_VEKTOR = ("embedding", "vector", "teks_embedding", "content_embedding")

_STATUS_BERLAKU = {"berlaku", "aktif", "active", "valid", "true", "1"}
_STATUS_CABUT = {
    "dicabut",
    "tidak berlaku",
    "cabut",
    "inactive",
    "revoked",
    "false",
    "0",
}


class Pembanding(BaseModel):
    """Satu potongan peraturan lain, calon pembanding."""

    judul: str = ""
    potongan: str = ""
    skor: float = 0.0
    status: str = ""

    def baris(self) -> str:
        return f"[{self.judul}] {self.potongan}"


class HasilCari(BaseModel):
    """Pembanding yang lolos, berikut yang dibuang dan alasannya."""

    pembanding: list[Pembanding] = Field(default_factory=list)
    dibuang_dicabut: int = 0
    dibuang_status_kosong: int = 0
    gagal: Optional[str] = None

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


def _ambil(sumber: dict[str, Any], nama: tuple[str, ...]) -> str:
    for n in nama:
        nilai = sumber.get(n)
        if isinstance(nilai, str) and nilai.strip():
            return nilai.strip()
        if isinstance(nilai, bool):
            return "true" if nilai else "false"
    return ""


def saring_status(status: str) -> Optional[bool]:
    """True berlaku, False dicabut, None tidak terbaca.

    None DIPERLAKUKAN SAMA DENGAN dicabut oleh pemanggil. Dibedakan di sini
    supaya sebabnya bisa dihitung terpisah dan terlihat saat diagnosa.
    """
    if not status:
        return None
    bersih = status.strip().lower()
    if bersih in _STATUS_BERLAKU:
        return True
    if bersih in _STATUS_CABUT:
        return False
    return None


class KorpusOpenSearch:
    """Pencarian ke indeks JDIH. GET dan _search saja."""

    def __init__(self, batas_waktu: float = 15.0) -> None:
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

        alamat = f"{self._url}/{self._indeks}/_search"
        with httpx.Client(verify=False, timeout=self._batas_waktu) as klien:
            resp = klien.post(alamat, json=badan, auth=self._auth)
            resp.raise_for_status()
            return resp.json()

    def cari(self, teks: str, vektor: list[float], jumlah: int = 5) -> HasilCari:
        if not self._siap:
            return HasilCari(gagal="OpenSearch belum terkonfigurasi. Periksa lewat GET /cek-env.")

        # Ambil lebih banyak daripada yang dibutuhkan: penyaring status keras
        # akan memangkas sebagian, dan memangkas sesudah mengambil lebih murah
        # daripada mencari dua kali.
        ambil = max(jumlah * 3, jumlah + 5)
        badan: dict[str, Any]
        if vektor:
            badan = {
                "size": ambil,
                "query": {"knn": {_MEDAN_VEKTOR[0]: {"vector": vektor, "k": ambil}}},
            }
        else:
            badan = {
                "size": ambil,
                "query": {"multi_match": {"query": teks, "fields": list(_MEDAN_ISI)}},
            }

        try:
            jawaban = self._minta(badan)
        except Exception as e:  # noqa: BLE001 — sengaja menangkap apa pun
            # Termasuk medan vektor bernama lain. Dicoba sekali lagi dengan
            # pencarian teks biasa sebelum menyerah.
            if vektor:
                try:
                    jawaban = self._minta(
                        {
                            "size": ambil,
                            "query": {
                                "multi_match": {"query": teks, "fields": list(_MEDAN_ISI)}
                            },
                        }
                    )
                except Exception as e2:  # noqa: BLE001
                    return HasilCari(gagal=f"{type(e2).__name__}: {e2}")
            else:
                return HasilCari(gagal=f"{type(e).__name__}: {e}")

        return self._baca(jawaban, jumlah)

    @staticmethod
    def _baca(jawaban: dict[str, Any], jumlah: int) -> HasilCari:
        hasil = HasilCari()
        for h in (jawaban.get("hits") or {}).get("hits") or []:
            sumber = h.get("_source") or {}
            if not isinstance(sumber, dict):
                continue
            status = _ambil(sumber, _MEDAN_STATUS)
            berlaku = saring_status(status)
            if berlaku is None:
                hasil.dibuang_status_kosong += 1
                continue
            if not berlaku:
                hasil.dibuang_dicabut += 1
                continue
            potongan = _ambil(sumber, _MEDAN_ISI)
            judul = _ambil(sumber, _MEDAN_JUDUL)
            if not potongan or not judul:
                continue
            hasil.pembanding.append(
                Pembanding(
                    judul=judul,
                    potongan=potongan[:1500],
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
