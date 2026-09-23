"""Ekspor Tahap 3 — peta Langkah 2 dan dugaan Langkah 3. TANPA jaringan.

Tes yang paling menentukan di berkas ini:
`TestTidakMenyimpang.test_bahan_persis_sama_dengan_yang_dikirim` — ekspor yang
menyusun ulang bisa menyimpang dari yang sebenarnya dikirim ke model, dan
ekspor yang berbohong lebih berbahaya daripada tidak ada ekspor: ia dipakai
memutuskan bahwa sesuatu BUKAN masalah.
"""

from app.db import simpanan
from app.fase2 import tahap2_baca, tahap3_menalar
from app.fase2.ekspor_tahap3 import susun_ekspor_tahap3
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import saring
from app.models.pekerjaan import BarisPeta, Dugaan
from app.models.temuan import ParagrafInput

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
    "Pasal 2",
    "Pengguna Barang wajib mengajukan permohonan paling lambat 30 (tiga puluh) hari.",
    "Pasal 3",
    "Pengguna Barang menyampaikan laporan kepada Menteri setiap tahun.",
]


def _paragraf() -> list[ParagrafInput]:
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(_BARIS)]


_RINGKASAN = {
    "pasal-2": "Mewajibkan Pengguna Barang mengajukan permohonan.",
    "pasal-3": "Mewajibkan penyampaian laporan tahunan.",
}


def _peta() -> list[BarisPeta]:
    """Peta LENGKAP — satu baris untuk tiap satuan yang lolos Langkah 1.

    Diturunkan dari `saring()`, bukan ditulis tangan, supaya tes "tidak ada
    satuan yang hilang dari peta" menguji keadaan yang sebenarnya dan tidak
    ikut berubah setiap kali penyaringnya disetel.
    """
    pohon = bangun_pohon(_paragraf())
    return [
        BarisPeta(
            satuan_id=s.id,
            ringkasan=_RINGKASAN.get(s.id, "Ringkasan satuan ini."),
            memuat_norma=True,
            istilah_dipakai=["Pengguna Barang"] if s.id == "pasal-2" else [],
            dugaan=(
                "batas waktunya tidak jelas dihitung dari kapan"
                if s.id == "pasal-2"
                else ""
            ),
        )
        for s in saring(pohon).dibaca
    ]


class TestTidakMenyimpang:
    def test_bahan_persis_sama_dengan_yang_dikirim(self):
        """KAIDAH YANG MENJAGA SELURUH EKSPOR INI.

        Kalau suatu hari ada yang menyusun ulang bahan Langkah 3 di dalam
        ekspor, tes ini yang berbunyi.
        """
        paragraf, peta = _paragraf(), _peta()
        pohon = bangun_pohon(paragraf)
        konteks = tahap2_baca.susun_konteks_tetap(pohon, ambil_definisi(pohon))
        bahan = tahap3_menalar.susun_bahan(peta, konteks)
        assert bahan in susun_ekspor_tahap3(paragraf, peta)

    def test_ringkasan_tiap_satuan_ikut_utuh(self):
        teks = susun_ekspor_tahap3(_paragraf(), _peta())
        assert "Mewajibkan Pengguna Barang mengajukan permohonan." in teks
        assert "batas waktunya tidak jelas dihitung dari kapan" in teks


class TestPetaKosong:
    def test_peta_kosong_tidak_meledak_dan_menjelaskan_sebabnya(self):
        teks = susun_ekspor_tahap3(_paragraf(), [])
        assert "PETA KOSONG" in teks
        assert "F2-1xx" in teks

    def test_tanpa_paragraf_pun_tetap_menjawab(self):
        """Panel memanggil ini sebelum pekerjaan apa pun ada."""
        assert "PETA KOSONG" in susun_ekspor_tahap3([], [])


class TestHasilLangkah3:
    def test_belum_tercatat_dibedakan_dari_nihil(self):
        """Dua keadaan yang berbeda jauh, dan penelusur bug perlu membedakannya:
        dugaan hilang karena backend restart, atau Langkah 3 memang tidak
        menemukan apa-apa."""
        belum = susun_ekspor_tahap3(_paragraf(), _peta(), None)
        nihil = susun_ekspor_tahap3(_paragraf(), _peta(), [])
        assert "TIDAK TERCATAT" in belum
        assert "TIDAK TERCATAT" not in nihil
        assert "DUGAAN (0)" in nihil

    def test_dugaan_eksternal_dihitung_terpisah(self):
        """Hanya yang eksternal yang dicarikan pembanding ke OpenSearch, jadi
        angka itu yang menjelaskan kenapa Langkah 6 jalan atau diam."""
        dugaan = [
            Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="a", eksternal=False),
            Dugaan(satuan_id="pasal-3", jenis="cakupan", alasan="b", eksternal=True),
        ]
        teks = susun_ekspor_tahap3(_paragraf(), _peta(), dugaan)
        assert "DUGAAN (2)" in teks
        assert "1 dari 2 bertanda eksternal" in teks

    def test_tabrakan_menyebut_kedua_satuannya(self):
        dugaan = [
            Dugaan(
                satuan_id="pasal-2",
                satuan_lain="pasal-3",
                jenis="tabrakan",
                alasan="dua batas waktu berbeda",
            )
        ]
        assert "bertabrakan dengan : pasal-3" in susun_ekspor_tahap3(
            _paragraf(), _peta(), dugaan
        )


class TestSatuanHilangDariPeta:
    def test_satuan_lolos_saring_yang_tidak_ada_di_peta_ditandai_bug(self):
        """Satuan yang lolos Langkah 1 tetapi tidak muncul di peta berarti
        Langkah 2 gagal membacanya — dan itu tidak kelihatan dari mana pun."""
        sebagian = [b for b in _peta() if b.satuan_id != "pasal-3"]
        teks = susun_ekspor_tahap3(_paragraf(), sebagian)
        potong = teks[teks.index("LOLOS penyaring tetapi hilang dari peta") :]
        assert "INI BUG" in potong
        assert "pasal-3" in potong

    def test_peta_lengkap_menyatakan_nihil(self):
        teks = susun_ekspor_tahap3(_paragraf(), _peta())
        potong = teks[teks.index("LOLOS penyaring tetapi hilang dari peta") :]
        assert "INI BUG" not in potong
        assert "nihil" in potong


class TestSimpananDugaan:
    def setup_method(self):
        simpanan.bersihkan_memori()

    def test_daftar_kosong_tetap_tercatat(self):
        """`[]` berarti Langkah 3 berjalan dan nihil; `None` berarti belum
        pernah. Menyamakan keduanya menghilangkan satu keadaan."""
        nomor = simpanan.buat("uji.docx")
        assert simpanan.ambil_dugaan(nomor) is None
        simpanan.simpan_dugaan(nomor, [])
        assert simpanan.ambil_dugaan(nomor) == []

    def test_pekerjaan_terakhir_memilih_yang_terbaru(self):
        simpanan.buat("uji.docx")
        kedua = simpanan.buat("uji.docx")
        assert simpanan.pekerjaan_terakhir("uji.docx") == kedua

    def test_pekerjaan_terakhir_dokumen_asing_none(self):
        simpanan.buat("uji.docx")
        assert simpanan.pekerjaan_terakhir("lain.docx") is None
