"""Nomor otomatis Word — regresi untuk cacat yang ditemukan 23 Sep 2026.

Pada naskah PMK sungguhan (PMK 18 Tahun 2026), 585 dari 974 paragraf bernomor
otomatis dan 110 di antaranya TEKSNYA KOSONG SAMA SEKALI: seluruh isinya
nomor. Karena `paragraph.text` di Word tidak memuat nomor otomatis, backend
menerima dokumen tanpa satu pun "Pasal" — lalu menuduh ayat yang jelas-jelas
ada di layar sebagai tidak ada.

Dua tes paling penting di berkas ini:

  - TestPenandaKeStruktur.test_pasal_dan_ayat_yang_TEKSNYA_KOSONG_terbaca
  - TestPenandaTidakMenggeserPenandaan.test_offset_dihitung_terhadap_teks_saja

Yang kedua menjaga kaidah yang membuat seluruh penandaan bisa dipercaya:
offset dihitung terhadap `teks`, bukan `utuh`. Kalau suatu hari ada yang
menempel penanda ke depan teks, tes itu yang berbunyi.
"""

from app.fase2.mekanis_konsistensi import jalankan_mekanis
from app.fase2.tahap0_definisi import _bentuk_pendek, ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.models.satuan import JenisSatuan
from app.models.temuan import ParagrafInput

_KEPALA = [
    ("", "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA"),
    ("", "NOMOR 12 TAHUN 2026"),
    ("", "TENTANG"),
    ("", "TATA CARA PENETAPAN STATUS PENGGUNAAN"),
    ("", "DENGAN RAHMAT TUHAN YANG MAHA ESA"),
    ("", "MENTERI KEUANGAN REPUBLIK INDONESIA,"),
    ("", "MEMUTUSKAN:"),
    ("", "Menetapkan : PERATURAN MENTERI KEUANGAN TENTANG TATA CARA."),
]


def _dok(baris: list[tuple[str, str]]) -> list[ParagrafInput]:
    """Tiap baris: (penanda, teks) — persis bentuk yang dikirim Office.js."""
    return [
        ParagrafInput(index=i, teks=t, penanda=p, tingkat=0 if p else -1)
        for i, (p, t) in enumerate(baris)
    ]


class TestUtuh:
    def test_penanda_digabung_dengan_satu_spasi(self):
        p = ParagrafInput(index=0, teks="Isi ayat.", penanda="(2)")
        assert p.utuh == "(2) Isi ayat."

    def test_paragraf_yang_teksnya_kosong_jadi_nomornya_saja(self):
        """110 paragraf PMK 18 berbentuk begini."""
        p = ParagrafInput(index=0, teks="", penanda="Pasal 5")
        assert p.utuh == "Pasal 5"

    def test_tanpa_penanda_utuh_sama_dengan_teks(self):
        p = ParagrafInput(index=0, teks="Isi biasa.")
        assert p.utuh == "Isi biasa."

    def test_teks_TIDAK_ikut_berubah(self):
        """Yang dipakai menghitung offset penandaan tidak boleh tersentuh."""
        p = ParagrafInput(index=0, teks="Isi ayat.", penanda="(2)")
        assert p.teks == "Isi ayat."


