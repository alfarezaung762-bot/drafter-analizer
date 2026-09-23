"""Tempat pekerjaan dan peta disimpan — di Postgres kalau ada, di memori kalau tidak.

Pemanggil TIDAK PERNAH tahu yang mana yang sedang dipakai. Itu yang membuat
add-in ini bisa dicoba di mesin penelaah tanpa menyiapkan basis data dulu,
sementara di server ia tetap tahan restart.

YANG DISIMPAN KE POSTGRES: pekerjaan dan peta. Peta bagian termahal Fase 2 —
Langkah 2 memanggil model belasan sampai puluhan kali, dan itu yang paling
sayang hilang. Backend yang mati di satuan ke-68 meninggalkan 68 baris peta
yang sudah dibayar, dan analisis ulang meneruskan dari situ.

YANG TINGGAL DI MEMORI: temuan. Temuan lahir di Langkah 5 dari bahan yang
sudah tersimpan, jadi kehilangannya cuma memerlukan penalaran ulang, bukan
pembacaan ulang seluruh naskah. Akibatnya yang perlu diketahui penelaah:
sesudah backend restart, daftar temuan perlu dijalankan lagi — tetapi
tagihannya jauh lebih kecil daripada dari nol.
"""

from __future__ import annotations

import threading
from typing import Optional

from app.db import sesi as db_sesi
from app.models.pekerjaan import BarisPeta, Dugaan, Pekerjaan, StatusPekerjaan
from app.models.temuan import Temuan


class _Memori:
    """Simpanan cadangan. Hidup selama proses hidup, tidak lebih."""

    def __init__(self) -> None:
        self.pekerjaan: dict[int, Pekerjaan] = {}
        self.peta: dict[int, list[BarisPeta]] = {}
        self.urut = 0


_memori = _Memori()
_temuan: dict[int, list[Temuan]] = {}
# Temuan Fase 1 yang dapat keberatan model. Dipisah dari `_temuan` karena
# panel sudah memegang temuan itu — yang perlu dikirim balik cuma catatannya,
# bukan temuannya lagi.
_keberatan: dict[int, list[Temuan]] = {}
# Dugaan Langkah 3. Di memori saja, sekelas temuan: sekali petanya tersimpan,
# menalar ulang cuma satu panggilan — jauh lebih murah daripada membaca ulang
# seluruh naskah. Yang dipakai Ekspor Tahap 3 untuk memperlihatkan apa yang
# KELUAR dari Langkah 3, bukan cuma apa yang masuk.
_dugaan: dict[int, list[Dugaan]] = {}
_kunci = threading.Lock()


def _pisah(teks: str) -> list[str]:
    return [x.strip() for x in teks.split(",") if x.strip()]


# ---------------------------------------------------------------------------
# Pekerjaan
# ---------------------------------------------------------------------------


def buat(dokumen: str, satuan_total: int = 0) -> int:
    """Daftarkan satu analisis baru, kembalikan nomornya."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            _memori.urut += 1
            nomor = _memori.urut
            _memori.pekerjaan[nomor] = Pekerjaan(
                id=nomor,
                dokumen=dokumen,
                status=StatusPekerjaan.BERJALAN,
                satuan_total=satuan_total,
            )
            _memori.peta[nomor] = []
            _temuan[nomor] = []
        return nomor

    from app.db.tabel import PekerjaanDB

    with s:
        baris = PekerjaanDB(
            dokumen=dokumen,
            status=StatusPekerjaan.BERJALAN.value,
            satuan_total=satuan_total,
        )
        s.add(baris)
        s.commit()
        s.refresh(baris)
        nomor = int(baris.id or 0)
    with _kunci:
        _temuan[nomor] = []
    return nomor


def perbarui(
    nomor: int,
    status: Optional[StatusPekerjaan] = None,
    satuan_total: Optional[int] = None,
    satuan_selesai: Optional[int] = None,
    panggilan: Optional[int] = None,
    token_masuk: Optional[int] = None,
    token_keluar: Optional[int] = None,
    pesan: Optional[str] = None,
) -> None:
    """Perbarui kemajuan. Field yang None dibiarkan apa adanya."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            p = _memori.pekerjaan.get(nomor)
            if p is None:
                return
            if status is not None:
                p.status = status
            if satuan_total is not None:
                p.satuan_total = satuan_total
            if satuan_selesai is not None:
                p.satuan_selesai = satuan_selesai
            if panggilan is not None:
                p.panggilan = panggilan
            if token_masuk is not None:
                p.token_masuk = token_masuk
            if token_keluar is not None:
                p.token_keluar = token_keluar
            if pesan is not None:
                p.pesan = pesan
        return

    from datetime import datetime, timezone

    from app.db.tabel import PekerjaanDB

    with s:
        baris = s.get(PekerjaanDB, nomor)
        if baris is None:
            return
        if status is not None:
            baris.status = status.value
        if satuan_total is not None:
            baris.satuan_total = satuan_total
        if satuan_selesai is not None:
            baris.satuan_selesai = satuan_selesai
        if panggilan is not None:
            baris.panggilan = panggilan
        if token_masuk is not None:
            baris.token_masuk = token_masuk
        if token_keluar is not None:
            baris.token_keluar = token_keluar
        if pesan is not None:
            baris.pesan = pesan
        baris.diperbarui = datetime.now(timezone.utc)
        s.add(baris)
        s.commit()


