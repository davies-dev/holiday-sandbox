from holiday_parser.models.tree import HandHistoryTree
from holiday_parser.models.hand_data import HandHistoryData
from holiday_parser.parsers.factory import get_hand_history_parser

# Sample PokerStars hand (you can replace this with one of your own)
raw_hand = """
PokerStars Hand #250880484380:  Hold'em No Limit ($0.01/$0.02) - 2024/06/06 1:47:34 ET
Table 'Halley' 6-max Seat #1 is the button
Seat 1: Levchuga ($2.21 in chips)
Seat 2: Ximphia ($1.98 in chips)
Seat 3: 1221Vik1221 ($1.51 in chips)
Seat 4: Übermenschen ($8.02 in chips)
Seat 5: BKOOL99 ($6.12 in chips)
Seat 6: HumptyD ($2 in chips)
Ximphia: posts small blind $0.01
1221Vik1221: posts big blind $0.02
Levchuga: folds
Ximphia: folds
1221Vik1221: checks
*** FLOP *** [6c 4d 2h]
1221Vik1221: bets $0.05
*** TURN *** [6c 4d 2h] [Qs]
1221Vik1221: checks
*** RIVER *** [6c 4d 2h Qs] [Kd]
*** SHOW DOWN ***
1221Vik1221: shows [7d 8d] (high card King)
"""

# Parse the hand using the parser factory
parser = get_hand_history_parser("stars_zoom_cash_6max")  # adjust if needed
hand_data: HandHistoryData = parser.parse_hand(raw_hand)

# Build the action tree
tree = HandHistoryTree(hand_data)

print("✅ Parsed hand:")
print(f"Game Type: {hand_data.game_type}")
print(f"Streets: {list(tree.street_nodes.keys())}")
print(f"Preflop Sequence: {hand_data.pf_action_seq}")
print(f"Tree Root Action: {tree.root_node.action_type}")
print(f"Total Nodes in Tree: {len(tree.all_nodes)}")
