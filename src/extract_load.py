"""
Utility module for Extract (fetch data from source) and Load (save data to destination).

Includes:
- DataExtractor: Download files from URL, read CSV/Parquet.
- DataLoader: Static class to save DataFrame to Parquet and convert Parquet to CSV.
"""

# Import Library
import requests
import os
import pandas as pd
import pyarrow.parquet as pq
from .logger import logger

class DataExtractor:
    """
    Handle data extraction from external sources (URL or local files).
    """

    def __init__(self, raw_folder="data/raw"):
        self.raw_folder = raw_folder
        os.makedirs(self.raw_folder, exist_ok=True)

    def download_file(self, url, file_name):
        """
        Download a file from a URL to the raw folder.
        """

        file_path = os.path.join(self.raw_folder, file_name)
        response = requests.get(url)
        
        # Log start of download file
        logger.info(f"Preparing download file {file_name}")

        if response.status_code == 200:
            with open(file_path, "wb") as f:
                f.write(response.content)

            # Log success
            logger.info(f"Download file {file_name} : [SUCCESS]")
            return file_path
        else:
            # Log failure and raise exception
            logger.error(f"[X] Gagal download dari URL: {url} (Status: {response.status_code})")
            raise Exception(f"Gagal download {url}")

    def read_csv(self, file_path):
        """ 
        Read a CSV file into a pandas DataFrame.
        """
        logger.info("Read CSV to Dataframe")
        return pd.read_csv(file_path)

    def read_parquet(self, file_path):
        """ 
        Read a Parquet file into a pandas DataFrame.
        """
        logger.info("Read PARQUET to Dataframe")
        return pd.read_parquet(file_path)


class DataLoader:
    @staticmethod
    def save_parquet(df, directory, filename):
        """
        Save a DataFrame to a Parquet file.
        """

        # Create folder if needed & Ensure .parquet extension
        os.makedirs(directory, exist_ok=True)
        if not filename.endswith('.parquet'):
            filename += '.parquet'

        # Save DataFrame to Parquet
        file_path = os.path.join(directory, filename)
        df.to_parquet(file_path, index=False)
        logger.info("Save to Parquet")
        

    @staticmethod
    def parquet_to_csv(parquet_path, csv_path=None, batch_size=100000):
        """
        Convert a Parquet file to CSV using batch processing (memory efficient).
        Automatically decodes byte columns to UTF-8 strings.
        """

        if csv_path is None:
            csv_path = os.path.splitext(parquet_path)[0] + '.csv'
        os.makedirs(os.path.dirname(os.path.abspath(csv_path)), exist_ok=True)
        logger.info(f"Convert Parquet to CSV Data Mart")

        # Open Parquet file for batch reading
        parquet_file = pq.ParquetFile(parquet_path)
        first_chunk = True
        total_rows = 0

        # Process each batch
        for batch in parquet_file.iter_batches(batch_size=batch_size):
            chunk = batch.to_pandas()

            # Decode bytes columns to UTF-8 strings
            for col in chunk.columns:
                if chunk[col].dtype == 'object' and len(chunk) > 0:
                    sample = chunk[col].iloc[0]
                    if isinstance(sample, bytes):
                        chunk[col] = chunk[col].str.decode('utf-8', errors='replace')

            # Write chunk to CSV
            chunk.to_csv(csv_path, mode='a', header=first_chunk, index=False, encoding='utf-8-sig')
            total_rows += len(chunk)
            first_chunk = False

        logger.info(f"Convert [SUCCESS]")

