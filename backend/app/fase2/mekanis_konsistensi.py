"""F2-001 … F2-007 — pemeriksaan mekanis, DI LUAR jalur AI.

Namanya sengaja bukan `tahap*`: aturan di sini melompat langsung dari Langkah 1
ke Langkah 5, tanpa pernah menyentuh model. Gratis, hasilnya pasti, dan kalau
salah bisa ditunjukkan barisnya.

Fungsi murni seperti Fase 1: masuk pohon satuan, keluar daftar Temuan. Bisa
dites tanpa server, tanpa model, tanpa kredensial.

KAIDAH YANG DIWARISI, TANPA KELONGGARAN:
  Apa pun yang ditandai wajib benar-benar salah. Aturan yang tidak bisa
  membuktikan kesalahannya MEMILIH DIAM, bukan diperhalus.
"""

from __future__ import annotations

import re
import uuid
from typing import Optional

from app.fase2.tahap0_definisi import DaftarDefinisi
from app.models.satuan import JenisSatuan, PohonSatuan, Satuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)
from app.rules.rujukan_kmk527 import ambil_rujukan


def _buat_temuan(
    aturan_id: str,
    satuan: Satuan,
    paragraf: list[ParagrafInput],
    teks_asli: str,
    catatan: str,
    usulan: Optional[str] = None,
) -> Optional[Temuan]:
    """Bentuk Temuan dari sebuah satuan, atau None kalau tidak bisa ditandai.

    Mengembalikan None bila `teks_asli` tidak ditemukan persis di rentang
    paragraf satuan itu. Temuan yang rentangnya tidak ketemu TIDAK DITANDAI
    SAMA SEKALI — bukan diperlebar ke satu paragraf. CLAUDE.md butir 6.
    """
    if not satuan.bisa_ditandai:
        return None

    for p in paragraf:
        if not (satuan.paragraf_mulai <= p.index < satuan.paragraf_akhir):
            continue
        posisi = p.teks.find(teks_asli)
        if posisi == -1:
            continue
        return Temuan(
            id=f"f-{uuid.uuid4().hex[:8]}",
            aturan_id=aturan_id,
            fase=2,
            jenis_tanda=JenisTanda.CATATAN,
            # skor sengaja dibiarkan kosong: aturan mekanis tidak menebak,
            # jadi tidak ada keyakinan yang perlu diangkakan.
            satuan_id=satuan.id,
            lokasi=LokasiTemuan(
                paragraf_index=p.index,
                offset_mulai=posisi,
                panjang=len(teks_asli),
                teks_asli=teks_asli,
            ),
            catatan=catatan,
            usulan_rumusan=usulan,
            rujukan=RujukanTemuan(**ambil_rujukan(aturan_id)),
            status=StatusTemuan.BELUM_DITINJAU,
        )
    return None


# ===========================================================================
# F2-001 — rujukan antar-pasal menunjuk satuan yang tidak ada
# ===========================================================================
#
# Sengaja DIPERSEMPIT ke bentuk baku rujukan internal: "sebagaimana dimaksud
# dalam/pada Pasal N". Dua sebab:
#
#   1. "Pasal 12" bisa menunjuk peraturan LAIN — "Pasal 12 Undang-Undang
#      Nomor 1 Tahun 2004". Menandainya berarti menuduh naskah memakai rujukan
#      menggantung padahal rujukannya ke dokumen lain dan sah.
#   2. Bentuk baku itu yang dipakai KMK 527 untuk rujukan di dalam dokumen,
#      jadi mempersempit ke situ tidak kehilangan banyak.

_RUJUKAN_INTERNAL = re.compile(
    r"sebagaimana\s+dimaksud\s+(?:dalam|pada)\s+"
    r"Pasal\s+(\d+[A-Z]?)"
    r"(?:\s+ayat\s+\((\d+)\))?",
    re.IGNORECASE,
)

# Kalau sesudah nomor pasal menyusul nama peraturan, itu rujukan ke dokumen
# lain — bukan urusan F2-001.
_MENUNJUK_PERATURAN_LAIN = re.compile(
    r"^\s*(Undang-Undang|Peraturan|Keputusan|UU)\b", re.IGNORECASE
)


