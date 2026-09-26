"""Tes aturan mekanis Fase 2 — F2-001, F2-003, F2-004, F2-007."""

from app.fase2.mekanis_konsistensi import _kata_jadi_angka, jalankan_mekanis
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.models.temuan import ParagrafInput

_KEPALA = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA", "NOMOR 12 TAHUN 2026",
    "TENTANG", "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA", "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "Mengingat :", "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan;",
    "MEMUTUSKAN:", "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
]


def _jalan(baris, aturan=None):
    doc = [ParagrafInput(index=i, teks=t) for i, t in enumerate(_KEPALA + baris)]
    pohon = bangun_pohon(doc)
    return jalankan_mekanis(pohon, ambil_definisi(pohon), doc, aturan)


def _kode(temuan):
    return sorted(t.aturan_id for t in temuan)


class TestF2001RujukanMenggantung:
    def test_rujukan_ke_pasal_yang_tidak_ada(self):
        t = _jalan([
            "Pasal 1", "Ketentuan sebagaimana dimaksud dalam Pasal 30 berlaku.",
        ], ["F2-001"])
        assert len(t) == 1
        assert "Pasal 30" in t[0].catatan
        assert t[0].fase == 2

    def test_rujukan_ke_pasal_yang_ada_tidak_ditandai(self):
        assert _jalan([
            "Pasal 1", "Isi pasal satu.",
            "Pasal 2", "Ketentuan sebagaimana dimaksud dalam Pasal 1 berlaku.",
        ], ["F2-001"]) == []

    def test_rujukan_ke_ayat_yang_tidak_ada(self):
        t = _jalan([
            "Pasal 1", "(1) Isi ayat satu.",
            "Pasal 2", "Ketentuan sebagaimana dimaksud dalam Pasal 1 ayat (5) berlaku.",
        ], ["F2-001"])
        assert len(t) == 1
        assert "ayat (5)" in t[0].catatan

    def test_rujukan_ke_peraturan_lain_TIDAK_ditandai(self):
        """Yang paling rawan salah tandai: Pasal milik dokumen lain."""
        assert _jalan([
            "Pasal 1",
            "Ketentuan sebagaimana dimaksud dalam Pasal 12 Undang-Undang "
            "Nomor 1 Tahun 2004 berlaku juga di sini.",
        ], ["F2-001"]) == []

    def test_kata_pasal_tanpa_frasa_baku_tidak_ditandai(self):
        """Hanya bentuk baku 'sebagaimana dimaksud dalam' yang diperiksa."""
        assert _jalan([
            "Pasal 1", "Hal ini diatur juga di Pasal 30 peraturan sebelumnya.",
        ], ["F2-001"]) == []


class TestF2003DefinisiTakTerpakai:
    def test_definisi_tidak_pernah_dipakai(self):
        t = _jalan([
            "Pasal 1",
            "1. Sistem Informasi adalah aplikasi pencatatan barang.",
            "2. Hari adalah hari kerja.",
            "Pasal 2", "Permohonan diselesaikan dalam 5 (lima) Hari.",
        ], ["F2-003"])
        assert len(t) == 1
        assert "Sistem Informasi" in t[0].catatan

    def test_dipakai_dengan_huruf_kecil_tetap_dianggap_terpakai(self):
        """Naskah kerap menulis istilahnya huruf kecil di batang tubuh."""
        assert _jalan([
            "Pasal 1", "1. Pengelola Barang adalah pejabat yang berwenang.",
            "Pasal 2", "Permohonan diajukan kepada pengelola barang.",
        ], ["F2-003"]) == []

    def test_dipakai_di_pasal_dua_angka_tetap_dianggap_terpakai(self):
        """KAIDAH YANG MENJAGA SELURUH F2-003.

        Teks pembanding dulu disusun dengan membuang satuan ber-id BERAWALAN
        "pasal-1" — yang juga mengenai pasal-10 sampai pasal-19. Sepuluh pasal
        hilang diam-diam, dan tiap istilah yang kebetulan hanya dipakai di sana
        dituduh mubazir. Terbukti pada PMK 17 Tahun 2026: "DIPA" dipakai di
        Pasal 10 dan Pasal 19, tetap ditandai.

        Kalau suatu hari awalan id dipakai lagi sebagai penyaring, tes ini yang
        berbunyi.
        """
        isi = ["Pasal 1", "1. DIPA adalah dokumen pelaksanaan anggaran."]
        for n in range(2, 20):
            isi += [f"Pasal {n}", f"Ketentuan pelaksanaan tahap ke-{n} berlaku."]
        # Satu-satunya pemakaian ada di Pasal 12 — di dalam rentang yang dulu
        # terbuang. Dipasang PERSIS di situ, bukan di Pasal 2, supaya tesnya
        # benar-benar menguji rentang yang bermasalah.
        isi[2 * 12 - 1] = "Penyaluran dibebankan pada DIPA BUN."
        assert _jalan(isi, ["F2-003"]) == []

    def test_definisi_di_pasal_1_sendiri_tidak_dihitung_pemakaian(self):
        """Batasnya tetap ada: istilah yang cuma muncul di daftar definisi
        Pasal 1 memang belum dipakai."""
        t = _jalan([
            "Pasal 1",
            "1. Sistem Informasi adalah aplikasi pencatatan barang.",
            "2. Hari adalah Sistem Informasi yang dipakai harian.",
            "Pasal 2", "Permohonan diselesaikan dalam 5 (lima) Hari.",
        ], ["F2-003"])
        assert [x.lokasi.teks_asli for x in t] == ["Sistem Informasi"]


