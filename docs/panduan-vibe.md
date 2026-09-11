# Panduan Vibe

Aturan kerja di repo ini:

- Logika bisnis ditulis sebagai fungsi murni, bebas framework. Tidak ada objek
  Request/Response di dalamnya.
- Route handler setipis mungkin: parse input → panggil fungsi → kembalikan JSON.
- Komponen UI ditulis sebagai React polos. Hindari server component dan server
  action **di dalam komponen** — proyek ini akan dimigrasikan ke React + Vite.
- Semua pemanggilan ke layanan luar (OpenSearch, Azure OpenAI) dikumpulkan di
  satu lapisan, tidak tersebar.
- Kredensial hanya hidup di backend, tidak pernah sampai ke browser.
- Jangan pakai LLM untuk hal yang bisa diselesaikan dengan regex atau logika
  biasa. Lebih murah, lebih cepat, dan hasilnya pasti.
- Sebelum menambah dependency baru, periksa dulu apakah kebutuhannya bisa
  dipenuhi yang sudah ada.
