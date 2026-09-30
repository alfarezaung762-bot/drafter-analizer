"""Rekonsiliasi Fase 1 ↔ Fase 2. TANPA jaringan.

Ditetapkan penelaah 23 Sep 2026: **AI membaca, KODE yang memutuskan.** Model
boleh tahu apa yang sudah ditemukan pemeriksaan format, boleh berkeberatan,
tetapi TIDAK PERNAH menghapus temuan yang kesalahannya sudah terbukti.

Tes yang paling menentukan di berkas ini:
`TestKeberatan.test_keberatan_TIDAK_menghapus_temuan` — kalau suatu hari ada
yang membuat model bisa membatalkan temuan, tes itu yang berbunyi.
"""

import json

from app.bersama.llm import KlienPalsu, Ongkos
from app.models.pekerjaan import CalonTemuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)
from app.telaah import tahap3_cari_dugaan, tahap5_verifikasi
from app.telaah.tahap1_parser.definisi import ambil_definisi
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import susun_bahan

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
]


def _paragraf() -> list[ParagrafInput]:
    return [ParagrafInput(index=i, teks=t) for i, t in enumerate(_BARIS)]


def _temuan(nomor: int, paragraf_index: int, teks_asli: str, aturan="F1-005") -> Temuan:
    asal = _BARIS[paragraf_index]
    return Temuan(
        id=f"f1-{nomor}",
        nomor=nomor,
        aturan_id=aturan,
        fase=1,
        jenis_tanda=JenisTanda.CATATAN,
        lokasi=LokasiTemuan(
            paragraf_index=paragraf_index,
            offset_mulai=asal.index(teks_asli),
            panjang=len(teks_asli),
            teks_asli=teks_asli,
        ),
        catatan="Ejaan tidak baku.",
        rujukan=RujukanTemuan(sumber="KMK 527", butir="33", kutipan="…", pdf_url="x"),
        status=StatusTemuan.BELUM_DITINJAU,
    )


class TestTemuanIkutKeModel:
    def test_temuan_fase1_ikut_di_bahan_dengan_letak_satuannya(self):
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        bahan = susun_bahan(paragraf, pohon, [t])
        assert "(T3) [pasal-2] pada teks 'wajib mengajukan permohonan': Ejaan tidak baku." in bahan.teks

    def test_tanpa_temuan_fase1_tidak_ada_bloknya(self):
        paragraf = _paragraf()
        bahan = susun_bahan(paragraf, bangun_pohon(paragraf))
        assert "TEMUAN PEMERIKSAAN FORMAT" not in bahan.teks


class TestKeberatan:
    """Keberatan dikumpulkan di panggilan lintas naskah tahap 3."""

    def _jalan(self, jawaban_keberatan, temuan_fase1):
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        bahan = susun_bahan(paragraf, pohon, temuan_fase1)
        pg = tahap3_cari_dugaan.panggilan_lintas(bahan, ["tabrakan"], ada_fase1=True)
        jawab = json.dumps({"dugaan": [], "keberatan": jawaban_keberatan}, ensure_ascii=False)
        tahap3_cari_dugaan.cari_dugaan(
            [pg], pohon, bahan, KlienPalsu([jawab]), Ongkos(), temuan_fase1=temuan_fase1
        )

    def test_keberatan_menempel_ke_temuan_yang_benar(self):
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        self._jalan([{"nomor": 3, "alasan": "Frasa itu kutipan dari peraturan lain."}], [t])
        assert t.catatan_ai == "Frasa itu kutipan dari peraturan lain."

    def test_keberatan_TIDAK_menghapus_temuan(self):
        """KAIDAH YANG MENJAGA SELURUH REKONSILIASI.

        Keyakinan model tidak boleh menghapus bukti. Temuan yang hilang
        diam-diam adalah kegagalan yang paling sulit diketahui penelaah.
        """
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        semula = (t.id, t.nomor, t.aturan_id, t.catatan, t.lokasi.teks_asli)
        self._jalan([{"nomor": 3, "alasan": "menurut saya ini keliru"}], [t])
        assert (t.id, t.nomor, t.aturan_id, t.catatan, t.lokasi.teks_asli) == semula
        assert t.status == StatusTemuan.BELUM_DITINJAU

    def test_keberatan_bernomor_karangan_diabaikan(self):
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        self._jalan([{"nomor": 99, "alasan": "x"}], [t])
        assert t.catatan_ai == ""

    def test_keberatan_tanpa_alasan_diabaikan(self):
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        self._jalan([{"nomor": 3, "alasan": "   "}], [t])
        assert t.catatan_ai == ""


class TestPenyaringTumpangTindih:
    def _calon(self, teks_asli: str) -> CalonTemuan:
        return CalonTemuan(
            aturan_id="F2-102",
            satuan_id="pasal-2",
            alasan="tidak jelas pemikulnya",
            teks_asli=teks_asli,
            skor=0.95,
        )

    def _jalan(self, calon, temuan_ada):
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        return tahap5_verifikasi.verifikasi(
            [calon], pohon, ambil_definisi(pohon), paragraf, 0.7, temuan_ada=temuan_ada
        )

    def test_rentang_yang_bertindihan_dibuang(self):
        lama = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        lolos, gugur = self._jalan(self._calon("mengajukan permohonan"), [lama])
        assert lolos == []
        assert "bertindihan dengan T3" in gugur[0]

    def test_rentang_yang_TIDAK_bertindihan_tetap_lolos(self):
        lama = _temuan(3, 14, "Pengguna Barang", "F1-008")
        lolos, _ = self._jalan(self._calon("paling lambat 30 (tiga puluh) hari"), [lama])
        assert len(lolos) == 1

    def test_paragraf_berbeda_tidak_dianggap_bertindihan(self):
        lama = _temuan(1, 7, "Undang-undang")
        lolos, _ = self._jalan(self._calon("wajib mengajukan permohonan"), [lama])
        assert len(lolos) == 1

    def test_tanpa_temuan_lama_semua_lolos(self):
        lolos, _ = self._jalan(self._calon("wajib mengajukan permohonan"), None)
        assert len(lolos) == 1
