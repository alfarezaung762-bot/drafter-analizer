"""LANGKAH 2 — membaca per satuan. Keluarannya satu baris peta per satuan.

Tiap panggilan berisi tiga bagian, dalam urutan ini:

    KONTEKS DOKUMEN   judul, Menimbang, Mengingat, definisi Pasal 1, kerangka
                      pasal. SAMA PERSIS di setiap panggilan untuk dokumen
                      yang sama, dan ditaruh PALING DEPAN supaya potongan
                      harga awalan prompt berlaku kalau deployment-nya
                      mendukung. Tanpa ini sebuah satuan dibaca tanpa tahu
                      istilahnya berarti apa.
    SATUAN DIPERIKSA  beberapa satuan sekaligus, teksnya utuh.
    (dirujuk)         satuan yang disebut "sebagaimana dimaksud dalam Pasal N"
                      ikut dilampirkan — dicari PARSER, bukan ditebak model.

Kenapa beberapa satuan sekaligus: dokumen 175 satuan tidak boleh jadi 175
panggilan. Kelompoknya tetap kecil dan BERHENTI DI BATAS PASAL, sehingga
seluruh ayat sebuah pasal selalu terbaca bersama, dan panggilan yang putus
cuma menghanguskan satu kelompok.
"""

from __future__ import annotations

import re
from typing import Callable, Optional

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, baca_json
from app.fase2.tahap0_definisi import DaftarDefinisi
from app.models.pekerjaan import BarisPeta
from app.models.satuan import JenisSatuan, PohonSatuan, Satuan
from app.models.temuan import Temuan

_RUJUKAN = re.compile(
    r"sebagaimana\s+dimaksud\s+(?:dalam|pada)\s+Pasal\s+(\d+[A-Z]?)"
    r"(?:\s+ayat\s+\((\d+)\))?",
    re.IGNORECASE,
)


def susun_konteks_tetap(pohon: PohonSatuan, daftar: DaftarDefinisi) -> str:
    """Bagian prompt yang sama persis di setiap panggilan untuk satu dokumen."""
    bagian: list[str] = ["== KONTEKS DOKUMEN =="]

    judul = pohon.semua(JenisSatuan.JUDUL)
    if judul:
        bagian.append("Judul: " + judul[0].teks)

    menimbang = pohon.semua(JenisSatuan.MENIMBANG)
    if menimbang:
        bagian.append("Menimbang:")
        bagian += ["  " + s.nomor + ". " + s.teks for s in menimbang]

    mengingat = pohon.semua(JenisSatuan.MENGINGAT)
    if mengingat:
        bagian.append("Mengingat:")
        bagian += ["  " + s.nomor + ". " + s.teks for s in mengingat]

    if daftar.gagal is None and daftar.definisi:
        bagian.append("Definisi (Pasal 1):")
        bagian += ["  " + d.istilah + " = " + d.arti for d in daftar.definisi]

    pasal = pohon.semua(JenisSatuan.PASAL)
    if pasal:
        bagian.append("Kerangka pasal: " + ", ".join("Pasal " + s.nomor for s in pasal))

    return "\n".join(bagian)


def satuan_dirujuk(satuan: Satuan, pohon: PohonSatuan) -> list[Satuan]:
    """Satuan yang disebut oleh satuan ini.

    Dicari dengan regex pada pohon, BUKAN ditanyakan ke model. Kalau model
    yang menentukan apa yang dirujuk, ia bisa menyebut Pasal yang tidak ada
    dan kita ikut mengarang bersamanya.
    """
    hasil: list[Satuan] = []
    for m in _RUJUKAN.finditer(satuan.teks):
        target = "pasal-" + m.group(1).lower()
        if m.group(2):
            target = target + "-ayat-" + m.group(2)
        rujuk = pohon.cari(target)
        if rujuk is not None and rujuk.id != satuan.id and rujuk not in hasil:
            hasil.append(rujuk)
    return hasil


