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
    _cek_label_bagian,
    cek_butir_menimbang,
    cek_ejaan,
    cek_judul_menetapkan,
    cek_judul_tanpa_tanda_baca,
    cek_penomoran_dasar_hukum,
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

    def test_diktum_gabungan_ikut_menghentikan(self):
        # KMK 527 sendiri punya diktum sampai KEDUAPULUHLIMA. Pola lama
        # (`KEDUA\b`) tidak cocok dengan penomoran gabungan karena ada
        # lanjutannya. Kata berawalan KE- yang bukan angka harus tetap lolos.
        from app.rules.format_baku import _PENGHENTI_MENETAPKAN as P

        for diktum in [
            "KESATU", "KESEPULUH", "KESEBELAS", "KEDUABELAS",
            "KEEMPATBELAS", "KESEMBILANBELAS", "KEDUAPULUH",
            "KEDUAPULUHSATU", "KEDUAPULUHLIMA", "BAB I", "Pasal 1",
        ]:
            assert P.match(diktum), f"{diktum} seharusnya menghentikan"

        for bukan in [
            "KEUANGAN", "KEPUTUSAN MENTERI KEUANGAN TENTANG PEDOMAN",
            "KEMENTERIAN KEUANGAN", "Ketentuan lebih lanjut",
            "Kepala Biro Hukum", "Rancangan peraturan",
        ]:
            assert not P.match(bukan), f"{bukan} seharusnya TIDAK menghentikan"

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

    def test_kata_menetapkan_di_batang_tubuh_bukan_klausul_menetapkan(self):
        """Regresi bug RPMK DBH Sawit, 18 Sep 2026.

        Pencarian lama memakai re.search tanpa jangkar, jadi "menetapkan:" di
        tengah kalimat Pasal 4 dikira klausul Menetapkan. Isi Pasal 4 lalu
        dituduh "judulnya berbeda dari judul pembuka" — padahal bukan judul.
        """
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            "PENGELOLAAN DANA BAGI HASIL PERKEBUNAN SAWIT",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG PENGELOLAAN DANA "
            "BAGI HASIL PERKEBUNAN SAWIT.",
            "BAB I",
            "Pasal 4",
            "(1) Dalam rangka pengelolaan DBH Sawit, Menteri selaku PA BUN "
            "Pengelola TKD menetapkan:",
            "a. Direktur Jenderal Perimbangan Keuangan sebagai Pemimpin PPA "
            "BUN Pengelola TKD;",
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.PMK) == []

    def test_klausul_menetapkan_bertabel_tetap_terbaca(self):
        # Naskah yang menaruh klausul Menetapkan di dalam tabel: label dan
        # isinya jatuh di paragraf yang berbeda, sehingga paragraf labelnya
        # cuma berbunyi "Menetapkan" tanpa titik dua.
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan",
            ": PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA KELUARAN.",
            "Pasal 1",
        ])
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "KELUARAN"

    def test_tanpa_memutuskan_aturan_judul_konsisten_diam(self):
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Pasal 1",
            "Menetapkan : sesuatu yang bukan judul.",
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.PMK) == []

    def test_menimbang_tidak_mendarat_di_baris_kosong(self):
        """Regresi bug PMK 119, 18 Sep 2026.

        Lokasi temuan dulu diambil dari paragraf_akhir - 1 begitu saja, yaitu
        paragraf tepat sebelum "Mengingat" — yang pada naskah nyata sering baris
        kosong. Hasilnya kartu hampa di panel: tanpa cuplikan, tanpa warna,
        tanpa komentar, tapi bertombol Terima/Tolak.
        """
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3;",
            "b. bahwa berdasarkan hal tersebut di atas, perlu menetapkan "
            "aturan mengenai uji coba penelaahan;",
            "",
            "",
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        # Mendarat di paragraf butirnya (indeks 2), bukan di baris kosong.
        assert temuan[0].lokasi.paragraf_index == 2
        assert temuan[0].lokasi.teks_asli.strip() != ""

    def test_temuan_tanpa_teks_dibuang_jalankan_semua(self):
        # Jaring pengaman lapis terakhir: tidak boleh ada temuan berteks kosong
        # yang lolos ke panel, kecuali F1-003 yang memang tidak punya lokasi.
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3;",
            "b. bahwa berdasarkan hal tersebut, perlu menetapkan aturan;",
            "",
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA "
            "MASUKAN.",
            "Pasal 1",
        ])
        for t in jalankan_semua(doc, JenisDokumen.PMK):
            if t.aturan_id != "F1-003":
                assert t.lokasi.teks_asli.strip() != "", (
                    f"{t.aturan_id} lolos dengan teks_asli kosong"
                )

    def test_butir_panjang_dipotong_agar_bisa_dicari_di_word(self):
        """Regresi bug PMK 5 Tahun 2025, 18 Sep 2026.

        Butir Menimbang di naskah nyata bisa 400-500 karakter. Word.search()
        dibatasi sekitar 255 karakter, jadi temuan sepanjang itu tidak pernah
        ketemu dan tidak pernah tertandai — penelaah melihat kartu di panel
        tanpa ada apa pun di dokumen.
        """
        butir_panjang = (
            "b. bahwa berdasarkan pertimbangan huruf a serta untuk "
            "melaksanakan ketentuan Pasal 3 ayat (10) dan Pasal 27 ayat (5) "
            "Peraturan Presiden Nomor 112 Tahun 2022 tentang Percepatan "
            "Pengembangan Energi Terbarukan untuk Penyediaan Tenaga Listrik, "
            "perlu menetapkan Peraturan Menteri Keuangan tentang Tata Cara "
            "Pemberian dan Pelaksanaan Penjaminan Pemerintah serta "
            "Penanggungan Risiko dalam rangka Percepatan Pengembangan Energi "
            "Terbarukan untuk Penyediaan Tenaga Listrik;"
        )
        assert len(butir_panjang) > 400, "contohnya harus benar-benar panjang"

        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa berdasarkan ketentuan Pasal 23 ayat (3);",
            butir_panjang,
            "Mengingat :",
        ])
        temuan = cek_frasa_baku_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.panjang <= 120
        # Dipotong di batas kata, bukan di tengah kata.
        assert not temuan[0].lokasi.teks_asli.endswith(" ")
        # Dan tetap dimulai di tempat penyimpangannya: naskah menulis
        # "berdasarkan pertimbangan huruf a", bunyi bakunya "berdasarkan
        # pertimbangan sebagaimana dimaksud dalam huruf a".
        assert temuan[0].lokasi.teks_asli.startswith(
            "bahwa berdasarkan pertimbangan huruf a"
        )

    def test_aturan_aktif_menyaring_pemeriksaan(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3;",
            "b. bahwa berdasarkan hal tersebut, perlu menetapkan aturan;",
            "Mengingat :",
            "1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
        ])
        semua = {t.aturan_id for t in jalankan_semua(doc, JenisDokumen.PMK)}
        assert "F1-004" in semua and "F1-005" in semua

        hanya_ejaan = jalankan_semua(doc, JenisDokumen.PMK, ["F1-005"])
        assert {t.aturan_id for t in hanya_ejaan} == {"F1-005"}

        assert jalankan_semua(doc, JenisDokumen.PMK, []) == []

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
            "Mengingat :",
            "1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-005"
        assert temuan[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert temuan[0].usulan_rumusan == "Undang-Undang"

    def test_ejaan_undang_undang_sah(self):
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
        ])
        temuan = cek_ejaan(doc)
        assert len(temuan) == 0

    def test_ejaan_hanya_berlaku_di_dasar_hukum(self):
        """Regresi PMK Lampiran, 18 Sep 2026.

        Butir 32 dan 33 dua-duanya berbicara tentang DASAR HUKUM, bukan
        seluruh dokumen. Sebelum dipersempit, aturan ini menandai rujukan
        generik di dalam Lampiran — "…atau undang-undang yang mengatur
        mengenai pencegahan…" — yang sama sekali bukan dasar hukum.
        """
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
            "Pasal 1",
            "Angka 14 : diisi dengan pasal yang disangkakan dalam "
            "Undang-Undang Ketentuan Umum dan Tata Cara Perpajakan atau "
            "undang-undang yang mengatur mengenai pencegahan dan "
            "pemberantasan tindak pidana pencucian uang.",
        ])
        assert cek_ejaan(doc) == []

    def test_ejaan_tanpa_mengingat_tidak_memeriksa_apa_pun(self):
        doc = _buat_dokumen([
            "1. Undang-undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
        ])
        assert cek_ejaan(doc) == []

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
            # Pelanggaran 2 di indeks 11: "Undang-undang" huruf u kecil, juga
            # pada Mengingat — sejak 18 Sep 2026 aturan ejaan HANYA berlaku di
            # dasar hukum (butir 32 dan 33).
            "3. Undang-undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;", # 11
            "MEMUTUSKAN:",                                           # 12
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA KELUARAN TAHUN ANGGARAN 2025.", # 12
        ]

        # Isi pasal-pasal dari indeks 14 hingga 179 (total 180 paragraf).
        #
        # Dua baris berejaan salah sengaja ditaruh di BATANG TUBUH, dan
        # sengaja TIDAK boleh terdeteksi: butir 32 dan 33 hanya berlaku pada
        # dasar hukum. Sebelum dipersempit, keduanya ikut ditandai — dan pada
        # PMK sungguhan hal itu menandai rujukan generik di dalam Lampiran.
        for i in range(14, 180):
            if i == 95:
                baris_list.append(
                    "Ketentuan lebih lanjut mengenai tata cara diatur dalam Undang-undang Perbendaharaan Negara."
                )
            elif i == 175:
                baris_list.append(
                    "Peraturan ini tunduk pada peraturan pemerintah pengganti undang-undang yang berlaku."
                )
            elif i % 2 == 1:
                pasal_no = (i - 14) // 2 + 1
                baris_list.append(f"Pasal {pasal_no}")
            else:
                baris_list.append(
                    "Standar biaya keluaran sebagaimana dimaksud pada ayat ini dialokasikan sesuai ketentuan perundang-undangan."
                )

        assert len(baris_list) == 180
        doc = _buat_dokumen(baris_list)
        temuan = jalankan_semua(doc, JenisDokumen.PMK)

        # Dua pelanggaran pada Mengingat terdeteksi; dua yang di batang tubuh
        # sengaja tidak — lihat komentar di atas.
        assert len(temuan) == 2
        assert [t.lokasi.teks_asli for t in temuan] == ["Tentang", "Undang-undang"]
        assert all(t.lokasi.paragraf_index in (10, 11) for t in temuan)

        # Pelanggaran 1: Mengingat Butir 32 di indeks 10
        t1 = next(t for t in temuan if t.lokasi.paragraf_index == 10)
        assert t1.aturan_id == "F1-005"
        assert t1.lokasi.teks_asli == "Tentang"
        assert t1.usulan_rumusan == "tentang"

        # Pelanggaran 2: Ejaan Undang-undang di indeks 11, masih di Mengingat
        t2 = next(t for t in temuan if t.lokasi.paragraf_index == 11)
        assert t2.aturan_id == "F1-005"
        assert t2.lokasi.teks_asli == "Undang-undang"
        assert t2.usulan_rumusan == "Undang-Undang"

        # Dua baris berejaan salah di batang tubuh (indeks 95 dan 175) sengaja
        # TIDAK terdeteksi — butir 32 dan 33 hanya berlaku pada dasar hukum.
        assert not any(t.lokasi.paragraf_index in (95, 175) for t in temuan)


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


