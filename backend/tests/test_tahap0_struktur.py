"""Tes parser struktur — Fase 2 Langkah 0.

Fungsi murni, dites tanpa server, tanpa model, tanpa kredensial — pola yang
sama dengan tes Fase 1.
"""

from app.models.satuan import JenisSatuan
from app.models.temuan import ParagrafInput
from app.telaah.tahap1_parser.struktur import bangun_pohon, pasangan_label


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


class TestBatangInduk:
    """Butir tabulasi tidak boleh sampai ke model tanpa kalimat induknya.

    Dua satuan di bawah ini disalin dari PMK 17 Tahun 2026, dan keduanya kasus
    nyata yang sudah menghasilkan salah tandai 26 Sep 2026: dikirim telanjang,
    "Pertanggungjawaban." terbaca model sebagai norma yang tidak menyebut
    pemikul kewajiban — padahal ia butir daftar ruang lingkup.
    """

    _ISI = [
        "Pasal 2",
        "Ruang lingkup pengaturan dalam Peraturan Menteri ini meliputi:",
        "a. Koordinasi dalam rangka penyusunan RKA Otoritas Jasa Keuangan;",
        "b. Pejabat perbendaharaan; dan",
        "c. Pertanggungjawaban.",
        "Pasal 9",
        "(1) KPA BUN sebagaimana dimaksud dalam Pasal 7 menetapkan pegawai sebagai:",
        "a. PPK; dan",
        "b. PPSPM.",
    ]

    def _pohon(self):
        return bangun_pohon(_dok(_PEMBUKAAN + self._ISI))

    def test_butir_ruang_lingkup_membawa_kalimat_pembukanya(self):
        gabung = self._pohon().teks_dengan_induk("pasal-2-huruf-c")
        assert "Ruang lingkup" in gabung and "meliputi" in gabung
        assert "Pertanggungjawaban." in gabung

    def test_huruf_di_dalam_ayat_membawa_batang_ayatnya(self):
        """"PPK;" sendirian tidak berarti apa-apa."""
        gabung = self._pohon().teks_dengan_induk("pasal-9-ayat-1-huruf-a")
        assert "menetapkan pegawai sebagai:" in gabung
        assert "PPK" in gabung

    def test_batang_TIDAK_membawa_saudara_sebutirnya(self):
        """Kalau anak-cucu induknya ikut, butir yang diperiksa tenggelam."""
        assert "PPSPM" not in self._pohon().batang_induk("pasal-9-ayat-1-huruf-a")

    def test_satuan_teratas_tidak_punya_batang(self):
        assert self._pohon().batang_induk("pasal-2") == ""

    def test_id_karangan_tidak_meledak(self):
        assert self._pohon().batang_induk("pasal-99-ayat-3") == ""
        assert self._pohon().teks_dengan_induk("pasal-99-ayat-3") == ""


class TestButirBersarang:
    """Regresi PMK 45 Tahun 2026 Pasal 3, 27 Sep 2026 — docs/perbaiki bug.md bug 1.

    Angka 1–9 di bawah huruf a dulu jadi anak ayat (1), bersaudara dengan
    huruf a. Model menerima "Lembaga Kepresidenan;" sebagai lanjutan
    "merupakan barang yang:", melompati "digunakan … oleh:".
    """

    _ISI = [
        "BAB II",
        "PEMBEBASAN BEA MASUK",
        "Pasal 3",
        "(1) Barang sebagaimana dimaksud dalam Pasal 2 merupakan barang yang:",
        "a. digunakan bagi keperluan pertahanan dan keamanan negara oleh:",
        "1. Lembaga Kepresidenan;",
        "2. Kementerian Pertahanan; dan/atau",
        "b. digunakan dalam kegiatan militer bersama.",
        "(2) Barang dan bahan dipergunakan untuk keperluan lain.",
    ]

    def _pohon(self):
        return bangun_pohon(_dok(_PEMBUKAAN + self._ISI))

    def test_angka_di_bawah_huruf_menjadi_anak_hurufnya(self):
        pohon = self._pohon()
        angka = pohon.cari("pasal-3-ayat-1-huruf-a-angka-1")
        assert angka is not None and angka.induk == "pasal-3-ayat-1-huruf-a"
        assert not pohon.ada("pasal-3-ayat-1-angka-1")

    def test_huruf_sesudah_daftar_angka_kembali_bersaudara_dengan_huruf_a(self):
        b = self._pohon().cari("pasal-3-ayat-1-huruf-b")
        assert b is not None and b.induk == "pasal-3-ayat-1"

    def test_rentang_huruf_a_mencakup_angkanya(self):
        pohon = self._pohon()
        a = pohon.cari("pasal-3-ayat-1-huruf-a")
        angka_2 = pohon.cari("pasal-3-ayat-1-huruf-a-angka-2")
        assert a.paragraf_akhir == angka_2.paragraf_akhir

    def test_ayat_baru_menutup_seluruh_butir(self):
        ayat_2 = self._pohon().cari("pasal-3-ayat-2")
        assert ayat_2 is not None and ayat_2.induk == "pasal-3"

    def test_huruf_di_bawah_angka_juga_bersarang_lalu_kembali(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 4",
            "(1) Dokumen terdiri atas:",
            "1. dokumen pokok, yang meliputi:",
            "a. surat permohonan;",
            "b. surat kuasa;",
            "2. dokumen pendukung.",
        ]))
        assert pohon.cari("pasal-4-ayat-1-angka-1-huruf-b").induk == "pasal-4-ayat-1-angka-1"
        assert pohon.cari("pasal-4-ayat-1-angka-2").induk == "pasal-4-ayat-1"

    def test_definisi_pasal_1_tetap_bersaudara(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1",
            "1. Hari adalah hari kerja.",
            "2. Menteri adalah menteri keuangan.",
        ]))
        assert pohon.cari("pasal-1-angka-2").induk == "pasal-1"


