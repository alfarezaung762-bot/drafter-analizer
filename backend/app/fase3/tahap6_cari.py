"""LANGKAH 6a — mencari pembanding di korpus peraturan.

Dijalankan HANYA untuk dugaan yang ditandai `eksternal`: dugaan yang
pembuktiannya menuntut dokumen di luar rancangan ini. Dugaan internal tidak
pernah sampai ke sini, dan itu yang menahan biaya Fase 3 tetap kecil.

URUTANNYA: teks utuh dibaca DULU di Langkah 4, korpus dicari SESUDAHNYA.
Tiga alasan, dan ketiganya sudah diputuskan di rancangan bagian 3:

  1. Dugaan yang gugur di Langkah 4 tidak perlu dicarikan pembanding sama
     sekali — pencarian korpus adalah bagian termahal Fase 3.
  2. Kata pencariannya jauh lebih baik sesudah ketentuannya dibaca utuh
     daripada dari ringkasan peta.
  3. Teks korpus berasal dari pemindaian yang OCR-nya rusak. Memasukkannya
     lebih awal berarti seluruh penalaran sesudahnya bertumpu pada teks
     yang mungkin salah baca.
"""

from __future__ import annotations

from app.bersama.llm import Perapal
from app.bersama.opensearch import HasilCari, Korpus
from app.models.pekerjaan import CalonTemuan
from app.models.satuan import PohonSatuan

# Panjang teks yang dijadikan kata pencarian. Seluruh pasal terlalu panjang
# untuk satu vektor yang tajam; potongan awalnya memuat rumusan normanya.
_PANJANG_KUERI = 1200


def susun_kueri(calon: CalonTemuan, pohon: PohonSatuan) -> str:
    """Teks yang dicarikan pembandingnya.

    Kutipan yang dipermasalahkan ditaruh di depan supaya paling menentukan,
    lalu disusul ketentuan utuhnya sebagai konteks.
    """
    isi = pohon.teks_lengkap(calon.satuan_id)
    kueri = (calon.teks_asli + " " + isi).strip()
    return kueri[:_PANJANG_KUERI]


def cari_pembanding(
    calon: CalonTemuan,
    pohon: PohonSatuan,
    korpus: Korpus,
    perapal: Perapal,
    jumlah: int = 5,
) -> HasilCari:
    """Cari peraturan lain yang mungkin bersinggungan dengan ketentuan ini."""
    kueri = susun_kueri(calon, pohon)
    if not kueri:
        return HasilCari(gagal="Tidak ada teks yang bisa dijadikan kata pencarian.")

    try:
        vektor = perapal.rapalkan(kueri)
    except Exception as e:  # noqa: BLE001
        # Embedding gagal bukan alasan menghentikan Fase 3 — pencarian teks
        # biasa masih mungkin, dan hasilnya tetap diverifikasi Langkah 5.
        vektor = []
        hasil = korpus.cari(kueri, vektor, jumlah)
        if hasil.gagal is None and not hasil.pembanding:
            hasil.gagal = f"embedding gagal ({type(e).__name__}), pencarian teks tidak menemukan apa pun"
        return hasil

    return korpus.cari(kueri, vektor, jumlah)
