"""Tes unit untuk aturan pemeriksaan format baku (Fase 1).

Semua tes menguji fungsi murni tanpa server FastAPI.
"""

import pytest

from app.models.temuan import ParagrafInput, TingkatKeparahan
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
        temuan = cek_judul_kapital(doc)
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
        temuan = cek_judul_kapital(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-001"
        assert temuan[0].tingkat_keparahan == TingkatKeparahan.TINGGI
        assert temuan[0].lokasi.paragraf_index == 3
        assert temuan[0].usulan_rumusan == "STANDAR BIAYA MASUKAN TAHUN ANGGARAN 2024"

    def test_kmk_judul_kapital_sah(self):
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 456/KMK.01/2023",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        ])
        temuan = cek_judul_kapital(doc)
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
        temuan = cek_judul_kapital(doc)
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
        temuan = cek_judul_kapital(doc)
        assert len(temuan) == 0

    def test_tanpa_blok_tentang(self):
        doc = _buat_dokumen(["Paragraf pembuka acak tanpa struktur resmi"])
        temuan = cek_judul_kapital(doc)
        assert len(temuan) == 0


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
        temuan = cek_judul_konsisten(doc)
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
        temuan = cek_judul_konsisten(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-002"
        assert temuan[0].tingkat_keparahan == TingkatKeparahan.TINGGI

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
        temuan = cek_judul_konsisten(doc)
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
        temuan = cek_frasa_baku_menimbang(doc)
        assert len(temuan) == 0

    def test_multi_butir_tanpa_frasa_baku(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa dipandang perlu mengatur mengenai hal tersebut;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert temuan[0].tingkat_keparahan == TingkatKeparahan.SEDANG

    def test_satu_butir_tanpa_huruf_sah_dilewati(self):
        # Bentuk sah KMK 527 butir 19: satu butir tanpa penanda huruf
        doc = _buat_dokumen([
            "Menimbang : bahwa untuk memenuhi kebutuhan organisasi, perlu dilakukan evaluasi;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc)
        assert len(temuan) == 0

    def test_multi_butir_menyatu_sah(self):
        # Bentuk menyatu DAN multi-butir (KMK 527 Lampiran II) — varian sah
        doc = _buat_dokumen([
            "Menimbang : a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, perlu menetapkan Peraturan Menteri Keuangan tentang Standar Biaya Masukan;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc)
        assert len(temuan) == 0

    def test_multi_butir_menyatu_tanpa_frasa_baku(self):
        # Bentuk menyatu DAN multi-butir — varian tanpa frasa baku
        doc = _buat_dokumen([
            "Menimbang : a. bahwa untuk melaksanakan ketentuan Pasal 5 ... ;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, dipandang perlu menetapkan pengaturan terkait hal tersebut;",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-004"
        assert temuan[0].tingkat_keparahan == TingkatKeparahan.SEDANG
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
        temuan = cek_frasa_baku_menimbang(doc)
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
        temuan = cek_frasa_baku_menimbang(doc)
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
        temuan = cek_frasa_baku_menimbang(doc)
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
        temuan = cek_frasa_baku_menimbang(doc)
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
        assert temuan[0].tingkat_keparahan == TingkatKeparahan.RENDAH
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
        assert "butir 32" in temuan[0].catatan

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
        temuan = jalankan_semua(doc)
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
        temuan = jalankan_semua(doc)

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
