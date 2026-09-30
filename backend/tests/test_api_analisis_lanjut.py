"""Tes endpoint /analisis/lanjut dan ekspor tahap 1–5 — TANPA memanggil model.

Yang diuji di sini kontrak HTTP-nya saja: rutenya terdaftar, pekerjaan yang
tidak ada dijawab 404, dan bentuk jawabannya sesuai. Jalur analisisnya sendiri
sudah diuji tuntas di test_alur_fase2.py dan test_tahap3_cari_dugaan.py dengan
KlienPalsu.

Sengaja TIDAK ada tes yang benar-benar memulai pekerjaan: `_jalankan` memanggil
Azure OpenAI sungguhan di utas terpisah, dan tes yang memanggil layanan
berbayar bukan tes lagi.
"""

from fastapi.testclient import TestClient

from app.db import simpanan
from app.main import app
from tests.naskah_uji import naskah

# DATABASE_URL dikosongkan untuk seluruh suite oleh tests/conftest.py. Tanpa
# itu, GET /analisis/lanjut/{nomor} menyambung ke Postgres sungguhan dan tes
# berubah jadi pemeriksaan jaringan.
klien = TestClient(app)

_PARAGRAF = [p.model_dump() for p in naskah()]


def test_rute_terdaftar():
    jalan = klien.get("/openapi.json").json()["paths"]
    assert "/analisis/lanjut" in jalan
    assert "/analisis/lanjut/{nomor}" in jalan
    for tahap in range(1, 6):
        assert f"/analisis/tahap{tahap}" in jalan
    assert "/analisis/tahap0" not in jalan


def test_pekerjaan_yang_tidak_ada_dijawab_404():
    resp = klien.get("/analisis/lanjut/999999")
    assert resp.status_code == 404


def test_kemajuan_menyebut_tahapnya():
    nomor = simpanan.buat("uji.docx")
    simpanan.perbarui(nomor, tahap="3 cari dugaan", selesai=2, total=5)
    isi = klien.get(f"/analisis/lanjut/{nomor}").json()
    assert (isi["tahap"], isi["selesai"], isi["total"]) == ("3 cari dugaan", 2, 5)


def test_fase_1_tidak_terganggu():
    """Endpoint lama tetap berjalan apa adanya."""
    resp = klien.post(
        "/analisis/jalankan",
        json={"jenis_dokumen": "PMK", "paragraf": [{"index": 0, "teks": "Pasal 1"}]},
    )
    assert resp.status_code == 200
    assert "temuan" in resp.json()


# ---------------------------------------------------------------------------
# Ekspor — alat pengembang, tidak memanggil model
# ---------------------------------------------------------------------------


def test_tahap1_dan_tahap2_disusun_dari_naskah_saat_ini():
    for tahap, kepala in ((1, "===== TAHAP 1 · POHON SATUAN"), (2, "===== TAHAP 2 · PERKIRAAN TOKEN")):
        resp = klien.post(f"/analisis/tahap{tahap}", json={"paragraf": _PARAGRAF})
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/plain")
        assert resp.text.startswith(kepala)


def test_tahap2_menerima_kerangka_tabel_raksasa():
    sesudah = next(p["index"] for p in _PARAGRAF if p["teks"] == "DAFTAR BARANG")
    resp = klien.post(
        "/analisis/tahap2",
        json={
            "paragraf": _PARAGRAF,
            "tabel_raksasa": [
                {"tabel": 40, "sesudah_paragraf": sesudah, "jumlah_baris": 5000,
                 "jumlah_kolom": 2, "contoh": [["Desa", "Jumlah"]]}
            ],
        },
    )
    assert "[TABEL 40 · KERANGKA DARI PANEL — 5.000 baris × 2 kolom." in resp.text


def test_tahap3_tanpa_pekerjaan_menjawab_satu_kalimat():
    """Bukan 404 dan bukan galat: belum ada analisis adalah keadaan yang wajar."""
    resp = klien.post("/analisis/tahap3", json={"dokumen": "belum-ada.docx"})
    assert resp.status_code == 200
    assert resp.text.startswith("Pesan tahap 3 tidak tercatat")


def test_tahap3_jatuh_ke_pekerjaan_terbaru_dokumen_itu():
    """Panel yang dimuat ulang lupa nomor pekerjaannya. Tanpa jatuh-tempo ini,
    ekspornya selalu kosong sesudah panel ditutup sekali."""
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_pesan_tahap3(nomor, [("TAHAP 3 · LINTAS NASKAH", [("system", "PERAN"), ("user", "isi")])])
    resp = klien.post("/analisis/tahap3", json={"dokumen": "uji.docx"})
    assert resp.text.startswith("===== TAHAP 3 · LINTAS NASKAH · system =====\nPERAN")


def test_tahap4_dokumen_lain_tidak_ikut_terbawa():
    """Pesan dokumen lain yang bocor ke sini akan dibaca sebagai milik dokumen
    ini, dan penelusur bug akan mengejar hantu."""
    lain = simpanan.buat("lain.docx")
    simpanan.simpan_pesan_tahap4(lain, [("x", [("user", "milik dokumen lain")])])
    resp = klien.post("/analisis/tahap4", json={"dokumen": "uji.docx"})
    assert "milik dokumen lain" not in resp.text


def test_tahap5_tersimpan_dikembalikan_apa_adanya():
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_ekspor_tahap5(nomor, "===== TAHAP 3 · DUGAAN (0) =====\n")
    resp = klien.post("/analisis/tahap5", json={"pekerjaan": nomor})
    assert resp.text == "===== TAHAP 3 · DUGAAN (0) =====\n"


def test_tahap5_tanpa_pekerjaan_satu_kalimat():
    resp = klien.post("/analisis/tahap5", json={"dokumen": "belum-ada.docx"})
    assert resp.text.startswith("Hasil tahap 5 tidak tercatat")
