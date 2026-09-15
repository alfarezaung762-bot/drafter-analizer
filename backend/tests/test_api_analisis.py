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
    assert len(data["temuan"]) >= 1

    # Cek bahwa temuan judul kapital tertangkap
    temuan_f1_001 = [t for t in data["temuan"] if t["aturan_id"] == "F1-001"]
    assert len(temuan_f1_001) == 1
    assert temuan_f1_001[0]["tingkat_keparahan"] == "tinggi"
    assert temuan_f1_001[0]["usulan_rumusan"] == "TATA CARA PENYUSUNAN ANGGARAN"
    assert temuan_f1_001[0]["rujukan"]["butir"] == "..."
