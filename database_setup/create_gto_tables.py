#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'scripts'))

import psycopg2
from config import DB_PARAMS
from pathlib import Path

def create_gto_tables():
    """Create GTO+ related tables"""
    conn = psycopg2.connect(**DB_PARAMS)
    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gto_mappings (
                id SERIAL PRIMARY KEY,
                state_name VARCHAR(50) NOT NULL,
                game_type VARCHAR(50) NOT NULL,
                gto_file_path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state_name, game_type)
            )
        """)
    
    conn.commit()
    conn.close()
    print("GTO+ tables created successfully")

if __name__ == "__main__":
    create_gto_tables() 