from pathlib import Path
from config import GTO_BASE_PATH

def find_gto_file_in_locations(original_path):
    """
    Search for a GTO+ file in multiple possible locations.
    Returns the actual path where the file was found, or None if not found.
    """
    original_path = Path(original_path)
    search_paths = []

    # 1. Original path from database
    search_paths.append(original_path)

    # 2. Processing directory (base path)
    base_path = GTO_BASE_PATH
    if base_path.exists():
        # Look for the file with original name
        processing_path = base_path / original_path.name
        search_paths.append(processing_path)

        # Look for the file with "0 - " prefix
        processing_path_prefixed = base_path / f"0 - {original_path.name}"
        search_paths.append(processing_path_prefixed)

    # 3. Processed directory
    processed_base = base_path / "processed"
    if processed_base.exists():
        # Look for the file with original name
        processed_path = processed_base / original_path.name
        search_paths.append(processed_path)

        # Look for the file with "0 - " prefix
        processed_path_prefixed = processed_base / f"0 - {original_path.name}"
        search_paths.append(processed_path_prefixed)

    # Search through all possible paths
    for search_path in search_paths:
        if search_path.exists():
            return str(search_path)

    return None 