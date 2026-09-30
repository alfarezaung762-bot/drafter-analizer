"""Parser lampiran — tahap 1, bug 7. Bingkai tiap lampiran dan jenis fisik bloknya.

Kode MENGUMPULKAN, tidak memutuskan: yang diuji di sini hanya pemilahan —
menilai bingkainya urusan model (F2-106).
"""

from app.models.temuan import KerangkaTabel, ParagrafInput
from app.telaah.tahap1_parser.lampiran import baca_lampiran
from app.telaah.tahap1_parser.struktur import bangun_pohon
from tests.naskah_uji import data_barang, naskah, nomori, teks


def _lampiran(paragraf, kerangka=None):
    return baca_lampiran(paragraf, bangun_pohon(paragraf), kerangka)


def test_dua_lampiran_berangka_romawi_terpisah():
    lampiran = _lampiran(naskah())
    assert [lam.nama for lam in lampiran] == ["Lampiran I", "Lampiran II"]


def test_lampiran_surat_di_dalam_contoh_format_BUKAN_lampiran_baru():
    """PMK 119/2025 memuat "Lampiran Surat" di tengah contoh format surat."""
    lampiran = _lampiran(naskah())
    assert len(lampiran) == 2
    assert any("Lampiran Surat" in b for b in lampiran[1].kepala)


def test_kepala_dan_penutup_dikumpulkan_apa_adanya():
    lam = _lampiran(naskah())[0]
    assert lam.kepala[:3] == [
        "LAMPIRAN I",
        "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
        "NOMOR 12 TAHUN 2026",
    ]
    assert lam.penutup[-3:] == ["MENTERI KEUANGAN REPUBLIK INDONESIA,", "ttd.", "NAMA MENTERI"]


def test_blok_menurut_jenis_fisiknya():
    lam = _lampiran(naskah())[0]
    jenis = [b.jenis for b in lam.blok]
    assert jenis == ["teks", "tabel", "teks"]
    tabel = lam.blok[1]
    assert (tabel.tabel, tabel.baris, tabel.kolom) == (0, 7, 3)


def test_dua_tabel_berdempetan_tetap_dua_blok():
    lam = _lampiran(naskah(tabel_lampiran=[data_barang(0), data_barang(1)]))[0]
    assert [b.tabel for b in lam.blok if b.jenis == "tabel"] == [0, 1]


def test_gambar_tanpa_teks_jadi_blok_gambar():
    paragraf = naskah()
    i = next(p.index for p in paragraf if p.teks == "DAFTAR BARANG")
    paragraf.insert(i + 1, ParagrafInput(index=0, teks="", gambar=1))
    lam = _lampiran(nomori(paragraf))[0]
    assert "gambar" in [b.jenis for b in lam.blok]


def test_kerangka_dari_panel_disisipkan_di_tempatnya():
    paragraf = naskah(tabel_lampiran=[])
    sesudah = next(p.index for p in paragraf if p.teks == "DAFTAR BARANG")
    k = KerangkaTabel(tabel=7, sesudah_paragraf=sesudah, jumlah_baris=52000, jumlah_kolom=6)
    lam = _lampiran(paragraf, [k])[0]
    kerangka = [b for b in lam.blok if b.jenis == "kerangka"]
    assert len(kerangka) == 1 and kerangka[0].baris == 52000


def test_naskah_tanpa_lampiran():
    assert _lampiran(naskah(lampiran=False)) == []


def test_lampiran_tunggal_tanpa_nomor():
    isi = [p.teks for p in naskah(lampiran=False)] + [
        "LAMPIRAN",
        "PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA",
        "Isi lampiran.",
    ]
    paragraf = nomori(teks(isi))
    lampiran = _lampiran(paragraf)
    assert len(lampiran) == 1 and lampiran[0].nomor == ""
