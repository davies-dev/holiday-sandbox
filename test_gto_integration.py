#!/usr/bin/env python3
"""
Test script for GTO+ integration
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from db_access import DatabaseAccess
from config import DB_PARAMS

def test_gto_integration():
    """Test the GTO+ database integration"""
    print("Testing GTO+ Integration...")
    
    # Create database connection
    db = DatabaseAccess(**DB_PARAMS)
    
    # Test inserting a mapping
    print("\n1. Testing insert_gto_mapping...")
    success = db.insert_gto_mapping(
        state_name="37",
        game_type="zoom_cash_6max",
        file_path="C:\\@myfiles\\30000 Poker\\GAMES\\6 max\\6 max MPT GTO snap shot 20210114\\6 max 37 btn v bb 2.5x.gto",
        description="37 - btn v bb 2.5x"
    )
    print(f"Insert result: {'Success' if success else 'Failed'}")
    
    # Test getting file path
    print("\n2. Testing get_gto_file_path...")
    file_path = db.get_gto_file_path("37", "zoom_cash_6max")
    print(f"File path for state 37: {file_path}")
    
    # Test getting all mappings
    print("\n3. Testing get_all_gto_mappings...")
    mappings = db.get_all_gto_mappings()
    print(f"Total mappings: {len(mappings)}")
    for mapping in mappings:
        print(f"  - {mapping['state_name']}: {mapping['description']}")
    
    # Test getting game types
    print("\n4. Testing get_game_types...")
    game_types = db.get_game_types()
    print(f"Game types: {game_types}")
    
    # Test deleting a mapping
    print("\n5. Testing delete_gto_mapping...")
    success = db.delete_gto_mapping("37", "zoom_cash_6max")
    print(f"Delete result: {'Success' if success else 'Failed'}")
    
    # Verify deletion
    mappings_after = db.get_all_gto_mappings()
    print(f"Mappings after deletion: {len(mappings_after)}")
    
    db.close()
    print("\nGTO+ Integration test completed!")

if __name__ == "__main__":
    test_gto_integration() 