# Enhanced GTO+ File Management System

## Overview

The GTO+ file management system has been enhanced to support a sophisticated priority-based workflow with multiple file locations and prefix-based ordering. This system allows for efficient management of GTO+ files as they move through different stages of processing.

## File Location Hierarchy

The system searches for GTO+ files in **5 locations** in order of priority:

### 1. **Snapshot Directory** (Highest Priority)
- **Path**: `C:\@myfiles\30000 Poker\GAMES\6 max\6 max MPT GTO snap shot 20210114\`
- **Purpose**: Original GTO+ files in their permanent location
- **Prefix**: None (original filenames)
- **Example**: `6 max 37 btn v bb 2.5x.gto`

### 2. **Processing Directory** (No Prefix)
- **Path**: `C:\@myfiles\gtotorunwhenIleave\`
- **Purpose**: Files ready for processing
- **Prefix**: None
- **Example**: `6 max 37 btn v bb 2.5x.gto`

### 3. **GTO+ Running Directory** (With "0 - " Prefix)
- **Path**: `C:\@myfiles\gtotorunwhenIleave\`
- **Purpose**: Files currently being processed by GTO+
- **Prefix**: `0 - `
- **Example**: `0 - 6 max 37 btn v bb 2.5x.gto`

### 4. **Priority Queue Directory** (With "1.x - " Prefix)
- **Path**: `C:\@myfiles\gtotorunwhenIleave\`
- **Purpose**: Files queued for processing with priority order
- **Prefix**: `1.x - ` (where x is an integer indicating priority)
- **Examples**: 
  - `1.1 - 6 max 37 btn v bb 2.5x.gto`
  - `1.5 - 6 max 80 btn 3b v hj.gto`
  - `1.11 - 6 max 19 bb flat v sb 3x.gto`

### 5. **Processed Directory** (With "1.x - " Prefix)
- **Path**: `C:\@myfiles\gtotorunwhenIleave\processed\`
- **Purpose**: Completed files with priority prefixes
- **Prefix**: `1.x - ` (same as priority queue)
- **Example**: `1.2 - 6 max 73 btn v bb 3x.gto`

## File Lifecycle

```
Snapshot Directory
        ↓
Priority Queue (1.x - prefix)
        ↓
Processing Directory (no prefix)
        ↓
GTO+ Running (0 - prefix)
        ↓
Processed Directory (1.x - prefix)
        ↓
Back to Snapshot (no prefix)
```

## Key Features

### 1. **Priority-Based Prefix System**
- Files with `1.x - ` prefixes are ordered by priority number
- Lower numbers = higher priority (1.1, 1.2, 1.3, etc.)
- Daily priority changes are supported

### 2. **Smart File Storage**
- When adding files with `1.x - ` prefixes, they're stored as if they're in the snapshot directory
- This maintains consistency regardless of current file location

### 3. **Comprehensive Search**
- Searches all 5 locations in priority order
- Automatically handles prefix variations
- Returns the first matching file found

### 4. **Filename Normalization**
- Removes priority prefixes to get original filenames
- Maintains file identity across different locations

## Configuration

All paths and patterns are configured in `scripts/config.py`:

```python
# GTO+ file location configuration
GTO_SNAPSHOT_PATH = Path("C:\\@myfiles\\30000 Poker\\GAMES\\6 max\\6 max MPT GTO snap shot 20210114\\")
GTO_PROCESSING_PATH = GTO_BASE_PATH
GTO_RUNNING_PATH = GTO_BASE_PATH
GTO_PRIORITY_PATH = GTO_BASE_PATH
GTO_PROCESSED_PATH = GTO_BASE_PATH / "processed"

# File prefix patterns
GTO_RUNNING_PREFIX = "0 - "
GTO_PRIORITY_PREFIX_PATTERN = r"^1\.\d+ - "  # Matches "1.x - " where x is any integer
```

## API Functions

### `find_gto_file_in_locations(original_path)`
Searches for a GTO+ file in all 5 locations in priority order.

**Parameters:**
- `original_path` (str): The original file path or filename

**Returns:**
- `str` or `None`: Full path to the found file, or None if not found

**Example:**
```python
from scripts.file_utils import find_gto_file_in_locations

# Search for a file
found_path = find_gto_file_in_locations("6 max 37 btn v bb 2.5x.gto")
if found_path:
    print(f"Found at: {found_path}")
```

### `normalize_gto_filename(filename)`
Removes priority prefixes from filenames.

**Parameters:**
- `filename` (str): Filename with or without prefix

**Returns:**
- `str`: Filename without priority prefix

**Example:**
```python
from scripts.file_utils import normalize_gto_filename

# Normalize filenames
normalized = normalize_gto_filename("1.5 - 6 max 37 btn v bb 2.5x.gto")
print(normalized)  # Output: "6 max 37 btn v bb 2.5x.gto"
```

### `get_gto_storage_path(filename)`
Gets the storage path for database storage.

**Parameters:**
- `filename` (str): Original file path

**Returns:**
- `str`: Path to use for database storage

**Example:**
```python
from scripts.file_utils import get_gto_storage_path

# Get storage path
storage_path = get_gto_storage_path("1.11 - 6 max 80 btn 3b v hj.gto")
# Returns: "C:\@myfiles\30000 Poker\GAMES\6 max\6 max MPT GTO snap shot 20210114\6 max 80 btn 3b v hj.gto"
```

## Usage Examples

### Adding Files with Priority Prefixes

When you add a file with a `1.x - ` prefix through the UI:

1. **File Selection**: User selects `1.5 - 6 max 37 btn v bb 2.5x.gto`
2. **Storage Path**: System stores it as if it's in the snapshot directory
3. **Database Entry**: File is recorded as `6 max 37 btn v bb 2.5x.gto` in snapshot location
4. **File Location**: Actual file remains in priority queue with prefix

### Opening Files

When opening a linked document:

1. **Search Order**: System searches all 5 locations in priority order
2. **Prefix Handling**: Automatically handles files with any prefix
3. **File Found**: Returns the first matching file found
4. **Opening**: Opens the file in its current location

### Priority Management

The priority system allows for:

- **Daily Priority Changes**: Update `1.x - ` prefixes daily
- **Queue Management**: Files are processed in priority order
- **Flexible Workflow**: Files can move between locations seamlessly

## Testing

Run the test script to verify the system:

```bash
python test_gto_file_locations_enhanced.py
```

This tests:
- Configuration paths
- Filename normalization
- Storage path generation
- File location search
- Priority prefix detection

## Benefits

1. **Flexible Workflow**: Supports complex file management workflows
2. **Priority System**: Allows for ordered processing of files
3. **Location Independence**: Files can be found regardless of current location
4. **Consistent Storage**: Database entries remain consistent
5. **Daily Adaptability**: Priority prefixes can change daily

## Integration

The enhanced system is integrated into:

- **Document Addition**: Automatically handles priority prefixes when adding files
- **File Opening**: Searches all locations when opening linked documents
- **Database Storage**: Maintains consistent file paths in database
- **UI Operations**: Seamlessly works with existing UI features

## Future Enhancements

Potential improvements:
- **Bulk Priority Updates**: Tools for updating multiple file priorities
- **Priority History**: Track priority changes over time
- **Automated Workflow**: Automatic file movement between locations
- **Priority Analytics**: Analyze processing patterns and priorities 