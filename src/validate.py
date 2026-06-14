import pandas as pd
import os
from .logger import logger

class DataValidator:
    def __init__(self, df):
        self.df = df.copy()
        logger.info(f"DataValidator initialized with {len(self.df):,} rows.")

    def mark_errors(self):

        logger.info("Validating trip durations and distances...")
        df = self.df
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
        df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"])

        if "trip_duration_minutes" not in df.columns:
            df["trip_duration_minutes"] = (df["dropoff_datetime"] - df["pickup_datetime"]).dt.total_seconds() / 60

        invalid_duration = (df["pickup_datetime"] >= df["dropoff_datetime"]) | (df["trip_duration_minutes"] <= 0)

        invalid_distance = df["trip_distance"] <= 0

        df["error_type"] = ""
        df.loc[invalid_duration & ~invalid_distance, "error_type"] = "duration invalid"
        df.loc[invalid_distance & ~invalid_duration, "error_type"] = "distance invalid"
        df.loc[invalid_duration & invalid_distance, "error_type"] = "duration invalid; distance invalid"

        self.df = df
        return self

    def split_valid_invalid(self):
        valid = self.df[self.df["error_type"] == ""].drop(columns=["error_type"])
        invalid = self.df[self.df["error_type"] != ""]
        return valid, invalid

    def save_clean_and_quarantine(self, output_dir="data/mart_cleaned"):
        os.makedirs(output_dir, exist_ok=True)
        valid, invalid = self.split_valid_invalid()

        logger.info(f"Saving {len(valid):,} clean rows to {output_dir}...")
        valid.to_csv(
            os.path.join(output_dir, "taxi_trips_cleaned.csv"),
            index=False, 
            encoding="utf-8-sig"
        )

        invalid.to_csv(
            os.path.join(output_dir,"taxi_trips_quarantine.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        report = {
            "Total Data Awal": len(self.df),
            "Data Valid (Bersih)": len(valid),
            "Data Invalid (Karantina)": len(invalid),
            "Penyebab: Durasi Bermasalah": self.df["error_type"].str.contains("duration").sum(),
            "Penyebab: Jarak Bermasalah": self.df["error_type"].str.contains("distance").sum(),
        }

        logger.info("Data quality check and split completed successfully.")
        return report

