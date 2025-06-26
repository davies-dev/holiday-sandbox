#!/usr/bin/env python3
import psycopg2
from psycopg2 import sql
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from config import DB_PARAMS

def create_review_tables(conn):
    """Create the review system tables"""
    
    # Create the review status enum type
    create_review_status_enum = """
    DO $$ BEGIN
        CREATE TYPE review_status_enum AS ENUM (
            'unreviewed',
            'eyeballed',
            'marked_for_review',
            'waiting_on_gto',
            'completed'
        );
    EXCEPTION
        WHEN duplicate_object THEN null;
    END $$;
    """
    
    # Create hand_reviews table
    create_hand_reviews = """
    CREATE TABLE IF NOT EXISTS hand_reviews (
        hand_id BIGINT PRIMARY KEY,
        review_status review_status_enum NOT NULL DEFAULT 'unreviewed',
        last_updated TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_hand_histories
            FOREIGN KEY(hand_id)
            REFERENCES hand_histories(id)
            ON DELETE CASCADE
    );
    """
    
    # Create index for hand_reviews
    create_hand_reviews_index = """
    CREATE INDEX IF NOT EXISTS idx_hand_reviews_status ON hand_reviews(review_status);
    """
    
    # Create hand_notes table
    create_hand_notes = """
    CREATE TABLE IF NOT EXISTS hand_notes (
        id SERIAL PRIMARY KEY,
        hand_id BIGINT NOT NULL,
        note_file_path VARCHAR(500) NOT NULL,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        CONSTRAINT fk_hand_histories
            FOREIGN KEY(hand_id)
            REFERENCES hand_histories(id)
            ON DELETE CASCADE
    );
    """
    
    with conn.cursor() as cur:
        cur.execute(create_review_status_enum)
        cur.execute(create_hand_reviews)
        cur.execute(create_hand_reviews_index)
        cur.execute(create_hand_notes)
    conn.commit()

def main():
    # Connect to PostgreSQL database
    conn = psycopg2.connect(**DB_PARAMS)
    
    try:
        create_review_tables(conn)
        print("Review tables created successfully.")
    except Exception as e:
        print("Error creating review tables:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 