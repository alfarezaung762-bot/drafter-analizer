# Kunci naskah uji Fase 1

> **Dibangkitkan otomatis oleh `tools/buat_contoh_uji.py`. Jangan disunting tangan** — jalankan ulang skripnya, dan berkas ini ikut benar dengan sendirinya. Naskahnya karangan yang sengaja dirusak, bukan rancangan sungguhan.

Dua naskah, dua bentuk yang berbeda:

| Berkas | Bentuk | Gunanya |
|---|---|---|
| `uji-pmk-lengkap.docx` | paragraf biasa | menguji sebagian besar aturan sekaligus |
| `uji-kmk-lengkap.docx` | pembukaan di dalam **tabel** | bentuk naskah sungguhan, dan yang paling sering membuat aturan salah tandai |

## Cara memakainya

```bash
# tanpa membuka Word
cd backend && python tools/cek_docx.py tools/contoh/uji-pmk-lengkap.docx --jenis PMK
cd backend && python tools/cek_docx.py tools/contoh/uji-kmk-lengkap.docx --jenis KMK
```

Lalu buka berkasnya di Word lewat add-in, pilih jenis dokumennya, dan cocokkan dengan tabel di bawah.

**Dua hal yang layak dicoba juga:**

1. Buka `uji-kmk-lengkap.docx` lalu pilih **PMK** (jenis yang salah). Temuan F1-004 akan berubah bunyinya — itu memperlihatkan kenapa pilihan jenis dokumen dibuat wajib dan tanpa nilai awal.
2. Warnai satu kata dengan warna biru sebelum menganalisis, lalu tekan **Bersihkan Daftar**. Warna itu harus tetap biru — alat hanya boleh mencabut warnanya sendiri.

## Yang BELUM bisa diuji dari kedua berkas ini

**F1-003 (kelengkapan Menimbang / Mengingat / Menetapkan).** Menguji aturan ini menuntut salah satu bagian itu DIHAPUS — dan begitu dihapus, hampir seluruh aturan lain ikut kehilangan jangkarnya lalu memilih diam. Cara mengujinya: buka salah satu berkas di Word, hapus baris `Mengingat`, lalu jalankan analisis. Hasil yang benar: muncul peringatan dokumen berlatar merah muda di atas daftar, **bukan** kartu temuan — karena ketiadaan sebuah bagian tidak punya lokasi untuk ditunjuk.

---

### Naskah PMK — yang sengaja dirusak

| Aturan | Kesalahannya | Cuplikan |
|---|---|---|
| F1-006 | judul peraturan diakhiri tanda baca titik (butir 8) | `NOMOR 5 TAHUN 2023 TENTANG TATA CARA PENYUSUNAN STAN…` |
| F1-007 | kata "Menimbang" ditulis kapital seluruhnya (butir 16) | `MENIMBANG :` |
| F1-008 | butir Menimbang tidak diawali kata "bahwa" (butir 21) | `a. untuk melaksanakan ketentuan Pasal 12 ayat (3) Pe…` |
| F1-008 | butir Menimbang diakhiri titik, bukan titik koma (butir 21) | `b. bahwa standar biaya masukan perlu disesuaikan den…` |
| F1-004 | butir terakhir tidak memakai frasa "sebagaimana dimaksud dalam huruf" (butir 22) | `c. bahwa berdasarkan hal tersebut di atas, perlu men…` |
| F1-009 | kata "Mengingat" ditulis kapital seluruhnya (butir 23) | `MENGINGAT :` |
| F1-005 | "Undang-undang" — kedua huruf u wajib kapital (butir 33) | `1. Undang-undang Nomor 17 Tahun 2003 tentang Keuanga…` |
| F1-005 | kata "Tentang" pada dasar hukum wajib huruf kecil (butir 32) | `2. Peraturan Pemerintah Nomor 45 Tahun 2013 Tentang …` |
| F1-010 | dasar hukum tidak diakhiri titik koma (butir 31) | `3. Peraturan Presiden Nomor 57 Tahun 2020 tentang Ke…` |
| F1-011 | kata "Menetapkan" ditulis kapital seluruhnya (butir 38) | `MENETAPKAN :` |
| F1-012 | tiga hal sekaligus di satu baris — lihat kunci di bawah | `PERATURAN MENTERI KEUANGAN REPUBLIK INDONESIA TENTAN…` |

### Naskah PMK — jebakan yang TIDAK boleh ditandai

