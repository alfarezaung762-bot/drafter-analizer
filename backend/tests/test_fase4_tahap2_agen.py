"""Fase 4 — Tahap 2 agen, SELURUHNYA klien palsu (rancangan Fase 4 bagian 5.6).

Klien palsu memerankan agen: memanggil alat, mencatat temuan, kutipan terlalu
panjang, status tidak lengkap, putaran macet, 429; penilai palsu menolak satu
calon → calon itu gugur sebelum gerbang.
"""

import threading

from app.bersama.llm import KlienAgenPalsu, Ongkos
from app.telaah.alur import jalankan_agen
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import susun_naskah_berlabel
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import bangun_pohon, id_awal_satuan, peta_satuan
from app.telaah.tahap2_agen.langkah1_pilih_analisis import muat_katalog
from app.telaah.tahap2_agen.langkah2_bagi_putaran import Putaran, bagi_putaran, kelompok_fokus
from app.telaah.tahap2_agen.langkah3_alat_agen import BahanAlat
from app.telaah.tahap2_agen.langkah3_jalankan_agen import Setelan, jalankan_putaran
from app.telaah.tahap2_agen.langkah4_penilai_kedua import nilai_calon
from tests.naskah_uji import naskah

KATALOG = muat_katalog()


def _bahan(paragraf=None):
    par = paragraf or naskah()
    pohon = bangun_pohon(par)
    return BahanAlat(
        paragraf=par,
        pohon=pohon,
        peta=peta_satuan(pohon),
        id_awal=id_awal_satuan(pohon),
        berlabel=susun_naskah_berlabel(par, pohon),
        anotasi_format={},
        katalog=KATALOG,
    )


def _putaran(kode=("F2-101",), fokus=("pasal-2",)):
    return Putaran(
        kode=fokus[0] if fokus else "naskah",
        judul="Putaran 1/1 · uji",
        lingkup="per pasal" if fokus else "seluruh naskah",
        analisis=[KATALOG.cari(k) for k in kode],
        fokus=list(fokus),
    )


def _selesai(fokus=("pasal-2",), kode=("F2-101",)):
    return ("selesai", {"laporan": [{"pasal": p, "analisis": k, "status": "diperiksa"} for p in (fokus or ["naskah"]) for k in kode]})


def _catat(**ganti):
    isi = {
        "analisis": "F2-101", "letak": "pasal-2", "kutipan": "paling lambat 30 (tiga puluh) hari",
        "bentuk": "catatan", "temuan": "uji", "bacaan": ["satu", "dua"], "skor": 0.9,
    }
    isi.update(ganti)
    return ("catat_temuan", isi)


def _jalan(klien, putaran=None, **kw):
    return jalankan_putaran(putaran or _putaran(), _bahan(), "tugas", klien, Ongkos(), **kw)


class TestBagiPutaran:
    def test_pasal_dikelompokkan_tanpa_dibelah(self):
        assert kelompok_fokus(bangun_pohon(naskah()), per_fokus=3) == [["pasal-1", "pasal-2", "pasal-3"], ["pasal-4"]]

    def test_satu_pasal_panjang_tetap_satu_kelompok(self):
        assert kelompok_fokus(bangun_pohon(naskah()), per_fokus=6, batas_token=1) == [
            ["pasal-1"], ["pasal-2"], ["pasal-3"], ["pasal-4"]
        ]

    def test_putaran_menurut_lingkup(self):
        analisis = [KATALOG.cari(k) for k in ("F2-101", "F1-003", "F2-106", "F-20")]
        b = bagi_putaran(analisis, bangun_pohon(naskah()), True, per_fokus=2)
        assert [p.lingkup for p in b.putaran] == ["per pasal", "per pasal", "seluruh naskah", "lampiran", "format"]
        assert b.putaran[0].judul == "Putaran 1/5 · Pasal 1–2"

    def test_lampiran_tanpa_urusan_lampiran_tidak_dijalankan(self):
        b = bagi_putaran([KATALOG.cari("F2-106")], bangun_pohon(naskah(lampiran=False)), False)
        assert not b.putaran and b.tidak_dijalankan[0][0] == "F2-106"


