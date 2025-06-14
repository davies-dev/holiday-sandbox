#!/usr/bin/env python3
import psycopg2
from psycopg2 import sql
from config import DB_PARAMS


def create_tables(conn):
    action_patterns = """
    CREATE TABLE action_patterns (
    id SERIAL PRIMARY KEY,
    pattern_name VARCHAR(50) NOT NULL,  -- e.g., 'check-raise'
    applies_to VARCHAR(50) NOT NULL,      -- e.g., 'postflop' (or 'flop,turn,river')
    sql_pattern VARCHAR(100) NOT NULL,    -- e.g., '^.k.r$' for a check-raise
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
    );
    """
    

    
    with conn.cursor() as cur:
        cur.execute(action_patterns)
        
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