"""Tes jalur AI Fase 2 dan korpus — tahap 4 (memastikan), 5 (verifikasi), dan alurnya.

SELURUHNYA MEMAKAI KlienPalsu DAN KorpusPalsu. Tidak ada jaringan, tidak ada
kredensial, tidak ada biaya. Yang diuji bukan kecerdasan modelnya melainkan
apa yang terjadi pada JAWABAN model — termasuk jawaban yang mengarang, yang
rusak, dan yang di luar pertanyaan.

Tahap 3 (cari dugaan) diuji di test_tahap3_cari_dugaan.py, bahan tahap 2 di
test_tahap2_bahan.py.

Yang paling penting di berkas ini tes-tes bertanda NEGATIF: membuktikan bahwa
jawaban model yang salah TIDAK sampai ke naskah.
"""

import json

from app.bersama.llm import KlienPalsu, Ongkos, PerapalPalsu
from app.bersama.opensearch import HasilCari, KorpusPalsu, Pembanding, saring_status
from app.models.pekerjaan import CalonTemuan, Dugaan
from app.models.temuan import JenisTanda, ParagrafInput
from app.telaah import tahap5_verifikasi
from app.telaah.alur import jalankan_lanjut
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import susun_bahan
from app.telaah.tahap4_memastikan import korpus_cari, korpus_pastikan, memastikan

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
# TAHAP 4 — memastikan, dengan naskah utuh dan alat
# ===========================================================================


_TERBUKTI = {
    "terbukti": True,
    "alasan": "tidak jelas siapa yang wajib",
    "teks_asli": "wajib mengajukan permohonan",
    "saran": "sebutkan subjeknya",
    "usulan_rumusan": "",
    "skor": 0.9,
}


def _pastikan(dugaan, jawaban, tambahan=None, aturan=None, paragraf=None):
    if paragraf is None:
        paragraf, pohon, _ = _siapkan(tambahan)
    else:
        pohon = bangun_pohon(paragraf)
    klien = KlienPalsu(jawaban)
    bahan = susun_bahan(paragraf, pohon)
    hasil = memastikan.memastikan(dugaan, pohon, bahan, klien, Ongkos(), aturan)
    return hasil, klien, bahan


def _tugas(pesan: str) -> str:
    """Bagian pesan SESUDAH naskah utuh — tempat blok khusus tahap 4 berada."""
    return pesan.split("\n\n---\n\nTUGAS")[1]


