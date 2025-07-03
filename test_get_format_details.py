#!/usr/bin/env python3
"""
Test script to check if get_format_details() method is available in HandHistoryData.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

def test_get_format_details():
    """Test if get_format_details() method is available."""
    print("=== Testing get_format_details() Method Availability ===")
    
    try:
        # Try to import the parser and create HandHistoryData
        from holiday_parser import get_hand_history_parser
        
        # Sample hand history text
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

        # Parse the hand history
        parser = get_hand_history_parser(hand_text)
        hh_data = parser.parse(hand_text)
        
        print("✅ HandHistoryData object created successfully!")
        print(f"Type: {type(hh_data)}")
        
        # Check if get_format_details method exists
        if hasattr(hh_data, 'get_format_details'):
            print("✅ get_format_details() method is available!")
            
            # Test the method
            try:
                format_details = hh_data.get_format_details()
                print("✅ get_format_details() executed successfully!")
                print(f"Format details: {format_details}")
                
                # Check expected structure
                expected_keys = ['game_class', 'game_variant', 'table_size']
                missing_keys = [key for key in expected_keys if key not in format_details]
                
                if missing_keys:
                    print(f"⚠️  Missing expected keys: {missing_keys}")
                else:
                    print("✅ All expected keys present in format details")
                
                # Show the details
                print("\nFormat Details Breakdown:")
                for key, value in format_details.items():
                    print(f"  {key}: {value}")
                
                return True
                
            except Exception as e:
                print(f"❌ Error calling get_format_details(): {e}")
                return False
        else:
            print("❌ get_format_details() method is NOT available")
            print("Available methods:")
            for attr in dir(hh_data):
                if not attr.startswith('_') and callable(getattr(hh_data, attr)):
                    print(f"  {attr}()")
            return False
            
    except ImportError as e:
        print(f"❌ Could not import holiday_parser: {e}")
        return False
    except Exception as e:
        print(f"❌ Error creating HandHistoryData: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_structured_format_matching():
    """Test the structured format matching with the new method."""
    print("\n=== Testing Structured Format Matching ===")
    
    try:
        from holiday_parser import get_hand_history_parser
        from scripts.db_access import DatabaseAccess
        from scripts.config import DB_PARAMS
        
        # Sample hand history
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

        # Parse the hand
        parser = get_hand_history_parser(hand_text)
        hh_data = parser.parse(hand_text)
        
        if not hasattr(hh_data, 'get_format_details'):
            print("❌ get_format_details() not available, skipping matching test")
            return False
        
        # Test rule matching
        db = DatabaseAccess(**DB_PARAMS)
        
        # Create a test rule that should match
        test_rule = {
            'game_class_pattern': 'cash',
            'game_variant_pattern': 'zoom',
            'table_size_pattern': '6-max',
            'pf_pattern': '',
            'flop_pattern': '',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': '',
            'min_stack_bb': None,
            'max_stack_bb': None,
            'game_type_pattern': '',
            'num_players': None
        }
        
        print("Testing rule matching with structured formats...")
        match_result = db._check_rule_match(test_rule, hh_data)
        print(f"Rule match result: {'✅ MATCHED' if match_result else '❌ NO MATCH'}")
        
        db.close()
        return match_result
        
    except Exception as e:
        print(f"❌ Error in structured format matching test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing get_format_details() method availability...")
    
    success1 = test_get_format_details()
    
    if success1:
        print("\n🎉 get_format_details() method is available and working!")
        success2 = test_structured_format_matching()
        
        if success2:
            print("\n🎉 Structured format matching is working correctly!")
        else:
            print("\n⚠️  Structured format matching needs attention.")
    else:
        print("\n❌ get_format_details() method is not available.")
        print("Please ensure the hpcursor project has been updated with this method.")
    
    print("\nTest completed.") 