"""Fase 4 — endpoint /analisis/daftar dan /analisis/agen, TANPA model sungguhan.

Utas analisis (`_jalankan`) dijalankan langsung dengan KlienAzure diganti
klien palsu: label, satu putaran agen, penilai kedua — lalu dijalankan ulang
dengan `lanjutkan` dan klien kosong, untuk membuktikan jawaban lama dipakai
ulang tanpa satu request pun.
"""

import json

from fastapi.testclient import TestClient

from app.api import analisis_agen
from app.bersama import llm
from app.db import simpanan
from app.main import app
from app.telaah.tahap1_bahan.parser_cadangan_pmk_biasa import bangun_pohon, id_awal_satuan
from tests.naskah_uji import naskah

klien = TestClient(app)
_PARAGRAF = naskah()


class _KlienPalsu(llm.KlienAgenPalsu):
    siap = True

    def __init__(self, langkah, label, penilai):
        super().__init__(langkah, penilai)
        self._label = label

    def tanya(self, peran, pesan):
        if "SUSUNAN" in peran:
            self.diminta_penilai.append((peran, pesan))
            return llm.Jawaban(self._label, 100, 10)
        return super().tanya(peran, pesan)


def _palsu(kosong: bool = False) -> _KlienPalsu:
    label = json.dumps({
        "jenis": "pmk biasa",
        "label": [{"p": p, "label": l} for p, l in id_awal_satuan(bangun_pohon(_PARAGRAF)).items()],
    })
    if kosong:
        return _KlienPalsu([], label, [])
    langkah = [
        [("catat_temuan", {"analisis": "F2-007", "letak": "pasal-2", "kutipan": "30 (tiga puluh)",
                           "bentuk": "catatan", "temuan": "Bilangan diperiksa.", "skor": 0.9})],
        [("selesai", {"laporan": [{"pasal": f"pasal-{i}", "analisis": "F2-007", "status": "diperiksa"} for i in range(1, 5)]})],
    ]
    return _KlienPalsu(langkah, label, ['{"putusan": [{"calon": "C1", "putusan": "setuju", "alasan": "nyata"}]}'])


def _jalan(monkeypatch, klien_palsu, lanjutkan=None) -> int:
    monkeypatch.setattr(llm, "KlienAzure", lambda: klien_palsu)
    req = analisis_agen.AnalisisAgenRequest(
        paragraf=_PARAGRAF, dokumen="uji-agen.docx", aturan_aktif=["F2-007"], lanjutkan=lanjutkan,
    )
    nomor = simpanan.buat(req.dokumen)
    simpanan.tanda_batal(nomor)
    analisis_agen._jalankan(nomor, req)
    return nomor


def test_rute_agen_terdaftar():
    jalan = klien.get("/openapi.json").json()["paths"]
    for rute in (
        "/analisis/daftar", "/analisis/agen", "/analisis/agen/{nomor}", "/analisis/agen/{nomor}/batal",
        "/analisis/agen/ekspor1", "/analisis/agen/ekspor2", "/analisis/agen/ekspor3",
    ):
        assert rute in jalan, rute


def test_daftar_dibaca_dari_formulir():
    isi = klien.get("/analisis/daftar", params={"jenis": "PMK"}).json()
    assert isi["alur"] in ("lama", "agen")
    kode = {a["id"] for a in isi["analisis"]}
    assert {"F2-101", "I-37", "S-64", "F-19", "F-20"} <= kode and "F1-001" not in kode
    a = next(x for x in isi["analisis"] if x["id"] == "F2-003")
    assert a["respons"] == "dibuang" and a["dasar_status"] == "visual" and a["diperiksa"]


def test_kmk_belum_tersedia():
    isi = klien.get("/analisis/daftar", params={"jenis": "KMK"}).json()
    assert isi["analisis"] and not any(a["tersedia"] for a in isi["analisis"])


def test_pekerjaan_yang_tidak_ada():
    assert klien.get("/analisis/agen/999999").status_code == 404
    assert klien.post("/analisis/agen/999999/batal").status_code == 404


def test_ekspor_tanpa_hasil_menyebut_terang():
    body = {"dokumen": "belum-pernah.docx", "paragraf": [p.model_dump() for p in _PARAGRAF]}
    assert "tidak tercatat" in klien.post("/analisis/agen/ekspor2", json=body).text
    assert "tidak tercatat" in klien.post("/analisis/agen/ekspor3", json=body).text
    # Ekspor 1 tetap bisa menyusun bahan tanpa AI.
    assert "¶" in klien.post("/analisis/agen/ekspor1", json=body).text


def test_jalan_utuh_lalu_dilanjutkan_tanpa_request_baru(monkeypatch):
    nomor = _jalan(monkeypatch, _palsu())
    isi = klien.get(f"/analisis/agen/{nomor}").json()
    assert isi["status"] == "selesai", isi["pesan"]
    assert [t["lokasi"]["teks_asli"] for t in isi["temuan"]] == ["30 (tiga puluh)"]
    assert isi["putaran"] and isi["putaran"][0]["keadaan"] == "selesai"
    assert isi["panggilan"] >= 3  # label + 2 langkah agen + penilai

    body = {"dokumen": "uji-agen.docx", "pekerjaan": nomor}
    assert "Putaran 1/1" in klien.post("/analisis/agen/ekspor2", json=body).text
    assert "LOLOS JADI TEMUAN (1)" in klien.post("/analisis/agen/ekspor3", json=body).text

    kosong = _palsu(kosong=True)
    nomor2 = _jalan(monkeypatch, kosong, lanjutkan=nomor)
    isi2 = klien.get(f"/analisis/agen/{nomor2}").json()
    assert isi2["status"] == "selesai", isi2["pesan"]
    assert [t["lokasi"]["teks_asli"] for t in isi2["temuan"]] == ["30 (tiga puluh)"]
    assert not kosong.diminta and not kosong.diminta_penilai


def test_batal_sebelum_mulai_tidak_menyentuh_apa_pun(monkeypatch):
    palsu = _palsu()
    monkeypatch.setattr(llm, "KlienAzure", lambda: palsu)
    req = analisis_agen.AnalisisAgenRequest(paragraf=_PARAGRAF, dokumen="uji-batal.docx", aturan_aktif=["F2-007"])
    nomor = simpanan.buat(req.dokumen)
    simpanan.tanda_batal(nomor)
    assert klien.post(f"/analisis/agen/{nomor}/batal").status_code == 200
    analisis_agen._jalankan(nomor, req)
    isi = klien.get(f"/analisis/agen/{nomor}").json()
    assert isi["status"] == "selesai" and isi["tahap"] == "dibatalkan" and not isi["temuan"]
    assert not palsu.diminta and not palsu.diminta_penilai  # label pun tidak diminta
