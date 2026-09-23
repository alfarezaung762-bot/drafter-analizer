"""Tes parser struktur — Fase 2 Langkah 0.

Fungsi murni, dites tanpa server, tanpa model, tanpa kredensial — pola yang
sama dengan tes Fase 1.
"""

from app.fase2.tahap0_struktur import bangun_pohon
from app.models.satuan import JenisSatuan
from app.models.temuan import ParagrafInput


def _dok(baris: list[str]) -> list[ParagrafInput]:
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]


_PEMBUKAAN = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN BARANG MILIK NEGARA",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "Menimbang :",
    "a. bahwa untuk tertib pengelolaan barang milik negara perlu diatur;",
    "b. bahwa berdasarkan pertimbangan sebagaimana dimaksud dalam huruf a, "
    "perlu menetapkan Peraturan Menteri Keuangan tentang Tata Cara;",
    "Mengingat :",
    "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
    "2. Peraturan Pemerintah Nomor 27 Tahun 2014 tentang Pengelolaan BMN;",
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
]


class TestPembukaan:
    def test_judul_menimbang_mengingat_menetapkan_terbaca(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + ["Pasal 1", "Isi pasal satu."]))
        assert pohon.gagal is None

        judul = pohon.semua(JenisSatuan.JUDUL)
        assert len(judul) == 1
        assert judul[0].teks == "TATA CARA PENETAPAN STATUS PENGGUNAAN BARANG MILIK NEGARA"

        assert [s.nomor for s in pohon.semua(JenisSatuan.MENIMBANG)] == ["a", "b"]
        assert [s.nomor for s in pohon.semua(JenisSatuan.MENGINGAT)] == ["1", "2"]
        assert pohon.ada("menetapkan")

    def test_butir_menimbang_tanpa_label_bagiannya(self):
        """Teks butir tidak boleh membawa serta kata 'Menimbang :'."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + ["Pasal 1", "Isi."]))
        butir = pohon.cari("menimbang-a")
        assert butir is not None
        assert butir.teks.startswith("bahwa untuk tertib")

    def test_kmk_tanpa_frasa_dengan_rahmat(self):
        """Blok judul KMK berakhir di baris jabatan, bukan Dengan Rahmat."""
        pohon = bangun_pohon(_dok([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 88/KMK.01/2026",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa dalam rangka tertib administrasi perlu ditetapkan;",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN.",
        ]))
        judul = pohon.semua(JenisSatuan.JUDUL)
        assert len(judul) == 1
        assert judul[0].teks == "PENETAPAN PEJABAT PENGELOLA KEUANGAN"


class TestBatangTubuh:
    def _naskah_bertingkat(self) -> list[ParagrafInput]:
        return _dok(_PEMBUKAAN + [
            "BAB I", "KETENTUAN UMUM",
            "Pasal 1",
            "Dalam Peraturan Menteri ini yang dimaksud dengan:",
            "1. Barang Milik Negara adalah semua barang yang dibeli.",
            "2. Hari adalah hari kerja.",
            "BAB II", "TATA CARA",
            "Bagian Kesatu", "Pengajuan",
            "Pasal 2",
            "(1) Pengguna Barang mengajukan permohonan.",
            "(2) Permohonan sebagaimana dimaksud pada ayat (1) dilengkapi dengan:",
            "a. fotokopi dokumen kepemilikan;",
            "b. surat pernyataan tanggung jawab.",
            "(3) Permohonan diselesaikan paling lambat 30 (tiga puluh) hari kerja.",
            "Bagian Kedua", "Penetapan",
            "Paragraf 1", "Kewenangan",
            "Pasal 3",
            "Pengelola Barang menetapkan status penggunaan.",
        ])

    def test_seluruh_tingkat_terbaca(self):
        pohon = bangun_pohon(self._naskah_bertingkat())
        assert pohon.gagal is None
        for id_satuan in [
            "bab-i", "bab-ii",
            "bab-ii-bagian-kesatu", "bab-ii-bagian-kedua",
            "bab-ii-bagian-kedua-paragraf-1",
            "pasal-1", "pasal-1-angka-1", "pasal-1-angka-2",
            "pasal-2", "pasal-2-ayat-1", "pasal-2-ayat-2", "pasal-2-ayat-3",
            "pasal-2-ayat-2-huruf-a", "pasal-2-ayat-2-huruf-b",
            "pasal-3",
        ]:
            assert pohon.ada(id_satuan), id_satuan

    def test_induk_menunjuk_ke_atas_dengan_benar(self):
        pohon = bangun_pohon(self._naskah_bertingkat())
        assert pohon.cari("pasal-2-ayat-2-huruf-a").induk == "pasal-2-ayat-2"
        assert pohon.cari("pasal-2-ayat-2").induk == "pasal-2"
        assert pohon.cari("pasal-1-angka-1").induk == "pasal-1"
        assert pohon.cari("bab-ii-bagian-kesatu").induk == "bab-ii"

    def test_bagian_menutup_ayat_yang_terbuka(self):
        """REGRESI. Tanpa ini ayat terakhir menelan judul Bagian berikutnya.

        Rentang tanda temuan pada ayat itu akan menimpa baris judul yang
        sama sekali tidak bersalah — pelanggaran kaidah Fase 1.
        """
        pohon = bangun_pohon(self._naskah_bertingkat())
        ayat3 = pohon.cari("pasal-2-ayat-3")
        bagian2 = pohon.cari("bab-ii-bagian-kedua")
        assert ayat3.paragraf_akhir <= bagian2.paragraf_mulai

    def test_judul_bab_ikut_terbaca(self):
        """REGRESI. 'BAB I' tanpa 'KETENTUAN UMUM' kehilangan artinya."""
        pohon = bangun_pohon(self._naskah_bertingkat())
        assert pohon.cari("bab-i").teks == "BAB I KETENTUAN UMUM"
        assert pohon.cari("bab-ii-bagian-kesatu").teks == "Bagian Kesatu Pengajuan"

    def test_pasal_sisipan_berhuruf(self):
        """Pasal 12A muncul di peraturan perubahan — harus terbaca."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 12", "Isi pasal dua belas.",
            "Pasal 12A", "Isi pasal sisipan.",
        ]))
        assert pohon.ada("pasal-12a")
        assert pohon.cari("pasal-12a").nomor == "12A"

    def test_kata_pasal_di_tengah_kalimat_bukan_judul_pasal(self):
        """Pola dijangkar di awal paragraf — pelajaran Fase 1 Kasus 3."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 5",
            "Ketentuan sebagaimana dimaksud dalam Pasal 3 berlaku juga di sini.",
        ]))
        assert [s.nomor for s in pohon.semua(JenisSatuan.PASAL)] == ["5"]


class TestPencarian:
    def test_ada_menjawab_rujukan_menggantung(self):
        """Inilah yang dipakai F2-001 dan Langkah 5."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1", "(1) Isi ayat satu.",
        ]))
        assert pohon.ada("pasal-1-ayat-1")
        assert not pohon.ada("pasal-30")
        assert not pohon.ada("pasal-1-ayat-9")

    def test_teks_lengkap_merangkai_anak_cucu(self):
        """Dipakai Langkah 4, yang menuntut teks UTUH."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1",
            "(1) Pengguna Barang mengajukan permohonan.",
            "(2) Permohonan dilengkapi dengan:",
            "a. dokumen kepemilikan;",
        ]))
        utuh = pohon.teks_lengkap("pasal-1")
        assert "mengajukan permohonan" in utuh
        assert "dokumen kepemilikan" in utuh


class TestMemilihDiam:
    """Batas kewajaran. Parser MELAPOR GAGAL, tidak menebak."""

    def test_tanpa_paragraf_sama_sekali(self):
        assert bangun_pohon([]).gagal is not None

    def test_dokumen_panjang_tanpa_satu_pun_pasal(self):
        pohon = bangun_pohon(_dok([f"baris nomor {i}" for i in range(40)]))
        assert pohon.gagal is not None
        assert "Pasal" in pohon.gagal

    def test_dokumen_pendek_tanpa_pasal_tidak_dianggap_gagal(self):
        """Potongan naskah pendek memang wajar tidak punya pasal."""
        assert bangun_pohon(_dok(["Menimbang :", "a. bahwa sesuatu;"])).gagal is None

    def test_penomoran_melompat_jauh_dianggap_pembacaan_kacau(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1", "Isi.",
            "Pasal 99", "Isi.",
        ]))
        assert pohon.gagal is not None
        assert "melompat" in pohon.gagal

    def test_lompatan_wajar_tidak_dianggap_gagal(self):
        """Penomoran yang benar-benar cacat urusan F2-004, bukan parser."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1", "Isi.",
            "Pasal 3", "Isi.",
        ]))
        assert pohon.gagal is None

    def test_tiap_satuan_punya_rentang_paragraf_yang_sah(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "BAB I", "KETENTUAN UMUM",
            "Pasal 1", "(1) Isi ayat.",
        ]))
        assert pohon.gagal is None
        for s in pohon.satuan:
            assert s.bisa_ditandai, s.id