class TestMemastikan:
    def test_dugaan_terbukti_jadi_calon(self):
        hasil, _, _ = _pastikan(
            [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")], [_js(_TERBUKTI)]
        )
        assert [c.aturan_id for c in hasil.calon] == ["F2-102"]
        assert hasil.jejak == ["F2-102 [pasal-2]: terbukti"]

    def test_dugaan_gugur_tidak_jadi_apa_apa_dan_alasannya_dicatat(self):
        hasil, _, _ = _pastikan(
            [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")],
            [_js({"terbukti": False, "alasan": "ternyata jelas"})],
        )
        assert hasil.calon == []
        assert hasil.jejak == ["F2-102 [pasal-2]: tidak terbukti — ternyata jelas"]

    def test_NEGATIF_terbukti_tanpa_teks_asli_digugurkan(self):
        hasil, _, _ = _pastikan(
            [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")],
            [_js({"terbukti": True, "alasan": "ada", "teks_asli": "", "skor": 1})],
        )
        assert hasil.calon == []

    def test_NASKAH_UTUH_ikut_di_depan_pesan(self):
        _, klien, bahan = _pastikan(
            [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")], [_js(_TERBUKTI)]
        )
        assert bahan.teks in klien.diminta[0][1]
        assert klien.diminta[0][1].index(bahan.teks) < klien.diminta[0][1].index("TUGAS")

    def test_tabrakan_mengirim_KEDUA_teks_utuh_dalam_satu_panggilan(self):
        jawab = {
            "terbukti": True,
            "satuan_ditandai": "pasal-3",
            "alasan": "Pasal 2 dan Pasal 3 tidak bisa berlaku bersamaan",
            "teks_asli": "dapat disampaikan secara elektronik",
            "saran": "selaraskan",
            "skor": 0.85,
        }
        d = Dugaan(satuan_id="pasal-2", satuan_lain="pasal-3", jenis="tabrakan", alasan="x")
        hasil, klien, _ = _pastikan([d], [_js(jawab)])
        assert len(hasil.calon) == 1
        c = hasil.calon[0]
        assert (c.aturan_id, c.satuan_id, c.satuan_lain) == ("F2-104", "pasal-3", "pasal-2")
        assert len(klien.diminta) == 1
        tugas = _tugas(klien.diminta[0][1])
        assert "[pasal-2] Pengguna Barang wajib mengajukan permohonan" in tugas
        assert "[pasal-3] Permohonan sebagaimana dimaksud" in tugas

    def test_NEGATIF_tabrakan_menunjuk_satuan_di_luar_dua_yang_dikirim(self):
        jawab = {"terbukti": True, "satuan_ditandai": "pasal-1", "alasan": "x", "teks_asli": "y", "skor": 1}
        d = Dugaan(satuan_id="pasal-2", satuan_lain="pasal-3", jenis="tabrakan", alasan="x")
        hasil, _, _ = _pastikan([d], [_js(jawab)])
        assert hasil.calon == []

    def test_aturan_dimatikan_penelaah_tidak_dipanggil(self):
        hasil, klien, _ = _pastikan(
            [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")], ["{}"], aturan={"F2-101"}
        )
        assert klien.diminta == [] and hasil.calon == []
        assert "dimatikan penelaah" in hasil.jejak[0]

    def test_klaim_tidak_ada_dibawa_ke_calon(self):
        jawab = dict(_TERBUKTI, tidak_ada=["Pasal 9"])
        hasil, _, _ = _pastikan([Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")], [_js(jawab)])
        assert hasil.calon[0].tidak_ada == ["Pasal 9"]

    def test_alat_dipanggil_dan_HASILNYA_TEREKAM_untuk_ekspor(self):
        jawaban = [{"alat": "cari_teks", "argumen": {"teks": "pengelola barang"}}, _js(_TERBUKTI)]
        hasil, _, _ = _pastikan([Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="x")], jawaban)
        judul, blok = hasil.rekaman[0]
        assert judul == "TAHAP 4 · DUGAAN 1/1 · F2-102 [pasal-2]"
        siapa = [s for s, _ in blok]
        assert siapa == ["system", "user", "AI memanggil alat", "hasil alat (dibaca AI)"]
        assert blok[2][1] == 'cari_teks({"teks": "pengelola barang"})'
        assert blok[3][1].startswith("KETEMU")

    def test_dugaan_lampiran_membawa_parameter_dan_fakta_lampiran(self):
        from tests.naskah_uji import naskah

        d = Dugaan(satuan_id="lampiran", jenis="lampiran", alasan="parameter 5")
        hasil, klien, bahan = _pastikan([d], [_js({"terbukti": False, "alasan": "ada"})], paragraf=naskah())
        tugas = _tugas(klien.diminta[0][1])
        assert "== PARAMETER LAMPIRAN (KMK 527 butir 120–121) ==" in tugas
        assert bahan.fakta_lampiran in tugas
        assert "SATUAN YANG DIUJI: LAMPIRAN" in tugas


# ===========================================================================
# TAHAP 5 — gerbang terakhir
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

    def test_usulan_yang_membawa_kata_ASING_ke_naskah_tetap_kuning(self):
        """KAIDAH YANG MENJAGA KEBIJAKAN HIJAU — bentuknya 26 Sep 2026.

        Usulan ini harfiah dan ejaannya benar, tetapi "Gubernur" tidak ada di
        mana pun dalam naskah ini, tidak berdefinisi di Pasal 1, dan tidak ada
        peraturan pembanding. Jadi ia lahir dari model sendiri — dan penilaian
        model atas dirinya sendiri bukan bukti, berapa pun skornya.

        Satu kata karangan cukup untuk membatalkan seluruh usulan. Kalau suatu
        hari syarat ini hilang, tes ini yang berbunyi.
        """
        lolos, gugur = self._jalan(
            self._calon(usulan_rumusan="wajib mengajukan permohonan kepada Gubernur")
        )
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert lolos[0].usulan_rumusan is None
        assert "Contoh rumusan:" in lolos[0].saran
        assert "tanpa sumber" in gugur[0]

    def test_usulan_dari_istilah_berdefinisi_naskah_sendiri_jadi_hijau(self):
        """PILIHAN B, ditetapkan penelaah 26 Sep 2026.

        "Pengelola Barang" bukan karangan model: ia berdefinisi di Pasal 1
        angka 1 naskah ini juga. Penelaah bisa memeriksa asalnya tanpa
        meninggalkan dokumen yang sedang dibukanya — syarat yang ia rumuskan
        sendiri sebagai "ada textnya di pasal".
        """
        lolos, _ = self._jalan(
            self._calon(usulan_rumusan="wajib mengajukan permohonan kepada Pengelola Barang")
        )
        assert lolos[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert lolos[0].usulan_rumusan
        # Medan sendiri, bukan menumpang di `saran` — komentar temuan hijau
        # melewati blok Saran, dan sumbernya tidak boleh ikut terbuang.
        assert lolos[0].sumber_usulan == (
            "istilah berdefinisi Pasal 1: Pengelola Barang"
        )

    def test_model_yang_DIAM_soal_pengganti_dicatat_di_daftar_gugur(self):
        """Temuannya tetap ada, tetapi kebisuannya tercatat.

        Penelaah 26 Sep 2026: "ai dapat menemukan kesalahan internal tapi ia
        tidak bisa memberi rekomendasi apapun ... seharusnya kamu dapat
        memaksanya". Pemaksaannya di prompt Langkah 4; catatan ini yang
        membuat pelanggarannya bisa DIHITUNG sesudah satu kali jalan berbiaya.
        """
        lolos, gugur = self._jalan(self._calon(sasaran="satuan ini"))
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert any("tidak mengusulkan pengganti" in g for g in gugur)

    def test_sasaran_di_tempat_lain_boleh_tanpa_usulan(self):
        """Kebalikannya, dan ini BUKAN pelanggaran.

        Perbaikannya memang dikerjakan di Pasal 1, bukan di teks yang dicoret
        — kaidah penelaah 25 Sep 2026: "kalo mengharuskan di tempat yang
        berbeda hannya bertanda kuning dan ada komentar". Menuntut usulan di
        sini justru akan menghasilkan sisipan yang salah tempat.
        """
        _, gugur = self._jalan(self._calon(sasaran="pasal-1"))
        assert not any("tidak mengusulkan pengganti" in g for g in gugur)

    def test_MEMBUANG_kata_modal_tidak_lolos_sebagai_susunan_ulang(self):
        """LUBANG YANG SUDAH TEMBUS SEKALI, PMK 17 26 Sep 2026.

        Penjaga jalur internal memeriksa kata yang DIBAWA MASUK usulan.
        Usulan ini tidak membawa masuk apa pun yang berisi — satu-satunya
        tambahannya "oleh", yang memang perancah kalimat — jadi ia lolos
        sebagai "susunan ulang kata" dan jadi hijau di naskah nyata.

        Padahal "dapat" hilang. Kewenangan berubah jadi keharusan, persis
        yang diperiksa F2-103. Membuang kata modal harus sama beratnya dengan
        menambahkannya.
        """
        lolos, gugur = self._jalan(
            self._calon(
                satuan_id="pasal-3",
                teks_asli="dapat disampaikan secara elektronik",
                usulan_rumusan="disampaikan secara elektronik oleh Pengelola Barang",
            )
        )
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert lolos[0].usulan_rumusan is None
        assert "tanpa sumber" in gugur[0]

    def test_menukar_KATA_MODAL_tidak_lolos_lewat_jalur_internal(self):
        """JEBAKAN PALING BERBAHAYA DI PILIHAN B.

        "dapat" jadi "wajib" cuma menukar satu kata, dan sepintas kelihatan
        seperti perapian bahasa — padahal ia mengubah kewenangan jadi
        kewajiban. Akibat hukumnya berbeda sama sekali, dan itu justru yang
        diperiksa F2-103.

        Yang menahannya: "wajib" tidak ada di Pasal 3, jadi ia kata yang
        DIBAWA MASUK model, bukan yang sudah ada di naskah. Kalau suatu hari
        kata modal masuk ke `_KATA_FUNGSI` demi meloloskan lebih banyak hijau,
        tes ini yang berbunyi.
        """
        lolos, gugur = self._jalan(
            self._calon(
                aturan_id="F2-103",
                satuan_id="pasal-3",
                teks_asli="dapat disampaikan secara",
                usulan_rumusan="wajib disampaikan secara",
            )
        )
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert lolos[0].usulan_rumusan is None
        assert "tanpa sumber" in gugur[0]

    def test_usulan_BERIKUT_peraturan_sumber_jadi_hijau(self):
        """JALUR KORPUS, DAN IA TIDAK DIMATIKAN PILIHAN B.

        "Gubernur" sengaja dipakai: kata itu tidak ada di naskah, jadi jalur
        internal pasti menolaknya. Yang meloloskannya cuma peraturan berlaku
        dari korpus OpenSearch. Kalau suatu hari jalur ini ikut dimatikan
        sewaktu merapikan kebijakan hijau, tes ini yang berbunyi.
        """
        lolos, _ = self._jalan(
            self._calon(
                usulan_rumusan="wajib mengajukan permohonan kepada Gubernur",
                pembanding="PMK 40 TAHUN 2024",
                pembanding_sah=["PMK 40 TAHUN 2024"],
            )
        )
        assert lolos[0].jenis_tanda == JenisTanda.PENGGANTIAN
        assert lolos[0].usulan_rumusan

    def test_hijau_menyebut_peraturan_sumbernya_di_komentar(self):
        """Syarat kebijakan hijau, bukan hiasan: penelaah harus bisa memeriksa
        sendiri bahwa ini bukan asal klaim."""
        lolos, _ = self._jalan(
            self._calon(
                usulan_rumusan="wajib mengajukan permohonan kepada Gubernur",
                pembanding="PMK 40 TAHUN 2024",
                pembanding_sah=["PMK 40 TAHUN 2024"],
            )
        )
        assert lolos[0].sumber_usulan == "PMK 40 TAHUN 2024 (masih berlaku)"

    def test_aturan_di_luar_himpunan_hijau_tidak_pernah_hijau(self):
        """F3-001 membawa pembanding juga, tetapi temuannya KEMUNGKINAN —
        bukan kesimpulan — jadi ia tetap kuning."""
        lolos, gugur = self._jalan(
            self._calon(
                aturan_id="F3-001",
                usulan_rumusan="wajib mengajukan permohonan kepada Pengelola Barang",
                pembanding="PMK 40 TAHUN 2024",
                pembanding_sah=["PMK 40 TAHUN 2024"],
            )
        )
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert "tidak membuktikan kesalahan" in gugur[0]

    def test_DITURUNKAN_usulan_berupa_penjelasan_bukan_pengganti(self):
        lolos, gugur = self._jalan(
            self._calon(usulan_rumusan="Sebaiknya subjeknya disebutkan secara tegas")
        )
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert "DITURUNKAN" in gugur[0]

    def test_DITURUNKAN_istilah_berdefinisi_salah_eja_di_usulan(self):
        """Peraturan sumbernya sah, tetapi istilah berdefinisi salah eja —
        "Pengeloa Barang" mengubah arti hukumnya. Turun jadi kuning."""
        lolos, gugur = self._jalan(
            self._calon(
                usulan_rumusan="wajib mengajukan permohonan kepada Pengeloa Barang",
                pembanding="PMK 40 TAHUN 2024",
                pembanding_sah=["PMK 40 TAHUN 2024"],
            )
        )
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert "salah eja" in gugur[0]

    def test_saran_punya_medan_sendiri_terpisah_dari_catatan(self):
        """Komentar Word menata 'Temuan:' lalu 'Saran:' — dua medan, bukan satu."""
        lolos, _ = self._jalan(self._calon())
        assert lolos[0].saran == "sebutkan subjeknya"
        assert "Saran" not in lolos[0].catatan
        assert lolos[0].catatan == "tidak jelas siapa pemikulnya"

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
            korpus_pastikan.pastikan_ulang(
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
        calon = korpus_pastikan.pastikan_ulang(
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
            korpus_pastikan.pastikan_ulang(
                self._calon(), pohon, self._hasil(), klien, Ongkos()
            )
            is None
        )

    def test_daftar_pembanding_ikut_dikirim_ke_model(self):
        _, pohon, _ = _siapkan()
        klien = KlienPalsu([_js({"terbukti": False})])
        korpus_pastikan.pastikan_ulang(
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
        assert korpus_cari.susun_kueri(calon, pohon).startswith("wajib mengajukan")

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
        hasil = korpus_cari.cari_pembanding(calon, pohon, korpus, PerapalRusak())
        assert len(hasil.pembanding) == 1


# ===========================================================================
# ORKESTRASI — lima tahap berurutan
# ===========================================================================


def _jawab_pasal(dugaan=None):
    """Jawaban tahap 3 per kelompok pasal untuk naskah uji (Pasal 1–3 sekaligus)."""
    hasil = [{"pasal": p, "dugaan": []} for p in ("pasal-1", "pasal-2", "pasal-3")]
    if dugaan:
        hasil[1]["dugaan"] = dugaan
    return _js({"hasil": hasil})


_LINTAS_KOSONG = _js({"dugaan": [], "keberatan": []})


class TestAlurLengkap:
    def test_tanpa_klien_hanya_mekanis_yang_jalan(self):
        paragraf = _naskah(["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 88 berlaku."])
        hasil = jalankan_lanjut(paragraf, klien=None)
        assert hasil.berjalan
        assert [t.aturan_id for t in hasil.temuan] == ["F2-001"]
        assert hasil.ongkos.panggilan == 0
        assert hasil.bahan is not None  # bahan tetap disusun — gratis

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
        klien = KlienPalsu([])
        hasil = jalankan_lanjut(paragraf, klien=klien)
        assert not hasil.berjalan
        assert "diktum" in hasil.tidak_dijalankan.lower()
        assert hasil.temuan == [] and klien.diminta == []

    def test_alur_penuh_menghasilkan_temuan_dari_penalaran(self):
        dugaan = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "pemikulnya tidak tegas"}]
        jawaban = [
            _jawab_pasal(dugaan),  # tahap 3, per kelompok pasal
            _LINTAS_KOSONG,  # tahap 3, lintas naskah
            _js(
                {
                    "terbukti": True,
                    "alasan": "kewajiban tanpa pemikul yang tegas",
                    "teks_asli": "wajib mengajukan permohonan",
                    "saran": "sebutkan subjeknya",
                    "skor": 0.9,
                }
            ),  # tahap 4
        ]
        hasil = jalankan_lanjut(_naskah(), klien=KlienPalsu(jawaban), mulai_nomor=14)
        assert [t.aturan_id for t in hasil.temuan] == ["F2-102"]
        assert hasil.temuan[0].nomor == 14
        assert len(hasil.pesan_tahap3) == 2 and len(hasil.pesan_tahap4) == 1

    def test_semua_aturan_AI_mati_tidak_memanggil_model(self):
        klien = KlienPalsu([])
        hasil = jalankan_lanjut(_naskah(), klien=klien, aturan_aktif=["F2-001", "F2-004"])
        assert klien.diminta == []
        assert hasil.pesan_tahap3 == [] and hasil.pesan_tahap4 == []

    def test_penomoran_melanjutkan_fase_1_tidak_mengulang_dari_satu(self):
        paragraf = _naskah(["Pasal 4", "Hal sebagaimana dimaksud dalam Pasal 88 berlaku."])
        hasil = jalankan_lanjut(paragraf, klien=None, mulai_nomor=14)
        assert hasil.temuan[0].nomor == 14

    def _eksternal(self):
        dugaan = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "mungkin bentrok peraturan lain", "eksternal": True}]
        return [
            _jawab_pasal(dugaan),
            _LINTAS_KOSONG,
            _js({"terbukti": True, "alasan": "perlu dibandingkan", "teks_asli": "wajib mengajukan permohonan", "skor": 0.95}),
        ]

    def test_klaim_eksternal_digugurkan_kalau_korpus_mati(self):
        hasil = jalankan_lanjut(_naskah(), klien=KlienPalsu(self._eksternal()))
        assert all(t.aturan_id != "F3-001" for t in hasil.temuan)
        assert any("korpus (Fase 3) tidak aktif" in g for g in hasil.gugur)

    def test_korpus_aktif_menghasilkan_temuan_f3(self):
        jawaban = self._eksternal() + [
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
        ]
        korpus = KorpusPalsu(
            [HasilCari(pembanding=[Pembanding(judul="PMK 1/2020", potongan="teks", status="berlaku")])]
        )
        hasil = jalankan_lanjut(
            _naskah(), klien=KlienPalsu(jawaban), korpus=korpus, perapal=PerapalPalsu()
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


# ===========================================================================
# REGRESI — dua cacat yang ditemukan saat --lanjut dijalankan pada
# contoh-rancangan-uji.docx, 22 Sep 2026. Keduanya lolos seluruh tes yang ada
# waktu itu, dan baru kelihatan dari keluaran model sungguhan.
# ===========================================================================


class TestRegresiUsulanMenimpaLebihDariRentangnya:
    """CACAT A — yang paling merusak, dan paling sulit dilihat.

    Model menjawab usulan yang menulis ulang SELURUH kalimat, padahal yang
    dicoret cuma penggalan belakangnya. Usulannya terbaca wajar sendirian dan
    panjangnya masih masuk akal, jadi pemeriksaan panjang meloloskannya. Begitu
    disisipkan, kalimatnya tertulis dua kali di naskah penelaah.
    """

    _PARAGRAF = (
        "(2) Catatan telaah sebagaimana dimaksud pada ayat (1) "
        "disampaikan kepada Unit Pemrakarsa."
    )
    _ASLI = "disampaikan kepada Unit Pemrakarsa."
    _USULAN_MENIMPA = (
        "Catatan telaah sebagaimana dimaksud pada ayat (1) "
        "disampaikan kepada Unit Pemrakarsa oleh Penelaah."
    )

    def _sebelum(self):
        return self._PARAGRAF[: self._PARAGRAF.index(self._ASLI)]

    def test_usulan_yang_mengulang_teks_sebelumnya_ditolak(self):
        assert not tahap5_verifikasi.usulan_harfiah(
            self._USULAN_MENIMPA, self._ASLI, self._sebelum()
        )

    def test_panjangnya_saja_TIDAK_cukup_menangkapnya(self):
        """Bukti kenapa pemeriksaan teks-sebelum perlu ada.

        Tanpa `sebelum`, usulan yang sama lolos — 99 huruf masih di bawah
        batas 175 untuk teks_asli 35 huruf.
        """
        assert tahap5_verifikasi.usulan_harfiah(self._USULAN_MENIMPA, self._ASLI)

    def test_pengganti_yang_benar_tetap_diterima(self):
        assert tahap5_verifikasi.usulan_harfiah(
            "disampaikan oleh Penelaah kepada Unit Pemrakarsa.",
            self._ASLI,
            self._sebelum(),
        )

    def test_teks_sebelum_yang_pendek_tidak_menghalangi(self):
        """Nomor ayat di depan ("(1) ") terlalu pendek untuk jadi penanda."""
        assert tahap5_verifikasi.usulan_harfiah(
            "Pengguna Barang wajib mengajukan", "wajib mengajukan", "(1) "
        )

    def test_lewat_verifikasi_penuh_temuannya_turun_jadi_kuning(self):
        paragraf = _naskah(
            [
                "Pasal 4",
                "(1) Permohonan sebagaimana dimaksud dalam Pasal 2 "
                "disampaikan kepada Pengelola Barang.",
            ]
        )
        pohon = bangun_pohon(paragraf)
        daftar = ambil_definisi(pohon)
        calon = CalonTemuan(
            aturan_id="F2-102",
            satuan_id="pasal-4-ayat-1",
            alasan="tidak jelas siapa yang menyampaikan",
            teks_asli="disampaikan kepada Pengelola Barang.",
            usulan_rumusan=(
                "Permohonan sebagaimana dimaksud dalam Pasal 2 disampaikan "
                "kepada Pengelola Barang oleh Pengguna Barang."
            ),
            # Pembanding diisi supaya calon ini LOLOS kebijakan hijau dan
            # benar-benar sampai ke pemeriksaan rentang. Yang diuji di sini
            # penjagaan rentangnya, bukan kebijakan hijau-kuningnya — dan
            # penjagaan itu harus menahan usulan sekalipun sumbernya sah.
            pembanding="PMK 40 TAHUN 2024",
            pembanding_sah=["PMK 40 TAHUN 2024"],
            skor=0.95,
        )
        lolos, gugur = tahap5_verifikasi.verifikasi(
            [calon], pohon, daftar, paragraf, 0.7
        )
        assert len(lolos) == 1
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        # Alasannya disebut spesifik, bukan "bukan pengganti harfiah" yang
        # generik — penelusur bug perlu tahu penjaga MANA yang berbunyi.
        assert "tertulis dua kali" in gugur[0]


class TestRegresiIstilahBerdefinisiSalingMenuduh:
    """CACAT B — dua istilah sah yang cuma terpaut satu-dua huruf.

    Naskah hukum penuh pasangan begini: Penelaah/Penelaahan,
    Pengguna/Penggunaan. Usulan yang menulis salah satunya dengan BENAR
    dituduh salah mengeja tetangganya, lalu diturunkan tanpa sebab.
    """

    _DEF = [
        "Pasal 1",
        "Dalam Peraturan Menteri ini yang dimaksud dengan:",
        "1. Penelaah adalah pegawai yang melakukan penelaahan.",
        "2. Penelaahan adalah kegiatan memeriksa kesesuaian Rancangan.",
        "3. Rancangan adalah naskah yang belum ditetapkan.",
    ]

    def _daftar(self):
        paragraf = [
            ParagrafInput(index=i, teks=t) for i, t in enumerate(_KEPALA + self._DEF)
        ]
        return ambil_definisi(bangun_pohon(paragraf))

    def test_istilah_tetangga_yang_dieja_benar_tidak_dituduh(self):
        d = self._daftar()
        assert "Penelaah" in d.istilah_saja() and "Penelaahan" in d.istilah_saja()
        assert d.cari_mirip("Catatan disampaikan oleh Penelaah.") == []

    def test_salah_ketik_sungguhan_TETAP_tertangkap(self):
        """Penjagaan baru tidak boleh mematikan gunanya yang asli."""
        d = self._daftar()
        assert "Penelaah" in d.cari_mirip("Catatan disampaikan oleh Peneleah.")


class TestBahanMemuatButirPasal1YangTakTerbaca:
    """CLAUDE.md butir 14: seluruh butir Pasal 1 wajib sampai ke model."""

    def test_butir_tak_terbaca_dikirim_apa_adanya(self):
        paragraf = _naskah()
        sisip = next(i for i, p in enumerate(paragraf) if p.teks.startswith("2. Pengguna"))
        baris = [p.teks for p in paragraf]
        baris.insert(sisip + 1, "3. Barang Titipan ialah barang yang dititipkan.")
        paragraf = [ParagrafInput(index=i, teks=t) for i, t in enumerate(baris)]
        pohon = bangun_pohon(paragraf)
        assert ambil_definisi(pohon).tak_terbaca  # memang tidak terbaca parser
        bahan = susun_bahan(paragraf, pohon)
        assert "3. Barang Titipan ialah barang yang dititipkan." in bahan.teks


# ===========================================================================
# Regresi uji Word 27 Sep 2026 — docs/perbaiki bug.md bug 1, 5, 6
# ===========================================================================

_PASAL_4 = [
    "Pasal 4",
    "(1) Pengguna Barang mengajukan permohonan dengan melampirkan:",
    "a. surat pengantar;",
    "b. dokumen kepemilikan.",
    "(2) Dokumen sebagaimana dimaksud pada ayat (1) huruf b wajib disahkan.",
    "(3) Surat sebagaimana dimaksud pada ayat (1) huruf c wajib dilampirkan.",
    "Pasal 5",
    "Pengguna Barang wajib mengajukan permohonan ulang setiap tahun.",
]


def _calon(**ganti):
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


def _verifikasi(*calon, paragraf=None):
    if paragraf is None:
        paragraf = _naskah(_PASAL_4)
    pohon = bangun_pohon(paragraf)
    daftar = ambil_definisi(pohon)
    return tahap5_verifikasi.verifikasi(list(calon), pohon, daftar, paragraf, 0.7)


class TestTahap4MelampirkanYangDirujuk:
    """Tahap 4 tempat temuan lahir, dan dulu tidak menerima lampiran ini."""

    def test_satuan_yang_dirujuk_ikut_dalam_tugas(self):
        d = Dugaan(satuan_id="pasal-4-ayat-2", jenis="makna_ganda", alasan="x")
        _, klien, _ = _pastikan([d], [_js({"terbukti": False, "alasan": "jelas"})], tambahan=_PASAL_4)
        tugas = _tugas(klien.diminta[0][1])
        assert "SATUAN YANG DIRUJUK" in tugas
        assert "[pasal-4-ayat-1-huruf-b]" in tugas
        assert "b. dokumen kepemilikan." in tugas

    def test_alamat_yang_tidak_ada_dikatakan_tidak_ada(self):
        d = Dugaan(satuan_id="pasal-4-ayat-3", jenis="makna_ganda", alasan="x")
        _, klien, _ = _pastikan([d], [_js({"terbukti": False, "alasan": "jelas"})], tambahan=_PASAL_4)
        assert "[pasal-4-ayat-1-huruf-c] TIDAK ADA di naskah" in _tugas(klien.diminta[0][1])

    def test_tabrakan_juga_membawa_batang_induk(self):
        d = Dugaan(
            satuan_id="pasal-4-ayat-1-huruf-a", satuan_lain="pasal-5",
            jenis="tabrakan", alasan="x",
        )
        _, klien, _ = _pastikan([d], [_js({"terbukti": False, "alasan": "jelas"})], tambahan=_PASAL_4)
        tugas = _tugas(klien.diminta[0][1])
        assert "BATANG KALIMAT INDUKNYA" in tugas
        assert "melampirkan:" in tugas


class TestGugurRujukanYangAda:
    def test_GUGUR_menandai_rujukan_yang_tujuannya_ada(self):
        lolos, gugur = _verifikasi(_calon(
            aturan_id="F2-101", satuan_id="pasal-4-ayat-2",
            teks_asli="ayat (1) huruf b", bacaan=["x satu", "y dua"],
            alasan="ayat (1) tidak memiliki huruf b",
        ))
        assert lolos == []
        assert "cuma rujukan internal" in gugur[0]

    def test_rujukan_yang_tujuannya_TIDAK_ada_tetap_dinilai(self):
        lolos, _ = _verifikasi(_calon(
            aturan_id="F2-101", satuan_id="pasal-4-ayat-3",
            teks_asli="ayat (1) huruf c", bacaan=["x satu", "y dua"],
            alasan="ayat (1) tidak memiliki huruf c",
        ))
        assert len(lolos) == 1


class TestGugurTuduhanTakBerdefinisi:
    def test_GUGUR_istilah_yang_tertulis_di_pasal_1(self):
        lolos, gugur = _verifikasi(_calon(
            teks_asli="Pengguna Barang", sasaran="pasal-1",
            alasan="Istilah Pengguna Barang tidak ditemukan definisinya di Pasal 1.",
        ))
        assert lolos == []
        assert "tidak berdefinisi, padahal tertulis di Pasal 1" in gugur[0]

    def test_temuan_tentang_ISI_definisi_tetap_lolos(self):
        lolos, _ = _verifikasi(_calon(
            teks_asli="Pengguna Barang", sasaran="pasal-1",
            alasan="Definisi Pengguna Barang di Pasal 1 tidak mencakup kuasa pengguna.",
        ))
        assert len(lolos) == 1


class TestF2101WajibDuaTafsiran:
    def _f2101(self, bacaan):
        return _calon(aturan_id="F2-101", alasan="bisa dibaca dua arah", bacaan=bacaan)

    def test_GUGUR_tanpa_tafsiran(self):
        lolos, gugur = _verifikasi(self._f2101([]))
        assert lolos == [] and "dua tafsiran" in gugur[0]

    def test_GUGUR_dua_tafsiran_yang_sama(self):
        lolos, _ = _verifikasi(self._f2101(["Pengguna wajib.", "pengguna wajib"]))
        assert lolos == []

    def test_dua_tafsiran_berbeda_lolos_dan_tertulis_di_catatan(self):
        lolos, _ = _verifikasi(self._f2101(
            ["tenggatnya hari kalender", "tenggatnya hari kerja"]
        ))
        assert len(lolos) == 1
        assert "Bisa dibaca: (1) tenggatnya hari kalender; atau (2) tenggatnya hari kerja." in lolos[0].catatan

    def test_aturan_lain_tidak_dituntut_tafsiran(self):
        lolos, _ = _verifikasi(_calon())
        assert len(lolos) == 1


class TestLabelDiKutipan:
    def test_kutipan_berlabel_ketemu_walau_label_berupa_penomoran_otomatis(self):
        paragraf = _naskah(_PASAL_4)
        i = next(p.index for p in paragraf if p.teks.startswith("(2) Dokumen"))
        paragraf[i] = ParagrafInput(
            index=i, penanda="(2)",
            teks="Dokumen sebagaimana dimaksud pada ayat (1) huruf b wajib disahkan.",
        )
        lolos, _ = _verifikasi(
            _calon(satuan_id="pasal-4-ayat-2", teks_asli="(2) Dokumen sebagaimana dimaksud"),
            paragraf=paragraf,
        )
        assert len(lolos) == 1
        assert lolos[0].lokasi.teks_asli == "Dokumen sebagaimana dimaksud"
        assert lolos[0].lokasi.offset_mulai == 0


class TestGabungKembar:
    """PMK 104 dan PMK 17, 27 Sep 2026: satu kesalahan = satu kartu, satu komentar."""

    def test_teks_dan_aturan_sama_di_dua_pasal_jadi_satu(self):
        lolos, gugur = _verifikasi(
            _calon(),
            _calon(satuan_id="pasal-5"),
        )
        assert len(lolos) == 1
        assert lolos[0].satuan_id == "pasal-2"
        assert lolos[0].juga_di == ["Pasal 5"]
        assert any("digabung" in g for g in gugur)

    def test_aturan_berbeda_tidak_digabung(self):
        lolos, _ = _verifikasi(
            _calon(),
            _calon(satuan_id="pasal-5", aturan_id="F2-103"),
        )
        assert len(lolos) == 2


# ===========================================================================
# Tahap 5 — tambahan bug 7: klaim "tidak ada", kutipan tahan spasi, letak
# ===========================================================================


class TestKlaimTidakAda:
    """⑨ — klaim "X tidak ada" dibuktikan kode di seluruh teks mentah."""

    def test_GUGUR_yang_diklaim_tidak_ada_ternyata_ada(self):
        lolos, gugur = _verifikasi(_calon(tidak_ada=["Pasal 5"]))
        assert lolos == []
        assert "mengklaim 'Pasal 5' tidak ada, padahal ada" in gugur[0]

    def test_yang_memang_tidak_ada_tetap_lolos(self):
        lolos, _ = _verifikasi(_calon(tidak_ada=["Lampiran IX"]))
        assert len(lolos) == 1

    def test_tidak_peka_huruf_besar_kecil_dan_spasi(self):
        lolos, _ = _verifikasi(_calon(tidak_ada=["pengguna   BARANG   mengajukan"]))
        assert lolos == []

    def test_paragraf_temuan_itu_sendiri_dikecualikan(self):
        """"Merujuk huruf c yang tidak ada" memang memuat kata itu di kalimatnya."""
        lolos, _ = _verifikasi(_calon(
            satuan_id="pasal-4-ayat-3", teks_asli="ayat (1) huruf c", aturan_id="F2-101",
            bacaan=["x satu", "y dua"], tidak_ada=["ayat (1) huruf c"],
        ))
        assert len(lolos) == 1

    def test_klaim_di_alasan_tanpa_medan_tetap_diperiksa(self):
        lolos, gugur = _verifikasi(_calon(
            alasan="Merujuk 'Pengguna Barang mengajukan permohonan' yang tidak ada di naskah.",
        ))
        assert lolos == [] and "mengklaim" in gugur[0]

    def test_kutipan_yang_memang_ditandai_tidak_dihitung_klaim(self):
        lolos, _ = _verifikasi(_calon(
            alasan="Frasa 'wajib mengajukan permohonan' tidak ada di naskah lain sebagai rujukan.",
        ))
        assert len(lolos) == 1


class TestKutipanTahanSpasi:
    def test_spasi_ganda_dan_tab_di_naskah_tetap_ketemu(self):
        paragraf = _naskah(_PASAL_4)
        i = next(p.index for p in paragraf if p.teks.startswith("Pengguna Barang wajib"))
        paragraf[i] = ParagrafInput(
            index=i, teks="Pengguna Barang wajib  mengajukan\tpermohonan paling lambat 30 (tiga puluh) hari."
        )
        lolos, _ = _verifikasi(_calon(), paragraf=paragraf)
        assert len(lolos) == 1
        # Yang ditandai rentang ASLI paragrafnya, bukan kutipan model.
        assert lolos[0].lokasi.teks_asli == "wajib  mengajukan\tpermohonan"
        assert lolos[0].lokasi.panjang == len("wajib  mengajukan\tpermohonan")

    def test_huruf_yang_berbeda_tetap_gugur(self):
        lolos, _ = _verifikasi(_calon(teks_asli="wajib mengajukan permohonannya"))
        assert lolos == []


class TestLetakTidakPasti:
    """Paragraf sesudah tabel raksasa: nomornya bukan nomor Word — tidak pernah ditandai."""

    def _naskah_tak_pasti(self):
        paragraf = _naskah(_PASAL_4)
        batas = next(p.index for p in paragraf if p.teks == "Pasal 4")
        return [
            p.model_copy(update={"letak_pasti": p.index < batas}) for p in paragraf
        ]

    def test_temuan_dilaporkan_tetapi_tidak_bisa_ditandai(self):
        lolos, _ = _verifikasi(
            _calon(satuan_id="pasal-5", teks_asli="wajib mengajukan permohonan ulang"),
            paragraf=self._naskah_tak_pasti(),
        )
        assert len(lolos) == 1
        t = lolos[0]
        assert t.lokasi.paragraf_index == tahap5_verifikasi.LETAK_TIDAK_PASTI
        assert "Tidak ditandai di naskah" in t.catatan

    def test_usulan_tidak_pernah_disisipkan(self):
        # Usulan yang di tempat lain boleh hijau: kata-katanya sudah ada di
        # coretannya sendiri. Yang menahannya di sini hanya letaknya.
        lolos, gugur = _verifikasi(
            _calon(
                satuan_id="pasal-5",
                teks_asli="wajib mengajukan permohonan ulang",
                usulan_rumusan="wajib mengajukan ulang permohonan",
            ),
            paragraf=self._naskah_tak_pasti(),
        )
        assert lolos[0].jenis_tanda == JenisTanda.CATATAN
        assert lolos[0].usulan_rumusan is None
        assert any("letaknya sesudah tabel raksasa" in g for g in gugur)

    def test_urutannya_paling_akhir(self):
        lolos, _ = _verifikasi(
            _calon(satuan_id="pasal-5", teks_asli="wajib mengajukan permohonan ulang"),
            _calon(),
            paragraf=self._naskah_tak_pasti(),
        )
        assert [t.satuan_id for t in lolos] == ["pasal-2", "pasal-5"]
