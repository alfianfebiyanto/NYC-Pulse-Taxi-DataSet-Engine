# Menggunakan base image Python 3.12 ringan
FROM python:3.12-slim

# Set working directory di dalam container
WORKDIR /app

# Copy requirements.txt (harus ada)
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh kode sumber dan script
COPY main.py .
COPY src/ ./src/
COPY scripts/ ./scripts/

# Perintah default saat container dijalankan
CMD ["python", "main.py"]