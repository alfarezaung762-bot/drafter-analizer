"""Tempat pekerjaan dan jawaban disimpan — di Postgres kalau ada, di memori kalau tidak.

Pemanggil TIDAK PERNAH tahu yang mana yang sedang dipakai. Itu yang membuat
add-in ini bisa dicoba di mesin penelaah tanpa menyiapkan basis data dulu,
sementara di server ia tetap tahan restart.

YANG DISIMPAN KE POSTGRES: pekerjaan, dan jawaban tiap panggilan tahap 3 —
bagian yang dibayar per token dan paling sayang hilang. Analisis yang
dilanjutkan sesudah backend restart tidak membayar ulang pesan yang sama.

YANG TINGGAL DI MEMORI: temuan, keberatan, tahap yang sedang berjalan, dan
percakapan untuk Ekspor Tahap 3–5. Temuan lahir di tahap 5 dari jawaban yang
tersimpan, jadi kehilangannya cuma memerlukan pemastian ulang, bukan
pembacaan ulang seluruh naskah.
"""

from __future__ import annotations

import threading
from typing import Optional

from app.bersama.llm import Blok
from app.db import sesi as db_sesi
from app.models.pekerjaan import Pekerjaan, StatusPekerjaan
from app.models.temuan import Temuan

Rekaman = list[tuple[str, list[Blok]]]


class _Memori:
    """Simpanan cadangan. Hidup selama proses hidup, tidak lebih."""

    def __init__(self) -> None:
        self.pekerjaan: dict[int, Pekerjaan] = {}
        self.jawaban: dict[int, dict[str, str]] = {}
        self.urut = 0


_memori = _Memori()
_temuan: dict[int, list[Temuan]] = {}
# Temuan Fase 1 yang dapat keberatan model. Dipisah dari `_temuan` karena
# panel sudah memegang temuan itu — yang perlu dikirim balik cuma catatannya.
_keberatan: dict[int, list[Temuan]] = {}
# Tahap yang sedang berjalan ("3 cari dugaan"). Di memori saja: kolomnya tidak
# ada di tabel pekerjaan, dan menambah kolom menuntut migrasi.
_tahap: dict[int, str] = {}
# Percakapan tahap 3 dan 4, apa adanya, dan teks Ekspor Tahap 5. Ekspor
# menuliskannya tanpa menyusun ulang: naskah di Word sudah berubah sesudah
# ditandai, jadi menyusunnya ulang dari naskah sekarang bisa berbeda dari
# yang dulu benar-benar dikirim.
_pesan_tahap3: dict[int, Rekaman] = {}
_pesan_tahap4: dict[int, Rekaman] = {}
_ekspor_tahap5: dict[int, str] = {}
_kunci = threading.Lock()


# ---------------------------------------------------------------------------
# Pekerjaan
# ---------------------------------------------------------------------------


def buat(dokumen: str) -> int:
    """Daftarkan satu analisis baru, kembalikan nomornya."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            _memori.urut += 1
            nomor = _memori.urut
            _memori.pekerjaan[nomor] = Pekerjaan(
                id=nomor, dokumen=dokumen, status=StatusPekerjaan.BERJALAN
            )
            _memori.jawaban[nomor] = {}
            _temuan[nomor] = []
        return nomor

    from app.db.tabel import PekerjaanDB

    with s:
        baris = PekerjaanDB(dokumen=dokumen, status=StatusPekerjaan.BERJALAN.value)
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
    tahap: Optional[str] = None,
    selesai: Optional[int] = None,
    total: Optional[int] = None,
    panggilan: Optional[int] = None,
    token_masuk: Optional[int] = None,
    token_keluar: Optional[int] = None,
    pesan: Optional[str] = None,
) -> None:
    """Perbarui kemajuan. Field yang None dibiarkan apa adanya."""
    if tahap is not None:
        with _kunci:
            _tahap[nomor] = tahap

    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            p = _memori.pekerjaan.get(nomor)
            if p is None:
                return
            if status is not None:
                p.status = status
            if tahap is not None:
                p.tahap = tahap
            if selesai is not None:
                p.selesai = selesai
            if total is not None:
                p.total = total
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
        if total is not None:
            baris.satuan_total = total
        if selesai is not None:
            baris.satuan_selesai = selesai
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
            p = _memori.pekerjaan.get(nomor)
            return p.model_copy() if p is not None else None

    from app.db.tabel import PekerjaanDB

    with s:
        baris = s.get(PekerjaanDB, nomor)
        if baris is None:
            return None
        with _kunci:
            tahap = _tahap.get(nomor, "")
        return Pekerjaan(
            id=baris.id,
            dokumen=baris.dokumen,
            status=StatusPekerjaan(baris.status),
            tahap=tahap,
            selesai=baris.satuan_selesai,
            total=baris.satuan_total,
            panggilan=baris.panggilan,
            token_masuk=baris.token_masuk,
            token_keluar=baris.token_keluar,
            pesan=baris.pesan,
        )


# ---------------------------------------------------------------------------
# Jawaban tahap 3 — yang membuat restart tidak mahal
# ---------------------------------------------------------------------------


def simpan_jawaban(nomor: int, kunci: str, jawaban: str) -> None:
    """Simpan jawaban satu panggilan. Yang sudah ada TIDAK ditimpa."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            _memori.jawaban.setdefault(nomor, {}).setdefault(kunci, jawaban)
        return

    from sqlmodel import select

    from app.db.tabel import HasilPanggilanDB

    with s:
        ada = s.exec(
            select(HasilPanggilanDB.id).where(
                HasilPanggilanDB.pekerjaan_id == nomor, HasilPanggilanDB.kunci == kunci
            )
        ).first()
        if ada is None:
            s.add(HasilPanggilanDB(pekerjaan_id=nomor, kunci=kunci, jawaban=jawaban))
            s.commit()


