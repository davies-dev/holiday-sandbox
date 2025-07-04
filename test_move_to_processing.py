#!/usr/bin/env python3
"""
Test script to verify the move to processing functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS
from scripts.file_utils import find_gto_file_in_locations
from pathlib import Path
import shutil

def test_move_to_processing():
    """Test the move to processing functionality."""
    print("=== Testing Move to Processing Functionality ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Test 1: Get all spots with GTO+ documents
        print("\n1. Testing get_all_spots_with_profiles()...")
        spots_with_profiles = db.get_all_spots_with_profiles()
        print(f"Found {len(spots_with_profiles)} spots:")
        
        gto_spots = []
        for spot_id, spot_name, description, profile_names in spots_with_profiles:
            # Get documents for this spot
            docs = db.get_documents_for_spot(spot_id)
            for doc in docs:
                if doc['file_path'].lower().endswith(('.gto', '.gto+')):
                    gto_spots.append((spot_id, spot_name, doc))
                    break
        
        print(f"Found {len(gto_spots)} spots with GTO+ documents:")
        for spot_id, spot_name, doc in gto_spots[:3]:  # Show first 3
            print(f"  {spot_name}: {doc['file_path']}")
        if len(gto_spots) > 3:
            print(f"  ... and {len(gto_spots) - 3} more spots")
        
        # Test 2: Test file location finding
        if gto_spots:
            print("\n2. Testing file location finding...")
            test_spot = gto_spots[0]
            spot_id, spot_name, doc = test_spot
            print(f"   Testing with spot: {spot_name}")
            print(f"   Document path from DB: {doc['file_path']}")
            
            actual_path = find_gto_file_in_locations(doc['file_path'])
            if actual_path:
                print(f"   Found file at: {actual_path}")
                
                # Test 3: Check processing directory
                processing_dir = Path("C:\\@myfiles\\gtotorunwhenIleave\\")
                print(f"\n3. Testing processing directory...")
                print(f"   Processing directory: {processing_dir}")
                print(f"   Directory exists: {processing_dir.exists()}")
                
                if processing_dir.exists():
                    # List some files in processing directory
                    files = list(processing_dir.glob("*.gto*"))[:5]
                    print(f"   Found {len(files)} GTO+ files in processing directory:")
                    for file in files:
                        print(f"     {file.name}")
                
                # Test 4: Test filename prefix logic
                print(f"\n4. Testing filename prefix logic...")
                source_path = Path(actual_path)
                filename = source_path.name
                print(f"   Original filename: {filename}")
                
                if filename.startswith("0 - "):
                    dest_filename = filename
                else:
                    dest_filename = f"0 - {filename}"
                
                print(f"   Destination filename: {dest_filename}")
                dest_path = processing_dir / dest_filename
                print(f"   Would move to: {dest_path}")
                print(f"   Destination already exists: {dest_path.exists()}")
                
            else:
                print(f"   File not found in any location")
        
        print("\n=== Test completed successfully! ===")
        print("\nNote: To test actual file moving, use the 'Move to Processing' button in the UI.")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_move_to_processing() 