"""F3-002 — dasar hukum di Mengingat yang sudah dicabut. TANPA jaringan.

Aturan paling rawan di seluruh alat: mengatakan dasar hukum penelaah sudah
dicabut padahal masih berlaku membuat penelaah mengubah bagian Mengingat yang
sebenarnya sudah benar. Karena itu sebagian besar tes di sini membuktikan
aturannya MEMILIH DIAM, bukan membuktikan ia menemukan sesuatu.
"""

from app.bersama.opensearch import (
    Kutipan,
    PencariPalsu,
    StatusPeraturan,
    baca_kutipan,
    baca_nomor_korpus,
    baca_status_peraturan,
)
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase3.tahap6_dasar_hukum import cek_dasar_hukum
from app.models.temuan import ParagrafInput

_KEPALA = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
]
_EKOR = [
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
    "Pasal 1",
    "Isi pasal satu.",
]

_UU17 = "1. Undang-Undang Nomor 17 Tahun 2003 tentang Keuangan Negara;"
_PP45 = "2. Peraturan Pemerintah Nomor 45 Tahun 2013 tentang Tata Cara Pelaksanaan APBN;"


def _naskah(butir_mengingat):
    baris = _KEPALA + ["Mengingat :"] + butir_mengingat + _EKOR
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]


def _jalan(butir_mengingat, jawaban):
    par = _naskah(butir_mengingat)
    return cek_dasar_hukum(bangun_pohon(par), par, PencariPalsu(jawaban))


class TestBacaKutipan:
    def test_bentuk_tahun_terpisah(self):
        k = baca_kutipan("Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan")
        assert (k.bentuk, k.nomor, k.tahun) == ("UU", 1, 2004)

    def test_bentuk_bergaris_miring(self):
        k = baca_kutipan("Peraturan Menteri Keuangan Nomor 246/PMK.06/2014 tentang X")
        assert (k.bentuk, k.nomor, k.tahun) == ("PMK", 246, 2014)

    def test_perppu_tidak_terbaca_sebagai_pp(self):
        """Bentuk yang TERPANJANG harus dicocokkan lebih dulu."""
        k = baca_kutipan(
            "Peraturan Pemerintah Pengganti Undang-Undang Nomor 1 Tahun 2020 tentang X"
        )
        assert k.bentuk == "PERPPU"

    def test_bentuk_di_luar_cakupan_DILEWATI(self):
        assert baca_kutipan("Ketetapan MPR Nomor 1 Tahun 2003 tentang X") is None
        assert baca_kutipan("Peraturan Daerah Nomor 5 Tahun 2019 tentang X") is None

    def test_pasal_uud_bukan_kutipan_peraturan(self):
        assert baca_kutipan("Pasal 17 ayat (3) Undang-Undang Dasar Tahun 1945;") is None


class TestBacaNomorKorpus:
    """Medan Nomor di korpus bentuknya lima macam. Semuanya harus terbaca."""

    def test_berspasi(self):
        assert baca_nomor_korpus("UU 1 TAHUN 2004", 2004.0) == (1, 2004)

    def test_tanpa_spasi(self):
        assert baca_nomor_korpus("UU 17TAHUN2003", 2003) == (17, 2003)

    def test_bergaris_miring(self):
        assert baca_nomor_korpus("61/PMK.03/2022", 2022) == (61, 2022)

    def test_spasi_nyasar(self):
        assert baca_nomor_korpus("PMK 246 /PMK.06/2014", 2014.0) == (246, 2014)

    def test_tak_terbaca_jadi_none(self):
        assert baca_nomor_korpus("", None) is None
        assert baca_nomor_korpus("tanpa angka", None) is None


