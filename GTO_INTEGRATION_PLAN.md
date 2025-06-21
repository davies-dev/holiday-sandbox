# GTO+ Integration Plan for Hand History Explorer

## Overview
This document outlines the plan to integrate GTO+ file functionality into the Hand History Explorer with a separate admin tool for management.

## 1. Simplified UI Integration

### 1.1 Add GTO+ Button to State Display
- Add a single "Open GTO+ File" button next to the "Matching State Name" text box
- Button is enabled only when a valid state name is detected (not "Unnamed" or error)
- Button automatically launches the corresponding GTO+ file based on state name

### 1.2 Button Behavior
```python
# Button state logic
if state_name != "Unnamed" and not state_name.startswith("Error"):
    self.gto_button.config(state=tk.NORMAL)
    self.gto_button.config(text=f"Open GTO+ ({state_name})")
else:
    self.gto_button.config(state=tk.DISABLED)
    self.gto_button.config(text="Open GTO+")
```

## 2. Enhanced GTO+ Admin Tool

### 2.1 Create `gto_admin.py`
- Similar structure to `action_pattern_admin.py`
- Dedicated interface for managing GTO+ file mappings
- Import settings.txt functionality with enhanced file handling
- Database management for GTO+ mappings

### 2.2 Database Schema
```sql
CREATE TABLE gto_mappings (
    id SERIAL PRIMARY KEY,
    state_name VARCHAR(50) NOT NULL,
    game_type VARCHAR(50) NOT NULL,
    gto_file_path TEXT NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state_name, game_type)
);
```

## 3. Implementation Steps

### 3.1 Minimal UI Changes to `hh_explorer.py`
```python
# Add to build_left_panel after state display frame
self.gto_button = ttk.Button(state_display_frame, text="Open GTO+", 
                             command=self.open_gto_file, state=tk.DISABLED)
self.gto_button.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)

# Add method to open GTO+ file
def open_gto_file(self):
    """Open the corresponding GTO+ file for the current state"""
    if not self.current_hand:
        return
    
    # Get current state name
    state_name = self.matching_state_var.get().split(" (")[0]  # Extract state name
    game_type = self.pf_game_type_var.get().strip()
    
    # Look up GTO+ file path from database
    gto_path = self.db.get_gto_file_path(state_name, game_type)
    if gto_path and os.path.exists(gto_path):
        # Use pathlib for cross-platform compatibility
        from pathlib import Path
        gto_path = Path(gto_path)
        webbrowser.open(str(gto_path))
    else:
        messagebox.showwarning("GTO+ File Not Found", 
                              f"No GTO+ file found for state {state_name}")
```

## 4. Enhanced Database Methods

### 4.1 Add to `db_access.py`
```python
def insert_gto_mapping(self, state_name, game_type, file_path, description):
    """Insert a GTO+ mapping into the database"""
    query = """
        INSERT INTO gto_mappings (state_name, game_type, gto_file_path, description)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (state_name, game_type) 
        DO UPDATE SET gto_file_path = EXCLUDED.gto_file_path, 
                      description = EXCLUDED.description
    """
    with self.conn.cursor() as cur:
        cur.execute(query, (state_name, game_type, file_path, description))
    self.conn.commit()

def get_gto_file_path(self, state_name, game_type):
    """Get GTO+ file path for a given state and game type"""
    query = "SELECT gto_file_path FROM gto_mappings WHERE state_name = %s AND game_type = %s"
    with self.conn.cursor() as cur:
        cur.execute(query, (state_name, game_type))
        result = cur.fetchone()
    return result[0] if result else None

def get_all_gto_mappings(self):
    """Get all GTO+ mappings"""
    query = "SELECT state_name, game_type, gto_file_path, description FROM gto_mappings ORDER BY state_name"
    with self.conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return [
        {
            'state_name': row[0],
            'game_type': row[1], 
            'gto_file_path': row[2],
            'description': row[3]
        }
        for row in rows
    ]

def delete_gto_mapping(self, state_name, game_type):
    """Delete a GTO+ mapping"""
    query = "DELETE FROM gto_mappings WHERE state_name = %s AND game_type = %s"
    with self.conn.cursor() as cur:
        cur.execute(query, (state_name, game_type))
    self.conn.commit()

def get_game_types(self):
    """Get all unique game types from gto_mappings"""
    query = "SELECT DISTINCT game_type FROM gto_mappings ORDER BY game_type"
    with self.conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
    return [row[0] for row in rows]
```

## 5. Database Setup Script

### 5.1 Create `database_setup/create_gto_tables.py`
```python
#!/usr/bin/env python3
import psycopg2
from config import DB_PARAMS
from pathlib import Path

def create_gto_tables():
    """Create GTO+ related tables"""
    conn = psycopg2.connect(**DB_PARAMS)
    
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS gto_mappings (
                id SERIAL PRIMARY KEY,
                state_name VARCHAR(50) NOT NULL,
                game_type VARCHAR(50) NOT NULL,
                gto_file_path TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(state_name, game_type)
            )
        """)
    
    conn.commit()
    conn.close()
    print("GTO+ tables created successfully")

if __name__ == "__main__":
    create_gto_tables()
```

## 6. Usage Workflow

### 6.1 Initial Setup
1. Run `python database_setup/create_gto_tables.py` to create the table
2. Run `python scripts/gto_admin.py` to import settings.txt
3. Use the admin tool to manage mappings with enhanced file browsing

### 6.2 Daily Usage
1. Run `python scripts/hh_explorer.py`
2. Load a hand history
3. If a state name is detected, the "Open GTO+" button becomes enabled
4. Click the button to automatically open the corresponding GTO+ file

## 7. Implementation Order

1. Create database table
2. Add database methods to db_access.py
3. Create gto_admin.py
4. Add GTO+ button to hh_explorer.py
5. Test integration
6. Import settings.txt data 