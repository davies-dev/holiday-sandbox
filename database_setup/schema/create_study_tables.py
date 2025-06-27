#!/usr/bin/env python3
import psycopg2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from config import DB_PARAMS

def create_study_tables(conn):
    create_study_documents = """
    CREATE TABLE IF NOT EXISTS study_documents (
        id SERIAL PRIMARY KEY,
        title VARCHAR(255) NOT NULL,
        file_path VARCHAR(500) NOT NULL UNIQUE,
        source_info TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    create_study_tags = """
    CREATE TABLE IF NOT EXISTS study_tags (
        id SERIAL PRIMARY KEY,
        tag_name VARCHAR(100) NOT NULL UNIQUE,
        description TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    create_study_document_tags = """
    CREATE TABLE IF NOT EXISTS study_document_tags (
        document_id INT NOT NULL REFERENCES study_documents(id) ON DELETE CASCADE,
        tag_id INT NOT NULL REFERENCES study_tags(id) ON DELETE CASCADE,
        PRIMARY KEY (document_id, tag_id)
    );
    """
    create_study_tag_rules = """
    CREATE TABLE IF NOT EXISTS study_tag_rules (
        id SERIAL PRIMARY KEY,
        tag_id INT NOT NULL REFERENCES study_tags(id) ON DELETE CASCADE,
        rule_description TEXT,
        pf_action_seq_pattern TEXT,
        flop_action_seq_pattern TEXT,
        turn_action_seq_pattern TEXT,
        river_action_seq_pattern TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
    );
    """
    with conn.cursor() as cur:
        cur.execute(create_study_documents)
        cur.execute(create_study_tags)
        cur.execute(create_study_document_tags)
        cur.execute(create_study_tag_rules)
    conn.commit()

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        create_study_tables(conn)
        print("Study tables created successfully.")
    except Exception as e:
        print("Error creating study tables:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 