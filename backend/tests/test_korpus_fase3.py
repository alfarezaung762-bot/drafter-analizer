"""Tes lapisan korpus Fase 3 — TANPA jaringan.

Jawaban OpenSearch di sini disalin dari bentuk yang SUNGGUHAN, diperiksa
langsung ke indeks `law_analyzer_emb3sm` pada 23 Sep 2026. Tebakan bentuk
sebelumnya seluruhnya keliru (huruf kecil, medan teks datar), dan tes yang
memakai bentuk tebakan cuma membuktikan tebakannya konsisten dengan dirinya
sendiri.
"""

from app.bersama.opensearch import (
    HasilCari,
    KorpusOpenSearch,
    Pembanding,
    baca_jawaban,
    saring_status,
)


def _hit(judul, nomor, status, pasal, isi, bentuk="Peraturan Menteri Keuangan", skor=1.7):
    return {
        "_score": skor,
        "_source": {
            "Judul": judul,
            "Nomor": nomor,
            "Bentuk": bentuk,
            "Status": status,
            "Tahun": 2024,
        },
        "inner_hits": {
            "Blocks": {
                "hits": {
                    "hits": [{"_source": {"Pasal": pasal, "Content": isi}}]
                }
            }
        },
    }


def _jawaban(*hits):
    return {"hits": {"hits": list(hits)}}


class TestSaringStatus:
    def test_berlaku(self):
        assert saring_status("Berlaku") is True

    def test_tidak_berlaku(self):
        assert saring_status("Tidak Berlaku") is False

    def test_dicabut(self):
        assert saring_status("Dicabut") is False

    def test_kosong_tidak_terbaca(self):
        assert saring_status("") is None

    def test_tetap_tidak_terbaca(self):
        """"Tetap" ada 211 dokumen di indeks jdih dan artinya belum jelas.

        Yang tidak jelas diperlakukan sama dengan dicabut — memilih diam.
        """
        assert saring_status("Tetap") is None


class TestBacaJawaban:
    def test_pembanding_berlaku_terbaca_utuh(self):
        h = baca_jawaban(
            _jawaban(
                _hit(
                    "Tata Cara Penggunaan Barang Milik Negara",
                    "PMK 40 TAHUN 2024",
                    "Berlaku",
                    "pasal-14",
                    "(1) Pengelola Barang melakukan penetapan status Penggunaan BMN.",
                )
            ),
            5,
        )
        assert len(h.pembanding) == 1
        p = h.pembanding[0]
        assert p.pasal == "pasal-14"
        assert p.sebutan == "Peraturan Menteri Keuangan PMK 40 TAHUN 2024"
        assert "penetapan status" in p.potongan

    def test_PENYARING_KERAS_peraturan_dicabut_dibuang(self):
        """Menyodorkan peraturan cabut bukan temuan lemah — temuan SALAH."""
        h = baca_jawaban(
            _jawaban(_hit("Judul", "PMK 1/2010", "Tidak Berlaku", "pasal-2", "isi")), 5
        )
        assert h.pembanding == []
        assert h.dibuang_dicabut == 1

    def test_status_tidak_terbaca_juga_dibuang_dan_dihitung_terpisah(self):
        h = baca_jawaban(_jawaban(_hit("Judul", "PMK 1/2010", "", "pasal-2", "isi")), 5)
        assert h.pembanding == []
        assert h.dibuang_status_kosong == 1
        assert "status berlakunya tidak terbaca" in h.ringkas

    def test_tanpa_kutipan_tidak_dipakai(self):
        """Pembanding tanpa teks tidak bisa ditimbang penelaah."""
        h = baca_jawaban(_jawaban(_hit("Judul", "PMK 1/2024", "Berlaku", "pasal-2", "")), 5)
        assert h.pembanding == []

    def test_jumlah_dibatasi(self):
        hits = [
            _hit(f"Judul {i}", f"PMK {i}/2024", "Berlaku", "pasal-1", "isi")
            for i in range(9)
        ]
        assert len(baca_jawaban(_jawaban(*hits), 3).pembanding) == 3

    def test_nama_sah_dipakai_langkah_5(self):
        h = baca_jawaban(
            _jawaban(
                _hit("A", "PMK 40 TAHUN 2024", "Berlaku", "pasal-14", "isi"),
                _hit("B", "PP 27 TAHUN 2014", "Berlaku", "pasal-17", "isi",
                     bentuk="Peraturan Pemerintah"),
            ),
            5,
        )
        assert h.nama_sah == {
            "Peraturan Menteri Keuangan PMK 40 TAHUN 2024",
            "Peraturan Pemerintah PP 27 TAHUN 2014",
        }


class TestBentukKueri:
    """Bentuk kueri dikunci di tes karena kesalahannya TIDAK BERSUARA.

    Kueri `knn` biasa terhadap indeks yang `index.knn`-nya mati mengembalikan
    nol hasil tanpa error. Kalau bentuknya berubah diam-diam, gejalanya cuma
    "Fase 3 tidak pernah menemukan apa-apa" — dan itu bisa berbulan-bulan
    tidak ketahuan.
    """

    def _badan(self, vektor):
        k = KorpusOpenSearch.__new__(KorpusOpenSearch)
        inti = k._inti_vektor(vektor) if vektor else k._inti_teks("kata kunci")
        return k._badan(inti, 5)

    def test_memakai_script_score_BUKAN_knn_biasa(self):
        b = self._badan([0.1] * 1536)
        teks = str(b)
        assert "script_score" in teks
        assert "knn_score" in teks
        assert "'knn': {'Blocks" not in teks  # kueri knn biasa tidak dipakai

    def test_status_berlaku_jadi_penyaring_keras_di_tingkat_dokumen(self):
        b = self._badan([0.1] * 1536)
        assert {"term": {"Status": "Berlaku"}} in b["query"]["bool"]["filter"]

    def test_kutipan_diambil_dari_blok_induk_bukan_dari_chunk(self):
        """Vektor ada di Chunks, teks ada di Blocks induknya."""
        b = self._badan([0.1] * 1536)
        luar = b["query"]["bool"]["must"][0]["nested"]
        assert luar["path"] == "Blocks"
        assert "Blocks.Content" in luar["inner_hits"]["_source"]["includes"]
        dalam = luar["query"]["bool"]["must"][0]["nested"]
        assert dalam["path"] == "Blocks.Chunks"

    def test_hanya_blok_pasal_yang_jadi_pembanding(self):
        b = self._badan([0.1] * 1536)
        saring = b["query"]["bool"]["must"][0]["nested"]["query"]["bool"]["filter"]
        assert {"match_phrase": {"Blocks.Type": "CONTENT_PASAL"}} in saring

    def test_tanpa_vektor_jatuh_ke_pencarian_teks(self):
        b = self._badan(None)
        assert "script_score" not in str(b)
        assert "Blocks.Content" in str(b["query"]["bool"]["must"][0]["nested"]["query"])
