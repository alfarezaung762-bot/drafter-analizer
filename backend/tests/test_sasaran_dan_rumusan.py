"""Sasaran perbaikan, penghapusan, dan Langkah 6c. TANPA jaringan.

Tiga penetapan penelaah 23 Sep 2026 yang diuji di sini:

  1. Tiap temuan menyebut DI MANA perbaikannya — dan tempat yang tidak bisa
     dibuktikan ada di naskah TIDAK ditulis, bukan ditebak.
  2. Kesalahan yang perbaikannya MEMBUANG dicoret merah tanpa sisipan hijau.
  3. Hijau untuk aturan penalaran menuntut peraturan sumber yang bisa
     ditunjuk — rumusan dari peraturan yang masih berlaku.

Tes yang paling menentukan:
`TestLangkah6c.test_peraturan_di_luar_hasil_pencarian_tidak_dipakai` — kalau
suatu hari model bisa menyebut peraturan dari ingatannya dan usulannya tetap
masuk, tes itu yang berbunyi.
"""

import json

from app.bersama.llm import KlienPalsu, Ongkos, PerapalPalsu
from app.bersama.opensearch import HasilCari, KorpusPalsu, Pembanding
from app.models.pekerjaan import CalonTemuan
from app.models.temuan import JenisTanda, ParagrafInput
from app.telaah import tahap5_verifikasi
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.mekanis_konsistensi import jalankan_mekanis
from app.telaah.tahap4_memastikan import korpus_rumusan

_BARIS = [
    "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
    "NOMOR 12 TAHUN 2026",
    "TENTANG",
    "TATA CARA PENETAPAN STATUS PENGGUNAAN",
    "DENGAN RAHMAT TUHAN YANG MAHA ESA",
    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
    "Mengingat :",
    "1. Undang-undang Nomor 1 Tahun 2004 tentang Perbendaharaan;",
    "MEMUTUSKAN:",
    "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA.",
    "Pasal 1",
    "Dalam Peraturan Menteri ini yang dimaksud dengan:",
    "1. Pengguna Barang adalah pejabat pemegang kewenangan penggunaan.",
    "2. Sistem Informasi adalah aplikasi pencatatan barang milik negara.",
    "Pasal 2",
    "(1) Pengguna Barang wajib mengajukan permohonan kepada Menteri.",
    "(2) Permohonan sebagaimana dimaksud pada ayat (1) memuat alasan.",
]


def _paragraf() -> list[ParagrafInput]:
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(_BARIS)]


def _pohon():
    return bangun_pohon(_paragraf())


def _calon(**ganti) -> CalonTemuan:
    dasar = dict(
        aturan_id="F2-102",
        satuan_id="pasal-2-ayat-1",
        alasan="tidak jelas siapa pemikulnya",
        teks_asli="wajib mengajukan permohonan",
        saran="sebutkan subjeknya",
        skor=0.9,
    )
    dasar.update(ganti)
    return CalonTemuan(**dasar)


def _verifikasi(calon):
    paragraf = _paragraf()
    pohon = bangun_pohon(paragraf)
    return tahap5_verifikasi.verifikasi(
        [calon], pohon, ambil_definisi(pohon), paragraf, 0.7
    )


