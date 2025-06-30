#!/usr/bin/env python3
"""
Test script to verify monotone flop rule matching
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from db_access import DatabaseAccess
from config import DB_PARAMS
from board_analyzer import analyze_board

class MockHandHistoryData:
    """Mock class to simulate hand history data for testing"""
    def __init__(self, flop_cards=None, action_sequences=None, raw_text=None):
        self.flop_cards = flop_cards or []
        self.action_sequences = action_sequences or {}
        self.raw_text = raw_text or ""
    
    def get_simple_action_sequence(self, street):
        return self.action_sequences.get(street, "")

def test_monotone_rule():
    """Test the monotone flop rule matching"""
    print("Testing Monotone Flop Rule...")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    # Test board analyzer first
    print("\n1. Testing Board Analyzer:")
    test_cases = [
        (['Ah', 'Kh', '2h'], "monotone flop"),
        (['Ah', 'Kh', '2c'], "two-tone flop"),
        (['Ah', 'Kh', '2d'], "rainbow flop")
    ]
    
    for cards, description in test_cases:
        textures = analyze_board(cards)
        print(f"   {cards} -> {textures} ({description})")
    
    # Test rule matching
    print("\n2. Testing Rule Matching:")
    
    # Create test hand with monotone flop
    monotone_hand = MockHandHistoryData(
        flop_cards=['Ah', 'Kh', '2h'],
        action_sequences={
            'preflop': '1f2f3r4r5c6c',
            'flop': '1k2k3b4c5c',
            'turn': '',
            'river': ''
        },
        raw_text="*** FLOP *** [Ah Kh 2h]"
    )
    
    # Create test hand with rainbow flop
    rainbow_hand = MockHandHistoryData(
        flop_cards=['Ah', 'Kh', '2d'],
        action_sequences={
            'preflop': '1f2f3r4r5c6c',
            'flop': '1k2k3b4c5c',
            'turn': '',
            'river': ''
        },
        raw_text="*** FLOP *** [Ah Kh 2d]"
    )
    
    # Check which rules match each hand
    print("\n3. Checking which rules match:")
    
    # Get all rules
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT r.id, r.rule_description, r.board_texture_pattern, t.tag_name,
                       r.pf_action_seq_pattern, r.flop_action_seq_pattern
                FROM study_tag_rules r
                JOIN study_tags t ON r.tag_id = t.id
                ORDER BY r.id
            """)
            all_rules = cur.fetchall()
        
        print("\n   Monotone flop hand rules:")
        for rule in all_rules:
            rule_id, desc, texture, tag, pf_pattern, flop_pattern = rule
            rule_dict = {
                'id': rule_id,
                'rule_description': desc,
                'board_texture': texture,
                'tag_id': 1,  # dummy value
                'pf_pattern': pf_pattern or '',
                'flop_pattern': flop_pattern or '',
                'turn_pattern': '',
                'river_pattern': ''
            }
            
            if db._check_rule_match(rule_dict, monotone_hand):
                print(f"   ✅ Rule {rule_id} ({tag}): {desc}")
                print(f"      Board texture: '{texture}'")
            else:
                print(f"   ❌ Rule {rule_id} ({tag}): {desc}")
                print(f"      Board texture: '{texture}'")
        
        print("\n   Rainbow flop hand rules:")
        for rule in all_rules:
            rule_id, desc, texture, tag, pf_pattern, flop_pattern = rule
            rule_dict = {
                'id': rule_id,
                'rule_description': desc,
                'board_texture': texture,
                'tag_id': 1,  # dummy value
                'pf_pattern': pf_pattern or '',
                'flop_pattern': flop_pattern or '',
                'turn_pattern': '',
                'river_pattern': ''
            }
            
            if db._check_rule_match(rule_dict, rainbow_hand):
                print(f"   ✅ Rule {rule_id} ({tag}): {desc}")
                print(f"      Board texture: '{texture}'")
            else:
                print(f"   ❌ Rule {rule_id} ({tag}): {desc}")
                print(f"      Board texture: '{texture}'")
                
    except Exception as e:
        print(f"Error checking rules: {e}")
    
    # Find relevant documents for both hands
    print("\n4. Finding relevant documents:")
    print("\n   Monotone flop hand:")
    monotone_docs = db.find_relevant_study_documents(monotone_hand)
    print(f"   Found {len(monotone_docs)} relevant documents")
    for doc in monotone_docs:
        print(f"   - {doc[1]} ({doc[2]})")
    
    print("\n   Rainbow flop hand:")
    rainbow_docs = db.find_relevant_study_documents(rainbow_hand)
    print(f"   Found {len(rainbow_docs)} relevant documents")
    for doc in rainbow_docs:
        print(f"   - {doc[1]} ({doc[2]})")
    
    db.close()

if __name__ == "__main__":
    test_monotone_rule() 