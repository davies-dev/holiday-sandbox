#!/usr/bin/env python3
import psycopg2
from psycopg2 import sql
from config import DB_PARAMS

def create_tables(conn):
    create_hand_histories = """
    CREATE TABLE IF NOT EXISTS hand_histories (
        id SERIAL PRIMARY KEY,
        game_type VARCHAR(50),
        number_of_players INT,
        hand_id VARCHAR(30),
        poker_site VARCHAR(30),
        button_name VARCHAR(100),
        player_names JSONB,
        stack_sizes JSONB,
        positions JSONB,
        ante NUMERIC,
        pf_action_seq VARCHAR(40),
        flop_action_seq VARCHAR(40),
        turn_action_seq VARCHAR(40),
        river_action_seq VARCHAR(40),
        raw_text TEXT,
        created_at TIMESTAMP DEFAULT NOW()
    );
    """
    create_hand_actions = """
    CREATE TABLE IF NOT EXISTS hand_actions (
        id SERIAL PRIMARY KEY,
        hand_history_id INT REFERENCES hand_histories(id) ON DELETE CASCADE,
        street VARCHAR(20) NOT NULL,
        player VARCHAR(100) NOT NULL,
        action_type VARCHAR(20) NOT NULL,
        bet_amount NUMERIC,
        total NUMERIC,
        pot_size NUMERIC,
        action_order INT
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_hand_histories)
        cur.execute(create_hand_actions)
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
