"""Tes pembaca rujukan internal — Fase 2 Langkah 0.

Regresi PMK 45 Tahun 2026, 27 Sep 2026 (docs/perbaiki bug.md bug 1): rujukan
"Pasal 3 ayat (1) huruf b" dulu hanya dicocokkan sampai ayat, dan rujukan di
pasal yang sama ("pada ayat (1) huruf b") tidak dicari sama sekali.
"""

from app.models.temuan import ParagrafInput
from app.telaah.tahap1_parser.rujukan import (
    baca_rujukan,
    baris_dirujuk,
    blok_dirujuk,
    frasa_rujukan_saja,
    satuan_dirujuk,
)
from app.telaah.tahap1_parser.struktur import bangun_pohon

_BARIS = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 45 TAHUN 2026",
    "TENTANG",
    "PEMBEBASAN BEA MASUK",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG PEMBEBASAN BEA MASUK.",
    "Pasal 3",
    "(1) Barang sebagaimana dimaksud dalam Pasal 2 merupakan barang yang:",
    "a. digunakan bagi keperluan pertahanan oleh:",
    "1. Lembaga Kepresidenan;",
    "2. Kementerian Pertahanan; dan/atau",
    "b. digunakan dalam kegiatan militer bersama.",
    "Pasal 4",
    "(1) Impor barang dilakukan oleh:",
    "a. Kementerian/Lembaga; atau",
    "b. Pihak Ketiga.",
    "(2) Impor barang dan bahan dilakukan oleh Industri Tertentu.",
    "(3) Impor barang sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf b "
    "dikecualikan dari ketentuan sebagaimana dimaksud pada ayat (1) huruf b.",
]


def _pohon():
    return bangun_pohon([ParagrafInput(index=i, teks=t) for i, t in enumerate(_BARIS)])


def _id(rujukan):
    return [r.id_sasaran for r in rujukan]


class TestBacaRujukan:
    def test_sampai_tingkat_huruf(self):
        pohon = _pohon()
        r = baca_rujukan(pohon.cari("pasal-4-ayat-3").teks, "pasal-4-ayat-3", pohon)
        assert _id(r) == ["pasal-3-ayat-1-huruf-b", "pasal-4-ayat-1-huruf-b"]
        assert all(x.tepat for x in r)

    def test_rujukan_di_pasal_yang_sama_dilengkapi_dari_letaknya(self):
        pohon = _pohon()
        r = baca_rujukan("sebagaimana dimaksud pada ayat (2)", "pasal-4-ayat-3", pohon)
        assert _id(r) == ["pasal-4-ayat-2"]

    def test_daftar_rujukan_dipecah(self):
        pohon = _pohon()
        r = baca_rujukan(
            "sebagaimana dimaksud pada ayat (1) dan ayat (2)", "pasal-4-ayat-3", pohon
        )
        assert _id(r) == ["pasal-4-ayat-1", "pasal-4-ayat-2"]

    def test_unsur_atas_diwarisi_dalam_daftar(self):
        pohon = _pohon()
        r = baca_rujukan(
            "sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf a dan huruf b", "pasal-4-ayat-3", pohon
        )
        assert _id(r) == ["pasal-3-ayat-1-huruf-a", "pasal-3-ayat-1-huruf-b"]

    def test_sampai_tingkat_angka_di_bawah_huruf(self):
        pohon = _pohon()
        r = baca_rujukan(
            "sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf a angka 2", "pasal-4-ayat-3", pohon
        )
        assert _id(r) == ["pasal-3-ayat-1-huruf-a-angka-2"] and r[0].tepat

    def test_alamat_yang_tidak_ada_menunjuk_induk_terdekatnya(self):
        """Huruf c tidak ada → yang dilampirkan ayat (1), dan itu dikatakan."""
        pohon = _pohon()
        r = baca_rujukan(
            "sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf c", "pasal-4-ayat-3", pohon
        )
        assert not r[0].tepat and r[0].satuan.id == "pasal-3-ayat-1"
        assert "TIDAK ADA di naskah" in baris_dirujuk(r[0], pohon)

    def test_rujukan_ke_peraturan_lain_bukan_rujukan_internal(self):
        pohon = _pohon()
        teks = (
            "sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf h dan i Undang-Undang "
            "Nomor 17 Tahun 2006 tentang Kepabeanan"
        )
        assert baca_rujukan(teks, "pasal-4-ayat-3", pohon) == []

    def test_peraturan_menteri_ini_tetap_rujukan_internal(self):
        pohon = _pohon()
        teks = "sebagaimana dimaksud dalam Pasal 3 Peraturan Menteri ini"
        assert _id(baca_rujukan(teks, "pasal-4-ayat-3", pohon)) == ["pasal-3"]

    def test_lampiran_untuk_model_berlabel(self):
        pohon = _pohon()
        r = baca_rujukan(pohon.cari("pasal-4-ayat-3").teks, "pasal-4-ayat-3", pohon)
        baris = baris_dirujuk(r[0], pohon)
        assert baris.startswith("[pasal-3-ayat-1-huruf-b]")
        assert "b. digunakan dalam kegiatan militer" in baris
        assert "(1) Barang" in baris


class TestFrasaRujukanSaja:
    def test_alamat_telanjang(self):
        pohon = _pohon()
        r = frasa_rujukan_saja("Pasal 3 ayat (1) huruf b", "pasal-4-ayat-3", pohon)
        assert _id(r) == ["pasal-3-ayat-1-huruf-b"]

    def test_dengan_pembukanya(self):
        pohon = _pohon()
        r = frasa_rujukan_saja(
            "sebagaimana dimaksud dalam Pasal 3 ayat (1) huruf b", "pasal-4-ayat-3", pohon
        )
        assert _id(r) == ["pasal-3-ayat-1-huruf-b"]

    def test_kata_lain_di_luar_alamat_bukan_rujukan_saja(self):
        pohon = _pohon()
        assert frasa_rujukan_saja(
            "Impor barang sebagaimana dimaksud dalam Pasal 3", "pasal-4-ayat-3", pohon
        ) == []
        assert frasa_rujukan_saja(
            "atas permohonan sebagaimana dimaksud pada ayat (1)", "pasal-4-ayat-3", pohon
        ) == []


class TestSatuanDirujuk:
    """Pindah dari tahap2_baca yang dihapus (bug 7) — perilakunya tetap."""

    def test_satuan_yang_dirujuk_ada(self):
        pohon = _pohon()
        dirujuk = satuan_dirujuk(pohon.cari("pasal-4-ayat-3"), pohon)
        assert [s.id for s in dirujuk] == ["pasal-3-ayat-1-huruf-b", "pasal-4-ayat-1-huruf-b"]

    def test_rujukan_ke_pasal_yang_tidak_ada_tidak_dilampirkan_sebagai_satuan(self):
        baris = _BARIS + ["Pasal 5", "Hal sebagaimana dimaksud dalam Pasal 99 berlaku."]
        pohon = bangun_pohon([ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)])
        assert satuan_dirujuk(pohon.cari("pasal-5"), pohon) == []

    def test_blok_dirujuk_menyebut_alamat_yang_tidak_ada(self):
        baris = _BARIS + ["Pasal 5", "Hal sebagaimana dimaksud dalam Pasal 99 berlaku."]
        pohon = bangun_pohon([ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)])
        blok = blok_dirujuk([pohon.cari("pasal-5")], pohon)
        assert "[pasal-99] TIDAK ADA di naskah." in blok
