"""Tes unit untuk aturan pemeriksaan format baku (Fase 1).

Semua tes menguji fungsi murni tanpa server FastAPI.
"""

import pytest

from app.models.temuan import (
    AnalisisRequest,
    JenisDokumen,
    JenisTanda,
    ParagrafInput,
)
from app.rules.format_baku import (
    cek_ejaan,
    cek_frasa_baku_menimbang,
    cek_judul_kapital,
    cek_judul_konsisten,
    cek_kelengkapan_struktur,
    jalankan_semua,
)


def _buat_dokumen(baris_list: list[str]) -> list[ParagrafInput]:
    """Helper untuk membuat daftar ParagrafInput dari list string."""
    return [ParagrafInput(index=i, teks=baris) for i, baris in enumerate(baris_list)]


# ---------------------------------------------------------------------------
# Tes 1: cek_judul_kapital (F1-001)
# ---------------------------------------------------------------------------

class TestCekJudulKapital:
    def test_pmk_judul_kapital_sah(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_pmk_judul_tidak_kapital(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "Standar Biaya Masukan Tahun Anggaran 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-001"
        # Catatan, bukan penggantian — lihat alasannya di cek_judul_kapital().
        assert temuan[0].jenis_tanda == JenisTanda.CATATAN
        assert temuan[0].lokasi.paragraf_index == 3
        # Yang ditandai berhenti di "Anggaran": "2024" sudah sama dengan versi
        # kapitalnya, jadi bukan bagian dari yang salah. Persis itulah maksud
        # penandaan setingkat kata.
        assert temuan[0].lokasi.teks_asli == "Standar Biaya Masukan Tahun Anggaran"
        assert temuan[0].lokasi.offset_mulai == 0
        # usulan_rumusan tetap diisi sebagai bahan tampilan, tetapi TIDAK
        # pernah disisipkan ke naskah — kontraknya mengizinkan itu untuk
        # temuan berjenis catatan.
        assert temuan[0].usulan_rumusan == "STANDAR BIAYA MASUKAN TAHUN ANGGARAN"

    def test_kmk_judul_kapital_sah(self):
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 456/KMK.01/2023",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc, JenisDokumen.KMK)
        assert len(temuan) == 0

    def test_judul_multi_paragraf(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 789/PMK.01/2023",
            "TENTANG",
            "TATA CARA PENATAUSAHAAN PIUTANG NEGARA PADA",
            "KEMENTERIAN KEUANGAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_judul_pencabutan_dengan_kata_tentang_di_dalamnya(self):
        # Kasus nyata: PMK 88/PMK.01/2022 mencabut PMK lain yang punya kata TENTANG di dalamnya
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 88/PMK.01/2022",
            "TENTANG",
            "PENCABUTAN PERATURAN MENTERI KEUANGAN NOMOR 113/PMK.01/2006",
            "TENTANG PEDOMAN PENATAUSAHAAN PERSEDIAAN DI LINGKUNGAN",
            "DEPARTEMEN KEUANGAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_tanpa_blok_tentang(self):
        doc = _buat_dokumen(["Paragraf pembuka acak tanpa struktur resmi"])
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 0


# ---------------------------------------------------------------------------
# Tes 1b: penandaan setingkat kata
# ---------------------------------------------------------------------------
#
# Keluhan penelaah 17 Sep 2026: yang tersorot satu paragraf judul penuh padahal
# yang salah cuma satu kata. Tes di kelas ini mengunci perilaku barunya.

class TestPenandaanSetingkatKata:
    def _judul_pmk(self, judul: str) -> list[ParagrafInput]:
        return _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            judul,
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])

    def test_satu_kata_nyasar_hanya_menandai_kata_itu(self):
        doc = self._judul_pmk("STANDAR Biaya MASUKAN TAHUN ANGGARAN")
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "Biaya"
        assert temuan[0].lokasi.offset_mulai == len("STANDAR ")
        assert temuan[0].lokasi.panjang == len("Biaya")

    def test_dua_kata_terpisah_jadi_dua_temuan(self):
        doc = self._judul_pmk("STANDAR Biaya MASUKAN Tahun ANGGARAN")
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert [t.lokasi.teks_asli for t in temuan] == ["Biaya", "Tahun"]

    def test_kata_beruntun_digabung_jadi_satu_temuan(self):
        # Kalau tiap kata jadi temuan sendiri, judul yang seluruhnya salah
        # menghasilkan belasan komentar untuk satu persoalan yang sama.
        doc = self._judul_pmk("STANDAR Biaya Masukan TAHUN ANGGARAN")
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "Biaya Masukan"

    def test_kata_bertanda_hubung_tidak_terpotong(self):
        doc = self._judul_pmk("PEMBENTUKAN PERATURAN Perundang-Undangan NEGARA")
        temuan = cek_judul_kapital(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "Perundang-Undangan"

    def test_judul_kapital_dengan_angka_dan_garis_miring_tidak_ditandai(self):
        doc = self._judul_pmk(
            "PENCABUTAN PERATURAN MENTERI KEUANGAN NOMOR 113/PMK.01/2006"
        )
        assert cek_judul_kapital(doc, JenisDokumen.PMK) == []

    def test_judul_konsisten_hanya_menandai_kata_yang_beda(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA "
            "KELUARAN TAHUN ANGGARAN 2024.",
        ])
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        # Bukan seluruh paragraf Menetapkan — cuma kata yang berbeda.
        assert temuan[0].lokasi.teks_asli == "KELUARAN"

    def test_kmk_diktum_kesatu_tidak_menelan_klausul_menetapkan(self):
        """Regresi bug RKMK 527, 17 Sep 2026.

        Daftar penghenti lama memuat PERTAMA (penomoran diktum PMK) tetapi tidak
        KESATU (penomoran diktum KMK), sehingga pengambilan judul Menetapkan
        kebablasan menelan diktum KESATU. Judulnya jadi panjang sekali lalu
        dilaporkan berbeda dari judul pembuka — padahal sama persis. Penelaah
        melihat paragraf Menetapkan disorot tanpa ada yang salah di situ.
        """
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR [@NomorND]",
            "TENTANG",
            "PERUBAHAN ATAS KEPUTUSAN MENTERI KEUANGAN NOMOR",
            "527/KMK.01/2022 TENTANG PEDOMAN PEMBENTUKAN PERATURAN DAN",
            "KEPUTUSAN DI LINGKUNGAN KEMENTERIAN KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PERUBAHAN ATAS "
            "KEPUTUSAN MENTERI KEUANGAN NOMOR 527/KMK.01/2022 TENTANG PEDOMAN "
            "PEMBENTUKAN PERATURAN DAN KEPUTUSAN DI LINGKUNGAN KEMENTERIAN "
            "KEUANGAN.",
            "KESATU : Beberapa ketentuan dalam Keputusan Menteri Keuangan "
            "Nomor 527/KMK.01/2022 tentang Pedoman Pembentukan Peraturan dan "
            "Keputusan di Lingkungan Kementerian Keuangan diubah sebagai "
            "berikut:",
            "1. Diktum KELIMA diubah sehingga berbunyi sebagai berikut:",
            "KEDUA : Keputusan Menteri ini mulai berlaku pada tanggal "
            "ditetapkan.",
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.KMK) == []

    def test_judul_menetapkan_kebablasan_memilih_diam(self):
        # Tidak ada penghenti sama sekali sesudah Menetapkan. Daripada melapor
        # judul sepanjang dokumen sebagai "berbeda", aturannya diam.
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 456/KMK.01/2023",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN "
            "PEJABAT PENGELOLA KEUANGAN",
            *[f"Paragraf lanjutan tanpa penanda diktum nomor {i}" for i in range(20)],
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.KMK) == []

    def test_menimbang_kurang_titik_koma_saja_menandai_satu_karakter(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam "
            "huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang "
            "Standar Biaya Masukan",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.panjang == 1
        assert temuan[0].lokasi.teks_asli == "n"  # huruf terakhir "Masukan"


# ---------------------------------------------------------------------------
# Tes 2: cek_judul_konsisten (F1-002)
# ---------------------------------------------------------------------------

class TestCekJudulKonsisten:
    def test_judul_konsisten_sah(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024.",
            "Pasal 1",
        ])
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_judul_tidak_konsisten(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA KELUARAN TAHUN ANGGARAN 2024.",
            "Pasal 1",
        ])
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-002"
        assert temuan[0].jenis_tanda == JenisTanda.CATATAN

    def test_judul_konsisten_sah_walau_ada_paragraf_kosong_sesudahnya(self):
        # Regresi: paragraf kosong sesudah klausul Menetapkan membuat teks
        # gabungan berakhir dengan spasi. Kalau titik akhir dibuang sebelum
        # spasi dirapatkan, judul yang konsisten salah dilaporkan melanggar.
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024.",
            "",
            "BAB I",
            "KETENTUAN UMUM",
            "Pasal 1",
        ])
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 0