class TestSebutanSasaran:
    def test_nama_tetap_jadi_bacaan_manusia(self):
        p = _pohon()
        assert tahap5_verifikasi.sebutan_sasaran("menimbang", "pasal-2", p) == (
            "bagian Menimbang"
        )
        assert tahap5_verifikasi.sebutan_sasaran("mengingat", "pasal-2", p) == (
            "bagian Mengingat"
        )

    def test_pasal_1_disebut_ketentuan_umum(self):
        """Penelaah langsung tahu ini soal daftar istilah."""
        assert tahap5_verifikasi.sebutan_sasaran("pasal-1", "pasal-2", _pohon()) == (
            "Pasal 1 (Ketentuan Umum)"
        )

    def test_id_bertingkat_terbaca_utuh(self):
        assert tahap5_verifikasi.sebutan_sasaran(
            "pasal-2-ayat-2", "pasal-2-ayat-1", _pohon()
        ) == "Pasal 2 ayat (2)"

    def test_satuan_yang_TIDAK_ADA_dikosongkan(self):
        """KAIDAH YANG MENJAGA BARIS 'Perbaiki di'.

        Menunjuk Pasal 45 yang tidak ada lebih buruk daripada diam soal
        tempat — penelaah akan mencarinya dan tidak menemukan apa pun.
        """
        assert tahap5_verifikasi.sebutan_sasaran("pasal-45", "pasal-2", _pohon()) == ""

    def test_kalimat_bebas_dikosongkan(self):
        """Model kadang menjawab kalimat, bukan id. Tidak bisa dibuktikan."""
        assert tahap5_verifikasi.sebutan_sasaran(
            "di bagian ketentuan umum saja", "pasal-2", _pohon()
        ) == ""

    def test_satuan_sendiri_dikosongkan(self):
        """'Perbaiki di: Pasal 2' pada komentar yang menempel di Pasal 2
        menambah baris tanpa menambah keterangan."""
        assert tahap5_verifikasi.sebutan_sasaran("pasal-2", "pasal-2", _pohon()) == ""
        assert tahap5_verifikasi.sebutan_sasaran("satuan ini", "pasal-2", _pohon()) == ""


class TestSasaranSampaiKeTemuan:
    def test_sasaran_sah_terbawa(self):
        lolos, _ = _verifikasi(_calon(sasaran="pasal-1"))
        assert lolos[0].sasaran == "Pasal 1 (Ketentuan Umum)"

    def test_sasaran_karangan_tidak_terbawa(self):
        lolos, _ = _verifikasi(_calon(sasaran="pasal-99"))
        assert lolos[0].sasaran == ""

    def test_tanpa_sasaran_tetap_jalan(self):
        """Temuan lama dan aturan mekanis tidak mengisinya sama sekali."""
        lolos, _ = _verifikasi(_calon())
        assert lolos[0].sasaran == ""


class TestAngkaDefinisiTerkait:
    """Mempertajam "Perbaiki di: Pasal 1" jadi angka definisinya.

    Ditambahkan 26 Sep 2026 sesudah penelaah melihat komentar pada PMK PPh 21
    yang cuma berkata "Perbaiki di: Pasal 1 (Ketentuan Umum)" — padahal Pasal
    1 naskah itu memuat empat belas definisi, dan penelaah harus menebak
    sendiri yang mana.
    """

    def _daftar(self):
        pohon = _pohon()
        return ambil_definisi(pohon)

    def test_istilah_di_dalam_kutipan_disebut_angkanya(self):
        angka = tahap5_verifikasi.angka_definisi_terkait(
            "Pengguna Barang wajib mengajukan permohonan", self._daftar()
        )
        assert angka == ["angka 1 (Pengguna Barang)"]

    def test_diurutkan_menurut_nomor_angka_bukan_urutan_kalimat(self):
        """Penelaah membaca Pasal 1 dari atas ke bawah, bukan mengikuti
        urutan kata di kalimat yang ditandai."""
        paragraf = [
            ParagrafInput(index=i, teks=t)
            for i, t in enumerate(
                _BARIS[:12]
                + [
                    "1. Pengguna Barang adalah pejabat pemegang kewenangan.",
                    "2. Sistem Informasi adalah aplikasi pencatatan.",
                    "Pasal 2",
                    "Sistem Informasi dipakai Pengguna Barang untuk mencatat.",
                ]
            )
        ]
        daftar = ambil_definisi(bangun_pohon(paragraf))
        angka = tahap5_verifikasi.angka_definisi_terkait(
            "Sistem Informasi dipakai Pengguna Barang", daftar
        )
        assert angka == ["angka 1 (Pengguna Barang)", "angka 2 (Sistem Informasi)"]

    def test_istilah_yang_TIDAK_muncul_tidak_disebut(self):
        assert (
            tahap5_verifikasi.angka_definisi_terkait(
                "permohonan diselesaikan tepat waktu", self._daftar()
            )
            == []
        )

    def test_huruf_besar_kecil_DIBEDAKAN(self):
        """Istilah berdefinisi ditulis berhuruf awal kapital (butir 67 KMK
        527). Mencocokkan tanpa peduli kapital akan menangkap kata biasa yang
        kebetulan sama bunyinya — 'pengguna barang' di kalimat lepas bukan
        rujukan ke istilah berdefinisi."""
        assert (
            tahap5_verifikasi.angka_definisi_terkait(
                "pengguna barang wajib mengajukan", self._daftar()
            )
            == []
        )

    def test_daftar_definisi_gagal_tidak_meledak(self):
        paragraf = [ParagrafInput(index=0, teks="Naskah tanpa Pasal 1.")]
        daftar = ambil_definisi(bangun_pohon(paragraf))
        assert tahap5_verifikasi.angka_definisi_terkait("apa pun", daftar) == []


