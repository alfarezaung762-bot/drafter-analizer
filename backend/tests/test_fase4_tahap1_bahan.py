"""Fase 4 — Tahap 1 bahan: bukti label, peta letak, naskah berlabel, naskah berformat.

Bukti label diuji dulu dengan label parser yang PASTI benar (rancangan 5.2):
uji 2 Okt 2026 sempat salah dua kali karena "Bagian Kesatu" dibandingkan
menurut abjad dan huruf i/v/x dibaca Romawi.
"""

from pathlib import Path

import pytest

from app.models.temuan import FormatParagraf, ParagrafInput
from app.telaah.tahap1_bahan.langkah2_bukti_label import (
    buktikan,
    peta_letak,
    pohon_dari_label,
)
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import susun_naskah_berlabel
from app.telaah.tahap1_bahan.langkah7_naskah_berformat import BUTIR_KOSONG, susun_naskah_berformat
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import bangun_pohon, id_awal_satuan
from tests.naskah_uji import naskah

TEMPAT_PMK = Path(__file__).resolve().parent.parent / "tools" / "contoh" / "tempat pmk"


def _label_parser(paragraf):
    return id_awal_satuan(bangun_pohon(paragraf))


def _p(teks, i, penanda=""):
    return ParagrafInput(index=i, teks=teks, penanda=penanda)


class TestBuktiLabel:
    def test_label_parser_naskah_uji_lolos_semua(self):
        par = naskah()
        lab = _label_parser(par)
        b = buktikan(lab, par)
        assert not b.gagal and not b.tanpa_label and len(b.lolos) == len(lab)

    def test_penanda_tidak_cocok_ditolak(self):
        par = naskah()
        lab = dict(_label_parser(par))
        p = next(k for k, v in lab.items() if v == "pasal-2")
        lab[p] = "pasal-7"
        gagal = {x[1]: x[2] for x in buktikan(lab, par).gagal}
        assert "penanda tidak cocok" in gagal["pasal-7"]

    def test_label_dobel_dan_tanpa_induk_ditolak(self):
        par = [_p("Pasal 1", 0), _p("(1) satu", 1), _p("(1) satu lagi", 2), _p("(2) dua", 3)]
        b = buktikan({0: "pasal-1", 1: "pasal-1-ayat-1", 2: "pasal-1-ayat-1", 3: "pasal-9-ayat-2"}, par)
        alasan = {p: a for p, _, a in b.gagal}
        assert "label dobel" in alasan[2]
        assert "induk pasal-9 tidak ada" in alasan[3]

    def test_urutan_mundur_ditolak_sisipan_naik(self):
        par = [_p("Pasal 1", 0), _p("(2) dua", 1), _p("(2a) sisipan", 2), _p("(1) satu", 3)]
        b = buktikan({0: "pasal-1", 1: "pasal-1-ayat-2", 2: "pasal-1-ayat-2a", 3: "pasal-1-ayat-1"}, par)
        assert [p for p, _, _ in b.gagal] == [3]
        assert "urutan mundur" in b.gagal[0][2]

    def test_bagian_kesatu_kedua_tidak_diurutkan_menurut_abjad(self):
        par = [_p("BAB I", 0), _p("Bagian Kesatu", 1), _p("Bagian Kedua", 2)]
        b = buktikan({0: "bab-i", 1: "bab-i-bagian-kesatu", 2: "bab-i-bagian-kedua"}, par)
        assert not b.gagal

    def test_huruf_i_v_x_tidak_dibaca_romawi(self):
        """h, i, j berurut menurut abjad — i bukan 1, v bukan 5."""
        par = [_p("Pasal 1", 0)] + [_p(f"{h}. butir", n + 1) for n, h in enumerate("hijuvwx")]
        lab = {0: "pasal-1"} | {n + 1: f"pasal-1-huruf-{h}" for n, h in enumerate("hijuvwx")}
        assert not buktikan(lab, par).gagal

    def test_paragraf_berpenanda_tanpa_label_terhitung(self):
        par = [_p("Pasal 1", 0), _p("(1) satu", 1), _p("(2) dua", 2), _p("Ditetapkan di Jakarta", 3)]
        b = buktikan({0: "pasal-1", 1: "pasal-1-ayat-1", 3: "penutup"}, par)
        assert b.tanpa_label == [2]


