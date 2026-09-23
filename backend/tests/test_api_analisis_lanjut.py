"""Tes endpoint /analisis/lanjut — TANPA memanggil model.

Yang diuji di sini kontrak HTTP-nya saja: rutenya terdaftar, pekerjaan yang
tidak ada dijawab 404, dan bentuk jawabannya sesuai. Jalur analisisnya sendiri
sudah diuji tuntas di test_alur_fase2.py dengan KlienPalsu.

Sengaja TIDAK ada tes yang benar-benar memulai pekerjaan: `_jalankan` memanggil
Azure OpenAI sungguhan di utas terpisah, dan tes yang memanggil layanan
berbayar bukan tes lagi.
"""

from fastapi.testclient import TestClient

from app.db import simpanan
from app.main import app
from app.models.pekerjaan import BarisPeta, Dugaan

# DATABASE_URL dikosongkan untuk seluruh suite oleh tests/conftest.py. Tanpa
# itu, GET /analisis/lanjut/{nomor} menyambung ke Postgres sungguhan dan tes
# berubah jadi pemeriksaan jaringan.
klien = TestClient(app)

_PARAGRAF = [
    {"index": i, "teks": t}
    for i, t in enumerate(
        [
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
            "1. Pengguna Barang adalah pejabat pemegang kewenangan.",
            "Pasal 2",
            "Pengguna Barang wajib mengajukan permohonan paling lambat 30 hari.",
        ]
    )
]


def test_rute_terdaftar():
    jalan = klien.get("/openapi.json").json()["paths"]
    assert "/analisis/lanjut" in jalan
    assert "/analisis/lanjut/{nomor}" in jalan
    assert "/analisis/tahap0" in jalan
    assert "/analisis/tahap3" in jalan


def test_pekerjaan_yang_tidak_ada_dijawab_404():
    resp = klien.get("/analisis/lanjut/999999")
    assert resp.status_code == 404


def test_fase_1_tidak_terganggu():
    """Endpoint lama tetap berjalan apa adanya."""
    resp = klien.post(
        "/analisis/jalankan",
        json={
            "jenis_dokumen": "PMK",
            "paragraf": [{"index": 0, "teks": "Pasal 1"}],
        },
    )
    assert resp.status_code == 200
    assert "temuan" in resp.json()


# ---------------------------------------------------------------------------
# Ekspor Tahap 3 — alat pengembang, tidak memanggil model
# ---------------------------------------------------------------------------


def test_tahap3_tanpa_pekerjaan_menjawab_peta_kosong():
    """Bukan 404 dan bukan galat: belum ada analisis adalah keadaan yang wajar,
    dan jawabannya harus menjelaskan sebabnya, bukan membuat panel gagal."""
    resp = klien.post(
        "/analisis/tahap3", json={"paragraf": _PARAGRAF, "dokumen": "belum-ada.docx"}
    )
    assert resp.status_code == 200
    assert "PETA KOSONG" in resp.text


def test_tahap3_jatuh_ke_pekerjaan_terbaru_dokumen_itu():
    """Panel yang dimuat ulang lupa nomor pekerjaannya. Tanpa jatuh-tempo ini,
    ekspornya selalu kosong sesudah panel ditutup sekali."""
    nomor = simpanan.buat("uji.docx")
    simpanan.simpan_peta(
        nomor, [BarisPeta(satuan_id="pasal-2", ringkasan="Mewajibkan permohonan.")]
    )
    simpanan.simpan_dugaan(
        nomor, [Dugaan(satuan_id="pasal-2", jenis="pemikul", alasan="tidak jelas")]
    )

    resp = klien.post(
        "/analisis/tahap3", json={"paragraf": _PARAGRAF, "dokumen": "uji.docx"}
    )
    assert resp.status_code == 200
    assert f"#{nomor}" in resp.text
    assert "Mewajibkan permohonan." in resp.text
    assert "DUGAAN (1)" in resp.text


def test_tahap3_dokumen_lain_tidak_ikut_terbawa():
    """Peta dokumen lain yang bocor ke sini akan dibaca sebagai peta dokumen
    ini, dan penelusur bug akan mengejar hantu."""
    lain = simpanan.buat("lain.docx")
    simpanan.simpan_peta(
        lain, [BarisPeta(satuan_id="pasal-9", ringkasan="Ringkasan dokumen lain.")]
    )
    resp = klien.post(
        "/analisis/tahap3", json={"paragraf": _PARAGRAF, "dokumen": "uji.docx"}
    )
    assert "Ringkasan dokumen lain." not in resp.text
    assert "PETA KOSONG" in resp.text


def test_tahap3_teks_biasa_bukan_json():
    """Panel mengunduhnya sebagai .txt apa adanya."""
    resp = klien.post("/analisis/tahap3", json={"paragraf": _PARAGRAF})
    assert resp.headers["content-type"].startswith("text/plain")
