"""Sambungan ke basis data, dan simpanan cadangan kalau tidak ada.

`DATABASE_URL` dibaca dari core/config.py — BUKAN dari .env langsung.
CLAUDE.md butir 10: kredensial hanya hidup di backend dan berkas .env tidak
pernah dibaca kode di luar config.

BASIS DATANYA BOLEH TIDAK ADA. Kalau `DATABASE_URL` kosong, Fase 2 tetap
berjalan penuh — yang hilang hanya kemampuan bertahan dari restart. Itu
disengaja: seorang penelaah yang mencoba add-in ini di mesinnya sendiri tidak
perlu menyiapkan Postgres dulu, dan seluruh tes berjalan tanpa jaringan.

Neon maupun Postgres internal sama-sama Postgres, jadi pindah dari satu ke
yang lain cuma mengganti satu baris di .env. Tidak ada satu pun kode di sini
yang tahu ia sedang bicara dengan Neon.
"""

from __future__ import annotations

import threading
from typing import Optional

from app.core.config import settings

_mesin = None
_sudah_disiapkan = False
_kunci = threading.Lock()


def _rapikan_url(url: str) -> str:
    """Samakan bentuk URL yang biasa ditempel orang dari papan Neon.

    Neon memberikan `postgresql://...`; SQLAlchemy 2 dengan psycopg 3 menuntut
    `postgresql+psycopg://`. Tanpa penyesuaian ini sambungannya gagal dengan
    pesan yang menyesatkan soal psycopg2 yang memang tidak dipasang.
    """
    url = url.strip()
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def tersedia() -> bool:
    return bool(settings.DATABASE_URL.strip())


def mesin():
    """Mesin SQLAlchemy, dibuat sekali. None kalau DATABASE_URL kosong."""
    global _mesin, _sudah_disiapkan
    if not tersedia():
        return None
    with _kunci:
        if _mesin is None:
            from sqlmodel import SQLModel, create_engine

            from app.db import tabel  # noqa: F401 — mendaftarkan tabel

            _mesin = create_engine(
                _rapikan_url(settings.DATABASE_URL),
                pool_pre_ping=True,  # Neon menidurkan sambungan yang menganggur
                pool_recycle=300,
            )
            if not _sudah_disiapkan:
                SQLModel.metadata.create_all(_mesin)
                _sudah_disiapkan = True
    return _mesin


def sesi():
    """Sesi baru, atau None kalau basis datanya tidak ada.

    Pemanggil WAJIB memeriksa None. Sengaja tidak melempar: ketiadaan basis
    data bukan kesalahan, melainkan keadaan yang sah.
    """
    m = mesin()
    if m is None:
        return None
    from sqlmodel import Session

    return Session(m)


def periksa() -> dict[str, object]:
    """Cek sambungan untuk /cek-env. Tidak menulis apa pun."""
    if not tersedia():
        return {"tersedia": False, "pesan": "DATABASE_URL belum diisi"}
    try:
        from sqlalchemy import text
        from sqlmodel import Session

        m = mesin()
        with Session(m) as s:
            s.exec(text("SELECT 1"))
        return {"tersedia": True, "pesan": "tersambung"}
    except Exception as e:  # noqa: BLE001
        return {"tersedia": False, "pesan": f"{type(e).__name__}: {e}"}