class TestPetaLetak:
    def test_label_sama_dengan_parser_memakai_pohon_parser(self):
        par = naskah()
        peta = peta_letak(dict(_label_parser(par)), par)
        assert peta.sumber == "label AI = parser" and not peta.beda_parser

    def test_satu_label_gagal_pmk_biasa_mundur_ke_parser(self):
        par = naskah()
        lab = dict(_label_parser(par))
        p = next(k for k, v in lab.items() if v == "pasal-2")
        lab[p] = "pasal-7"
        peta = peta_letak(lab, par)
        assert peta.sumber == "parser cadangan"
        assert any("parser cadangan" in c for c in peta.catatan)

    def test_tanpa_label_ai_memakai_parser(self):
        assert peta_letak(None, naskah()).sumber == "parser cadangan"

    def test_pohon_dari_label_setara_parser(self):
        par = naskah()
        parser = bangun_pohon(par)
        pohon = pohon_dari_label(buktikan(_label_parser(par), par).lolos, par)
        assert [s.id for s in pohon.satuan] == [s.id for s in parser.satuan]
        for s in parser.satuan:
            t = pohon.cari(s.id)
            assert t.jenis == s.jenis and t.nomor == s.nomor and t.induk == s.induk, s.id
            assert t.paragraf_mulai == s.paragraf_mulai, s.id

    @pytest.mark.skipif(not TEMPAT_PMK.exists(), reason="naskah uji nyata tidak ada")
    def test_label_parser_pmk45_lolos_bukti(self):
        from tools.cek_docx import baca_naskah

        berkas = next((x for x in TEMPAT_PMK.iterdir() if "PMK 45 " in x.name), None)
        if berkas is None:
            pytest.skip("PMK 45 tidak ada")
        _, par, _ = baca_naskah(berkas)
        lab = _label_parser(par)
        b = buktikan(lab, par)
        assert len(lab) == 353 and len(b.lolos) == 353 and not b.gagal and not b.tanpa_label


class TestNaskahBerlabel:
    def test_seluruh_paragraf_berisi_ikut_dengan_nomor_dan_label(self):
        par = naskah()
        nb = susun_naskah_berlabel(par, bangun_pohon(par))
        for p in par:
            if p.tabel < 0 and p.teks.strip():
                assert f"¶{p.index} " in nb.teks, p.teks
        assert "[pasal-1-angka-1] 1. Pengelola Barang" in nb.teks
        # baris tanpa label tetap ada, mentah (CLAUDE.md butir 14)
        assert "Dalam Peraturan Menteri ini yang dimaksud dengan:" in nb.teks

    def test_baris_tabel_lampiran_membawa_rentang_paragraf(self):
        par = naskah()
        nb = susun_naskah_berlabel(par, bangun_pohon(par))
        assert any(b.startswith("¶") and "| Barang 0-1 |" in b for b in nb.teks.splitlines())
        assert nb.baris_tabel_paragraf


class TestNaskahBerformat:
    def test_butir_kosong_dan_teks_tersembunyi_tertulis(self):
        par = [
            ParagrafInput(index=0, teks="Menimbang : a. bahwa satu;", format=FormatParagraf(huruf="Bookman Old Style", ukuran=12)),
            ParagrafInput(index=1, teks="", penanda="b."),
            ParagrafInput(index=2, teks=""),
            ParagrafInput(
                index=3, teks="jJ jJ Mengingat : 1. UU;",
                format=FormatParagraf(huruf="Bookman Old Style", ukuran=12, tersembunyi=["jJ jJ"], rata="rata kiri-kanan"),
            ),
        ]
        nf = susun_naskah_berformat(par, bangun_pohon(par), None)
        assert BUTIR_KOSONG in nf.anotasi[1]
        assert 'tersembunyi: "jJ jJ"' in nf.anotasi[3]
        assert "1 baris kosong sebelumnya" in nf.anotasi[3]
        assert nf.terbaca

    def test_tanpa_bacaan_format_disebut_terang(self):
        par = naskah()
        nf = susun_naskah_berformat(par, bangun_pohon(par), None)
        assert not nf.terbaca and "tidak terbaca" in nf.teks
