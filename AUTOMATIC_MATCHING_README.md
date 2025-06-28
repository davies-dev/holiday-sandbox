# Automatic Study Note Matching

## Overview

The Hand History Explorer now includes **automatic study note matching** functionality that intelligently finds and displays relevant study documents based on the current hand's action sequences. This creates a powerful connection between your hand history analysis and your study library.

## How It Works

### 1. Pattern Matching Engine
The system uses regex pattern matching to compare the current hand's action sequences against rules defined in the Study Librarian:

- **Preflop Patterns**: Matches preflop action sequences
- **Flop Patterns**: Matches flop action sequences  
- **Turn Patterns**: Matches turn action sequences
- **River Patterns**: Matches river action sequences

### 2. Rule Evaluation
For each rule in the database:
- **Exact Match**: All specified patterns must match the hand's action sequences
- **Wildcard Support**: Empty/blank patterns act as wildcards (always match)
- **Partial Match**: Rules can specify patterns for only some streets

### 3. Document Retrieval
When rules match:
- Find all tags associated with matching rules
- Retrieve all study documents linked to those tags
- Display results in the "Relevant Study Notes" panel

## Features

### 🎯 **Automatic Detection**
- **Real-time Matching**: Automatically finds relevant study materials when you load a hand
- **Smart Suggestions**: Shows study documents that match the current poker situation
- **Context-Aware**: Considers the specific action patterns of the current hand

### 📚 **Study Integration**
- **Direct Access**: Double-click to open study notes in Obsidian
- **Multiple Matches**: Can find multiple relevant documents for complex situations
- **Tag-Based**: Leverages your existing tag and rule system

### 🔧 **Flexible Matching**
- **Regex Patterns**: Use powerful regex patterns for precise matching
- **Wildcard Support**: Leave patterns empty for "any action" matching
- **Street-Specific**: Define patterns for individual streets or combinations

## User Interface

### Review Panel Enhancements
The Review Panel now includes a new section:

**"Relevant Study Notes" Panel:**
- **ID Column**: Shows document ID (40px width)
- **Title Column**: Shows document title (150px width)
- **File Column**: Shows file path (200px width)
- **Double-Click**: Opens the study note in Obsidian

### Workflow
1. **Load a Hand**: Navigate to any hand in the Hand History Explorer
2. **Automatic Matching**: The system automatically finds relevant study documents
3. **View Results**: See matching documents in the "Relevant Study Notes" panel
4. **Access Study Materials**: Double-click to open study notes in Obsidian

## Technical Implementation

### Database Methods

#### `_check_rule_match(rule, hh_data)`
```python
def _check_rule_match(self, rule, hh_data):
    """
    Checks if a hand's data matches a single rule's patterns.
    A blank/None pattern is considered a wildcard (always matches).
    """
```

**Parameters:**
- `rule`: Dictionary containing rule patterns
- `hh_data`: HandHistoryData object with action sequences

**Returns:** `True` if all patterns match, `False` otherwise

#### `find_relevant_study_documents(hh_data)`
```python
def find_relevant_study_documents(self, hh_data):
    """
    Finds all study documents with tags whose rules match the given hand data.
    """
```

**Parameters:**
- `hh_data`: HandHistoryData object with action sequences

**Returns:** List of tuples `(doc_id, title, file_path)`

### Pattern Format

#### Action Sequence Format
Action sequences use a simplified format:
- **Numbers (1-6)**: Represent player positions
- **Letters**: Represent actions
  - `f` = fold
  - `c` = call
  - `r` = raise
  - `k` = check
  - `b` = bet

#### Example Patterns
```python
# Preflop: UTG and MP fold, CO and BN raise, SB and BB call
"1f2f3r4r5c6c"

# Flop: UTG and MP check, CO bets, BN and SB call
"1k2k3b4c5c"

# Turn: UTG bets, MP folds, CO calls
"1b2f3c"

# River: UTG bets, MP calls
"1b2c"
```

#### Wildcard Patterns
```python
# Only preflop pattern specified, others are wildcards
pf_pattern = "1f2f3r4r5c6c"
flop_pattern = ""  # Matches any flop action
turn_pattern = ""  # Matches any turn action
river_pattern = "" # Matches any river action
```

## Example Workflow

### 1. Create Study Materials
```bash
# Start the Librarian app
python librarian_app.py

# Create a tag for "Delayed C-Bet Out of Position"
# Add study documents about this concept
# Create rules that define the action patterns
```

### 2. Define Rules
**Rule Example:**
- **Description**: "OOP Check/Call, Turn Bet"
- **Preflop Pattern**: `"1f2f3r4r5c6c"` (specific preflop action)
- **Flop Pattern**: `"1k2k3b4c5c"` (check-call pattern)
- **Turn Pattern**: `"1b2f3c"` (bet-fold-call pattern)
- **River Pattern**: `""` (wildcard - any river action)

### 3. Use in Hand History Explorer
```bash
# Start the Hand History Explorer
python scripts/hh_explorer.py

# Navigate to a hand with similar action patterns
# The system automatically finds and displays relevant study documents
# Double-click to open study materials in Obsidian
```

## Benefits

### 🎓 **Enhanced Learning**
- **Contextual Study**: Study materials appear when relevant situations occur
- **Active Learning**: Connect theory to actual hands in real-time
- **Reinforcement**: Review concepts when they naturally arise

### ⚡ **Improved Efficiency**
- **No Manual Search**: Automatically find relevant materials
- **Instant Access**: Direct integration with Obsidian
- **Smart Organization**: Leverage your existing tag system

### 🔄 **Continuous Improvement**
- **Pattern Recognition**: Identify recurring situations
- **Study Gaps**: Discover areas needing more study materials
- **Knowledge Application**: Apply study concepts to real hands

## Testing

Run the test script to verify automatic matching functionality:

```bash
python test_study_matching.py
```

This tests:
- Rule creation and pattern matching
- Document retrieval and linking
- Wildcard pattern support
- Error handling

## Future Enhancements

### Potential Improvements
1. **Scoring System**: Rank matches by relevance/confidence
2. **Learning Algorithm**: Improve suggestions based on usage patterns
3. **Batch Processing**: Match multiple hands at once
4. **Analytics**: Track which concepts appear most frequently
5. **Smart Notifications**: Alert when new study materials match current situations

### Integration Opportunities
1. **GTO+ Integration**: Link patterns to GTO+ solutions
2. **Video Integration**: Match to video study materials
3. **Community Features**: Share and discover patterns
4. **Mobile Support**: Access study materials on mobile devices

## Troubleshooting

### Common Issues

**No Matching Documents Found:**
- Check that rules exist in the Librarian
- Verify pattern syntax is correct
- Ensure documents are linked to tags with matching rules

**Patterns Not Matching:**
- Verify action sequence format
- Check regex syntax
- Test patterns with simple examples first

**Study Notes Not Opening:**
- Verify Obsidian vault path is correct
- Check file paths exist
- Ensure Obsidian is running

### Debug Information
The system provides detailed logging for troubleshooting:
- Pattern matching results
- Database query results
- Error messages and stack traces

## Conclusion

The automatic study note matching system creates a powerful bridge between hand history analysis and study materials. By automatically identifying relevant study documents based on action patterns, it transforms passive study into an active, contextual learning experience.

This feature represents a significant step toward making the Hand History Explorer a comprehensive poker study platform that not only helps you analyze hands but also guides your learning process with intelligent suggestions. 