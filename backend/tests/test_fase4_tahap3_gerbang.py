"""Fase 4 — Tahap 3 gerbang: satu-satunya tempat calon jadi Temuan (rancangan 5.6).

Yang diuji di sini hal yang bisa dibuktikan kode, bukan pendapat agen: letak
dan kutipan, bukti format, batas atas Respons, sumber usulan, alasan dibuang,
sisipan satuan baru, Periksa ulang, dan rujukan yang tidak boleh dikarang.
"""

from app.models.pekerjaan import CalonAgen
from app.models.temuan import FormatParagraf, JenisTanda
from app.telaah.tahap1_bahan.langkah3_istilah_pasal1 import ambil_definisi
from app.telaah.tahap1_bahan.langkah6_naskah_berlabel import susun_naskah_berlabel
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import bangun_pohon, id_awal_satuan, peta_satuan
from app.telaah.tahap2_agen.langkah1_pilih_analisis import muat_katalog
from app.telaah.tahap2_agen.langkah3_alat_agen import BahanAlat, CatatanPutaran
from app.telaah.tahap3_verifikasi import BahanGerbang, verifikasi, verifikasi_satu
from tests.naskah_uji import BATANG, naskah

KATALOG = muat_katalog()
JUDUL = "Putaran 1/1 · uji"


def _g(par=None, anotasi=None, catatan=None, lama=None) -> BahanGerbang:
    par = par or naskah()
    pohon = bangun_pohon(par)
    bahan = BahanAlat(
        paragraf=par,
        pohon=pohon,
        peta=peta_satuan(pohon),
        id_awal=id_awal_satuan(pohon),
        berlabel=susun_naskah_berlabel(par, pohon),
        anotasi_format=anotasi or {},
        katalog=KATALOG,
    )
    return BahanGerbang(
        bahan=bahan,
        definisi=ambil_definisi(pohon),
        katalog=KATALOG,
        catatan={JUDUL: catatan} if catatan is not None else {},
        temuan_lama=lama or [],
    )


def _c(**ganti) -> CalonAgen:
    isi = dict(
        nomor="C1", putaran=JUDUL, analisis="F2-007", letak="pasal-2", kutipan="30 (tiga puluh)",
        bentuk="catatan", temuan="Bilangan perlu diperiksa.", skor=0.9,
    )
    isi.update(ganti)
    return CalonAgen(**isi)


def _indeks(par, teks: str) -> int:
    return next(p.index for p in par if p.teks == teks)


def _naskah(batang: list[str], lampiran: bool = True):
    return naskah(batang=batang, lampiran=lampiran)


class TestLetakDanKutipan:
    def test_kutipan_persis_lolos_dengan_rujukan_dasar(self):
        h = verifikasi_satu(_c(), _g())
        t = h.temuan
        assert t is not None, h.alasan
        assert t.lokasi.teks_asli == "30 (tiga puluh)" and t.satuan_id == "pasal-2"
        assert t.jenis_tanda == JenisTanda.CATATAN and t.fase == 2
        assert t.rujukan.status == "visual"
        assert t.rujukan.butir == "Lampiran II angka III huruf C butir 54 huruf j, hlm 41"
        assert t.rujukan.halaman == "41" and t.rujukan.kutipan.startswith("Penulisan bilangan")

    def test_letak_berupa_nomor_paragraf(self):
        par = naskah()
        i = _indeks(par, BATANG[5])
        assert verifikasi_satu(_c(letak=f"¶{i}"), _g(par)).temuan is not None

    def test_kutipan_tidak_ada_di_letak_gugur(self):
        h = verifikasi_satu(_c(kutipan="40 (empat puluh)"), _g())
        assert h.temuan is None and "kutipan tidak ketemu persis" in h.alasan

    def test_kutipan_di_pasal_lain_gugur(self):
        h = verifikasi_satu(_c(letak="pasal-3"), _g())
        assert h.temuan is None and "kutipan tidak ketemu persis" in h.alasan

    def test_kutipan_ganda_tidak_ditandai_tetap_di_panel(self):
        """Jaring kedua: yang pertama belum tentu yang salah — tidak ditandai sama sekali."""
        h = verifikasi_satu(_c(analisis="F2-102", letak="pasal-1", kutipan="Barang"), _g())
        t = h.temuan
        assert t is not None and t.lokasi.paragraf_index == -1
        assert "muncul lebih dari sekali" in t.catatan

    def test_letak_karangan_gugur(self):
        assert "tidak ada di peta letak" in verifikasi_satu(_c(letak="pasal-9"), _g()).alasan

    def test_skor_di_bawah_ambang_gugur(self):
        assert "di bawah ambang" in verifikasi_satu(_c(skor=0.5), _g()).alasan

    def test_menyebut_pasal_yang_tidak_ada_gugur(self):
        assert "Pasal yang tidak ada" in verifikasi_satu(_c(temuan="Bertabrakan dengan Pasal 9."), _g()).alasan
        # "Peraturan Menteri ini" = naskah ini sendiri; nomornya tetap diperiksa.
        c = _c(temuan="Bertabrakan dengan Pasal 9 Peraturan Menteri ini.")
        assert "Pasal yang tidak ada" in verifikasi_satu(c, _g()).alasan

    def test_pasal_peraturan_lain_tidak_diperiksa_di_naskah_ini(self):
        for teks in ("Sejalan dengan PMK 99 Tahun 2019 Pasal 12.", "Sejalan dengan Pasal 12 Undang-Undang Nomor 1 Tahun 2004."):
            assert verifikasi_satu(_c(temuan=teks), _g()).temuan is not None, teks

    def test_dua_arah_tanpa_dua_bacaan_berbeda_gugur(self):
        c = _c(analisis="F2-101", bacaan=["hari kalender", "hari kalender"])
        assert "dua bacaan" in verifikasi_satu(c, _g()).alasan


