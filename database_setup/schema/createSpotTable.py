#!/usr/bin/env python3
import psycopg2
from psycopg2 import sql
from config import DB_PARAMS


def create_tables(conn):
    create_spot_metadata = """
    CREATE TABLE spot_metadata (
        pf_action_seq VARCHAR(40) PRIMARY KEY,
        spot_name VARCHAR(100),
        links JSONB  -- e.g., an array of link objects, such as:
                    -- [ {"type": "flopzilla", "url": "http://..."}, {"type": "chart", "url": "/path/to/chart.jpg"} ]
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_spot_metadata)
    conn.commit()

def main():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(**DB_PARAMS)
    
    try:
        create_tables(conn)
        print("Tables created successfully.")
    except Exception as e:
        print("Error creating tables:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main()