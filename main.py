import os
import sys
import time
import logging
import pandas as pd
from src.extract_load import DataExtractor, DataLoader
from src.transform import DataTransformer
from src.validate import DataValidator

# Mengimpor modul logger terpusat dari src/logger.py
from src.logger import setup_logger


# ==========================================
# +             PATH KONFIGURASI           +
# ==========================================
BASE_DIR = os.getcwd() # otomatis mendeteksi folder project yang aktif
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
TRANSFORM_PATH = os.path.join(BASE_DIR, "data", "transformed")
MART_PATH = os.path.join(BASE_DIR, "data", "mart")
CLEANED_MART_PATH = os.path.join(BASE_DIR, "data", "mart_cleaned")

# URL SUMBER DATASET
TAXI_TRIPS_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
ZONE_TAXI_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"


def main():

    # Inisialisasi Logging 
    logger = setup_logger()

    # Mulai hitung Waktu Ekeskusi Pipeline
    start_time = time.time()

    logger.info("=" * 50)
    logger.info("        STARTING ETL PIPELINE")
    logger.info("=" * 50)

    data_url = os.getenv("Data_URL",TAXI_TRIPS_URL)

    # ==========================================
    # 1. STEP: EXTRACT DATA
    # ==========================================

    logger.info("[1/4] STEP: EXTRACT & INGESTION STARTED")

    extractor = DataExtractor(raw_folder=RAW_PATH)

    # Proses Download otomatis file dari source
    zone_file = extractor.download_file(ZONE_TAXI_URL, "taxi_zone_lookup.csv")
    trip_file = extractor.download_file(data_url, "yellow_tripdata_2026-01.parquet")

    # membaca file data ke dalam Pandas Dataframe
    zone_df = extractor.read_csv(zone_file)
    zone_df.columns = ["location_id", "borough", "zone", "service_zone"]
    taxi_df = extractor.read_parquet(trip_file)
    
    logger.info("[1/4] STEP: EXTRACT & INGESTION COMPLETED")

    # ==========================================
    # 2. STEP: TRANSFORM DATA
    # ==========================================

    logger.info("[2/4] STEP: TRANSFORMATION STARTED")

    transformer = DataTransformer()
    taxi_df = transformer.rename_columns_trip(taxi_df)
    taxi_df = transformer.enrich_datetime(taxi_df)
    taxi_df = transformer.add_time_period(taxi_df)
    taxi_df = transformer.map_categorical(taxi_df)
    taxi_df = transformer.join_zones(taxi_df, zone_df)
    taxi_df = transformer.reorder_columns(taxi_df)
    
    logger.info("[2/4] STEP: TRANSFORMATION COMPLETED")

    # ==========================================
    # 3. STEP: LOAD LAYER (STAGING TO MART)
    # ==========================================

    logger.info("[3/4] STEP: LOAD STARTED")

    loader = DataLoader()

    loader.save_parquet(taxi_df, "data/transformed", "taxi_nyc.parquet")
    loader.parquet_to_csv(
        os.path.join(TRANSFORM_PATH,"taxi_nyc.parquet"),
        os.path.join(MART_PATH,"taxi_nyc.csv")
    )

    logger.info("[3/4] STEP: LOAD COMPLETED")

    # ==========================================
    # 4. STEP: DATA QUALITY CHECK & VALIDATION
    # ==========================================

    logger.info("[4/4] STEP: DATA QUALITY CHECK STARTED")

    MART_CSV_INPUT = os.path.join(MART_PATH, "taxi_nyc.csv")
    TAXI_TRIPS_VALIDATE = pd.read_csv(MART_CSV_INPUT)

    validator = DataValidator(TAXI_TRIPS_VALIDATE)
    validator.mark_errors()

    report = validator.save_clean_and_quarantine(CLEANED_MART_PATH)
    logger.info("[4/4] STEP: DATA QUALITY CHECK COMPLETED")


    # ==========================================
    # FINAL OUTPUT: SUMMARY REPORT PRINT
    # ==========================================
    # --- Print report ---
    print("\n" + "="*50)
    print("LAPORAN VALIDASI DATA")
    print("="*50)
    for key, value in report.items():
        print(f"{key:<30}: {value:,}")
    print("="*50)
    
    # Hitung Total Durasi Eksekusi Akhir Pipeline
    elapsed_time = time.time() - start_time
    menit = int(elapsed_time // 60)
    detik = int(elapsed_time % 60)
    
    logger.info(f"[SUKSES] Pipeline berjalan sukses dalam {menit} menit {detik} detik ({elapsed_time:.2f} detik)")
    logger.info(f"-> Berkas tersaring rapi di folder: {CLEANED_MART_PATH}\n")

if __name__ == "__main__":
    main()


























































# import os
# import time
# import pandas as pd
# from src.extract_load import (
#     download_file,
#     read_csv,
#     read_parquet,
#     save_parquet,
#     parquet_to_csv,
# )
# from src.transform import (
#     rename_columns_trip,
#     enrich_datetime,
#     add_time_period,
#     map_categorical,
#     join_zones,
#     reorder_columns,
# )

# # Mengimpor modul validasi utama dari src/validate.py
# from src.validate import save_clean_and_quarantine

# # ==========================================
# # +             PATH KONFIGURASI           +
# # ==========================================
# BASE_DIR = os.getcwd()  # Otomatis menyesuaikan folder project aktif
# RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
# TRANSFORM_PATH = os.path.join(BASE_DIR, "data", "transformed")
# MART_PATH = os.path.join(BASE_DIR, "data", "mart")
# CLEANED_PATH = os.path.join(BASE_DIR, "data", "mart_cleaned")

# # URL SUMBER DATASET
# URL_DATASET_1 = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
# URL_DATASET_2 = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"


# def main():

#     # 2. Catat waktu awal seluruh pipeline
#     pipeline_start = time.time()

#     print("\n" + "=" * 50)
#     print("        STARTING ETL & VALIDATION PIPELINE")
#     print("=" * 50)

#     # ==========================================
#     # 1. STEP: EXTRACT DATA
#     # ==========================================
#     print("\n[1/4] STEP: EXTRACT & INGESTION")

#     # Memastikan direktori penampung file mentah sudah dibuat
#     os.makedirs(RAW_PATH, exist_ok=True)

#     # [Wajib Aktif] Download otomatis berkas dari internet ke folder raw
#     print("[*] Mendownload berkas fakta: Yellow Trip Taxi Parquet...")
#     download_file(
#         url=URL_DATASET_1,
#         file_name="yellow_tripdata_2026-01.parquet",
#         raw_folder=RAW_PATH,
#     )

#     print("[*] Mendownload berkas dimensi: Taxi Zone Lookup CSV...")
#     download_file(
#         url=URL_DATASET_2,
#         file_name="taxi_zone_lookup.csv",
#         raw_folder=RAW_PATH,
#     )

#     # Path file lokal setelah didownload
#     zone_taxi_file = os.path.join(RAW_PATH, "taxi_zone_lookup.csv")
#     trip_taxi_file = os.path.join(RAW_PATH, "yellow_tripdata_2026-01.parquet")

#     # ==========================================
#     # 2. STEP: TRANSFORM DATA
#     # ==========================================
#     print("\n[2/4] STEP: TRANSFORMATION")

#     print("[*] Memproses dimensi data: Taxi Zone...")
#     zone_df = read_csv(zone_taxi_file)
#     zone_df.columns = ["location_id", "borough", "zone", "service_zone"]

#     print(
#         "[*] Memproses fakta data: Yellow Trip Taxi (Cleaning & Enrichment)..."
#     )
#     taxi_df = read_parquet(trip_taxi_file)
#     taxi_df = rename_columns_trip(df=taxi_df)
#     taxi_df = enrich_datetime(df=taxi_df)
#     taxi_df = add_time_period(df=taxi_df)
#     taxi_df = map_categorical(df=taxi_df)
#     taxi_df = join_zones(df=taxi_df, join_df=zone_df)
#     taxi_df = reorder_columns(df=taxi_df)

#     # ==========================================
#     # 3. STEP: LOAD LAYER (STAGING TO MART)
#     # ==========================================
#     print("\n[3/4] STEP: LOAD LAYER")

#     # Menyimpan file parquet sebagai arsip transformasi
#     print(f"[*] Menyimpan file parquet hasil transformasi ke: {TRANSFORM_PATH}")
#     os.makedirs(TRANSFORM_PATH, exist_ok=True)
#     save_parquet(
#         df=taxi_df, directory=TRANSFORM_PATH, filename="taxi_nyc.parquet"
#     )

#     # Membuat file CSV mentah ke folder Data Mart sebelum divalidasi
#     print(f"[*] Membuat file data mart mentah (CSV) di: {MART_PATH}")
#     os.makedirs(MART_PATH, exist_ok=True)
#     parquet_to_csv(
#         os.path.join(TRANSFORM_PATH, "taxi_nyc.parquet"),
#         os.path.join(MART_PATH, "taxi_nyc.csv"),
#     )

#     # ==========================================
#     # 4. STEP: DATA VALIDATION & QUARANTINE
#     # ==========================================
#     print("\n[4/4] STEP: DATA VALIDATION & QUALITY CONTROL")

#     mart_csv_input = os.path.join(MART_PATH, "taxi_nyc.csv")

#     print(f"[*] Membaca berkas CSV dari data mart: {mart_csv_input}")
#     taxi_validate = pd.read_csv(mart_csv_input)

#     print("[*] Menjalankan fungsi validasi terpisah...")
#     # Memanggil fungsi yang mengembalikan dictionary report dari src/validate.py
#     hasil_laporan = save_clean_and_quarantine(
#         taxi_validate, output_dir=CLEANED_PATH
#     )

#     # ==========================================
#     # FINAL OUTPUT: SUMMARY REPORT PRINT
#     # ==========================================
#     print("\n" + "=" * 50)
#     print("         LAPORAN VALIDASI DATA TERCETAK")
#     print("=" * 50)
#     for key, value in hasil_laporan.items():
#         print(f"{key:<30}: {value:,}")
#     print("=" * 50)
#     print(f"[SUKSES] Seluruh rangkaian Pipeline ETL sukses dijalankan!")
#     print(f"-> File Valid & Karantina (CSV) disimpan di: {CLEANED_PATH}\n")

#     total_durasi_detik = time.time() - pipeline_start
#     menit = int(total_durasi_detik // 60)
#     detik = int(total_durasi_detik % 60)

#     print(F"waktu yang di butuhkan {menit}: {detik}")

# if __name__ == "__main__":
#     main()
















# # import os
# # import pandas as pd
# # from src.extract_load import download_file, read_csv, read_parquet, save_parquet, parquet_to_csv
# # from src.transform import rename_columns_trip, enrich_datetime, add_time_period, map_categorical, join_zones,reorder_columns
# # from src.validate import mark_errors

# # # PATH KONFIGURASI

# # BASE_DIR = os.getcwd() # base home /mnt/d/Sandbox/Capstone Project
# # RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
# # TRANSFORM_PATH = os.path.join(BASE_DIR, "data", "transformed")
# # MART_PATH = os.path.join(BASE_DIR, "data", "mart")
# # VALIDATION_PATH = os.path.join(BASE_DIR, "data", "mart")

# # # URL
# # URL_DATASET_1 = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
# # URL_DATASET_2 = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"




# # # =================================
# # # +          Extract Data         +  
# # # =================================

# # # Load Data from source url
# # # download_file(url=URL_DATASET_1,file_name="yellow_tripdata_2026-01.parquet",raw_folder=RAW_PATH)
# # # download_file(url=URL_DATASET_2,file_name="taxi_zone_lookup.csv",raw_folder=RAW_PATH)

# # # Data Path Source
# # zone_taxi = os.path.join(
# #     RAW_PATH,
# #     "taxi_zone_lookup.csv"
# # )

# # trip_taxi = os.path.join(
# #     RAW_PATH,
# #     "yellow_tripdata_2026-01.parquet"
# # )

# # # ==============================
# # # +      Transform Data        +  
# # # ==============================

# # #  transform zone taxi
# # # zone_df = read_csv(zone_taxi)
# # # zone_df.columns = ["location_id", "borough", "zone", "service_zone"]

# # # test data
# # # print(zone_df.head(10))
# # # print(zone_df['location_id'].is_unique)  # Harus True
# # # print(zone_df['location_id'].isna().sum()) # Harus 0


# # # transform trip_taxi
# # # taxi_df = read_parquet(trip_taxi)
# # # taxi_df = rename_columns_trip(df=taxi_df)
# # # taxi_df = enrich_datetime(df=taxi_df)
# # # taxi_df = add_time_period(df=taxi_df)
# # # taxi_df = map_categorical(df=taxi_df)
# # # taxi_df = join_zones(df=taxi_df,join_df=zone_df)
# # # taxi_df = reorder_columns(df=taxi_df)

# # # Test data
# # # print(taxi_df["tpep_pickup_datetime"].min())
# # # print(taxi_df["tpep_pickup_datetime"].max())
# # #taxi_df.head(10)

# # # ===========================
# # # +       Load Data         +  
# # # ===========================

# # # Load to transformed data folder
# # # save to tranformed

# # # X_path = os.path.join(
# # #     TRANSFORM_PATH,
# # #     "doraemon.csv"
# # # )
# # # # save parquet dulu di folder data tranformed
# # # save_parquet(df=taxi_df,directory=TRANSFORM_PATH,filename="taxi_nyc.parquet")
# # # print("Convert dataframe to csv completed")


# # # # convert dari parquet ke data mart format csv
# # # parquet_to_csv("data/transformed/taxi_nyc.parquet", "data/mart/taxi_nyc.csv")

# # # =============================
# # # +       Validate Data       +  
# # # =============================



# #     # 1. Tentukan lokasi folder project kamu
# #     BASE_DIR = "/mnt/d/Sandbox/Capstone Project"
# #     input_file = os.path.join(BASE_DIR, "data", "mart", "taxi_nyc.csv")
# #     output_folder = os.path.join(BASE_DIR, "data", "mart_cleaned")

# #     # 2. Membaca data mentah
# #     print(f"[*] Membaca CSV dari: {input_file}")
# #     taxi_validate = pd.read_csv(input_file)

# #     print("[*] Memproses validasi data dan memisahkan berkas...")

# #     # 3. Jalankan fungsi utama
# #     hasil_laporan = save_clean_and_quarantine(
# #         taxi_validate, output_dir=output_folder
# #     )

# #     # 4. Tampilkan summary laporan di terminal
# #     print("\n" + "=" * 40)
# #     print("        LAPORAN VALIDASI DATA TERCETAK")
# #     print("=" * 40)
# #     for key, value in hasil_laporan.items():
# #         print(f"{key:<30}: {value:,}")
# #     print("=" * 40)
# #     print(f"[Sukses] Berhasil mengekstrak 2 file CSV ke: {output_folder}\n")