class TestBacaStatusPeraturan:
    _K = Kutipan(bentuk="UU", bentuk_indeks="Undang-Undang", nomor=1, tahun=2004)

    def _jwb(self, *sumber):
        return {"hits": {"hits": [{"_source": s} for s in sumber]}}

    def test_cocok_tunggal_berlaku(self):
        s = baca_status_peraturan(
            self._jwb(
                {
                    "Nomor": "UU 1 TAHUN 2004",
                    "Tahun": 2004.0,
                    "Status": "Berlaku",
                    "Judul": "Perbendaharaan Negara",
                }
            ),
            self._K,
        )
        assert s.berlaku is True

    def test_cocok_tunggal_dicabut(self):
        s = baca_status_peraturan(
            self._jwb(
                {"Nomor": "UU 1 TAHUN 2004", "Tahun": 2004, "Status": "Tidak Berlaku", "Judul": "X"}
            ),
            self._K,
        )
        assert s.berlaku is False

    def test_DIAM_kalau_tidak_ketemu(self):
        """Korpus tidak memuat segalanya. Tidak ketemu BUKAN bukti dicabut."""
        s = baca_status_peraturan(
            self._jwb({"Nomor": "UU 9 TAHUN 2004", "Tahun": 2004, "Status": "Berlaku"}),
            self._K,
        )
        assert s.berlaku is None
        assert "tidak ditemukan" in s.alasan

    def test_DIAM_kalau_cocok_ganda_berstatus_beda(self):
        s = baca_status_peraturan(
            self._jwb(
                {"Nomor": "UU 1 TAHUN 2004", "Tahun": 2004, "Status": "Berlaku"},
                {"Nomor": "UU 1TAHUN2004", "Tahun": 2004, "Status": "Tidak Berlaku"},
            ),
            self._K,
        )
        assert s.berlaku is None
        assert "statusnya berbeda" in s.alasan

    def test_DIAM_kalau_status_di_luar_yang_dikenal(self):
        s = baca_status_peraturan(
            self._jwb({"Nomor": "UU 1 TAHUN 2004", "Tahun": 2004, "Status": "Tetap"}),
            self._K,
        )
        assert s.berlaku is None


class TestAturanF3002:
    def test_dasar_hukum_dicabut_ditandai(self):
        t, _ = _jalan(
            [_UU17, _PP45],
            {
                "PP 45/2013": StatusPeraturan(
                    kutipan="PP 45/2013",
                    berlaku=False,
                    judul="Tata Cara Pelaksanaan APBN",
                    nomor="PP 45 TAHUN 2013",
                )
            },
        )
        assert len(t) == 1
        assert t[0].aturan_id == "F3-002"
        assert t[0].fase == 3
        assert "Tidak Berlaku" in t[0].catatan

    def test_yang_ditandai_sebutan_peraturannya_BUKAN_seluruh_butir(self):
        t, _ = _jalan(
            [_PP45],
            {"PP 45/2013": StatusPeraturan(kutipan="PP 45/2013", berlaku=False, nomor="PP 45 TAHUN 2013")},
        )
        assert t[0].lokasi.teks_asli == "Peraturan Pemerintah Nomor 45 Tahun 2013"
        assert "Lembaran" not in t[0].lokasi.teks_asli

    def test_saran_meminta_penelaah_memastikan_sendiri(self):
        """Status di korpus bisa tertinggal dari keadaan sebenarnya."""
        t, _ = _jalan(
            [_PP45],
            {"PP 45/2013": StatusPeraturan(kutipan="PP 45/2013", berlaku=False, nomor="PP 45")},
        )
        assert "pastikan" in t[0].saran.lower()

    def test_yang_masih_berlaku_TIDAK_ditandai(self):
        t, _ = _jalan([_UU17], {"UU 17/2003": StatusPeraturan(kutipan="UU 17/2003", berlaku=True)})
        assert t == []

    def test_yang_tidak_diketahui_TIDAK_ditandai_tetapi_dicatat(self):
        t, lewat = _jalan([_UU17], {})
        assert t == []
        assert any("UU 17/2003" in x for x in lewat)

    def test_tanpa_pencari_tidak_jalan_dan_menyebutkan_alasannya(self):
        par = _naskah([_UU17])
        t, lewat = cek_dasar_hukum(bangun_pohon(par), par, None)
        assert t == []
        assert "tidak tersedia" in lewat[0]

    def test_tanpa_mengingat_diam_dan_menyebutkan_alasannya(self):
        par = [ParagrafInput(index=i, teks=x) for i, x in enumerate(_KEPALA + _EKOR)]
        t, lewat = cek_dasar_hukum(bangun_pohon(par), par, PencariPalsu({}))
        assert t == []
        assert "tidak ada butir Mengingat" in lewat[0]

    def test_mengingat_kelewat_panjang_diam(self):
        """Batas kewajaran: Mengingat sepanjang itu pertanda salah baca."""
        butir = [f"{i}. Undang-Undang Nomor {i} Tahun 2003 tentang X;" for i in range(1, 60)]
        t, lewat = _jalan(butir, {})
        assert t == []
        assert "melebihi batas kewajaran" in lewat[0]

    def test_korpus_tidak_ditanyai_untuk_bentuk_yang_tak_dikenali(self):
        par = _naskah(["1. Ketetapan MPR Nomor 1 Tahun 2003 tentang X;"])
        pencari = PencariPalsu({})
        cek_dasar_hukum(bangun_pohon(par), par, pencari)
        assert pencari.diminta == []
