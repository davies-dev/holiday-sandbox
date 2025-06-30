#!/usr/bin/env python3
"""
Script to check existing rules and their board texture patterns
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from db_access import DatabaseAccess
from config import DB_PARAMS

def check_rules():
    """Check all rules in the database"""
    print("Checking existing rules...")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.rule_description, r.board_texture_pattern, t.tag_name
                FROM study_tag_rules r
                JOIN study_tags t ON r.tag_id = t.id
                ORDER BY r.id
            """)
            rules = cur.fetchall()
        
        if not rules:
            print("No rules found in database.")
            return
        
        print(f"\nFound {len(rules)} rules:")
        print("-" * 80)
        for rule in rules:
            rule_id, description, board_texture, tag_name = rule
            print(f"Rule ID: {rule_id}")
            print(f"Tag: {tag_name}")
            print(f"Description: {description}")
            print(f"Board Texture: '{board_texture}'")
            print("-" * 80)
            
    except Exception as e:
        print(f"Error checking rules: {e}")
    
    db.close()

if __name__ == "__main__":
    check_rules() 