# ---------------------------------------------------------------------------
# Tes 3: cek_kelengkapan_struktur (F1-003)
# ---------------------------------------------------------------------------

class TestCekKelengkapanStruktur:
    def test_struktur_lengkap(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang : a. bahwa ...",
            "Mengingat : 1. Undang-Undang ...",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG ...",
        ])
        temuan = cek_kelengkapan_struktur(doc)
        assert len(temuan) == 0

    def test_struktur_kurang_mengingat(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang : a. bahwa ...",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG ...",
        ])
        temuan = cek_kelengkapan_struktur(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-003"
        assert "Mengingat" in temuan[0].catatan

    def test_struktur_kurang_semua(self):
        doc = _buat_dokumen(["Hanya teks acak tanpa struktur."])
        temuan = cek_kelengkapan_struktur(doc)
        assert len(temuan) == 3


# ---------------------------------------------------------------------------
# Tes 4: cek_frasa_baku_menimbang (F1-004)
# ---------------------------------------------------------------------------

class TestCekFrasaBakuMenimbang:
    def test_multi_butir_sah(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_multi_butir_tanpa_frasa_baku(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa dipandang perlu mengatur mengenai hal tersebut;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert temuan[0].jenis_tanda == JenisTanda.CATATAN

    def test_satu_butir_tanpa_huruf_sah_dilewati(self):
        # Bentuk sah KMK 527 butir 19: satu butir tanpa penanda huruf
        doc = _buat_dokumen([
            "Menimbang : bahwa untuk memenuhi kebutuhan organisasi, perlu dilakukan evaluasi;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_multi_butir_menyatu_sah(self):
        # Bentuk menyatu DAN multi-butir (KMK 527 Lampiran II) — varian sah
        doc = _buat_dokumen([
            "Menimbang : a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_multi_butir_menyatu_tanpa_frasa_baku(self):
        # Bentuk menyatu DAN multi-butir — varian tanpa frasa baku
        doc = _buat_dokumen([
            "Menimbang : a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, dipandang perlu menetapkan pengaturan terkait hal tersebut;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert temuan[0].jenis_tanda == JenisTanda.CATATAN
        assert temuan[0].lokasi.paragraf_index == 1

    # -- Bunyi baku butir 22 diperiksa empat bagian, bukan dua substring --

    def test_tanpa_frasa_sebagaimana_dimaksud(self):
        # "berdasarkan hal tersebut" bukan bunyi baku butir 22
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan hal tersebut, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert "sebagaimana dimaksud" in temuan[0].catatan

    def test_kmk_sah_memakai_nama_jenis_kmk(self):
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang :",
            "a. bahwa dalam rangka tertib administrasi ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Keputusan Menteri Keuangan tentang Penetapan Pejabat Pengelola Keuangan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.KMK)
        assert len(temuan) == 0

    def test_kmk_keliru_memakai_nama_jenis_pmk(self):
        # Dokumen KMK tetapi butir terakhir menyebut "Peraturan Menteri Keuangan"
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang :",
            "a. bahwa dalam rangka tertib administrasi ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Penetapan Pejabat Pengelola Keuangan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.KMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert "Keputusan Menteri Keuangan" in temuan[0].catatan

    def test_diakhiri_titik_bukan_titik_koma(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan.",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert "titik koma" in temuan[0].catatan


# ---------------------------------------------------------------------------
# Tes 5: cek_ejaan (F1-005)
# ---------------------------------------------------------------------------

class TestCekEjaan:
    def test_ejaan_undang_undang_salah(self):
        doc = _buat_dokumen([
            "1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-005"
        assert temuan[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert temuan[0].usulan_rumusan == "Undang-Undang"

    def test_ejaan_undang_undang_sah(self):
        doc = _buat_dokumen([
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 0

    def test_ejaan_tentang_kapital_di_mengingat_salah(self):
        # Butir 32: kata "tentang" tetap huruf kecil di dalam judul peraturan pada dasar hukum
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 39 Tahun 2008 Tentang Kementerian Negara;",
            "MEMUTUSKAN:",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-005"
        assert temuan[0].lokasi.teks_asli == "Tentang"
        assert temuan[0].usulan_rumusan == "tentang"
        assert temuan[0].lokasi.paragraf_index == 1
        # Nomor butirnya TIDAK lagi ditanam di teks catatan — sumbernya satu,
        # yaitu tabel rujukan. Yang diperiksa di sini isi catatannya.
        assert "huruf kecil" in temuan[0].catatan
        assert temuan[0].rujukan.sumber.startswith("KMK 527")

    def test_ejaan_tentang_kecil_di_mengingat_sah(self):
        # Butir 32: kata "tentang" sudah huruf kecil
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 39 Tahun 2008 tentang Kementerian Negara;",
            "MEMUTUSKAN:",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 0

    def test_tentang_kapital_di_luar_mengingat_tidak_ditandai_butir_32(self):
        # Blok pembuka sah memiliki TENTANG kapital, tidak boleh ditandai ejaan butir 32
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 0


# ---------------------------------------------------------------------------
# Tes 6: jalankan_semua & Dokumen Panjang
# ---------------------------------------------------------------------------

class TestJalankanSemua:
    def test_dokumen_lengkap_dan_benar(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 123/PMK.01/2023",
            "TENTANG",
            "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan Tahun Anggaran 2024;",
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024.",
            "Pasal 1",
        ])
        temuan = jalankan_semua(doc, JenisDokumen.PMK)
        assert len(temuan) == 0

    def test_dokumen_panjang_175_paragraf(self):
        # Membangun dokumen 180 paragraf (minimal 175 paragraf sesuai ukuran PMK 124/2024)
        baris_list = [
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",        # 0
            "NOMOR 124/PMK.01/2024",                                 # 1
            "TENTANG",                                               # 2
            "STANDAR BIAYA KELUARAN TAHUN ANGGARAN 2025",            # 3
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",                     # 4
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",                  # 5
            "Menimbang : a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;", # 6
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Keluaran Tahun Anggaran 2025;", # 7
            "Mengingat :",                                           # 8
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;", # 9
            # Pelanggaran 1 di indeks 10: "Tentang" dengan T kapital pada Mengingat
            "2. Undang-Undang Nomor 39 Tahun 2008 Tentang Kementerian Negara;", # 10
            "MEMUTUSKAN:",                                           # 11
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA KELUARAN TAHUN ANGGARAN 2025.", # 12
        ]

        # Isi pasal-pasal dari indeks 13 hingga 179 (total 180 paragraf)
        for i in range(13, 180):
            if i == 95:
                # Pelanggaran 2 di tengah dokumen (indeks 95): "Undang-undang" huruf u kecil
                baris_list.append(
                    "Ketentuan lebih lanjut mengenai tata cara diatur dalam Undang-undang Perbendaharaan Negara."
                )
            elif i == 175:
                # Pelanggaran 3 di akhir dokumen (indeks 175): jenis peraturan ejaan salah
                baris_list.append(
                    "Peraturan ini tunduk pada peraturan pemerintah pengganti undang-undang yang berlaku."
                )
            elif i % 2 == 1:
                pasal_no = (i - 13) // 2 + 1
                baris_list.append(f"Pasal {pasal_no}")
            else:
                baris_list.append(
                    "Standar biaya keluaran sebagaimana dimaksud pada ayat ini dialokasikan sesuai ketentuan perundang-undangan."
                )

        assert len(baris_list) == 180
        doc = _buat_dokumen(baris_list)
        temuan = jalankan_semua(doc, JenisDokumen.PMK)

        # Pastikan tepat 3 pelanggaran yang kita sisipkan terdeteksi
        assert len(temuan) == 3

        # Pelanggaran 1: Mengingat Butir 32 di indeks 10
        t1 = next(t for t in temuan if t.lokasi.paragraf_index == 10)
        assert t1.aturan_id == "F1-005"
        assert t1.lokasi.teks_asli == "Tentang"
        assert t1.usulan_rumusan == "tentang"

        # Pelanggaran 2: Ejaan Undang-undang di indeks 95
        t2 = next(t for t in temuan if t.lokasi.paragraf_index == 95)
        assert t2.aturan_id == "F1-005"
        assert t2.lokasi.teks_asli == "Undang-undang"
        assert t2.usulan_rumusan == "Undang-Undang"

        # Pelanggaran 3: Ejaan di indeks 175
        t3 = next(t for t in temuan if t.lokasi.paragraf_index == 175)
        assert t3.aturan_id == "F1-005"
        assert t3.usulan_rumusan == "Peraturan Pemerintah Pengganti Undang-Undang"


# ---------------------------------------------------------------------------
# Tes penomoran temuan dan kontrak request
# ---------------------------------------------------------------------------

class TestPenomoranTemuan:
    def _dokumen_bermasalah(self):
        # Sengaja memuat beberapa pelanggaran di posisi yang berbeda-beda
        return _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 00 TAHUN 2026",
            "TENTANG",
            "Tata Cara Uji Coba",                      # F1-001, paragraf 3
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa sesuatu;",
            "b. bahwa berdasarkan hal tersebut, perlu menetapkan aturan.",
            "Mengingat :",
            "1. Undang-undang Nomor 39 Tahun 2008;",   # F1-005, paragraf 10
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA UJI COBA.",
        ])

    def test_nomor_urut_mengikuti_posisi_dokumen(self):
        temuan = jalankan_semua(self._dokumen_bermasalah(), JenisDokumen.PMK)
        assert len(temuan) >= 2

        # Nomor berurutan 1..N tanpa bolong
        assert [t.nomor for t in temuan] == list(range(1, len(temuan) + 1))

        # Urutannya mengikuti posisi di dokumen, bukan urutan aturan dijalankan
        posisi = [(t.lokasi.paragraf_index, t.lokasi.offset_mulai) for t in temuan]
        assert posisi == sorted(posisi)

    def test_tiap_temuan_punya_jenis_tanda_yang_sah(self):
        temuan = jalankan_semua(self._dokumen_bermasalah(), JenisDokumen.PMK)
        for t in temuan:
            assert t.jenis_tanda in (JenisTanda.PENGGANTIAN, JenisTanda.CATATAN)
            # Kontrak: penggantian WAJIB membawa rumusan pengganti harfiah
            if t.jenis_tanda == JenisTanda.PENGGANTIAN:
                assert t.usulan_rumusan, f"{t.aturan_id} penggantian tanpa usulan"

    def test_jenis_dokumen_wajib_di_request(self):
        import pydantic

        with pytest.raises(pydantic.ValidationError):
            AnalisisRequest(paragraf=[])

    def test_jenis_dokumen_mengubah_tuntutan_frasa_menimbang(self):
        # Butir terakhir menyebut "Keputusan Menteri Keuangan".
        # Sah bila dokumennya KMK, keliru bila dokumennya PMK.
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa sesuatu;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam "
            "huruf a, perlu menetapkan Keputusan Menteri Keuangan tentang "
            "Sesuatu;",
            "Mengingat :",
        ])
        assert cek_frasa_baku_menimbang(doc, JenisDokumen.KMK) == []

        temuan_pmk = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan_pmk) == 1
        assert "Peraturan Menteri Keuangan" in temuan_pmk[0].catatan


class TestJudulBergayaAllCaps:
    """Judul yang tampil kapital lewat atribut All Caps bukan pelanggaran.

    Ditemukan pada RKMK sungguhan 17 Sep 2026: naskahnya diketik huruf campur
    lalu ditampilkan kapital lewat gaya, sehingga aturan menandainya dan
    mengusulkan .upper() yang di layar tidak mengubah apa pun.
    """

    def _dokumen(self, tampil_kapital: bool):
        baris = [
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 456/KMK.01/2023",
            "TENTANG",
            "Perubahan Atas Keputusan Menteri Keuangan Nomor 527",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ]
        return [
            ParagrafInput(
                index=i,
                teks=b,
                # Hanya baris judulnya yang bergaya All Caps
                tampil_kapital=(i == 3 and tampil_kapital),
            )
            for i, b in enumerate(baris)
        ]

    def test_huruf_campur_tanpa_gaya_ditandai(self):
        temuan = cek_judul_kapital(self._dokumen(False), JenisDokumen.KMK)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-001"

    def test_huruf_campur_dengan_gaya_all_caps_dilewati(self):
        temuan = cek_judul_kapital(self._dokumen(True), JenisDokumen.KMK)
        assert temuan == []

    def test_default_tanpa_field_tetap_menandai(self):
        # Paragraf lama yang tidak membawa tampil_kapital harus berperilaku
        # seperti sebelumnya — default False, bukan melewatkan pemeriksaan.
        p = ParagrafInput(index=0, teks="apa pun")
        assert p.tampil_kapital is False
