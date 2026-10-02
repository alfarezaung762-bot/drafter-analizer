"""Parser cadangan PMK biasa — peta letak tanpa AI.

Dipakai bila label AI gagal bukti (rancangan Fase 4 bagian 5.2), dan sebagai
kunci jawaban label selama peralihan. Isinya parser alur lama,
`tahap1_parser/struktur.py`, dipakai apa adanya — dipindah ke sini saat alur
lama dihapus (langkah 9).
"""

from app.telaah.tahap1_parser.struktur import bangun_pohon, pasangan_label  # noqa: F401
from app.telaah.tahap2_persiapan.bahan import id_awal_satuan, peta_satuan  # noqa: F401
