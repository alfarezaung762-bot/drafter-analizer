"""LANGKAH 3 — menalar di atas PETA, bukan di atas teks penuh.

Satu panggilan untuk seluruh dokumen. Yang dikirim hanya baris-baris peta,
sehingga dokumen 175 satuan pun muat dalam satu jendela konteks.

KENAPA PETA, BUKAN TEKS PENUH. Dua alasan, dan keduanya menentukan:

  1. Kejanggalan yang dicari di sini HANYA terlihat kalau dokumen dipandang
     sebagai satu kesatuan — Pasal 7 yang meniadakan Pasal 23, tujuan di
     Menimbang yang tidak ada ketentuannya. Itu mustahil terlihat kalau
     pasalnya dibaca satu per satu.
  2. Teks penuh 175 satuan tidak muat, dan kalaupun muat, model kehilangan
     ketelitian pada konteks sepanjang itu.

HARGANYA: peta kehilangan detail. Karena itu keluaran langkah ini DUGAAN, dan
tidak satu pun boleh menyentuh naskah sebelum diuji ulang pada teks utuhnya di
Langkah 4. Aturan ini keras dan tidak punya pengecualian.
"""

from __future__ import annotations

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, baca_json
from app.models.pekerjaan import BarisPeta, Dugaan
from app.models.satuan import PohonSatuan

_JENIS_SAH = {"tabrakan", "pemikul", "makna_ganda", "operasional", "cakupan"}

# Batas kewajaran. Dugaan sebanyak ini dari satu dokumen sudah menandakan
# model sedang mencari-cari, bukan menemukan. Yang kelebihan dipotong menurut
# urutan jawaban model, bukan diacak.
_BATAS_DUGAAN = 80


def susun_bahan(peta: list[BarisPeta], konteks: str) -> str:
    """Rangkai bahan satu panggilan Langkah 3."""
    bagian = [konteks, "", "== PETA SELURUH RANCANGAN =="]
    bagian += [b.baris() for b in peta]
    return "\n".join(bagian)


def menalar(
    peta: list[BarisPeta],
    pohon: PohonSatuan,
    konteks: str,
    klien: Klien,
    ongkos: Ongkos,
) -> list[Dugaan]:
    """Peta masuk, dugaan keluar. Belum ada satu pun temuan di sini."""
    if not peta:
        return []

    bahan = susun_bahan(peta, konteks)
    jawab = klien.tanya(P.PERAN, P.susun(P.TAHAP3_MENALAR, bahan))
    ongkos.catat(jawab)

    isi = baca_json(jawab.teks)
    if not isi or not isinstance(isi.get("dugaan"), list):
        ongkos.gagal += 1
        return []

    # Satuan yang boleh disebut: yang ada di peta yang baru saja dikirim.
    # Satuan di luar itu tidak pernah dibaca model, jadi dugaan atasnya
    # tidak bertumpu pada apa pun.
    sah = {b.satuan_id for b in peta}

    hasil: list[Dugaan] = []
    for d in isi["dugaan"]:
        if not isinstance(d, dict):
            continue
        sid = str(d.get("satuan_id", "")).strip()
        if sid not in sah:
            continue

        lain = str(d.get("satuan_lain", "")).strip()
        if lain and (lain not in sah or lain == sid):
            # Tabrakan dengan satuan yang tidak pernah dibaca, atau dengan
            # dirinya sendiri. Dugaannya digugurkan seluruhnya, bukan
            # diturunkan jadi dugaan tunggal: yang diklaim model memang
            # hubungan antar-dua satuan, dan satu sisinya tidak ada.
            continue

        jenis = str(d.get("jenis", "")).strip().lower()
        if jenis not in _JENIS_SAH:
            continue

        alasan = str(d.get("alasan", "")).strip()
        if not alasan:
            continue

        hasil.append(
            Dugaan(
                satuan_id=sid,
                satuan_lain=lain,
                jenis=jenis,
                alasan=alasan,
                eksternal=bool(d.get("eksternal", False)),
            )
        )

    if len(hasil) > _BATAS_DUGAAN:
        hasil = hasil[:_BATAS_DUGAAN]
    return hasil