class TestFormat:
    def test_bukti_format_tidak_cocok_gugur(self):
        par = naskah()
        i = _indeks(par, BATANG[5])
        c = _c(analisis="F-19", letak=f"¶{i}", kutipan="xx", bukti_format='tersembunyi: "xx"')
        h = verifikasi_satu(c, _g(par, anotasi={i: "Bookman Old Style 12"}))
        assert h.temuan is None and "bukti format" in h.alasan

    def test_teks_tersembunyi_dikomentari_tanpa_sorot_di_kata_terlihat(self):
        batang = list(BATANG)
        batang[5] = "jJ jJ " + BATANG[5]
        par = _naskah(batang)
        i = _indeks(par, batang[5])
        par[i] = par[i].model_copy(update={"format": FormatParagraf(tersembunyi=["jJ jJ"])})
        c = _c(analisis="F-19", letak=f"¶{i}", kutipan="jJ jJ", bukti_format='tersembunyi: "jJ jJ"')
        h = verifikasi_satu(c, _g(par, anotasi={i: 'tersembunyi: "jJ jJ"'}))
        t = h.temuan
        assert t is not None, h.alasan
        assert t.tanpa_sorot and t.lokasi.teks_asli == "Pengguna" and t.lokasi.paragraf_index == i
        assert t.rujukan.status == "prioritas"

    def test_butir_kosong_menempel_di_kata_terakhir_sebelumnya(self):
        batang = BATANG[:6] + [""] + BATANG[6:]
        par = _naskah(batang)
        isi = _indeks(par, BATANG[5])
        kosong = isi + 1
        c = _c(analisis="F-20", letak=f"¶{kosong}", kutipan="b.", bukti_format="butir bernomor tanpa isi", ketiadaan=True)
        h = verifikasi_satu(c, _g(par, anotasi={kosong: "butir bernomor tanpa isi"}))
        t = h.temuan
        assert t is not None, h.alasan
        assert t.tanpa_sorot and t.lokasi.paragraf_index == isi and t.lokasi.teks_asli == "hari."


