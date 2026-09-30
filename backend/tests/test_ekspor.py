"""Ekspor Tahap 1–5 — alat pengembang. TANPA jaringan.

Ditetapkan penelaah 27–28 Sep 2026: ekspor berisi "real apa yang dibaca AI",
tanpa tambahan. Tesnya karena itu SAMA PERSIS dengan yang diterima klien, bukan
sekadar "memuat" — kecuali kepala perkiraan token Tahap 2, yang memang diminta.
"""

import json

from app.bersama.llm import KlienPalsu
from app.models.temuan import ParagrafInput
from app.telaah.alur import jalankan_lanjut
from app.telaah.ekspor.tahap1 import susun_ekspor_tahap1
from app.telaah.ekspor.tahap2 import susun_ekspor_tahap2
from app.telaah.ekspor.tahap3 import susun_ekspor_tahap3, tulis_percakapan
from app.telaah.ekspor.tahap4 import susun_ekspor_tahap4
from app.telaah.ekspor.tahap5 import susun_ekspor_tahap5
from app.telaah.tahap1_parser.struktur import bangun_pohon
from app.telaah.tahap2_persiapan.bahan import susun_bahan
from tests.naskah_uji import BATANG, naskah


def _js(obj) -> str:
    return json.dumps(obj, ensure_ascii=False)


_KMK = [
    ParagrafInput(index=i, teks=t)
    for i, t in enumerate(
        [
            "KEPUTUSAN MENTERI KEUANGAN REPUBLIK INDONESIA",
            "TENTANG",
            "PEMBENTUKAN TIM",
            "MENTERI KEUANGAN REPUBLIK INDONESIA,",
            "MEMUTUSKAN:",
            "Menetapkan : KEPUTUSAN MENTERI KEUANGAN TENTANG PEMBENTUKAN TIM.",
            "KESATU : Membentuk Tim.",
        ]
    )
]


def _analisis(paragraf=None):
    """Satu analisis penuh dengan KlienPalsu: satu dugaan, satu pemanggilan alat."""
    paragraf = paragraf or naskah()
    fokus = ["pasal-1", "pasal-2", "pasal-3", "pasal-4"]
    hasil_pasal = [{"pasal": p, "dugaan": []} for p in fokus]
    hasil_pasal[1]["dugaan"] = [{"satuan_id": "pasal-2", "jenis": "pemikul", "alasan": "pemikul tidak tegas"}]
    jawaban = [
        _js({"hasil": hasil_pasal}),
        _js({"dugaan": [], "keberatan": []}),
        _js({"dugaan": []}),
        {"alat": "cari_teks", "argumen": {"teks": "Pengguna Barang"}},
        _js({"terbukti": False, "alasan": "subjeknya jelas: Pengguna Barang"}),
    ]
    klien = KlienPalsu(jawaban)
    return jalankan_lanjut(paragraf, klien=klien), klien


class TestTahap1:
    def test_pohon_definisi_dan_lampiran(self):
        teks = susun_ekspor_tahap1(naskah())
        assert "===== TAHAP 1 · POHON SATUAN" in teks
        assert "[pasal-2] pasal · paragraf" in teks
        assert "[pasal-1-angka-1] Pengelola Barang" in teks
        assert "Lampiran I — paragraf" in teks and "Lampiran II — paragraf" in teks
        assert "  tabel 0 — 7 baris × 3 kolom" in teks

    def test_paragraf_yang_tidak_masuk_satuan_disebut(self):
        batang = BATANG[:6] + ["a) rincian yang tidak dikenali parser;"] + BATANG[6:]
        teks = susun_ekspor_tahap1(naskah(batang=batang))
        bagian = teks.split("PARAGRAF BATANG TUBUH DI LUAR TEKS SATUAN")[1]
        assert "a) rincian yang tidak dikenali parser;" in bagian.split("=====")[1]

    def test_parser_menyerah_disebut(self):
        assert "PARSER MENYERAH" in susun_ekspor_tahap1(_KMK)


