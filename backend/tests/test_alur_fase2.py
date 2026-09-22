"""Tes jalur penalaran Fase 2 dan Fase 3 — Langkah 2, 3, 4, 5, 6.

SELURUHNYA MEMAKAI KlienPalsu DAN KorpusPalsu. Tidak ada jaringan, tidak ada
kredensial, tidak ada biaya. Yang diuji bukan kecerdasan modelnya melainkan
apa yang terjadi pada JAWABAN model — termasuk jawaban yang mengarang, yang
rusak, dan yang di luar pertanyaan.

Yang paling penting di berkas ini tes-tes bertanda NEGATIF: membuktikan bahwa
jawaban model yang salah TIDAK sampai ke naskah.
"""

import json

from app.bersama.llm import KlienPalsu, Ongkos, PerapalPalsu
from app.bersama.opensearch import HasilCari, KorpusPalsu, Pembanding, saring_status
from app.fase2 import tahap2_baca, tahap3_menalar, tahap4_memastikan, tahap5_verifikasi
from app.fase2.alur import jalankan_lanjut
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import saring
from app.fase3 import tahap6_cari, tahap6_pastikan_ulang
from app.models.pekerjaan import BarisPeta, CalonTemuan, Dugaan
from app.models.temuan import JenisTanda, ParagrafInput

_KEPALA = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "Menimbang :",
    "a. bahwa untuk melaksanakan ketentuan Pasal 5 Peraturan Pemerintah;",
    "Mengingat :",
    "1. Undang-Undang Nomor 1 Tahun 2004 tentang Perbendaharaan;",
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
]

_BATANG = [
    "Pasal 1",
    "Dalam Peraturan Menteri ini yang dimaksud dengan:",
    "1. Pengelola Barang adalah pejabat yang berwenang menetapkan status penggunaan.",
    "2. Pengguna Barang adalah pejabat pemegang kewenangan penggunaan barang.",
    "Pasal 2",
    "Pengguna Barang wajib mengajukan permohonan paling lambat 30 (tiga puluh) hari.",
    "Pasal 3",
    "Permohonan sebagaimana dimaksud dalam Pasal 2 dapat disampaikan secara elektronik kepada Pengelola Barang.",
]


def _naskah(tambahan=None):
    baris = _KEPALA + _BATANG + (tambahan or [])
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]


def _siapkan(tambahan=None):
    paragraf = _naskah(tambahan)
    pohon = bangun_pohon(paragraf)
    daftar = ambil_definisi(pohon)
    return paragraf, pohon, daftar


def _js(obj):
    return json.dumps(obj, ensure_ascii=False)


# ===========================================================================
# LANGKAH 2 — membaca per satuan
# ===========================================================================


class TestKonteksTetap:
    def test_memuat_judul_menimbang_mengingat_definisi_dan_kerangka(self):
        _, pohon, daftar = _siapkan()
        konteks = tahap2_baca.susun_konteks_tetap(pohon, daftar)
        assert "Menimbang:" in konteks
        assert "Mengingat:" in konteks
        assert "Pengelola Barang" in konteks
        assert "Kerangka pasal:" in konteks

    def test_konteks_sama_persis_di_tiap_panggilan(self):
        """Yang membuat potongan harga awalan prompt mungkin berlaku."""
        _, pohon, daftar = _siapkan()
        klien = KlienPalsu(['{"baris": []}'] * 5)
        disaring = saring(pohon)
        tahap2_baca.baca_satuan(
            pohon, daftar, disaring.dibaca, klien, Ongkos(), per_panggilan=1
        )
        assert len(klien.diminta) >= 2
        awalan = [pesan.split("== SATUAN YANG DIPERIKSA ==")[0] for _, pesan in klien.diminta]
        assert len(set(awalan)) == 1


class TestSatuanDirujuk:
    def test_satuan_yang_dirujuk_ikut_dilampirkan(self):
        _, pohon, daftar = _siapkan()
        pasal3 = pohon.cari("pasal-3")
        dirujuk = tahap2_baca.satuan_dirujuk(pasal3, pohon)
        assert [s.id for s in dirujuk] == ["pasal-2"]

    def test_rujukan_ke_pasal_yang_tidak_ada_tidak_melampirkan_apa_pun(self):
        _, pohon, _ = _siapkan(
            ["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 99 berlaku."]
        )
        assert tahap2_baca.satuan_dirujuk(pohon.cari("pasal-4"), pohon) == []