class TestPutaranAgen:
    def test_alat_dijalankan_dan_hasilnya_dikirim_balik(self):
        klien = KlienAgenPalsu([[("cari_teks", {"teks": "Lampiran I"})], [_selesai()]])
        h = _jalan(klien)
        assert h.berakhir == "selesai"
        kedua = klien.diminta[1]
        assert kedua[-1]["role"] == "tool" and "KETEMU" in kedua[-1]["content"]
        assert h.langkah[0].alat[0][0] == "cari_teks"

    def test_kutipan_terlalu_panjang_ditolak_saat_itu_juga(self):
        klien = KlienAgenPalsu([[_catat(kutipan="x" * 250)], [_catat()], [_selesai()]])
        h = _jalan(klien)
        assert len(h.catatan.calon) == 1
        assert "lebih dari 200" in h.catatan.ditolak_catat[0]
        assert "DITOLAK" in h.langkah[0].alat[0][2]

    def test_kutipan_ganda_di_letaknya_ditolak(self):
        """PMK 45, 2 Okt 2026: kutipan yang muncul dua kali menandai kemunculan yang salah."""
        klien = KlienAgenPalsu([[_catat(letak="pasal-1", kutipan="Barang")], [_selesai()]])
        h = _jalan(klien)
        assert not h.catatan.calon
        assert "muncul 2 kali" in h.catatan.ditolak_catat[0]

    def test_kutipan_yang_tidak_ada_di_letak_ditolak_dengan_isi_letaknya(self):
        klien = KlienAgenPalsu([[_catat(kutipan="kalimat karangan")], [_selesai()]])
        h = _jalan(klien)
        assert not h.catatan.calon and "tidak ketemu persis" in h.catatan.ditolak_catat[0]

    def test_status_tidak_lengkap_ditagih_sekali_lalu_tidak_diperiksa(self):
        fokus = ("pasal-2", "pasal-3")
        klien = KlienAgenPalsu([
            [("selesai", {"laporan": [{"pasal": "pasal-2", "analisis": "F2-101", "status": "diperiksa"}]})],
            [("selesai", {"laporan": []})],
        ])
        h = _jalan(klien, _putaran(fokus=fokus))
        assert h.berakhir == "ditagih"
        assert h.tidak_diperiksa == [("pasal-3", "F2-101")]
        assert "Belum dilaporkan" in klien.diminta[1][-1]["content"]

    def test_tagihan_dipenuhi_berakhir_selesai(self):
        fokus = ("pasal-2", "pasal-3")
        klien = KlienAgenPalsu([
            [("selesai", {"laporan": [{"pasal": "pasal-2", "analisis": "F2-101", "status": "diperiksa"}]})],
            [("selesai", {"laporan": [{"pasal": "pasal-3", "analisis": "F2-101", "status": "tidak relevan"}]})],
        ])
        assert _jalan(klien, _putaran(fokus=fokus)).berakhir == "selesai"

    def test_alat_sama_berulang_berarti_macet(self):
        klien = KlienAgenPalsu([[("cari_teks", {"teks": "x"})]] * 5)
        h = _jalan(klien, setelan=Setelan(macet_ulang=3))
        assert h.berakhir.startswith("macet") and len(h.langkah) == 3

    def test_terlalu_lama_tanpa_kemajuan_berarti_macet(self):
        klien = KlienAgenPalsu([[("cari_teks", {"teks": f"x{i}"})] for i in range(10)])
        h = _jalan(klien, setelan=Setelan(macet_ulang=99, macet_langkah=4))
        assert h.berakhir.startswith("macet") and len(h.langkah) == 4

    def test_jawaban_tanpa_alat_didorong(self):
        klien = KlienAgenPalsu(["saya rasa tidak ada masalah", [_selesai()]])
        h = _jalan(klien)
        assert h.berakhir == "selesai" and "didorong" in h.langkah[0].catatan[0]

    def test_429_ditunggu_bukan_gagal(self):
        klien = KlienAgenPalsu(["429", [_selesai()]])
        h = _jalan(klien, setelan=Setelan(tunggu_429=0.01))
        assert h.berakhir == "selesai"
        assert any("429" in c for c in h.langkah[0].catatan)

    def test_batal_berhenti_mengirim_request_baru(self):
        batal = threading.Event()
        batal.set()
        klien = KlienAgenPalsu([[_selesai()]])
        h = _jalan(klien, batal=batal)
        assert h.berakhir == "dibatalkan" and not klien.diminta

    def test_dilanjutkan_dari_simpanan_tanpa_bayar_ulang(self):
        simpanan: dict[str, str] = {}
        langkah = [[_catat()], [_selesai()]]
        h1 = _jalan(KlienAgenPalsu(list(langkah)), simpan=simpanan.__setitem__)
        klien2 = KlienAgenPalsu([])
        h2 = _jalan(klien2, tersimpan=simpanan)
        assert h2.berakhir == "selesai" and len(h2.catatan.calon) == len(h1.catatan.calon) == 1
        assert not klien2.diminta
        assert all(x.dari_simpanan for x in h2.langkah)


