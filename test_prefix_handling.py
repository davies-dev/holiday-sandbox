#!/usr/bin/env python3
"""
Test script to verify GTO file prefix handling, especially for processed directory.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.file_utils import (
    find_gto_file_in_locations, normalize_gto_filename, 
    get_gto_storage_path, move_gto_file_to_processed
)
from scripts.config import (
    GTO_SNAPSHOT_PATH, GTO_PROCESSING_PATH, GTO_RUNNING_PATH, 
    GTO_PRIORITY_PATH, GTO_PROCESSED_PATH, GTO_RUNNING_PREFIX, 
    GTO_PRIORITY_PREFIX_PATTERN
)

def test_prefix_handling():
    """Test the GTO file prefix handling functionality."""
    print("=== Testing GTO File Prefix Handling ===")
    
    # Test 1: Configuration paths
    print("\n1. Testing configuration paths...")
    print(f"   Snapshot path: {GTO_SNAPSHOT_PATH}")
    print(f"   Processing path: {GTO_PROCESSING_PATH}")
    print(f"   Running path: {GTO_RUNNING_PATH}")
    print(f"   Priority path: {GTO_PRIORITY_PATH}")
    print(f"   Processed path: {GTO_PROCESSED_PATH}")
    print(f"   Running prefix: {GTO_RUNNING_PREFIX}")
    print(f"   Priority pattern: {GTO_PRIORITY_PREFIX_PATTERN}")
    
    # Test 2: Filename normalization
    print("\n2. Testing filename normalization...")
    test_filenames = [
        "6 max 37 btn v bb 2.5x.gto",
        "1.5 - 6 max 37 btn v bb 2.5x.gto",
        "1.11 - 73 gto blah blah.gto",
        "0 - 6 max 80 btn 3b v hj.gto"
    ]
    
    for filename in test_filenames:
        normalized = normalize_gto_filename(filename)
        print(f"   '{filename}' -> '{normalized}'")
    
    # Test 3: Storage path handling
    print("\n3. Testing storage path handling...")
    test_paths = [
        "C:/@myfiles/gtotorunwhenIleave/1.5 - 6 max 37 btn v bb 2.5x.gto",
        "C:/@myfiles/gtotorunwhenIleave/0 - 6 max 80 btn 3b v hj.gto",
        "C:/@myfiles/30000 Poker/GAMES/6 max/6 max MPT GTO snap shot 20210114/6 max 19 bb flat v sb 3x.gto"
    ]
    
    for file_path in test_paths:
        storage_path = get_gto_storage_path(file_path)
        print(f"   '{file_path}' -> '{storage_path}'")
    
    # Test 4: File location search
    print("\n4. Testing file location search...")
    test_search_files = [
        "6 max 37 btn v bb 2.5x.gto",
        "6 max 80 btn 3b v hj.gto",
        "6 max 19 bb flat v sb 3x.gto"
    ]
    
    for filename in test_search_files:
        found_path = find_gto_file_in_locations(filename)
        if found_path:
            print(f"   Found '{filename}' at: {found_path}")
        else:
            print(f"   Not found: {filename}")
    
    # Test 5: Move to processed simulation
    print("\n5. Testing move to processed logic...")
    test_move_files = [
        "0 - 6 max 37 btn v bb 2.5x.gto",
        "6 max 80 btn 3b v hj.gto",
        "1.5 - 6 max 19 bb flat v sb 3x.gto"
    ]
    
    for filename in test_move_files:
        # Simulate what the destination filename would be
        if filename.startswith("0 - "):
            dest_filename = filename[4:]  # Remove "0 - " prefix
        else:
            dest_filename = filename
        
        print(f"   '{filename}' would move to processed as: '{dest_filename}'")
    
    print("\n=== Test completed! ===")
    print("\nNote: The move_gto_file_to_processed() function is available for actual file operations.")
    print("It will automatically remove '0 - ' prefixes when moving files to processed directory.")
    
    # Test 6: Simulate document addition through UI
    print("\n6. Testing document addition simulation...")
    test_ui_files = [
        "C:/@myfiles/gtotorunwhenIleave/0 - test 0000.gto",
        "C:/@myfiles/gtotorunwhenIleave/0 - test torun 0001.gto",
        "C:/@myfiles/gtotorunwhenIleave/1.2 - testing  proc 1p2.gto"
    ]
    
    for file_path in test_ui_files:
        storage_path = get_gto_storage_path(file_path)
        print(f"   UI adds '{file_path}' -> DB stores as '{storage_path}'")
    
    print("\n=== All tests completed! ===")

if __name__ == "__main__":
    test_prefix_handling() 