class TestJudulBabBerbaris:
    """Regresi PMK 45 dan PMK 17, 27 Sep 2026: baris kedua judul BAB hilang."""

    def test_judul_bab_dua_baris_terbaca_utuh(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "BAB III",
            "PERMOHONAN, PENELITIAN,",
            "DAN PENETAPAN PEMBEBASAN BEA MASUK",
            "Pasal 6",
            "Isi pasal enam.",
        ]))
        bab = pohon.cari("bab-iii")
        assert bab.teks == "BAB III PERMOHONAN, PENELITIAN, DAN PENETAPAN PEMBEBASAN BEA MASUK"
        assert pohon.cari("pasal-6").teks == "Isi pasal enam."

    def test_judul_bagian_tidak_menelan_kalimat_pasal(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "BAB I",
            "KETENTUAN UMUM",
            "Pasal 1",
            "Isi pasal satu.",
        ]))
        assert pohon.cari("bab-i").teks == "BAB I KETENTUAN UMUM"


class TestLabelDiTeksModel:
    """CLAUDE.md butir 14: label penomoran wajib ikut di teks yang dibaca model."""

    def _pohon(self):
        return TestButirBersarang()._pohon()

    def test_teks_berlabel_memuat_huruf_dan_angka(self):
        utuh = self._pohon().teks_lengkap("pasal-3-ayat-1", berlabel=True)
        assert "a. digunakan bagi" in utuh
        assert "1. Lembaga Kepresidenan;" in utuh
        assert "b. digunakan dalam kegiatan militer" in utuh

    def test_akar_tidak_dilabeli_karena_jadi_sumber_kutipan(self):
        utuh = self._pohon().teks_lengkap("pasal-3-ayat-1", berlabel=True)
        assert utuh.startswith("Barang sebagaimana")

    def test_bawaan_tanpa_label_untuk_pencocokan_kata(self):
        utuh = self._pohon().teks_lengkap("pasal-3-ayat-1")
        assert "a. " not in utuh and "1. " not in utuh

    def test_batang_induk_membawa_label_tiap_tingkat(self):
        batang = self._pohon().batang_induk("pasal-3-ayat-1-huruf-a-angka-1")
        assert "Pasal 3" in batang
        assert "(1) Barang" in batang
        assert "a. digunakan bagi keperluan" in batang

    def test_teks_dengan_induk_melabeli_akarnya(self):
        gabung = self._pohon().teks_dengan_induk("pasal-3-ayat-1-huruf-b")
        assert "b. digunakan dalam kegiatan militer" in gabung


# ===========================================================================
# Bug 11 — naskah bertata letak tabel: nomor dan teks di sel terpisah
# ===========================================================================


def _baris_tabel(isi: list[list[str]], tabel: int = 0, mulai: int = 0) -> list[ParagrafInput]:
    """Satu paragraf per sel, berurutan seperti body.paragraphs di Word."""
    hasil = []
    for b, sel in enumerate(isi):
        for s, t in enumerate(sel):
            hasil.append(ParagrafInput(index=0, teks=t, tabel=tabel, baris=b, sel=s))
    return hasil