class TestKelompokkan:
    def test_tidak_pernah_membelah_satu_pasal(self):
        _, pohon, _ = _siapkan(
            [
                "Pasal 4",
                "(1) Ayat satu.",
                "(2) Ayat dua.",
                "(3) Ayat tiga.",
                "(4) Ayat empat.",
            ]
        )
        semua = saring(pohon).dibaca
        for kelompok in tahap2_baca.kelompokkan(semua, per_panggilan=2):
            pasal = {tahap2_baca._pasal_induk(s) for s in kelompok}
            # Sebuah kelompok boleh memuat beberapa pasal, tetapi tiap pasal
            # harus utuh di dalam satu kelompok saja.
            for p in pasal:
                jumlah_di_sini = sum(1 for s in kelompok if tahap2_baca._pasal_induk(s) == p)
                jumlah_total = sum(1 for s in semua if tahap2_baca._pasal_induk(s) == p)
                assert jumlah_di_sini == jumlah_total

    def test_kelompok_kosong_aman(self):
        assert tahap2_baca.kelompokkan([], 5) == []


class TestBacaSatuan:
    def test_baris_peta_terbentuk(self):
        paragraf, pohon, daftar = _siapkan()
        disaring = saring(pohon)
        sid = disaring.dibaca[0].id
        klien = KlienPalsu(
            [
                _js(
                    {
                        "baris": [
                            {
                                "satuan_id": sid,
                                "ringkasan": "mengatur permohonan",
                                "memuat_norma": True,
                                "istilah_dipakai": ["Pengguna Barang"],
                                "dugaan": "",
                            }
                        ]
                    }
                )
            ]
            * 10
        )
        peta = tahap2_baca.baca_satuan(pohon, daftar, disaring.dibaca, klien, Ongkos())
        assert any(b.satuan_id == sid for b in peta)

    def test_NEGATIF_satuan_id_karangan_dibuang(self):
        paragraf, pohon, daftar = _siapkan()
        disaring = saring(pohon)
        klien = KlienPalsu(
            [_js({"baris": [{"satuan_id": "pasal-999", "ringkasan": "karangan"}]})] * 10
        )
        peta = tahap2_baca.baca_satuan(pohon, daftar, disaring.dibaca, klien, Ongkos())
        assert peta == []

    def test_NEGATIF_jawaban_rusak_dilewati_analisis_tetap_jalan(self):
        paragraf, pohon, daftar = _siapkan()
        disaring = saring(pohon)
        sid = disaring.dibaca[-1].id
        jawaban = ["bukan json sama sekali"] * 20
        jawaban[-1] = _js({"baris": [{"satuan_id": sid, "ringkasan": "terakhir"}]})
        klien = KlienPalsu(jawaban)
        ongkos = Ongkos()
        # per_panggilan=1 supaya tiap satuan jadi satu panggilan sendiri
        peta = tahap2_baca.baca_satuan(
            pohon, daftar, disaring.dibaca, klien, ongkos, per_panggilan=1
        )
        assert ongkos.gagal >= 1
        assert ongkos.panggilan == len(klien.diminta)

    def test_jawaban_berpagar_json_tetap_terbaca(self):
        paragraf, pohon, daftar = _siapkan()
        disaring = saring(pohon)
        sid = disaring.dibaca[0].id
        isi = _js({"baris": [{"satuan_id": sid, "ringkasan": "ada"}]})
        klien = KlienPalsu(["```json\n" + isi + "\n```"] * 10)
        peta = tahap2_baca.baca_satuan(pohon, daftar, disaring.dibaca, klien, Ongkos())
        assert any(b.satuan_id == sid for b in peta)


# ===========================================================================
# LANGKAH 3 — menalar di atas peta
# ===========================================================================


