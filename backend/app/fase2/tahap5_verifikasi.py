"""LANGKAH 5 — gerbang terakhir. SATU-SATUNYA tempat calon jadi Temuan.

Seluruh langkah sebelumnya menghasilkan calon. Tidak ada satu pun yang boleh
menyentuh naskah tanpa lewat sini, dan yang diperiksa di sini bukan pendapat
model melainkan hal-hal yang bisa dibuktikan kode:

  ① Kutipannya ADA di naskah, persis huruf demi huruf, di dalam rentang
    paragraf satuan yang dimaksud. Model terbukti gemar merapikan kutipan.
    Kutipan yang meleset satu koma tidak bisa ditandai — dan yang tidak bisa
    ditandai TIDAK DITANDAI, bukan diperlebar ke satu paragraf.
  ② Pasal yang disebut di alasan/saran BENAR-BENAR ADA di dokumen. Temuan yang
    bertumpu pada pasal karangan gugur seluruhnya, sekalipun kalimatnya
    meyakinkan.
  ③ Peraturan pembanding yang disebut ADA di hasil pencarian (Fase 3). Model
    tidak boleh menyebut peraturan dari ingatannya — brief 8.10.
  ④ Istilah berdefinisi di dalam usulan dieja PERSIS. "Pengeloa Barang" untuk
    "Pengelola Barang" mengubah arti hukumnya.
  ⑤ Skornya di atas ambang yang diatur penelaah.

DUA MACAM KEGAGALAN, DAN AKIBATNYA BERBEDA:

  GUGUR       ①②③⑤ gagal → temuannya tidak ada sama sekali.
  DITURUNKAN  ④ gagal, atau usulannya bukan pengganti harfiah → temuannya
              TETAP ADA sebagai catatan kuning, tetapi usulannya tidak pernah
              disisipkan ke naskah. Panel tetap menampilkannya sebagai saran
              yang dibaca penelaah; `office.ts` hanya menyisipkan teks hijau
              untuk jenis_tanda "penggantian", jadi catatan kuning aman
              membawa saran.

Alasan gugurnya ikut dikembalikan supaya bisa dilihat saat menguji. Alat
diagnosa yang cuma bilang "tidak ada temuan" tidak bisa dibedakan dari alat
yang rusak.
"""

from __future__ import annotations

import re
import uuid
from typing import Optional

from app.fase2.tahap0_definisi import DaftarDefinisi
from app.models.pekerjaan import CalonTemuan
from app.models.satuan import PohonSatuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)
from app.rules.rujukan_kmk527 import ambil_rujukan

_PASAL_DISEBUT = re.compile(r"\bPasal\s+(\d+[A-Z]?)\b")

# Sesudah nomor pasal menyusul nama peraturan → rujukan ke dokumen lain, bukan
# ke rancangan ini. Tidak diperiksa keberadaannya di pohon.
_PASAL_DOKUMEN_LAIN = re.compile(
    r"\bPasal\s+\d+[A-Z]?\s+(Undang-Undang|Peraturan|Keputusan|UU|PP|PMK|KMK)\b"
)

# Usulan yang dimulai kata-kata ini bukan pengganti harfiah melainkan
# penjelasan — "Sebaiknya diubah menjadi ...". Kalau disisipkan apa adanya,
# kalimat itulah yang muncul hijau di naskah.
_BUKAN_PENGGANTI = re.compile(
    r"^\s*(sebaiknya|seharusnya|ganti|diubah|ubah|misalnya|contoh|gunakan|"
    r"tambahkan|hapus|perjelas|disarankan|dapat ditulis|bisa ditulis)\b",
    re.IGNORECASE,
)

# Batas kewajaran panjang usulan. Pengganti harfiah untuk sebuah frasa tidak
# masuk akal jadi lima kali lipat panjangnya — yang begitu hampir pasti
# penjelasan yang menyamar.
_LIPAT_MAKS = 5
_SELISIH_BEBAS = 40  # frasa pendek boleh melar tanpa dihitung lipatannya


class Hasil:
    """Keluaran verifikasi satu calon: temuannya, atau alasan gugurnya."""

    def __init__(self, temuan: Optional[Temuan], alasan: str = "", diturunkan: str = "") -> None:
        self.temuan = temuan
        self.alasan = alasan
        self.diturunkan = diturunkan

    @property
    def lolos(self) -> bool:
        return self.temuan is not None


def _cari_lokasi(
    calon: CalonTemuan, pohon: PohonSatuan, paragraf: list[ParagrafInput]
) -> Optional[LokasiTemuan]:
    """Pemeriksaan ① — kutipannya ada persis di dalam rentang satuannya."""
    satuan = pohon.cari(calon.satuan_id)
    if satuan is None or not satuan.bisa_ditandai:
        return None
    for p in paragraf:
        if not (satuan.paragraf_mulai <= p.index < satuan.paragraf_akhir):
            continue
        posisi = p.teks.find(calon.teks_asli)
        if posisi == -1:
            continue
        return LokasiTemuan(
            paragraf_index=p.index,
            offset_mulai=posisi,
            panjang=len(calon.teks_asli),
            teks_asli=calon.teks_asli,
        )
    return None


