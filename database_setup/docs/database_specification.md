# Database Specification for Poker Analytics Framework

## 1. Database Structure

### Main Tables

#### `hand_histories`
- **Description**: Stores complete hand history data
- **Columns**:
  - `id` (SERIAL, PK): Unique identifier
  - `game_type` (VARCHAR(50)): Game type (e.g., "zoom_cash_6max")
  - `number_of_players` (INT): Number of players in the hand
  - `hand_id` (VARCHAR(30)): External identifier for the hand
  - `poker_site` (VARCHAR(30)): Site where the hand was played
  - `button_name` (VARCHAR(100)): Player on the button
  - `player_names` (JSONB): Array of player names
  - `stack_sizes` (JSONB): Dictionary mapping player names to stack sizes
  - `positions` (JSONB): Dictionary mapping positions to player names
  - `ante` (NUMERIC): Ante amount if applicable
  - `pf_action_seq` (VARCHAR(40)): Normalized preflop action sequence
  - `flop_action_seq` (VARCHAR(40)): Normalized flop action sequence
  - `turn_action_seq` (VARCHAR(40)): Normalized turn action sequence
  - `river_action_seq` (VARCHAR(40)): Normalized river action sequence
  - `raw_text` (TEXT): Complete hand history text
  - `created_at` (TIMESTAMP): When the record was created

#### `hand_actions`
- **Description**: Stores individual actions within each hand
- **Columns**:
  - `id` (SERIAL, PK): Unique identifier
  - `hand_history_id` (INT, FK): Reference to hand_histories.id
  - `street` (VARCHAR(20)): Street where action occurred
  - `player` (VARCHAR(100)): Player who performed the action
  - `action_type` (VARCHAR(20)): Type of action (bet, call, fold, etc.)
  - `bet_amount` (NUMERIC): Amount bet/called if applicable
  - `total` (NUMERIC): Total amount contributed
  - `pot_size` (NUMERIC): Pot size after action
  - `action_order` (INT): Sequence order of action

### Reference Tables

#### `hand_state`
- **Description**: Categorizes and labels action sequences
- **Columns**:
  - `id` (SERIAL, PK): Unique identifier
  - `state_type` (VARCHAR(20)): Street (preflop, flop, turn, river)
  - `state_value` (VARCHAR(40)): Normalized action string
  - `state_name` (VARCHAR(100)): Descriptive name or identifier
  - `game_type` (VARCHAR(50)): Game type this state applies to
  - `is_favorite` (BOOLEAN): Whether state is marked as favorite
  - `description` (TEXT): Optional description
  - `created_at` (TIMESTAMP): When record was created

#### `action_patterns`
- **Description**: Defines patterns for analyzing action sequences
- **Columns**:
  - `id` (SERIAL, PK): Unique identifier
  - `pattern_name` (VARCHAR(50)): Descriptive name
  - `applies_to` (VARCHAR(50)): Which streets pattern applies to
  - `sql_pattern` (VARCHAR(100)): Regex pattern for SQL matching
  - `description` (TEXT): Explanation of pattern
  - `created_at` (TIMESTAMP): Creation timestamp
  - `updated_at` (TIMESTAMP): Last updated timestamp

#### `chain_sequence`
- **Description**: Defines sequences of actions across streets
- **Columns**:
  - `id` (SERIAL, PK): Unique identifier
  - `chain_name` (VARCHAR(100)): Descriptive name
  - `preflop_state_id` (INT, FK): Reference to hand_state
  - `flop_state_id` (INT, FK): Reference to hand_state
  - `turn_state_id` (INT, FK): Reference to hand_state
  - `river_state_id` (INT, FK): Reference to hand_state
  - `description` (TEXT): Optional description
  - `is_favorite` (BOOLEAN): Whether chain is marked as favorite
  - `created_at` (TIMESTAMP): Creation timestamp

#### `spot_metadata`
- **Description**: Stores additional information about specific spots
- **Columns**:
  - `pf_action_seq` (VARCHAR(40), PK): Preflop action sequence
  - `spot_name` (VARCHAR(100)): Name for the spot
  - `links` (JSONB): External references and tools for the spot

