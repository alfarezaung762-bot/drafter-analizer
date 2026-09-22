"""Drafter Analiser — backend.

  FASE 1   rules/format_baku.py     format baku, tanpa AI          SELESAI
  FASE 2   fase2/alur.py            konsistensi + kejelasan        dibangun
  FASE 3   fase3/tahap6_*           pertentangan peraturan lain    dibangun,
                                                                   mati bawaan

  bersama/   pintu ke layanan luar — llm.py (Azure), opensearch.py (baca saja)
  models/    bentuk data saja, tanpa aksi — temuan, satuan, pekerjaan
  api/       endpoint, handler tipis. analisis.py Fase 1,
             analisis_lanjut.py Fase 2/3 (pekerjaan latar belakang)
  db/        Postgres untuk pekerjaan dan peta. BOLEH TIDAK ADA — tanpa
             DATABASE_URL simpanan pindah ke memori dan Fase 2 tetap jalan

SATU KAIDAH YANG BERLAKU DI SELURUH BACKEND: apa pun yang dihasilkan model
tidak pernah menyentuh naskah tanpa lewat fase2/tahap5_verifikasi.py. Di
sanalah kutipannya dibuktikan benar-benar ada di naskah, dan yang tidak
terbukti tidak ditandai sama sekali — bukan diperlebar ke satu paragraf.

Rancangannya di docs/fase-2dan-3drafter.md; Fase 1 di docs/fase1 drafter.md.
"""