def ambil_jawaban(nomor: int) -> dict[str, str]:
    """Jawaban yang sudah tersimpan untuk satu pekerjaan, menurut sidik pesannya."""
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            return dict(_memori.jawaban.get(nomor, {}))

    from sqlmodel import select

    from app.db.tabel import HasilPanggilanDB

    with s:
        baris = s.exec(
            select(HasilPanggilanDB).where(HasilPanggilanDB.pekerjaan_id == nomor)
        ).all()
        return {b.kunci: b.jawaban for b in baris}


# ---------------------------------------------------------------------------
# Temuan dan keberatan — memori saja, dan itu disengaja (lihat docstring)
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
# Bahan ekspor tahap 3–5 — memori saja
# ---------------------------------------------------------------------------


def simpan_pesan_tahap3(nomor: int, rekaman: Rekaman) -> None:
    """Daftar kosong TETAP dicatat: tahap 3 berjalan tanpa mengirim apa pun."""
    with _kunci:
        _pesan_tahap3[nomor] = list(rekaman)


def ambil_pesan_tahap3(nomor: int) -> Optional[Rekaman]:
    """None kalau tidak tercatat — tahap 3 tidak jalan, atau backend restart."""
    with _kunci:
        ada = _pesan_tahap3.get(nomor)
        return None if ada is None else list(ada)


def simpan_pesan_tahap4(nomor: int, rekaman: Rekaman) -> None:
    """Daftar kosong TETAP dicatat: tahap 4 berjalan tanpa dugaan untuk diuji."""
    with _kunci:
        _pesan_tahap4[nomor] = list(rekaman)


def ambil_pesan_tahap4(nomor: int) -> Optional[Rekaman]:
    with _kunci:
        ada = _pesan_tahap4.get(nomor)
        return None if ada is None else list(ada)


def simpan_ekspor_tahap5(nomor: int, teks: str) -> None:
    with _kunci:
        _ekspor_tahap5[nomor] = teks


def ambil_ekspor_tahap5(nomor: int) -> Optional[str]:
    with _kunci:
        return _ekspor_tahap5.get(nomor)


def pekerjaan_terakhir(dokumen: str) -> Optional[int]:
    """Nomor pekerjaan terbaru untuk sebuah dokumen, atau None.

    Dipakai Ekspor Tahap 3–5 supaya panel yang baru dimuat ulang — dan karena
    itu lupa nomor pekerjaannya — tetap bisa mengekspor analisis terakhir.
    """
    s = db_sesi.sesi()
    if s is None:
        with _kunci:
            cocok = [n for n, p in _memori.pekerjaan.items() if p.dokumen == dokumen]
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
        _memori.jawaban.clear()
        _memori.urut = 0
        _temuan.clear()
        _keberatan.clear()
        _tahap.clear()
        _pesan_tahap3.clear()
        _pesan_tahap4.clear()
        _ekspor_tahap5.clear()
