"""Bahan untuk model — tahap 2, bug 7. TANPA jaringan.

Tes yang paling menentukan: `test_TIDAK_ADA_PARAGRAF_YANG_KELUAR_DARI_BAHAN`.
Tiga salah tandai di uji 27 Sep 2026 lahir dari teks yang tidak ikut terbawa,
dan pada PMK 119 seluruh definisi Pasal 1 tidak pernah sampai ke model. Kalau
suatu hari penyusun bahan membuang satu paragraf pun, tes itu yang berbunyi.
"""

import re

from app.models.temuan import (
    JenisTanda,
    KerangkaTabel,
    LokasiTemuan,
    ParagrafInput,
    RujukanTemuan,
    Temuan,
)
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan import bahan as B
from tests.naskah_uji import BATANG, data_barang, naskah, nomori, tabel, teks


def _bahan(paragraf, **kw):
    return B.susun_bahan(paragraf, bangun_pohon(paragraf), **kw)


def _rapi(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def test_TIDAK_ADA_PARAGRAF_YANG_KELUAR_DARI_BAHAN():
    # Paragraf yang TIDAK dikenali parser ikut: rincian "a)" tidak punya satuan.
    batang = BATANG[:6] + ["a) rincian yang tidak dikenali parser;"] + BATANG[6:]
    paragraf = naskah(batang=batang)
    bahan = _bahan(paragraf)
    for p in paragraf:
        if p.utuh.strip():
            assert _rapi(p.utuh) in bahan.teks, p.utuh


def test_satuan_ditandai_id_nya():
    bahan = _bahan(naskah())
    assert "[pasal-2] Pasal 2" in bahan.teks
    assert "[pasal-1-angka-1] 1. Pengelola Barang adalah" in bahan.teks
    assert "[menimbang-a] a. bahwa untuk tertib" in bahan.teks


def test_label_terpisah_sel_disatukan_seperti_parser_membacanya():
    """PMK 119: "1." di satu sel, teksnya di sel sebelahnya (bug 11)."""
    batang = teks(["Pasal 1", "Dalam Peraturan Menteri ini yang dimaksud dengan:"]) + tabel(
        [["1.", "Pengelola Barang adalah pejabat yang berwenang."]], nomor=0
    ) + teks(["Pasal 2", "Pengelola Barang wajib melapor."])
    paragraf = nomori(naskah(lampiran=False, batang=[])[:12] + batang)
    bahan = _bahan(paragraf)
    assert "[pasal-1-angka-1] 1. Pengelola Barang adalah pejabat yang berwenang." in bahan.teks


def test_tabel_lampiran_ditulis_per_baris_sel():
    bahan = _bahan(naskah())
    assert "[TABEL 0 · 7 baris × 3 kolom]" in bahan.teks
    assert "| NO. | NAMA BARANG | JUMLAH |" in bahan.teks
    assert "| 3. | Barang 0-3 | 3.000 |" in bahan.teks


def test_di_bawah_anggaran_semua_utuh():
    bahan = _bahan(naskah())
    assert bahan.kerangka == []
    assert "KERANGKA" not in bahan.teks


def test_melewati_anggaran_TABEL_DATA_SEJENIS_jadi_kerangka_bersama():
    paragraf = naskah(tabel_lampiran=[data_barang(0, 30), data_barang(1, 30)])
    bahan = _bahan(paragraf, anggaran=10)
    assert len(bahan.kerangka) == 1, "dua tabel sejenis wajib satu kelompok"
    assert "[TABEL 0 · KERANGKA" in bahan.teks and "[TABEL 1 · KERANGKA" in bahan.teks
    assert "| 30. | Barang 0-30 | 30.000 |" not in bahan.teks
    # Judul kolom dan baris contoh tetap ikut.
    assert "| NO. | NAMA BARANG | JUMLAH |" in bahan.teks
    assert "| 1. | Barang 0-1 | 1.000 |" in bahan.teks


def test_melewati_anggaran_TEKS_DAN_BATANG_TUBUH_tidak_pernah_dipangkas():
    paragraf = naskah(tabel_lampiran=[data_barang(0, 30)])
    bahan = _bahan(paragraf, anggaran=10)
    for p in paragraf:
        if p.tabel < 0 and p.utuh.strip():
            assert _rapi(p.utuh) in bahan.teks, p.utuh


def test_tabel_raksasa_dari_panel_disebut_tidak_bisa_dibuka():
    paragraf = naskah(tabel_lampiran=[])
    sesudah = next(p.index for p in paragraf if p.teks == "DAFTAR BARANG")
    k = KerangkaTabel(
        tabel=9, sesudah_paragraf=sesudah, jumlah_baris=52000, jumlah_kolom=2,
        contoh=[["Desa", "Jumlah"], ["Desa A", "10"]],
    )
    bahan = _bahan(paragraf, tabel_raksasa=[k])
    assert "[TABEL 9 · KERANGKA DARI PANEL — 52.000 baris × 2 kolom." in bahan.teks
    assert "tidak bisa dibuka" in bahan.teks
    assert "| Desa A | 10 |" in bahan.teks


def test_gambar_disebut_tidak_terbaca():
    paragraf = naskah()
    i = next(p.index for p in paragraf if p.teks == "DAFTAR BARANG")
    paragraf.insert(i + 1, ParagrafInput(index=0, teks="", gambar=1))
    bahan = _bahan(nomori(paragraf))
    assert "[GAMBAR — isinya tidak bisa dibaca]" in bahan.teks


def test_temuan_fase1_ikut_dengan_letak_satuannya():
    paragraf = naskah()
    i = next(p.index for p in paragraf if p.teks.startswith("Pengguna Barang wajib"))
    t = Temuan(
        id="f1-3", nomor=3, aturan_id="F1-008", fase=1, jenis_tanda=JenisTanda.CATATAN,
        lokasi=LokasiTemuan(paragraf_index=i, offset_mulai=0, panjang=15, teks_asli="Pengguna Barang"),
        catatan="Ejaan tidak baku.",
        rujukan=RujukanTemuan(sumber="KMK 527", butir="33", kutipan="…", pdf_url="x"),
    )
    bahan = _bahan(paragraf, temuan_fase1=[t])
    assert "== TEMUAN PEMERIKSAAN FORMAT YANG SUDAH ADA" in bahan.teks
    assert "(T3) [pasal-2] pada teks 'Pengguna Barang': Ejaan tidak baku." in bahan.teks


def test_bahan_SAMA_PERSIS_untuk_naskah_yang_sama():
    """Awalan yang sama di tiap panggilan — syarat potongan harga awalan prompt."""
    assert _bahan(naskah()).teks == _bahan(naskah()).teks


def test_token_dihitung_per_bagian():
    bahan = _bahan(naskah())
    assert bahan.token["naskah"] > 0 and bahan.token["lampiran"] > 0
    assert bahan.total_token >= bahan.token["naskah"] + bahan.token["lampiran"] - 5
    assert bahan.cara_hitung


class TestFaktaLampiran:
    def test_memuat_judul_nomor_dan_bingkai_tiap_lampiran(self):
        fakta = _bahan(naskah()).fakta_lampiran
        assert "Judul PMK di halaman pertama: TATA CARA PENETAPAN STATUS PENGGUNAAN" in fakta
        assert "Nomor PMK di halaman pertama: NOMOR 12 TAHUN 2026" in fakta
        assert "- Lampiran I (paragraf" in fakta and "- Lampiran II (paragraf" in fakta
        assert "/ MENTERI KEUANGAN REPUBLIK INDONESIA, / ttd. / NAMA MENTERI" in fakta

    def test_memuat_pasal_yang_menyebut_lampiran(self):
        fakta = _bahan(naskah()).fakta_lampiran
        assert "- [pasal-3] Daftar barang tercantum dalam Lampiran I" in fakta

    def test_salah_ketik_lampiran_dikumpulkan(self):
        batang = BATANG[:7] + ["Daftar barang tercantum dalam Lampirn I."] + BATANG[8:]
        bahan = _bahan(naskah(batang=batang))
        assert '- "Lampirn" di [pasal-3]' in bahan.fakta_lampiran
        assert bahan.lampiran_mirip == 1

    def test_kata_sah_berakar_lampir_BUKAN_salah_ketik(self):
        batang = BATANG[:5] + ["Pengguna Barang melampirkan dokumen dan lampirannya."] + BATANG[6:]
        bahan = _bahan(naskah(batang=batang))
        assert bahan.lampiran_mirip == 0

    def test_satu_huruf_meleset_atau_tertukar_terjaring(self):
        for salah in ("Lampirn", "Lampiraan", "Lanpiran", "Lamipran"):
            assert B._mirip_lampiran(salah), salah

    def test_NEGATIF_kata_lain_yang_terpaut_dua_huruf_tidak_terjaring(self):
        """PMK 104: "laporan" dulu terjaring dan menyeret panggilan lampiran percuma."""
        for sah in ("laporan", "lamaran", "Lampiran", "lampirkan"):
            assert not B._mirip_lampiran(sah), sah

    def test_tanpa_lampiran_dan_tanpa_sebutan_tidak_ada_urusan_lampiran(self):
        batang = [b for b in BATANG if "Lampiran" not in b]
        bahan = _bahan(naskah(batang=batang, lampiran=False))
        assert not bahan.ada_urusan_lampiran
