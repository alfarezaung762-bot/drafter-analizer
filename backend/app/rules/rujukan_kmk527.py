"""Tabel rujukan KMK 527 — statis, diverifikasi manusia.

Setiap aturan Fase 1 punya satu entri di sini. Butir dan kutipan
harus diisi dari pembacaan visual KMK 527 Lampiran II — BUKAN dari
OCR, BUKAN dari OpenSearch, BUKAN dari model.

Selama butir/kutipan masih placeholder ("..."), temuan WAJIB ditandai
"rujukan belum diverifikasi" di UI (gate legal).
"""

RUJUKAN: dict[str, dict[str, object]] = {
    "F1-001": {
        "nama_aturan": "Judul ditulis kapital seluruhnya",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
    "F1-002": {
        "nama_aturan": "Judul pembuka konsisten dengan judul pada Menetapkan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
    "F1-003": {
        "nama_aturan": "Kelengkapan Menimbang / Mengingat / Menetapkan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
    "F1-004": {
        "nama_aturan": "Frasa baku butir Menimbang terakhir",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
    "F1-005": {
        "nama_aturan": "Ejaan baku penyusunan peraturan",
        "sumber": "KMK 527/KMK.01/2022 Lampiran II",
        "butir": "...",
        "kutipan": "...",
        "halaman_pdf": 0,
        "pdf_url": "https://jdih.kemenkeu.go.id/...",
    },
}


def rujukan_sudah_lengkap(aturan_id: str) -> bool:
    """Cek apakah butir dan kutipan sudah diisi (bukan placeholder)."""
    entri = RUJUKAN.get(aturan_id)
    if entri is None:
        return False
    return entri["butir"] != "..." and entri["kutipan"] != "..."


def ambil_rujukan(aturan_id: str) -> dict[str, str]:
    """Ambil rujukan untuk aturan tertentu.

    Returns dict dengan key: sumber, butir, kutipan, pdf_url.
    """
    entri = RUJUKAN.get(aturan_id)
    if entri is None:
        raise KeyError(f"Aturan {aturan_id} tidak ditemukan di tabel rujukan")
    return {
        "sumber": str(entri["sumber"]),
        "butir": str(entri["butir"]),
        "kutipan": str(entri["kutipan"]),
        "pdf_url": str(entri["pdf_url"]),
    }
