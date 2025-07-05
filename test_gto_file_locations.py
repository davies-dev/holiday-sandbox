#!/usr/bin/env python3
"""
Test script to verify GTO file location search functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.file_utils import find_gto_file_in_locations

def test_gto_file_locations():
    """Test the GTO file location search functionality."""
    print("=== Testing GTO File Location Search ===")
    
    # Test cases with different file paths
    test_files = [
        "6 max 37 btn v bb 2.5x.gto",
        "6 max 80 btn 3b v  hj.gto", 
        "6 max 19 bb flat v sb 3x.gto",
        "nonexistent_file.gto"
    ]
    
    for filename in test_files:
        print(f"\nTesting: {filename}")
        found_path = find_gto_file_in_locations(filename)
        
        if found_path:
            print(f"  ✅ Found at: {found_path}")
            print(f"  📁 Directory: {os.path.dirname(found_path)}")
        else:
            print(f"  ❌ Not found in any location")
    
    print("\n=== Test completed! ===")
    print("\nNote: The double-click functionality now searches multiple locations for GTO files:")
    print("1. Original path from database")
    print("2. Processing directory (C:\\@myfiles\\gtotorunwhenIleave\\)")
    print("3. Other common GTO file locations")

if __name__ == "__main__":
    test_gto_file_locations() 