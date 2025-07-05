#!/usr/bin/env python3
"""
Test script to verify the flop extraction and clipboard functionality.
"""

import sys
import os
import re
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_flop_extraction():
    """Test flop extraction from hand history text."""
    print("=== Testing Flop Extraction ===")
    
    # Test cases with different hand history formats
    test_cases = [
        {
            "name": "Standard PokerStars format",
            "text": """PokerStars Zoom Hand #250961217484:  Hold'em No Limit ($0.01/$0.02) - 2024/06/10 19:21:02 ET
Table 'Halley' 6-max Seat #1 is the button
*** HOLE CARDS ***
Dealt to HumptyD [5c Qh]
*** FLOP *** [4d 8s 4c]
HumptyD: checks
*** TURN *** [4d 8s 4c] [Ah]
*** RIVER *** [4d 8s 4c Ah] [Kh]""",
            "expected": ["4d", "8s", "4c"]
        },
        {
            "name": "Different card format",
            "text": """*** FLOP *** [Jh 6d 8s]
alenastorm: checks
WB_SOH: bets $0.21""",
            "expected": ["Jh", "6d", "8s"]
        },
        {
            "name": "No flop in hand",
            "text": """PokerStars Zoom Hand #250961217484:  Hold'em No Limit ($0.01/$0.02) - 2024/06/10 19:21:02 ET
*** HOLE CARDS ***
Dealt to HumptyD [5c Qh]
HumptyD: folds""",
            "expected": []
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        
        # Extract flop using regex
        flop_match = re.search(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]', test_case['text'])
        if flop_match:
            flop_text = flop_match.group(1)
            flop_cards = [card.strip() for card in flop_text.split()]
            print(f"   Extracted: {flop_cards}")
            print(f"   Expected:  {test_case['expected']}")
            print(f"   Match:     {flop_cards == test_case['expected']}")
        else:
            print(f"   No flop found")
            print(f"   Expected:  {test_case['expected']}")
            print(f"   Match:     {[] == test_case['expected']}")

def test_clipboard_functionality():
    """Test clipboard functionality."""
    print("\n=== Testing Clipboard Functionality ===")
    
    try:
        import tkinter as tk
        
        # Create a temporary root window for clipboard access
        root = tk.Tk()
        root.withdraw()  # Hide the window
        
        # Test data
        test_flop = "4d 8s 4c"
        
        # Copy to clipboard
        root.clipboard_clear()
        root.clipboard_append(test_flop)
        
        # Read from clipboard
        clipboard_content = root.clipboard_get()
        
        print(f"Test flop:     {test_flop}")
        print(f"Clipboard:     {clipboard_content}")
        print(f"Match:         {test_flop == clipboard_content}")
        
        root.destroy()
        
    except Exception as e:
        print(f"Clipboard test failed: {e}")

if __name__ == "__main__":
    test_flop_extraction()
    test_clipboard_functionality()
    print("\n=== Test completed! ===") 