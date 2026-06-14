#!/bin/bash

# Log file location
LOG_DIR="./logs"
LOG_FILE="$LOG_DIR/pipeline.log"

# Create logs directory if not exists
mkdir -p "$LOG_DIR"

# Function to log with timestamp
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Start pipeline
log "=========================================="
log "     STARTING ETL PIPELINE VIA SCRIPT"
log "=========================================="

# Optional: set environment variable if not already set
# export DATA_URL="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2026-01.parquet"

log "Step 1: Running main.py (full pipeline)"
python main.py
if [ $? -eq 0 ]; then
    log "Pipeline completed successfully"
else
    log "Pipeline failed with error code $?"
    exit 1
fi

log "=========================================="
log "              PIPELINE FINISHED"
log "=========================================="