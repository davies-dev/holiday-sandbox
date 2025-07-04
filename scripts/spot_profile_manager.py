#!/usr/bin/env python3
"""
Spot Profile Manager - A window for managing which spots are assigned to which game profiles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Dict

class SpotProfileManager(tk.Toplevel):
    def __init__(self, parent, db_access):
        super().__init__(parent)
        self.db = db_access
        self.parent = parent
        
        self.title("Spot Profile Manager")
        self.geometry("800x600")
        self.transient(parent)
        self.grab_set()
        
        # Center the window on the parent
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() // 2) - (self.winfo_width() // 2)
        y = parent.winfo_y() + (parent.winfo_height() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")
        
        self.build_ui()
        self.load_data()
        
    def build_ui(self):
        """Build the user interface."""
        # Main frame
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="Manage Spot Profile Assignments", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=(0, 10))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                               text="Select a spot from the list below, then check/uncheck the game profiles\n"
                                    "you want to assign it to. Click 'Save Changes' to apply.",
                               justify=tk.CENTER)
        instructions.pack(pady=(0, 10))
        
        # Create paned window for spots list and profile selection
        paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Left side - Spots list
        left_frame = ttk.Frame(paned)
        paned.add(left_frame, weight=1)
        
        ttk.Label(left_frame, text="Spots:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Spots listbox with scrollbar
        spots_frame = ttk.Frame(left_frame)
        spots_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.spots_listbox = tk.Listbox(spots_frame, font=("Arial", 10))
        spots_scrollbar = ttk.Scrollbar(spots_frame, orient=tk.VERTICAL, command=self.spots_listbox.yview)
        self.spots_listbox.configure(yscrollcommand=spots_scrollbar.set)
        
        self.spots_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        spots_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.spots_listbox.bind('<<ListboxSelect>>', self.on_spot_selected)
        
        # Right side - Profile selection
        right_frame = ttk.Frame(paned)
        paned.add(right_frame, weight=1)
        
        ttk.Label(right_frame, text="Game Profiles:", font=("Arial", 12, "bold")).pack(anchor=tk.W)
        
        # Profile checkboxes frame with scrollbar
        profiles_frame = ttk.Frame(right_frame)
        profiles_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Create a canvas with scrollbar for the checkboxes
        canvas = tk.Canvas(profiles_frame)
        scrollbar = ttk.Scrollbar(profiles_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.profiles_inner_frame = ttk.Frame(canvas)
        
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        canvas.create_window((0, 0), window=self.profiles_inner_frame, anchor=tk.NW)
        self.profiles_inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        self.save_button = ttk.Button(button_frame, text="Save Changes", command=self.save_changes)
        self.save_button.pack(side=tk.RIGHT, padx=5)
        
        self.refresh_button = ttk.Button(button_frame, text="Refresh", command=self.load_data)
        self.refresh_button.pack(side=tk.RIGHT, padx=5)
        
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.LEFT, padx=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(fill=tk.X, pady=(5, 0))
        
    def load_data(self):
        """Load spots and profiles data."""
        try:
            self.status_var.set("Loading data...")
            self.update()
            
            # Load spots
            spots_data = self.db.get_all_spots_with_profiles()
            self.spots = {row[0]: {"name": row[1], "description": row[2], "profiles": row[3] or []} 
                         for row in spots_data}
            
            # Load profiles
            profiles_data = self.db.get_all_game_profiles_with_ids()
            self.profiles = {row[0]: row[1] for row in profiles_data}
            
            # Update spots listbox
            self.spots_listbox.delete(0, tk.END)
            for spot_id, spot_info in self.spots.items():
                profile_text = f" ({', '.join(spot_info['profiles'])})" if spot_info['profiles'] else ""
                self.spots_listbox.insert(tk.END, f"{spot_info['name']}{profile_text}")
            
            # Create profile checkboxes
            self.create_profile_checkboxes()
            
            self.status_var.set(f"Loaded {len(self.spots)} spots and {len(self.profiles)} profiles")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")
            self.status_var.set("Error loading data")
    
    def create_profile_checkboxes(self):
        """Create checkboxes for all game profiles."""
        # Clear existing checkboxes
        for widget in self.profiles_inner_frame.winfo_children():
            widget.destroy()
        
        self.profile_vars = {}
        
        for profile_id, profile_name in self.profiles.items():
            var = tk.BooleanVar()
            self.profile_vars[profile_id] = var
            
            checkbox = ttk.Checkbutton(self.profiles_inner_frame, text=profile_name, variable=var)
            checkbox.pack(anchor=tk.W, padx=5, pady=2)
    
    def on_spot_selected(self, event):
        """Handle spot selection."""
        selection = self.spots_listbox.curselection()
        if not selection:
            return
        
        # Get the selected spot
        spot_index = selection[0]
        spot_ids = list(self.spots.keys())
        if spot_index >= len(spot_ids):
            return
        
        spot_id = spot_ids[spot_index]
        spot_info = self.spots[spot_id]
        
        # Update status
        self.status_var.set(f"Selected: {spot_info['name']}")
        
        # Update checkboxes to reflect current assignments
        for profile_id, var in self.profile_vars.items():
            profile_name = self.profiles[profile_id]
            var.set(profile_name in spot_info['profiles'])
    
    def save_changes(self):
        """Save the current profile assignments for the selected spot."""
        selection = self.spots_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a spot first.")
            return
        
        spot_index = selection[0]
        spot_ids = list(self.spots.keys())
        if spot_index >= len(spot_ids):
            return
        
        spot_id = spot_ids[spot_index]
        spot_info = self.spots[spot_id]
        
        # Get selected profile IDs
        selected_profile_ids = []
        for profile_id, var in self.profile_vars.items():
            if var.get():
                selected_profile_ids.append(profile_id)
        
        try:
            self.status_var.set("Saving changes...")
            self.update()
            
            # Update the database
            success = self.db.update_spot_profiles(spot_id, selected_profile_ids)
            
            if success:
                # Update local data
                selected_profile_names = [self.profiles[pid] for pid in selected_profile_ids]
                self.spots[spot_id]['profiles'] = selected_profile_names
                
                # Update the listbox display
                profile_text = f" ({', '.join(selected_profile_names)})" if selected_profile_names else ""
                self.spots_listbox.delete(spot_index)
                self.spots_listbox.insert(spot_index, f"{spot_info['name']}{profile_text}")
                self.spots_listbox.selection_set(spot_index)
                
                self.status_var.set(f"Saved changes for {spot_info['name']}")
                messagebox.showinfo("Success", f"Profile assignments updated for '{spot_info['name']}'")
            else:
                self.status_var.set("Error saving changes")
                messagebox.showerror("Error", "Failed to save changes")
                
        except Exception as e:
            self.status_var.set("Error saving changes")
            messagebox.showerror("Error", f"Failed to save changes: {e}")

def open_spot_profile_manager(parent, db_access):
    """Open the Spot Profile Manager window."""
    manager = SpotProfileManager(parent, db_access)
    return manager 