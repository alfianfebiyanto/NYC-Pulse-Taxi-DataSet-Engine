# Import Libary
import os
import sys
import time
import logging
import pandas as pd
from src.extract_load import DataExtractor, DataLoader
from src.transform import DataTransformer
from src.validate import DataValidator

# Import centralized logger module from src/logger.py
from src.logger import setup_logger

"""
Main ETL pipeline for NYC Taxi Trip Data.

Orchestrates the end-to-end data pipeline:
1. Extract - Download raw data from remote sources
2. Transform - Clean, enrich, and join datasets
3. Load - Save transformed data to staging and mart
4. Validate - Perform data quality checks and quarantine invalid records
"""

# ==========================================
# +             PATH CONFIGURATION          +
# ==========================================
BASE_DIR = os.getcwd()  # Root directory of the project
RAW_PATH = os.path.join(BASE_DIR, "data", "raw")
TRANSFORM_PATH = os.path.join(BASE_DIR, "data", "transformed")
MART_PATH = os.path.join(BASE_DIR, "data", "mart")
CLEANED_MART_PATH = os.path.join(BASE_DIR, "data", "mart_cleaned")

# Dataset source URLs
TAXI_TRIPS_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"
ZONE_TAXI_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"


def main():
    """
    Execute the complete ETL pipeline with validation.

    Workflow:
        - Initialize logging and timer.
        - Extract raw data (trips and zones).
        - Transform data (rename columns, datetime enrichment, categorical mapping, zone joins).
        - Load transformed data to Parquet and CSV (data mart).
        - Validate data quality and split clean/invalid records.
        - Print summary report and execution time.
    """

    logger = setup_logger() # Initialize logger 
    start_time = time.time() # Track total pipeline execution time

    logger.info("=" * 50)
    logger.info("        STARTING ETL PIPELINE")
    logger.info("=" * 50)

    # Allow override of taxi trips URL via environment variable
    data_url = os.getenv("Data_URL",TAXI_TRIPS_URL)

    # ==========================================
    # 1. STEP: EXTRACT DATA
    # ==========================================

    logger.info("[1/4] STEP: EXTRACT & INGESTION STARTED")
    extractor = DataExtractor(raw_folder=RAW_PATH)

    # Download zone lookup CSV and trip Parquet file
    zone_file = extractor.download_file(ZONE_TAXI_URL, "taxi_zone_lookup.csv")
    trip_file = extractor.download_file(data_url, "yellow_tripdata_2026-01.parquet")

    # Load data into pandas DataFrames
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

    # Save as Parquet for archival/transformed layer
    loader.save_parquet(taxi_df, "data/transformed", "taxi_nyc.parquet")
    
    # Convert to CSV for downstream validation and reporting
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
    
    # Calculate and log total execution duration
    elapsed_time = time.time() - start_time
    menit = int(elapsed_time // 60)
    detik = int(elapsed_time % 60)
    
    logger.info(f"[SUKSES] Pipeline berjalan sukses dalam {menit} menit {detik} detik ({elapsed_time:.2f} detik)")
    logger.info(f"-> Berkas tersaring rapi di folder: {CLEANED_MART_PATH}\n")

if __name__ == "__main__":
    main()