"""Tes endpoint /analisis/lanjut — TANPA memanggil model.

Yang diuji di sini kontrak HTTP-nya saja: rutenya terdaftar, pekerjaan yang
tidak ada dijawab 404, dan bentuk jawabannya sesuai. Jalur analisisnya sendiri
sudah diuji tuntas di test_alur_fase2.py dengan KlienPalsu.

Sengaja TIDAK ada tes yang benar-benar memulai pekerjaan: `_jalankan` memanggil
Azure OpenAI sungguhan di utas terpisah, dan tes yang memanggil layanan
berbayar bukan tes lagi.
"""

import pytest
from fastapi.testclient import TestClient

from app.core.config import settings
from app.db import simpanan
from app.main import app

klien = TestClient(app)


@pytest.fixture(autouse=True)
def tanpa_basis_data(monkeypatch):
    """Kosongkan DATABASE_URL untuk SELURUH tes di berkas ini.

    Tanpa ini, GET /analisis/lanjut/{nomor} menyambung ke Postgres sungguhan
    dan tes berubah jadi pemeriksaan jaringan — lambat, dan bergantung pada
    basis data yang seharusnya tidak disentuh tes.
    """
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    simpanan.bersihkan_memori()
    yield
    simpanan.bersihkan_memori()


def test_rute_terdaftar():
    jalan = klien.get("/openapi.json").json()["paths"]
    assert "/analisis/lanjut" in jalan
    assert "/analisis/lanjut/{nomor}" in jalan


def test_pekerjaan_yang_tidak_ada_dijawab_404():
    resp = klien.get("/analisis/lanjut/999999")
    assert resp.status_code == 404


def test_fase_1_tidak_terganggu():
    """Endpoint lama tetap berjalan apa adanya."""
    resp = klien.post(
        "/analisis/jalankan",
        json={
            "jenis_dokumen": "PMK",
            "paragraf": [{"index": 0, "teks": "Pasal 1"}],
        },
    )
    assert resp.status_code == 200
    assert "temuan" in resp.json()
