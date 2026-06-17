"""
Centralized logging configuration for the entire pipeline.
"""


# Import Library
import logging
import os
from datetime import datetime


def setup_logger():
    """
    Initialize global logging configuration.
    Logs are written to both a daily rotating file and the terminal.
    """

    log_dir = os.path.join(os.getcwd(), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # Log file format: pipeline_YYYY-MM-DD.lo
    log_filename = f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)

    # Log message format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    format_jam = "%Y-%m-%d %H:%M:%S"

    # Base configuration
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=format_jam,
        handlers=[
            logging.FileHandler(log_filepath, encoding="utf-8"), # Output to file
            logging.StreamHandler(),  # Output to terminal
        ],
    )

    # Return the main logger for use across modules
    return logging.getLogger("PipelineUtama")

# Global logger instance
logger = setup_logger()