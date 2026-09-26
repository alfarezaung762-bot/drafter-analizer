"""Kontrak tabel rujukan KMK 527 — TANPA jaringan.

Yang dijaga di sini satu hal: **rujukan tidak boleh berbohong.** Butir yang
tertulis di komentar naskah penelaah adalah dasar hukum yang akan ia telusuri
sendiri; butir yang dikarang atau yang statusnya kebesaran merusak kepercayaan
lebih cepat daripada tidak ada rujukan sama sekali. CLAUDE.md butir 3.

Tes yang paling menentukan:
`TestStatus.test_butir_terisi_berarti_sudah_dibaca` — status "visual" atau
"turunan" hanya boleh dipasang setelah butirnya benar-benar dibaca dari citra
halaman, dan itu meninggalkan jejak berupa `halaman_pdf` yang bukan nol.
"""

import pytest

from app.rules.rujukan_kmk527 import (
    RUJUKAN,
    rujukan_sudah_lengkap,
    rujukan_turunan,
)

_STATUS_SAH = {"placeholder", "ekstraksi", "turunan", "visual"}

# Status yang menyatakan butirnya SUDAH dibaca manusia dari naskah.
_SUDAH_DIBACA = {"visual", "turunan"}


class TestBentuk:
    @pytest.mark.parametrize("aturan_id", sorted(RUJUKAN))
    def test_medan_wajib_ada(self, aturan_id):
        entri = RUJUKAN[aturan_id]
        for medan in ("nama_aturan", "sumber", "butir", "kutipan", "status", "pdf_url"):
            assert medan in entri, f"{aturan_id} tidak punya medan {medan}"

    @pytest.mark.parametrize("aturan_id", sorted(RUJUKAN))
    def test_statusnya_dikenali(self, aturan_id):
        assert RUJUKAN[aturan_id]["status"] in _STATUS_SAH, aturan_id


class TestStatus:
    @pytest.mark.parametrize("aturan_id", sorted(RUJUKAN))
    def test_butir_terisi_berarti_sudah_dibaca(self, aturan_id):
        """KAIDAH YANG MENJAGA SELURUH TABEL INI.

        Status "visual" maupun "turunan" berarti ada manusia yang membaca
        butirnya dari naskah. Pembacaan itu meninggalkan jejak: nomor halaman.
        Status yang dinaikkan tanpa halaman berarti dinaikkan karena
        kutipannya "kelihatan benar" — persis yang dilarang docstring berkas
        itu sendiri.
        """
        entri = RUJUKAN[aturan_id]
        if entri["status"] not in _SUDAH_DIBACA:
            return
        assert entri["butir"] != "...", aturan_id
        assert entri["kutipan"] != "...", aturan_id
        assert entri.get("halaman_pdf"), (
            f"{aturan_id} berstatus {entri['status']} tetapi halaman_pdf kosong"
        )

    @pytest.mark.parametrize("aturan_id", sorted(RUJUKAN))
    def test_placeholder_tidak_membawa_butir(self, aturan_id):
        """Kebalikannya juga dijaga: butir yang terisi sementara statusnya
        placeholder membuat komentar menampilkan dasar yang belum diperiksa."""
        entri = RUJUKAN[aturan_id]
        if entri["status"] != "placeholder":
            return
        assert entri["butir"] == "...", aturan_id

    def test_turunan_TIDAK_dihitung_lengkap(self):
        """Butirnya benar, tetapi aturannya akibat butir itu — bukan bunyinya.

        Gate legal di panel wajib tetap menyala. Kalau suatu hari "turunan"
        ikut dihitung lengkap, penelaah akan membaca dasar turunan sebagai
        kutipan langsung.
        """
        turunan = [k for k, v in RUJUKAN.items() if v["status"] == "turunan"]
        assert turunan, "tidak ada entri turunan — tes ini jadi tidak menguji apa pun"
        for aturan_id in turunan:
            assert not rujukan_sudah_lengkap(aturan_id), aturan_id
            assert rujukan_turunan(aturan_id), aturan_id

    def test_visual_dihitung_lengkap(self):
        for aturan_id, entri in RUJUKAN.items():
            if entri["status"] == "visual":
                assert rujukan_sudah_lengkap(aturan_id), aturan_id
                assert not rujukan_turunan(aturan_id), aturan_id


class TestFase1TetapUtuh:
    """Kedua belas aturan Fase 1 sudah diverifikasi 18 Sep 2026 dan TIDAK
    boleh turun statusnya oleh pekerjaan Fase 2/3."""

    @pytest.mark.parametrize("nomor", range(1, 13))
    def test_fase1_tetap_visual(self, nomor):
        entri = RUJUKAN[f"F1-{nomor:03d}"]
        assert entri["status"] == "visual"
        assert entri["butir"] != "..."


class TestAturanFase23:
    def test_yang_belum_ketemu_dasarnya_mengaku_apa_adanya(self):
        """F2-102 dan F2-103 sudah DICARI di Lampiran II dan tidak ketemu.

        Keduanya sengaja dibiarkan placeholder. Kalau suatu hari butirnya
        diisi, catatannya harus ikut berubah — dan tes ini memaksa itu
        ketahuan, bukan lewat diam-diam.
        """
        for aturan_id in ("F2-102", "F2-103"):
            entri = RUJUKAN[aturan_id]
            assert entri["status"] == "placeholder", aturan_id
            assert "TIDAK KETEMU" in str(entri["catatan"]), aturan_id

    def test_f3_002_mencatat_koreksinya(self):
        """Butir 28 dan 29 melarang mencantumkan peraturan yang BELUM
        BERLAKU, bukan yang SUDAH DICABUT — padahal yang diperiksa aturan ini
        justru yang sudah dicabut. Koreksi itu harus tetap terbaca."""
        catatan = str(RUJUKAN["F3-002"]["catatan"])
        assert "belum berlaku" in catatan.lower()
        assert "dicabut" in catatan.lower()