# ---------------------------------------------------------------------------
# Tes aturan F1-006 s.d. F1-012 — butir terverifikasi visual 18 Sep 2026
# ---------------------------------------------------------------------------
#
# Tiap aturan punya dua macam tes: satu membuktikan ia MENEMUKAN pelanggaran,
# satu lagi membuktikan ia DIAM ketika tidak bisa membuktikan apa-apa. Yang
# kedua yang lebih penting — naskah PMK/KMK sungguhan memakai tabel, dan aturan
# yang tidak tahu diri di situ akan menuduh naskah yang benar.

class TestAturanButirTerverifikasi:
    def _pmk(self, *baris: str) -> list[ParagrafInput]:
        return _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            *baris,
        ])

    # --- F1-006, butir 8: judul tidak diakhiri tanda baca ------------------

    def test_f1_006_judul_berakhir_titik_ditandai(self):
        doc = self._pmk(
            "STANDAR BIAYA MASUKAN.",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        )
        temuan = cek_judul_tanpa_tanda_baca(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "MASUKAN."
        assert temuan[0].usulan_rumusan == "MASUKAN"

    def test_f1_006_judul_bersih_tidak_ditandai(self):
        doc = self._pmk(
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        )
        assert cek_judul_tanpa_tanda_baca(doc, JenisDokumen.PMK) == []

    def test_f1_006_kurung_tutup_tidak_dituduh(self):
        # Butir 8 mempersoalkan akronimnya, bukan tanda kurungnya.
        doc = self._pmk(
            "PENYAMPAIAN LAPORAN PAJAK-PAJAK PRIBADI (LP2P)",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        )
        assert cek_judul_tanpa_tanda_baca(doc, JenisDokumen.PMK) == []

    def test_f1_006_baris_kosong_di_akhir_judul_dilewati(self):
        doc = self._pmk(
            "STANDAR BIAYA MASUKAN",
            "",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        )
        assert cek_judul_tanpa_tanda_baca(doc, JenisDokumen.PMK) == []

    # --- F1-007 / F1-009 / F1-011, butir 16 / 23 / 38 ----------------------

    def _dok_label(self, label: str, *baris: str) -> list[ParagrafInput]:
        """Naskah minimal yang memuat penanda MEMUTUSKAN.

        Sejak 18 Sep 2026 `_cek_label_bagian()` hanya memeriksa label di dalam
        jendelanya masing-masing — Menimbang dan Mengingat sebelum MEMUTUSKAN,
        Menetapkan sesudahnya. Tanpa penanda itu jendelanya tidak bisa
        ditetapkan dan aturannya memilih diam, jadi naskah uji wajib
        memuatnya persis seperti naskah sungguhan.
        """
        if label.upper() == "MENETAPKAN":
            return _buat_dokumen(["MEMUTUSKAN:", *baris, "Pasal 1"])
        return _buat_dokumen([*baris, "MEMUTUSKAN:"])

    def test_label_huruf_besar_semua_diusulkan_dibetulkan(self):
        doc = self._dok_label("Menimbang", "MENIMBANG : a. bahwa sesuatu;")
        temuan = _cek_label_bagian(doc, "Menimbang", "F1-007")
        assert len(temuan) == 1
        assert temuan[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert temuan[0].lokasi.teks_asli == "MENIMBANG"
        assert temuan[0].usulan_rumusan == "Menimbang"

    def test_label_tanpa_titik_dua_ditandai(self):
        doc = self._dok_label(
            "Menimbang", "Menimbang a. bahwa sesuatu yang panjang sekali;"
        )
        temuan = _cek_label_bagian(doc, "Menimbang", "F1-007")
        assert len(temuan) == 1
        assert "titik dua" in temuan[0].catatan

    def test_label_berdiri_sendiri_MEMILIH_DIAM(self):
        """Yang paling penting di kelas ini.

        Pada naskah bertabel, label dan titik duanya ada di sel berbeda,
        sehingga paragraf labelnya cuma berbunyi "Menimbang". Titik duanya
        TIDAK BISA dibuktikan hilang dari sini, jadi tidak boleh dituduhkan.
        """
        doc = self._dok_label("Menimbang", "Menimbang", ":", "a. bahwa sesuatu;")
        assert _cek_label_bagian(doc, "Menimbang", "F1-007") == []

    def test_label_sudah_benar_tidak_ditandai(self):
        for label, aturan in [
            ("Menimbang", "F1-007"),
            ("Mengingat", "F1-009"),
            ("Menetapkan", "F1-011"),
        ]:
            doc = self._dok_label(label, f"{label} : sesuatu yang cukup panjang;")
            assert _cek_label_bagian(doc, label, aturan) == [], label

    def test_kata_berawalan_sama_tidak_dikira_label(self):
        # "Menimbangkan" bukan label. Harus dilewati.
        doc = self._dok_label(
            "Menimbang", "Menimbangkan hal tersebut, maka berlaku hal ini."
        )
        assert _cek_label_bagian(doc, "Menimbang", "F1-007") == []

    # --- Regresi 18 Sep 2026: jendela label dan pemindaian yang kebablasan --

    def test_f1_011_TIDAK_menuduh_isi_diktum_kmk(self):
        """Regresi. Isi diktum KMK yang diawali kata "Menetapkan".

        Pada KMK bertabel, "KESATU" dan isi diktumnya jatuh di paragraf yang
        berbeda, sehingga isi diktumnya berbunyi "Menetapkan Pedoman ...".
        Sebelum jendela dipasang, F1-011 menuduh batang tubuh itu kurang
        titik dua — padahal klausul Menetapkan yang sah ada di atasnya dan
        sudah benar. Tanpa perbaikan, tes ini gagal.
        """
        doc = _buat_dokumen([
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PEDOMAN PENYUSUNAN.",
            "KESATU",
            "Menetapkan Pedoman Penyusunan sebagaimana tercantum dalam Lampiran.",
            "KEDUA",
            "Keputusan Menteri ini mulai berlaku pada tanggal ditetapkan.",
        ])
        assert _cek_label_bagian(doc, "Menetapkan", "F1-011") == []

    def test_label_muncul_dua_kali_hanya_diperiksa_sekali(self):
        """Regresi. Cabang normal dulu memakai `continue`, bukan `break`.

        Akibatnya pemindaian berlanjut setiap kali labelnya ternyata sudah
        benar, dan kata yang sama di tempat lain menghasilkan temuan kedua —
        kadang dengan rentang yang sama persis, yang di Word berarti dua tanda
        di satu rentang.
        """
        doc = _buat_dokumen([
            "MENIMBANG : a. bahwa sesuatu yang cukup panjang;",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG SESUATU.",
            "Pasal 1",
            "MENIMBANG hal tersebut, ditetapkan tata cara sebagai berikut.",
        ])
        temuan = _cek_label_bagian(doc, "Menimbang", "F1-007")
        assert len(temuan) == 1
        assert temuan[0].lokasi.paragraf_index == 0

    def test_tanpa_memutuskan_label_MEMILIH_DIAM(self):
        """Tanpa MEMUTUSKAN, batas pembukaan tidak bisa dipastikan sama sekali.

        Sejalan dengan `_ekstrak_judul_menetapkan()` yang sudah lebih dulu
        memilih diam dalam keadaan yang sama.
        """
        doc = _buat_dokumen(["MENIMBANG a. bahwa sesuatu yang cukup panjang;"])
        assert _cek_label_bagian(doc, "Menimbang", "F1-007") == []

    # --- F1-008, butir 21: bentuk tiap butir Menimbang ---------------------

    def test_f1_008_butir_tidak_diakhiri_titik_koma(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3 diperlukan aturan.",
            "Mengingat :",
        ])
        temuan = cek_butir_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert "titik koma" in temuan[0].catatan
        assert temuan[0].lokasi.panjang == 1

    def test_f1_008_butir_tidak_diawali_bahwa(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. untuk melaksanakan ketentuan Pasal 3 diperlukan aturan baru;",
            "Mengingat :",
        ])
        temuan = cek_butir_menimbang(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert "bahwa" in temuan[0].catatan

    def test_f1_008_butir_benar_tidak_ditandai(self):
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan Pasal 3 diperlukan aturan;",
            "b. bahwa berdasarkan pertimbangan huruf a perlu ditetapkan aturan;",
            "Mengingat :",
        ])
        assert cek_butir_menimbang(doc, JenisDokumen.PMK) == []

    # --- F1-010, butir 31: penomoran dan tanda baca dasar hukum ------------

    def test_f1_010_dasar_hukum_tanpa_titik_koma(self):
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "2. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara",
            "MEMUTUSKAN:",
        ])
        temuan = cek_penomoran_dasar_hukum(doc)
        assert len(temuan) == 1
        assert temuan[0].lokasi.paragraf_index == 2

    def test_f1_010_judul_panjang_berlanjut_tidak_dituduh(self):
        """Regresi yang dicegah sejak awal.

        Judul peraturan yang panjang memenuhi beberapa paragraf. Paragraf
        lanjutannya memang tidak berangka dan tidak berakhir titik koma —
        memeriksa per paragraf berarti menuduh tiap lanjutan.
        """
        doc = _buat_dokumen([
            "Mengingat :",
            "1. Undang-Undang Nomor 12 Tahun 2011 tentang Pembentukan",
            "Peraturan Perundang-Undangan (Lembaran Negara Republik Indonesia",
            "Tahun 2011 Nomor 82, Tambahan Lembaran Negara Nomor 5234);",
            "2. Keputusan Presiden Nomor 113/P Tahun 2019;",
            "MEMUTUSKAN:",
        ])
        assert cek_penomoran_dasar_hukum(doc) == []

    def test_f1_010_tanpa_paragraf_berangka_MEMILIH_DIAM(self):
        # Nomornya mungkin ada di sel tabel yang lain — tidak bisa dibedakan
        # dari dasar hukum tunggal yang memang tidak bernomor.
        doc = _buat_dokumen([
            "Mengingat :",
            "Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara",
            "MEMUTUSKAN:",
        ])
        assert cek_penomoran_dasar_hukum(doc) == []

    # --- F1-012, butir 39: bentuk judul pada Menetapkan --------------------

    def _dengan_menetapkan(self, *baris: str) -> list[ParagrafInput]:
        return _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 5 TAHUN 2026",
            "TENTANG",
            "STANDAR BIAYA MASUKAN",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            *baris,
            "Pasal 1",
        ])

    def test_f1_012_tanpa_titik_di_akhir(self):
        doc = self._dengan_menetapkan(
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA MASUKAN"
        )
        temuan = cek_judul_menetapkan(doc)
        assert len(temuan) == 1
        assert temuan[0].usulan_rumusan == "MASUKAN."

    def test_f1_012_republik_indonesia_harus_dibuang(self):
        doc = self._dengan_menetapkan(
            "Menetapkan : PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA "
            "TENTANG STANDAR BIAYA MASUKAN."
        )
        temuan = cek_judul_menetapkan(doc)
        assert len(temuan) == 1
        assert temuan[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert temuan[0].lokasi.teks_asli == "MENTERI KEUANGAN REPUBLIK INDONESIA"
        # Penggantinya BUKAN teks kosong — Range.insertText tidak bisa
        # menyisipkan teks kosong, usulannya akan diam-diam batal terpasang.
        assert temuan[0].usulan_rumusan == "MENTERI KEUANGAN"

    def test_f1_012_sudah_benar_tidak_ditandai(self):
        doc = self._dengan_menetapkan(
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG STANDAR BIAYA MASUKAN."
        )
        assert cek_judul_menetapkan(doc) == []

    # --- Rujukan ------------------------------------------------------------

    def test_semua_aturan_punya_rujukan_terverifikasi(self):
        from app.rules.rujukan_kmk527 import RUJUKAN

        for aturan_id in [f"F1-{n:03d}" for n in range(1, 13)]:
            assert aturan_id in RUJUKAN, f"{aturan_id} tidak punya rujukan"
            entri = RUJUKAN[aturan_id]
            assert entri["butir"] != "...", aturan_id
            assert entri["kutipan"] != "...", aturan_id
            assert entri["status"] == "visual", aturan_id


# ---------------------------------------------------------------------------
# Tes regresi 18 Sep 2026 — empat salah tandai dan satu lubang cakupan
# ---------------------------------------------------------------------------
#
# Tiap tes di kelas ini GAGAL tanpa perbaikannya. Riwayatnya di
# docs/fase1 drafter.md bagian 6.10, Kasus 6 sampai 10.

class TestRegresi18September:
    def _naskah_pmk(self, memutuskan: str, menetapkan: str) -> list[ParagrafInput]:
        """Naskah PMK utuh yang bagian MEMUTUSKAN-nya bisa diganti-ganti."""
        return _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 99/PMK.01/2024",
            "TENTANG",
            "TATA CARA PENGELOLAAN DANA",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa untuk melaksanakan ketentuan peraturan perundang-undangan;",
            "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, "
            "perlu menetapkan Peraturan Menteri Keuangan tentang Tata Cara "
            "Pengelolaan Dana;",
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            memutuskan,
            menetapkan,
            "Pasal 1",
        ])

    # --- Kasus 6: MEMUTUSKAN berspasi huruf --------------------------------

    def test_memutuskan_berspasi_tetap_dikenali(self):
        """Regresi. Bentuk berspasi huruf lazim dipakai naskah peraturan.

        Pencocokan lama menuntut teksnya persis "MEMUTUSKAN", sehingga pada
        naskah berspasi F1-002 dan F1-012 sama-sama memilih diam dan kesalahan
        nyata di klausul Menetapkan lewat tanpa ada yang memberi tahu.
        """
        salah = (
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA "
            "PENGELOLAAN DANA DAERAH"
        )
        hasil = {}
        for label in ["MEMUTUSKAN:", "MEMUTUSKAN :", "M E M U T U S K A N :"]:
            doc = self._naskah_pmk(label, salah)
            temuan = jalankan_semua(doc, JenisDokumen.PMK, ["F1-002", "F1-012"])
            hasil[label] = sorted(t.aturan_id for t in temuan)

        assert hasil["M E M U T U S K A N :"] == hasil["MEMUTUSKAN:"]
        assert hasil["MEMUTUSKAN:"] == ["F1-002", "F1-012"]

    # --- Kasus 7: F1-012 mencopot nama resmi peraturan lain ----------------

    def test_f1_012_TIDAK_menyentuh_judul_peraturan_yang_dirujuk(self):
        """Regresi. Judul perubahan memuat nama resmi peraturan LAIN.

        Butir 39 mengatur jenis dan nama peraturan INI, yang berhenti di kata
        TENTANG. Sesudahnya yang ada judul, dan judul boleh mengutip nama resmi
        peraturan lain berikut frasa Republik Indonesia-nya. Tanpa pembatasan
        itu alat mengusulkan mengubah nama resmi dokumen orang.
        """
        doc = self._naskah_pmk(
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG PERUBAHAN ATAS "
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA NOMOR 5 TAHUN 2023 "
            "TENTANG TATA CARA PENAGIHAN.",
        )
        temuan = [
            t for t in cek_judul_menetapkan(doc) if "Republik Indonesia" in t.catatan
        ]
        assert temuan == []

    def test_f1_012_jenis_sendiri_tetap_ditandai(self):
        """Penjaga sisi lain: yang berada di posisi JENIS tetap harus ketemu."""
        doc = self._naskah_pmk(
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA "
            "TENTANG TATA CARA PENGELOLAAN DANA.",
        )
        temuan = [
            t for t in cek_judul_menetapkan(doc) if "Republik Indonesia" in t.catatan
        ]
        assert len(temuan) == 1
        assert temuan[0].usulan_rumusan == "MENTERI KEUANGAN"

    # --- Kasus 8: F1-008 menandai ujung paragraf, bukan ujung butir --------

    def test_f1_008_titik_koma_ditandai_di_ujung_butirnya_sendiri(self):
        """Regresi. Satu paragraf memuat dua butir, keduanya kurang titik koma.

        Dulu keduanya ditandai di karakter terakhir PARAGRAF: butir a mendarat
        di tempat milik butir b, dan dua temuan berakhir dengan rentang yang
        sama persis — dua content control dan dua komentar di satu karakter.
        """
        doc = _buat_dokumen([
            "Menimbang : a. bahwa ketentuan Pasal 5 ayat (2) perlu dilaksanakan. "
            "b. bahwa berdasarkan pertimbangan tersebut perlu ditetapkan aturan.",
            "Mengingat :",
        ])
        temuan = [
            t
            for t in cek_butir_menimbang(doc, JenisDokumen.PMK)
            if "titik koma" in t.catatan
        ]
        assert len(temuan) == 2
        letak = sorted(t.lokasi.offset_mulai for t in temuan)
        assert letak[0] != letak[1], "dua butir tidak boleh berbagi satu letak"
        for t in temuan:
            assert t.lokasi.teks_asli == "."

    def test_f1_008_butir_terpotong_antarparagraf_MEMILIH_DIAM(self):
        """Ujung butir yang tidak bisa dipastikan tidak boleh ditebak."""
        doc = _buat_dokumen([
            "Menimbang :",
            "a. bahwa dalam rangka melaksanakan ketentuan Pasal 5 ayat (2)",
            "peraturan perundang-undangan yang berlaku pada saat ini",
            "Mengingat :",
        ])
        temuan = [
            t
            for t in cek_butir_menimbang(doc, JenisDokumen.PMK)
            if "titik koma" in t.catatan
        ]
        assert temuan == []

    # --- Kasus 9: F1-002 jalur cadangan menyorot satu paragraf penuh -------

    def test_f1_002_kekurangan_kata_tidak_menyorot_paragraf(self):
        """Regresi. Judul Menetapkan KEKURANGAN kata dari judul pembuka.

        Tidak ada frasa beda yang bisa ditunjuk di naskah, karena yang salah
        justru kata yang TIDAK ADA. Cadangan lama menyorot satu paragraf penuh
        berikut label Menetapkan yang bukan bagian judul — melanggar bagian 6.5
        dan CLAUDE.md butir 6. Sekarang temuannya tanpa lokasi, ditampilkan
        panel sebagai peringatan dokumen.
        """
        doc = self._naskah_pmk(
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
        )
        temuan = cek_judul_konsisten(doc, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == ""
        assert temuan[0].lokasi.panjang == 0
        assert "PENGELOLAAN DANA" in temuan[0].catatan

    def test_f1_002_tanpa_lokasi_lolos_saringan_jalankan_semua(self):
        """Temuan tanpa lokasi F1-002 tidak boleh ikut terbuang.

        Saringan di jalankan_semua() membuang temuan ber-teks_asli kosong
        karena dulu itu selalu tanda cacat. F1-002 dan F1-003 dikecualikan.
        """
        doc = self._naskah_pmk(
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
        )
        temuan = jalankan_semua(doc, JenisDokumen.PMK, ["F1-002"])
        assert len(temuan) == 1
        assert temuan[0].aturan_id == "F1-002"
        assert temuan[0].lokasi.teks_asli == ""

    # --- Kasus 10: temuan kembar dari aturan yang sama ---------------------

    def test_aturan_sama_tidak_boleh_punya_dua_tanda_di_satu_rentang(self):
        """Jaring pengaman lapis terakhir, berlaku untuk seluruh aturan."""
        doc = self._naskah_pmk(
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA "
            "PENGELOLAAN DANA.",
        )
        temuan = jalankan_semua(doc, JenisDokumen.PMK)
        terlihat = set()
        for t in temuan:
            if not t.lokasi.teks_asli.strip():
                continue
            kunci = (
                t.aturan_id,
                t.lokasi.paragraf_index,
                t.lokasi.offset_mulai,
                t.lokasi.panjang,
            )
            assert kunci not in terlihat, f"tanda kembar: {kunci}"
            terlihat.add(kunci)

    # --- Kasus 11: normalisasi judul yang tidak simetris -------------------

    def test_f1_002_tidak_menuduh_beda_kalau_yang_beda_cuma_titiknya(self):
        """Regresi. Judul pembuka diakhiri titik, isinya sama persis.

        Sisi Menetapkan membuang titik akhir, sisi pembuka tidak — sehingga
        naskah yang judul pembukanya diakhiri titik (kesalahan yang SUDAH
        dilaporkan F1-006) membuat F1-002 ikut melapor "judulnya berbeda",
        padahal kata per katanya sama persis. Penelaah melihat dua tanda,
        salah satunya menuduh perbedaan yang tidak ada.

        Pembagian tugasnya: F1-006 mengurusi tanda bacanya, F1-002 isinya.
        """
        doc = _buat_dokumen([
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 12 TAHUN 2026",
            "TENTANG",
            "TATA CARA PENYUSUNAN STANDAR BIAYA MASUKAN.",
            "DENGAN RAHMAT TUHAN YANG MAHA ESA",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa sesuatu hal perlu diatur lebih lanjut dalam peraturan ini;",
            "Mengingat :",
            "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA "
            "PENYUSUNAN STANDAR BIAYA MASUKAN.",
            "Pasal 1",
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.PMK) == []

        # Penjaga sisi sebaliknya: perbedaan ISI tetap harus ketemu.
        doc_beda = list(doc)
        doc_beda[11] = ParagrafInput(
            index=11,
            teks="Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA "
            "PENYUSUNAN STANDAR BIAYA KELUARAN.",
        )
        temuan = cek_judul_konsisten(doc_beda, JenisDokumen.PMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "KELUARAN"

    # --- Kasus 12: klausul Menetapkan bertabel, tanpa titik dua ------------

    def test_f1_002_naskah_bertabel_judul_sama_tidak_dituduh_beda(self):
        """Regresi. Label "Menetapkan" dan isinya di sel yang berbeda.

        `_AWAL_MENETAPKAN` sudah membuat titik dua opsional sejak Kasus 3,
        tetapi normalisasinya masih mewajibkannya — perbaikan itu terpasang
        separuh. Akibatnya kata "Menetapkan" ikut terbawa ke dalam judul,
        awalan "KEPUTUSAN MENTERI KEUANGAN TENTANG" tidak terpotong karena
        jangkar `^` tidak lagi mengenai apa pun, dan judul yang SAMA PERSIS
        dengan judul pembuka dilaporkan berbeda.

        Bentuk bertabel inilah yang dipakai naskah sungguhan, jadi salah
        tandai ini akan muncul pada hampir setiap KMK yang rapi.
        """
        doc = _buat_dokumen([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 88/KMK.01/2026",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang",
            "a. bahwa dalam rangka tertib administrasi perlu ditetapkan pejabat;",
            "Mengingat",
            "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
            "M E M U T U S K A N :",
            "Menetapkan",
            "KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN PEJABAT PENGELOLA "
            "KEUANGAN.",
            "KESATU",
            "Menetapkan pejabat pengelola keuangan sebagaimana tercantum dalam "
            "Lampiran yang merupakan bagian tidak terpisahkan.",
        ])
        assert cek_judul_konsisten(doc, JenisDokumen.KMK) == []

        # Penjaga sisi sebaliknya: perbedaan yang NYATA tetap harus ketemu,
        # meski bentuknya bertabel.
        doc_beda = list(doc)
        doc_beda[11] = ParagrafInput(
            index=11,
            teks="KEPUTUSAN MENTERI KEUANGAN TENTANG PENUNJUKAN PEJABAT "
            "PENGELOLA KEUANGAN.",
        )
        temuan = cek_judul_konsisten(doc_beda, JenisDokumen.KMK)
        assert len(temuan) == 1
        assert temuan[0].lokasi.teks_asli == "PENUNJUKAN"
