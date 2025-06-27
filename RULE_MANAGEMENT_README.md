# Rule Management in Study Librarian

## Overview

The Study Librarian application now includes advanced rule management functionality that allows you to define specific action sequence patterns for each tag. This feature is the foundation for making the main replayer app "smart" by teaching it what each tag means in terms of poker actions.

## What are Rules?

A **Rule** is a set of action sequence patterns that define a poker concept. Each rule consists of:

- **Description**: A human-readable description of the poker situation
- **Preflop Pattern**: Regex pattern for preflop action sequences
- **Flop Pattern**: Regex pattern for flop action sequences  
- **Turn Pattern**: Regex pattern for turn action sequences
- **River Pattern**: Regex pattern for river action sequences

## Features

### 1. Rule Creation and Management
- Create multiple rules for each tag
- Define regex patterns for each street's action sequences
- Edit existing rules with a user-friendly interface
- Delete rules as needed

### 2. Enhanced User Interface
- **Left Panel**: Document list (unchanged)
- **Right Panel**: 
  - **Tags Section**: Shows tags assigned to selected document
  - **Rules Section**: Shows rules for selected tag
- **Rule Editor**: Modal window for creating/editing rules

### 3. Database Integration
- Rules are stored in the `study_tag_rules` table
- Each rule is linked to a specific tag
- Full CRUD operations (Create, Read, Update, Delete)

## How to Use

### Starting the Application
```bash
python librarian_app.py
```

### Creating Rules for Tags

1. **Select a Document**: Click on a document in the left panel
2. **Select a Tag**: Click on a tag in the Tags section
3. **Add a Rule**: Click "Add Rule" in the Rules section
4. **Fill in the Rule Details**:
   - **Description**: Enter a clear description (e.g., "OOP Check/Call, Turn Bet")
   - **Preflop Pattern**: Enter regex for preflop actions (e.g., "1f2f3r4r5c6c")
   - **Flop Pattern**: Enter regex for flop actions (e.g., "1k2k3b4c5c")
   - **Turn Pattern**: Enter regex for turn actions (e.g., "1b2f3c")
   - **River Pattern**: Enter regex for river actions (e.g., "1b2c")
5. **Save**: Click "Save Rule" to store the rule

### Editing Rules

1. **Select a Tag**: Choose the tag that contains the rule
2. **Select a Rule**: Click on the rule in the Rules section
3. **Edit**: Click "Edit Rule" to open the editor
4. **Modify**: Update the patterns as needed
5. **Save**: Click "Save Rule" to update the rule

### Deleting Rules

1. **Select a Rule**: Click on the rule you want to delete
2. **Delete**: Click "Delete Rule"
3. **Confirm**: Confirm the deletion in the dialog

## Action Sequence Patterns

### Pattern Format
Action sequences use a simplified format where:
- Numbers (1-6) represent player positions
- Letters represent actions:
  - `f` = fold
  - `c` = call
  - `r` = raise
  - `k` = check
  - `b` = bet

### Example Patterns

#### Preflop Patterns
- `"1f2f3r4r5c6c"` - UTG and MP fold, CO and BN raise, SB and BB call
- `"1r2f3f4f5f6f"` - UTG raise, everyone else folds
- `"1f2f3f4f5r6c"` - BN raise, BB call, others fold

#### Flop Patterns
- `"1k2k3b4c5c"` - UTG and MP check, CO bets, BN and SB call
- `"1b2f3f4f5f"` - UTG bets, everyone folds
- `"1k2k3k4k5k6k"` - Everyone checks

#### Turn Patterns
- `"1b2f3c"` - UTG bets, MP folds, CO calls
- `"1k2b3f"` - UTG checks, MP bets, CO folds

#### River Patterns
- `"1b2c"` - UTG bets, MP calls
- `"1k2k"` - Both players check

## Database Schema

### `study_tag_rules` Table
```sql
CREATE TABLE study_tag_rules (
    id SERIAL PRIMARY KEY,
    tag_id INT NOT NULL REFERENCES study_tags(id) ON DELETE CASCADE,
    rule_description TEXT,
    pf_action_seq_pattern TEXT,
    flop_action_seq_pattern TEXT,
    turn_action_seq_pattern TEXT,
    river_action_seq_pattern TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## API Methods

The following methods are available in the `DatabaseAccess` class:

### Rule Management
- `get_rules_for_tag(tag_id)`: Gets all rules for a specific tag
- `get_rule_details(rule_id)`: Gets full details of a specific rule
- `save_rule(rule_data)`: Creates or updates a rule
- `delete_rule(rule_id)`: Deletes a rule

### Example Usage

```python
from scripts.db_access import DatabaseAccess
from scripts.config import DB_PARAMS

# Initialize database connection
db = DatabaseAccess(**DB_PARAMS)

# Create a rule for a tag
rule_data = {
    "tag_id": 1,
    "rule_description": "OOP Check/Call, Turn Bet",
    "pf_pattern": "1f2f3r4r5c6c",
    "flop_pattern": "1k2k3b4c5c",
    "turn_pattern": "1b2f3c",
    "river_pattern": "1b2c"
}

# Save the rule
success = db.save_rule(rule_data)

# Get rules for a tag
rules = db.get_rules_for_tag(1)
for rule_id, desc in rules:
    print(f"Rule {rule_id}: {desc}")

# Get rule details
rule_details = db.get_rule_details(1)
if rule_details:
    print(f"Description: {rule_details['rule_description']}")
    print(f"Preflop: {rule_details['pf_pattern']}")
    print(f"Flop: {rule_details['flop_pattern']}")

db.close()
```

## Testing

Run the test script to verify rule management functionality:

```bash
python test_rule_management.py
```

This will test:
- Rule creation
- Rule retrieval
- Rule updates
- Rule deletion
- Error handling

## Benefits

1. **Knowledge Base**: Build a comprehensive library of poker concepts
2. **Pattern Recognition**: Define specific action sequences for each concept
3. **Smart Replayer**: Enable the main app to recognize and suggest relevant study materials
4. **Flexibility**: Create multiple rules per tag for different variations
5. **Scalability**: Add new concepts and patterns as your study evolves

## Future Integration

This rule management system is designed to integrate with the main hand history replayer:

1. **Pattern Matching**: The replayer will match current hand actions against stored patterns
2. **Smart Suggestions**: When patterns match, the replayer will suggest relevant study documents
3. **Learning System**: The system can learn from your study patterns and improve suggestions
4. **Analytics**: Track which concepts appear most frequently in your play

## Example Workflow

1. **Study a Hand**: Review a hand where you made a delayed continuation bet out of position
2. **Create a Tag**: Create a "DelayedCBetOOP" tag
3. **Add Documents**: Link relevant study materials to this tag
4. **Define Rules**: Create rules that describe the action patterns for this concept
5. **Use in Replayer**: When similar patterns occur in future hands, the replayer will suggest your study materials

This creates a powerful feedback loop where your study materials become increasingly relevant and accessible during actual play. 