class TestBatasRespons:
    def test_usulan_pada_respons_catatan_diturunkan_jadi_contoh(self):
        c = _c(bentuk="usulan", usulan="30 (tiga puluh) hari kerja")
        temuan, gugur = verifikasi([c], _g())
        t = temuan[0]
        assert t.jenis_tanda == JenisTanda.CATATAN and t.usulan_rumusan is None
        assert 'Contoh rumusan: "30 (tiga puluh) hari kerja"' in t.saran
        assert any("DITURUNKAN — bentuk usulan melewati Respons catatan" in g for g in gugur)

    def test_salah_ketik_yang_ejaannya_ada_di_naskah_jadi_hijau(self):
        batang = list(BATANG)
        batang[5] = BATANG[5].replace("permohonan", "permohnan")
        g = _g(_naskah(batang))
        c = _c(analisis="S-64", kutipan="permohnan", bentuk="usulan", usulan="permohonan")
        h = verifikasi_satu(c, g)
        t = h.temuan
        assert t is not None, h.alasan
        assert t.jenis_tanda == JenisTanda.PENGGANTIAN and t.usulan_rumusan == "permohonan", h.diturunkan
        assert t.sumber_usulan == "ejaan yang sama tertulis di bagian lain naskah ini"
        assert t.rujukan.status == "prioritas"

    def test_usulan_berkata_baru_tanpa_sumber_diturunkan(self):
        c = _c(analisis="S-64", kutipan="mengajukan", bentuk="usulan", usulan="menyampaikan")
        h = verifikasi_satu(c, _g())
        assert h.temuan.jenis_tanda == JenisTanda.CATATAN
        assert any("tanpa sumber" in x for x in h.diturunkan), h.diturunkan


BATANG_RUJUK = BATANG[:6] + [
    "Pasal 3",
    "Permohonan sebagaimana dimaksud dalam Pasal 4 diajukan secara tertulis.",
    "Pasal 4",
    "Peraturan Menteri ini mulai berlaku pada tanggal diundangkan.",
]


class TestRujukanInternal:
    def test_yang_ditandai_cuma_rujukan_yang_tujuannya_ada_gugur(self):
        c = _c(analisis="F2-001", letak="pasal-3", kutipan="sebagaimana dimaksud dalam Pasal 4")
        h = verifikasi_satu(c, _g(_naskah(BATANG_RUJUK, lampiran=False)))
        assert h.temuan is None and "cuma rujukan internal" in h.alasan

    def test_i37_dikecualikan_dan_usulannya_bersumber_tujuan_yang_ada(self):
        c = _c(analisis="I-37", letak="pasal-3", kutipan="Pasal 4", bentuk="usulan", usulan="Pasal 2")
        h = verifikasi_satu(c, _g(_naskah(BATANG_RUJUK, lampiran=False)))
        t = h.temuan
        assert t is not None, h.alasan
        assert t.jenis_tanda == JenisTanda.PENGGANTIAN, h.diturunkan
        assert t.usulan_rumusan == "Pasal 2" and t.sumber_usulan


class TestDibuang:
    def _f2003(self, **ganti):
        isi = dict(
            analisis="F2-003", letak="pasal-1-angka-1", kutipan="Pengelola Barang", bentuk="dibuang",
            alasan_buang="tidak_dipakai", tidak_ada=["Pengelola Barang"],
            temuan='Istilah "Pengelola Barang" tidak dipakai di luar Pasal 1.',
        )
        isi.update(ganti)
        return _c(**isi)

    def test_istilah_yang_terbukti_tidak_dipakai_dicoret(self):
        h = verifikasi_satu(self._f2003(), _g())
        t = h.temuan
        assert t is not None, h.alasan
        assert t.jenis_tanda == JenisTanda.PENGHAPUSAN and t.lokasi.teks_asli == "Pengelola Barang"
        assert t.rujukan.kutipan.count(" | ") == 1  # butir 61 dan 64

    def test_istilah_yang_ternyata_dipakai_gugur(self):
        c = self._f2003(letak="pasal-1-angka-2", kutipan="Pengguna Barang", tidak_ada=["Pengguna Barang"])
        h = verifikasi_satu(c, _g())
        assert h.temuan is None and "padahal ada di paragraf" in h.alasan

    def test_tanpa_istilah_di_tidak_ada_gugur(self):
        """Kalimat definisi utuh tidak pernah muncul dua kali — itu bukan bukti istilahnya tidak dipakai."""
        c = self._f2003(
            kutipan="Pengguna Barang adalah pejabat pemegang kewenangan penggunaan barang.",
            letak="pasal-1-angka-2", tidak_ada=[],
        )
        h = verifikasi_satu(c, _g())
        assert h.temuan is None and "tidak_ada" in h.alasan

    def test_f2003_sebagai_catatan_pun_dibuktikan(self):
        c = self._f2003(letak="pasal-1-angka-2", kutipan="Pengguna Barang", tidak_ada=["Pengguna Barang"], bentuk="catatan")
        assert verifikasi_satu(c, _g()).temuan is None

    def test_mengulang_tanpa_kembaran_jadi_catatan_hapus(self):
        c = _c(
            analisis="F2-102", kutipan="paling lambat 30 (tiga puluh) hari", bentuk="dibuang",
            alasan_buang="mengulang", bukti_letak="pasal-4",
        )
        h = verifikasi_satu(c, _g())
        assert h.temuan.jenis_tanda == JenisTanda.CATATAN
        assert 'Hapus "paling lambat 30 (tiga puluh) hari".' in h.temuan.saran

    def test_mengulang_yang_terbukti_dicoret(self):
        batang = BATANG[:9] + [BATANG[5]]
        c = _c(analisis="F2-102", kutipan=BATANG[5], bentuk="dibuang", alasan_buang="mengulang", bukti_letak="pasal-4")
        h = verifikasi_satu(c, _g(_naskah(batang)))
        assert h.temuan.jenis_tanda == JenisTanda.PENGHAPUSAN, h.diturunkan

    def test_frasa_dilarang_tanpa_kutipan_kaidah_jadi_catatan(self):
        c = _c(analisis="F2-102", kutipan="paling lambat", bentuk="dibuang", alasan_buang="frasa_dilarang")
        h = verifikasi_satu(c, _g())
        assert h.temuan.jenis_tanda == JenisTanda.CATATAN
        assert any("frasa_dilarang" in x for x in h.diturunkan)


