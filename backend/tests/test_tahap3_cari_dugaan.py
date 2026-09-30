"""Tahap 3 — cari dugaan pada naskah utuh (bug 7). SELURUHNYA KlienPalsu.

Yang diuji bukan kecerdasan modelnya melainkan apa yang terjadi pada JAWABAN
model — termasuk yang mengarang id, yang melewatkan pasal, dan yang rusak.
Tes bertanda NEGATIF membuktikan jawaban yang salah tidak lolos.
"""

import json

from app.bersama import prompt as P
from app.bersama.llm import KlienPalsu, Ongkos
from app.models.temuan import JenisTanda, LokasiTemuan, RujukanTemuan, Temuan
from app.telaah import tahap3_cari_dugaan as T3
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import susun_bahan
from tests.naskah_uji import BATANG, naskah


def _js(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


def _siapkan(paragraf=None, fase1=None):
    paragraf = paragraf or naskah()
    pohon = bangun_pohon(paragraf)
    return paragraf, pohon, susun_bahan(paragraf, pohon, fase1)


def _temuan_fase1(nomor=3) -> Temuan:
    return Temuan(
        id=f"f1-{nomor}", nomor=nomor, aturan_id="F1-008", fase=1,
        jenis_tanda=JenisTanda.CATATAN,
        lokasi=LokasiTemuan(paragraf_index=7, offset_mulai=0, panjang=5, teks_asli="bahwa"),
        catatan="Bentuk butir Menimbang.",
        rujukan=RujukanTemuan(sumber="KMK 527", butir="21", kutipan="…", pdf_url="x"),
    )


def _jawab_pasal(fokus, dugaan=None):
    """Jawaban per kelompok pasal: tiap pasal fokus dijawab, dugaan di pasal pertama."""
    hasil = [{"pasal": p, "dugaan": []} for p in fokus]
    if dugaan:
        hasil[0]["dugaan"] = dugaan
    return _js({"hasil": hasil})


class TestRencana:
    def test_pasal_dikelompokkan_tanpa_dibelah(self):
        _, pohon, _ = _siapkan()
        kelompok = T3.kelompok_fokus(pohon, per_fokus=3)
        assert kelompok == [["pasal-1", "pasal-2", "pasal-3"], ["pasal-4"]]

    def test_satu_pasal_panjang_tetap_satu_kelompok(self):
        _, pohon, _ = _siapkan()
        assert T3.kelompok_fokus(pohon, per_fokus=6, batas_token=1) == [
            ["pasal-1"], ["pasal-2"], ["pasal-3"], ["pasal-4"]
        ]

    def test_tiga_macam_panggilan(self):
        _, pohon, bahan = _siapkan()
        rencana = T3.rencana(pohon, bahan)
        assert [pg.macam for pg in rencana] == ["pasal", "lintas", "lampiran"]

    def test_jenis_yang_dimatikan_penelaah_tidak_ditanyakan(self):
        _, pohon, bahan = _siapkan()
        rencana = T3.rencana(pohon, bahan, aturan_aktif={"F2-102"})
        assert [pg.macam for pg in rencana] == ["pasal"]
        assert rencana[0].jenis == ["pemikul"]
        assert "makna_ganda" not in rencana[0].pesan.split("---")[-1]

    def test_semua_AI_mati_tidak_ada_panggilan(self):
        _, pohon, bahan = _siapkan()
        assert T3.rencana(pohon, bahan, aturan_aktif={"F2-001", "F2-004"}) == []

    def test_keberatan_tetap_ditanya_walau_jenis_lintas_mati(self):
        """Fitur keberatan atas temuan Fase 1 tidak boleh hilang diam-diam."""
        _, pohon, bahan = _siapkan(fase1=[_temuan_fase1()])
        rencana = T3.rencana(pohon, bahan, aturan_aktif={"F2-102"}, ada_fase1=True)
        lintas = [pg for pg in rencana if pg.macam == "lintas"]
        assert len(lintas) == 1 and lintas[0].jenis == []
        assert P.TAHAP3_KEBERATAN_ADA in lintas[0].pesan

    def test_panggilan_lampiran_dilewati_kalau_tidak_ada_urusan_lampiran(self):
        batang = [b for b in BATANG if "Lampiran" not in b]
        _, pohon, bahan = _siapkan(naskah(batang=batang, lampiran=False))
        assert "lampiran" not in [pg.macam for pg in T3.rencana(pohon, bahan)]

    def test_NASKAH_UTUH_di_depan_SAMA_PERSIS_di_tiap_panggilan(self):
        """Awalan yang sama — syarat potongan harga awalan prompt, dan jaminan
        bahwa tiap panggilan menilai di atas naskah yang sama."""
        _, pohon, bahan = _siapkan()
        rencana = T3.rencana(pohon, bahan, per_fokus=1)
        assert len(rencana) >= 4
        awalan = {pg.pesan.split("\n\n---\n\nTUGAS")[0] for pg in rencana}
        assert len(awalan) == 1
        assert bahan.teks in awalan.pop()

    def test_panggilan_lampiran_membawa_fakta_lampiran(self):
        _, pohon, bahan = _siapkan()
        lampiran = [pg for pg in T3.rencana(pohon, bahan) if pg.macam == "lampiran"][0]
        assert bahan.fakta_lampiran in lampiran.pesan
        assert "(butir 120)" in lampiran.pesan


class TestJawaban:
    def _jalan(self, jawaban, aturan=None, fase1=None, **kw):
        paragraf, pohon, bahan = _siapkan(fase1=fase1)
        rencana = T3.rencana(pohon, bahan, aturan, ada_fase1=bool(fase1), per_fokus=6)
        klien = KlienPalsu(jawaban)
        hasil = T3.cari_dugaan(rencana, pohon, bahan, klien, Ongkos(), temuan_fase1=fase1, **kw)
        return hasil, klien

    FOKUS = ["pasal-1", "pasal-2", "pasal-3", "pasal-4"]

    def test_dugaan_sah_diteruskan(self):
        dugaan = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "pemikul tidak tegas"}]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, dugaan)], {"F2-102"})
        assert [(d.satuan_id, d.jenis) for d in hasil.dugaan] == [("pasal-2", "pemikul")]
        assert hasil.tidak_dijawab == []

    def test_NEGATIF_id_karangan_dibuang(self):
        dugaan = [{"satuan_id": "pasal-99", "jenis": "pemikul", "alasan": "x"}]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, dugaan)], {"F2-102"})
        assert hasil.dugaan == []

    def test_NEGATIF_satuan_di_luar_pasal_fokus_dibuang(self):
        _, pohon, bahan = _siapkan()
        pg = T3.panggilan_pasal(bahan, ["pasal-2"], ["pemikul"], "uji")
        jawab = _js({"hasil": [{"pasal": "pasal-2", "dugaan": [
            {"satuan_id": "pasal-4", "jenis": "pemikul", "alasan": "x"}]}]})
        hasil = T3.cari_dugaan([pg], pohon, bahan, KlienPalsu([jawab]), Ongkos())
        assert hasil.dugaan == []

    def test_NEGATIF_jenis_yang_tidak_ditanyakan_dibuang(self):
        dugaan = [{"satuan_id": "pasal-2", "jenis": "tabrakan", "alasan": "x"}]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, dugaan)], {"F2-102"})
        assert hasil.dugaan == []

    def test_NEGATIF_alasan_kosong_dibuang(self):
        dugaan = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "  "}]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, dugaan)], {"F2-102"})
        assert hasil.dugaan == []

    def test_NEGATIF_tabrakan_dengan_satuan_yang_tidak_ada_digugurkan(self):
        jawab = _js({"dugaan": [{"satuan_id": "pasal-2", "satuan_lain": "pasal-77",
                                 "jenis": "tabrakan", "alasan": "x"}]})
        hasil, _ = self._jalan([jawab], {"F2-104"})
        assert hasil.dugaan == []

    def test_tabrakan_sah(self):
        jawab = _js({"dugaan": [{"satuan_id": "pasal-4", "satuan_lain": "pasal-2",
                                 "jenis": "tabrakan", "alasan": "dua batas waktu"}]})
        hasil, _ = self._jalan([jawab], {"F2-104"})
        assert [(d.satuan_id, d.satuan_lain) for d in hasil.dugaan] == [("pasal-4", "pasal-2")]

    def test_dugaan_lampiran_menunjuk_satuan_lampiran(self):
        jawab = _js({"dugaan": [{"satuan_id": "lampiran", "alasan": "parameter 5 — tanpa nama pejabat"}]})
        hasil, _ = self._jalan([jawab], {"F2-106"})
        assert [(d.satuan_id, d.jenis) for d in hasil.dugaan] == [("lampiran", "lampiran")]

    def test_pasal_yang_terlewat_DITANYAKAN_ULANG(self):
        sebagian = _js({"hasil": [{"pasal": "pasal-1", "dugaan": []}, {"pasal": "pasal-2", "dugaan": []}]})
        ulang = _jawab_pasal(["pasal-3", "pasal-4"])
        hasil, klien = self._jalan([sebagian, ulang], {"F2-102"})
        assert len(klien.diminta) == 2
        assert "Pasal fokus: pasal-3, pasal-4" in klien.diminta[1][1]
        assert hasil.tidak_dijawab == []
        assert hasil.rekaman[-1][0].endswith("· TANYA ULANG")

    def test_yang_TETAP_tidak_dijawab_dicatat_bukan_dianggap_bersih(self):
        kosong = _js({"hasil": []})
        hasil, _ = self._jalan([kosong, kosong], {"F2-102"})
        assert hasil.tidak_dijawab == self.FOKUS
        assert any("TIDAK diperiksa" in c for c in hasil.catatan)

    def test_jawaban_rusak_dicatat_dan_pasalnya_ditanya_ulang(self):
        hasil, klien = self._jalan(["bukan json", _jawab_pasal(self.FOKUS)], {"F2-102"})
        assert len(klien.diminta) == 2
        assert hasil.tidak_dijawab == []
        assert any("tidak terbaca" in c for c in hasil.catatan)

    def test_dugaan_kembar_cukup_sekali(self):
        kembar = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": f"alasan {i}"}
                  for i in range(5)]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, kembar)], {"F2-102"})
        assert len(hasil.dugaan) == 1

    def test_batas_kewajaran_memotong_dan_mencatatnya(self, monkeypatch):
        monkeypatch.setattr(T3, "BATAS_DUGAAN", 1)
        dua = [
            {"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "a"},
            {"satuan_id": "pasal-2", "jenis": "makna_ganda", "alasan": "b"},
        ]
        hasil, _ = self._jalan([_jawab_pasal(self.FOKUS, dua)], {"F2-101", "F2-102"})
        assert len(hasil.dugaan) == 1
        assert any("batas 1 dugaan" in c for c in hasil.catatan)

    def test_keberatan_menempel_TIDAK_menghapus(self):
        t = _temuan_fase1()
        semula = (t.id, t.nomor, t.catatan, t.lokasi.teks_asli)
        jawab = _js({"dugaan": [], "keberatan": [{"nomor": 3, "alasan": "Butir itu sudah baku."}]})
        self._jalan([jawab], {"F2-104"}, fase1=[t])
        assert t.catatan_ai == "Butir itu sudah baku."
        assert (t.id, t.nomor, t.catatan, t.lokasi.teks_asli) == semula

    def test_keberatan_bernomor_karangan_diabaikan(self):
        t = _temuan_fase1()
        jawab = _js({"dugaan": [], "keberatan": [{"nomor": 99, "alasan": "x"}]})
        self._jalan([jawab], {"F2-104"}, fase1=[t])
        assert t.catatan_ai == ""


class TestLanjutkan:
    def test_jawaban_tersimpan_tidak_dibayar_ulang(self):
        _, pohon, bahan = _siapkan()
        pg = T3.panggilan_pasal(bahan, ["pasal-2"], ["pemikul"], "uji")
        tersimpan = {pg.kunci: _jawab_pasal(["pasal-2"])}
        klien = KlienPalsu([])
        ongkos = Ongkos()
        hasil = T3.cari_dugaan([pg], pohon, bahan, klien, ongkos, tersimpan=tersimpan)
        assert klien.diminta == [] and ongkos.panggilan == 0
        assert hasil.tidak_dijawab == []

    def test_hanya_jawaban_terbaca_yang_disimpan(self):
        _, pohon, bahan = _siapkan()
        pg = T3.panggilan_pasal(bahan, ["pasal-2"], ["pemikul"], "uji")
        disimpan = {}
        T3.cari_dugaan(
            [pg], pohon, bahan, KlienPalsu(["rusak", "rusak juga"]), Ongkos(),
            simpan=lambda k, v: disimpan.__setitem__(k, v),
        )
        assert disimpan == {}

    def test_kunci_berubah_kalau_naskahnya_berubah(self):
        _, pohon, bahan = _siapkan()
        batang = BATANG[:5] + ["Pengguna Barang wajib mengajukan permohonan paling lambat 14 hari."] + BATANG[6:]
        _, pohon2, bahan2 = _siapkan(naskah(batang=batang))
        a = T3.panggilan_pasal(bahan, ["pasal-2"], ["pemikul"], "uji")
        b = T3.panggilan_pasal(bahan2, ["pasal-2"], ["pemikul"], "uji")
        assert a.kunci != b.kunci


class _KlienMenjawabFokus:
    """Menjawab tiap pasal fokus yang tertulis di pesannya — urutan panggilan
    antar-utas tidak pasti, jadi jawabannya tidak boleh bergantung urutan."""

    def tanya(self, peran, pesan):
        from app.bersama.llm import Jawaban

        fokus = pesan.split("Pasal fokus: ")[1].split("\n")[0].split(", ")
        return Jawaban(_jawab_pasal(fokus))


def test_berbarengan_hasilnya_tetap_urut():
    """Panggilan boleh berjalan berbarengan; rekamannya tetap urut rencana."""
    _, pohon, bahan = _siapkan()
    rencana = T3.rencana(pohon, bahan, {"F2-102"}, per_fokus=1)
    klien = _KlienMenjawabFokus()
    hasil = T3.cari_dugaan(rencana, pohon, bahan, klien, Ongkos(), berbarengan=4)
    assert [j for j, _ in hasil.rekaman] == [pg.judul for pg in rencana]
    assert hasil.tidak_dijawab == []
