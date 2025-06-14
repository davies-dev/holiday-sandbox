#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db_access import DatabaseAccess
from query_builder import QueryBuilder, Condition
from saved_state_manager import SavedStateManager
from typing import List
from holiday_parser import (
    get_hand_history_parser, 
    HandHistoryData, 
    BettingOpportunity, 
    HandHistoryTree, 
    HandNode, 
    ForcedAction, 
    PlayerAction, 
    DecisionPoint, 
    StreetChange, 
    PlayerState, 
    NodeType
)
from dataclasses import dataclass, field
from typing import Optional, Dict
import sys
from config import DB_PARAMS
#from betting_op import BettingOppurtunity
#from betting_op import * 
#------------------------------
#New: BettingOpportunity Data Structure
#------------------------------

# BettingOpportunity class is now imported from kk10.py

# ------------------------------
# Main Application: QueryStateBrowser
# ------------------------------
class HandHistoryExplorer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Hand History Explorer")
        self.geometry("1200x750")
        
        # Create our database access instance.
        self.db = DatabaseAccess(**DB_PARAMS)
        # Initialize our saved state manager.
        self.state_manager = SavedStateManager("saved_states.json")
        # Initialize query results and current index.
        self.query_results = []
        self.current_index = 0
        # Keep track of left panel visibility.
        self.left_visible = True
        # Initialize current hand
        self.current_hand = None

        # --- Toggle Button for Left Panel ---
        self.toggle_btn = ttk.Button(self, text="Hide Input Panel", command=self.toggle_left_panel)
        self.toggle_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        
        # --- Main PanedWindow ---
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel: Inputs and State Management.
        self.left_frame = ttk.Frame(self.main_paned)
        self.build_left_panel(self.left_frame)
        self.main_paned.add(self.left_frame, weight=1)
        
        # Right Panel: Hand History Display and Navigation.
        self.right_frame = ttk.Frame(self.main_paned)
        self.build_right_panel(self.right_frame)
        self.main_paned.add(self.right_frame, weight=3)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def build_left_panel(self, parent):
        # --- Query Settings Panel ---
        query_frame = ttk.LabelFrame(parent, text="Query Settings")
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(query_frame, text="PF Game Type:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.pf_game_type_var = tk.StringVar(value="zoom_cash_6max")
        game_types = ["zoom_cash_6max", "spingo", "husng spots"]
        self.pf_game_type_combo = ttk.Combobox(query_frame, textvariable=self.pf_game_type_var,
                                               values=game_types, state="readonly", width=20)
        self.pf_game_type_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.pf_game_type_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_pf_actions())
        
        ttk.Label(query_frame, text="Preflop Action Number:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        # Store label reference for dynamic update
        self.pf_seq_label = ttk.Label(query_frame, text="Preflop Action Number:")
        self.pf_seq_label.grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        # Dropdown setup (keep reference for dynamic update)
        self.pf_actions = self.load_pf_actions()
        pf_options = self.build_pf_options(self.pf_actions)
        self.pf_seq_var = tk.StringVar(value=pf_options[0] if pf_options else "")
        self.pf_seq_combo = ttk.Combobox(query_frame, textvariable=self.pf_seq_var,
                                         values=pf_options, state="readonly", width=20)
        self.pf_seq_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.pf_seq_combo.bind("<<ComboboxSelected>>", self.on_pf_selection)

        # Add a read-only entry for preflop SQL pattern (initially empty)
        self.pf_sql_pattern_var = tk.StringVar()
        self.pf_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.pf_sql_pattern_var, width=40, state="readonly")
        self.pf_sql_pattern_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        self.pf_sql_pattern_entry.grid_remove()  # Hide by default

        # Add pf Action no checkbox to the right of the SQL pattern entry
        self.pf_action_no_var = tk.BooleanVar(value=True)
        self.pf_action_no_checkbox = ttk.Checkbutton(query_frame, text="pf Action no", variable=self.pf_action_no_var, command=self.on_pf_action_no_toggle)
        self.pf_action_no_checkbox.grid(row=1, column=4, sticky=tk.W, padx=5, pady=5)

        # Action String label/entry (only shown when checkbox is checked)
        self.pf_action_str_label = ttk.Label(query_frame, text="Action String:")
        self.pf_action_str_label.grid(row=1, column=2, sticky=tk.E, padx=5, pady=5)
        self.pf_action_str_var = tk.StringVar()
        self.pf_action_entry = ttk.Entry(query_frame, textvariable=self.pf_action_str_var, width=40)
        self.pf_action_entry.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Flop Pattern:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.flop_pattern_var = tk.StringVar(value="None")
        self.flop_pattern_combo = ttk.Combobox(query_frame, textvariable=self.flop_pattern_var,
                                               values=["None"] + sorted(self.load_postflop_patterns().keys()), 
                                               state="readonly", width=20)
        self.flop_pattern_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.flop_pattern_combo.bind("<<ComboboxSelected>>", self.on_flop_pattern_selection)
        ttk.Label(query_frame, text="Flop SQL Pattern:").grid(row=2, column=2, sticky=tk.E, padx=5, pady=5)
        self.flop_sql_pattern_var = tk.StringVar()
        self.flop_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.flop_sql_pattern_var,
                                                width=40, state="readonly")
        self.flop_sql_pattern_entry.grid(row=2, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Turn Pattern:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.turn_pattern_var = tk.StringVar(value="None")
        self.turn_pattern_combo = ttk.Combobox(query_frame, textvariable=self.turn_pattern_var,
                                               values=["None"] + sorted(self.load_postflop_patterns().keys()), 
                                               state="readonly", width=20)
        self.turn_pattern_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.turn_pattern_combo.bind("<<ComboboxSelected>>", self.on_turn_pattern_selection)
        ttk.Label(query_frame, text="Turn SQL Pattern:").grid(row=3, column=2, sticky=tk.E, padx=5, pady=5)
        self.turn_sql_pattern_var = tk.StringVar()
        self.turn_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.turn_sql_pattern_var,
                                                width=40, state="readonly")
        self.turn_sql_pattern_entry.grid(row=3, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="River Pattern:").grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        self.river_pattern_var = tk.StringVar(value="None")
        self.river_pattern_combo = ttk.Combobox(query_frame, textvariable=self.river_pattern_var,
                                               values=["None"] + sorted(self.load_postflop_patterns().keys()), 
                                               state="readonly", width=20)
        self.river_pattern_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.river_pattern_combo.bind("<<ComboboxSelected>>", self.on_river_pattern_selection)
        ttk.Label(query_frame, text="River SQL Pattern:").grid(row=4, column=2, sticky=tk.E, padx=5, pady=5)
        self.river_sql_pattern_var = tk.StringVar()
        self.river_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.river_sql_pattern_var,
                                                width=40, state="readonly")
        self.river_sql_pattern_entry.grid(row=4, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Button Name:").grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        self.button_name_var = tk.StringVar()
        self.button_entry = ttk.Entry(query_frame, textvariable=self.button_name_var, width=30)
        self.button_entry.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Position:").grid(row=6, column=0, sticky=tk.E, padx=5, pady=5)
        self.position_var = tk.StringVar(value="None")
        positions_list = ["None", "BN", "SB", "BB", "UTG", "MP", "CO"]
        self.position_combo = ttk.Combobox(query_frame, textvariable=self.position_var,
                                           values=positions_list, state="readonly", width=20)
        self.position_combo.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Player Name for Position:").grid(row=6, column=2, sticky=tk.E, padx=5, pady=5)
        self.position_player_var = tk.StringVar()
        self.position_player_entry = ttk.Entry(query_frame, textvariable=self.position_player_var, width=30)
        self.position_player_entry.grid(row=6, column=3, sticky=tk.W, padx=5, pady=5)
        
        self.query_button = ttk.Button(query_frame, text="Run Query", command=self.run_query)
        self.query_button.grid(row=7, column=0, columnspan=4, pady=10)
        
        # Add after the query button
        refresh_btn = ttk.Button(query_frame, text="↻ Refresh Dropdowns", command=self.refresh_all_dropdowns)
        refresh_btn.grid(row=7, column=3, pady=10, sticky=tk.E)
        
        # --- New: Betting Opportunities Button ---
        opp_btn = ttk.Button(parent, text="Show Betting Opportunities", command=self.show_betting_opportunities)
        opp_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- New: Combined Actions and Opportunities Button ---
        combined_btn = ttk.Button(parent, text="Show Combined Actions & Opportunities", command=self.show_combined_view)
        combined_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- New: Hand Actions Button ---
        actions_btn = ttk.Button(parent, text="Show Hand Actions", command=self.show_hand_actions)
        actions_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- Existing: New PF Action Panel and State Management Panel ---
        new_pf_frame = ttk.LabelFrame(parent, text="New PF Action")
        new_pf_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(new_pf_frame, text="New PF Action Number:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.new_pf_number_var = tk.StringVar()
        self.new_pf_number_entry = ttk.Entry(new_pf_frame, textvariable=self.new_pf_number_var, width=20)
        self.new_pf_number_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(new_pf_frame, text="New PF Action String:").grid(row=0, column=2, sticky=tk.E, padx=5, pady=5)
        self.new_pf_string_var = tk.StringVar()
        self.new_pf_string_entry = ttk.Entry(new_pf_frame, textvariable=self.new_pf_string_var, width=40)
        self.new_pf_string_entry.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(new_pf_frame, text="Game Type:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.new_game_type_var = tk.StringVar(value="zoom_cash_6max")
        self.new_game_type_combo = ttk.Combobox(new_pf_frame, textvariable=self.new_game_type_var,
                                                values=game_types, state="readonly", width=20)
        self.new_game_type_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        
        self.save_new_pf_button = ttk.Button(new_pf_frame, text="Save New PF Action", command=self.save_new_pf_action)
        self.save_new_pf_button.grid(row=1, column=3, sticky=tk.W, padx=5, pady=5)
        
        state_frame = ttk.LabelFrame(parent, text="Saved States")
        state_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.state_list = tk.Listbox(state_frame, height=5, width=40)
        self.state_list.grid(row=0, column=0, rowspan=3, padx=5, pady=5)
        self.refresh_state_list()
        
        ttk.Label(state_frame, text="State Name:").grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        self.state_name_var = tk.StringVar()
        self.state_entry = ttk.Entry(state_frame, textvariable=self.state_name_var, width=30)
        self.state_entry.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        
        self.save_state_button = ttk.Button(state_frame, text="Save State", command=self.save_state)
        self.save_state_button.grid(row=1, column=2, padx=5, pady=5)
        self.load_state_button = ttk.Button(state_frame, text="Load State", command=self.load_state)
        self.load_state_button.grid(row=2, column=2, padx=5, pady=5)
        self.delete_state_button = ttk.Button(state_frame, text="Delete State", command=self.delete_state)
        self.delete_state_button.grid(row=3, column=2, padx=5, pady=5)
    
    def build_right_panel(self, parent):
        results_frame = ttk.Frame(parent)
        results_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Add Show Tree button
        self.show_tree_button = ttk.Button(results_frame, text="Show Tree", command=self.show_tree)
        self.show_tree_button.pack(side=tk.TOP, pady=5)
        
        self.result_text = tk.Text(results_frame, wrap=tk.WORD, font=("Courier", 10))
        self.result_text.pack(fill=tk.BOTH, expand=True)
        
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(pady=5)
        self.prev_button = ttk.Button(nav_frame, text="Previous", command=self.prev_result)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button = ttk.Button(nav_frame, text="Next", command=self.next_result)
        self.next_button.pack(side=tk.LEFT, padx=5)
    
    def toggle_left_panel(self):
        if self.left_visible:
            self.main_paned.forget(self.left_frame)
            self.toggle_btn.config(text="Show Input Panel")
            self.left_visible = False
        else:
            self.main_paned.add(self.left_frame, weight=1)
            self.toggle_btn.config(text="Hide Input Panel")
            self.left_visible = True
    
    def load_pf_actions(self):
        game_type = self.pf_game_type_var.get().strip()
        pf_actions = {}
        try:
            query_named = (
                f"SELECT state_name, state_value FROM hand_state "
                f"WHERE state_type = 'preflop' AND game_type = '{game_type}' AND TRIM(state_name) <> '' "
                f"ORDER BY state_name::int ASC"
            )
            with self.db.conn.cursor() as cur:
                cur.execute(query_named)
                rows = cur.fetchall()
            for row in rows:
                state_name, state_value = row
                pf_actions[str(state_name).strip()] = str(state_value).strip()
            query_unnamed = (
                f"SELECT DISTINCT pf_action_seq FROM hand_histories "
                f"WHERE game_type LIKE '{game_type}%' AND pf_action_seq IS NOT NULL "
                f"AND pf_action_seq NOT IN ("
                f"    SELECT state_value FROM hand_state "
                f"    WHERE state_type = 'preflop' AND game_type = '{game_type}'"
                f") "
                f"ORDER BY pf_action_seq"
            )
            with self.db.conn.cursor() as cur:
                cur.execute(query_unnamed)
                unnamed_rows = cur.fetchall()
            if unnamed_rows:
                unnamed_list = [str(r[0]).strip() for r in unnamed_rows]
                aggregated = "; ".join(sorted(set(unnamed_list)))
                pf_actions["Unnamed"] = aggregated
            else:
                pf_actions["Unnamed"] = ""
        except Exception as e:
            print("Error retrieving PF actions from DB:", e)
        return pf_actions
    
    def build_pf_options(self, pf_actions):
        options = []
        options.append("Unnamed")
        named_keys = [k for k in pf_actions.keys() if k != "Unnamed"]
        try:
            named_keys.sort(key=lambda x: int(x))
        except Exception as e:
            print("Error sorting PF action numbers:", e)
        options.extend(named_keys)
        return options
    
    def refresh_pf_actions(self):
        self.pf_actions = self.load_pf_actions()
        options = self.build_pf_options(self.pf_actions)
        self.pf_seq_combo['values'] = options
        if options:
            self.pf_seq_var.set(options[0])
            self.on_pf_selection(None)
        else:
            self.pf_seq_var.set("")
            self.pf_action_str_var.set("")
    
    def load_postflop_patterns(self):
        query = "SELECT pattern_name, sql_pattern FROM action_patterns WHERE applies_to = 'postflop' ORDER BY pattern_name"
        patterns = {}
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            for row in rows:
                pattern_name, sql_pattern = row
                patterns[pattern_name.strip()] = sql_pattern.strip()
        except Exception as e:
            print("Error retrieving postflop patterns from DB:", e)
        return patterns
    
    def on_pf_selection(self, event):
        selected = self.pf_seq_var.get().strip()
        action_str = self.pf_actions.get(selected, "")
        self.pf_action_str_var.set(action_str)
    
    def on_flop_pattern_selection(self, event):
        selected = self.flop_pattern_var.get().strip()
        if selected == "None":
            self.flop_sql_pattern_var.set("")
        else:
            sql_pattern = self.load_postflop_patterns().get(selected, "")
            self.flop_sql_pattern_var.set(sql_pattern)
    
    def on_turn_pattern_selection(self, event):
        selected = self.turn_pattern_var.get().strip()
        if selected == "None":
            self.turn_sql_pattern_var.set("")
        else:
            sql_pattern = self.load_postflop_patterns().get(selected, "")
            self.turn_sql_pattern_var.set(sql_pattern)
    
    def on_river_pattern_selection(self, event):
        selected = self.river_pattern_var.get().strip()
        if selected == "None":
            self.river_sql_pattern_var.set("")
        else:
            sql_pattern = self.load_postflop_patterns().get(selected, "")
            self.river_sql_pattern_var.set(sql_pattern)
    
    def run_query(self):
        qb = QueryBuilder(
            "SELECT id, game_type, pf_action_seq, flop_action_seq, turn_action_seq, river_action_seq, raw_text FROM hand_histories"
        )
        qb.add_condition(Condition("game_type", "LIKE", "zoom_cash_6max%"))
        pf_selected = self.pf_seq_var.get().strip()
        pf_action_str = self.pf_action_str_var.get().strip()
        # Use different logic depending on the checkbox
        if hasattr(self, 'pf_action_no_var') and not self.pf_action_no_var.get():
            # Checkbox is unchecked: use preflop pattern SQL
            pf_sql_pattern = self.pf_sql_pattern_var.get().strip()
            if pf_sql_pattern:
                qb.add_condition(Condition("pf_action_seq", "~", pf_sql_pattern))
        else:
            # Checkbox is checked: use preflop action number logic
            if pf_selected == "Unnamed":
                pf_values = tuple(v.strip() for v in pf_action_str.split(";") if v.strip())
                if pf_values:
                    qb.add_condition(Condition("pf_action_seq", "IN", pf_values))
                else:
                    qb.add_condition(Condition("pf_action_seq", "=", ""))
            else:
                qb.add_condition(Condition("pf_action_seq", "=", pf_action_str))
        flop_sql_pattern = self.flop_sql_pattern_var.get().strip()
        if flop_sql_pattern:
            qb.add_condition(Condition("flop_action_seq", "~", flop_sql_pattern))
        turn_sql_pattern = self.turn_sql_pattern_var.get().strip()
        if turn_sql_pattern:
            qb.add_condition(Condition("turn_action_seq", "~", turn_sql_pattern))
        river_sql_pattern = self.river_sql_pattern_var.get().strip()
        if river_sql_pattern:
            qb.add_condition(Condition("river_action_seq", "~", river_sql_pattern))
        button_name = self.button_name_var.get().strip()
        if button_name:
            qb.add_condition(Condition("button_name", "=", button_name))
        position = self.position_var.get().strip()
        position_player = self.position_player_var.get().strip()
        if position and position != "None" and position_player:
            qb.add_condition(Condition(f"positions->>'{position}'", "=", position_player))
        query = qb.build_query()
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error executing query: {e}\n")
            return
        self.query_results = rows
        self.current_index = 0
        self.display_current_result()
    
    def display_current_result(self):
        try:
            self.result_text.delete("1.0", tk.END)
            if not self.query_results:
                self.result_text.insert(tk.END, "No matching hand histories found.\n")
            else:
                row = self.query_results[self.current_index]
                (hand_id, game_type, pf_seq, flop_seq, turn_seq, river_seq, raw_text) = row
                
                # Parse the hand history to get HandHistoryData
                parser = get_hand_history_parser(raw_text)
                hh_data = parser.parse(raw_text)
                
                # Generate action sequences on the fly
                pf_seq = hh_data.get_simple_action_sequence("preflop")
                flop_seq = hh_data.get_simple_action_sequence("flop")
                turn_seq = hh_data.get_simple_action_sequence("turn")
                river_seq = hh_data.get_simple_action_sequence("river")
                
                display_text = (f"Result {self.current_index+1} of {len(self.query_results)}\n"
                              f"ID: {hand_id}\nGame Type: {game_type}\n"
                              f"Preflop: {pf_seq}\nFlop: {flop_seq}\nTurn: {turn_seq}\nRiver: {river_seq}\n\n"
                              f"Raw Hand History:\n{raw_text}\n")
                self.result_text.insert(tk.END, display_text)
                # Load the hand data
                self.load_hand(row)
            
            self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_index < len(self.query_results)-1 else tk.DISABLED)
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error displaying result: {e}\n")
    
    def next_result(self):
        try:
            if self.current_index < len(self.query_results)-1:
                self.current_index += 1
                self.display_current_result()
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error navigating to next result: {e}\n")
    
    def prev_result(self):
        try:
            if self.current_index > 0:
                self.current_index -= 1
                self.display_current_result()
        except Exception as e:
            messagebox.showerror("Error", f"Error navigating to previous result: {str(e)}\nThe application will continue running.")
            # Reset to a safe state
            self.current_index = max(0, min(self.current_index, len(self.query_results)-1))
    
    def save_new_pf_action(self):
        new_pf_number = self.new_pf_number_var.get().strip()
        new_pf_string = self.new_pf_string_var.get().strip()
        new_game_type = self.new_game_type_var.get().strip()
        if not new_pf_number or not new_pf_string or not new_game_type:
            messagebox.showerror("Error", "Please provide values for all new PF action fields.")
            return
        insert_query = ("INSERT INTO hand_state (state_type, state_name, state_value, game_type) "
                        "VALUES ('preflop', %s, %s, %s)")
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(insert_query, (new_pf_number, new_pf_string, new_game_type))
            self.db.conn.commit()
            messagebox.showinfo("Success", f"New PF Action {new_pf_number} saved successfully.")
            if new_game_type == self.pf_game_type_var.get().strip():
                self.pf_actions[new_pf_number] = new_pf_string
                options = self.build_pf_options(self.pf_actions)
                self.pf_seq_combo['values'] = options
            self.new_pf_number_var.set("")
            self.new_pf_string_var.set("")
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Error saving new PF action: {e}")
    
    def save_state(self):
        state_name = self.state_name_var.get().strip()
        if not state_name:
            messagebox.showerror("Error", "Please provide a name for the state.")
            return
        state_data = {
            "pf_game_type": self.pf_game_type_var.get().strip(),
            "pf_action_number": self.pf_seq_var.get().strip(),
            "flop_pattern": self.flop_pattern_var.get().strip(),
            "turn_pattern": self.turn_pattern_var.get().strip(),
            "river_pattern": self.river_pattern_var.get().strip(),
            "button_name": self.button_name_var.get().strip(),
            "position": self.position_var.get().strip(),
            "position_player": self.position_player_var.get().strip(),
            "pf_action_string": self.pf_action_str_var.get().strip()
        }
        self.state_manager.set_state(state_name, state_data)
        self.refresh_state_list()
        messagebox.showinfo("Saved", f"State '{state_name}' saved successfully.")
    
    def load_state(self):
        selection = self.state_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a saved state to load.")
            return
        state_name = self.state_list.get(selection[0])
        state_data = self.state_manager.get_state(state_name)
        if state_data:
            self.pf_game_type_var.set(state_data.get("pf_game_type", "zoom_cash_6max"))
            self.refresh_pf_actions()
            self.pf_seq_var.set(state_data.get("pf_action_number", ""))
            self.flop_pattern_var.set(state_data.get("flop_pattern", "None"))
            self.turn_pattern_var.set(state_data.get("turn_pattern", "None"))
            self.river_pattern_var.set(state_data.get("river_pattern", "None"))
            self.button_name_var.set(state_data.get("button_name", ""))
            self.position_var.set(state_data.get("position", "None"))
            self.position_player_var.set(state_data.get("position_player", ""))
            self.pf_action_str_var.set(state_data.get("pf_action_string", ""))
            self.on_pf_selection(None)
            self.on_flop_pattern_selection(None)
            self.on_turn_pattern_selection(None)
            self.on_river_pattern_selection(None)
            messagebox.showinfo("Loaded", f"State '{state_name}' loaded successfully.")
        else:
            messagebox.showerror("Error", f"State '{state_name}' not found.")
    
    def delete_state(self):
        selection = self.state_list.curselection()
        if not selection:
            messagebox.showerror("Error", "Please select a saved state to delete.")
            return
        state_name = self.state_list.get(selection[0])
        self.state_manager.delete_state(state_name)
        self.refresh_state_list()
        messagebox.showinfo("Deleted", f"State '{state_name}' deleted successfully.")
    
    def refresh_state_list(self):
        self.state_list.delete(0, tk.END)
        for state_name in self.state_manager.list_states():
            self.state_list.insert(tk.END, state_name)
    
    # ------------------------------
    # New: Show Betting Opportunities Popup
    # ------------------------------
    def show_betting_opportunities(self):
        """Show betting opportunities for the current hand."""
        if not self.current_hand:
            messagebox.showerror("Error", "No hand history loaded.")
            return
        
        # Create a new window for betting opportunities
        popup = tk.Toplevel(self)
        popup.title("Betting Opportunities")
        popup.geometry("1200x800")
        
        # Create a text widget with scrollbar
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        # Add title and separator
        text_widget.insert(tk.END, "Betting Opportunities\n")
        text_widget.insert(tk.END, "=" * 50 + "\n\n")
        
        # Get the hand history data
        hand_data = self.current_hand.get("hand_history_data")
        if not hand_data or not hasattr(hand_data, "betting_opportunities"):
            text_widget.insert(tk.END, "No betting opportunities available for this hand.\n")
        else:
            # Display each opportunity
            for i, opp in enumerate(hand_data.betting_opportunities, 1):
                text_widget.insert(tk.END, f"Opportunity {i}\n")
                text_widget.insert(tk.END, "-" * 30 + "\n")
                text_widget.insert(tk.END, f"Street: {opp.street}\n")
                text_widget.insert(tk.END, f"Type: {opp.opportunity_type}\n")
                text_widget.insert(tk.END, f"Player: {opp.player_position}\n")
                text_widget.insert(tk.END, f"Stack: ${opp.player_stack:.2f}\n")
                text_widget.insert(tk.END, f"Pot: ${opp.pot_size:.2f}\n")
                
                if opp.board_cards:
                    text_widget.insert(tk.END, f"Board: {' '.join(opp.board_cards)}\n")
                
                text_widget.insert(tk.END, f"Betting Sequence: {opp.get_betting_sequence_summary()}\n")
                text_widget.insert(tk.END, f"Normalized Sequence: {opp.normalized_betting_sequence}\n")
                text_widget.insert(tk.END, f"Available Actions: {', '.join(opp.available_actions)}\n")
                
                if opp.decision:
                    text_widget.insert(tk.END, f"Decision Made: {opp.decision}\n")
                if opp.outcome_bucket:
                    text_widget.insert(tk.END, f"Outcome: {opp.outcome_bucket}\n")
                if opp.bet_amount is not None:
                    text_widget.insert(tk.END, f"Bet Amount: ${opp.bet_amount:.2f}\n")
                if opp.additional_context:
                    text_widget.insert(tk.END, "Additional Context:\n")
                    for key, value in opp.additional_context.items():
                        text_widget.insert(tk.END, f"  {key}: {value}\n")
                
                text_widget.insert(tk.END, "\n")
        
        # Make the text widget read-only
        text_widget.config(state=tk.DISABLED)
        
    # Optionally, add scrollbars if needed.

    
    # ------------------------------
    # New: Show Hand Actions Popup
    # ------------------------------
    def check_bet_or_raise_folded(self, actions):
        """
        Given a list of Action objects (in order) for a particular street,
        returns a dictionary mapping the index of each bet/raise action to a boolean indicating
        whether that action is 'folded' (i.e. every subsequent action from a different player is a fold).
        """
        result = {}
        for i, act in enumerate(actions):
            if act.action_type in ('bet', 'raise'):
                bettor = act.player
                folded = True
                # Check subsequent actions (ignoring actions by the same player)
                for subsequent_act in actions[i+1:]:
                    if subsequent_act.player == bettor:
                        continue
                    if subsequent_act.action_type != 'fold':
                        folded = False
                        break
                result[i] = folded
        return result

    # ------------------------------
    # Modified: Show Hand Actions Popup
    # ------------------------------
    def show_hand_actions(self):
        """Display all actions in the hand history"""
        if not self.current_hand or not self.current_hand.get("hand_history_data"):
            messagebox.showerror("Error", "No hand history loaded.")
            return
            
        # Create a new window for displaying actions
        actions_window = tk.Toplevel(self)
        actions_window.title("Hand Actions")
        actions_window.geometry("800x600")
        
        # Create a text widget with scrollbar
        text_frame = ttk.Frame(actions_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        result_text = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        result_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=result_text.yview)
        
        # Display header
        hand_data = self.current_hand["hand_history_data"]
        result_text.insert(tk.END, f"Hand ID: {hand_data.hand_id}\n")
        result_text.insert(tk.END, f"Game Type: {hand_data.game_type}\n")
        result_text.insert(tk.END, f"Number of Players: {hand_data.number_of_players}\n")
        result_text.insert(tk.END, f"Small Blind: ${hand_data.sb_size:.2f}\n")
        result_text.insert(tk.END, f"Big Blind: ${hand_data.bb_size:.2f}\n")
        if hand_data.ante:
            result_text.insert(tk.END, f"Ante: ${hand_data.ante:.2f}\n")
        result_text.insert(tk.END, "\n")
        
        # Display actions for each street
        for street in ["anteing", "preflop", "flop", "turn", "river"]:
            actions = hand_data.actions.get(street, [])
            if actions:
                result_text.insert(tk.END, f"\n{street.upper()} ACTIONS:\n")
                result_text.insert(tk.END, "-" * 80 + "\n")
                result_text.insert(tk.END, f"{'Player':<20} {'Action':<10} {'Amount':<10} {'Total':<10} {'Norm Seq':<15} {'Additional Info'}\n")
                result_text.insert(tk.END, "-" * 80 + "\n")
                
                for action in actions:
                    amount_str = f"${action.bet_amount:.2f}" if action.bet_amount is not None else "N/A"
                    total_str = f"${action.total:.2f}" if action.total is not None else "N/A"
                    norm_seq = action.normalized_sequence if hasattr(action, "normalized_sequence") and action.normalized_sequence else "N/A"
                    additional_info = f"Pot: ${action.pot_size:.2f}" if hasattr(action, "pot_size") and action.pot_size is not None else ""
                    result_text.insert(tk.END, f"{action.player:<20} {action.action_type:<10} {amount_str:<10} {total_str:<10} {norm_seq:<15} {additional_info}\n")
                result_text.insert(tk.END, "\n")
        
        # Make the text widget read-only
        result_text.config(state=tk.DISABLED)
    
    def on_close(self):
        self.db.close()
        self.destroy()

    def load_hand(self, row):
        """Load a hand from the query results."""
        try:
            self.current_hand = {
                "hand_id": row[0],
                "raw_text": row[6],
                "hand_history_data": None
            }
            
            # Parse the hand history
            parser = get_hand_history_parser(row[6])
            hh_data = parser.parse(row[6])
            hh_data.hand_id = row[0]  # Set the hand ID
            hh_data.compute_betting_opportunities()  # Compute betting opportunities
            self.current_hand["hand_history_data"] = hh_data
        except Exception as e:
            messagebox.showerror("Error", f"Error loading hand: {str(e)}\nThe application will continue running.")
            self.current_hand = None

    def show_combined_view(self):
        """Show actions and betting opportunities side by side in an alternating format."""
        if not self.current_hand:
            messagebox.showerror("Error", "No hand history loaded.")
            return
            
        # Create a new window for the combined view
        popup = tk.Toplevel(self)
        popup.title("Combined Actions & Betting Opportunities")
        popup.geometry("1400x800")
        
        # Create a text widget with scrollbar
        text_frame = ttk.Frame(popup)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar.config(command=text_widget.yview)
        
        # Add title and separator
        text_widget.insert(tk.END, "Combined Actions & Betting Opportunities\n")
        text_widget.insert(tk.END, "=" * 100 + "\n\n")
        
        # Get the hand history data
        hand_data = self.current_hand.get("hand_history_data")
        if not hand_data or not hasattr(hand_data, "betting_opportunities"):
            text_widget.insert(tk.END, "No data available for this hand.\n")
        else:
            # Create a list of all actions across all streets, skipping anteing
            all_actions = []
            for street in ["preflop", "flop", "turn", "river"]:
                for action in hand_data.actions.get(street, []):
                    all_actions.append((street, action))
            
            # Create a list of all betting opportunities
            all_opportunities = hand_data.betting_opportunities
            
            # Combine and sort by sequence
            combined_items = []
            action_index = 0
            opp_index = 0
            
            # Skip the first opportunity (which is for the blinds)
            if all_opportunities:
                opp_index = 1
            
            while action_index < len(all_actions) or opp_index < len(all_opportunities):
                # Add action if available
                if action_index < len(all_actions):
                    street, action = all_actions[action_index]
                    combined_items.append(("action", street, action))
                    action_index += 1
                
                # Add opportunity if available
                if opp_index < len(all_opportunities):
                    opp = all_opportunities[opp_index]
                    combined_items.append(("opportunity", opp.street, opp))
                    opp_index += 1
            
            # Display the combined items
            for item_type, street, item in combined_items:
                if item_type == "action":
                    # Format action
                    text_widget.insert(tk.END, f"Action on {street.upper()}:\n")
                    text_widget.insert(tk.END, "-" * 50 + "\n")
                    text_widget.insert(tk.END, f"Player: {item.player}\n")
                    text_widget.insert(tk.END, f"Type: {item.action_type}\n")
                    if item.bet_amount is not None:
                        text_widget.insert(tk.END, f"Amount: ${item.bet_amount:.2f}\n")
                    if item.total is not None:
                        text_widget.insert(tk.END, f"Total: ${item.total:.2f}\n")
                    if item.pot_size is not None:
                        text_widget.insert(tk.END, f"Pot Size: ${item.pot_size:.2f}\n")
                else:
                    # Format opportunity
                    text_widget.insert(tk.END, f"Betting Opportunity on {street.upper()}:\n")
                    text_widget.insert(tk.END, "-" * 50 + "\n")
                    text_widget.insert(tk.END, f"Type: {item.opportunity_type}\n")
                    text_widget.insert(tk.END, f"Player: {item.player_position}\n")
                    text_widget.insert(tk.END, f"Stack: ${item.player_stack:.2f}\n")
                    text_widget.insert(tk.END, f"Pot: ${item.pot_size:.2f}\n")
                    if item.board_cards:
                        text_widget.insert(tk.END, f"Board: {' '.join(item.board_cards)}\n")
                    text_widget.insert(tk.END, f"Betting Sequence: {item.get_betting_sequence_summary()}\n")
                    text_widget.insert(tk.END, f"Normalized Sequence: {item.normalized_betting_sequence}\n")
                    text_widget.insert(tk.END, f"Available Actions: {', '.join(item.available_actions)}\n")
                
            text_widget.insert(tk.END, "\n")  

        # Make the text widget read-only
        text_widget.config(state=tk.DISABLED)

    def show_tree(self):
        """Display the hand history tree structure"""
        if not self.current_hand or not self.current_hand.get("hand_history_data"):
            messagebox.showerror("Error", "No hand history data loaded.")
            return
            
        # Get the hand history tree from the hand history data
        hand_history_data = self.current_hand["hand_history_data"]
        if not hand_history_data.hand_history_tree:
            messagebox.showerror("Error", "No hand history tree available.")
            return
            
        # Create a new window for the tree view
        tree_window = tk.Toplevel(self)
        tree_window.title("Hand History Tree Structure")
        tree_window.geometry("800x600")
        
        # Create a text widget with scrollbar
        text_frame = ttk.Frame(tree_window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        text_widget = tk.Text(text_frame, wrap=tk.WORD, yscrollcommand=scrollbar.set)
        text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=text_widget.yview)
        
        # Get all nodes from the tree
        nodes = hand_history_data.hand_history_tree.get_all_nodes()
        
        # Print header
        text_widget.insert(tk.END, "Hand History Tree Structure\n")
        text_widget.insert(tk.END, "=" * 80 + "\n\n")
        
        # Print each node with proper indentation
        for i, node in enumerate(nodes):
            # Add indentation based on node type
            indent = "  " * i
            
            # Print node type and basic info
            text_widget.insert(tk.END, f"{indent}Node {i+1}: {node.node_type.value}\n")
            text_widget.insert(tk.END, f"{indent}Street: {node.street}\n")
            text_widget.insert(tk.END, f"{indent}Current Bet Level: ${node.current_bet_level:.2f}\n")
            text_widget.insert(tk.END, f"{indent}Pot Size: ${node.pot_size:.2f}\n")
            
            # Print node-specific details
            if isinstance(node, ForcedAction):
                text_widget.insert(tk.END, f"{indent}Player: {node.player}\n")
                text_widget.insert(tk.END, f"{indent}Action Type: {node.action_type}\n")
                text_widget.insert(tk.END, f"{indent}Amount: ${node.amount:.2f}\n")
            elif isinstance(node, PlayerAction):
                text_widget.insert(tk.END, f"{indent}Player: {node.player}\n")
                text_widget.insert(tk.END, f"{indent}Action Type: {node.action_type}\n")
                text_widget.insert(tk.END, f"{indent}Parent Pot Size: ${node.parent_pot_size:.2f}\n")
                # Find the corresponding betting opportunity for this action
                for opp in hand_history_data.betting_opportunities:
                    if opp.street == node.street and opp.player_position == node.player:
                        text_widget.insert(tk.END, f"{indent}Normalized Sequence: {opp.normalized_betting_sequence}\n")
                        break
                if node.bet_amount is not None:
                    text_widget.insert(tk.END, f"{indent}Bet Amount: ${node.bet_amount:.2f}\n")
                if node.total is not None:
                    text_widget.insert(tk.END, f"{indent}Total: ${node.total:.2f}\n")
            elif isinstance(node, DecisionPoint):
                text_widget.insert(tk.END, f"{indent}Player: {node.player}\n")
                text_widget.insert(tk.END, f"{indent}Opportunity Type: {node.opportunity_type}\n")
                text_widget.insert(tk.END, f"{indent}Player Stack: ${node.player_stack:.2f}\n")
                text_widget.insert(tk.END, f"{indent}Available Actions: {', '.join(node.available_actions)}\n")
                text_widget.insert(tk.END, f"{indent}Min Raise: ${node.min_raise:.2f}\n")
                text_widget.insert(tk.END, f"{indent}Max Raise: ${node.max_raise:.2f}\n")
            elif isinstance(node, StreetChange):
                text_widget.insert(tk.END, f"{indent}Community Cards: {' '.join(node.community_cards)}\n")
            
            # Print active players
            text_widget.insert(tk.END, f"{indent}Active Players:\n")
            for player in node.active_players:
                text_widget.insert(tk.END, f"{indent}  - {player.player} (Stack: ${player.stack:.2f}, "
                                         f"Remaining: ${player.remaining_stack:.2f}, "
                                         f"Contribution: ${player.total_contribution:.2f}, "
                                         f"Position: {player.position or 'N/A'}, "
                                         f"Active: {player.is_active})\n")
            
            text_widget.insert(tk.END, "\n")
        
        # Make the text widget read-only
        text_widget.config(state=tk.DISABLED)

    def refresh_all_dropdowns(self):
        """Refresh all dropdown lists with latest data from database."""
        # Refresh preflop actions
        self.refresh_pf_actions()
        
        # Refresh postflop patterns
        patterns = self.load_postflop_patterns()
        pattern_values = ["None"] + sorted(patterns.keys())
        
        # Update flop patterns
        current_flop = self.flop_pattern_var.get()
        self.flop_pattern_combo['values'] = pattern_values
        if current_flop in pattern_values:
            self.flop_pattern_var.set(current_flop)
        else:
            self.flop_pattern_var.set("None")
        
        # Update turn patterns
        current_turn = self.turn_pattern_var.get()
        self.turn_pattern_combo['values'] = pattern_values
        if current_turn in pattern_values:
            self.turn_pattern_var.set(current_turn)
        else:
            self.turn_pattern_var.set("None")
        
        # Update river patterns
        current_river = self.river_pattern_var.get()
        self.river_pattern_combo['values'] = pattern_values
        if current_river in pattern_values:
            self.river_pattern_var.set(current_river)
        else:
            self.river_pattern_var.set("None")
        
        messagebox.showinfo("Success", "All dropdowns have been refreshed with latest data.")

    def on_pf_action_no_toggle(self):
        if self.pf_action_no_var.get():
            # Checked: show preflop action number
            self.pf_seq_label.config(text="Preflop Action Number:")
            self.pf_actions = self.load_pf_actions()
            pf_options = self.build_pf_options(self.pf_actions)
            self.pf_seq_combo['values'] = pf_options
            if pf_options:
                self.pf_seq_var.set(pf_options[0])
                self.on_pf_selection(None)
            else:
                self.pf_seq_var.set("")
                self.pf_action_str_var.set("")
            self.pf_seq_combo.bind("<<ComboboxSelected>>", self.on_pf_selection)
            self.pf_sql_pattern_var.set("")
            self.pf_sql_pattern_entry.grid_remove()
            self.pf_action_str_label.grid()
            self.pf_action_entry.grid()
        else:
            # Unchecked: show preflop pattern
            self.pf_seq_label.config(text="Preflop Pattern:")
            patterns = self.load_preflop_patterns()
            pattern_options = ["None"] + sorted(patterns.keys())
            self.pf_seq_combo['values'] = pattern_options
            if pattern_options:
                self.pf_seq_var.set(pattern_options[0])
            else:
                self.pf_seq_var.set("")
            self.pf_action_str_var.set("")
            self.pf_seq_combo.unbind("<<ComboboxSelected>>")
            self.pf_seq_combo.bind("<<ComboboxSelected>>", self.on_preflop_pattern_selection)
            # Set the SQL pattern for the initial selection
            self.on_preflop_pattern_selection(None)
            self.pf_sql_pattern_entry.grid()
            self.pf_action_str_label.grid_remove()
            self.pf_action_entry.grid_remove()

    def on_preflop_pattern_selection(self, event):
        selected = self.pf_seq_var.get().strip()
        if selected == "None":
            self.pf_sql_pattern_var.set("")
        else:
            patterns = self.load_preflop_patterns()
            sql_pattern = patterns.get(selected, "")
            self.pf_sql_pattern_var.set(sql_pattern)

    def load_preflop_patterns(self):
        query = "SELECT pattern_name, sql_pattern FROM action_patterns WHERE applies_to = 'preflop' ORDER BY pattern_name"
        patterns = {}
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            for row in rows:
                pattern_name, sql_pattern = row
                patterns[pattern_name.strip()] = sql_pattern.strip()
        except Exception as e:
            print("Error retrieving preflop patterns from DB:", e)
        return patterns

if __name__ == "__main__":
    app = HandHistoryExplorer()
    app.mainloop()