class TestPenandaKeStruktur:
    def test_pasal_dan_ayat_yang_TEKSNYA_KOSONG_terbaca(self):
        """Bentuk persis seperti PMK 18: numId 274 = 'Pasal %1' + '(%2)'."""
        pohon = bangun_pohon(
            _dok(
                _KEPALA
                + [
                    ("BAB I", ""),
                    ("", "KETENTUAN UMUM"),
                    ("Pasal 1", ""),
                    ("", "Dalam Peraturan Menteri ini yang dimaksud dengan:"),
                    ("1.", "Pengelola Barang adalah pejabat yang berwenang."),
                    ("Pasal 2", ""),
                    ("(1)", "Pengguna Barang mengajukan permohonan."),
                    ("(2)", "Permohonan disampaikan secara elektronik."),
                ]
            )
        )
        assert pohon.gagal is None
        assert [s.nomor for s in pohon.semua(JenisSatuan.PASAL)] == ["1", "2"]
        assert pohon.ada("pasal-2-ayat-1")
        assert pohon.ada("pasal-2-ayat-2")
        assert pohon.cari("pasal-2-ayat-2").teks == "Permohonan disampaikan secara elektronik."

    def test_rujukan_ke_ayat_bernomor_otomatis_TIDAK_lagi_salah_tandai(self):
        """Cacat yang dilihat penelaah di Word, 23 Sep 2026.

        Komentar berbunyi "Merujuk Pasal 2 ayat (2), tetapi Pasal 2 ayat (2)
        tidak ada di naskah ini" — padahal ayatnya jelas ada di layar. Yang
        tidak ada cuma nomornya di dalam `paragraph.text`.
        """
        paragraf = _dok(
            _KEPALA
            + [
                ("Pasal 2", ""),
                ("(1)", "Pengguna Barang mengajukan permohonan."),
                ("(2)", "Permohonan disampaikan secara elektronik."),
                ("Pasal 3", ""),
                ("(1)", "Pegawai sebagaimana dimaksud pada Pasal 2 ayat (2) berupa:"),
            ]
        )
        pohon = bangun_pohon(paragraf)
        temuan = jalankan_mekanis(pohon, ambil_definisi(pohon), paragraf, ["F2-001"])
        assert temuan == [], [t.catatan for t in temuan]

    def test_TANPA_penanda_kasus_yang_sama_MEMANG_gagal(self):
        """Bukti bahwa penandanyalah yang menyembuhkan, bukan kebetulan."""
        pohon = bangun_pohon(
            [
                ParagrafInput(index=i, teks=t)
                for i, (_, t) in enumerate(
                    _KEPALA
                    + [
                        ("Pasal 2", ""),
                        ("(1)", "Pengguna Barang mengajukan permohonan."),
                        ("(2)", "Permohonan disampaikan secara elektronik."),
                    ]
                )
            ]
        )
        assert not pohon.ada("pasal-2-ayat-2")

    def test_huruf_bertingkat_di_bawah_ayat_terbaca(self):
        pohon = bangun_pohon(
            _dok(
                _KEPALA
                + [
                    ("Pasal 4", ""),
                    ("(1)", "Jenis kantor terdiri atas:"),
                    ("a.", "kantor wajib pajak besar;"),
                    ("b.", "kantor khusus."),
                ]
            )
        )
        assert pohon.ada("pasal-4-ayat-1-huruf-a")
        assert pohon.ada("pasal-4-ayat-1-huruf-b")


class TestPenandaTidakMenggeserPenandaan:
    def test_offset_dihitung_terhadap_teks_saja(self):
        """KAIDAH YANG MENJAGA SELURUH PENANDAAN.

        Kalau penanda ikut ditempel ke teks, `offset_mulai` bergeser sepanjang
        penanda, dan tiap sorotan di Word mendarat meleset sejauh itu.
        """
        paragraf = _dok(
            _KEPALA
            + [
                ("Pasal 1", ""),
                ("", "Dalam Peraturan Menteri ini yang dimaksud dengan:"),
                ("1.", "Sistem Informasi adalah rangkaian perangkat."),
                ("Pasal 2", ""),
                ("(1)", "Permohonan diselesaikan paling lambat 30 (tiga belas) Hari."),
            ]
        )
        pohon = bangun_pohon(paragraf)
        temuan = jalankan_mekanis(pohon, ambil_definisi(pohon), paragraf, ["F2-007"])
        assert len(temuan) == 1
        t = temuan[0]
        asal = next(p for p in paragraf if p.index == t.lokasi.paragraf_index)
        potong = asal.teks[t.lokasi.offset_mulai : t.lokasi.offset_mulai + t.lokasi.panjang]
        assert potong == t.lokasi.teks_asli == "30 (tiga belas)"