class TestNaskahBertabel:
    """Bentuk yang dipakai naskah sungguhan — label dan isi di sel berbeda."""

    def test_label_menimbang_berdiri_sendiri(self):
        pohon = bangun_pohon(_dok([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 88/KMK.01/2026",
            "TENTANG",
            "PENETAPAN PEJABAT",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang",
            "a. bahwa dalam rangka tertib administrasi perlu ditetapkan;",
            "Mengingat",
            "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
            "M E M U T U S K A N :",
            "Menetapkan",
            "KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN PEJABAT.",
        ]))
        assert pohon.gagal is None
        assert pohon.ada("menimbang-a")
        assert pohon.ada("mengingat-1")
        assert pohon.ada("menetapkan")

    def test_memutuskan_berspasi_tetap_dikenali(self):
        """Bentuk berspasi huruf lazim di naskah peraturan."""
        pohon = bangun_pohon(_dok([
            "TENTANG", "JUDUL UJI", "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "M E M U T U S K A N :",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG JUDUL UJI.",
            "Pasal 1", "Isi pasal.",
        ]))
        assert pohon.ada("menetapkan")
        assert pohon.ada("pasal-1")

    def test_butir_terpotong_antarparagraf_disambung(self):
        """REGRESI. Judul peraturan panjang memenuhi dua-tiga baris.

        Tanpa penyambungan, satuan cuma memuat baris pertamanya — dan temuan
        pada baris lanjutannya tidak bisa ditandai dengan benar.
        """
        pohon = bangun_pohon(_dok([
            "TENTANG", "JUDUL UJI", "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Mengingat",
            "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan",
            "Negara (Lembaran Negara Republik Indonesia Tahun 2004",
            "Nomor 5, Tambahan Lembaran Negara Nomor 4355);",
            "2. Peraturan Pemerintah Nomor 27 Tahun 2014;",
            "MEMUTUSKAN:",
            "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG JUDUL UJI.",
        ]))
        butir = pohon.cari("mengingat-1")
        assert butir is not None
        assert "Tambahan Lembaran Negara" in butir.teks
        # Rentangnya mencakup ketiga barisnya, bukan cuma yang pertama.
        assert butir.paragraf_akhir - butir.paragraf_mulai == 3
        # Butir berikutnya tidak ikut tertelan.
        assert pohon.cari("mengingat-2").teks.startswith("Peraturan Pemerintah")