def _nomori(paragraf: list[ParagrafInput]) -> list[ParagrafInput]:
    return [p.model_copy(update={"index": i}) for i, p in enumerate(paragraf)]


class TestLabelTerpisahSel:
    """PMK 119/2025: "1." di satu sel, "Pemerintah … adalah …" di sel sebelahnya."""

    def _naskah(self) -> list[ParagrafInput]:
        pembukaan = [ParagrafInput(index=0, teks=t) for t in _PEMBUKAAN[:6]]
        menimbang = _baris_tabel([
            ["Menimbang", ":", "a.", "bahwa untuk tertib pengelolaan perlu diatur;"],
            ["", "", "b.", "bahwa perlu menetapkan Peraturan Menteri Keuangan;"],
            ["Mengingat", ":", "1.", "Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan Negara;"],
        ], tabel=0)
        tengah = [ParagrafInput(index=0, teks=t) for t in _PEMBUKAAN[-2:]]
        batang = _baris_tabel([
            ["", "", "Pasal 1"],
            ["", "", "Dalam Peraturan Menteri ini yang dimaksud dengan:"],
            ["", "", "1.", "Pengelola Barang adalah pejabat yang berwenang."],
            ["", "", "2.", "Pengguna Barang adalah pejabat pemegang kewenangan."],
            ["", "", "Pasal 2"],
            ["", "", "(1)", "Pengguna Barang wajib mengajukan permohonan."],
        ], tabel=1)
        return _nomori(pembukaan + menimbang + tengah + batang)

    def test_definisi_pasal_1_terbaca_sebagai_angka(self):
        pohon = bangun_pohon(self._naskah())
        assert pohon.gagal is None
        angka = pohon.cari("pasal-1-angka-1")
        assert angka is not None
        assert angka.teks == "Pengelola Barang adalah pejabat yang berwenang."

    def test_rentang_satuan_mencakup_sel_teksnya(self):
        """Kutipan dari teks definisi harus ada di dalam rentang satuannya."""
        paragraf = self._naskah()
        pohon = bangun_pohon(paragraf)
        angka = pohon.cari("pasal-1-angka-1")
        isi = [p.teks for p in paragraf if angka.paragraf_mulai <= p.index < angka.paragraf_akhir]
        assert "Pengelola Barang adalah pejabat yang berwenang." in isi

    def test_menimbang_dan_mengingat_bertabel_terbaca(self):
        pohon = bangun_pohon(self._naskah())
        assert [s.nomor for s in pohon.semua(JenisSatuan.MENIMBANG)] == ["a", "b"]
        assert pohon.cari("menimbang-a").teks.startswith("bahwa untuk tertib")
        assert [s.nomor for s in pohon.semua(JenisSatuan.MENGINGAT)] == ["1"]

    def test_ayat_bertabel_terbaca(self):
        pohon = bangun_pohon(self._naskah())
        assert pohon.cari("pasal-2-ayat-1").teks == "Pengguna Barang wajib mengajukan permohonan."

    def test_NEGATIF_label_dan_teks_di_baris_berbeda_tidak_disambung(self):
        paragraf = _nomori(_baris_tabel([["1."], ["Teks baris lain."]]))
        assert pasangan_label(paragraf) == {}

    def test_NEGATIF_di_luar_tabel_tidak_disambung(self):
        paragraf = _dok(["1.", "Teks paragraf berikutnya."])
        assert pasangan_label(paragraf) == {}

    def test_NEGATIF_teks_yang_sudah_berlabel_tidak_disambung(self):
        paragraf = _nomori(_baris_tabel([["a.", "(1) Ayat yang berlabel sendiri."]]))
        assert pasangan_label(paragraf) == {}


class TestLampiranDicariSesudahPenutup:
    """Pasal yang kalimatnya diawali "Lampiran …" bukan kepala lampiran."""

    def test_pasal_berawalan_lampiran_tidak_memotong_batang_tubuh(self):
        pohon = bangun_pohon(_dok(_PEMBUKAAN + [
            "Pasal 1",
            "Lampiran merupakan bagian tidak terpisahkan dari Peraturan Menteri ini.",
            "Pasal 2",
            "Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.",
            "Ditetapkan di Jakarta",
            "LAMPIRAN",
            "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
        ]))
        assert pohon.ada("pasal-2")
        lampiran = pohon.cari("lampiran")
        assert lampiran is not None and lampiran.teks == "LAMPIRAN"
