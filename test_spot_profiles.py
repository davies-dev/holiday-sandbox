#!/usr/bin/env python3
"""
Test script to verify the spot-profile linking functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_spot_profiles():
    """Test the spot-profile linking functionality."""
    print("=== Testing Spot-Profile Linking Functionality ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get all spots with profiles
        print("\n1. Testing get_all_spots_with_profiles()...")
        spots_with_profiles = db.get_all_spots_with_profiles()
        print(f"Found {len(spots_with_profiles)} spots:")
        for spot_id, spot_name, description, profile_names in spots_with_profiles[:5]:  # Show first 5
            profile_text = f" -> {', '.join(profile_names)}" if profile_names else " -> (no profiles)"
            print(f"  {spot_name}{profile_text}")
        if len(spots_with_profiles) > 5:
            print(f"  ... and {len(spots_with_profiles) - 5} more spots")
        
        # Test 2: Get all game profiles with IDs
        print("\n2. Testing get_all_game_profiles_with_ids()...")
        profiles_with_ids = db.get_all_game_profiles_with_ids()
        print(f"Found {len(profiles_with_ids)} game profiles:")
        for profile_id, profile_name in profiles_with_ids:
            print(f"  {profile_id}: {profile_name}")
        
        # Test 3: Test filtered spot fetching
        print("\n3. Testing filtered spot fetching...")
        
        # Test with a specific profile
        if profiles_with_ids:
            test_profile = profiles_with_ids[0][1]  # Use first profile
            print(f"\n   Testing with '{test_profile}' profile:")
            filtered_spots = db.get_spots_for_dropdowns(test_profile)
            print(f"   Found {len(filtered_spots.get('preflop', {}))} preflop spots for {test_profile}")
            for spot_name, pattern in list(filtered_spots.get('preflop', {}).items())[:3]:  # Show first 3
                print(f"     {spot_name}: {pattern}")
            if len(filtered_spots.get('preflop', {})) > 3:
                print(f"     ... and {len(filtered_spots.get('preflop', {})) - 3} more")
        
        # Test 4: Test unfiltered spot fetching
        print("\n4. Testing unfiltered spot fetching...")
        all_spots = db.get_spots_for_dropdowns()
        print(f"   Found {len(all_spots.get('preflop', {}))} total preflop spots (unfiltered)")
        
        print("\n=== Test completed successfully! ===")
        print("\nNote: To test profile assignment, use the 'Manage Spot Profiles' button in the UI.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_spot_profiles() 