#!/usr/bin/env python3
"""
Test script for Obsidian URI construction
"""
import os
import urllib.parse

def test_obsidian_uri():
    """Test the Obsidian URI construction"""
    
    # Configuration (same as in ReviewPanel)
    OBSIDIAN_VAULT_PATH = "C:/projects/hh-explorer-vault"
    OBSIDIAN_VAULT_NAME = "hh-explorer-vault"
    
    # Test note path
    test_note_path = os.path.join(OBSIDIAN_VAULT_PATH, "HandNotes", "Hand_12345_20231201_120000.md")
    
    print("Testing Obsidian URI construction...")
    print(f"Vault path: {OBSIDIAN_VAULT_PATH}")
    print(f"Vault name: {OBSIDIAN_VAULT_NAME}")
    print(f"Test note path: {test_note_path}")
    
    # Get the path of the note relative to the vault's root directory
    relative_path = os.path.relpath(test_note_path, OBSIDIAN_VAULT_PATH)
    print(f"Relative path: {relative_path}")
    
    # URL-encode the path to handle spaces and special characters
    encoded_path = urllib.parse.quote(relative_path.replace(os.sep, '/')) # Ensure forward slashes
    print(f"Encoded path: {encoded_path}")
    
    # Construct the final URI
    obsidian_uri = f"obsidian://open?vault={OBSIDIAN_VAULT_NAME}&file={encoded_path}"
    print(f"Obsidian URI: {obsidian_uri}")
    
    # Test if the vault directory exists
    if os.path.exists(OBSIDIAN_VAULT_PATH):
        print(f"✅ Vault directory exists: {OBSIDIAN_VAULT_PATH}")
    else:
        print(f"❌ Vault directory does not exist: {OBSIDIAN_VAULT_PATH}")
    
    # Test if HandNotes subdirectory exists
    handnotes_dir = os.path.join(OBSIDIAN_VAULT_PATH, "HandNotes")
    if os.path.exists(handnotes_dir):
        print(f"✅ HandNotes directory exists: {handnotes_dir}")
    else:
        print(f"❌ HandNotes directory does not exist: {handnotes_dir}")
    
    print("\nTo test the URI, you can:")
    print("1. Copy the URI above")
    print("2. Paste it in your browser address bar")
    print("3. It should open Obsidian and navigate to the note")
    print("4. If Obsidian is not installed or the vault doesn't exist, you'll get an error")

if __name__ == "__main__":
    test_obsidian_uri() 