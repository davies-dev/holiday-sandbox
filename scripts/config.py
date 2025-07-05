import os
from pathlib import Path

# Database configuration
# Environment variables expected:
# - DB_HOST: Database host (default: "localhost")
# - DB_PORT: Database port (default: 5432)
# - DB_NAME: Database name (default: "HolidayBrowser")
# - DB_USER: Database username (default: "postgres")
# - DB_PASS: Database password (default: "Holidayedy123")

DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = int(os.environ.get("DB_PORT", "5432"))
DB_NAME = os.environ.get("DB_NAME", "HolidayBrowser")
DB_USER = os.environ.get("DB_USER", "postgres")
DB_PASS = os.environ.get("DB_PASS", "Holidayedy123")

# Database connection parameters
DB_PARAMS = {
    "host": DB_HOST,
    "port": DB_PORT,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASS
}

# GTO+ file processing configuration
# Base path for GTO+ file processing and storage
GTO_BASE_PATH = Path("C:\\@myfiles\\gtotorunwhenIleave\\")

# Path to the GTO+ executable
GTO_EXECUTABLE_PATH = r"C:\\Program Files\\GTO\\GTO.exe"

# GTO+ file location configuration
# Snapshot directory (original GTO+ files)
GTO_SNAPSHOT_PATH = Path("C:\\@myfiles\\30000 Poker\\GAMES\\6 max\\6 max MPT GTO snap shot 20210114\\")

# Processing directory (files being processed)
GTO_PROCESSING_PATH = GTO_BASE_PATH

# GTO+ running directory (files currently in GTO+)
GTO_RUNNING_PATH = GTO_BASE_PATH

# Priority queue directory (files with 1.x - prefix)
GTO_PRIORITY_PATH = GTO_BASE_PATH

# Processed directory (completed files)
GTO_PROCESSED_PATH = GTO_BASE_PATH / "processed"

# File prefix patterns
GTO_RUNNING_PREFIX = "0 - "
GTO_PRIORITY_PREFIX_PATTERN = r"^1\.\d+ - "  # Matches "1.x - " where x is any integer 