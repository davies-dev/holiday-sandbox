#!/usr/bin/env python3
"""
Test script for board texture matching functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from board_analyzer import analyze_board
from db_access import DatabaseAccess
from config import DB_PARAMS

class MockHandHistoryData:
    """Mock class to simulate hand history data for testing"""
    def __init__(self, flop_cards=None, action_sequences=None):
        self.flop_cards = flop_cards or []
        self.action_sequences = action_sequences or {}
    
    def get_simple_action_sequence(self, street):
        return self.action_sequences.get(street, "")

def test_board_analyzer():
    """Test the board analyzer with various board textures"""
    print("Testing Board Analyzer...")
    
    test_cases = [
        (['Ah', 'Kh', '2h'], {'monotone', 'A-high', 'broadway_present'}),
        (['Ah', 'Kh', 'Qh'], {'monotone', 'A-high', 'broadway_heavy'}),
        (['Ah', 'Kh', '2c'], {'two_tone', 'A-high', 'broadway_present'}),
        (['Ah', 'Kh', '2d'], {'rainbow', 'A-high', 'broadway_present'}),
        (['Ah', 'Ah', '2h'], {'monotone', 'A-high', 'paired'}),
        (['Ah', 'Ah', 'Kh'], {'monotone', 'A-high', 'paired', 'broadway_present'}),
        (['Ah', 'Ah', 'Kh', 'Kh'], {'monotone', 'A-high', 'two_pair', 'broadway_present'}),
        (['Ah', 'Ah', 'Ah', '2h'], {'monotone', 'A-high', 'trips'}),
        (['Ah', 'Ah', 'Ah', 'Kh'], {'monotone', 'A-high', 'trips', 'broadway_present'}),
        (['Ah', 'Ah', 'Ah', 'Kh', 'Kh'], {'monotone', 'A-high', 'full_house', 'trips', 'broadway_present'}),
        (['Ah', 'Ah', 'Ah', 'Ah', '2h'], {'monotone', 'A-high', 'quads'}),
    ]
    
    for cards, expected in test_cases:
        result = analyze_board(cards)
        if result == expected:
            print(f"✅ {cards} -> {result}")
        else:
            print(f"❌ {cards} -> {result} (expected {expected})")
    
    print()

def test_rule_matching():
    """Test rule matching with board textures"""
    print("Testing Rule Matching...")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    # Test case 1: Monotone board
    hand1 = MockHandHistoryData(
        flop_cards=['Ah', 'Kh', '2h'],
        action_sequences={'preflop': '1f2f3r4r5c6c', 'flop': '1k2k3b4c5c'}
    )
    
    # Test case 2: Paired board
    hand2 = MockHandHistoryData(
        flop_cards=['Ah', 'Ah', '2h'],
        action_sequences={'preflop': '1f2f3r4r5c6c', 'flop': '1k2k3b4c5c'}
    )
    
    # Test case 3: Broadway heavy board
    hand3 = MockHandHistoryData(
        flop_cards=['Ah', 'Kh', 'Qh'],
        action_sequences={'preflop': '1f2f3r4r5c6c', 'flop': '1k2k3b4c5c'}
    )
    
    # Create test rules
    test_rules = [
        {
            'id': 1,
            'tag_id': 1,
            'rule_description': 'Monotone Board Rule',
            'pf_pattern': '1f2f3r4r5c6c',
            'flop_pattern': '1k2k3b4c5c',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': 'monotone'
        },
        {
            'id': 2,
            'tag_id': 2,
            'rule_description': 'Paired Board Rule',
            'pf_pattern': '1f2f3r4r5c6c',
            'flop_pattern': '1k2k3b4c5c',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': 'paired'
        },
        {
            'id': 3,
            'tag_id': 3,
            'rule_description': 'Broadway Heavy Rule',
            'pf_pattern': '1f2f3r4r5c6c',
            'flop_pattern': '1k2k3b4c5c',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': 'broadway_heavy'
        },
        {
            'id': 4,
            'tag_id': 4,
            'rule_description': 'Multiple Texture Rule',
            'pf_pattern': '1f2f3r4r5c6c',
            'flop_pattern': '1k2k3b4c5c',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': 'monotone,A-high'
        }
    ]
    
    test_hands = [
        ('Monotone Board', hand1),
        ('Paired Board', hand2),
        ('Broadway Heavy Board', hand3)
    ]
    
    for hand_name, hand in test_hands:
        print(f"\nTesting {hand_name}:")
        for rule in test_rules:
            matches = db._check_rule_match(rule, hand)
            print(f"  {rule['rule_description']}: {'✅' if matches else '❌'}")
    
    db.close()

def main():
    """Run all tests"""
    print("Board Texture Matching Tests")
    print("=" * 40)
    
    test_board_analyzer()
    test_rule_matching()
    
    print("\nTests completed!")

if __name__ == "__main__":
    main() 