class TestSasaranParagraf:
    """Nomor paragraf sasaran — yang dipakai tombol "Lompat ke Perbaikan"."""

    def test_sasaran_sah_membawa_nomor_paragrafnya(self):
        lolos, _ = _verifikasi(_calon(sasaran="pasal-1"))
        assert lolos[0].sasaran_paragraf is not None

    def test_sasaran_kosong_tidak_membawa_nomor(self):
        """Tanpa sasaran, tombol lompatnya tidak boleh digambar sama sekali."""
        lolos, _ = _verifikasi(_calon())
        assert lolos[0].sasaran == ""
        assert lolos[0].sasaran_paragraf is None

    def test_sasaran_karangan_tidak_membawa_nomor(self):
        lolos, _ = _verifikasi(_calon(sasaran="pasal-99"))
        assert lolos[0].sasaran_paragraf is None

    def test_singkatan_yang_TERKANDUNG_di_singkatan_lain_tidak_ikut_ditunjuk(self):
        """SALAH TUNJUK YANG TERBUKTI, PMK 104 Tahun 2025, 27 Sep 2026.

        Teks yang ditandai "RPKBUNP SPAN", dan panel menyuruh penelaah
        memperbaiki "Pasal 1 angka 2 (BUN)" — karena "BUN" memang terkandung
        di dalam "RPK-BUN-P". Naskah hukum penuh jebakan begini: BUN di dalam
        RPKBUNP, PA di dalam KPA, SPM di dalam SPM-LS.

        Menunjuk angka yang salah lebih buruk daripada tidak menunjuk sama
        sekali.
        """
        daftar = ambil_definisi(_pohon())
        assert daftar.gagal is None

        terkait = tahap5_verifikasi.definisi_terkait(
            "penyaluran dana melalui RPKBUNP SPAN", daftar
        )
        assert [istilah for _, istilah, _ in terkait] == []

        # Penjaga sisi sebaliknya: istilah yang BERDIRI SENDIRI tetap ketemu.
        terkait = tahap5_verifikasi.definisi_terkait(
            "Pengguna Barang wajib mengajukan permohonan", daftar
        )
        assert [istilah for _, istilah, _ in terkait] == ["Pengguna Barang"]

    def test_lompatnya_ke_ANGKA_definisinya_bukan_pangkal_pasal_1(self):
        """KAIDAH YANG MENJAGA TOMBOL "Lompat ke Perbaikan".

        Dilaporkan penelaah 26 Sep 2026: tombolnya mendarat di "Pasal 1",
        bukan di angka yang dipersoalkan — pada naskah yang Pasal 1-nya
        belasan definisi, itu masih menyisakan pekerjaan menggulir dan
        menebak.

        Kalau suatu hari lompatannya dikembalikan ke pangkal pasal, tes ini
        yang berbunyi.
        """
        pohon = _pohon()
        pangkal = pohon.cari("pasal-1").paragraf_mulai
        angka = pohon.cari("pasal-1-angka-1").paragraf_mulai
        assert angka != pangkal, "fixture-nya tidak menguji apa pun"

        lolos, _ = _verifikasi(
            _calon(
                sasaran="pasal-1",
                teks_asli="Pengguna Barang wajib mengajukan permohonan",
            )
        )
        assert lolos[0].sasaran_paragraf == angka
        assert "angka 1 (Pengguna Barang)" in lolos[0].sasaran


