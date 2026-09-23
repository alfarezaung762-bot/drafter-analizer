"""LANGKAH 4, CABANG TABRAKAN — dua satuan dibaca UTUH dalam SATU panggilan.

Dipisah dari `tahap4_memastikan.py` bukan demi kerapian, melainkan karena
bentuk panggilannya memang berbeda: yang dikirim dua teks utuh sekaligus, dan
yang diminta bukan cuma "terbukti atau tidak" melainkan juga SATUAN MANA yang
menyimpang.

Kenapa keduanya wajib dibaca bersama: pengecualian yang sah — "kecuali
sebagaimana dimaksud dalam Pasal 12" — menyerupai tabrakan kalau cuma satu
sisinya yang dibaca. Menandai pengecualian yang sah sebagai pertentangan
adalah salah tandai, dan satu salah tandai merusak kepercayaan penelaah lebih
cepat daripada sepuluh temuan benar membangunnya.

Hanya SATU satuan yang ditandai, yaitu yang menyimpang. Menandai keduanya
berarti mengatakan dua-duanya salah, padahal yang salah hubungan di antara
keduanya.
"""

from __future__ import annotations

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, baca_jawaban, skor_sah
from app.models.pekerjaan import CalonTemuan, Dugaan
from app.models.satuan import PohonSatuan


def pastikan_tabrakan(
    dugaan: Dugaan,
    pohon: PohonSatuan,
    konteks: str,
    klien: Klien,
    ongkos: Ongkos,
) -> CalonTemuan | None:
    """Uji dugaan tabrakan. KEDUA satuan dibaca utuh dalam satu panggilan."""
    satu = pohon.cari(dugaan.satuan_id)
    dua = pohon.cari(dugaan.satuan_lain)
    if satu is None or dua is None:
        return None

    isi_satu = pohon.teks_lengkap(satu.id) or satu.teks
    isi_dua = pohon.teks_lengkap(dua.id) or dua.teks
    if not isi_satu.strip() or not isi_dua.strip():
        return None

    bahan = "\n".join(
        [
            konteks,
            "",
            "== DUGAAN TABRAKAN ==",
            "Alasan : " + dugaan.alasan,
            "",
            "== TEKS UTUH KEDUA SATUAN ==",
            "[" + satu.id + "] " + isi_satu,
            "",
            "[" + dua.id + "] " + isi_dua,
        ]
    )

    jawab = klien.tanya(P.PERAN, P.susun(P.TAHAP4_TABRAKAN, bahan))
    ongkos.catat(jawab)

    isi = baca_jawaban(jawab.teks, ongkos)
    if isi is None or not isi.get("terbukti"):
        return None

    ditandai = str(isi.get("satuan_ditandai", "")).strip()
    if ditandai not in (satu.id, dua.id):
        # Model menunjuk satuan di luar dua yang dikirimkan. Prompt sudah
        # menyuruh memilih yang lebih belakang bila ragu; jawaban di luar
        # pilihan berarti jawabannya tidak nyambung dengan pertanyaannya.
        return None

    teks_asli = str(isi.get("teks_asli", "")).strip()
    if not teks_asli:
        return None

    lain = dua.id if ditandai == satu.id else satu.id
    return CalonTemuan(
        aturan_id="F2-104",
        satuan_id=ditandai,
        satuan_lain=lain,
        alasan=str(isi.get("alasan", "")).strip(),
        teks_asli=teks_asli,
        saran=str(isi.get("saran", "")).strip(),
        sasaran=str(isi.get("sasaran", "")).strip(),
        skor=skor_sah(isi.get("skor")),
        eksternal=dugaan.eksternal,
    )
