"""
Modul utilitas untuk Extract (mengambil data dari sumber) dan Load (menyimpan data ke tujuan).
Mencakup download file dari URL, membaca CSV/Parquet, dan menyimpan ke Parquet/CSV.
"""
# Import Library
import requests
import os
import pandas as pd
import pyarrow.parquet as pq
from .logger import logger


class DataExtractor:
    def __init__(self, raw_folder="data/raw"):
        self.raw_folder = raw_folder
        os.makedirs(self.raw_folder, exist_ok=True)

    def download_file(self, url, file_name):
        file_path = os.path.join(self.raw_folder, file_name)
        response = requests.get(url)
        
        # Logging awall
        logger.info(f"Preparing download file {file_name}")

        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)

            #logging succes
            logger.info(f"Download file {file_name} : [SUCCESS]")
            return file_path
        else:
            #logging error
            logger.error(f"[X] Gagal download dari URL: {url} (Status: {response.status_code})")
            raise Exception(f"Gagal download {url}")

    def read_csv(self, file_path):
        logger.info("Read CSV to Dataframe")
        return pd.read_csv(file_path)

    def read_parquet(self, file_path):
        logger.info("Read PARQUET to Dataframe")
        return pd.read_parquet(file_path)


class DataLoader:
    @staticmethod
    def save_parquet(df, directory, filename):
        os.makedirs(directory, exist_ok=True)
        if not filename.endswith('.parquet'):
            filename += '.parquet'
        file_path = os.path.join(directory, filename)
        df.to_parquet(file_path, index=False)
        logger.info("Save to Parquet")
        

    @staticmethod
    def parquet_to_csv(parquet_path, csv_path=None, batch_size=100000):
        if csv_path is None:
            csv_path = os.path.splitext(parquet_path)[0] + '.csv'
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)

        logger.info(f"Convert Parquet to CSV Data Mart")

        parquet_file = pq.ParquetFile(parquet_path)
        first_chunk = True
        total_rows = 0
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            chunk = batch.to_pandas()
            for col in chunk.columns:
                if chunk[col].dtype == 'object' and len(chunk) > 0:
                    sample = chunk[col].iloc[0]
                    if isinstance(sample, bytes):
                        chunk[col] = chunk[col].str.decode('utf-8', errors='replace')
            chunk.to_csv(csv_path, mode='a', header=first_chunk, index=False, encoding='utf-8-sig')
            total_rows += len(chunk)
            first_chunk = False

        logger.info(f"Convert [SUCCESS]")