class TestMenalar:
    def _peta(self):
        return [
            BarisPeta(satuan_id="pasal-2", ringkasan="kewajiban mengajukan"),
            BarisPeta(satuan_id="pasal-3", ringkasan="boleh elektronik"),
        ]

    def test_dugaan_sah_diteruskan(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "dugaan": [
                            {
                                "satuan_id": "pasal-2",
                                "satuan_lain": "",
                                "jenis": "operasional",
                                "alasan": "wajib dan dapat bertabrakan",
                                "eksternal": False,
                            }
                        ]
                    }
                )
            ]
        )
        d = tahap3_menalar.menalar(self._peta(), pohon, "konteks", klien, Ongkos())
        assert len(d) == 1
        assert d[0].jenis == "operasional"
        assert not d[0].tabrakan

    def test_NEGATIF_satuan_di_luar_peta_dibuang(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [_js({"dugaan": [{"satuan_id": "pasal-99", "jenis": "pemikul", "alasan": "x"}]})]
        )
        assert tahap3_menalar.menalar(self._peta(), pohon, "k", klien, Ongkos()) == []

    def test_NEGATIF_tabrakan_dengan_satuan_di_luar_peta_digugurkan(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "dugaan": [
                            {
                                "satuan_id": "pasal-2",
                                "satuan_lain": "pasal-77",
                                "jenis": "tabrakan",
                                "alasan": "x",
                            }
                        ]
                    }
                )
            ]
        )
        assert tahap3_menalar.menalar(self._peta(), pohon, "k", klien, Ongkos()) == []

    def test_NEGATIF_jenis_karangan_dibuang(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [_js({"dugaan": [{"satuan_id": "pasal-2", "jenis": "aneh", "alasan": "x"}]})]
        )
        assert tahap3_menalar.menalar(self._peta(), pohon, "k", klien, Ongkos()) == []

    def test_NEGATIF_alasan_kosong_dibuang(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [_js({"dugaan": [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "  "}]})]
        )
        assert tahap3_menalar.menalar(self._peta(), pohon, "k", klien, Ongkos()) == []

    def test_peta_kosong_tidak_memanggil_model(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(["{}"])
        assert tahap3_menalar.menalar([], pohon, "k", klien, Ongkos()) == []
        assert klien.diminta == []

    def test_batas_kewajaran_memotong_dugaan_berlebihan(self):
        _, pohon, _ = _siapkan()
        banyak = [
            {"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": f"alasan {i}"}
            for i in range(200)
        ]
        klien = KlienPalsu([_js({"dugaan": banyak})])
        d = tahap3_menalar.menalar(self._peta(), pohon, "k", klien, Ongkos())
        assert len(d) == tahap3_menalar._BATAS_DUGAAN


# ===========================================================================
# LANGKAH 4 — memastikan pada teks utuh
# ===========================================================================


class TestMemastikan:
    def test_dugaan_terbukti_jadi_calon(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "terbukti": True,
                        "alasan": "tidak jelas siapa yang wajib",
                        "teks_asli": "wajib mengajukan permohonan",
                        "saran": "sebutkan subjeknya",
                        "usulan_rumusan": "",
                        "skor": 0.9,
                    }
                )
            ]
        )
        d = Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")
        calon = tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos())
        assert len(calon) == 1
        assert calon[0].aturan_id == "F2-102"

    def test_dugaan_gugur_tidak_jadi_apa_apa(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu([_js({"terbukti": False, "alasan": "ternyata jelas"})])
        d = Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")
        assert tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos()) == []

    def test_NEGATIF_terbukti_tanpa_teks_asli_digugurkan(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu([_js({"terbukti": True, "alasan": "ada", "teks_asli": "", "skor": 1})])
        d = Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")
        assert tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos()) == []

    def test_tabrakan_mengirim_KEDUA_teks_utuh_dalam_satu_panggilan(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "terbukti": True,
                        "satuan_ditandai": "pasal-3",
                        "alasan": "Pasal 2 dan Pasal 3 tidak bisa berlaku bersamaan",
                        "teks_asli": "dapat disampaikan secara elektronik",
                        "saran": "selaraskan",
                        "skor": 0.85,
                    }
                )
            ]
        )
        d = Dugaan(satuan_id="pasal-2", satuan_lain="pasal-3", jenis="tabrakan", alasan="x")
        calon = tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos())
        assert len(calon) == 1
        assert calon[0].aturan_id == "F2-104"
        assert calon[0].satuan_id == "pasal-3"
        assert calon[0].satuan_lain == "pasal-2"
        pesan = klien.diminta[0][1]
        assert "wajib mengajukan permohonan" in pesan
        assert "dapat disampaikan secara elektronik" in pesan

    def test_NEGATIF_tabrakan_menunjuk_satuan_di_luar_dua_yang_dikirim(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "terbukti": True,
                        "satuan_ditandai": "pasal-1",
                        "alasan": "x",
                        "teks_asli": "y",
                        "skor": 1,
                    }
                )
            ]
        )
        d = Dugaan(satuan_id="pasal-2", satuan_lain="pasal-3", jenis="tabrakan", alasan="x")
        assert tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos()) == []

    def test_aturan_dimatikan_penelaah_tidak_dipanggil(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(["{}"])
        d = Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")
        assert tahap4_memastikan.memastikan([d], pohon, "k", klien, Ongkos(), {"F2-101"}) == []
        assert klien.diminta == []


# ===========================================================================
# LANGKAH 5 — gerbang terakhir
# ===========================================================================


class TestVerifikasi:
    def _calon(self, **ganti):
        dasar = dict(
            aturan_id="F2-102",
            satuan_id="pasal-2",
            alasan="tidak jelas siapa pemikulnya",
            teks_asli="wajib mengajukan permohonan",
            saran="sebutkan subjeknya",
            skor=0.9,
        )
        dasar.update(ganti)
        return CalonTemuan(**dasar)

    def _jalan(self, calon, ambang=0.7, tambahan=None):
        paragraf, pohon, daftar = _siapkan(tambahan)
        return tahap5_verifikasi.verifikasi([calon], pohon, daftar, paragraf, ambang)

    def test_calon_sehat_jadi_temuan(self):
        lolos, gugur = self._jalan(self._calon())
        assert len(lolos) == 1
        assert lolos[0].fase == 2
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert lolos[0].lokasi.teks_asli == "wajib mengajukan permohonan"

    def test_lokasi_menunjuk_rentang_yang_sempit_bukan_satu_paragraf(self):
        lolos, _ = self._jalan(self._calon())
        t = lolos[0]
        assert t.lokasi.panjang == len("wajib mengajukan permohonan")
        assert t.lokasi.offset_mulai > 0

    def test_GUGUR_kutipan_tidak_ada_di_naskah(self):
        lolos, gugur = self._jalan(self._calon(teks_asli="kalimat yang tidak pernah ditulis"))
        assert lolos == []
        assert "kutipan tidak ketemu" in gugur[0]

    def test_GUGUR_kutipan_diparafrase_model(self):
        """Kutipan yang 'dirapikan' model tetap gugur — beda satu kata cukup."""
        lolos, _ = self._jalan(self._calon(teks_asli="wajib mengajukan Permohonan"))
        assert lolos == []

    def test_GUGUR_menyebut_pasal_yang_tidak_ada(self):
        lolos, gugur = self._jalan(
            self._calon(alasan="bertentangan dengan Pasal 40 peraturan ini")
        )
        assert lolos == []
        assert "Pasal yang tidak ada" in gugur[0]

    def test_pasal_milik_peraturan_LAIN_tidak_dianggap_karangan(self):
        lolos, _ = self._jalan(
            self._calon(alasan="mengikuti Pasal 45 Undang-Undang Nomor 1 Tahun 2004")
        )
        assert len(lolos) == 1

    def test_GUGUR_skor_di_bawah_ambang(self):
        lolos, gugur = self._jalan(self._calon(skor=0.5))
        assert lolos == []
        assert "di bawah ambang" in gugur[0]

    def test_usulan_harfiah_jadi_penggantian_hijau(self):
        lolos, _ = self._jalan(
            self._calon(usulan_rumusan="wajib mengajukan permohonan kepada Pengelola Barang")
        )
        assert lolos[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert lolos[0].usulan_rumusan

    def test_DITURUNKAN_usulan_berupa_penjelasan_bukan_pengganti(self):
        lolos, gugur = self._jalan(
            self._calon(usulan_rumusan="Sebaiknya subjeknya disebutkan secara tegas")
        )
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert "DITURUNKAN" in gugur[0]

    def test_DITURUNKAN_istilah_berdefinisi_salah_eja_di_usulan(self):
        lolos, gugur = self._jalan(
            self._calon(usulan_rumusan="wajib mengajukan permohonan kepada Pengeloa Barang")
        )
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert "salah eja" in gugur[0]

    def test_saran_ikut_terbaca_penelaah_di_catatan(self):
        lolos, _ = self._jalan(self._calon())
        assert "Saran:" in lolos[0].catatan

    def test_GUGUR_pembanding_fase3_di_luar_hasil_pencarian(self):
        paragraf, pohon, daftar = _siapkan()
        calon = self._calon(aturan_id="F3-001", pembanding="PMK yang tidak dicari")
        lolos, gugur = tahap5_verifikasi.verifikasi(
            [calon], pohon, daftar, paragraf, 0.7, {"PMK 1/2020"}
        )
        assert lolos == []
        assert "pembanding tidak ada" in gugur[0]

    def test_temuan_fase3_bernomor_fase_3(self):
        paragraf, pohon, daftar = _siapkan()
        calon = self._calon(aturan_id="F3-001", pembanding="PMK 1/2020")
        lolos, _ = tahap5_verifikasi.verifikasi(
            [calon], pohon, daftar, paragraf, 0.7, {"PMK 1/2020"}
        )
        assert lolos[0].fase == 3


class TestUsulanHarfiah:
    def test_usulan_jauh_lebih_panjang_ditolak(self):
        assert not tahap5_verifikasi.usulan_harfiah("x" * 500, "pendek")

    def test_usulan_sama_persis_ditolak(self):
        assert not tahap5_verifikasi.usulan_harfiah("sama", "sama")

    def test_usulan_kosong_ditolak(self):
        assert not tahap5_verifikasi.usulan_harfiah("", "apa pun")

    def test_pengganti_wajar_diterima(self):
        assert tahap5_verifikasi.usulan_harfiah(
            "Pengguna Barang wajib mengajukan", "wajib mengajukan"
        )


# ===========================================================================
# LANGKAH 6 — Fase 3
# ===========================================================================


class TestSaringStatus:
    def test_berlaku(self):
        assert saring_status("Berlaku") is True

    def test_dicabut(self):
        assert saring_status("Dicabut") is False

    def test_kosong_tidak_terbaca(self):
        assert saring_status("") is None

    def test_nilai_asing_tidak_terbaca(self):
        assert saring_status("entah") is None


class TestPastikanUlang:
    def _hasil(self):
        return HasilCari(
            pembanding=[
                Pembanding(judul="PMK 1/2020", potongan="ketentuan lain", status="berlaku")
            ]
        )

    def _calon(self):
        return CalonTemuan(
            aturan_id="F2-101",
            satuan_id="pasal-2",
            alasan="mungkin bersinggungan",
            teks_asli="wajib mengajukan permohonan",
            eksternal=True,
            skor=0.9,
        )

    def test_tanpa_pembanding_model_TIDAK_dipanggil(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(["{}"])
        assert (
            tahap6_pastikan_ulang.pastikan_ulang(
                self._calon(), pohon, HasilCari(), klien, Ongkos()
            )
            is None
        )
        assert klien.diminta == []

    def test_terbukti_jadi_calon_f3(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "terbukti": True,
                        "peraturan": "PMK 1/2020",
                        "alasan": "berpotensi bertentangan dengan PMK 1/2020",
                        "teks_asli": "wajib mengajukan permohonan",
                        "saran": "periksa",
                        "skor": 0.8,
                    }
                )
            ]
        )
        calon = tahap6_pastikan_ulang.pastikan_ulang(
            self._calon(), pohon, self._hasil(), klien, Ongkos()
        )
        assert calon is not None
        assert calon.aturan_id == "F3-001"
        assert calon.pembanding == "PMK 1/2020"

    def test_NEGATIF_bahasa_bertentangan_tanpa_berpotensi_digugurkan(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu(
            [
                _js(
                    {
                        "terbukti": True,
                        "peraturan": "PMK 1/2020",
                        "alasan": "bertentangan dengan PMK 1/2020",
                        "teks_asli": "wajib mengajukan permohonan",
                        "skor": 0.9,
                    }
                )
            ]
        )
        assert (
            tahap6_pastikan_ulang.pastikan_ulang(
                self._calon(), pohon, self._hasil(), klien, Ongkos()
            )
            is None
        )

    def test_daftar_pembanding_ikut_dikirim_ke_model(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu([_js({"terbukti": False})])
        tahap6_pastikan_ulang.pastikan_ulang(
            self._calon(), pohon, self._hasil(), klien, Ongkos()
        )
        assert "PMK 1/2020" in klien.diminta[0][1]
        assert "hanya ini yang boleh kamu sebut" in klien.diminta[0][1]


class TestCariPembanding:
    def test_kueri_menaruh_kutipan_di_depan(self):
        _, pohon, _ = _siapkan()
        calon = CalonTemuan(
            aturan_id="F2-101", satuan_id="pasal-2", teks_asli="wajib mengajukan"
        )
        assert tahap6_cari.susun_kueri(calon, pohon).startswith("wajib mengajukan")

    def test_embedding_gagal_tetap_mencoba_pencarian_teks(self):
        _, pohon, _ = _siapkan()

        class PerapalRusak:
            def rapalkan(self, teks):
                raise RuntimeError("deployment mati")

        korpus = KorpusPalsu(
            [HasilCari(pembanding=[Pembanding(judul="PMK 9/2021", potongan="x", status="berlaku")])]
        )
        calon = CalonTemuan(
            aturan_id="F2-101", satuan_id="pasal-2", teks_asli="wajib mengajukan"
        )
        hasil = tahap6_cari.cari_pembanding(calon, pohon, korpus, PerapalRusak())
        assert len(hasil.pembanding) == 1


# ===========================================================================
# ORKESTRASI — tujuh langkah berurutan
# ===========================================================================


class TestAlurLengkap:
    def test_tanpa_klien_hanya_mekanis_yang_jalan(self):
        paragraf = _naskah(["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 88 berlaku."])
        hasil = jalankan_lanjut(paragraf, klien=None)
        assert hasil.berjalan
        assert [t.aturan_id for t in hasil.temuan] == ["F2-001"]
        assert hasil.ongkos.panggilan == 0

    def test_kmk_tidak_dijalankan_dan_alasannya_disebut(self):
        kmk = [
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "NOMOR 1/KM.1/2026",
            "TENTANG",
            "PEMBENTUKAN TIM",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PEMBENTUKAN TIM.",
            "KESATU : Membentuk Tim.",
            "KEDUA : Tim bertugas menyusun laporan.",
        ]
        paragraf = [ParagrafInput(index=i, teks=t) for i, t in enumerate(kmk)]
        hasil = jalankan_lanjut(paragraf, klien=KlienPalsu([]))
        assert not hasil.berjalan
        assert "diktum" in hasil.tidak_dijalankan.lower()
        assert hasil.temuan == []

    def test_alur_penuh_menghasilkan_temuan_dari_penalaran(self):
        paragraf = _naskah()
        pohon = bangun_pohon(paragraf)
        dibaca = saring(pohon).dibaca
        baris = [
            {"satuan_id": s.id, "ringkasan": "ringkas", "memuat_norma": True}
            for s in dibaca
        ]
        # Tiga satuan, per_panggilan bawaan 6 -> Langkah 2 cuma satu panggilan.
        jawaban = [_js({"baris": baris})]  # Langkah 2
        jawaban.append(  # Langkah 3
            _js(
                {
                    "dugaan": [
                        {
                            "satuan_id": "pasal-2",
                            "jenis": "pemikul",
                            "alasan": "pemikulnya tidak tegas",
                            "eksternal": False,
                        }
                    ]
                }
            )
        )
        jawaban.append(  # Langkah 4
            _js(
                {
                    "terbukti": True,
                    "alasan": "kewajiban tanpa pemikul yang tegas",
                    "teks_asli": "wajib mengajukan permohonan",
                    "saran": "sebutkan subjeknya",
                    "skor": 0.9,
                }
            )
        )
        hasil = jalankan_lanjut(paragraf, klien=KlienPalsu(jawaban), mulai_nomor=14)
        kode = [t.aturan_id for t in hasil.temuan]
        assert "F2-102" in kode
        assert hasil.temuan[0].nomor == 14

    def test_penomoran_melanjutkan_fase_1_tidak_mengulang_dari_satu(self):
        paragraf = _naskah(["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 88 berlaku."])
        hasil = jalankan_lanjut(paragraf, klien=None, mulai_nomor=14)
        assert hasil.temuan[0].nomor == 14

    def test_klaim_eksternal_digugurkan_kalau_fase3_mati(self):
        paragraf = _naskah()
        pohon = bangun_pohon(paragraf)
        dibaca = saring(pohon).dibaca
        jawaban = [
            _js({"baris": [{"satuan_id": s.id, "ringkasan": "r"} for s in dibaca]})
        ]
        jawaban.append(
            _js(
                {
                    "dugaan": [
                        {
                            "satuan_id": "pasal-2",
                            "jenis": "makna_ganda",
                            "alasan": "mungkin bentrok peraturan lain",
                            "eksternal": True,
                        }
                    ]
                }
            )
        )
        jawaban.append(
            _js(
                {
                    "terbukti": True,
                    "alasan": "perlu dibandingkan",
                    "teks_asli": "wajib mengajukan permohonan",
                    "skor": 0.95,
                }
            )
        )
        hasil = jalankan_lanjut(paragraf, klien=KlienPalsu(jawaban))
        assert all(t.aturan_id != "F3-001" for t in hasil.temuan)
        assert any("Fase 3 tidak aktif" in g for g in hasil.gugur)

    def test_fase3_aktif_menghasilkan_temuan_f3(self):
        paragraf = _naskah()
        pohon = bangun_pohon(paragraf)
        dibaca = saring(pohon).dibaca
        jawaban = [
            _js({"baris": [{"satuan_id": s.id, "ringkasan": "r"} for s in dibaca]})
        ]
        jawaban.append(
            _js(
                {
                    "dugaan": [
                        {
                            "satuan_id": "pasal-2",
                            "jenis": "makna_ganda",
                            "alasan": "mungkin bentrok peraturan lain",
                            "eksternal": True,
                        }
                    ]
                }
            )
        )
        jawaban.append(
            _js(
                {
                    "terbukti": True,
                    "alasan": "perlu dibandingkan",
                    "teks_asli": "wajib mengajukan permohonan",
                    "skor": 0.95,
                }
            )
        )
        jawaban.append(
            _js(
                {
                    "terbukti": True,
                    "peraturan": "PMK 1/2020",
                    "alasan": "berpotensi bertentangan dengan PMK 1/2020",
                    "teks_asli": "wajib mengajukan permohonan",
                    "saran": "periksa keselarasannya",
                    "skor": 0.85,
                }
            )
        )
        korpus = KorpusPalsu(
            [
                HasilCari(
                    pembanding=[
                        Pembanding(judul="PMK 1/2020", potongan="teks", status="berlaku")
                    ]
                )
            ]
        )
        hasil = jalankan_lanjut(
            paragraf, klien=KlienPalsu(jawaban), korpus=korpus, perapal=PerapalPalsu()
        )
        f3 = [t for t in hasil.temuan if t.aturan_id == "F3-001"]
        assert len(f3) == 1
        assert f3[0].fase == 3
        assert "berpotensi bertentangan" in f3[0].catatan

    def test_batas_temuan_memotong_tanpa_memaksa_mencari(self):
        paragraf = _naskah(
            [
                "Pasal 4",
                "Hal sebagaimana dimaksud dalam Pasal 88 berlaku.",
                "Pasal 5",
                "Hal sebagaimana dimaksud dalam Pasal 89 berlaku.",
            ]
        )
        hasil = jalankan_lanjut(paragraf, klien=None, batas_temuan=1)
        assert len(hasil.temuan) == 1

    def test_pengaturan_penelaah_mematikan_aturan(self):
        paragraf = _naskah(["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 88 berlaku."])
        hasil = jalankan_lanjut(paragraf, klien=None, aturan_aktif=["F2-004"])
        assert hasil.temuan == []
