"""TAHAP 2 · LANGKAH 3 — menjalankan satu putaran agen sampai `selesai`.

    kirim → jalankan alat yang diminta → kirim ulang (naskah + riwayat + hasil
    alat) → … sampai agen memanggil `selesai`

AI tidak punya ingatan: tiap langkah mengirim ulang naskah + riwayat putaran
itu. Awalan yang sama (peran + naskah) membuat potongan harga awalan prompt
berlaku. Yang dijaga kode (rancangan Fase 4 bagian 5.3):

  - TAGIH: pasal × analisis yang tidak dilaporkan di `selesai` ditagih SEKALI;
    tetap tidak → dicatat "tidak diperiksa", tidak pernah dianggap bersih.
  - MACET: alat yang sama dengan argumen yang sama berulang, atau sekian
    langkah tanpa temuan maupun status baru → putaran dihentikan; panel
    menyebut "analisis macet". Angkanya di `.env`.
  - 429: kuota Azure penuh → menunggu sesuai Retry-After, lalu lanjut — bukan
    gagal.
  - BATAL: kode berhenti mengirim request baru; yang sudah terpakai tetap
    tercatat di jejak.
  - JEJAK: tiap langkah disimpan menurut sidik pesannya; backend yang mati di
    tengah jalan melanjutkan dari langkah terakhir tanpa bayar ulang.

Tanpa batas biaya, token, atau jumlah langkah (ditetapkan penelaah 30 Sep
2026) — yang dihentikan hanya putaran yang macet.
"""

from __future__ import annotations

import hashlib
import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from typing import Callable, Optional

from app.bersama.llm import LangkahModel, Ongkos, adalah_429, tunggu_429
from app.telaah.tahap2_agen.langkah2_bagi_putaran import Putaran
from app.telaah.tahap2_agen.langkah3_alat_agen import Alat, BahanAlat, CatatanPutaran, alat_putaran
from app.telaah.tahap2_agen.peran_agen_dan_penilai import DORONG, PERAN_AGEN, TAGIH

Lapor = Callable[[str, dict], None]


@dataclass
class Setelan:
    macet_ulang: int = 3
    """Alat yang sama dengan argumen yang sama sebanyak ini → macet."""
    macet_langkah: int = 12
    """Langkah berturut-turut tanpa calon temuan maupun status baru → macet."""
    tunggu_429: float = 30.0
    """Detik menunggu 429 bila Azure tidak memberi Retry-After."""


@dataclass
class LangkahJejak:
    nomor: int
    token_masuk: int = 0
    token_keluar: int = 0
    token_cache: int = 0
    dari_simpanan: bool = False
    teks: str = ""
    alat: list[tuple[str, str, str]] = field(default_factory=list)
    """(nama, argumen mentah, hasil yang dibaca agen)."""
    catatan: list[str] = field(default_factory=list)


@dataclass
class HasilPutaran:
    putaran: Putaran
    catatan: CatatanPutaran
    langkah: list[LangkahJejak] = field(default_factory=list)
    berakhir: str = ""
    """selesai · ditagih · macet: … · dibatalkan · gagal: …"""
    tidak_diperiksa: list[tuple[str, str]] = field(default_factory=list)
    pesan_awal: str = ""
    penilai: Optional[object] = None
    ongkos: Ongkos = field(default_factory=Ongkos)
    detik: float = 0.0


def kunci_langkah(pesan: list[dict], alat: list[dict]) -> str:
    """Sidik request — jawaban tersimpan hanya dipakai ulang untuk request yang SAMA."""
    isi = json.dumps(pesan, ensure_ascii=False, sort_keys=True) + "|" + json.dumps(
        [a["function"]["name"] for a in alat]
    )
    return "agen:" + hashlib.sha1(isi.encode("utf-8")).hexdigest()


