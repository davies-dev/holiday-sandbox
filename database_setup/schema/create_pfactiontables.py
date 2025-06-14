#!/usr/bin/env python3
import psycopg2
from psycopg2 import sql
from config import DB_PARAMS


def create_tables(conn):
    create_hand_state = """
    CREATE TABLE hand_state (
        id SERIAL PRIMARY KEY,
        state_type VARCHAR(20) NOT NULL,   -- e.g. 'preflop', 'flop', 'turn', 'river'
        state_value VARCHAR(40) NOT NULL,    -- the normalized action string (e.g., "1f2f3f4r5r6r5c")
        state_name VARCHAR(100),             -- an optional descriptive name (e.g., "Everyone folds to SB, flat BB")
        is_favorite BOOLEAN DEFAULT false,   -- mark if of interest
        description TEXT,
        created_at TIMESTAMP DEFAULT NOW()
        );"""
    

    create_chain_sequence="""
    CREATE TABLE chain_sequence (
        id SERIAL PRIMARY KEY,
    chain_name VARCHAR(100) NOT NULL,    -- e.g., "Triple Barrel"
    preflop_state_id INT REFERENCES hand_state(id),
    flop_state_id INT REFERENCES hand_state(id),
    turn_state_id INT REFERENCES hand_state(id),
    river_state_id INT REFERENCES hand_state(id),
    description TEXT,
    is_favorite BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
    );"""
    with conn.cursor() as cur:
        cur.execute(create_hand_state)
        cur.execute(create_chain_sequence)
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