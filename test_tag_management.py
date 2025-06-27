#!/usr/bin/env python3
"""
Test script for tag management functionality in the Study Librarian application.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_tag_management():
    """Test the tag management functionality."""
    print("Testing Tag Management Functionality")
    print("=" * 50)
    
    # Initialize database connection
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Create tags
        print("\n1. Testing tag creation...")
        tags_to_create = [
            ("DelayedCBetOOP", "Delayed continuation bet out of position"),
            ("3BetBluff", "Three-bet bluff situations"),
            ("RiverBluff", "River bluff opportunities"),
            ("ValueBet", "Value betting scenarios")
        ]
        
        for tag_name, description in tags_to_create:
            success = db.create_tag(tag_name, description)
            print(f"   Created tag '{tag_name}': {'✓' if success else '✗'}")
        
        # Test 2: Get all tags
        print("\n2. Testing get all tags...")
        all_tags = db.get_all_tags()
        print(f"   Found {len(all_tags)} tags:")
        for tag_id, tag_name in all_tags:
            print(f"     ID {tag_id}: {tag_name}")
        
        # Test 3: Add a test document
        print("\n3. Testing document creation...")
        test_doc_success = db.add_study_document(
            "Test Document for Tag Management", 
            "/path/to/test/document.md",
            "Test document for tag management functionality"
        )
        print(f"   Created test document: {'✓' if test_doc_success else '✗'}")
        
        # Test 4: Get the document ID
        documents = db.get_all_study_documents()
        test_doc_id = None
        for doc_id, title, path in documents:
            if "Test Document for Tag Management" in title:
                test_doc_id = doc_id
                break
        
        if test_doc_id:
            print(f"   Test document ID: {test_doc_id}")
            
            # Test 5: Assign tags to document
            print("\n4. Testing tag assignment...")
            for tag_id, tag_name in all_tags[:2]:  # Assign first 2 tags
                success = db.assign_tag_to_document(test_doc_id, tag_id)
                print(f"   Assigned tag '{tag_name}' to document: {'✓' if success else '✗'}")
            
            # Test 6: Get tags for document
            print("\n5. Testing get tags for document...")
            doc_tags = db.get_tags_for_document(test_doc_id)
            print(f"   Document has {len(doc_tags)} tags:")
            for tag_id, tag_name in doc_tags:
                print(f"     {tag_name}")
            
            # Test 7: Remove a tag
            print("\n6. Testing tag removal...")
            if doc_tags:
                tag_to_remove_id, tag_to_remove_name = doc_tags[0]
                success = db.remove_tag_from_document(test_doc_id, tag_to_remove_id)
                print(f"   Removed tag '{tag_to_remove_name}': {'✓' if success else '✗'}")
                
                # Verify removal
                updated_doc_tags = db.get_tags_for_document(test_doc_id)
                print(f"   Document now has {len(updated_doc_tags)} tags")
        
        print("\n" + "=" * 50)
        print("Tag management test completed!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_tag_management() 