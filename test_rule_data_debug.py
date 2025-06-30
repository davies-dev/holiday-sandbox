#!/usr/bin/env python3
"""
Test script to debug what stack depth data is actually in the database
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_rule_data():
    """Test what's actually in the database for the rule"""
    print("=== Testing Rule Data from Database ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    # Get all rules to see what's in the database
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT id, rule_description, min_effective_stack_bb, max_effective_stack_bb, board_texture_pattern, pf_action_seq_pattern, flop_action_seq_pattern, turn_action_seq_pattern, river_action_seq_pattern
                FROM study_tag_rules
                ORDER BY id
            """)
            rules = cur.fetchall()
        print(f"Found {len(rules)} rules in database")
        print()
        for rule in rules:
            print(f"Rule ID: {rule[0]}")
            print(f"  Description: {rule[1]}")
            print(f"  Min Stack BB: {rule[2]}")
            print(f"  Max Stack BB: {rule[3]}")
            print(f"  Board Texture: {rule[4]}")
            print(f"  PF Pattern: {rule[5]}")
            print(f"  Flop Pattern: {rule[6]}")
            print(f"  Turn Pattern: {rule[7]}")
            print(f"  River Pattern: {rule[8]}")
            print()
        # Look specifically for rules with stack depth constraints
        stack_rules = [r for r in rules if r[2] is not None or r[3] is not None]
        print(f"Rules with stack depth constraints: {len(stack_rules)}")
        for rule in stack_rules:
            print(f"  Rule {rule[0]}: {rule[2]}-{rule[3]} bb")
        
        # Check specifically for Tag 12 rules
        print(f"\n=== Checking Tag 12 Rules ===")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.rule_description, r.min_effective_stack_bb, r.max_effective_stack_bb, 
                       r.board_texture_pattern, r.pf_action_seq_pattern, r.flop_action_seq_pattern, 
                       r.turn_action_seq_pattern, r.river_action_seq_pattern, t.tag_name
                FROM study_tag_rules r
                JOIN study_tags t ON r.tag_id = t.id
                WHERE r.tag_id = 12
                ORDER BY r.id
            """)
            tag_12_rules = cur.fetchall()
        
        print(f"Tag 12 has {len(tag_12_rules)} rules:")
        for rule in tag_12_rules:
            print(f"  Rule ID: {rule[0]}")
            print(f"    Description: {rule[1]}")
            print(f"    Min Stack BB: {rule[2]}")
            print(f"    Max Stack BB: {rule[3]}")
            print(f"    Board Texture: {rule[4]}")
            print(f"    PF Pattern: '{rule[5]}'")
            print(f"    Flop Pattern: '{rule[6]}'")
            print(f"    Turn Pattern: '{rule[7]}'")
            print(f"    River Pattern: '{rule[8]}'")
            print(f"    Tag Name: {rule[9]}")
            print()
            
    except Exception as e:
        print(f"Error querying rules: {e}")
    db.close()

if __name__ == "__main__":
    test_rule_data() 