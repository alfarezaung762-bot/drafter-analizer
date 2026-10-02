"""Tahap 2 · agen — AI mencari, membuktikan, dan mencatat calon temuan (Fase 4).

  langkah1_pilih_analisis   membaca analisis.md, analisisformat.md, dan skills;
                            menolak formulir cacat; memilih analisis menurut
                            jenis naskah dan baris Butuh
  langkah2_bagi_putaran     per kelompok pasal · seluruh naskah · lampiran ·
                            format, menurut baris Lingkup
  langkah3_jalankan_agen    kirim → jalankan alat → ulang sampai selesai;
                            tagih pasal yang belum dilaporkan; hentikan putaran
                            macet; tunggu bila 429; simpan jejak
  langkah3_alat_agen        alat yang boleh dipanggil agen
  langkah4_penilai_kedua    setuju / tolak tiap calon temuan, request terpisah
  peran_agen_dan_penilai    teks peran untuk langkah 3 dan 4

Yang keluar CALON temuan — belum menyentuh naskah. Satu-satunya tempat temuan
lahir tetap gerbang kode, `tahap3_verifikasi.py`.
"""
