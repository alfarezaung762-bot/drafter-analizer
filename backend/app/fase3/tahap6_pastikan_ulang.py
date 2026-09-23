"""LANGKAH 6b — memastikan ulang dengan pembanding di tangan.

Yang masuk ke sini sudah lolos Langkah 4: ketentuannya sudah dibaca utuh dan
dugaannya sudah terbukti dari dokumen itu sendiri. Yang ditambahkan di sini
cuma satu hal — apakah ketentuan itu berpotensi bertentangan dengan peraturan
LAIN yang masih berlaku.

TIGA PAGAR, dan semuanya sudah pernah jadi masalah nyata di Law Analyzer:

  1. Model hanya boleh menyebut peraturan yang ADA DI DAFTAR PEMBANDING.
     Prompt melarangnya, dan Langkah 5 membuktikannya dengan mencocokkan
     nama yang disebut ke daftar yang dikirim. Larangan tanpa pembuktian
     tidak berarti apa-apa untuk keluaran model.
  2. Bahasanya wajib "berpotensi bertentangan", bukan "bertentangan".
     Menyatakan pertentangan sebagai kesimpulan bukan wewenang alat ini.
  3. Kutipan pembandingnya berasal dari pemindaian. Statusnya tidak pernah
     "visual", jadi panel selalu menyalakan penanda "belum diverifikasi".

Tanpa pembanding yang lolos penyaring status, langkah ini TIDAK memanggil
model sama sekali. Tidak ada pembanding berarti tidak ada yang bisa
dipertentangkan — dan bertanya tanpa bahan cuma mengundang karangan.
"""

from __future__ import annotations

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, baca_json, skor_sah
from app.bersama.opensearch import HasilCari
from app.models.pekerjaan import CalonTemuan
from app.models.satuan import PohonSatuan

_WAJIB_BERPOTENSI = "berpotensi bertentangan"


def susun_bahan(calon: CalonTemuan, pohon: PohonSatuan, hasil: HasilCari) -> str:
    isi = pohon.teks_lengkap(calon.satuan_id)
    bagian = [
        "== KETENTUAN YANG DIPERIKSA ==",
        "[" + calon.satuan_id + "] " + isi,
        "",
        "Dugaan dari langkah sebelumnya: " + calon.alasan,
        "",
        "== DAFTAR PEMBANDING (hanya ini yang boleh kamu sebut) ==",
    ]
    bagian += [p.baris() for p in hasil.pembanding]
    return "\n".join(bagian)


def pastikan_ulang(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    hasil: HasilCari,
    klien: Klien,
    ongkos: Ongkos,
) -> CalonTemuan | None:
    """Naikkan calon internal jadi calon Fase 3, atau gugurkan."""
    if not hasil.pembanding:
        return None

    jawab = klien.tanya(
        P.PERAN, P.susun(P.TAHAP6_PASTIKAN_ULANG, susun_bahan(calon, pohon, hasil))
    )
    ongkos.catat(jawab)

    isi = baca_json(jawab.teks)
    if not isi:
        ongkos.gagal += 1
        return None
    if not isi.get("terbukti"):
        return None

    alasan = str(isi.get("alasan", "")).strip()
    teks_asli = str(isi.get("teks_asli", "")).strip()
    peraturan = str(isi.get("peraturan", "")).strip()
    if not alasan or not teks_asli or not peraturan:
        return None

    # Pagar 1, ditegakkan di tempat daftarnya masih ada. Prompt sudah
    # melarang menyebut peraturan di luar daftar, tetapi larangan kepada
    # model tanpa pembuktian tidak berarti apa-apa.
    sah = hasil.nama_sah
    if peraturan not in sah:
        # Model kadang menyalin nama berikut judulnya. Diterima kalau
        # sebutan resminya memang ada di dalamnya; selain itu gugur.
        cocok = [n for n in sah if n and n in peraturan]
        if len(cocok) != 1:
            return None
        peraturan = cocok[0]

    # Pagar 2, ditegakkan kode. Prompt sudah memintanya, tetapi permintaan
    # kepada model bukan jaminan — dan temuan yang menyatakan "bertentangan"
    # begitu saja melampaui wewenang alat ini.
    if _WAJIB_BERPOTENSI not in alasan.lower():
        return None

    return CalonTemuan(
        aturan_id="F3-001",
        satuan_id=calon.satuan_id,
        alasan=alasan,
        teks_asli=teks_asli,
        saran=str(isi.get("saran", "")).strip(),
        skor=skor_sah(isi.get("skor")),
        eksternal=True,
        pembanding=peraturan,
        pembanding_sah=sorted(sah),
    )