class TestKmkBelumDidukung:
    """Fase 2 fokus PMK dulu — dan diamnya harus TERDENGAR.

    Diputuskan 22 Sep 2026. Tanpa penjaga ini, KMK menghasilkan pembukaan saja
    tanpa peringatan apa pun, dan penelaah mengira naskahnya sudah diperiksa.
    """

    def test_kmk_melapor_gagal_bukan_diam(self):
        pohon = bangun_pohon(_dok([
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 88/KMK.01/2026",
            "TENTANG",
            "PENETAPAN PEJABAT PENGELOLA KEUANGAN",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "Menimbang :",
            "a. bahwa dalam rangka tertib administrasi perlu ditetapkan;",
            "Mengingat :",
            "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PENETAPAN PEJABAT.",
            "KESATU",
            "Menetapkan pejabat pengelola keuangan sebagaimana tercantum dalam Lampiran.",
            "KEDUA",
            "Pejabat sebagaimana dimaksud dalam Diktum KESATU wajib menyampaikan laporan.",
        ]))
        assert pohon.gagal is not None
        assert "KMK" in pohon.gagal
        assert "Fase 1 tetap berjalan" in pohon.gagal

    def test_pmk_dengan_kata_kesatu_di_dalam_pasal_tidak_ikut_kena(self):
        """Penjaga KMK hanya menyala kalau TIDAK ADA Pasal sama sekali."""
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1",
            "Tahap kesatu dilaksanakan oleh Pengelola Barang.",
            "Pasal 2",
            "Isi pasal dua.",
        ]))
        assert pohon.gagal is None
        assert pohon.ada("pasal-1")


