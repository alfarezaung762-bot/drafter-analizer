"""Penjaga bentuk kalimat untuk usulan hijau. TANPA jaringan.

Ditetapkan penelaah 25 Sep 2026, dengan kaidah yang ia sebutkan sendiri:

    "selama memang kata yang benarnya bisa disisipkan di kalimat yang
     berpotensi salah (dicoret merah) masukkan saja, tapi kalau mengharuskan
     di tempat yang berbeda hanya bertanda kuning dan ada komentar"

Masalahnya ada usulan yang KELIHATAN muat padahal tidak: ia menggantikan satu
bagian kalimat, tetapi hasilnya kalimatnya pincang.

Keempat kasus di bawah adalah skema yang dipakai memutuskan, dinamai sama
persis supaya `pytest -v` terbaca seperti skemanya. Jalankan:

    .venv/Scripts/python.exe -m pytest tests/test_usulan_muat_di_kalimat.py -v
"""

from app.fase2.tahap5_verifikasi import periksa_usulan, usulan_harfiah


class TestEmpatKasusYangDipakaiMemutuskan:
    def test_kasus_1_klausa_diganti_frasa_DITAHAN(self):
        """Yang terjadi di contoh-rancangan-uji.docx, dan yang memicu semua ini.

        Kata kerja "dilakukan" ikut tercoret tanpa pengganti. Kalau disisipkan,
        ayatnya berbunyi "... perbedaan pendapat ..., rapat pembahasan yang
        diselenggarakan oleh unit kerja yang melakukan penelaahan." — tanpa
        predikat.
        """
        sebab = periksa_usulan(
            "rapat pembahasan yang diselenggarakan oleh unit kerja yang melakukan penelaahan",
            "penyelesaiannya dilakukan melalui rapat pembahasan",
            "(3) Dalam hal terdapat perbedaan pendapat atas catatan telaah, ",
        )
        assert sebab, "Kasus 1 wajib ditahan"
        assert "penyelesaiannya" in sebab

    def test_kasus_2_menambah_subjek_LOLOS(self):
        """Frasa pendek, pembukanya utuh, kalimatnya jadi benar."""
        assert usulan_harfiah(
            "wajib mengajukan permohonan kepada Menteri",
            "wajib mengajukan permohonan",
            "(1) Pengguna Barang ",
        )

    def test_kasus_3_dijadikan_kalimat_aktif_DITAHAN(self):
        """HARGA YANG SENGAJA DIBAYAR.

        Usulannya benar — mengubah pasif jadi aktif memang lebih jelas —
        tetapi pembukanya hilang, dan penjaga tidak bisa membedakannya dari
        Kasus 1. Ditahan, dan usulannya tetap terbaca penelaah di komentar
        sebagai contoh rumusan.
        """
        assert periksa_usulan(
            "Kantor Pelayanan Pajak melakukan penelitian setempat",
            "dilakukan penelitian setempat oleh Kantor Pelayanan Pajak",
            "(2) Untuk memastikan keadaan Wajib Pajak, ",
        )

    def test_kasus_4_melengkapi_bilangan_dan_keterangan_LOLOS(self):
        """Inilah yang hilang kalau penjaganya dibuat menurut jumlah kata.

        Tujuh kata dicoret, tetapi pembukanya utuh dan kalimatnya tetap benar —
        justru jenis perbaikan yang paling bisa diandalkan dari korpus.
        """
        assert usulan_harfiah(
            "diselesaikan paling lambat 30 (tiga puluh) Hari sejak permohonan diterima",
            "diselesaikan paling lambat 30 hari sejak permohonan",
            "(2) Permohonan ",
        )


class TestBatasPenjagaBentukKalimat:
    def test_frasa_pendek_boleh_diganti_seluruhnya(self):
        """Di bawah empat kata, membuang kata pertama justru lazim dan benar.

        Kalau penjaga ini berlaku untuk frasa pendek juga, perbaikan bilangan
        seperti ini ikut ditahan tanpa sebab.
        """
        assert usulan_harfiah("13 (tiga belas)", "30 (tiga belas)", "paling lambat ")

    def test_pembuka_dihitung_tanpa_peduli_huruf_besar_kecil(self):
        assert usulan_harfiah(
            "Diselesaikan paling lambat 30 (tiga puluh) Hari sejak permohonan",
            "diselesaikan paling lambat 30 hari sejak permohonan",
            "(2) Permohonan ",
        )

    def test_pembuka_tidak_cocok_sepotong_kata_lain(self):
        """"lakukan" di dalam "melakukan" bukan kemunculan kata "dilakukan".

        Tanpa batas kata, penjaga ini akan meloloskan Kasus 1 dan 3 diam-diam.
        """
        assert periksa_usulan(
            "yang melakukan penelaahan atas berkas permohonan itu",
            "dilakukan penelaahan atas berkas permohonan",
            "(1) Terhadap permohonan tersebut ",
        )

    def test_tanda_baca_di_pembuka_tidak_menggagalkan(self):
        assert usulan_harfiah(
            "“Penelaah” wajib menyampaikan laporan setiap bulan",
            "“Penelaah” wajib menyampaikan laporan",
            "(1) Dalam hal demikian, ",
        )


class TestPenjagaLamaTetapBerlaku:
    """Penjaga baru ditambahkan, bukan menggantikan. Ketiganya tetap hidup."""

    def test_usulan_berupa_penjelasan_tetap_ditahan(self):
        assert "penjelasan" in periksa_usulan(
            "Sebaiknya subjeknya disebutkan secara tegas",
            "wajib mengajukan permohonan",
        )

    def test_usulan_yang_mengulang_teks_sebelumnya_tetap_ditahan(self):
        sebab = periksa_usulan(
            "Catatan telaah sebagaimana dimaksud pada ayat (1) disampaikan kepada Unit Pemrakarsa oleh Penelaah.",
            "disampaikan kepada Unit Pemrakarsa.",
            "(2) Catatan telaah sebagaimana dimaksud pada ayat (1) ",
        )
        assert "dua kali" in sebab

    def test_usulan_terlalu_panjang_tetap_ditahan(self):
        assert "terlalu panjang" in periksa_usulan("x" * 400, "wajib mengajukan")

    def test_usulan_sama_persis_tetap_ditahan(self):
        assert "tidak mengubah" in periksa_usulan(
            "wajib mengajukan permohonan", "wajib mengajukan permohonan"
        )
