#!/usr/bin/env python3
"""
Test script to verify that the default values are set correctly.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_defaults():
    """Test that the default values are available in the database."""
    print("=== Testing Default Values ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Check if "zoom 6-max" game profile exists
        print("\n1. Testing Game Profile 'zoom 6-max':")
        game_profiles = db.get_game_profiles()
        if "zoom 6-max" in game_profiles:
            print(f"   ✅ 'zoom 6-max' profile found")
            profile = game_profiles["zoom 6-max"]
            print(f"   Class: {profile['class']}")
            print(f"   Variant: {profile['variant']}")
            print(f"   Size: {profile['size']}")
        else:
            print(f"   ❌ 'zoom 6-max' profile not found")
            print(f"   Available profiles: {list(game_profiles.keys())}")
        
        # Test 2: Check if preflop spot "37" exists
        print("\n2. Testing Preflop Spot '37':")
        all_spots = db.get_spots_for_dropdowns()
        preflop_spots = all_spots.get('preflop', {})
        if "37" in preflop_spots:
            print(f"   ✅ Preflop spot '37' found")
            print(f"   Pattern: {preflop_spots['37']}")
        else:
            print(f"   ❌ Preflop spot '37' not found")
            print(f"   Available preflop spots: {list(preflop_spots.keys())[:10]}...")  # Show first 10
        
        # Test 3: Check filtered spots for "zoom 6-max" profile
        print("\n3. Testing Filtered Spots for 'zoom 6-max':")
        if "zoom 6-max" in game_profiles:
            filtered_spots = db.get_spots_for_dropdowns("zoom 6-max")
            preflop_filtered = filtered_spots.get('preflop', {})
            if "37" in preflop_filtered:
                print(f"   ✅ Preflop spot '37' available in filtered spots")
                print(f"   Pattern: {preflop_filtered['37']}")
            else:
                print(f"   ❌ Preflop spot '37' not available in filtered spots")
                print(f"   Available filtered spots: {list(preflop_filtered.keys())[:10]}...")
        
        print("\n=== Test completed! ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_defaults() 