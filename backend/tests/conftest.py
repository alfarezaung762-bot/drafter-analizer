"""Setelan yang berlaku untuk SELURUH tes.

MEMUTUS BASIS DATA DARI SELURUH SUITE, dan itu bukan kerapian.

`DATABASE_URL` yang terisi membuat `simpanan` menyambung ke Neon sungguhan.
Akibatnya nyata dan sudah pernah terjadi: suite yang tadinya 1 detik jadi 15
detik, dan `create_all` membuat tabel `da_pekerjaan` serta `da_hasil_satuan`
di basis data bersama — tes menulis ke tempat yang bukan miliknya, lalu
meninggalkan barisnya di sana.

Dulu penjagaannya ditulis ulang di tiap berkas yang membutuhkannya, dan itu
persis jenis penjagaan yang gampang terlupa: berkas tes baru yang kebetulan
memanggil `simpanan` akan menyambung ke Neon tanpa ada yang menyadarinya,
karena tidak ada yang gagal — cuma jadi lambat. Ditaruh di sini, ia berlaku
untuk berkas yang sudah ada dan untuk yang belum ditulis.

Tes yang memang hendak menguji jalur Postgres harus menyalakannya sendiri
secara eksplisit di dalam tesnya.
"""

import pytest

from app.core.config import settings
from app.db import simpanan


@pytest.fixture(autouse=True)
def tanpa_basis_data(monkeypatch):
    monkeypatch.setattr(settings, "DATABASE_URL", "")
    simpanan.bersihkan_memori()
    yield
    simpanan.bersihkan_memori()
