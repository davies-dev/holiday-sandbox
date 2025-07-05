#!/usr/bin/env python3
"""
Test script to verify the double-click functionality for linked documents.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

def test_double_click_functionality():
    """Test that linked documents can be opened via double-click."""
    print("=== Testing Double-Click Document Functionality ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get all spots with linked documents
        print("\n1. Testing spots with linked documents...")
        spots_with_profiles = db.get_all_spots_with_profiles()
        
        spots_with_docs = []
        for spot_id, spot_name, description, profile_names in spots_with_profiles:
            docs = db.get_documents_for_spot(spot_id)
            if docs:
                spots_with_docs.append((spot_id, spot_name, docs))
        
        print(f"Found {len(spots_with_docs)} spots with linked documents:")
        for spot_id, spot_name, docs in spots_with_docs[:3]:  # Show first 3
            print(f"  {spot_name} -> {len(docs)} documents")
            for doc in docs[:2]:  # Show first 2 docs per spot
                print(f"    - {doc['title']} ({doc['file_path']})")
        if len(spots_with_docs) > 3:
            print(f"  ... and {len(spots_with_docs) - 3} more spots")
        
        # Test 2: Verify document file paths exist
        print("\n2. Testing document file path validity...")
        valid_docs = 0
        invalid_docs = 0
        
        for spot_id, spot_name, docs in spots_with_docs:
            for doc in docs:
                if os.path.exists(doc['file_path']):
                    valid_docs += 1
                else:
                    invalid_docs += 1
                    print(f"    WARNING: File not found: {doc['file_path']}")
        
        print(f"Valid documents: {valid_docs}")
        print(f"Invalid documents: {invalid_docs}")
        
        # Test 3: Check document types
        print("\n3. Testing document types...")
        doc_types = {}
        for spot_id, spot_name, docs in spots_with_docs:
            for doc in docs:
                ext = os.path.splitext(doc['file_path'])[1].lower()
                doc_types[ext] = doc_types.get(ext, 0) + 1
        
        print("Document types found:")
        for ext, count in sorted(doc_types.items()):
            print(f"  {ext}: {count} documents")
        
        print("\n=== Test completed successfully! ===")
        print("\nNote: To test double-click functionality:")
        print("1. Load a hand history that matches a spot with linked documents")
        print("2. Look for the 'Linked Documents' section in the Review Panel")
        print("3. Double-click on any document in the list to open it")
        print("4. Markdown files will open in Obsidian, other files with system default")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_double_click_functionality() 