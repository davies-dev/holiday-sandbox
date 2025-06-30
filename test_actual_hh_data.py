#!/usr/bin/env python3
"""
Test script to check what's actually in the HandHistoryData object
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_actual_hand_history_data():
    """Test what's actually in the HandHistoryData object"""
    print("=== Testing Actual HandHistoryData Object ===")
    
    # Sample hand history text from the user's example
    hand_text = """PokerStars Zoom Hand #256760112737:  Hold'em No Limit ($0.01/$0.02) - 2025/06/30 1:47:29 ET
Table 'Halley' 6-max Seat #1 is the button
Seat 1: cowpop3 ($2.29 in chips) 
Seat 2: phantomaup ($0.30 in chips) 
Seat 3: HumptyD ($2.08 in chips) 
Seat 4: Trollrian ($2.01 in chips) 
Seat 5: CrushingLife ($3.14 in chips) 
Seat 6: EatBatteries ($3.26 in chips) 
phantomaup: posts small blind $0.01
HumptyD: posts big blind $0.02
*** HOLE CARDS ***
Dealt to HumptyD [As Jc]
Trollrian: folds 
CrushingLife: folds 
EatBatteries: folds 
cowpop3: raises $0.03 to $0.05
phantomaup: folds 
HumptyD: calls $0.03
*** FLOP *** [Jd 3d 5d]
HumptyD: checks 
cowpop3: bets $0.04
HumptyD: calls $0.04
*** TURN *** [Jd 3d 5d] [9c]
HumptyD: checks 
cowpop3: checks 
*** RIVER *** [Jd 3d 5d 9c] [9d]
HumptyD: checks 
cowpop3: checks
*** SHOW DOWN ***
HumptyD: shows [As Jc] (two pair, Jacks and Nines)
cowpop3: mucks hand 
HumptyD collected $0.18 from pot"""

    try:
        # Import the parser and create actual HandHistoryData
        from holiday_parser import get_hand_history_parser
        
        # Parse the hand history
        parser = get_hand_history_parser(hand_text)
        hh_data = parser.parse(hand_text)
        
        print("HandHistoryData object created successfully!")
        print(f"Type: {type(hh_data)}")
        
        # Check what attributes are available
        print("\nAvailable attributes:")
        for attr in dir(hh_data):
            if not attr.startswith('_'):
                try:
                    value = getattr(hh_data, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except Exception as e:
                    print(f"  {attr}: Error accessing - {e}")
        
        # Specifically check for effective_stack_bb
        print(f"\nChecking effective_stack_bb specifically:")
        if hasattr(hh_data, 'effective_stack_bb'):
            print(f"  effective_stack_bb exists: {getattr(hh_data, 'effective_stack_bb')}")
        else:
            print("  effective_stack_bb does NOT exist")
        
        # Check for other stack-related attributes
        stack_attrs = ['stack_sizes', 'stacks', 'player_stacks', 'effective_stack']
        for attr in stack_attrs:
            if hasattr(hh_data, attr):
                print(f"  {attr}: {getattr(hh_data, attr)}")
        
        # Test the rule matching with the actual object
        print(f"\nTesting rule matching with actual HandHistoryData:")
        
        # Create database access object
        db = DatabaseAccess(**DB_PARAMS)
        
        # Test rule matching with a rule that should NOT match (85-95 bb range)
        rule_85_95 = {
            'min_stack_bb': 85,
            'max_stack_bb': 95,
            'pf_pattern': '1f2f3f4r5f6c',  # Should match
            'flop_pattern': '6k4b6c',       # Should match
            'turn_pattern': '6k4k',         # Should match
            'river_pattern': '6k4k'         # Should match
        }
        
        match_result = db._check_rule_match(rule_85_95, hh_data)
        print(f"Rule 85-95 bb match result: {match_result}")
        
        if match_result:
            print("❌ ERROR: Hand should NOT match the rule (104 bb > 95 bb)")
        else:
            print("✅ CORRECT: Hand correctly does NOT match the rule")
        
        db.close()
        
    except ImportError as e:
        print(f"Could not import holiday_parser: {e}")
        print("This suggests the holiday_parser module is not available or not properly installed.")
    except Exception as e:
        print(f"Error creating HandHistoryData: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_actual_hand_history_data() 