## 2. Query Interface

### Database Connection
- **Host**: localhost
- **Port**: 5432
- **Database**: HolidayBrowser
- **User**: postgres

### Primary Query Methods
The existing codebase uses several querying patterns:

1. **Direct SQL via Parameter Substitution**:
   ```python
   with conn.cursor() as cur:
       cur.execute("SELECT * FROM hand_histories WHERE game_type = %s", (game_type,))
       rows = cur.fetchall()
   ```

2. **Query Builder Pattern**:
   ```python
   qb = QueryBuilder("SELECT * FROM hand_histories")
   qb.add_condition(Condition("game_type", "LIKE", "zoom_cash_6max%"))
   query = qb.build_query()
   ```

3. **JSON Field Access**:
   ```python
   # Example querying positions field which is JSONB
   qb.add_condition(Condition("positions->>'{}'", "=", player_name))
   ```

### Common Queries

#### Retrieving Hand Histories
```sql
SELECT id, game_type, pf_action_seq, flop_action_seq, turn_action_seq, river_action_seq, raw_text 
FROM hand_histories
WHERE game_type LIKE 'zoom_cash_6max%'
AND pf_action_seq = '1f2f3f4r5r6r5c'
```

#### Retrieving Action Patterns
```sql
SELECT pattern_name, sql_pattern 
FROM action_patterns 
WHERE applies_to = 'postflop'
```

#### Retrieving Hand Actions
```sql
SELECT street, player, action_type, bet_amount, total, pot_size
FROM hand_actions
WHERE hand_history_id = 12345
ORDER BY action_order
```

## 3. Data Characteristics

### Volumes and Performance
- **Approximate hand count**: Appears to be structured for large volumes (100,000+ hands)
- **Query performance**: Optimized for reading hand histories with filters
- **Indexing**: Primary keys and standard indexes appear to be used

### Data Format Details
- **Normalized sequences**: Uses shorthand notation (e.g., "1f2f3f4r5r6r5c") where:
  - Numbers represent players (by position)
  - Letters represent actions (f=fold, r=raise, c=call, k=check)
- **JSONB fields**: Used for positions, stack sizes, and player names
- **Raw text**: Complete hand history stored for reference/parsing

## 4. Implementation Considerations

### Analytics Integration Points

1. **Querying Data**
   ```python
   def retrieve_hands_by_pattern(db, pattern, limit=1000):
       query = f"""
           SELECT id, game_type, pf_action_seq, raw_text 
           FROM hand_histories
           WHERE pf_action_seq ~ %s
           LIMIT %s
       """
       with db.conn.cursor() as cur:
           cur.execute(query, (pattern, limit))
           return cur.fetchall()
   ```

2. **Processing Results**
   ```python
   def analyze_decision_points(hands):
       # Parse each hand and extract decision points
       results = {}
       for hand_id, game_type, pf_seq, raw_text in hands:
           hh_data = HandHistoryData.from_raw_text(raw_text)
           for opp in hh_data.betting_opportunities:
               key = opp.normalized_betting_sequence
               if key not in results:
                   results[key] = {'count': 0, 'ev': []}
               results[key]['count'] += 1
               # Additional analysis...
       return results
   ```

### Performance Optimizations

1. **Use Prepared Statements**:
   ```python
   prepared_query = "SELECT * FROM hand_histories WHERE game_type = %s"
   cur.execute(prepared_query, (game_type,))
   ```

2. **Batch Processing**:
   ```python
   def process_in_batches(query, batch_size=1000):
       offset = 0
       while True:
           batch_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
           # Process batch
           if len(results) < batch_size:
               break
           offset += batch_size
   ```

3. **Index Usage**:
   Ensure queries leverage existing indexes on:
   - `game_type`
   - `pf_action_seq`
   - Primary keys

## Related Documentation

For details on how this database structure will be used in the analytics framework, please refer to `analytics_implementation_plan.md`. The analytics implementation plan provides a comprehensive roadmap for building advanced poker analytics features on top of this database structure.