class TestPenghapusan:
    def test_F2_003_lahir_sebagai_penghapusan(self):
        """Definisi yang tidak pernah dipakai tidak punya rumusan pengganti
        yang masuk akal — dicoret merah, tanpa hijau."""
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        temuan = jalankan_mekanis(pohon, ambil_definisi(pohon), paragraf, ["F2-003"])
        hapus = [t for t in temuan if t.aturan_id == "F2-003"]
        assert hapus, "F2-003 seharusnya menemukan 'Sistem Informasi'"
        assert hapus[0].jenis_tanda == JenisTanda.PENGHAPUSAN
        assert hapus[0].usulan_rumusan is None

    def test_aturan_mekanis_lain_tetap_catatan(self):
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        temuan = jalankan_mekanis(pohon, ambil_definisi(pohon), paragraf, None)
        for t in temuan:
            if t.aturan_id != "F2-003":
                assert t.jenis_tanda != JenisTanda.PENGHAPUSAN


class TestLayakDicarikan:
    def test_yang_sudah_punya_usulan_dilewati(self):
        assert not korpus_rumusan.layak_dicarikan(_calon(usulan_rumusan="apa pun"))

    def test_kutipan_kosong_dilewati(self):
        assert not korpus_rumusan.layak_dicarikan(_calon(teks_asli="   "))

    def test_kutipan_terlalu_panjang_dilewati(self):
        """Penggantinya pasti ditolak `usulan_harfiah`, jadi membayarinya
        satu pencarian korpus cuma membuang uang."""
        assert not korpus_rumusan.layak_dicarikan(_calon(teks_asli="x" * 201))

    def test_calon_biasa_layak(self):
        assert korpus_rumusan.layak_dicarikan(_calon())


