"""Penyimpanan hasil Fase 2/3.

    sesi.py       sambungan ke Postgres (Neon), dan izin untuk tidak ada
    tabel.py      dua tabel: pekerjaan dan peta
    simpanan.py   satu-satunya pintu tulis/baca yang dipakai kode lain

Kode di luar folder ini memanggil `simpanan`, tidak pernah `sesi` atau
`tabel` langsung — supaya Fase 2 tetap berjalan ketika basis datanya tidak
ada, tanpa satu pun pemanggil perlu tahu.
"""