def jalankan_putaran(
    putaran: Putaran,
    bahan: BahanAlat,
    pesan_awal: str,
    klien,
    ongkos: Ongkos,
    tersimpan: Optional[dict[str, str]] = None,
    simpan: Optional[Callable[[str, str], None]] = None,
    batal: Optional[threading.Event] = None,
    lapor: Optional[Lapor] = None,
    setelan: Optional[Setelan] = None,
) -> HasilPutaran:
    setelan = setelan or Setelan()
    tersimpan = tersimpan or {}
    catatan = CatatanPutaran()
    alat = Alat(putaran, bahan, catatan)
    daftar_alat = alat_putaran(putaran, bahan)
    hasil = HasilPutaran(putaran=putaran, catatan=catatan, pesan_awal=pesan_awal)
    pesan: list[dict] = [
        {"role": "system", "content": PERAN_AGEN},
        {"role": "user", "content": pesan_awal},
    ]
    ulang: dict[tuple[str, str], int] = {}
    tanpa_kemajuan = 0
    sudah_ditagih = False
    mulai = time.monotonic()

    def kabar(keadaan: str) -> None:
        if lapor:
            lapor(
                putaran.kode,
                {
                    "judul": putaran.judul,
                    "keadaan": keadaan,
                    "langkah": len(hasil.langkah),
                    "calon": len(catatan.calon),
                },
            )

    kabar("berjalan")
    while True:
        if batal is not None and batal.is_set():
            hasil.berakhir = "dibatalkan"
            break
        nomor = len(hasil.langkah) + 1
        jejak = LangkahJejak(nomor=nomor)
        kunci = kunci_langkah(pesan, daftar_alat)
        jawab: Optional[LangkahModel] = None
        if kunci in tersimpan:
            try:
                jawab = LangkahModel.dari_json(tersimpan[kunci])
                jejak.dari_simpanan = True
            except (ValueError, KeyError):
                jawab = None
        if jawab is None:
            try:
                jawab = _minta(klien, pesan, daftar_alat, setelan, batal, jejak)
            except _Dibatalkan:
                hasil.berakhir = "dibatalkan"
                break
            except Exception as e:  # noqa: BLE001 — satu putaran gagal tidak menjatuhkan yang lain
                hasil.berakhir = f"gagal: {type(e).__name__}: {e}"
                break
            ongkos.catat_langkah(jawab)
            hasil.ongkos.catat_langkah(jawab)
            if simpan is not None:
                simpan(kunci, jawab.ke_json())
        jejak.token_masuk = jawab.token_masuk
        jejak.token_keluar = jawab.token_keluar
        jejak.token_cache = jawab.token_cache
        jejak.teks = jawab.teks
        hasil.langkah.append(jejak)
        pesan.append(jawab.pesan_asisten())

        calon_sebelum = len(catatan.calon)
        laporan_sebelum = len(catatan.laporan)
        macet = ""
        selesai_di_langkah_ini = False
        for p in jawab.panggilan:
            hasil_alat = alat.jalankan(p.nama, p.argumen) if not p.argumen_rusak else (
                f"Argumen alat {p.nama} bukan JSON yang terbaca. Kirim ulang."
            )
            jejak.alat.append((p.nama, p.argumen_mentah, hasil_alat))
            pesan.append({"role": "tool", "tool_call_id": p.id, "content": hasil_alat})
            k = (p.nama, json.dumps(p.argumen, sort_keys=True, ensure_ascii=False))
            ulang[k] = ulang.get(k, 0) + 1
            if ulang[k] >= setelan.macet_ulang and not macet:
                macet = f"alat {p.nama} dengan argumen yang sama dipanggil {ulang[k]} kali"
            if p.nama == "selesai":
                selesai_di_langkah_ini = True

        ada_kemajuan = len(catatan.calon) > calon_sebelum or len(catatan.laporan) > laporan_sebelum
        tanpa_kemajuan = 0 if ada_kemajuan else tanpa_kemajuan + 1
        kabar("berjalan")

        if selesai_di_langkah_ini or (catatan.selesai_dipanggil and not jawab.panggilan):
            kurang = alat.belum_dilaporkan()
            if not kurang:
                hasil.berakhir = "selesai"
                break
            if not sudah_ditagih:
                sudah_ditagih = True
                daftar = "\n".join(f"- {p} × {k}" for p, k in kurang)
                pesan.append({"role": "user", "content": TAGIH.format(daftar=daftar)})
                jejak.catatan.append(f"ditagih: {len(kurang)} pasal × analisis belum dilaporkan")
                tanpa_kemajuan = 0
                continue
            hasil.tidak_diperiksa = kurang
            hasil.berakhir = "ditagih"
            break

        if macet:
            hasil.berakhir = "macet: " + macet
            break
        if tanpa_kemajuan >= setelan.macet_langkah:
            hasil.berakhir = f"macet: {tanpa_kemajuan} langkah tanpa calon temuan maupun status baru"
            break
        if not jawab.panggilan:
            pesan.append({"role": "user", "content": DORONG})
            jejak.catatan.append("didorong: jawaban tanpa alat")

    if hasil.berakhir != "selesai" and not hasil.tidak_diperiksa:
        hasil.tidak_diperiksa = alat.belum_dilaporkan()
    hasil.detik = round(time.monotonic() - mulai, 1)
    return hasil


class _Dibatalkan(Exception):
    pass


def _minta(klien, pesan, alat, setelan: Setelan, batal, jejak: LangkahJejak) -> LangkahModel:
    """Satu request; 429 ditunggu sampai lewat — atau sampai dibatalkan."""
    while True:
        try:
            return klien.minta_langkah(pesan, alat)
        except Exception as e:  # noqa: BLE001
            if not adalah_429(e):
                raise
            detik = tunggu_429(e, setelan.tunggu_429)
            jejak.catatan.append(f"429 — kuota Azure penuh, menunggu {detik:g} dtk")
            akhir = time.monotonic() + detik
            while time.monotonic() < akhir:
                if batal is not None and batal.is_set():
                    raise _Dibatalkan()
                time.sleep(min(0.5, max(0.0, akhir - time.monotonic())))


def jalankan_semua(
    putaran: list[Putaran],
    pesan_awal: dict[str, str],
    bahan: dict[str, BahanAlat],
    klien,
    ongkos: Ongkos,
    tersimpan: Optional[dict[str, str]] = None,
    simpan: Optional[Callable[[str, str], None]] = None,
    batal: Optional[threading.Event] = None,
    lapor: Optional[Lapor] = None,
    setelan: Optional[Setelan] = None,
    berbarengan: int = 4,
    sesudah: Optional[Callable[[HasilPutaran], None]] = None,
) -> list[HasilPutaran]:
    """Semua putaran, berbarengan. Urutan hasil = urutan putaran.

    `bahan` per kode putaran — putaran format membaca bahan berformat.
    `sesudah` dijalankan di utas putaran itu begitu ia selesai — dipakai
    menjalankan penilai kedua tanpa menunggu putaran lain.
    """

    def satu(p: Putaran) -> HasilPutaran:
        h = jalankan_putaran(
            p, bahan[p.kode], pesan_awal[p.kode], klien, ongkos, tersimpan, simpan, batal, lapor, setelan
        )
        if sesudah is not None:
            sesudah(h)
        return h

    if berbarengan <= 1 or len(putaran) <= 1:
        return [satu(p) for p in putaran]
    with ThreadPoolExecutor(max_workers=berbarengan) as pelaksana:
        return list(pelaksana.map(satu, putaran))