class TestLangkah6c:
    def _korpus(self, *sebutan, kali: int = 1):
        """`kali` banyaknya pencarian yang akan dilayani — KorpusPalsu memakai
        antrean, jadi tes berulang perlu menyiapkan sebanyak pemanggilannya."""
        hasil = HasilCari(
            pembanding=[
                Pembanding(
                    bentuk=s.split(" ", 1)[0],
                    nomor=s.split(" ", 1)[1],
                    judul="Tata Cara Penggunaan",
                    pasal="pasal-14",
                    potongan="Pengguna Barang mengajukan permohonan kepada Menteri.",
                    status="Berlaku",
                )
                for s in sebutan
            ]
        )
        return KorpusPalsu([hasil.model_copy(deep=True) for _ in range(kali)])

    def _jalan(self, jawaban: dict, *sebutan):
        calon = _calon()
        klien = KlienPalsu([json.dumps(jawaban, ensure_ascii=False)])
        korpus_rumusan.cari_rumusan(
            calon,
            _pohon(),
            self._korpus(*sebutan),
            PerapalPalsu(),
            klien,
            Ongkos(),
        )
        return calon

    def test_usulan_sah_terpasang_berikut_sumbernya(self):
        calon = self._jalan(
            {
                "usulan_rumusan": "wajib mengajukan permohonan kepada Menteri",
                "peraturan": "PMK 40/2024",
                "saran": "Sebutkan kepada siapa permohonan diajukan.",
                "skor": 0.9,
            },
            "PMK 40/2024",
        )
        assert calon.usulan_rumusan == "wajib mengajukan permohonan kepada Menteri"
        assert calon.pembanding == "PMK 40/2024"
        assert "PMK 40/2024" in calon.pembanding_sah

    def test_peraturan_di_luar_hasil_pencarian_tidak_dipakai(self):
        """KAIDAH YANG MENJAGA SELURUH LANGKAH 6c.

        Model menyebut peraturan yang tidak pernah dikirimkan kepadanya —
        artinya ia menyebutnya dari ingatan. Usulannya dibuang di sini, bukan
        dibiarkan lewat untuk digugurkan Langkah 5, supaya calon tidak
        terlanjur membawa pembanding yang menggugurkan temuannya seluruhnya.
        """
        calon = self._jalan(
            {
                "usulan_rumusan": "wajib mengajukan permohonan kepada Menteri",
                "peraturan": "PMK 99/1999",
                "skor": 0.9,
            },
            "PMK 40/2024",
        )
        assert calon.usulan_rumusan == ""
        assert calon.pembanding == ""

    def test_nama_berikut_judulnya_tetap_diterima(self):
        calon = self._jalan(
            {
                "usulan_rumusan": "wajib mengajukan permohonan kepada Menteri",
                "peraturan": "PMK 40/2024 tentang Tata Cara Penggunaan",
                "skor": 0.9,
            },
            "PMK 40/2024",
        )
        assert calon.pembanding == "PMK 40/2024"

    def test_model_mengosongkan_bukan_kegagalan(self):
        calon = self._jalan(
            {"usulan_rumusan": "", "peraturan": "", "skor": 0.0}, "PMK 40/2024"
        )
        assert calon.usulan_rumusan == ""
        assert calon.pembanding == ""
        assert calon.skor == 0.9  # temuannya sendiri tidak ikut turun

    def test_tanpa_pembanding_korpus_model_tidak_dipanggil(self):
        """Bertanya tanpa bahan cuma mengundang karangan — dan membayar."""
        calon = _calon()
        klien = KlienPalsu([])
        korpus_rumusan.cari_rumusan(
            calon, _pohon(), KorpusPalsu([HasilCari()]), PerapalPalsu(), klien, Ongkos()
        )
        assert klien.diminta == []
        assert calon.usulan_rumusan == ""

    def test_batas_per_dokumen_ditaati_dan_dicatat(self):
        """Batas biaya. Yang kelebihan TIDAK diam-diam dilewati — catatannya
        masuk daftar gugur, supaya batas tidak nanti disangka bug."""
        banyak = [_calon() for _ in range(korpus_rumusan.BATAS_RUMUSAN + 4)]
        jawab = json.dumps(
            {
                "usulan_rumusan": "wajib mengajukan permohonan kepada Menteri",
                "peraturan": "PMK 40/2024",
                "skor": 0.9,
            }
        )
        klien = KlienPalsu([jawab] * len(banyak))
        catatan = korpus_rumusan.lengkapi(
            banyak,
            _pohon(),
            self._korpus("PMK 40/2024", kali=len(banyak)),
            PerapalPalsu(),
            klien,
            Ongkos(),
        )
        assert len(klien.diminta) == korpus_rumusan.BATAS_RUMUSAN
        assert any("batas" in c for c in catatan)

    def test_langkah_yang_berjalan_tanpa_hasil_tetap_tercatat(self):
        """Langkah yang berjalan tanpa hasil dan langkah yang tidak pernah
        berjalan terlihat sama dari luar — dan bedanya menentukan saat
        menelusuri kenapa tidak ada temuan hijau."""
        satu = [_calon()]
        klien = KlienPalsu([json.dumps({"usulan_rumusan": "", "peraturan": ""})])
        catatan = korpus_rumusan.lengkapi(
            satu,
            _pohon(),
            self._korpus("PMK 40/2024"),
            PerapalPalsu(),
            klien,
            Ongkos(),
        )
        assert any("1 temuan dicarikan rumusan, 0 dapat" in c for c in catatan)

    def test_tidak_ada_yang_layak_tidak_meninggalkan_catatan(self):
        """Tidak ada yang dibayar berarti tidak ada yang perlu dilaporkan."""
        assert korpus_rumusan.lengkapi(
            [_calon(usulan_rumusan="sudah ada")],
            _pohon(),
            self._korpus("PMK 40/2024"),
            PerapalPalsu(),
            KlienPalsu([]),
            Ongkos(),
        ) == []

    def test_yang_tidak_layak_tidak_menghabiskan_jatah(self):
        """Calon yang sudah punya usulan dilewati tanpa dibayar, jadi jatahnya
        utuh untuk yang benar-benar memerlukannya."""
        campur = [_calon(usulan_rumusan="sudah ada") for _ in range(10)] + [_calon()]
        klien = KlienPalsu(
            [json.dumps({"usulan_rumusan": "x", "peraturan": "PMK 40/2024", "skor": 0.9})]
        )
        korpus_rumusan.lengkapi(
            campur,
            _pohon(),
            self._korpus("PMK 40/2024"),
            PerapalPalsu(),
            klien,
            Ongkos(),
        )
        assert len(klien.diminta) == 1

    def test_skor_temuan_tidak_pernah_dinaikkan(self):
        """Temuan yang lolos ambang karena usulannya bagus adalah cara paling
        halus untuk salah tandai."""
        calon = self._jalan(
            {
                "usulan_rumusan": "wajib mengajukan permohonan kepada Menteri",
                "peraturan": "PMK 40/2024",
                "skor": 1.0,
            },
            "PMK 40/2024",
        )
        assert calon.skor == 0.9