class TestTahap2:
    def test_bahan_SAMA_PERSIS_dengan_yang_di_depan_pesan_tahap3(self):
        paragraf = naskah()
        _, klien = _analisis(paragraf)
        teks = susun_ekspor_tahap2(paragraf)
        bahan = teks.split("===== TAHAP 2 · BAHAN — persis, ikut di depan tiap panggilan tahap 3 dan 4 =====\n")[1]
        bahan = bahan.split("\n\n===== TAHAP 2 · FAKTA LAMPIRAN")[0]
        assert bahan == susun_bahan(paragraf, bangun_pohon(paragraf)).teks
        for _, pesan in klien.diminta:
            assert bahan in pesan

    def test_fakta_lampiran_SAMA_PERSIS_dengan_yang_di_panggilan_lampiran(self):
        paragraf = naskah()
        _, klien = _analisis(paragraf)
        fakta = susun_ekspor_tahap2(paragraf).split("(F2-106) =====\n")[1].rstrip("\n")
        assert fakta in klien.diminta[2][1]

    def test_perkiraan_token_di_atas(self):
        teks = susun_ekspor_tahap2(naskah())
        kepala = teks.split("===== TAHAP 2 · BAHAN")[0]
        assert kepala.startswith("===== TAHAP 2 · PERKIRAAN TOKEN =====")
        for baris in ("Cara hitung", "Naskah", "Lampiran", "Bahan utuh", "Tahap 3 — 3 panggilan", "Tahap 4"):
            assert baris in kepala

    def test_aturan_yang_dimatikan_mengubah_rencana(self):
        teks = susun_ekspor_tahap2(naskah(), aturan_aktif=["F2-102"])
        assert "Tahap 3 — 1 panggilan" in teks

    def test_naskah_yang_ditolak_cukup_satu_kalimat(self):
        teks = susun_ekspor_tahap2(_KMK)
        assert teks.startswith("Tidak ada yang dikirim ke AI")
        assert teks.count("\n") == 1


class TestTahap3:
    def test_isinya_persis_pesan_yang_dikirim(self):
        hasil, klien = _analisis()
        dikirim = klien.diminta[:3]
        judul = [j for j, _ in hasil.pesan_tahap3]
        harapan: list[str] = []
        for j, (peran, pesan) in zip(judul, dikirim):
            if harapan:
                harapan.append("")
            harapan += tulis_percakapan(j, [("system", peran), ("user", pesan)])
        assert susun_ekspor_tahap3(hasil.pesan_tahap3) == "\n".join(harapan) + "\n"

    def test_tidak_tercatat_dan_tidak_mengirim_dibedakan(self):
        assert susun_ekspor_tahap3(None).startswith("Pesan tahap 3 tidak tercatat")
        assert susun_ekspor_tahap3([]).startswith("Tahap 3 tidak mengirim apa pun")


class TestTahap4:
    def test_hasil_alat_ikut_persis(self):
        hasil, klien = _analisis()
        teks = susun_ekspor_tahap4(hasil.pesan_tahap4)
        judul = "TAHAP 4 · DUGAAN 1/1 · F2-102 [pasal-2]"
        assert teks.startswith(f"===== {judul} · system =====\n")
        assert f"===== {judul} · user =====\n{klien.diminta[3][1]}\n" in teks
        assert f'===== {judul} · AI memanggil alat =====\ncari_teks({{"teks": "Pengguna Barang"}})' in teks
        assert f"===== {judul} · hasil alat (dibaca AI) =====\nKETEMU" in teks

    def test_tanpa_dugaan(self):
        assert susun_ekspor_tahap4([]).startswith("Tahap 4 tidak mengirim apa pun")
        assert susun_ekspor_tahap4(None).count("\n") == 1


class TestTahap5:
    def test_nasib_tiap_dugaan_tertulis(self):
        hasil, _ = _analisis()
        teks = susun_ekspor_tahap5(hasil)
        assert "===== TAHAP 3 · DUGAAN (1) =====" in teks
        assert "F2-102 [pasal-2] — pemikul tidak tegas" in teks
        assert "F2-102 [pasal-2]: tidak terbukti — subjeknya jelas: Pengguna Barang" in teks
        lolos = teks.split("===== TAHAP 5 · LOLOS JADI TEMUAN")[1].split("===== TAHAP 5 · GUGUR")[0]
        assert "F2-102" not in lolos
        # Temuan kode ikut tercatat — naskah uji memang tidak memakai
        # "Pengelola Barang" di luar Pasal 1.
        assert "F2-003 (kode) [pasal-1-angka-1]" in lolos

    def test_fase2_tidak_jalan(self):
        hasil = jalankan_lanjut(_KMK, klien=KlienPalsu([]))
        assert susun_ekspor_tahap5(hasil).startswith("Fase 2 tidak dijalankan")
