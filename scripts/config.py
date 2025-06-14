import os

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