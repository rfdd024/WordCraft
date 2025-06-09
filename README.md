<h1 align="center">🧩 WordCraft</h1>

**WordCraft** adalah project Python sederhana yang membantu dalam mempelajari vocabulary Bahasa Inggris. Aplikasi ini menggunakan database **JSON** untuk menyimpan **flashcard** dari vocabulary yang ditambahkan.

---

![Demo Aplikasi WordCraft](./images1.png)
![Demo Aplikasi WordCraft](./images2.png)
![Demo Aplikasi WordCraft](./images3.png)
![Demo Aplikasi WordCraft](./images4.png)

---

## Prerequisites

- Python ≥ 3.8
- Streamlit
- Requests
- JSON API (bebas, bisa open/public)

---

## Setup Guide

- **Clone project.**  
  ```bash
  git clone https://github.com/rfdd024/WordCraft.git
  cd WordCraft
  ```

- **Install library.**  
  Install semua library yang dibutuhkan:
  ```bash
  pip install -r requirements.txt
  ```
  Atau jika `requirements.txt` belum tersedia:
  ```bash
  pip install streamlit requests
  ```

- **Atur API.**  
  Pada bagian kode yang menggunakan API, ubah:
  ```python
  url = f"https://exampleapi.com/lookup?key=YOUR-API-KEY&word={word}"
  ```
  Gantilah `YOUR-API-KEY` dengan API milik Anda. Untuk pengujian, bisa gunakan API gratis seperti:
  - https://api.dictionaryapi.dev/

- **Jalankan Aplikasi.**  
  Jalankan program dengan perintah:
  ```bash
  streamlit run app.py
  ```