def cek_rujukan_menggantung(
    pohon: PohonSatuan, paragraf: list[ParagrafInput]
) -> list[Temuan]:
    """F2-001 — rujukan internal menunjuk satuan yang tidak ada."""
    if pohon.gagal is not None:
        return []

    hasil: list[Temuan] = []
    for s in pohon.satuan:
        if s.jenis in (JenisSatuan.MENIMBANG, JenisSatuan.MENGINGAT):
            continue  # rujukan di pembukaan menunjuk peraturan lain
        for m in _RUJUKAN_INTERNAL.finditer(s.teks):
            if _MENUNJUK_PERATURAN_LAIN.match(s.teks[m.end() :]):
                continue

            nomor_pasal = m.group(1)
            nomor_ayat = m.group(2)
            target = f"pasal-{nomor_pasal.lower()}"
            sebutan = f"Pasal {nomor_pasal}"
            if nomor_ayat:
                target = f"{target}-ayat-{nomor_ayat}"
                sebutan = f"{sebutan} ayat ({nomor_ayat})"

            if pohon.ada(target):
                continue

            temuan = _buat_temuan(
                aturan_id="F2-001",
                satuan=s,
                paragraf=paragraf,
                teks_asli=m.group(0),
                catatan=(
                    f"Merujuk {sebutan}, tetapi {sebutan} tidak ada di naskah ini. "
                    "Saran: periksa nomor rujukannya, atau pastikan bagian yang "
                    "dirujuk memang sudah tertulis."
                ),
            )
            if temuan:
                hasil.append(temuan)
    return hasil


# ===========================================================================
# F2-003 — definisi di Pasal 1 tidak pernah dipakai
# ===========================================================================


def cek_definisi_tak_terpakai(
    pohon: PohonSatuan, daftar: DaftarDefinisi, paragraf: list[ParagrafInput]
) -> list[Temuan]:
    """F2-003 — istilah yang didefinisikan tetapi tidak pernah muncul lagi."""
    if pohon.gagal is not None or daftar.gagal is not None:
        return []

    # Pencarian SENGAJA tidak peduli huruf besar-kecil. Naskah kerap menulis
    # istilahnya dengan huruf kecil di batang tubuh, dan melaporkannya sebagai
    # "tidak pernah dipakai" adalah salah tandai.
    batang = " ".join(
        s.teks.lower()
        for s in pohon.satuan
        if not s.id.startswith("pasal-1")
        and s.jenis not in (JenisSatuan.MENIMBANG, JenisSatuan.MENGINGAT)
    )

    hasil: list[Temuan] = []
    for d in daftar.definisi:
        if d.istilah.lower() in batang:
            continue
        satuan = pohon.cari(d.satuan_id)
        if satuan is None:
            continue
        temuan = _buat_temuan(
            aturan_id="F2-003",
            satuan=satuan,
            paragraf=paragraf,
            teks_asli=d.istilah,
            catatan=(
                f"Istilah \"{d.istilah}\" didefinisikan di Pasal 1 tetapi tidak "
                "pernah dipakai di batang tubuh. Saran: hapus definisinya kalau "
                "memang tidak diperlukan, atau periksa apakah ada ketentuan yang "
                "terlewat ditulis."
            ),
        )
        if temuan:
            hasil.append(temuan)
    return hasil


# ===========================================================================
# F2-004 — penomoran melompat atau berulang
# ===========================================================================


def cek_penomoran(pohon: PohonSatuan, paragraf: list[ParagrafInput]) -> list[Temuan]:
    """F2-004 — Pasal atau ayat yang nomornya melompat atau berulang."""
    if pohon.gagal is not None:
        return []

    hasil: list[Temuan] = []

    # Pasal sisipan berhuruf (12A) sah dan sengaja dilewati dari pemeriksaan
    # urutan — ia memang menyisip di antara dua nomor.
    pasal = [s for s in pohon.semua(JenisSatuan.PASAL) if s.nomor.isdigit()]
    hasil += _periksa_deret(pasal, "Pasal", paragraf)

    for p in pohon.semua(JenisSatuan.PASAL):
        ayat = [a for a in pohon.anak_dari(p.id) if a.jenis == JenisSatuan.AYAT]
        hasil += _periksa_deret(ayat, f"Ayat pada Pasal {p.nomor}", paragraf)

    return hasil


def _periksa_deret(
    satuan: list[Satuan], sebutan: str, paragraf: list[ParagrafInput]
) -> list[Temuan]:
    hasil: list[Temuan] = []
    terlihat: set[int] = set()
    sebelum: Optional[int] = None

    for s in satuan:
        angka = re.sub(r"\D", "", s.nomor)
        if not angka:
            continue
        n = int(angka)

        if n in terlihat:
            t = _buat_temuan(
                "F2-004", s, paragraf, s.nomor.strip("()") if s.nomor else str(n),
                catatan=(
                    f"{sebutan} nomor {n} muncul lebih dari sekali. "
                    "Saran: nomori ulang berurutan."
                ),
            )
            if t:
                hasil.append(t)
        elif sebelum is not None and n > sebelum + 1:
            hilang = ", ".join(str(x) for x in range(sebelum + 1, n))
            t = _buat_temuan(
                "F2-004", s, paragraf, s.nomor.strip("()") if s.nomor else str(n),
                catatan=(
                    f"{sebutan} melompat dari {sebelum} ke {n} — nomor {hilang} "
                    "tidak ada. Saran: periksa apakah ada bagian yang terlewat, "
                    "atau nomori ulang berurutan."
                ),
            )
            if t:
                hasil.append(t)

        terlihat.add(n)
        sebelum = n
    return hasil


