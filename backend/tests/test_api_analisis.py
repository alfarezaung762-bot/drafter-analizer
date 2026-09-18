"""Tes untuk endpoint FastAPI POST /analisis/jalankan."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analisis_jalankan_endpoint():
    payload = {
        "jenis_dokumen": "PMK",
        "paragraf": [
            {"index": 0, "teks": "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA"},
            {"index": 1, "teks": "NOMOR 100/PMK.01/2024"},
            {"index": 2, "teks": "TENTANG"},
            {"index": 3, "teks": "Tata Cara Penyusunan Anggaran"},
            {"index": 4, "teks": "DENGAN RAHMAT TUHAN YANG MAHA ESA"},
            {"index": 5, "teks": "MENTERI KEUANGAN REPUBLIK INDONESIA,"},
        ]
    }
    response = client.post("/analisis/jalankan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "temuan" in data
    assert "jumlah_paragraf" in data
    assert data["jumlah_paragraf"] == 6

    # Cek struktur tiap temuan yang dikembalikan
    for t in data["temuan"]:
        assert "aturan_id" in t
        assert "jenis_tanda" in t
        assert t["jenis_tanda"] in ("penggantian", "catatan")
        assert "lokasi" in t
        assert "rujukan" in t

