"""LANGKAH 4 — menguji tiap dugaan pada TEKS UTUH satuannya.

Ini gerbang yang membuat seluruh Fase 2 bisa dipertanggungjawabkan. Langkah 3
menalar di atas ringkasan; ringkasan kehilangan detail; jadi apa pun yang
terlihat di sana masih mungkin salah. Di sini satuannya dibaca utuh, dan
dugaan yang tidak terbukti DIGUGURKAN.

    Dugaan yang gugur adalah hasil yang baik, bukan kegagalan.

Dua jalur, dan bedanya bukan sekadar teknis:

    tunggal    satu satuan dibaca utuh. Dugaan jenis pemikul, makna_ganda,
               operasional, cakupan.
    tabrakan   DUA satuan dibaca utuh DALAM SATU PANGGILAN. Wajib begitu:
               pengecualian yang sah ("kecuali sebagaimana dimaksud dalam
               Pasal 12") menyerupai tabrakan kalau cuma satu sisinya dibaca.
               Model juga harus memilih SATUAN MANA yang menyimpang, karena
               hanya satu yang akan ditandai.

Keluarannya CalonTemuan — masih belum menyentuh naskah. Langkah 5 yang
membuktikan kutipannya benar-benar ada, dan Langkah 5 yang memutuskan.
"""

from __future__ import annotations

from app.bersama import prompt as P
from app.bersama.llm import Klien, Ongkos, baca_jawaban, skor_sah
from app.fase2 import tahap4_tabrakan
from app.models.pekerjaan import CalonTemuan, Dugaan
from app.models.satuan import PohonSatuan

# Jenis dugaan → aturan yang akan tertulis di temuan. Dipisah begini supaya
# penelaah bisa mematikan satu jenis penalaran saja lewat panel Pengaturan,
# tidak harus mematikan seluruh Fase 2.
ATURAN: dict[str, str] = {
    "makna_ganda": "F2-101",
    "pemikul": "F2-102",
    "operasional": "F2-103",
    "tabrakan": "F2-104",
    "cakupan": "F2-105",
}


def pastikan_tunggal(
    dugaan: Dugaan,
    pohon: PohonSatuan,
    konteks: str,
    klien: Klien,
    ongkos: Ongkos,
) -> CalonTemuan | None:
    """Uji satu dugaan pada teks utuh satuannya."""
    satuan = pohon.cari(dugaan.satuan_id)
    if satuan is None:
        return None

    isi_satuan = pohon.teks_lengkap(dugaan.satuan_id) or satuan.teks
    if not isi_satuan.strip():
        # Satuan tanpa teks sendiri (mis. Pasal yang seluruh isinya ayat, tapi
        # ayatnya kosong). Tidak ada yang bisa dikutip, jadi tidak ada yang
        # bisa ditandai.
        return None

    bahan = "\n".join(
        [
            konteks,
            "",
            "== DUGAAN YANG DIUJI ==",
            "Jenis  : " + dugaan.jenis,
            "Alasan : " + dugaan.alasan,
            "",
            "== TEKS UTUH SATUAN ==",
            "[" + satuan.id + "] " + isi_satuan,
        ]
    )

    jawab = klien.tanya(P.PERAN, P.susun(P.TAHAP4_MEMASTIKAN, bahan))
    ongkos.catat(jawab)

    isi = baca_jawaban(jawab.teks, ongkos)
    if isi is None or not isi.get("terbukti"):
        return None

    teks_asli = str(isi.get("teks_asli", "")).strip()
    if not teks_asli:
        # Terbukti tetapi tidak menunjuk letaknya. Tidak bisa ditandai, dan
        # temuan tanpa lokasi tidak berguna bagi penelaah.
        return None

    return CalonTemuan(
        aturan_id=ATURAN.get(dugaan.jenis, "F2-101"),
        satuan_id=dugaan.satuan_id,
        alasan=str(isi.get("alasan", "")).strip(),
        teks_asli=teks_asli,
        saran=str(isi.get("saran", "")).strip(),
        usulan_rumusan=str(isi.get("usulan_rumusan", "")).strip(),
        skor=skor_sah(isi.get("skor")),
        eksternal=dugaan.eksternal,
    )


def memastikan(
    dugaan: list[Dugaan],
    pohon: PohonSatuan,
    konteks: str,
    klien: Klien,
    ongkos: Ongkos,
    aturan_aktif: set[str] | None = None,
) -> list[CalonTemuan]:
    """Jalankan Langkah 4 untuk seluruh dugaan.

    `aturan_aktif` datang dari panel Pengaturan — penelaah yang menentukan
    jenis penalaran mana yang dijalankan.
    """
    hasil: list[CalonTemuan] = []
    for d in dugaan:
        kode = ATURAN.get(d.jenis, "")
        if aturan_aktif is not None and kode not in aturan_aktif:
            continue
        calon = (
            tahap4_tabrakan.pastikan_tabrakan(d, pohon, konteks, klien, ongkos)
            if d.tabrakan
            else pastikan_tunggal(d, pohon, konteks, klien, ongkos)
        )
        if calon is not None:
            hasil.append(calon)
    return hasil
