#!/usr/bin/env python3
"""
Test script to verify the GTO+ running check functionality.
"""

import psutil

def is_gto_running():
    """Check if GTO+ is currently running."""
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'] and "GTO" in proc.info['name']:
                print(f"GTO+ is running: {proc.info['name']}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    print("GTO+ is not running")
    return False

if __name__ == "__main__":
    print("=== Testing GTO+ Running Check ===")
    is_gto_running()
    print("=== Test completed! ===") 