#!/usr/bin/env python3
"""
Test script to verify the game profiles functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_game_profiles():
    """Test the game profiles functionality."""
    print("=== Testing Game Profiles Functionality ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get all game profiles
        print("\n1. Testing get_game_profiles()...")
        profiles = db.get_game_profiles()
        print(f"Found {len(profiles)} game profiles:")
        for name, details in profiles.items():
            print(f"  {name}: {details}")
        
        # Test 2: Test filtered spot fetching
        print("\n2. Testing spot fetching...")
        
        # Test with all spots (no filtering)
        print("\n   Testing spot fetching (no filtering):")
        all_spots = db.get_spots_for_dropdowns()
        print(f"   Found {len(all_spots.get('preflop', {}))} preflop spots total")
        for spot_name, pattern in list(all_spots.get('preflop', {}).items())[:5]:  # Show first 5
            print(f"     {spot_name}: {pattern}")
        if len(all_spots.get('preflop', {})) > 5:
            print(f"     ... and {len(all_spots.get('preflop', {})) - 5} more")
        
        print(f"   Found {len(all_spots.get('postflop', {}))} postflop spots total")
        for spot_name, pattern in list(all_spots.get('postflop', {}).items())[:5]:  # Show first 5
            print(f"     {spot_name}: {pattern}")
        if len(all_spots.get('postflop', {})) > 5:
            print(f"     ... and {len(all_spots.get('postflop', {})) - 5} more")
        
        print("\n=== Test completed successfully! ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_game_profiles() 