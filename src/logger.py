import logging
import os
from datetime import datetime


def setup_logger():
    """Konfigurasi Logging secara terpusat untuk seluruh project."""

    log_dir = os.path.join(os.getcwd(), "logs")

    # PERBAIKAN: Menggunakan os.makedirs agar exist_ok bisa berjalan tanpa error
    os.makedirs(log_dir, exist_ok=True)

    # Nama file log berdasarkan tanggal, misal: pipeline_2026-06-11.log
    log_filename = f"pipeline_{datetime.now().strftime('%Y-%m-%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)

    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    format_jam = "%Y-%m-%d %H:%M:%S"

    # Konfigurasi dasar (Hanya dijalankan sekali di seluruh aplikasi)
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        datefmt=format_jam,
        handlers=[
            logging.FileHandler(
                log_filepath, encoding="utf-8"
            ),  # Catat ke file
            logging.StreamHandler(),  # Tetap munculkan di terminal
        ],
    )

    # Kembalikan logger utama
    return logging.getLogger("PipelineUtama")

logger =setup_logger()