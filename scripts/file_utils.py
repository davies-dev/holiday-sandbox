import re
from pathlib import Path
from scripts.config import (
    GTO_SNAPSHOT_PATH, GTO_PROCESSING_PATH, GTO_RUNNING_PATH, 
    GTO_PRIORITY_PATH, GTO_PROCESSED_PATH, GTO_RUNNING_PREFIX, 
    GTO_PRIORITY_PREFIX_PATTERN
)

def find_gto_file_in_locations(original_path):
    """
    Search for a GTO+ file in multiple possible locations with priority order.
    Returns the actual path where the file was found, or None if not found.
    
    Search order (priority):
    1. Snapshot directory (original location)
    2. Processing directory (no prefix)
    3. GTO+ running directory (with "0 - " prefix)
    4. Priority queue directory (with "1.x - " prefix)
    5. Processed directory (with "1.x - " prefix, no prefix, or '0 - ' prefix)
    """
    import re
    original_path = Path(original_path)
    filename = original_path.name
    search_paths = []

    # 1. Snapshot directory (highest priority - original location)
    if GTO_SNAPSHOT_PATH.exists():
        snapshot_path = GTO_SNAPSHOT_PATH / filename
        search_paths.append(snapshot_path)

    # 2. Processing directory (no prefix)
    if GTO_PROCESSING_PATH.exists():
        processing_path = GTO_PROCESSING_PATH / filename
        search_paths.append(processing_path)

    # 3. GTO+ running directory (with "0 - " prefix)
    if GTO_RUNNING_PATH.exists():
        running_path = GTO_RUNNING_PATH / f"{GTO_RUNNING_PREFIX}{filename}"
        search_paths.append(running_path)

    # 4. Priority queue directory (with "1.x - " prefix)
    if GTO_PRIORITY_PATH.exists():
        priority_pattern = re.compile(GTO_PRIORITY_PREFIX_PATTERN + re.escape(filename))
        for file_path in GTO_PRIORITY_PATH.glob("*.gto"):
            if priority_pattern.match(file_path.name):
                search_paths.append(file_path)

    # 5. Processed directory (with "1.x - " prefix, no prefix, or '0 - ' prefix)
    if GTO_PROCESSED_PATH.exists():
        # Look for any file with "1.x - " prefix followed by the original filename
        priority_pattern = re.compile(GTO_PRIORITY_PREFIX_PATTERN + re.escape(filename))
        for file_path in GTO_PROCESSED_PATH.glob("*.gto"):
            if priority_pattern.match(file_path.name):
                search_paths.append(file_path)
        # Also look for the original filename (no prefix) in processed directory
        processed_path = GTO_PROCESSED_PATH / filename
        search_paths.append(processed_path)
        # Also look for '0 - <filename>' in processed directory
        processed_zero_prefix = GTO_PROCESSED_PATH / f"0 - {filename}"
        search_paths.append(processed_zero_prefix)

    # Search through all possible paths in priority order
    for search_path in search_paths:
        if search_path.exists():
            return str(search_path)

    return None

def normalize_gto_filename(filename):
    """
    Remove priority prefix from filename to get the original name.
    Returns the filename without any "1.x - " or "0 - " prefix.
    """
    # Remove "1.x - " prefix if present
    priority_pattern = re.compile(GTO_PRIORITY_PREFIX_PATTERN)
    if priority_pattern.match(filename):
        # Remove the prefix and return the original filename
        return priority_pattern.sub("", filename)
    
    # Remove "0 - " prefix if present
    if filename.startswith("0 - "):
        return filename[4:]  # Remove "0 - " prefix
    
    return filename

def get_gto_storage_path(file_path):
    """
    Get the appropriate storage path for a GTO file, handling priority prefixes.
    
    Args:
        file_path (str): Original file path from database
        
    Returns:
        str: The storage path that should be stored in the database
    """
    from pathlib import Path
    file_path = Path(file_path)
    
    # Check if the file has a priority prefix (1.x -)
    import re
    priority_pattern = re.compile(GTO_PRIORITY_PREFIX_PATTERN)
    if priority_pattern.match(file_path.name):
        # Remove the prefix and return the path as if it's in the snapshot directory
        normalized_name = normalize_gto_filename(file_path.name)
        return str(GTO_SNAPSHOT_PATH / normalized_name)
    
    # Check if the file has a "0 - " prefix
    if file_path.name.startswith("0 - "):
        # Remove the prefix and return the path as if it's in the snapshot directory
        normalized_name = normalize_gto_filename(file_path.name)
        return str(GTO_SNAPSHOT_PATH / normalized_name)
    
    # For files without priority prefixes, return the original path
    return str(file_path)

def move_gto_file_to_processed(source_path):
    """
    Move a GTO file from processing directory to processed directory with proper prefix handling.
    
    Args:
        source_path (str or Path): Path to the file in processing directory
        
    Returns:
        bool: True if successful, False otherwise
    """
    from pathlib import Path
    import shutil
    
    source_path = Path(source_path)
    
    if not source_path.exists():
        print(f"Source file not found: {source_path}")
        return False
    
    # Ensure processed directory exists
    if not GTO_PROCESSED_PATH.exists():
        try:
            GTO_PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Could not create processed directory: {e}")
            return False
    
    # Determine the destination filename
    filename = source_path.name
    
    # If file has "0 - " prefix, remove it for processed directory
    if filename.startswith("0 - "):
        dest_filename = filename[4:]  # Remove "0 - " prefix
    else:
        dest_filename = filename
    
    dest_path = GTO_PROCESSED_PATH / dest_filename
    
    # Check if destination already exists
    if dest_path.exists():
        print(f"Destination file already exists: {dest_path}")
        return False
    
    try:
        # Move the file
        shutil.move(str(source_path), str(dest_path))
        print(f"Moved file from {source_path} to {dest_path}")
        return True
    except Exception as e:
        print(f"Error moving file to processed: {e}")
        return False 