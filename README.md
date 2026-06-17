# NYC Pulse Taxi Dataset Engine

A Python-based ETL pipeline for processing NYC Taxi & Limousine Commission (TLC) trip record data, containerized with Docker for reproducible execution.

## Overview

This project extracts, transforms, validates, and loads NYC taxi trip data through a layered data architecture (raw → transformed → mart), producing analysis-ready datasets for downstream EDA, reporting, or machine learning.

## Project Structure

```
NYC-PULSE-TAXI-DATASET-ENGINE/
├── data/
│   ├── raw/               # Raw extracted data
│   ├── transformed/       # Cleaned and transformed data
│   ├── mart/              # Final analysis-ready data
│   └── mart_cleaned/      # Additional cleaned mart layer
├── logs/                  # Pipeline execution logs
├── scripts/               # Helper/automation scripts
├── src/
│   ├── extract_load.py    # Data extraction and loading
│   ├── transform.py       # Data transformation logic
│   ├── validate.py        # Data validation checks
│   └── logger.py          # Logging configuration
├── EDA.ipynb              # Exploratory data analysis notebook
├── main.py                # Pipeline entry point
├── dockerfile
├── docker-compose.yaml
└── requirements.txt
```

## Tech Stack

- Python
- Pandas
- Docker & Docker Compose
- Jupyter Notebook

## Getting Started

### Run with Docker (recommended)

```bash
git clone https://github.com/alfianfebiyanto/NYC-Pulse-Taxi-DataSet-Engine.git
cd NYC-Pulse-Taxi-DataSet-Engine
docker-compose up --build
```

### Run locally

```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

## Pipeline Flow

1. **Extract** – `extract_load.py` pulls raw trip data into `data/raw/`
2. **Transform** – `transform.py` cleans and normalizes data into `data/transformed/`
3. **Validate** – `validate.py` checks data quality and consistency
4. **Load** – validated output is written to `data/mart/` and `data/mart_cleaned/`
5. **Logging** – all steps are logged via `logger.py` into `logs/`

## Data Source

| Nama Data | URL |
|---|---|
| Data Taxi Januari 2026 (Parquet) | `https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet` |
| Taxi Zone Lookup Table (CSV) | `https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv` |

<<<<<<<< HEAD:README_in_English.md
## License
========
## Documentation & Video

- Complete project documentation is available in the `README.md` and `README_Project_in_Indonesia` files.
- The project explanation video (maximum 10 minutes) can be accessed via the following link: `[insert Google Drive link]`

## Author
>>>>>>>> 33a15d573f36baf88c8626622a816ad3a728a4cf:README.md

**Alfian Febiyanto**
