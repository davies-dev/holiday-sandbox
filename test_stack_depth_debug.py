#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_stack_depth_calculation():
    """Test how effective stack is calculated from hand history"""
    
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

    print("=== Stack Depth Calculation Test ===")
    
    # Extract stack information
    import re
    
    # Find all seat entries with stack amounts
    seat_pattern = r'Seat \d+: ([^(]+) \(\$([\d.]+) in chips\)'
    seats = re.findall(seat_pattern, hand_text)
    
    print("All players and their stacks:")
    for player, stack in seats:
        print(f"  {player.strip()}: ${stack}")
    
    # Find the main players (those who actually played)
    # From the action, we can see cowpop3 and HumptyD were the main players
    main_players = ['cowpop3', 'HumptyD']
    
    print(f"\nMain players: {main_players}")
    
    # Get their stacks
    player_stacks = {}
    for player, stack in seats:
        player_name = player.strip()
        if player_name in main_players:
            player_stacks[player_name] = float(stack)
    
    print("Main player stacks:")
    for player, stack in player_stacks.items():
        print(f"  {player}: ${stack}")
    
    # Calculate effective stack (smaller of the two)
    if len(player_stacks) >= 2:
        effective_stack = min(player_stacks.values())
        print(f"\nEffective stack: ${effective_stack}")
        
        # Calculate big blinds
        # Extract blind level from hand text
        blind_match = re.search(r'No Limit \(\$([\d.]+)/\$([\d.]+)\)', hand_text)
        if blind_match:
            small_blind = float(blind_match.group(1))
            big_blind = float(blind_match.group(2))
            print(f"Blind level: ${small_blind}/${big_blind}")
            
            effective_stack_bb = effective_stack / big_blind
            print(f"Effective stack in big blinds: {effective_stack_bb}")
            
            # Test against the rule (85-95 bb)
            min_stack = 85
            max_stack = 95
            print(f"\nRule range: {min_stack}-{max_stack} bb")
            print(f"Hand effective stack: {effective_stack_bb} bb")
            
            if min_stack <= effective_stack_bb <= max_stack:
                print("✅ Hand SHOULD match the rule")
            else:
                print("❌ Hand should NOT match the rule")
        else:
            print("Could not extract blind level from hand text")
    else:
        print("Could not identify main players")

def test_rule_matching():
    """Test the actual rule matching logic"""
    print("\n=== Rule Matching Test ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    # Get all rules to see what's configured
    try:
        with db.conn.cursor() as cur:
            cur.execute("""
                SELECT id, rule_description, min_effective_stack_bb, max_effective_stack_bb
                FROM study_tag_rules
                WHERE min_effective_stack_bb IS NOT NULL OR max_effective_stack_bb IS NOT NULL
            """)
            stack_rules = cur.fetchall()
        
        print("Rules with stack depth constraints:")
        for rule_id, desc, min_stack, max_stack in stack_rules:
            print(f"  Rule {rule_id}: '{desc}' - Stack: {min_stack}-{max_stack} bb")
            
    except Exception as e:
        print(f"Error querying rules: {e}")

if __name__ == "__main__":
    test_stack_depth_calculation()
    test_rule_matching() 