class TestBentukPendekIstilah:
    """Cacat kedua yang muncul dari naskah nyata, 23 Sep 2026.

    "Direktur Jenderal Pajak yang selanjutnya disebut Direktur Jenderal adalah
    …" terbaca istilahnya sebagai rangkaian panjang itu, lalu F2-003 menuduh
    definisinya tidak pernah dipakai — padahal naskah memakai bentuk pendeknya.
    """

    def test_disebut_diambil_bentuk_pendeknya(self):
        assert (
            _bentuk_pendek("Direktur Jenderal Pajak yang selanjutnya disebut Direktur Jenderal")
            == "Direktur Jenderal"
        )

    def test_disingkat_juga(self):
        assert _bentuk_pendek("Barang Milik Negara yang selanjutnya disingkat BMN") == "BMN"

    def test_istilah_biasa_tidak_diapa_apakan(self):
        assert _bentuk_pendek("Pengelola Barang") == "Pengelola Barang"

    def test_f2_003_tidak_lagi_salah_tandai(self):
        paragraf = _dok(
            _KEPALA
            + [
                ("Pasal 1", ""),
                ("", "Dalam Peraturan Menteri ini yang dimaksud dengan:"),
                ("1.", "Direktur Jenderal Pajak yang selanjutnya disebut Direktur Jenderal adalah pimpinan."),
                ("Pasal 2", ""),
                ("(1)", "Direktur Jenderal menetapkan pembagian wilayah kerja."),
            ]
        )
        pohon = bangun_pohon(paragraf)
        daftar = ambil_definisi(pohon)
        assert daftar.istilah_saja() == ["Direktur Jenderal"]
        assert jalankan_mekanis(pohon, daftar, paragraf, ["F2-003"]) == []


class TestBagianBukanKalimatBiasa:
    """Cacat yang baru terlihat sesudah parser membaca naskah PMK sungguhan.

    PMK organisasi penuh unit bernama "Bagian Umum", "Bagian Kepegawaian".
    Pola lama `^Bagian\s+(\w+)` membaca kalimat "Bagian Umum mempunyai tugas
    …" sebagai JUDUL BAGIAN, lalu judul itu MENUTUP pasal yang baru dibuka dan
    menelan isinya. Pada PMK 18 Tahun 2026 beberapa pasal berakhir kosong dan
    isinya tidak pernah sampai ke model.
    """

    def _pohon(self, tambahan):
        return bangun_pohon(_dok(_KEPALA + tambahan))

    def test_kalimat_berawalan_Bagian_TIDAK_menutup_pasal(self):
        pohon = self._pohon(
            [
                ("Pasal 8", ""),
                ("", "Bagian Umum mempunyai tugas melaksanakan urusan kepegawaian."),
                ("Pasal 9", ""),
                ("", "Isi pasal sembilan."),
            ]
        )
        pasal8 = pohon.cari("pasal-8")
        assert pasal8 is not None
        assert pasal8.teks.startswith("Bagian Umum mempunyai tugas")
        assert pohon.semua(JenisSatuan.BAGIAN) == []

    def test_judul_bagian_sungguhan_tetap_terbaca(self):
        """Penjagaan yang kebablasan mematikan pembacaan Bagian yang sah."""
        pohon = self._pohon(
            [
                ("BAB II", ""),
                ("", "SUSUNAN ORGANISASI"),
                ("Bagian Kesatu", ""),
                ("", "Kantor Wilayah"),
                ("Pasal 3", ""),
                ("", "Isi pasal tiga."),
            ]
        )
        bagian = pohon.semua(JenisSatuan.BAGIAN)
        assert len(bagian) == 1
        assert bagian[0].nomor.lower() == "kesatu"

    def test_bagian_bilangan_majemuk_terbaca(self):
        pohon = self._pohon([("Bagian Kedua Belas", ""), ("", "Judulnya"), ("Pasal 1", ""), ("", "Isi.")])
        assert len(pohon.semua(JenisSatuan.BAGIAN)) == 1

    def test_tidak_ada_pasal_yang_isinya_hilang(self):
        """Ukuran yang sebenarnya: tiap pasal harus punya isi, sendiri atau di anaknya."""
        pohon = self._pohon(
            [
                ("Pasal 8", ""),
                ("", "Bagian Umum mempunyai tugas melaksanakan urusan."),
                ("Pasal 9", ""),
                ("(1)", "Bagian Keuangan mempunyai tugas melakukan pembayaran."),
            ]
        )
        for p in pohon.semua(JenisSatuan.PASAL):
            assert pohon.teks_lengkap(p.id), f"{p.id} kehilangan isinya"
