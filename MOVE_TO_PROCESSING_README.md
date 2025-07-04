# Move to Processing Feature

## Overview

The "Move to Processing" button has been added to the Hand History Explorer application to automatically move GTO+ files to the processing directory (`C:\@myfiles\gtotorunwhenIleave\`) for automated calculation.

## Location

The button is located in the Review Panel, next to the "Open Default Document" button.

## Functionality

When pressed, the button performs the following checks and actions:

### 1. File Availability Check
- Verifies that a spot is selected
- Ensures there are documents linked to the spot
- Finds the default GTO+ document for the spot

### 2. GTO+ File Validation
- Confirms the file is a GTO+ file (`.gto` or `.gto+` extension)
- Only GTO+ files can be moved to the processing directory

### 3. File Lock Check
- Checks if GTO+ is running
- Verifies the file is not currently open in GTO+
- Prevents moving files that are in use to avoid data loss

### 4. Processing Directory Check
- Creates the processing directory if it doesn't exist
- Checks if the file is already in the processing directory

### 5. File Naming
- If the file doesn't already start with "0 - ", adds this prefix
- This prefix is required for the automated processing system

### 6. File Movement
- Moves the file from its current location to the processing directory
- Uses the new filename with "0 - " prefix if needed

## User Feedback

### Success Messages
- **Status Label**: Shows "File moved to processing successfully" or "File already in processing directory"
- **Console Output**: Logs the move operation for debugging

### Error Messages
- **File Open Error**: "GTO+ file is currently open in GTO+. Please close the file in GTO+ before moving it to processing."
- **Permission Error**: "Permission denied moving file. Please ensure the file is not open in any application."
- **File Not Found**: Shows the searched locations for the missing file
- **Non-GTO File**: "Only GTO+ files can be moved to processing directory."

## Dependencies

The feature requires the `psutil` library to check if files are open in GTO+. This has been added to the requirements.txt file.

## Technical Details

### Files Modified
- `scripts/hh_explorer.py`: Added button, UI elements, and move logic
- `scripts/file_utils.py`: Fixed import path
- `requirements.txt`: Added psutil dependency
- `current_requirements.txt`: Added psutil dependency

### Key Methods
- `move_to_processing()`: Main method handling the file move operation
- `find_gto_file_in_locations()`: Utility to locate files in multiple directories

### Processing Directory
- **Path**: `C:\@myfiles\gtotorunwhenIleave\`
- **Purpose**: Files in this directory are automatically processed by the GTO+ calculation system
- **Naming Convention**: Files must start with "0 - " to be processed

## Usage

1. Select a hand history that matches a spot with a linked GTO+ document
2. In the Review Panel, click the "Move to Processing" button
3. The system will check all conditions and move the file if appropriate
4. Check the status label next to the button for operation results

## Safety Features

- **File Lock Detection**: Prevents moving files that are open in GTO+
- **Duplicate Prevention**: Won't move files already in the processing directory
- **Error Handling**: Comprehensive error messages for various failure scenarios
- **Permission Checks**: Validates file access before attempting moves 