class TestSisipan:
    def _calon(self, **sisipan):
        isi = {"sasaran": "pasal-1", "bentuk": "angka", "teks": "Permohonan adalah surat yang diajukan Pengguna Barang kepada Pengelola Barang."}
        isi.update(sisipan)
        return _c(analisis="F2-102", kutipan="mengajukan permohonan", temuan="Permohonan belum berdefinisi.", sisipan=isi)

    def test_angka_baru_bernomor_berikutnya_sesudah_butir_terakhir(self):
        par = naskah()
        h = verifikasi_satu(self._calon(), _g(par))
        s = h.temuan.sisipan
        assert s is not None, h.diturunkan
        assert s.penanda == "3." and s.sasaran == "pasal-1"
        assert s.sesudah_paragraf == _indeks(par, BATANG[3])
        assert s.sumber == "(prediksi AI)" and h.temuan.sumber_usulan == "(prediksi AI)"
        assert h.temuan.jenis_tanda == JenisTanda.CATATAN

    def test_isi_yang_ada_di_korpus_menyebut_peraturannya(self):
        cat = CatatanPutaran(korpus=[{"teks": "permohonan", "pembanding": [{
            "sebutan": "PMK 10 Tahun 2020", "judul": "uji", "pasal": "pasal-1",
            "potongan": "3. Permohonan adalah surat yang diajukan Pengguna Barang kepada Pengelola Barang.",
        }]}])
        s = verifikasi_satu(self._calon(), _g(catatan=cat)).temuan.sisipan
        assert s.sumber == "PMK 10 Tahun 2020 Pasal 1 (masih berlaku)"

    def test_respons_catatan_tidak_boleh_menyisipkan(self):
        c = self._calon()
        c.analisis = "F2-007"
        c.kutipan = "30 (tiga puluh)"
        h = verifikasi_satu(c, _g())
        assert h.temuan.sisipan is None
        assert "Contoh rumusan angka baru" in h.temuan.saran

    def test_bentuk_pasal_belum_didukung(self):
        h = verifikasi_satu(self._calon(bentuk="pasal"), _g())
        assert h.temuan.sisipan is None and any("belum didukung" in x for x in h.diturunkan)

    def test_dua_sisipan_di_tempat_sama_bernomor_berurutan(self):
        c1 = self._calon()
        c2 = self._calon(teks="Surat adalah naskah dinas yang diajukan Pengguna Barang kepada Pengelola Barang.")
        c2.nomor, c2.kutipan = "C2", "Pengguna Barang wajib"
        temuan, _ = verifikasi([c1, c2], _g())
        assert sorted(t.sisipan.penanda for t in temuan) == ["3.", "4."]
        # menjorok disamakan dengan angka terakhir Pasal 1
        assert {t.sisipan.format_dari for t in temuan} == {_indeks(naskah(), BATANG[3])}

    def test_sisipan_kembar_disisipkan_sekali(self):
        c1, c2 = self._calon(), self._calon()
        c2.nomor, c2.kutipan = "C2", "Pengguna Barang wajib"
        temuan, gugur = verifikasi([c1, c2], _g())
        assert len(temuan) == 2 and sum(1 for t in temuan if t.sisipan) == 1
        assert any("sisipan kembar" in g for g in gugur)

    def test_tempat_sisipan_karangan(self):
        h = verifikasi_satu(self._calon(sasaran="pasal-9"), _g())
        assert h.temuan.sisipan is None and any("tidak ada di peta letak" in x for x in h.diturunkan)


