#!/usr/bin/env python3
"""
Test script to verify document removal functionality in the Study Librarian application.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_document_removal():
    """Test the document removal functionality."""
    print("=== Testing Document Removal Functionality ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get initial document count
        print("\n1. Testing initial document count...")
        initial_docs = db.get_all_study_documents()
        print(f"   Found {len(initial_docs)} documents initially")
        
        # Test 2: Add a test document
        print("\n2. Testing document creation...")
        test_title = "Test Document for Removal"
        test_path = "/path/to/test/removal_document.md"
        test_source = "Test document for removal functionality"
        
        success = db.add_study_document(test_title, test_path, test_source)
        print(f"   Created test document: {'✓' if success else '✗'}")
        
        # Test 3: Verify document was added
        print("\n3. Testing document verification...")
        all_docs = db.get_all_study_documents()
        test_doc_id = None
        for doc_id, title, path in all_docs:
            if title == test_title:
                test_doc_id = doc_id
                break
        
        if test_doc_id:
            print(f"   Test document found with ID: {test_doc_id}")
            
            # Test 4: Create a test tag and assign it
            print("\n4. Testing tag assignment...")
            tag_success = db.create_tag("TestTagForRemoval", "Test tag for document removal")
            print(f"   Created test tag: {'✓' if tag_success else '✗'}")
            
            if tag_success:
                # Get the tag ID
                all_tags = db.get_all_tags()
                test_tag_id = None
                for tag_id, tag_name in all_tags:
                    if tag_name == "TestTagForRemoval":
                        test_tag_id = tag_id
                        break
                
                if test_tag_id:
                    # Assign tag to document
                    assign_success = db.assign_tag_to_document(test_doc_id, test_tag_id)
                    print(f"   Assigned tag to document: {'✓' if assign_success else '✗'}")
                    
                    # Verify tag assignment
                    doc_tags = db.get_tags_for_document(test_doc_id)
                    print(f"   Document has {len(doc_tags)} tags before removal")
            
            # Test 5: Remove the document
            print("\n5. Testing document removal...")
            remove_success = db.delete_study_document(test_doc_id)
            print(f"   Removed test document: {'✓' if remove_success else '✗'}")
            
            # Test 6: Verify document was removed
            print("\n6. Testing removal verification...")
            final_docs = db.get_all_study_documents()
            doc_still_exists = any(doc_id == test_doc_id for doc_id, title, path in final_docs)
            print(f"   Document still exists: {'✗' if doc_still_exists else '✓'}")
            
            # Test 7: Verify tag associations were also removed (cascade)
            print("\n7. Testing cascade removal...")
            if test_tag_id:
                # Try to get tags for the deleted document
                remaining_tags = db.get_tags_for_document(test_doc_id)
                print(f"   Remaining tag associations: {len(remaining_tags)} (should be 0)")
            
            # Test 8: Verify final document count
            print(f"\n8. Final document count: {len(final_docs)} (should be {len(initial_docs)})")
            
        else:
            print("   ✗ Test document not found after creation")
        
        print("\n=== Document removal test completed! ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_document_removal() 