class TestNaskahPerubahan:
    """Naskah PERUBAHAN ditolak Fase 2, dan penolakannya bersuara.

    Tanpa penjaga ini, alat SALAH TANDAI: pasal yang dikutip di dalam naskah
    perubahan milik peraturan induk, bukan draf yang sedang ditelaah. Dibuktikan
    22 Sep 2026 — F2-001 menandai "sebagaimana dimaksud dalam Pasal 18" sebagai
    rujukan menggantung padahal Pasal 18 ada di PMK induknya.
    """

    _KEPALA = [
        "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
        "NOMOR 40 TAHUN 2026",
        "TENTANG",
        "PERUBAHAN ATAS PERATURAN MENTERI KEUANGAN NOMOR 12 TAHUN 2024 "
        "TENTANG TATA CARA PENETAPAN STATUS PENGGUNAAN",
        "DENGAN RAHMAT TUHAN YANG MAHA ESA",
        "MENTERI KEUANGAN REPUBLIK INDONESIA,",
        "MEMUTUSKAN:",
        "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG PERUBAHAN ATAS "
        "PERATURAN MENTERI KEUANGAN NOMOR 12 TAHUN 2024.",
    ]
    _ISI = [
        "Pasal I",
        "Beberapa ketentuan dalam Peraturan Menteri Keuangan Nomor 12 Tahun 2024 diubah:",
        "1. Ketentuan Pasal 5 diubah sehingga berbunyi sebagai berikut:",
        "Pasal 5",
        "Permohonan sebagaimana dimaksud dalam Pasal 18 diajukan secara elektronik.",
        "Pasal II",
        "Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.",
    ]

    def _pohon(self, baris):
        return bangun_pohon(
            [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]
        )

    def test_dikenali_dari_judulnya(self):
        pohon = self._pohon(self._KEPALA + self._ISI)
        assert pohon.gagal is not None
        assert "PERUBAHAN" in pohon.gagal

    def test_alasannya_menyebut_peraturan_induk(self):
        """Penelaah harus tahu KENAPA, bukan cuma bahwa alat diam."""
        pohon = self._pohon(self._KEPALA + self._ISI)
        assert "induk" in pohon.gagal
        assert "Fase 1 tetap berjalan" in pohon.gagal

    def test_dikenali_dari_pasal_romawi_walau_judulnya_tidak_menyebut(self):
        kepala = list(self._KEPALA)
        kepala[3] = "TATA CARA PENETAPAN STATUS PENGGUNAAN"
        kepala[7] = "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA."
        pohon = self._pohon(kepala + self._ISI)
        assert pohon.gagal is not None
        assert "Pasal I" in pohon.gagal

    def test_perubahan_kedua_juga_dikenali(self):
        kepala = list(self._KEPALA)
        kepala[3] = "PERUBAHAN KEDUA ATAS PERATURAN MENTERI KEUANGAN NOMOR 12 TAHUN 2024"
        pohon = self._pohon(kepala + ["Pasal 1", "Isi biasa."])
        assert pohon.gagal is not None

    def test_NEGATIF_naskah_baru_biasa_tidak_ikut_ditolak(self):
        """Penjaga yang kebablasan mematikan Fase 2 untuk naskah yang sah."""
        pohon = self._pohon(
            self._KEPALA[:3]
            + [
                "TATA CARA PENETAPAN STATUS PENGGUNAAN",
                "DENGAN RAHMAT TUHAN YANG MAHA ESA",
                "MENTERI KEUANGAN REPUBLIK INDONESIA,",
                "MEMUTUSKAN:",
                "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
                "Pasal 1",
                "Isi pasal satu.",
                "Pasal 2",
                "Isi pasal dua.",
            ]
        )
        assert pohon.gagal is None

    def test_NEGATIF_kata_perubahan_tanpa_ATAS_tidak_ikut_ditolak(self):
        """"Perubahan Anggaran" bukan naskah perubahan."""
        kepala = list(self._KEPALA)
        kepala[3] = "TATA CARA PERUBAHAN ANGGARAN KEMENTERIAN NEGARA"
        kepala[7] = "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA."
        pohon = self._pohon(kepala + ["Pasal 1", "Isi pasal satu."])
        assert pohon.gagal is None
