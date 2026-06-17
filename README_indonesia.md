# NYC Pulse Taxi Dataset Engine

Pipeline ETL berbasis Python untuk memproses data perjalanan taksi NYC Taxi & Limousine Commission (TLC), dikemas menggunakan Docker agar eksekusinya mudah direproduksi.

## Gambaran Umum

Proyek ini melakukan ekstraksi, transformasi, validasi, dan pemuatan data perjalanan taksi NYC melalui arsitektur data berlapis (raw → transformed → mart), menghasilkan dataset yang siap dianalisis untuk kebutuhan EDA, pelaporan, atau machine learning.

## Struktur Proyek
```
NYC-PULSE-TAXI-DATASET-ENGINE/

├── data/
│   ├── raw/               # Data hasil ekstraksi mentah
│   ├── transformed/       # Data yang sudah dibersihkan dan ditransformasi
│   ├── mart/              # Data final siap analisis
│   └── mart_cleaned/       # Lapisan mart tambahan yang sudah dibersihkan
├── logs/                  # Log eksekusi pipeline
├── scripts/               # Skrip bantuan/otomatisasi
├── src/
│   ├── extract_load.py    # Ekstraksi dan pemuatan data
│   ├── transform.py       # Logika transformasi data
│   ├── validate.py        # Pengecekan validasi data
│   └── logger.py          # Konfigurasi logging
├── EDA.ipynb              # Notebook eksplorasi data analysis
├── main.py                # Titik masuk pipeline
├── dockerfile
├── docker-compose.yaml
└── requirements.txt

## Tech Stack

- Python
- Pandas
- Docker & Docker Compose
- Jupyter Notebook

## Cara Menjalankan

### Menjalankan dengan Docker  (recommended)

```bash
git clone https://github.com/alfianfebiyanto/NYC-Pulse-Taxi-DataSet-Engine.git
cd NYC-Pulse-Taxi-DataSet-Engine
docker-compose up --build
```

### Menjalankan secara lokal

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Alur Pipeline

1. **Extract** – `extract_load.py` mengambil data perjalanan mentah ke `data/raw/`
2. **Transform** – `transform.py` membersihkan dan menormalisasi data ke `data/transformed/`
3. **Validate** – `validate.py` memeriksa kualitas dan konsistensi data
4. **Load** – hasil yang sudah divalidasi ditulis ke `data/mart/` dan `data/mart_cleaned/`
5. **Logging** – seluruh tahapan dicatat melalui `logger.py` ke dalam `logs/`

## Sumber Data

NYC TLC Trip Record Data, tersedia di: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

## License
Open source, dibuat untuk keperluan edukasi/capstone.
