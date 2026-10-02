"""Tahap 1 · bahan — menyiapkan bacaan agen (Fase 4). Satu panggilan AI, sisanya kode.

  langkah1_label_ai            AI memberi label tiap paragraf pembuka satuan,
                               menurut skill label jenis naskahnya
  langkah2_bukti_label         kode membuktikan tiap label — penanda, urutan,
                               induk, tidak dobel — lalu menyusun peta letak
  langkah3_istilah_pasal1      daftar istilah Pasal 1 — dipakai gerbang
  langkah4_teks_dirujuk        teks yang dirujuk "sebagaimana dimaksud …"
  langkah5_lampiran            kepala, penutup, dan tabel tiap lampiran
  langkah6_naskah_berlabel     seluruh paragraf ¶ + [label]; tabel per baris
  langkah7_naskah_berformat    tiap paragraf ¶ beserta formatnya — putaran format
  langkah8_bahan_korpus        peraturan yang disebut naskah, dari korpus — hanya
                               bila ada analisis ber-Butuh: bahan korpus
  parser_cadangan_pmk_biasa    peta letak tanpa AI, bila label AI gagal bukti

Selama peralihan (rancangan Fase 4 bagian 4 langkah 8) beberapa langkah
memakai ulang kode alur lama di `tahap1_parser/` dan `tahap2_persiapan/`
tanpa menyalinnya — alur lama tetap hidup di balik saklar `FASE2_ALUR`.
"""