class TestF2004Penomoran:
    def test_pasal_melompat(self):
        t = _jalan([
            "Pasal 1", "Isi.", "Pasal 2", "Isi.", "Pasal 4", "Isi.",
        ], ["F2-004"])
        assert len(t) == 1
        assert "melompat dari 2 ke 4" in t[0].catatan

    def test_ayat_berulang(self):
        t = _jalan([
            "Pasal 1", "(1) Isi.", "(2) Isi.", "(2) Isi lagi.",
        ], ["F2-004"])
        assert len(t) == 1
        assert "lebih dari sekali" in t[0].catatan

    def test_pasal_sisipan_berhuruf_tidak_dianggap_melompat(self):
        assert _jalan([
            "Pasal 1", "Isi.", "Pasal 1A", "Isi sisipan.", "Pasal 2", "Isi.",
        ], ["F2-004"]) == []

    def test_urut_rapi_tidak_ditandai(self):
        assert _jalan([
            "Pasal 1", "(1) Isi.", "(2) Isi.", "Pasal 2", "Isi.",
        ], ["F2-004"]) == []


class TestF2007Bilangan:
    def test_angka_tidak_cocok_hurufnya(self):
        t = _jalan([
            "Pasal 1", "Permohonan diselesaikan paling lambat 30 (tiga belas) hari.",
        ], ["F2-007"])
        assert len(t) == 1
        assert "berarti 13" in t[0].catatan

    def test_contoh_rumusan_masuk_ke_saran_BUKAN_ke_naskah(self):
        """Kebijakan hijau/kuning, 22 Sep 2026.

        F2-007 membuktikan ketidakcocokannya, tetapi mana yang benar — angkanya
        atau hurufnya — justru pertanyaan pokoknya. Jadi tidak ada yang dicoret:
        rumusan yang cocok cuma ditawarkan di komentar.
        """
        t = _jalan([
            "Pasal 1", "Permohonan diselesaikan paling lambat 30 (tiga belas) hari.",
        ], ["F2-007"])[0]
        assert t.jenis_tanda.value == "catatan"
        assert t.usulan_rumusan is None
        assert 'Contoh rumusan: "13 (tiga belas)"' in t.saran

    def test_cocok_tidak_ditandai(self):
        assert _jalan([
            "Pasal 1", "Permohonan diselesaikan paling lambat 30 (tiga puluh) hari.",
        ], ["F2-007"]) == []

    def test_kata_tak_dikenal_memilih_diam(self):
        """Tidak bisa dibuktikan berarti tidak dituduhkan."""
        assert _jalan([
            "Pasal 1", "Berlaku bagi 3 (tiga) satuan kerja di 5 (lima) wilayah.",
            "Pasal 2", "Disampaikan kepada 2 (dua orang) pejabat.",
        ], ["F2-007"]) == []


class TestKataJadiAngka:
    def test_bentuk_yang_lazim(self):
        for kata, angka in [
            ("tiga puluh", 30), ("dua belas", 12), ("sepuluh", 10),
            ("sebelas", 11), ("lima", 5), ("seratus", 100),
            ("seratus dua puluh lima", 125), ("dua ribu", 2000),
            ("dua ribu lima ratus", 2500), ("tujuh puluh lima", 75),
        ]:
            assert _kata_jadi_angka(kata) == angka, kata

    def test_kata_asing_mengembalikan_none(self):
        assert _kata_jadi_angka("dua orang") is None
        assert _kata_jadi_angka("") is None


class TestPengaturanPenelaah:
    def test_aturan_yang_tidak_dicentang_tidak_jalan(self):
        baris = [
            "Pasal 1", "Ketentuan sebagaimana dimaksud dalam Pasal 30 berlaku "
            "paling lambat 30 (tiga belas) hari.",
        ]
        assert _kode(_jalan(baris, ["F2-001"])) == ["F2-001"]
        assert _kode(_jalan(baris, ["F2-007"])) == ["F2-007"]
        assert _jalan(baris, []) == []
        assert _kode(_jalan(baris)) == ["F2-001", "F2-007"]


class TestKaidahWarisanFase1:
    def test_pohon_gagal_tidak_menghasilkan_temuan(self):
        doc = [ParagrafInput(index=i, teks=f"baris {i}") for i in range(40)]
        pohon = bangun_pohon(doc)
        assert pohon.gagal is not None
        assert jalankan_mekanis(pohon, ambil_definisi(pohon), doc) == []

    def test_tiap_temuan_punya_teks_asli_yang_ada_persis_di_naskah(self):
        baris = [
            "Pasal 1", "Ketentuan sebagaimana dimaksud dalam Pasal 30 berlaku.",
            "Pasal 3", "Diselesaikan dalam 7 (delapan) hari.",
        ]
        doc = [ParagrafInput(index=i, teks=t) for i, t in enumerate(_KEPALA + baris)]
        for t in _jalan(baris):
            assert t.lokasi.teks_asli
            asli = doc[t.lokasi.paragraf_index].teks
            potong = asli[t.lokasi.offset_mulai : t.lokasi.offset_mulai + t.lokasi.panjang]
            assert potong == t.lokasi.teks_asli
