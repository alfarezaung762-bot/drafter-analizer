"""Tes ekstraksi definisi — Fase 2 Langkah 0, tahap kedua."""

from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.models.temuan import ParagrafInput


def _dok(baris):
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]


_KEPALA = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA", "NOMOR 12 TAHUN 2026",
    "TENTANG", "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA", "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "MEMUTUSKAN:", "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
]


def _daftar(baris_pasal1):
    return ambil_definisi(bangun_pohon(_dok(_KEPALA + baris_pasal1)))


class TestAmbilDefinisi:
    def test_bentuk_baku_berangka(self):
        d = _daftar([
            "Pasal 1",
            "Dalam Peraturan Menteri ini yang dimaksud dengan:",
            "1. Barang Milik Negara adalah semua barang yang dibeli atas beban APBN.",
            "2. Pengelola Barang adalah pejabat yang berwenang menetapkan status.",
            "3. Hari adalah hari kerja.",
        ])
        assert d.gagal is None
        assert d.istilah_saja() == ["Barang Milik Negara", "Pengelola Barang", "Hari"]
        assert d.ada("Hari")
        assert not d.ada("Pengguna Barang")

    def test_arti_ikut_terbaca(self):
        d = _daftar(["Pasal 1", "1. Hari adalah hari kerja."])
        assert d.definisi[0].arti == "hari kerja"
        assert d.definisi[0].satuan_id == "pasal-1-angka-1"

    def test_kalimat_pengantar_bukan_definisi(self):
        d = _daftar([
            "Pasal 1",
            "Dalam Peraturan Menteri ini yang dimaksud dengan:",
            "1. Hari adalah hari kerja.",
        ])
        assert d.istilah_saja() == ["Hari"]

    def test_istilah_kepanjangan_dilewati(self):
        """Hampir pasti pembacaan yang meleset, bukan istilah sungguhan."""
        d = _daftar([
            "Pasal 1",
            "1. Hari adalah hari kerja.",
            "2. Ketentuan lebih lanjut mengenai tata cara penetapan status "
            "penggunaan barang milik negara adalah sebagaimana diatur.",
        ])
        assert d.istilah_saja() == ["Hari"]


class TestMemilihDiam:
    def test_tanpa_pasal_1(self):
        d = _daftar(["Pasal 2", "Isi pasal dua."])
        assert d.gagal is not None
        assert "Pasal 1" in d.gagal

    def test_pasal_1_tanpa_kata_adalah(self):
        d = _daftar(["Pasal 1", "1. Ketentuan umum berlaku bagi seluruh unit."])
        assert d.gagal is not None
        assert d.definisi == []

    def test_pohon_gagal_ikut_diam(self):
        d = ambil_definisi(bangun_pohon(_dok([f"baris {i}" for i in range(40)])))
        assert d.gagal is not None


class TestCariMirip:
    """Pemeriksaan ④ Langkah 5 — salah ketik istilah berdefinisi di usulan."""

    def _d(self):
        return _daftar([
            "Pasal 1",
            "1. Pengelola Barang adalah pejabat yang berwenang.",
            "2. Hari adalah hari kerja.",
        ])

    def test_salah_ketik_tertangkap(self):
        assert "Pengelola Barang" in self._d().cari_mirip(
            "Pengeloa Barang wajib melaporkan setiap perubahan."
        )

    def test_ejaan_benar_tidak_dilaporkan(self):
        assert self._d().cari_mirip(
            "Pengelola Barang wajib melaporkan setiap perubahan."
        ) == []

    def test_kata_lain_yang_jauh_berbeda_tidak_dilaporkan(self):
        assert self._d().cari_mirip("Menteri Keuangan menetapkan besaran.") == []