| Kenapa dipasang | Cuplikan |
|---|---|
| KONTROL — bentuk berspasi huruf. Kalau penanda ini tidak dikenali, F1-002, F1-011, dan F1-012 ikut mati diam-diam | `M E M U T U S K A N :` |
| KONTROL — "undang-undang" generik di batang tubuh. Bukan dasar hukum, jadi butir 33 tidak berlaku dan tidak boleh ditandai | `Ketentuan mengenai standar biaya masukan sebagaimana…` |
| KONTROL — paragraf batang tubuh yang diawali kata "Menetapkan". Di luar jendela klausul Menetapkan, jadi bukan label bagian | `Menetapkan besaran standar biaya masukan sebagaimana…` |

### Naskah PMK — hasil NYATA hari ini

Dijalankan terhadap `uji-pmk-lengkap.docx` sebagai **PMK**, seluruh aturan menyala. Keluar **13 temuan**.

| # | Aturan | Jenis | Par | Yang ditandai |
|---|---|---|---|---|
| T1 | F1-006 | penggantian | 4 | `MASUKAN.` |
| T2 | F1-007 | penggantian | 8 | `MENIMBANG` |
| T3 | F1-008 | catatan | 9 | `untuk melaksanakan ketentuan Pasal 12 ay…` |
| T4 | F1-008 | catatan | 10 | `.` |
| T5 | F1-004 | catatan | 11 | `bahwa berdasarkan hal tersebut di atas, …` |
| T6 | F1-009 | penggantian | 13 | `MENGINGAT` |
| T7 | F1-005 | penggantian | 14 | `Undang-undang` |
| T8 | F1-005 | penggantian | 15 | `Tentang` |
| T9 | F1-010 | catatan | 16 | `n` |
| T10 | F1-011 | penggantian | 20 | `MENETAPKAN` |
| T11 | F1-012 | penggantian | 21 | `MENTERI KEUANGAN REPUBLIK INDONESIA` |
| T12 | F1-002 | catatan | 21 | `PENETAPAN` |
| T13 | F1-012 | penggantian | 21 | `MASUKAN` |

---

### Naskah KMK — yang sengaja dirusak

| Aturan | Kesalahannya | Cuplikan |
|---|---|---|
| F1-004 | naskah KMK tetapi menyebut "Peraturan Menteri Keuangan"; butir 22 menuntut "Keputusan Menteri Keuangan". INILAH yang membuat pilihan PMK/KMK di panel wajib | `b. bahwa berdasarkan pertimbangan sebagaimana dimaks…` |

### Naskah KMK — jebakan yang TIDAK boleh ditandai

| Kenapa dipasang | Cuplikan |
|---|---|
| KONTROL — label berdiri sendiri di selnya, titik duanya ada di sel sebelah. Tidak bisa dibuktikan hilang, jadi F1-007 harus DIAM | `Menimbang` |
| KONTROL — sama dengan Menimbang, F1-009 harus DIAM | `Mengingat` |
| KONTROL — penyebutan "Peraturan Menteri Keuangan" di dasar hukum sebuah KMK. Dulu jenis dokumen ditebak dari penyebutan pertama, dan naskah seperti ini dikira PMK | `2. Peraturan Menteri Keuangan Nomor 202/PMK.010/2017…` |
| KONTROL — isi diktum KMK yang diawali kata "Menetapkan". Inilah salah tandai yang ditemukan 18 Sep 2026 (6.10 Kasus 6): F1-011 menuduh batang tubuh ini kurang titik dua | `Menetapkan pejabat pengelola keuangan di lingkungan …` |

### Naskah KMK — hasil NYATA hari ini

Dijalankan terhadap `uji-kmk-lengkap.docx` sebagai **KMK**, seluruh aturan menyala. Keluar **2 temuan**.

| # | Aturan | Jenis | Par | Yang ditandai |
|---|---|---|---|---|
| T1 | F1-004 | catatan | 9 | `bahwa berdasarkan pertimbangan sebagaima…` |
| T2 | F1-002 | catatan | 16 | _(tanpa lokasi — jadi peringatan dokumen)_ |

---

## Cara membaca selisihnya

Bandingkan tabel **yang sengaja dirusak** dengan tabel **hasil nyata**. Tiga kemungkinan, dan ketiganya berguna:

- **Ada di keduanya** — aturannya bekerja.
- **Ada di rencana, tidak ada di hasil** — aturannya diam. Belum tentu cacat: bisa jadi ia memang memilih diam karena tidak bisa membuktikan kesalahannya. Periksa alasannya di panel Pengaturan, bagian "Yang TIDAK diperiksa".
- **Ada di hasil, tidak ada di rencana** — ini yang paling penting. Berarti alat menandai sesuatu yang tidak sengaja dirusak. Periksa naskahnya: kalau memang tidak salah, itu **salah tandai** dan wajib dilaporkan.

Satu baris bisa memuat lebih dari satu kesalahan, jadi jumlah temuan boleh lebih banyak daripada jumlah baris di tabel rencana.