def _pasal_induk(s: Satuan) -> str:
    """Nama pasal tempat satuan ini bernaung, dibaca dari id-nya."""
    return s.id.split("-ayat-")[0].split("-huruf-")[0].split("-angka-")[0]


def kelompokkan(satuan: list[Satuan], per_panggilan: int) -> list[list[Satuan]]:
    """Kelompokkan satuan, TIDAK PERNAH membelah satu pasal.

    Kelompok baru dibuka begitu jatahnya penuh DAN pasal berikutnya dimulai.
    Akibatnya sebuah kelompok boleh lebih panjang dari jatahnya — itu memang
    yang dikehendaki: pasal yang terbelah dua panggilan membuat model menilai
    ayat tanpa ayat tetangganya.
    """
    if per_panggilan < 1:
        per_panggilan = 1

    hasil: list[list[Satuan]] = []
    kini: list[Satuan] = []

    for s in satuan:
        penuh = len(kini) >= per_panggilan
        pasal_baru = bool(kini) and _pasal_induk(s) != _pasal_induk(kini[-1])
        if kini and penuh and pasal_baru:
            hasil.append(kini)
            kini = []
        kini.append(s)
    if kini:
        hasil.append(kini)
    return hasil


def temuan_di_satuan(satuan: Satuan, temuan: list[Temuan]) -> list[Temuan]:
    """Temuan yang jatuh di dalam rentang paragraf satuan ini."""
    return [
        t
        for t in temuan
        if satuan.paragraf_mulai <= t.lokasi.paragraf_index < satuan.paragraf_akhir
    ]


def susun_bahan(
    kelompok: list[Satuan],
    pohon: PohonSatuan,
    konteks: str,
    temuan_fase1: Optional[list[Temuan]] = None,
) -> str:
    """Rangkai bahan satu panggilan Langkah 2.

    Temuan Fase 1 yang jatuh di satuan ini ikut dilampirkan. Gunanya bukan
    supaya model menilainya, melainkan supaya model TIDAK MENGULANGNYA:
    duplikat yang tidak pernah lahir jauh lebih murah daripada duplikat yang
    dibuang belakangan, dan komentar yang menumpuk di margin adalah keluhan
    yang sudah pernah terjadi.
    """
    sudah = temuan_fase1 or []
    bagian = [konteks, "", "== SATUAN YANG DIPERIKSA =="]
    for s in kelompok:
        isi = pohon.teks_lengkap(s.id) or s.teks
        bagian.append("[" + s.id + "] " + isi)
        for t in temuan_di_satuan(s, sudah):
            bagian.append(
                f"    (SUDAH DITEMUKAN, T{t.nomor}) {t.catatan} "
                f"— pada teks: {t.lokasi.teks_asli!r}"
            )
        for r in satuan_dirujuk(s, pohon):
            isi_r = pohon.teks_lengkap(r.id) or r.teks
            bagian.append("    (dirujuk) [" + r.id + "] " + isi_r)
    return "\n".join(bagian)


def _serap_keberatan(isi: dict, temuan_fase1: list[Temuan]) -> None:
    """Tempelkan keberatan model ke temuan yang bersangkutan.

    MENEMPEL, TIDAK MENGHAPUS. Temuannya tetap muncul di panel dan di naskah;
    yang bertambah cuma satu baris catatan di komentarnya. Penelaah yang
    memutuskan — ditetapkan 23 Sep 2026.
    """
    daftar = isi.get("keberatan")
    if not isinstance(daftar, list) or not temuan_fase1:
        return
    menurut_nomor = {t.nomor: t for t in temuan_fase1}
    for k in daftar:
        if not isinstance(k, dict):
            continue
        try:
            nomor = int(k.get("nomor"))
        except (TypeError, ValueError):
            continue
        alasan = str(k.get("alasan", "")).strip()
        sasaran = menurut_nomor.get(nomor)
        # Nomor yang tidak ada di daftar yang dikirim berarti model mengarang
        # sasarannya — dilewati, bukan ditebak.
        if sasaran is not None and alasan:
            sasaran.catatan_ai = alasan


