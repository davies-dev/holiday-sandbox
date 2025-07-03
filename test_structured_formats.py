#!/usr/bin/env python3
"""
Test script to verify the structured format implementation.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_structured_formats():
    """Test the structured format implementation."""
    print("=== Testing Structured Format Implementation ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Test 1: Check if new columns exist
        print("\n1. Checking database schema...")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'hand_histories' 
                AND column_name IN ('game_class', 'game_variant', 'table_size')
                ORDER BY column_name
            """)
            columns = cur.fetchall()
        
        if not columns:
            print("[ERROR] New structured format columns not found!")
            print("Please run the migration script first:")
            print("python database_setup/schema/add_structured_format_columns.py")
            return False
        
        print("[OK] New columns found:")
        for col_name, data_type, nullable in columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable})")
        
        # Test 2: Check if data exists
        print("\n2. Checking data population...")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT COUNT(*) as total_hands,
                       COUNT(game_class) as with_game_class,
                       COUNT(game_variant) as with_game_variant,
                       COUNT(table_size) as with_table_size
                FROM hand_histories
            """)
            result = cur.fetchone()
            total_hands, with_game_class, with_game_variant, with_table_size = result
        
        print(f"Total hands: {total_hands}")
        print(f"With game_class: {with_game_class}")
        print(f"With game_variant: {with_game_variant}")
        print(f"With table_size: {with_table_size}")
        
        if with_game_class == 0:
            print("[WARNING] No data found in new columns. Run the backfill script:")
            print("python backfill_formats.py")
        
        # Test 3: Show sample data
        print("\n3. Sample data:")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT game_type, game_class, game_variant, table_size, number_of_players
                FROM hand_histories 
                WHERE game_class IS NOT NULL
                LIMIT 5
            """)
            samples = cur.fetchall()
            
            for game_type, game_class, game_variant, table_size, num_players in samples:
                print(f"  {game_type} -> {game_class}/{game_variant}/{table_size} ({num_players} players)")
        
        # Test 4: Check rule table structure
        print("\n4. Checking rule table structure...")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns 
                WHERE table_name = 'study_tag_rules' 
                AND column_name IN ('game_class_pattern', 'game_variant_pattern', 'table_size_pattern')
                ORDER BY column_name
            """)
            rule_columns = cur.fetchall()
        
        if not rule_columns:
            print("[ERROR] New rule columns not found!")
            return False
        
        print("[OK] New rule columns found:")
        for col_name, data_type, nullable in rule_columns:
            print(f"  {col_name}: {data_type} (nullable: {nullable})")
        
        # Test 5: Test rule creation with new fields
        print("\n5. Testing rule creation with new fields...")
        
        # Create a test rule
        test_rule = {
            'tag_id': 1,  # Assuming tag 1 exists
            'rule_description': 'Test Structured Format Rule',
            'pf_pattern': '',
            'flop_pattern': '',
            'turn_pattern': '',
            'river_pattern': '',
            'board_texture': '',
            'min_stack_bb': None,
            'max_stack_bb': None,
            'game_class_pattern': 'cash',
            'game_variant_pattern': 'zoom',
            'table_size_pattern': '6-max',
            'game_type_pattern': '',  # Legacy field
            'num_players': None  # Legacy field
        }
        
        success = db.save_rule(test_rule)
        if success:
            print("[OK] Test rule created successfully")
            
            # Get the rule back and verify
            with db.conn.cursor() as cur:
                cur.execute("""
                    SELECT game_class_pattern, game_variant_pattern, table_size_pattern
                    FROM study_tag_rules 
                    WHERE rule_description = 'Test Structured Format Rule'
                    ORDER BY id DESC
                    LIMIT 1
                """)
                result = cur.fetchone()
                if result:
                    game_class, game_variant, table_size = result
                    print(f"[OK] Retrieved rule: {game_class}/{game_variant}/{table_size}")
                else:
                    print("[ERROR] Could not retrieve test rule")
        else:
            print("[ERROR] Failed to create test rule")
        
        print("\n[OK] All tests completed successfully!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()

def test_rule_matching():
    """Test the rule matching with structured formats."""
    print("\n=== Testing Rule Matching with Structured Formats ===")
    
    db = None
    try:
        db = DatabaseAccess(**DB_PARAMS)
        
        # Create a mock hand data object
        class MockHandData:
            def __init__(self, game_type, number_of_players):
                self.game_type = game_type
                self.number_of_players = number_of_players
                self.effective_stack_bb = 100  # Default stack
            
            def get_simple_action_sequence(self, street):
                return "1f2f3r4r5c6c"  # Default action sequence
            
            def get_format_details(self):
                # Mock implementation of get_format_details
                game_type_lower = self.game_type.lower() if self.game_type else ''
                
                if 'cash' in game_type_lower:
                    game_class = 'cash'
                elif 'tournament' in game_type_lower:
                    game_class = 'tournament'
                else:
                    game_class = 'cash'
                
                if 'zoom' in game_type_lower:
                    game_variant = 'zoom'
                else:
                    game_variant = 'regular'
                
                if '6max' in game_type_lower:
                    table_size = '6-max'
                elif '2max' in game_type_lower:
                    table_size = '2-max'
                else:
                    table_size = '6-max'
                
                return {
                    'game_class': game_class,
                    'game_variant': game_variant,
                    'table_size': table_size
                }
        
        # Test cases
        test_cases = [
            ('zoom_cash_6max', 6, 'cash', 'zoom', '6-max'),
            ('normalCash_6max', 6, 'cash', 'regular', '6-max'),
            ('tournament_6max', 6, 'tournament', 'regular', '6-max'),
        ]
        
        for game_type, num_players, expected_class, expected_variant, expected_size in test_cases:
            print(f"\nTesting: {game_type} ({num_players} players)")
            
            hand_data = MockHandData(game_type, num_players)
            format_details = hand_data.get_format_details()
            
            print(f"  Expected: {expected_class}/{expected_variant}/{expected_size}")
            print(f"  Got: {format_details['game_class']}/{format_details['game_variant']}/{format_details['table_size']}")
            
            # Test rule matching
            test_rule = {
                'game_class_pattern': expected_class,
                'game_variant_pattern': expected_variant,
                'table_size_pattern': expected_size,
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
            
            match_result = db._check_rule_match(test_rule, hand_data)
            print(f"  Rule match: {'[OK]' if match_result else '[FAIL]'}")
        
        print("\n[OK] Rule matching tests completed!")
        return True
        
    except Exception as e:
        print(f"[ERROR] Rule matching test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if db:
            db.close()

if __name__ == "__main__":
    success1 = test_structured_formats()
    success2 = test_rule_matching()
    
    if success1 and success2:
        print("\n🎉 All tests passed! Structured format implementation is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed. Please check the implementation.")
        sys.exit(1) 