"""Telaah — Fase 2 dan 3 dalam lima tahap. Urutan folder = urutan jalan.

  alur                   ORKESTRASI seluruh tahap — dibaca duluan

  tahap1_parser/         PARSER — kode, gratis
    struktur             naskah datar  → pohon satuan
    definisi             pohon         → daftar istilah Pasal 1
    rujukan              "sebagaimana dimaksud …" → satuan yang dituju
    lampiran             lampiran      → bingkai + jenis fisik tiap blok

  tahap2_persiapan/      PERSIAPAN — kode, gratis
    bahan                seluruh paragraf → bahan untuk model + ukur token
    mekanis_konsistensi  F2-001/003/004/007 — langsung ke tahap 5
    dasar_hukum          F3-002 — status dasar hukum di korpus, tanpa AI

  tahap3_cari_dugaan     CARI DUGAAN — model: naskah utuh → dugaan

  tahap4_memastikan/     MEMASTIKAN — model
    memastikan           dugaan → calon / gugur, dengan naskah utuh
    alat                 cari teks, buka tabel, jumlah kolom
    korpus_cari          F3-001 — pembanding dari OpenSearch
    korpus_pastikan      F3-001 — uji ulang dengan pembanding di tangan
    korpus_rumusan       F3-003 — usulan rumusan dari peraturan berlaku

  tahap5_verifikasi      VERIFIKASI — kode, gratis: calon → temuan / gugur

  ekspor/                alat pengembang — apa yang dibaca dan diputuskan tiap tahap

SATU-SATUNYA tempat Temuan lahir adalah tahap5. Tidak ada jalan pintas dari
mana pun — termasuk dari korpus OpenSearch, yang tetap kembali ke tahap5.

Pemeriksaan korpus (F3-001, F3-002, F3-003) MATI SECARA BAWAAN di panel
Pengaturan: cakupan isi index OpenSearch belum diverifikasi langsung (brief
8.12), jadi "tidak ada pembanding" belum bisa dibedakan dari "korpusnya
memang tidak memuatnya".
"""
