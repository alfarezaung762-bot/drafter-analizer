"""Rekonsiliasi Fase 1 ↔ Fase 2, dan Ekspor Tahap 0. TANPA jaringan.

Ditetapkan penelaah 23 Sep 2026: **AI membaca, KODE yang memutuskan.** Model
boleh tahu apa yang sudah ditemukan pemeriksaan format, boleh berkeberatan,
tetapi TIDAK PERNAH menghapus temuan yang kesalahannya sudah terbukti.

Tes yang paling menentukan di berkas ini:
`TestKeberatan.test_keberatan_TIDAK_menghapus_temuan` — kalau suatu hari ada
yang membuat model bisa membatalkan temuan, tes itu yang berbunyi.
"""

import json

from app.bersama.llm import KlienPalsu, Ongkos
from app.fase2 import tahap2_baca, tahap5_verifikasi
from app.fase2.ekspor_tahap0 import susun_ekspor
from app.fase2.tahap0_definisi import ambil_definisi
from app.fase2.tahap0_struktur import bangun_pohon
from app.fase2.tahap1_saring import saring
from app.models.pekerjaan import CalonTemuan
from app.models.temuan import (
    JenisTanda,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    StatusTemuan,
    Temuan,
)

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
    def test_temuan_fase1_dilampirkan_pada_satuannya(self):
        pohon = bangun_pohon(_paragraf())
        pasal2 = pohon.cari("pasal-2")
        t = _temuan(3, 14, "wajib mengajukan permohonan", "F1-008")
        bahan = tahap2_baca.susun_bahan([pasal2], pohon, "KONTEKS", [t])
        assert "(SUDAH DITEMUKAN, T3)" in bahan
        assert "Ejaan tidak baku." in bahan

    def test_temuan_di_satuan_LAIN_tidak_ikut(self):
        """Melampirkan temuan yang bukan miliknya cuma membingungkan model."""
        pohon = bangun_pohon(_paragraf())
        pasal2 = pohon.cari("pasal-2")
        t = _temuan(1, 7, "Undang-undang")  # di Mengingat, jauh dari pasal-2
        bahan = tahap2_baca.susun_bahan([pasal2], pohon, "KONTEKS", [t])
        assert "SUDAH DITEMUKAN" not in bahan

    def test_tanpa_temuan_fase1_bahannya_sama_seperti_dulu(self):
        pohon = bangun_pohon(_paragraf())
        pasal2 = pohon.cari("pasal-2")
        assert tahap2_baca.susun_bahan([pasal2], pohon, "K") == tahap2_baca.susun_bahan(
            [pasal2], pohon, "K", []
        )


class TestKeberatan:
    def _jalan(self, jawaban_keberatan, temuan_fase1):
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        daftar = ambil_definisi(pohon)
        dibaca = saring(pohon).dibaca
        jawab = {
            "baris": [{"satuan_id": s.id, "ringkasan": "r"} for s in dibaca],
            "keberatan": jawaban_keberatan,
        }
        klien = KlienPalsu([json.dumps(jawab, ensure_ascii=False)])
        tahap2_baca.baca_satuan(
            pohon, daftar, dibaca, klien, Ongkos(), temuan_fase1=temuan_fase1
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


class TestEksporTahap0:
    def test_yang_dibuang_ditaruh_paling_atas_dengan_teksnya(self):
        """Inilah alasan ekspor ini dibuat — satuan yang dibuang tidak
        meninggalkan jejak apa pun di panel."""
        teks = susun_ekspor(_paragraf())
        i_buang = teks.index("YANG DIBUANG")
        assert i_buang < teks.index("YANG DIBACA")
        assert i_buang < teks.index("POHON SATUAN")
        # teks utuh satuan yang dibuang ikut, bukan cuma id-nya
        assert "Undang-undang Nomor 1 Tahun 2004" in teks

    def test_memuat_muatan_panggilan_apa_adanya(self):
        teks = susun_ekspor(_paragraf())
        assert "KONTEKS TETAP" in teks
        assert "MUATAN LANGKAH 2" in teks
        assert "== SATUAN YANG DIPERIKSA ==" in teks

    def test_penanda_ikut_ditampilkan(self):
        paragraf = [
            ParagrafInput(index=0, teks="", penanda="Pasal 5"),
            ParagrafInput(index=1, teks="Isi ayat.", penanda="(1)"),
        ]
        teks = susun_ekspor(paragraf)
        assert "'Pasal 5'" in teks
        assert "2 berpenanda nomor otomatis Word" in teks

    def test_naskah_yang_ditolak_tetap_diekspor_berikut_alasannya(self):
        """Justru naskah yang ditolak itulah yang paling perlu diperiksa."""
        kmk = [
            ParagrafInput(index=i, teks=t)
            for i, t in enumerate(
                [
                    "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
                    "TENTANG",
                    "PEMBENTUKAN TIM",
                    "MENTERI KEUANGAN REPUBLIK INDONESIA,",
                    "MEMUTUSKAN:",
                    "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PEMBENTUKAN TIM.",
                    "KESATU : Membentuk Tim.",
                ]
            )
        ]
        teks = susun_ekspor(kmk)
        assert "FASE 2 TIDAK DIJALANKAN" in teks
        assert "diktum" in teks.lower()

    def test_memakai_kode_yang_sama_dengan_yang_dikirim(self):
        """Ekspor yang menyusun ulang bisa menyimpang dari yang dikirim."""
        paragraf = _paragraf()
        pohon = bangun_pohon(paragraf)
        daftar = ambil_definisi(pohon)
        konteks = tahap2_baca.susun_konteks_tetap(pohon, daftar)
        assert konteks in susun_ekspor(paragraf)