def ambil(nomor: int) -> Optional[Pekerjaan]:
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            return _memori.pekerjaan.get(nomor)

    from app.db.tabel import PekerjaanDB

    with s:
        baris = s.get(PekerjaanDB, nomor)
        if baris is None:
            return None
        return Pekerjaan(
            id=baris.id,
            dokumen=baris.dokumen,
            status=StatusPekerjaan(baris.status),
            satuan_total=baris.satuan_total,
            satuan_selesai=baris.satuan_selesai,
            panggilan=baris.panggilan,
            token_masuk=baris.token_masuk,
            token_keluar=baris.token_keluar,
            pesan=baris.pesan,
        )


# ---------------------------------------------------------------------------
# Peta
# ---------------------------------------------------------------------------


def simpan_peta(nomor: int, baris: list[BarisPeta]) -> None:
    """Simpan baris peta yang sudah selesai. Yang sudah ada TIDAK ditimpa."""
    if not baris:
        return
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            ada = {b.satuan_id for b in _memori.peta.get(nomor, [])}
            _memori.peta.setdefault(nomor, []).extend(
                b for b in baris if b.satuan_id not in ada
            )
        return

    from sqlmodel import select

    from app.db.tabel import HasilSatuanDB

    with s:
        sudah = set(
            s.exec(
                select(HasilSatuanDB.satuan_id).where(HasilSatuanDB.pekerjaan_id == nomor)
            ).all()
        )
        for b in baris:
            if b.satuan_id in sudah:
                continue
            s.add(
                HasilSatuanDB(
                    pekerjaan_id=nomor,
                    satuan_id=b.satuan_id,
                    ringkasan=b.ringkasan,
                    memuat_norma=b.memuat_norma,
                    istilah_dipakai=", ".join(b.istilah_dipakai),
                    merujuk=", ".join(b.merujuk),
                    dugaan=b.dugaan,
                )
            )
        s.commit()


def ambil_peta(nomor: int) -> list[BarisPeta]:
    """Peta yang sudah tersimpan. Inilah yang membuat restart tidak mahal."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            return list(_memori.peta.get(nomor, []))

    from sqlmodel import select

    from app.db.tabel import HasilSatuanDB

    with s:
        baris = s.exec(
            select(HasilSatuanDB)
            .where(HasilSatuanDB.pekerjaan_id == nomor)
            .order_by(HasilSatuanDB.id)
        ).all()
        return [
            BarisPeta(
                satuan_id=b.satuan_id,
                ringkasan=b.ringkasan,
                memuat_norma=b.memuat_norma,
                istilah_dipakai=_pisah(b.istilah_dipakai),
                merujuk=_pisah(b.merujuk),
                dugaan=b.dugaan,
            )
            for b in baris
        ]


# ---------------------------------------------------------------------------
# Temuan — memori saja, dan itu disengaja (lihat docstring berkas)
# ---------------------------------------------------------------------------


def tambah_temuan(nomor: int, temuan: list[Temuan]) -> None:
    with _kunci:
        _temuan.setdefault(nomor, []).extend(temuan)


def ambil_temuan(nomor: int) -> list[Temuan]:
    with _kunci:
        return list(_temuan.get(nomor, []))


def tambah_keberatan(nomor: int, temuan: list[Temuan]) -> None:
    with _kunci:
        _keberatan.setdefault(nomor, []).extend(temuan)


def ambil_keberatan(nomor: int) -> list[Temuan]:
    with _kunci:
        return list(_keberatan.get(nomor, []))


# ---------------------------------------------------------------------------
# Dugaan Langkah 3 — memori saja
# ---------------------------------------------------------------------------


def simpan_dugaan(nomor: int, dugaan: list[Dugaan]) -> None:
    """Catat hasil Langkah 3. Daftar kosong TETAP dicatat, dan itu penting.

    "Langkah 3 tidak menghasilkan dugaan" dan "Langkah 3 belum pernah
    dijalankan" adalah dua keadaan yang berbeda, dan Ekspor Tahap 3 harus bisa
    membedakannya. Karena itu yang dipakai `nomor in _dugaan`, bukan panjang
    daftarnya.
    """
    with _kunci:
        _dugaan[nomor] = list(dugaan)


def ambil_dugaan(nomor: int) -> Optional[list[Dugaan]]:
    """None berarti BELUM PERNAH dicatat; daftar kosong berarti nihil."""
    with _kunci:
        ada = _dugaan.get(nomor)
        return None if ada is None else list(ada)


def pekerjaan_terakhir(dokumen: str) -> Optional[int]:
    """Nomor pekerjaan terbaru untuk sebuah dokumen, atau None.

    Dipakai Ekspor Tahap 3 supaya panel yang baru dimuat ulang — dan karena
    itu lupa nomor pekerjaannya — tetap bisa mengekspor analisis terakhir.
    """
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            cocok = [
                n for n, p in _memori.pekerjaan.items() if p.dokumen == dokumen
            ]
            return max(cocok) if cocok else None

    from sqlmodel import select

    from app.db.tabel import PekerjaanDB

    with s:
        baris = s.exec(
            select(PekerjaanDB.id)
            .where(PekerjaanDB.dokumen == dokumen)
            .order_by(PekerjaanDB.id.desc())  # type: ignore[union-attr]
            .limit(1)
        ).first()
        return baris


def bersihkan_memori() -> None:
    """Hanya untuk tes. Tidak menyentuh basis data."""
    with _kunci:
        _memori.pekerjaan.clear()
        _memori.peta.clear()
        _memori.urut = 0
        _temuan.clear()
        _keberatan.clear()
        _dugaan.clear()
        _temuan.clear()
        _keberatan.clear()
