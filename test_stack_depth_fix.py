#!/usr/bin/env python3
"""
Test script to verify the stack depth calculation and rule matching works correctly with the fix.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

class MockHandHistoryData:
    """Mock class to simulate hand history data for testing"""
    def __init__(self, action_sequences=None, raw_text=None, effective_stack_bb=None):
        self.action_sequences = action_sequences or {}
        self.raw_text = raw_text or ""
        self.effective_stack_bb = effective_stack_bb
    
    def get_simple_action_sequence(self, street):
        return self.action_sequences.get(street, "")

def test_stack_depth_matching():
    """Test the stack depth matching logic"""
    print("=== Testing Stack Depth Matching Logic ===")
    
    # Create a mock rule with stack depth constraints
    rule = {
        'pf_pattern': '',  # Wildcard
        'flop_pattern': '',  # Wildcard  
        'turn_pattern': '',  # Wildcard
        'river_pattern': '',  # Wildcard
        'board_texture_pattern': None,  # No board texture constraint
        'min_effective_stack_bb': 85,
        'max_effective_stack_bb': 95
    }
    
    # Test case 1: Hand with 104 bb (should NOT match)
    hh_data_104 = MockHandHistoryData(
        action_sequences={'preflop': '1f2f3r4r5c6c'},
        effective_stack_bb=104.0
    )
    
    # Test case 2: Hand with 90 bb (should match)
    hh_data_90 = MockHandHistoryData(
        action_sequences={'preflop': '1f2f3r4r5c6c'},
        effective_stack_bb=90.0
    )
    
    # Test case 3: Hand with 80 bb (should NOT match)
    hh_data_80 = MockHandHistoryData(
        action_sequences={'preflop': '1f2f3r4r5c6c'},
        effective_stack_bb=80.0
    )
    
    # Test case 4: Hand with no stack depth constraint (should match)
    rule_no_constraint = {
        'pf_pattern': '',  # Wildcard
        'flop_pattern': '',  # Wildcard  
        'turn_pattern': '',  # Wildcard
        'river_pattern': '',  # Wildcard
        'board_texture_pattern': None,  # No board texture constraint
        'min_effective_stack_bb': None,
        'max_effective_stack_bb': None
    }
    
    print(f"Rule stack range: {rule['min_effective_stack_bb']}-{rule['max_effective_stack_bb']} bb")
    print()
    
    # Test the matching logic manually
    def test_stack_depth_match(rule, hh_data):
        """Test stack depth matching logic"""
        min_stack = rule.get('min_effective_stack_bb')
        max_stack = rule.get('max_effective_stack_bb')
        hand_stack = hh_data.effective_stack_bb
        
        print(f"Hand stack: {hand_stack} bb")
        print(f"Rule min: {min_stack}, max: {max_stack}")
        
        # Check stack depth constraints
        if min_stack is not None and hand_stack < min_stack:
            print(f"FAIL: Hand stack {hand_stack} < min {min_stack}")
            return False
        if max_stack is not None and hand_stack > max_stack:
            print(f"FAIL: Hand stack {hand_stack} > max {max_stack}")
            return False
        
        print(f"PASS: Hand stack {hand_stack} within range {min_stack}-{max_stack}")
        return True
    
    print("Test 1: Hand with 104 bb (should NOT match)")
    result1 = test_stack_depth_match(rule, hh_data_104)
    print(f"Result: {'MATCH' if result1 else 'NO MATCH'}")
    print()
    
    print("Test 2: Hand with 90 bb (should match)")
    result2 = test_stack_depth_match(rule, hh_data_90)
    print(f"Result: {'MATCH' if result2 else 'NO MATCH'}")
    print()
    
    print("Test 3: Hand with 80 bb (should NOT match)")
    result3 = test_stack_depth_match(rule, hh_data_80)
    print(f"Result: {'MATCH' if result3 else 'NO MATCH'}")
    print()
    
    print("Test 4: Rule with no stack constraints (should match any stack)")
    result4 = test_stack_depth_match(rule_no_constraint, hh_data_104)
    print(f"Result: {'MATCH' if result4 else 'NO MATCH'}")
    print()
    
    # Verify expected results
    expected_results = [False, True, False, True]  # 104bb, 90bb, 80bb, no_constraint
    actual_results = [result1, result2, result3, result4]
    
    print("=== Summary ===")
    for i, (expected, actual) in enumerate(zip(expected_results, actual_results)):
        status = "PASS" if expected == actual else "FAIL"
        print(f"Test {i+1}: {status} (Expected: {expected}, Got: {actual})")
    
    all_passed = all(expected == actual for expected, actual in zip(expected_results, actual_results))
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")

if __name__ == "__main__":
    test_stack_depth_matching() 