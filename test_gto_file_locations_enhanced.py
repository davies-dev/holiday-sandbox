#!/usr/bin/env python3
"""
Test script to verify the enhanced GTO file location system with priority prefixes.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.file_utils import find_gto_file_in_locations, normalize_gto_filename, get_gto_storage_path
from scripts.config import (
    GTO_SNAPSHOT_PATH, GTO_PROCESSING_PATH, GTO_RUNNING_PATH, 
    GTO_PRIORITY_PATH, GTO_PROCESSED_PATH, GTO_RUNNING_PREFIX, 
    GTO_PRIORITY_PREFIX_PATTERN
)

def test_gto_file_locations():
    """Test the enhanced GTO file location system."""
    print("=== Testing Enhanced GTO File Location System ===")
    
    # Test 1: Configuration paths
    print("\n1. Testing configuration paths...")
    print(f"   Snapshot path: {GTO_SNAPSHOT_PATH}")
    print(f"   Processing path: {GTO_PROCESSING_PATH}")
    print(f"   Running path: {GTO_RUNNING_PATH}")
    print(f"   Priority path: {GTO_PRIORITY_PATH}")
    print(f"   Processed path: {GTO_PROCESSED_PATH}")
    print(f"   Running prefix: '{GTO_RUNNING_PREFIX}'")
    print(f"   Priority pattern: '{GTO_PRIORITY_PREFIX_PATTERN}'")
    
    # Test 2: Filename normalization
    print("\n2. Testing filename normalization...")
    test_filenames = [
        "6 max 37 btn v bb 2.5x.gto",
        "1.5 - 6 max 37 btn v bb 2.5x.gto",
        "1.11 - 6 max 80 btn 3b v hj.gto",
        "0 - 6 max 19 bb flat v sb 3x.gto",
        "1.2 - 6 max 73 btn v bb 3x.gto"
    ]
    
    for filename in test_filenames:
        normalized = normalize_gto_filename(filename)
        print(f"   '{filename}' -> '{normalized}'")
    
    # Test 3: Storage path generation
    print("\n3. Testing storage path generation...")
    for filename in test_filenames:
        storage_path = get_gto_storage_path(filename)
        print(f"   '{filename}' -> '{storage_path}'")
    
    # Test 4: File location search
    print("\n4. Testing file location search...")
    test_files = [
        "6 max 37 btn v bb 2.5x.gto",
        "6 max 80 btn 3b v hj.gto",
        "6 max 19 bb flat v sb 3x.gto"
    ]
    
    for filename in test_files:
        print(f"\n   Searching for: {filename}")
        found_path = find_gto_file_in_locations(filename)
        if found_path:
            print(f"     Found at: {found_path}")
        else:
            print(f"     Not found in any location")
    
    # Test 5: Priority prefix detection
    print("\n5. Testing priority prefix detection...")
    import re
    priority_pattern = re.compile(GTO_PRIORITY_PREFIX_PATTERN)
    
    test_priority_files = [
        "1.1 - test.gto",
        "1.5 - test.gto", 
        "1.11 - test.gto",
        "1.99 - test.gto",
        "0 - test.gto",
        "test.gto",
        "2.1 - test.gto"
    ]
    
    for filename in test_priority_files:
        is_priority = bool(priority_pattern.match(filename))
        print(f"   '{filename}' -> Priority: {is_priority}")
    
    print("\n=== Enhanced GTO file location test completed! ===")

if __name__ == "__main__":
    test_gto_file_locations() 