class TestPeriksaUlang:
    def test_bertindihan_dengan_temuan_lama_gugur_apa_pun_kodenya(self):
        lama = verifikasi_satu(_c(), _g()).temuan
        lama.nomor = 4
        c = _c(analisis="F2-101", kutipan="paling lambat 30 (tiga puluh) hari", bacaan=["hari kerja", "hari kalender"])
        temuan, gugur = verifikasi([c], _g(lama=[lama]))
        assert not temuan
        assert any("bertindihan dengan temuan lama T4 (F2-007)" in x for x in gugur)

    def test_tempat_lain_tetap_lolos(self):
        lama = verifikasi_satu(_c(), _g()).temuan
        c = _c(analisis="F2-102", kutipan="Pengguna Barang wajib")
        temuan, _ = verifikasi([c], _g(lama=[lama]))
        assert len(temuan) == 1


class TestRujukanAgen:
    def _f2101(self, rujukan):
        return _c(analisis="F2-101", kutipan="paling lambat 30 (tiga puluh) hari", bacaan=["hari kerja", "hari kalender"], rujukan=rujukan)

    def test_alamat_dan_kutipan_di_baris_kaidah_yang_sama(self):
        r = verifikasi_satu(self._f2101({
            "alamat": "KMK 527 Lampiran II angka III huruf C butir 54 huruf a, hlm 39",
            "kutipan": "memuat satu norma dan dirumuskan dalam satu kalimat",
        }), _g()).temuan.rujukan
        assert r.status == "agen" and r.halaman == "39"
        assert r.butir == "Lampiran II angka III huruf C butir 54 huruf a, hlm 39"

    def test_alamat_awalan_tidak_diterima(self):
        """'butir 5' tidak boleh meminjam kutipan 'butir 54'."""
        r = verifikasi_satu(self._f2101({
            "alamat": "Lampiran II angka III huruf C butir 5",
            "kutipan": "memuat satu norma dan dirumuskan dalam satu kalimat",
        }), _g()).temuan.rujukan
        assert r.status == "tanpa"

    def test_kutipan_karangan_tanpa_rujukan(self):
        r = verifikasi_satu(self._f2101({
            "alamat": "Lampiran II angka III huruf C butir 54 huruf a, hlm 39",
            "kutipan": "pasal wajib dibaca dua arah sekaligus",
        }), _g()).temuan.rujukan
        assert r.status == "tanpa" and not r.butir


class TestKorpus:
    def test_pembanding_yang_tidak_tercatat_gugur(self):
        c = _c(analisis="F3-001", kutipan="paling lambat 30 (tiga puluh) hari", pembanding="PMK 99 Tahun 2019",
               temuan="Berpotensi bertentangan dengan PMK 99 Tahun 2019.")
        h = verifikasi_satu(c, _g(catatan=CatatanPutaran()))
        assert h.temuan is None and "cari_korpus" in h.alasan

    def test_f3001_wajib_berbahasa_berpotensi(self):
        cat = CatatanPutaran(korpus=[{"teks": "30 hari", "pembanding": [
            {"sebutan": "PMK 99 Tahun 2019", "judul": "uji", "pasal": "pasal-5", "potongan": "paling lambat 14 hari"}
        ]}])
        c = _c(analisis="F3-001", kutipan="paling lambat 30 (tiga puluh) hari", pembanding="PMK 99 Tahun 2019",
               temuan="Bertentangan dengan PMK 99 Tahun 2019.")
        assert "berpotensi bertentangan" in verifikasi_satu(c, _g(catatan=cat)).alasan
        c.temuan = "Berpotensi bertentangan dengan PMK 99 Tahun 2019 Pasal 5."
        t = verifikasi_satu(c, _g(catatan=cat)).temuan
        assert t is not None and t.pembanding == "PMK 99 Tahun 2019 Pasal 5 (masih berlaku)" and t.fase == 3
