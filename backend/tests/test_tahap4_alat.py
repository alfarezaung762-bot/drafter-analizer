"""Alat tahap 4 — cari teks, buka tabel, jumlah kolom. Kode biasa, TANPA jaringan.

Salah tandai 27 Sep 2026 lahir dari model yang menyimpulkan sesuatu TIDAK ADA
tanpa pernah mencarinya. Alat ini yang mencarikannya — jadi ia sendiri wajib
tidak pernah melewatkan yang ada.
"""

from app.models.temuan import KerangkaTabel
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import susun_bahan
from app.telaah.tahap4_memastikan.alat import (
    ALAT_CARI,
    buka_tabel,
    cari_teks,
    daftar_alat,
    jalankan_alat,
    jumlah_kolom,
)
from tests.naskah_uji import BATANG, data_barang, naskah


def _bahan(paragraf=None, **kw):
    paragraf = paragraf or naskah()
    return susun_bahan(paragraf, bangun_pohon(paragraf), **kw)


class TestCariTeks:
    def test_tidak_peka_huruf_besar_kecil_dan_spasi(self):
        hasil = cari_teks(_bahan(), "pengguna   BARANG wajib")
        assert hasil.startswith("KETEMU di 1 paragraf")
        assert "[pasal-2]" in hasil

    def test_ikut_mencari_di_lampiran_dan_isi_tabel(self):
        hasil = cari_teks(_bahan(), "Barang 0-4")
        assert hasil.startswith("KETEMU")
        assert "(tabel 0, baris 5)" in hasil

    def test_yang_tidak_ada_dikatakan_tidak_ketemu(self):
        hasil = cari_teks(_bahan(), "Lampiran IX")
        assert hasil.startswith("TIDAK KETEMU")

    def test_tabel_raksasa_disebut_tidak_ikut_diperiksa(self):
        paragraf = naskah(tabel_lampiran=[])
        k = KerangkaTabel(tabel=9, sesudah_paragraf=len(paragraf) - 5, jumlah_baris=5000,
                          jumlah_kolom=2, contoh=[["Desa", "Jumlah"]])
        hasil = cari_teks(_bahan(paragraf, tabel_raksasa=[k]), "desa terpencil")
        assert "tidak ikut diperiksa selain baris contohnya" in hasil


class TestTabel:
    def test_buka_tabel_dengan_nomor_baris(self):
        hasil = buka_tabel(_bahan(), 0, 2, 3)
        assert "Tabel 0, baris 2–3 dari 7" in hasil
        assert "2. | 1. | Barang 0-1 | 1.000 |" in hasil

    def test_tabel_yang_tidak_ada(self):
        assert buka_tabel(_bahan(), 42).startswith("Tabel 42 tidak ada")

    def test_tabel_raksasa_tidak_bisa_dibuka(self):
        paragraf = naskah(tabel_lampiran=[])
        k = KerangkaTabel(tabel=9, sesudah_paragraf=len(paragraf) - 5, jumlah_baris=5000,
                          jumlah_kolom=2, contoh=[["Desa", "Jumlah"]])
        assert "tidak bisa dibuka" in buka_tabel(_bahan(paragraf, tabel_raksasa=[k]), 9)

    def test_jumlah_kolom_membaca_angka_cara_indonesia(self):
        # 1.000 + 2.000 + … + 6.000 = 21.000; baris judul dilewati.
        hasil = jumlah_kolom(_bahan(), 0, 3)
        assert "jumlah 21.000 dari 6 sel berangka" in hasil
        assert "1 sel bukan angka dilewati" in hasil

    def test_kolom_di_luar_tabel(self):
        assert "hanya punya 3 kolom" in jumlah_kolom(_bahan(), 0, 9)


class TestPelaksana:
    def test_alat_tak_dikenal_tidak_melempar(self):
        assert "tidak ada" in jalankan_alat(_bahan(), "hapus_naskah", {})

    def test_argumen_rusak_tidak_melempar(self):
        assert "tidak terbaca" in jalankan_alat(_bahan(), "buka_tabel", {"nomor": "abc"})

    def test_tanpa_tabel_alat_tabel_tidak_ditawarkan(self):
        batang = [b for b in BATANG]
        assert daftar_alat(_bahan(naskah(batang=batang, lampiran=False))) == [ALAT_CARI]
        assert len(daftar_alat(_bahan(naskah(tabel_lampiran=[data_barang(0)])))) == 3
