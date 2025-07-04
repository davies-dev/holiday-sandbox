#!/usr/bin/env python3
"""
Test script to verify the improved file lock detection functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS
from scripts.file_utils import find_gto_file_in_locations
from pathlib import Path
import psutil

def test_file_lock_detection():
    """Test the file lock detection functionality."""
    print("=== Testing File Lock Detection ===")
    
    db = DatabaseAccess(**DB_PARAMS)
    
    try:
        # Get a GTO+ file to test with
        spots_with_profiles = db.get_all_spots_with_profiles()
        gto_spots = []
        for spot_id, spot_name, description, profile_names in spots_with_profiles:
            docs = db.get_documents_for_spot(spot_id)
            for doc in docs:
                if doc['file_path'].lower().endswith(('.gto', '.gto+')):
                    gto_spots.append((spot_id, spot_name, doc))
                    break
        
        if not gto_spots:
            print("No GTO+ files found to test with.")
            return
        
        # Test with the first GTO+ file
        test_spot = gto_spots[0]
        spot_id, spot_name, doc = test_spot
        print(f"\nTesting with spot: {spot_name}")
        print(f"Document path from DB: {doc['file_path']}")
        
        actual_path = find_gto_file_in_locations(doc['file_path'])
        if not actual_path:
            print("File not found in any location.")
            return
        
        print(f"Found file at: {actual_path}")
        
        # Test file lock detection
        print(f"\n=== Testing File Lock Detection ===")
        normalized_actual_path = os.path.normpath(actual_path).lower()
        print(f"Normalized path: {normalized_actual_path}")
        
        file_is_open = False
        open_processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'exe']):
            try:
                open_files = proc.open_files()
                for file_info in open_files:
                    normalized_open_path = os.path.normpath(file_info.path).lower()
                    if normalized_actual_path == normalized_open_path:
                        file_is_open = True
                        open_processes.append(f"{proc.info['name']} (PID: {proc.info['pid']})")
                        print(f"File is open in process: {proc.info['name']} (PID: {proc.info['pid']})")
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
            except Exception as e:
                print(f"Error checking process {proc.info.get('name', 'unknown')}: {e}")
                continue
        
        if file_is_open:
            print(f"File is currently open in {len(open_processes)} process(es):")
            for proc in open_processes:
                print(f"  - {proc}")
        else:
            print("File is not open in any application")
        
        # Test file access
        print(f"\n=== Testing File Access ===")
        source_path = Path(actual_path)
        try:
            with open(source_path, 'rb') as test_file:
                print("File access test: SUCCESS - File can be opened for reading")
        except PermissionError:
            print("File access test: FAILED - Permission denied")
        except Exception as e:
            print(f"File access test: FAILED - {e}")
        
        print("\n=== Test completed! ===")
        
    except Exception as e:
        print(f"Error during testing: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_file_lock_detection() 