#!/usr/bin/env python3
"""
Debug script to test spingo hand parsing and check game_type extraction.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_spingo_parsing():
    """Test spingo hand parsing and game_type extraction."""
    print("=== Testing Spingo Hand Parsing ===")
    
    # Sample spingo hand history
    spingo_hand = """PokerStars Hand #256760112737:  Hold'em No Limit ($0.01/$0.02) - 2025/06/30 1:47:29 ET
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
        # Import the parser
        from holiday_parser import get_hand_history_parser
        
        # Parse the hand history
        parser = get_hand_history_parser(spingo_hand)
        hh_data = parser.parse(spingo_hand)
        
        print("✅ Hand parsed successfully!")
        print(f"Game Type: '{hh_data.game_type}'")
        print(f"Number of Players: {getattr(hh_data, 'number_of_players', 'N/A')}")
        
        # Check all attributes
        print("\nAll HandHistoryData attributes:")
        for attr in dir(hh_data):
            if not attr.startswith('_'):
                try:
                    value = getattr(hh_data, attr)
                    if not callable(value):
                        print(f"  {attr}: {value}")
                except Exception as e:
                    print(f"  {attr}: Error - {e}")
        
        # Test rule matching
        print(f"\n=== Testing Rule Matching ===")
        
        # Create database access
        db = DatabaseAccess(**DB_PARAMS)
        
        # Test with a spingo rule
        spingo_rule = {
            'id': 999,
            'tag_id': 1,
            'rule_description': 'Test Spingo Rule',
            'pf_pattern': '',  # wildcard
            'flop_pattern': '',  # wildcard
            'turn_pattern': '',  # wildcard
            'river_pattern': '',  # wildcard
            'board_texture': '',  # wildcard
            'min_stack_bb': None,
            'max_stack_bb': None,
            'game_type_pattern': 'spingo%',
            'num_players': 6
        }
        
        print(f"Testing rule: game_type_pattern='spingo%', num_players=6")
        match_result = db._check_rule_match(spingo_rule, hh_data)
        print(f"Rule match result: {match_result}")
        
        # Test with different patterns
        test_patterns = [
            ('spingo%', 6),
            ('spingo*', 6),
            ('*spingo*', 6),
            ('holdem%', 6),
            ('%', 6),  # wildcard
        ]
        
        print(f"\nTesting different game type patterns:")
        for pattern, players in test_patterns:
            test_rule = spingo_rule.copy()
            test_rule['game_type_pattern'] = pattern
            test_rule['num_players'] = players
            match = db._check_rule_match(test_rule, hh_data)
            print(f"  Pattern '{pattern}', players={players}: {'MATCH' if match else 'NO MATCH'}")
        
        db.close()
        
    except ImportError as e:
        print(f"❌ Could not import holiday_parser: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def check_database_spingo_hands():
    """Check what spingo hands exist in the database."""
    print("\n=== Checking Database for Spingo Hands ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Check for different game type patterns
        game_type_queries = [
            ("spingo%", "spingo%"),
            ("%spingo%", "%spingo%"),
            ("%ingo%", "%ingo%"),
            ("holdem%", "holdem%"),
        ]
        
        for pattern, query in game_type_queries:
            with db.conn.cursor() as cur:
                cur.execute("""
                    SELECT COUNT(*) as count, 
                           MIN(game_type) as sample_game_type,
                           MIN(number_of_players) as min_players,
                           MAX(number_of_players) as max_players
                    FROM hand_histories 
                    WHERE game_type LIKE %s
                """, (query,))
                result = cur.fetchone()
                
                if result:
                    count, sample_type, min_players, max_players = result
                    print(f"Pattern '{pattern}': {count} hands")
                    if count > 0:
                        print(f"  Sample game_type: '{sample_type}'")
                        print(f"  Player range: {min_players}-{max_players}")
                else:
                    print(f"Pattern '{pattern}': 0 hands")
        
        # Check all unique game types
        print(f"\nAll unique game types in database:")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT DISTINCT game_type, COUNT(*) as count
                FROM hand_histories 
                WHERE game_type IS NOT NULL
                ORDER BY count DESC
            """)
            results = cur.fetchall()
            
            for game_type, count in results:
                print(f"  '{game_type}': {count} hands")
        
        # Check for 3-player hands specifically
        print(f"\n3-player hands by game type:")
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT game_type, COUNT(*) as count
                FROM hand_histories 
                WHERE number_of_players = 3
                GROUP BY game_type
                ORDER BY count DESC
            """)
            results = cur.fetchall()
            
            for game_type, count in results:
                print(f"  '{game_type}': {count} hands")
        
    except Exception as e:
        print(f"❌ Database error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_spingo_parsing()
    check_database_spingo_hands() 