def pasal_karangan(teks: str, pohon: PohonSatuan) -> list[str]:
    """Pemeriksaan ② — nomor pasal yang disebut tetapi tidak ada di dokumen."""
    if not teks:
        return []
    # Buang dulu rujukan ke peraturan lain supaya tidak ikut diperiksa.
    bersih = _PASAL_DOKUMEN_LAIN.sub(" ", teks)
    hilang: list[str] = []
    for m in _PASAL_DISEBUT.finditer(bersih):
        nomor = m.group(1)
        if not pohon.ada("pasal-" + nomor.lower()) and nomor not in hilang:
            hilang.append(nomor)
    return hilang


def usulan_harfiah(usulan: str, teks_asli: str) -> bool:
    """Apakah `usulan` layak disisipkan sebagai pengganti `teks_asli`."""
    if not usulan:
        return False
    if _BUKAN_PENGGANTI.match(usulan):
        return False
    if usulan.strip() == teks_asli.strip():
        return False  # tidak mengubah apa pun
    batas = max(len(teks_asli) * _LIPAT_MAKS, len(teks_asli) + _SELISIH_BEBAS)
    return len(usulan) <= batas


def verifikasi_satu(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    ambang: float = 0.7,
    pembanding_sah: Optional[set[str]] = None,
) -> Hasil:
    """Jalankan kelima pemeriksaan atas satu calon."""

    # ⑤ Skor — diperiksa paling dulu karena paling murah.
    if calon.skor < ambang:
        return Hasil(None, f"skor {calon.skor:.2f} di bawah ambang {ambang:.2f}")

    # ③ Pembanding Fase 3 wajib berasal dari hasil pencarian.
    if pembanding_sah is not None and calon.pembanding not in pembanding_sah:
        return Hasil(
            None, "peraturan pembanding tidak ada di hasil pencarian: " + (calon.pembanding or "(kosong)")
        )

    # ② Pasal yang disebut wajib ada.
    if hilang := pasal_karangan(calon.alasan + " " + calon.saran, pohon):
        return Hasil(None, "menyebut Pasal yang tidak ada: " + ", ".join(hilang))

    # ① Kutipannya wajib ketemu persis.
    lokasi = _cari_lokasi(calon, pohon, paragraf)
    if lokasi is None:
        return Hasil(None, "kutipan tidak ketemu persis di naskah: " + repr(calon.teks_asli))

    # ④ Istilah berdefinisi di dalam usulan wajib dieja persis.
    diturunkan = ""
    usulan = calon.usulan_rumusan
    if usulan and not usulan_harfiah(usulan, calon.teks_asli):
        diturunkan = "usulan bukan pengganti harfiah"
    elif usulan and daftar.gagal is None:
        if salah_eja := daftar.cari_mirip(usulan):
            diturunkan = "istilah berdefinisi salah eja di usulan: " + ", ".join(salah_eja)

    boleh_hijau = bool(usulan) and not diturunkan
    catatan = calon.alasan
    if calon.saran:
        catatan = catatan + " Saran: " + calon.saran

    return Hasil(
        Temuan(
            id="f-" + uuid.uuid4().hex[:8],
            aturan_id=calon.aturan_id,
            fase=3 if calon.aturan_id.startswith("F3") else 2,
            jenis_tanda=JenisTanda.PENGGANTIAN if boleh_hijau else JenisTanda.CATATAN,
            satuan_id=calon.satuan_id,
            skor=calon.skor,
            lokasi=lokasi,
            catatan=catatan.strip(),
            usulan_rumusan=usulan or None,
            rujukan=RujukanTemuan(**ambil_rujukan(calon.aturan_id)),
            status=StatusTemuan.BELUM_DITINJAU,
        ),
        diturunkan=diturunkan,
    )


def verifikasi(
    calon: list[CalonTemuan],
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    ambang: float = 0.7,
    pembanding_sah: Optional[set[str]] = None,
) -> tuple[list[Temuan], list[str]]:
    """Verifikasi seluruh calon. Kembalikan temuan yang lolos dan alasan gugur.

    Temuan yang lolos diurutkan menurut posisi dokumen. Penomorannya TIDAK
    dilakukan di sini: nomor Fase 2 melanjutkan nomor terakhir Fase 1 dan
    tidak pernah diurutkan ulang, jadi hanya pemanggil yang tahu mulai dari
    berapa.
    """
    lolos: list[Temuan] = []
    gugur: list[str] = []
    for c in calon:
        hasil = verifikasi_satu(c, pohon, daftar, paragraf, ambang, pembanding_sah)
        if hasil.temuan is None:
            gugur.append(f"{c.aturan_id} {c.satuan_id}: {hasil.alasan}")
            continue
        if hasil.diturunkan:
            gugur.append(f"{c.aturan_id} {c.satuan_id}: DITURUNKAN — {hasil.diturunkan}")
        lolos.append(hasil.temuan)

    lolos.sort(key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai))
    return lolos, gugur