class TestPenilaiKedua:
    def _calon(self):
        klien = KlienAgenPalsu([[_catat(), _catat(kutipan="Pengguna Barang wajib mengajukan permohonan")], [_selesai()]])
        return _jalan(klien).catatan.calon

    def test_ditolak_dan_tidak_dijawab_bukan_setuju(self):
        calon = self._calon()
        klien = KlienAgenPalsu([], penilai=['{"putusan": [{"calon": "C1", "putusan": "tolak", "alasan": "lemah"}]}'])
        n = nilai_calon(calon, _putaran(), "naskah", klien, Ongkos())
        assert n.putusan["C1"][0] == "tolak" and n.putusan["C2"][0] == "tidak dijawab"
        assert calon[0].penilai == "tolak"

    def test_request_baru_tanpa_penalaran_agen(self):
        calon = self._calon()
        klien = KlienAgenPalsu([], penilai=['{"putusan": []}'])
        nilai_calon(calon, _putaran(), "NASKAH-UTUH", klien, Ongkos())
        peran, pesan = klien.diminta_penilai[0]
        assert "skeptis" in peran and pesan.startswith("NASKAH-UTUH")
        assert "C1 · F2-101" in pesan

    def test_jawaban_rusak_ditanya_ulang_sekali(self):
        calon = self._calon()
        klien = KlienAgenPalsu([], penilai=["bukan json", '{"putusan": [{"calon": "C1", "putusan": "setuju"}]}'])
        n = nilai_calon(calon, _putaran(), "naskah", klien, Ongkos())
        assert n.terbaca and n.putusan["C1"][0] == "setuju" and len(klien.diminta_penilai) == 2


class _KlienAlur(KlienAgenPalsu):
    """Untuk alur utuh: label dari parser, satu putaran, penilai menolak C2."""

    def __init__(self, langkah, label_json, penilai):
        super().__init__(langkah, penilai)
        self._label = label_json

    def tanya(self, peran, pesan):
        if "SUSUNAN" in peran:
            from app.bersama.llm import Jawaban

            return Jawaban(self._label, 100, 10)
        return super().tanya(peran, pesan)


class TestAlurAgen:
    def test_penilai_menolak_satu_calon_gugur_sebelum_gerbang(self):
        import json

        par = naskah()
        label = json.dumps({"jenis": "pmk biasa", "label": [{"p": p, "label": l} for p, l in id_awal_satuan(bangun_pohon(par)).items()]})
        langkah = [
            [
                ("catat_temuan", {"analisis": "F2-101", "letak": "pasal-2", "kutipan": "paling lambat 30 (tiga puluh) hari",
                                  "bentuk": "catatan", "temuan": "dua arah", "bacaan": ["a", "b"], "skor": 0.9}),
                ("catat_temuan", {"analisis": "F2-101", "letak": "pasal-2", "kutipan": "Pengguna Barang wajib mengajukan permohonan",
                                  "bentuk": "catatan", "temuan": "lemah", "bacaan": ["a", "b"], "skor": 0.9}),
            ],
            [("selesai", {"laporan": [{"pasal": p, "analisis": "F2-101", "status": "diperiksa"} for p in ("pasal-1", "pasal-2", "pasal-3", "pasal-4")]})],
        ]
        penilai = ['{"putusan": [{"calon": "C1", "putusan": "setuju", "alasan": "nyata"}, {"calon": "C2", "putusan": "tolak", "alasan": "lemah"}]}']
        hasil = jalankan_agen(par, "PMK", _KlienAlur(langkah, label, penilai), kode_dipilih=["F2-101"], berbarengan=1, kunci_jawaban=False)
        assert [t.lokasi.teks_asli for t in hasil.temuan] == ["paling lambat 30 (tiga puluh) hari"]
        assert any("DITOLAK PENILAI — lemah" in g for g in hasil.gugur)
        assert hasil.peta.sumber == "label AI = parser"

    def test_naskah_perubahan_tidak_dijalankan(self):
        klien = _KlienAlur([], '{"jenis": "pmk perubahan", "label": []}', [])
        hasil = jalankan_agen(naskah(), "PMK", klien, berbarengan=1)
        assert "PERUBAHAN" in hasil.tidak_dijalankan and not klien.diminta

    def test_tanpa_ai_tidak_ada_yang_dijalankan(self):
        assert "AI tidak terhubung" in jalankan_agen(naskah(), "PMK", None).tidak_dijalankan

    def test_kmk_belum_tersedia(self):
        hasil = jalankan_agen(naskah(), "KMK", KlienAgenPalsu([]))
        assert hasil.tidak_dijalankan and any("belum tersedia untuk KMK" in p for p in hasil.peringatan)
