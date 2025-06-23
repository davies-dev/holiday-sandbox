#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from db_access import DatabaseAccess
from config import DB_PARAMS, GTO_BASE_PATH
import os
import re
from pathlib import Path

class GTOAdmin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("GTO+ File Mappings Admin")
        self.geometry("900x700")
        
        self.db = DatabaseAccess(**DB_PARAMS)
        self.build_ui()
    
    def build_ui(self):
        # Import section
        import_frame = ttk.LabelFrame(self, text="Import Settings")
        import_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(import_frame, text="Import from settings.txt", 
                  command=self.import_settings).pack(pady=5)
        
        # Mappings display
        mappings_frame = ttk.LabelFrame(self, text="Current Mappings")
        mappings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Treeview for mappings
        columns = ("State Name", "Game Type", "File Path", "Description")
        self.tree = ttk.Treeview(mappings_frame, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            if col == "File Path":
                self.tree.column(col, width=300)
            else:
                self.tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(mappings_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Button(button_frame, text="Refresh", command=self.refresh_mappings).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete Selected", command=self.delete_mapping).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Add Manual", command=self.add_manual).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Test File Location", command=self.test_file_location).pack(side=tk.LEFT, padx=5)
        
        self.refresh_mappings()
    
    def get_existing_game_types(self):
        """Get existing game types from database for dropdown"""
        return self.db.get_game_types()
    
    def find_gto_file_in_locations(self, original_path):
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
                return search_path
        
        return None
    
    def import_settings(self):
        """Import GTO+ mappings from settings.txt file"""
        file_path = filedialog.askopenfilename(
            title="Select settings.txt file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            imported = 0
            errors = 0
            
            for line in lines:
                line = line.strip()
                if not line or not line.startswith('url,'):
                    continue
                
                # Parse: url,filepath,description
                parts = line.split(',', 2)
                if len(parts) < 3:
                    errors += 1
                    continue
                
                _, file_path, description = parts
                
                # Extract state name from description (e.g., "37 - btn v bb 2.5x" -> "37")
                state_match = re.match(r'(\d+)\s*-\s*', description)
                if not state_match:
                    errors += 1
                    continue
                
                state_name = state_match.group(1)
                game_type = "zoom_cash_6max"  # Default for 6-max settings
                
                # Use pathlib for cross-platform path handling
                file_path = str(Path(file_path))
                
                # Insert into database
                if self.db.insert_gto_mapping(state_name, game_type, file_path, description):
                    imported += 1
                else:
                    errors += 1
            
            messagebox.showinfo("Import Complete", 
                              f"Imported: {imported}\nErrors: {errors}")
            self.refresh_mappings()
            
        except Exception as e:
            messagebox.showerror("Import Error", f"Error importing settings: {e}")
    
    def refresh_mappings(self):
        """Refresh the mappings display"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Load from database
        mappings = self.db.get_all_gto_mappings()
        for mapping in mappings:
            self.tree.insert("", tk.END, values=(
                mapping['state_name'],
                mapping['game_type'],
                mapping['gto_file_path'],
                mapping['description']
            ))
    
    def delete_mapping(self):
        """Delete selected mapping"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mapping to delete")
            return
        
        item = self.tree.item(selection[0])
        state_name = item['values'][0]
        game_type = item['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Delete mapping for {state_name}?"):
            if self.db.delete_gto_mapping(state_name, game_type):
                self.refresh_mappings()
                messagebox.showinfo("Success", "Mapping deleted successfully")
            else:
                messagebox.showerror("Error", "Failed to delete mapping")
    
    def test_file_location(self):
        """Test if the selected mapping's file can be found"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a mapping to test")
            return
        
        item = self.tree.item(selection[0])
        state_name = item['values'][0]
        game_type = item['values'][1]
        original_path = item['values'][2]
        
        # Search for the file in multiple locations
        actual_location = self.find_gto_file_in_locations(original_path)
        
        if actual_location:
            messagebox.showinfo("File Found", 
                              f"State: {state_name}\n"
                              f"Game Type: {game_type}\n"
                              f"File found at: {actual_location}")
        else:
            # Show all the paths we searched
            from pathlib import Path
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
            
            search_paths_str = "\n".join([str(p) for p in search_paths])
            messagebox.showwarning("File Not Found", 
                                  f"State: {state_name}\n"
                                  f"Game Type: {game_type}\n"
                                  f"File not found in any of these locations:\n\n{search_paths_str}")
    
    def add_manual(self):
        """Add mapping manually with enhanced UI"""
        # Create a dialog for manual entry
        dialog = tk.Toplevel(self)
        dialog.title("Add GTO+ Mapping")
        dialog.geometry("500x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # State Name
        ttk.Label(dialog, text="State Name:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.E)
        state_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=state_var, width=20).grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Game Type (Combobox with existing types)
        ttk.Label(dialog, text="Game Type:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.E)
        game_var = tk.StringVar(value="zoom_cash_6max")
        existing_types = self.get_existing_game_types()
        if not existing_types:
            existing_types = ["zoom_cash_6max", "spingo", "husng spots"]
        game_combo = ttk.Combobox(dialog, textvariable=game_var, values=existing_types, width=20)
        game_combo.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        
        # File Path with Browse button
        ttk.Label(dialog, text="File Path:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.E)
        path_var = tk.StringVar()
        path_frame = ttk.Frame(dialog)
        path_frame.grid(row=2, column=1, padx=5, pady=5, sticky=tk.EW)
        
        path_entry = ttk.Entry(path_frame, textvariable=path_var, width=50)
        path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        def browse_file():
            file_path = filedialog.askopenfilename(
                title="Select GTO+ file",
                filetypes=[("GTO+ files", "*.gto"), ("All files", "*.*")]
            )
            if file_path:
                selected_path = Path(file_path)
                path_var.set(str(selected_path))
                
                # Check if this file exists in our processing directories
                actual_location = self.find_gto_file_in_locations(selected_path)
                if actual_location and actual_location != selected_path:
                    messagebox.showinfo("File Location", 
                                      f"File found in processing directory:\n{actual_location}\n\n"
                                      f"Original selection: {selected_path}")
        
        ttk.Button(path_frame, text="Browse...", command=browse_file).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Description
        ttk.Label(dialog, text="Description:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.E)
        desc_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=desc_var, width=50).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=20)
        
        def save():
            try:
                # Validate inputs
                if not state_var.get().strip():
                    messagebox.showerror("Error", "State name is required")
                    return
                if not path_var.get().strip():
                    messagebox.showerror("Error", "File path is required")
                    return
                
                # Use pathlib for cross-platform path handling
                file_path = str(Path(path_var.get().strip()))
                
                if self.db.insert_gto_mapping(
                    state_var.get().strip(), 
                    game_var.get().strip(), 
                    file_path, 
                    desc_var.get().strip()
                ):
                    self.refresh_mappings()
                    dialog.destroy()
                    messagebox.showinfo("Success", "Mapping added successfully")
                else:
                    messagebox.showerror("Error", "Failed to add mapping")
            except Exception as e:
                messagebox.showerror("Error", f"Error adding mapping: {e}")
        
        def cancel():
            dialog.destroy()
        
        ttk.Button(button_frame, text="Save", command=save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights for responsive layout
        dialog.columnconfigure(1, weight=1)
        path_frame.columnconfigure(0, weight=1)

if __name__ == "__main__":
    app = GTOAdmin()
    app.mainloop() 