def baca_satuan(
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    untuk_dibaca: list[Satuan],
    klien: Klien,
    ongkos: Ongkos,
    per_panggilan: int = 6,
    lapor: Optional[Callable[[int, int, list[BarisPeta]], None]] = None,
    sudah_ada: Optional[list[BarisPeta]] = None,
    temuan_fase1: Optional[list[Temuan]] = None,
) -> list[BarisPeta]:
    """Hasilkan PETA — satu baris ringkasan per satuan yang lolos penyaring.

    `lapor` dipanggil sesudah TIAP kelompok selesai, dengan (selesai, total,
    baris baru). Itu yang membuat panel bisa menunjukkan "82/175" alih-alih
    diam beberapa menit — kediaman persis itu yang membuat kemacetan Law
    Analyzer di 68/175 tidak ketahuan sampai terlambat.

    `sudah_ada` baris peta yang tersimpan dari analisis sebelumnya. Satuan
    yang sudah ada di situ TIDAK dibaca ulang, jadi analisis yang diteruskan
    sesudah backend restart tidak membayar dua kali.
    """
    if not untuk_dibaca:
        return []

    lama = {b.satuan_id: b for b in (sudah_ada or [])}
    sisa = [s for s in untuk_dibaca if s.id not in lama]
    peta: list[BarisPeta] = [lama[s.id] for s in untuk_dibaca if s.id in lama]
    if not sisa:
        return peta

    konteks = susun_konteks_tetap(pohon, daftar)
    total = len(untuk_dibaca)

    for kelompok in kelompokkan(sisa, per_panggilan):
        bahan = susun_bahan(kelompok, pohon, konteks, temuan_fase1)
        jawab = klien.tanya(P.PERAN, P.susun(P.TAHAP2_BACA, bahan))
        ongkos.catat(jawab)

        isi = baca_json(jawab.teks)
        if not isi or not isinstance(isi.get("baris"), list):
            # Jawaban tidak terbaca. Kelompok ini dilewati dan sisanya tetap
            # jalan — satu jawaban rusak tidak boleh menggagalkan seluruh
            # analisis, dan peta yang bolong lebih baik daripada peta karangan.
            ongkos.gagal += 1
            if lapor is not None:
                lapor(len(peta), total, [])
            continue

        _serap_keberatan(isi, temuan_fase1 or [])

        baru: list[BarisPeta] = []
        sah = {s.id for s in kelompok}
        for b in isi["baris"]:
            if not isinstance(b, dict):
                continue
            sid = str(b.get("satuan_id", "")).strip()
            # Model bisa mengarang satuan_id, atau menjawab satuan dari
            # kelompok sebelumnya. Yang tidak ada di kelompok yang BARU SAJA
            # dikirim pasti bukan jawaban atas pertanyaan ini.
            if sid not in sah:
                continue
            asal = pohon.cari(sid)
            baru.append(
                BarisPeta(
                    satuan_id=sid,
                    ringkasan=str(b.get("ringkasan", "")).strip(),
                    memuat_norma=bool(b.get("memuat_norma", False)),
                    istilah_dipakai=[
                        str(x).strip()
                        for x in (b.get("istilah_dipakai") or [])
                        if str(x).strip()
                    ],
                    merujuk=[r.id for r in satuan_dirujuk(asal, pohon)] if asal else [],
                    dugaan=str(b.get("dugaan", "")).strip(),
                )
            )

        peta += baru
        # Dilaporkan SESUDAH baris tersimpan di `peta`, bukan sebelum, supaya
        # angka kemajuan tidak pernah mendahului kenyataan.
        if lapor is not None:
            lapor(len(peta), total, baru)
    return peta
