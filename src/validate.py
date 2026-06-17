"""
Data validation and quality control for taxi trip records.
"""

# Import Library
import pandas as pd
import os
from .logger import logger

class DataValidator:
    """
    Validate taxi trip data, mark erroneous records, and separate clean vs invalid rows.
    """


    def __init__(self, df):
        """
        Initialize validator with a copy of the input DataFrame.
        """
        self.df = df.copy()
        logger.info(f"DataValidator initialized with {len(self.df):,} rows.")

    def mark_errors(self):
        """
        Identify invalid trip durations and distances.

        Rules:
        - Duration invalid: pickup >= dropoff OR duration <= 0 minutes.
        - Distance invalid: trip_distance <= 0.
        - error_type column stores the reason(s).

        """

        logger.info("Validating trip durations and distances...")
        df = self.df

        # Ensure datetime conversion
        df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"])
        df["dropoff_datetime"] = pd.to_datetime(df["dropoff_datetime"])

        # Calculate duration if not already present
        if "trip_duration_minutes" not in df.columns:
            df["trip_duration_minutes"] = (df["dropoff_datetime"] - df["pickup_datetime"]).dt.total_seconds() / 60

        # Boolean flags for invalid records
        invalid_duration = (df["pickup_datetime"] >= df["dropoff_datetime"]) | (df["trip_duration_minutes"] <= 0)
        invalid_distance = df["trip_distance"] <= 0

        # Assign error types
        df["error_type"] = ""
        df.loc[invalid_duration & ~invalid_distance, "error_type"] = "duration invalid"
        df.loc[invalid_distance & ~invalid_duration, "error_type"] = "distance invalid"
        df.loc[invalid_duration & invalid_distance, "error_type"] = "duration invalid; distance invalid"

        self.df = df
        return self

    def split_valid_invalid(self):
        """
        Split data into valid and invalid DataFrames based on error_type.
        """

        valid = self.df[self.df["error_type"] == ""].drop(columns=["error_type"])
        invalid = self.df[self.df["error_type"] != ""]
        return valid, invalid

    def save_clean_and_quarantine(self, output_dir="data/mart_cleaned"):
        """
        Save clean records to CSV and quarantine invalid records to a separate CSV.
        Generate a quality report dictionary.
        """

        # Split data into valid and invalid
        os.makedirs(output_dir, exist_ok=True)
        valid, invalid = self.split_valid_invalid()

        # Log clean row count
        logger.info(f"Saving {len(valid):,} clean rows to {output_dir}...")
        
        # save clean data to CSV
        valid.to_csv(
            os.path.join(output_dir, "taxi_trips_cleaned.csv"),
            index=False, 
            encoding="utf-8-sig"
        )

        # Save invalid data to quarantine CSV
        invalid.to_csv(
            os.path.join(output_dir,"taxi_trips_quarantine.csv"),
            index=False,
            encoding="utf-8-sig"
        )

        # Compile quality report
        report = {
            "Total Data Awal": len(self.df),
            "Data Valid (Bersih)": len(valid),
            "Data Invalid (Karantina)": len(invalid),
            "Penyebab: Durasi Bermasalah": self.df["error_type"].str.contains("duration").sum(),
            "Penyebab: Jarak Bermasalah": self.df["error_type"].str.contains("distance").sum(),
        }
        
        # Log completion and return report
        logger.info("Data quality check and split completed successfully.")
        return report
