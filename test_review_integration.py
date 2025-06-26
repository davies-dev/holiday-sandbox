#!/usr/bin/env python3
"""
Test script for Review System integration
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from db_access import DatabaseAccess
from config import DB_PARAMS

def test_review_integration():
    """Test the Review System database integration"""
    print("Testing Review System Integration...")
    
    # Create database connection
    db = DatabaseAccess(**DB_PARAMS)
    
    # Test getting or creating review data
    print("\n1. Testing get_or_create_review_data...")
    review_data = db.get_or_create_review_data(12345)
    print(f"Review data: {review_data}")
    
    # Test updating review status
    print("\n2. Testing update_review_status...")
    success = db.update_review_status(12345, "waiting_on_gto")
    print(f"Update status result: {'Success' if success else 'Failed'}")
    
    # Test adding a note
    print("\n3. Testing add_note_for_hand...")
    test_note_path = "C:/test/Hand_12345_20231201_120000.md"
    success = db.add_note_for_hand(12345, test_note_path)
    print(f"Add note result: {'Success' if success else 'Failed'}")
    
    # Test getting notes for hand
    print("\n4. Testing get_notes_for_hand...")
    notes = db.get_notes_for_hand(12345)
    print(f"Notes for hand 12345: {len(notes)} found")
    for note_path, created_at in notes:
        print(f"  - {note_path}: {created_at}")
    
    # Test deleting a note
    print("\n5. Testing delete_note_for_hand...")
    success = db.delete_note_for_hand(12345, test_note_path)
    print(f"Delete note result: {'Success' if success else 'Failed'}")
    
    # Verify deletion
    notes_after = db.get_notes_for_hand(12345)
    print(f"Notes after deletion: {len(notes_after)}")
    
    db.close()
    print("\nReview System Integration test completed!")

if __name__ == "__main__":
    test_review_integration() 