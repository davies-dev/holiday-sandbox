# Copy Flop Feature

## Overview

The "Copy Flop" button has been added to the Hand History Explorer application to quickly copy the current hand's flop cards to the system clipboard for easy pasting into other applications.

## Location

The button is located in the Review Panel, in the "Analysis Tools" section, next to the "Define New Spot" button.

## Functionality

### Button States
- **Disabled**: When no hand is loaded
- **Enabled**: When any hand is loaded (regardless of whether a spot is matched)

### Flop Extraction Methods

The feature uses multiple methods to extract flop cards from the hand history:

1. **Direct Attribute Access**: Checks if the hand history data has a `flop_cards` attribute
2. **Regex Pattern Matching**: Extracts flop cards from the raw hand history text using the pattern `*** FLOP *** [cards]`
3. **Hand History Tree**: Searches through the parsed hand history tree for flop nodes with board cards

### Output Format

The flop cards are formatted as requested: `4d 8s 4c` (space-separated, lowercase)

### Status Feedback

The feature provides real-time feedback through a status label:

- **"Copied: 4d 8s 4c"**: Successfully copied flop cards
- **"No hand loaded"**: No hand is currently loaded
- **"No flop to copy"**: Hand doesn't contain a flop (e.g., folded preflop)
- **"Error: [message]"**: An error occurred during extraction

The status message automatically clears after 3 seconds.

## Usage

1. Load a hand history in the Hand History Explorer
2. Click the "Copy Flop" button in the Review Panel
3. The flop cards will be copied to your system clipboard
4. Paste the flop cards into any application (e.g., GTO+ solver, notes, etc.)

## Technical Details

### Clipboard Implementation
- Uses Tkinter's built-in clipboard functionality
- Works across different operating systems (Windows, macOS, Linux)
- Automatically handles clipboard clearing and appending

### Error Handling
- Graceful handling of missing flop data
- Comprehensive error reporting
- Fallback methods for different hand history formats

### Performance
- Fast extraction using regex patterns
- Minimal memory usage
- Non-blocking UI updates

## Example

**Input Hand History:**
```
*** FLOP *** [4d 8s 4c]
HumptyD: checks
```

**Output Clipboard Content:**
```
4d 8s 4c
```

## Testing

A test script (`test_copy_flop.py`) is included to verify:
- Flop extraction from different hand history formats
- Clipboard functionality
- Error handling for edge cases

Run the test with:
```bash
python test_copy_flop.py
``` 