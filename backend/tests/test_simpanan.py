"""Tes simpanan pekerjaan dan peta — JALUR MEMORI SAJA.

`DATABASE_URL` sengaja dikosongkan di tiap tes. Dua alasan, dan keduanya
mengikat:

  1. Tes tidak boleh menyentuh jaringan. Tes yang butuh Neon hidup bukan tes
     lagi, melainkan pemeriksaan sambungan.
  2. Tes tidak boleh menulis ke basis data siapa pun — termasuk basis data
     proyek ini sendiri.

Yang diuji di sini perilaku yang DIJANJIKAN pemanggil: nomor pekerjaan naik,
kemajuan tersimpan, dan peta tidak pernah dibayar dua kali. Jalur Postgres
memakai kode yang sama persis, tinggal ditukar tempat simpannya.
"""

import pytest

from app.core.config import settings
from app.db import sesi as db_sesi
from app.db import simpanan
from app.models.pekerjaan import BarisPeta, StatusPekerjaan


@pytest.fixture(autouse=True)
def tanpa_basis_data(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    simpanan.bersihkan_memori()
    yield
    simpanan.bersihkan_memori()


def test_pekerjaan_baru_dapat_nomor_dan_berstatus_berjalan():
    nomor = simpanan.buat("uji.docx", satuan_total=12)
    p = simpanan.ambil(nomor)
    assert p is not None
    assert p.status == StatusPekerjaan.BERJALAN
    assert p.satuan_total == 12


def test_nomor_tidak_pernah_dipakai_ulang():
    assert simpanan.buat("a.docx") != simpanan.buat("b.docx")


def test_kemajuan_tersimpan_dan_terbaca():
    nomor = simpanan.buat("uji.docx")
    simpanan.perbarui(nomor, satuan_total=175, satuan_selesai=68, panggilan=30)
    p = simpanan.ambil(nomor)
    assert p.kemajuan == "68/175"
    assert p.panggilan == 30


def test_field_yang_tidak_disebut_tidak_ikut_berubah():
    nomor = simpanan.buat("uji.docx")
    simpanan.perbarui(nomor, satuan_selesai=5)
    simpanan.perbarui(nomor, panggilan=2)
    p = simpanan.ambil(nomor)
    assert p.satuan_selesai == 5
    assert p.panggilan == 2


def test_pekerjaan_yang_tidak_ada_mengembalikan_none():
    assert simpanan.ambil(9999) is None


def test_peta_tersimpan_utuh():
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_peta(
        nomor,
        [
            BarisPeta(
                satuan_id="pasal-2",
                ringkasan="kewajiban",
                memuat_norma=True,
                istilah_dipakai=["Pengguna Barang"],
                merujuk=["pasal-1"],
            )
        ],
    )
    peta = simpanan.ambil_peta(nomor)
    assert len(peta) == 1
    assert peta[0].istilah_dipakai == ["Pengguna Barang"]
    assert peta[0].merujuk == ["pasal-1"]


def test_satuan_yang_sama_tidak_disimpan_dua_kali():
    """Inilah yang membuat analisis yang diteruskan tidak dibayar dua kali."""
    nomor = simpanan.buat("uji.docx")
    baris = BarisPeta(satuan_id="pasal-2", ringkasan="pertama")
    simpanan.simpan_peta(nomor, [baris])
    simpanan.simpan_peta(nomor, [BarisPeta(satuan_id="pasal-2", ringkasan="kedua")])
    peta = simpanan.ambil_peta(nomor)
    assert len(peta) == 1
    assert peta[0].ringkasan == "pertama"


def test_peta_pekerjaan_lain_tidak_bercampur():
    a, b = simpanan.buat("a.docx"), simpanan.buat("b.docx")
    simpanan.simpan_peta(a, [BarisPeta(satuan_id="pasal-1")])
    simpanan.simpan_peta(b, [BarisPeta(satuan_id="pasal-9")])
    assert [x.satuan_id for x in simpanan.ambil_peta(a)] == ["pasal-1"]
    assert [x.satuan_id for x in simpanan.ambil_peta(b)] == ["pasal-9"]


def test_tanpa_database_url_simpanan_tetap_jalan():
    assert not db_sesi.tersedia()
    nomor = simpanan.buat("uji.docx")
    assert simpanan.ambil(nomor) is not None


class TestRapikanUrl:
    def test_postgres_pendek_dinaikkan_ke_psycopg(self):
        assert db_sesi._rapikan_url("postgres://a:b@c/d").startswith("postgresql+psycopg://")

    def test_postgresql_dinaikkan_ke_psycopg(self):
        assert db_sesi._rapikan_url("postgresql://a:b@c/d").startswith("postgresql+psycopg://")

    def test_yang_sudah_benar_tidak_diubah_dua_kali(self):
        url = "postgresql+psycopg://a:b@c/d"
        assert db_sesi._rapikan_url(url) == url
