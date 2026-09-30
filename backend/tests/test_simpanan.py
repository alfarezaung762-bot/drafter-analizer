"""Tes simpanan pekerjaan dan jawaban — JALUR MEMORI SAJA.

`DATABASE_URL` sengaja dikosongkan di tiap tes. Dua alasan, dan keduanya
mengikat:

  1. Tes tidak boleh menyentuh jaringan. Tes yang butuh Neon hidup bukan tes
     lagi, melainkan pemeriksaan sambungan.
  2. Tes tidak boleh menulis ke basis data siapa pun — termasuk basis data
     proyek ini sendiri.

Yang diuji di sini perilaku yang DIJANJIKAN pemanggil: nomor pekerjaan naik,
kemajuan per tahap tersimpan, dan jawaban tahap 3 tidak pernah dibayar dua
kali. Jalur Postgres memakai kode yang sama, tinggal ditukar tempat simpannya.
"""

from app.db import sesi as db_sesi
from app.db import simpanan
from app.models.pekerjaan import StatusPekerjaan


# Fixture `tanpa_basis_data` hidup di tests/conftest.py dan berlaku otomatis
# untuk seluruh suite, termasuk berkas ini.


def test_pekerjaan_baru_dapat_nomor_dan_berstatus_berjalan():
    nomor = simpanan.buat("uji.docx")
    p = simpanan.ambil(nomor)
    assert p is not None
    assert p.status == StatusPekerjaan.BERJALAN


def test_nomor_tidak_pernah_dipakai_ulang():
    assert simpanan.buat("a.docx") != simpanan.buat("b.docx")


def test_kemajuan_per_tahap_tersimpan_dan_terbaca():
    nomor = simpanan.buat("uji.docx")
    simpanan.perbarui(nomor, tahap="3 cari dugaan", selesai=4, total=12, panggilan=4)
    p = simpanan.ambil(nomor)
    assert p.tahap == "3 cari dugaan"
    assert p.kemajuan == "4/12"
    assert p.panggilan == 4


def test_field_yang_tidak_disebut_tidak_ikut_berubah():
    nomor = simpanan.buat("uji.docx")
    simpanan.perbarui(nomor, selesai=5)
    simpanan.perbarui(nomor, panggilan=2)
    p = simpanan.ambil(nomor)
    assert p.selesai == 5
    assert p.panggilan == 2


def test_pekerjaan_yang_tidak_ada_mengembalikan_none():
    assert simpanan.ambil(9999) is None


def test_jawaban_tersimpan_menurut_sidik_pesannya():
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_jawaban(nomor, "sidik-a", '{"hasil": []}')
    assert simpanan.ambil_jawaban(nomor) == {"sidik-a": '{"hasil": []}'}


def test_jawaban_yang_sama_tidak_ditimpa():
    """Jawaban yang sudah dibayar tidak diganti jawaban berikutnya untuk pesan yang sama."""
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_jawaban(nomor, "sidik-a", "pertama")
    simpanan.simpan_jawaban(nomor, "sidik-a", "kedua")
    assert simpanan.ambil_jawaban(nomor)["sidik-a"] == "pertama"


def test_jawaban_pekerjaan_lain_tidak_bercampur():
    a, b = simpanan.buat("a.docx"), simpanan.buat("b.docx")
    simpanan.simpan_jawaban(a, "k1", "milik a")
    simpanan.simpan_jawaban(b, "k2", "milik b")
    assert simpanan.ambil_jawaban(a) == {"k1": "milik a"}
    assert simpanan.ambil_jawaban(b) == {"k2": "milik b"}


def test_rekaman_ekspor_kosong_berbeda_dari_tidak_tercatat():
    """"Tahap 3 tidak mengirim apa pun" dan "belum pernah jalan" dua hal berbeda."""
    nomor = simpanan.buat("uji.docx")
    assert simpanan.ambil_pesan_tahap3(nomor) is None
    simpanan.simpan_pesan_tahap3(nomor, [])
    assert simpanan.ambil_pesan_tahap3(nomor) == []


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