# ===========================================================================
# F2-007 — bilangan: angka tidak cocok dengan hurufnya
# ===========================================================================
#
# "30 (tiga belas) hari" — kedua kata ejaannya benar sempurna, jadi pemeriksa
# ejaan Word tidak akan menangkapnya. Mata manusia juga mudah melewatkannya,
# karena yang dibaca biasanya angkanya. Justru itu pekerjaan yang pantas
# diserahkan ke alat.

_BILANGAN = re.compile(r"\b(\d[\d.]*)\s*\(([^()]{2,60})\)")

_SATUAN_KATA = {
    "nol": 0, "kosong": 0, "satu": 1, "dua": 2, "tiga": 3, "empat": 4,
    "lima": 5, "enam": 6, "tujuh": 7, "delapan": 8, "sembilan": 9,
}
_TUNGGAL = {"sepuluh": 10, "sebelas": 11, "seratus": 100, "seribu": 1000}


def _kata_jadi_angka(kata: str) -> Optional[int]:
    """Ubah bilangan berhuruf jadi angka. None kalau ada kata tak dikenal.

    Mengembalikan None — bukan menebak — begitu bertemu kata di luar daftar.
    Tidak bisa membuktikan berarti tidak menuduh.
    """
    hasil = 0
    kumpul = 0
    ada_isi = False

    for t in re.split(r"[\s-]+", kata.strip().lower()):
        if not t:
            continue
        ada_isi = True
        if t in _SATUAN_KATA:
            kumpul = _SATUAN_KATA[t]
        elif t in _TUNGGAL:
            hasil += _TUNGGAL[t]
            kumpul = 0
        elif t == "belas":
            hasil += 10 + kumpul
            kumpul = 0
        elif t == "puluh":
            hasil += kumpul * 10
            kumpul = 0
        elif t == "ratus":
            hasil += (kumpul or 1) * 100
            kumpul = 0
        elif t == "ribu":
            hasil = (hasil + (kumpul or 1)) * 1000
            kumpul = 0
        else:
            return None

    return hasil + kumpul if ada_isi else None


def cek_bilangan(pohon: PohonSatuan, paragraf: list[ParagrafInput]) -> list[Temuan]:
    """F2-007 — angka Arab tidak cocok dengan bilangan berhurufnya."""
    if pohon.gagal is not None:
        return []

    hasil: list[Temuan] = []
    for s in pohon.satuan:
        for m in _BILANGAN.finditer(s.teks):
            angka_teks, kata = m.group(1), m.group(2)
            try:
                angka = int(angka_teks.replace(".", ""))
            except ValueError:
                continue

            nilai = _kata_jadi_angka(kata)
            if nilai is None or nilai == angka:
                continue  # tak terbaca → diam; cocok → tidak ada temuan

            temuan = _buat_temuan(
                aturan_id="F2-007",
                satuan=s,
                paragraf=paragraf,
                teks_asli=m.group(0),
                catatan=(
                    f"Angka {angka} tidak cocok dengan hurufnya — \"{kata}\" "
                    f"berarti {nilai}. Saran: samakan keduanya; mana yang benar "
                    "ditentukan penelaah."
                ),
                usulan=f"{nilai} ({kata})",
            )
            if temuan:
                hasil.append(temuan)
    return hasil


# ===========================================================================
# Pemanggil
# ===========================================================================


def jalankan_mekanis(
    pohon: PohonSatuan,
    daftar: DaftarDefinisi,
    paragraf: list[ParagrafInput],
    aturan_aktif: Optional[list[str]] = None,
) -> list[Temuan]:
    """Jalankan seluruh aturan mekanis Fase 2, lalu urutkan menurut posisi.

    `aturan_aktif` datang dari panel Pengaturan — penelaah yang menentukan apa
    yang dianalisis. None berarti semua yang aktif secara bawaan.

    Penomoran temuan SENGAJA tidak dilakukan di sini. Nomor Fase 2 melanjutkan
    dari nomor terakhir Fase 1 dan tidak pernah diurutkan ulang — itu tugas
    pemanggil yang tahu berapa temuan Fase 1 sudah ada.
    """
    dipakai = None if aturan_aktif is None else {a.strip().upper() for a in aturan_aktif}

    def aktif(a: str) -> bool:
        return dipakai is None or a in dipakai

    hasil: list[Temuan] = []
    if aktif("F2-001"):
        hasil += cek_rujukan_menggantung(pohon, paragraf)
    if aktif("F2-003"):
        hasil += cek_definisi_tak_terpakai(pohon, daftar, paragraf)
    if aktif("F2-004"):
        hasil += cek_penomoran(pohon, paragraf)
    if aktif("F2-007"):
        hasil += cek_bilangan(pohon, paragraf)

    hasil.sort(key=lambda t: (t.lokasi.paragraf_index, t.lokasi.offset_mulai))
    return hasil
