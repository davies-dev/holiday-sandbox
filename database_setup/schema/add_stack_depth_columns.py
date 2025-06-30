#!/usr/bin/env python3
import psycopg2
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))
from config import DB_PARAMS

def add_stack_depth_columns(conn):
    """Add min_effective_stack_bb and max_effective_stack_bb columns to study_tag_rules table"""
    alter_table_sql = """
    ALTER TABLE study_tag_rules 
    ADD COLUMN IF NOT EXISTS min_effective_stack_bb INT,
    ADD COLUMN IF NOT EXISTS max_effective_stack_bb INT;
    """
    
    with conn.cursor() as cur:
        cur.execute(alter_table_sql)
    conn.commit()
    print("Added min_effective_stack_bb and max_effective_stack_bb columns to study_tag_rules table")

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    try:
        add_stack_depth_columns(conn)
        print("Database migration completed successfully.")
    except Exception as e:
        print("Error during migration:", e)
    finally:
        conn.close()

if __name__ == "__main__":
    main() 