#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from db_access import DatabaseAccess
from query_builder import QueryBuilder, Condition, SortCriterion
from saved_state_manager import SavedStateManager
from spot_profile_manager import open_spot_profile_manager
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
import os
import webbrowser
import pathlib
import urllib.parse
from datetime import datetime, timedelta
from scripts.config import DB_PARAMS, GTO_BASE_PATH, GTO_EXECUTABLE_PATH
from scripts.file_utils import find_gto_file_in_locations
import subprocess
#from betting_op import BettingOppurtunity
#from betting_op import * 
#------------------------------
#New: BettingOpportunity Data Structure
#------------------------------

# BettingOpportunity class is now imported from kk10.py

# ------------------------------
# Review Panel Class
# ------------------------------
class ReviewPanel(ttk.Frame):
    def __init__(self, parent, db_access, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.db = db_access
        self.current_hand_id = None
        self.current_hh_data = None  # To store the full hand data object
        self.current_spot = None     # To store the matched spot dictionary
        self.current_doc_id = None   # To store the currently selected document id

        # --- CONFIGURATION (should be correct from before) ---
        self.OBSIDIAN_VAULT_PATH = "C:/projects/hh-explorer-vault/hh_explorer"
        self.OBSIDIAN_VAULT_NAME = "hh_explorer"

        # --- NEW: Spot Info Frame ---
        spot_frame = ttk.LabelFrame(self, text="Spot Information")
        spot_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)
        
        self.spot_name_var = tk.StringVar(value="No spot matched.")
        spot_label = ttk.Label(spot_frame, textvariable=self.spot_name_var, font=("Segoe UI", 10, "bold"), wraplength=300)
        spot_label.pack(pady=5, padx=5)

        # --- Analysis Tools Frame ---
        tools_frame = ttk.LabelFrame(self, text="Analysis Tools")
        tools_frame.pack(fill=tk.X, padx=5, pady=5, side=tk.TOP)

        self.open_default_btn = ttk.Button(tools_frame, text="Open Default Document", command=self.open_default_document, state=tk.DISABLED)
        self.open_default_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- NEW: Move to Processing Button ---
        self.move_to_processing_btn = ttk.Button(tools_frame, text="Move to Processing", command=self.move_to_processing, state=tk.DISABLED)
        self.move_to_processing_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- NEW: Status Label for Move Operation ---
        self.move_status_var = tk.StringVar(value="")
        self.move_status_label = ttk.Label(tools_frame, textvariable=self.move_status_var, font=("Segoe UI", 9), foreground="green")
        self.move_status_label.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.define_spot_btn = ttk.Button(tools_frame, text="Define New Spot", command=self.define_new_spot, state=tk.DISABLED)
        self.define_spot_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- NEW: Copy Flop Button ---
        self.copy_flop_btn = ttk.Button(tools_frame, text="Copy Flop", command=self.copy_flop_to_clipboard, state=tk.DISABLED)
        self.copy_flop_btn.pack(side=tk.LEFT, padx=5, pady=5)
        
        # --- NEW: Copy Flop Status Label ---
        self.copy_flop_status_var = tk.StringVar(value="")
        self.copy_flop_status_label = ttk.Label(tools_frame, textvariable=self.copy_flop_status_var, font=("Segoe UI", 9), foreground="blue")
        self.copy_flop_status_label.pack(side=tk.LEFT, padx=5, pady=5)



        # --- Widgets ---
        # --- Relevant Study Notes ---
        study_frame = ttk.LabelFrame(self, text="Relevant Study Notes")
        study_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.study_notes_tree = ttk.Treeview(study_frame, columns=("id", "title", "path"), show="headings")
        self.study_notes_tree.heading("id", text="ID")
        self.study_notes_tree.column("id", width=40, anchor='center')
        self.study_notes_tree.heading("title", text="Title")
        self.study_notes_tree.column("title", width=150)
        self.study_notes_tree.heading("path", text="File")
        self.study_notes_tree.column("path", width=200)
        self.study_notes_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.study_notes_tree.bind("<Double-1>", self._open_study_note)

        note_frame = ttk.LabelFrame(self, text="Hand Notes")
        note_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.notes_tree = ttk.Treeview(note_frame, columns=("created_at"), show="headings")
        self.notes_tree.heading("#0", text="Note File") # The implicit first column
        self.notes_tree.heading("created_at", text="Date Created")
        self.notes_tree.column("#0", width=200, anchor='w')
        self.notes_tree.column("created_at", width=150, anchor='center')
        self.notes_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.notes_tree.bind("<Double-1>", self.open_selected_note)

        new_note_btn = ttk.Button(note_frame, text="Create New Note", command=self.create_new_hand_note)
        new_note_btn.pack(side=tk.BOTTOM, pady=5)

        # --- Status Widgets ---
        status_frame = ttk.LabelFrame(self, text="Review Status")
        status_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.status_var = tk.StringVar()
        status_options = ['unreviewed', 'eyeballed', 'marked_for_review', 'waiting_on_gto', 'completed']
        self.status_combo = ttk.Combobox(status_frame, textvariable=self.status_var, values=status_options, state="readonly")
        self.status_combo.pack(side=tk.LEFT, padx=5, pady=5)
        
        save_status_btn = ttk.Button(status_frame, text="Save Status", command=self.save_review_status)
        save_status_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # --- Document List Frame ---
        doc_frame = ttk.LabelFrame(self, text="Linked Documents")
        doc_frame.pack(fill=tk.X, padx=5, pady=5)
        self.doc_list = ttk.Treeview(doc_frame, columns=("title", "file_path", "is_default"), show="headings", selectmode="browse", height=3)
        self.doc_list.heading("title", text="Title")
        self.doc_list.heading("file_path", text="File Path")
        self.doc_list.heading("is_default", text="Default?")
        self.doc_list.pack(fill=tk.X, padx=5, pady=5)
        self.doc_list.bind("<<TreeviewSelect>>", self.on_doc_select)
        
        # --- Document Management Buttons ---
        doc_button_frame = ttk.Frame(doc_frame)
        doc_button_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.add_document_btn = ttk.Button(doc_button_frame, text="Add Document", command=self.add_document_to_spot, state=tk.DISABLED)
        self.add_document_btn.pack(side=tk.LEFT, padx=5)
        
        self.set_default_btn = ttk.Button(doc_button_frame, text="Set as Default Document", command=self.set_default_document, state=tk.DISABLED)
        self.set_default_btn.pack(side=tk.LEFT, padx=5)

    def load_hand_data(self, hand_id, hh_data):
        self.current_hand_id = hand_id
        self.current_hh_data = hh_data
        
        # Reset UI state
        self.open_default_btn.config(state=tk.DISABLED)
        self.define_spot_btn.config(state=tk.DISABLED)
        self.copy_flop_btn.config(state=tk.DISABLED)
        self.copy_flop_status_var.set("")
        self.spot_name_var.set("Finding spot...")
        self.current_spot = None # Clear previous spot

        # Find matching spot using the new DB method
        matched_spot = self.db.find_spot_for_hand(hh_data)
        
        if matched_spot:
            self.current_spot = matched_spot
            self.spot_name_var.set(f"Spot: {matched_spot['spot_name']}\n{matched_spot['description']}")
            self.open_default_btn.config(state=tk.NORMAL)
            self.move_to_processing_btn.config(state=tk.NORMAL)
            self.add_document_btn.config(state=tk.NORMAL)
        else:
            pf_seq = hh_data.get_simple_action_sequence('preflop')
            self.spot_name_var.set(f"Unnamed Spot\n(Sequence: {pf_seq})")
            self.define_spot_btn.config(state=tk.NORMAL)
        
        # Enable copy flop button for any loaded hand
        self.copy_flop_btn.config(state=tk.NORMAL)

        # Load status and notes as before
        review_data = self.db.get_or_create_review_data(hand_id)
        self.status_var.set(review_data.get('review_status', 'unreviewed'))
        self._refresh_notes_tree()

        # --- NEW: Find and display relevant study notes ---
        for item in self.study_notes_tree.get_children():
            self.study_notes_tree.delete(item)
            
        relevant_docs = self.db.find_relevant_study_documents(hh_data)
        for doc_id, title, file_path in relevant_docs:
            self.study_notes_tree.insert("", tk.END, values=(doc_id, title, file_path))

        # Populate document list
        self.doc_list.delete(*self.doc_list.get_children())
        if self.current_spot:
            docs = self.db.get_documents_for_spot(self.current_spot['id'])
            for doc in docs:
                self.doc_list.insert("", "end", iid=doc['id'], values=(doc['title'], doc['file_path'], "Yes" if doc['is_default'] else ""))
        self.set_default_btn.config(state=tk.DISABLED)
        self.current_doc_id = None

    def _refresh_notes_tree(self):
        """Clears and re-populates the notes tree from the database."""
        for item in self.notes_tree.get_children():
            self.notes_tree.delete(item)
        if self.current_hand_id:
            notes = self.db.get_notes_for_hand(self.current_hand_id)
            for note_path, created_at in notes:
                filename = os.path.basename(note_path)
                self.notes_tree.insert("", tk.END, text=filename, values=(created_at.strftime("%Y-%m-%d %H:%M"),))

    def create_new_hand_note(self):
        """Creates a new unique note file and links it to the current hand."""
        if not self.current_hand_id:
            messagebox.showerror("Error", "No hand is loaded.")
            return
        
        try:
            # Generate a unique filename using a precise timestamp
            notes_dir = os.path.join(self.OBSIDIAN_VAULT_PATH, "HandNotes")
            
            # Debug information
            print(f"Creating notes directory: {notes_dir}")
            print(f"OBSIDIAN_VAULT_PATH: {self.OBSIDIAN_VAULT_PATH}")
            
            # Create directory with better error handling
            try:
                os.makedirs(notes_dir, exist_ok=True)
                print(f"Successfully created/verified directory: {notes_dir}")
            except PermissionError as e:
                error_msg = f"Permission denied creating directory: {notes_dir}\n\nPlease check:\n1. Directory permissions\n2. Run as administrator if needed\n3. Choose a different path"
                messagebox.showerror("Permission Error", error_msg)
                print(f"Permission error: {e}")
                return
            except Exception as e:
                error_msg = f"Error creating directory: {notes_dir}\n\nError: {str(e)}"
                messagebox.showerror("Directory Error", error_msg)
                print(f"Directory creation error: {e}")
                return
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            note_path = os.path.join(notes_dir, f"Hand_{self.current_hand_id}_{timestamp}.md")
            
            print(f"Creating note file: {note_path}")
            
            # Create the file on disk and add its record to the database
            try:
                with open(note_path, 'w') as f:
                    f.write(f"# Notes for Hand ID: {self.current_hand_id}\n")
                    f.write(f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                print(f"Successfully created note file: {note_path}")
                
                # Add to database
                success = self.db.add_note_for_hand(self.current_hand_id, note_path)
                if not success:
                    messagebox.showerror("Database Error", "Failed to add note to database.")
                    return
                
                # Refresh the list in the UI and open the new note immediately
                self._refresh_notes_tree()
                
                # Open the note in Obsidian using the Obsidian URI scheme
                try:
                    # Get the path of the note relative to the vault's root directory
                    relative_path = os.path.relpath(note_path, self.OBSIDIAN_VAULT_PATH)
                    # URL-encode the path to handle spaces and special characters
                    encoded_path = urllib.parse.quote(relative_path.replace(os.sep, '/')) # Ensure forward slashes
                    
                    # Construct the final URI
                    obsidian_uri = f"obsidian://open?vault={self.OBSIDIAN_VAULT_NAME}&file={encoded_path}"
                    
                    print(f"Opening Obsidian URI: {obsidian_uri}")
                    webbrowser.open(obsidian_uri)
                    print(f"Opened note in Obsidian: {note_path}")
                except Exception as e:
                    print(f"Warning: Could not open note in Obsidian: {e}")
                    messagebox.showinfo("Note Created", f"Note created successfully at:\n{note_path}\n\nPlease open it manually in Obsidian.")
                
            except PermissionError as e:
                error_msg = f"Permission denied creating file: {note_path}\n\nPlease check file permissions."
                messagebox.showerror("File Permission Error", error_msg)
                print(f"File permission error: {e}")
                return
            except Exception as e:
                error_msg = f"Error creating note file: {note_path}\n\nError: {str(e)}"
                messagebox.showerror("File Error", error_msg)
                print(f"File creation error: {e}")
                return
                
        except Exception as e:
            error_msg = f"Unexpected error creating note: {str(e)}"
            messagebox.showerror("Unexpected Error", error_msg)
            print(f"Unexpected error in create_new_hand_note: {e}")
            return

    def open_selected_note(self, event):
        """Opens the note file that is double-clicked in the Treeview."""
        selected_item = self.notes_tree.focus()
        if not selected_item: return

        filename = self.notes_tree.item(selected_item, 'text')
        # For robustness, we reconstruct the full path. Storing it in the item is also an option.
        notes_dir = os.path.join(self.OBSIDIAN_VAULT_PATH, "HandNotes")
        full_path = os.path.join(notes_dir, filename)

        if not os.path.exists(full_path):
            messagebox.showerror("Error", f"File not found. It may have been moved or deleted.\nPath: {full_path}")
            return

        # Open the note in Obsidian using the Obsidian URI scheme
        try:
            # Get the path of the note relative to the vault's root directory
            relative_path = os.path.relpath(full_path, self.OBSIDIAN_VAULT_PATH)
            # URL-encode the path to handle spaces and special characters
            encoded_path = urllib.parse.quote(relative_path.replace(os.sep, '/')) # Ensure forward slashes
            
            # Construct the final URI
            obsidian_uri = f"obsidian://open?vault={self.OBSIDIAN_VAULT_NAME}&file={encoded_path}"
            
            print(f"Opening Obsidian URI: {obsidian_uri}")
            webbrowser.open(obsidian_uri)
        except Exception as e:
            print(f"Error opening note in Obsidian: {e}")
            messagebox.showerror("Error", f"Could not open note in Obsidian.\nError: {str(e)}")

    def save_review_status(self):
        """Saves the currently selected status to the database."""
        if not self.current_hand_id:
            messagebox.showwarning("Warning", "No hand loaded.")
            return
        new_status = self.status_var.get()
        if not new_status:
            messagebox.showwarning("Warning", "No status selected.")
            return
        self.db.update_review_status(self.current_hand_id, new_status)
        messagebox.showinfo("Success", f"Status for hand {self.current_hand_id} saved as '{new_status}'.")

    def lookup_state_name_for_pf_sequence(self, pf_sequence, game_type):
        if not pf_sequence:
            return "No sequence"
        try:
            query = (
                f"SELECT state_name FROM hand_state "
                f"WHERE state_type = 'preflop' AND game_type = %s AND state_value = %s"
            )
            with self.db.conn.cursor() as cur:
                cur.execute(query, (game_type, pf_sequence))
                result = cur.fetchone()
            if result:
                return result[0]
            else:
                return "Unnamed"
        except Exception as e:
            print(f"Error looking up state name for sequence {pf_sequence}: {e}")
            return f"Error: {e}"

    def open_default_document(self):
        if not self.current_spot:
            messagebox.showerror("Error", "No spot is selected.")
            return

        docs = self.db.get_documents_for_spot(self.current_spot['id'])
        if not docs:
            messagebox.showinfo("Info", "No documents are linked to this spot.")
            return

        # Find the default doc, or just take the first one if none is marked default
        default_doc = next((doc for doc in docs if doc['is_default']), docs[0])
        file_path_from_db = default_doc['file_path']

        # Use the utility to find the actual file path
        actual_path = find_gto_file_in_locations(file_path_from_db)

        if not actual_path:
            messagebox.showerror("Error", f"File not found. Searched multiple locations for:\n{os.path.basename(file_path_from_db)}")
            return

        # --- NEW: Check file type before opening ---
        from pathlib import Path
        file_suffix = Path(actual_path).suffix.lower()

        try:
            if file_suffix in ['.gto', '.gto+']:
                # Open with the system default application (no elevation required)
                print(f"Opening GTO+ file: {actual_path}")
                os.startfile(actual_path)
            else:
                # Assume it's a note for Obsidian
                print(f"Opening Obsidian note: {actual_path}")
                relative_path = os.path.relpath(actual_path, self.OBSIDIAN_VAULT_PATH)
                encoded_path = urllib.parse.quote(relative_path.replace(os.sep, '/'))
                obsidian_uri = f"obsidian://open?vault={self.OBSIDIAN_VAULT_NAME}&file={encoded_path}"
                webbrowser.open(obsidian_uri)
        except Exception as e:
            messagebox.showerror("Error Opening File", f"Could not open the file.\n\nError: {e}")
            print(f"Error opening file '{actual_path}': {e}")

    def move_to_processing(self):
        """Move the default GTO+ document to the processing directory."""
        if not self.current_spot:
            messagebox.showerror("Error", "No spot is selected.")
            return

        docs = self.db.get_documents_for_spot(self.current_spot['id'])
        if not docs:
            messagebox.showinfo("Info", "No documents are linked to this spot.")
            return

        # Find the default doc, or just take the first one if none is marked default
        default_doc = next((doc for doc in docs if doc['is_default']), docs[0])
        file_path_from_db = default_doc['file_path']

        # Use the utility to find the actual file path
        actual_path = find_gto_file_in_locations(file_path_from_db)

        if not actual_path:
            messagebox.showerror("Error", f"File not found. Searched multiple locations for:\n{os.path.basename(file_path_from_db)}")
            return

        # Check if it's a GTO+ file
        from pathlib import Path
        file_suffix = Path(actual_path).suffix.lower()
        if file_suffix not in ['.gto', '.gto+']:
            messagebox.showerror("Error", "Only GTO+ files can be moved to processing directory.")
            return

        # Check if GTO+ is running
        try:
            import psutil
            gto_running = False
            
            for proc in psutil.process_iter(['name']):
                try:
                    if proc.info['name'] and "GTO" in proc.info['name']:
                        gto_running = True
                        print(f"GTO+ is running: {proc.info['name']}")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            if gto_running:
                messagebox.showerror("Error", 
                    "GTO+ is currently running.\n\nPlease close GTO+ before moving files to processing.")
                return
            else:
                print("GTO+ is not running")
                
        except ImportError:
            # psutil not available, skip the check
            print("psutil not available, skipping GTO+ check")
            pass
        except Exception as e:
            print(f"Warning: Could not check if GTO+ is running: {e}")
            # Continue with the move operation if we can't check

        # Check if file is already in processing directory
        processing_dir = Path("C:\\@myfiles\\gtotorunwhenIleave\\")
        if not processing_dir.exists():
            try:
                processing_dir.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                messagebox.showerror("Error", f"Could not create processing directory:\n{processing_dir}\n\nError: {e}")
                return

        source_path = Path(actual_path)
        filename = source_path.name
        
        # Check if file already starts with "0 - "
        if filename.startswith("0 - "):
            dest_filename = filename
        else:
            dest_filename = f"0 - {filename}"
        
        dest_path = processing_dir / dest_filename

        # Check if file is already in processing directory
        if dest_path.exists():
            self.move_status_var.set("File already in processing directory")
            return

        # Check if source and destination are the same (file already in processing dir)
        if source_path.resolve() == dest_path.resolve():
            self.move_status_var.set("File already in processing directory")
            return



        # Move the file
        try:
            import shutil
            shutil.move(str(source_path), str(dest_path))
            self.move_status_var.set("File moved to processing successfully")
            print(f"Moved file from {source_path} to {dest_path}")
        except PermissionError:
            messagebox.showerror("Error", f"Permission denied moving file.\n\nPlease ensure the file is not open in any application.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to move file to processing directory:\n\nError: {e}")

    def define_new_spot(self):
        if not self.current_hh_data:
            return
        
        spot_name = simpledialog.askstring("New Spot", "Enter a name for this new spot (e.g., MPT #43):")
        if not spot_name:
            return

        description = simpledialog.askstring("Description", "Enter a brief description:")
        source = simpledialog.askstring("Source", "Enter the source (e.g., Modern Poker Theory):")
        
        spot_id = self.db.create_spot(spot_name, description, source, self.current_hh_data)
        
        if spot_id:
            messagebox.showinfo("Success", f"Spot '{spot_name}' created successfully!")
            # Refresh the panel to show the new spot info
            self.load_hand_data(self.current_hand_id, self.current_hh_data)
        else:
            messagebox.showerror("Error", "Failed to create spot. Does a spot for this exact action/format already exist?")

    def _open_study_note(self, event):
        """Opens the selected study note in Obsidian."""
        selection = self.study_notes_tree.selection()
        if not selection: 
            return
        
        item = self.study_notes_tree.item(selection[0])
        file_path = item['values'][2]  # id, title, path -> path is the 3rd value

        if not os.path.exists(file_path):
            messagebox.showerror("Error", f"File not found: {file_path}")
            return

        try:
            relative_path = os.path.relpath(file_path, self.OBSIDIAN_VAULT_PATH)
            encoded_path = urllib.parse.quote(relative_path.replace(os.sep, '/'))
            obsidian_uri = f"obsidian://open?vault={self.OBSIDIAN_VAULT_NAME}&file={encoded_path}"
            
            webbrowser.open(obsidian_uri)
            print(f"Opened study note in Obsidian: {file_path}")
        except Exception as e:
            print(f"Error opening study note in Obsidian: {e}")
            messagebox.showerror("Error", f"Could not open study note in Obsidian.\nError: {str(e)}")

    def on_doc_select(self, event):
        selected = self.doc_list.selection()
        if selected:
            self.current_doc_id = int(selected[0])
            self.set_default_btn.config(state=tk.NORMAL)
        else:
            self.current_doc_id = None
            self.set_default_btn.config(state=tk.DISABLED)

    def set_default_document(self):
        if not self.current_spot or not self.current_doc_id:
            return
        with self.db.conn.cursor() as cur:
            # Set this doc as default, others as not default
            cur.execute(
                "UPDATE spot_document_links SET is_default = (document_id = %s) WHERE spot_id = %s",
                (self.current_doc_id, self.current_spot['id'])
            )
        self.db.conn.commit()
        messagebox.showinfo("Success", "Default document updated.")
        # Refresh the doc list to show the new default
        self.load_hand_data(self.current_hand_id, self.current_hh_data)

    def add_document_to_spot(self):
        """Add a new document to the current spot."""
        if not self.current_spot:
            messagebox.showerror("Error", "No spot is selected.")
            return

        # Open file dialog to select a document
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("GTO+ files", "*.gto;*.gto+"),
                ("Markdown files", "*.md"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        
        if not file_path:
            return  # User cancelled
        
        # Get document title from user
        default_title = os.path.splitext(os.path.basename(file_path))[0]
        title = simpledialog.askstring("Document Title", 
                                     "Enter a title for this document:", 
                                     initialvalue=default_title)
        
        if not title:
            return  # User cancelled
        
        # Get source info from user
        source_info = simpledialog.askstring("Source Information", 
                                           "Enter source information (e.g., 'GTO+', 'Modern Poker Theory'):")
        
        if source_info is None:
            return  # User cancelled
        
        try:
            # Add document to study_documents table and get its ID
            with self.db.conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO study_documents (title, file_path, source_info)
                    VALUES (%s, %s, %s) ON CONFLICT (file_path) DO UPDATE SET title = EXCLUDED.title
                    RETURNING id
                    """,
                    (title, file_path, source_info)
                )
                doc_id = cur.fetchone()[0]
                
                # Link document to current spot
                cur.execute(
                    """
                    INSERT INTO spot_document_links (spot_id, document_id, is_default)
                    VALUES (%s, %s, %s) ON CONFLICT DO NOTHING
                    """,
                    (self.current_spot['id'], doc_id, False)
                )
                
                self.db.conn.commit()
                messagebox.showinfo("Success", f"Document '{title}' added to spot '{self.current_spot['spot_name']}' successfully!")
                # Refresh the document list
                self.load_hand_data(self.current_hand_id, self.current_hh_data)
                
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Failed to add document: {str(e)}")

    def copy_flop_to_clipboard(self):
        """Copy the current hand's flop cards to the clipboard."""
        if not self.current_hh_data:
            self.copy_flop_status_var.set("No hand loaded")
            return
        
        try:
            # Try to get flop cards from the hand history data
            flop_cards = []
            
            # Method 1: Check if flop_cards attribute exists
            if hasattr(self.current_hh_data, 'flop_cards') and self.current_hh_data.flop_cards:
                flop_cards = self.current_hh_data.flop_cards
            
            # Method 2: Extract from raw text using regex
            elif hasattr(self.current_hh_data, 'raw_text') and self.current_hh_data.raw_text:
                import re
                flop_match = re.search(r'\*\*\* FLOP \*\*\* \[([^\]]+)\]', self.current_hh_data.raw_text)
                if flop_match:
                    flop_text = flop_match.group(1)
                    flop_cards = [card.strip() for card in flop_text.split()]
            
            # Method 3: Check if there's a hand_history_tree with flop information
            elif hasattr(self.current_hh_data, 'hand_history_tree'):
                for node in self.current_hh_data.hand_history_tree.get_all_nodes():
                    if hasattr(node, 'street') and node.street == 'flop':
                        if hasattr(node, 'board_cards') and node.board_cards:
                            flop_cards = node.board_cards[:3]  # Take first 3 cards for flop
                            break
            
            if not flop_cards:
                self.copy_flop_status_var.set("No flop to copy")
                return
            
            # Format the flop cards as requested: "4d 8s 4c"
            formatted_flop = " ".join(flop_cards[:3])  # Ensure we only take 3 cards
            
            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(formatted_flop)
            
            # Update status
            self.copy_flop_status_var.set(f"Copied: {formatted_flop}")
            
            # Clear status after 3 seconds
            self.after(3000, lambda: self.copy_flop_status_var.set(""))
            
        except Exception as e:
            self.copy_flop_status_var.set(f"Error: {str(e)}")
            print(f"Error copying flop to clipboard: {e}")

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
        self.game_profiles = self.db.get_game_profiles()
        self.all_spots = self.db.get_spots_for_dropdowns()
        # Initialize our saved state manager.
        self.state_manager = SavedStateManager("saved_states.json")
        # Initialize query results and current index.
        self.query_results = []
        self.current_index = 0
        # Keep track of left panel visibility.
        self.left_visible = True
        # Keep track of review panel visibility.
        self.review_visible = True
        # Initialize current hand
        self.current_hand = None

        # --- Toggle Button for Left Panel ---
        self.toggle_btn = ttk.Button(self, text="Hide Input Panel", command=self.toggle_left_panel)
        self.toggle_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        
        # --- Toggle Button for Review Panel ---
        self.toggle_review_btn = ttk.Button(self, text="Hide Review Panel", command=self.toggle_review_panel)
        self.toggle_review_btn.pack(side=tk.TOP, anchor=tk.W, padx=5, pady=5)
        
        # --- Main PanedWindow ---
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel: Inputs and State Management.
        self.left_frame = ttk.Frame(self.main_paned)
        self.build_left_panel(self.left_frame)
        self.main_paned.add(self.left_frame, weight=1)
        
        # Review Panel: Review controls and notes.
        self.review_panel = ReviewPanel(self.main_paned, self.db)
        self.main_paned.add(self.review_panel, weight=1)
        
        # Right Panel: Hand History Display and Navigation.
        self.right_frame = ttk.Frame(self.main_paned)
        self.build_right_panel(self.right_frame)
        self.main_paned.add(self.right_frame, weight=3)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Initialize defaults after UI is built
        self._initialize_defaults()
    
    def build_left_panel(self, parent):
        # --- Query Settings Panel ---
        query_frame = ttk.LabelFrame(parent, text="Query Settings")
        query_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # --- Game Profile Dropdown ---
        ttk.Label(query_frame, text="Game Profile:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.game_profile_var = tk.StringVar(value="zoom 6-max")
        profile_names = list(self.game_profiles.keys())
        self.game_profile_combo = ttk.Combobox(query_frame, textvariable=self.game_profile_var,
                                               values=profile_names, state="readonly", width=20)
        self.game_profile_combo.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        self.game_profile_combo.bind("<<ComboboxSelected>>", self._on_profile_selected)
        
        ttk.Label(query_frame, text="PF Game Type:").grid(row=1, column=0, sticky=tk.E, padx=5, pady=5)
        self.pf_game_type_var = tk.StringVar(value="zoom_cash_6max")
        game_types = ["zoom_cash_6max", "spingo", "husng spots","tournament"]
        self.pf_game_type_combo = ttk.Combobox(query_frame, textvariable=self.pf_game_type_var,
                                               values=game_types, state="readonly", width=20)
        self.pf_game_type_combo.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)
        self.pf_game_type_combo.bind("<<ComboboxSelected>>", lambda event: self.refresh_pf_actions())
        
        # --- Structured Format Dropdowns ---
        ttk.Label(query_frame, text="Game Class:").grid(row=2, column=0, sticky=tk.E, padx=5, pady=5)
        self.game_class_var = tk.StringVar(value="")
        game_classes = ["", "cash", "tournament"]
        self.game_class_combo = ttk.Combobox(query_frame, textvariable=self.game_class_var,
                                             values=game_classes, state="readonly", width=20)
        self.game_class_combo.grid(row=2, column=1, sticky=tk.W, padx=5, pady=5)
        self.game_class_combo.bind("<<ComboboxSelected>>", self._update_spot_dropdown)
        
        ttk.Label(query_frame, text="Game Variant:").grid(row=3, column=0, sticky=tk.E, padx=5, pady=5)
        self.game_variant_var = tk.StringVar(value="")
        game_variants = ["", "zoom", "regular"]
        self.game_variant_combo = ttk.Combobox(query_frame, textvariable=self.game_variant_var,
                                               values=game_variants, state="readonly", width=20)
        self.game_variant_combo.grid(row=3, column=1, sticky=tk.W, padx=5, pady=5)
        self.game_variant_combo.bind("<<ComboboxSelected>>", self._update_spot_dropdown)
        
        ttk.Label(query_frame, text="Table Size:").grid(row=4, column=0, sticky=tk.E, padx=5, pady=5)
        self.table_size_var = tk.StringVar(value="")
        table_sizes = ["", "2-max", "3-max", "6-max", "9-max"]
        self.table_size_combo = ttk.Combobox(query_frame, textvariable=self.table_size_var,
                                             values=table_sizes, state="readonly", width=20)
        self.table_size_combo.grid(row=4, column=1, sticky=tk.W, padx=5, pady=5)
        self.table_size_combo.bind("<<ComboboxSelected>>", self._update_spot_dropdown)
        
        ttk.Label(query_frame, text="Preflop Spot:").grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        # Store label reference for dynamic update
        self.pf_spot_label = ttk.Label(query_frame, text="Preflop Spot:")
        self.pf_spot_label.grid(row=5, column=0, sticky=tk.E, padx=5, pady=5)
        # Dropdown setup (keep reference for dynamic update)
        self.pf_actions = self.all_spots.get('preflop', {})
        pf_options = sorted(self.pf_actions.keys(), key=lambda x: int(x) if x.isdigit() else 999)
        self.pf_seq_var = tk.StringVar(value="37")
        self.pf_seq_combo = ttk.Combobox(query_frame, textvariable=self.pf_seq_var,
                                         values=["Unnamed"] + pf_options, state="readonly", width=20)
        self.pf_seq_combo.grid(row=5, column=1, sticky=tk.W, padx=5, pady=5)
        self.pf_seq_combo.bind("<<ComboboxSelected>>", self.on_pf_selection)

        # Add a read-only entry for preflop SQL pattern (initially empty)
        self.pf_sql_pattern_var = tk.StringVar()
        self.pf_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.pf_sql_pattern_var, width=40, state="readonly")
        self.pf_sql_pattern_entry.grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        self.pf_sql_pattern_entry.grid_remove()  # Hide by default

        # Add pf Action no checkbox to the right of the SQL pattern entry
        self.pf_action_no_var = tk.BooleanVar(value=True)
        self.pf_action_no_checkbox = ttk.Checkbutton(query_frame, text="pf Action no", variable=self.pf_action_no_var, command=self.on_pf_action_no_toggle)
        self.pf_action_no_checkbox.grid(row=5, column=4, sticky=tk.W, padx=5, pady=5)

        # Action String label/entry (only shown when checkbox is checked)
        self.pf_action_str_label = ttk.Label(query_frame, text="Action String:")
        self.pf_action_str_label.grid(row=5, column=2, sticky=tk.E, padx=5, pady=5)
        self.pf_action_str_var = tk.StringVar()
        self.pf_action_entry = ttk.Entry(query_frame, textvariable=self.pf_action_str_var, width=40)
        self.pf_action_entry.grid(row=5, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Flop Pattern:").grid(row=6, column=0, sticky=tk.E, padx=5, pady=5)
        postflop_patterns = self.all_spots.get('postflop', {})
        postflop_options = ["None"] + sorted(postflop_patterns.keys())
        self.flop_pattern_var = tk.StringVar(value="None")
        self.flop_pattern_combo = ttk.Combobox(query_frame, textvariable=self.flop_pattern_var,
                                               values=postflop_options, state="readonly", width=20)
        self.flop_pattern_combo.grid(row=6, column=1, sticky=tk.W, padx=5, pady=5)
        self.flop_pattern_combo.bind("<<ComboboxSelected>>", self.on_flop_pattern_selection)
        ttk.Label(query_frame, text="Flop SQL Pattern:").grid(row=6, column=2, sticky=tk.E, padx=5, pady=5)
        self.flop_sql_pattern_var = tk.StringVar()
        self.flop_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.flop_sql_pattern_var,
                                                width=40, state="readonly")
        self.flop_sql_pattern_entry.grid(row=6, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Turn Pattern:").grid(row=7, column=0, sticky=tk.E, padx=5, pady=5)
        postflop_patterns = self.all_spots.get('postflop', {})
        postflop_options = ["None"] + sorted(postflop_patterns.keys())
        self.turn_pattern_var = tk.StringVar(value="None")
        self.turn_pattern_combo = ttk.Combobox(query_frame, textvariable=self.turn_pattern_var,
                                               values=postflop_options, state="readonly", width=20)
        self.turn_pattern_combo.grid(row=7, column=1, sticky=tk.W, padx=5, pady=5)
        self.turn_pattern_combo.bind("<<ComboboxSelected>>", self.on_turn_pattern_selection)
        ttk.Label(query_frame, text="Turn SQL Pattern:").grid(row=7, column=2, sticky=tk.E, padx=5, pady=5)
        self.turn_sql_pattern_var = tk.StringVar()
        self.turn_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.turn_sql_pattern_var,
                                                width=40, state="readonly")
        self.turn_sql_pattern_entry.grid(row=7, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="River Pattern:").grid(row=8, column=0, sticky=tk.E, padx=5, pady=5)
        postflop_patterns = self.all_spots.get('postflop', {})
        postflop_options = ["None"] + sorted(postflop_patterns.keys())
        self.river_pattern_var = tk.StringVar(value="None")
        self.river_pattern_combo = ttk.Combobox(query_frame, textvariable=self.river_pattern_var,
                                                values=postflop_options, state="readonly", width=20)
        self.river_pattern_combo.grid(row=8, column=1, sticky=tk.W, padx=5, pady=5)
        self.river_pattern_combo.bind("<<ComboboxSelected>>", self.on_river_pattern_selection)
        ttk.Label(query_frame, text="River SQL Pattern:").grid(row=8, column=2, sticky=tk.E, padx=5, pady=5)
        self.river_sql_pattern_var = tk.StringVar()
        self.river_sql_pattern_entry = ttk.Entry(query_frame, textvariable=self.river_sql_pattern_var,
                                                width=40, state="readonly")
        self.river_sql_pattern_entry.grid(row=8, column=3, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Button Name:").grid(row=9, column=0, sticky=tk.E, padx=5, pady=5)
        self.button_name_var = tk.StringVar()
        self.button_entry = ttk.Entry(query_frame, textvariable=self.button_name_var, width=30)
        self.button_entry.grid(row=9, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Position:").grid(row=10, column=0, sticky=tk.E, padx=5, pady=5)
        self.position_var = tk.StringVar(value="None")
        positions_list = ["None", "BN", "SB", "BB", "UTG", "MP", "CO"]
        self.position_combo = ttk.Combobox(query_frame, textvariable=self.position_var,
                                           values=positions_list, state="readonly", width=20)
        self.position_combo.grid(row=10, column=1, sticky=tk.W, padx=5, pady=5)
        
        ttk.Label(query_frame, text="Player Name for Position:").grid(row=10, column=2, sticky=tk.E, padx=5, pady=5)
        self.position_player_var = tk.StringVar()
        self.position_player_entry = ttk.Entry(query_frame, textvariable=self.position_player_var, width=30)
        self.position_player_entry.grid(row=10, column=3, sticky=tk.W, padx=5, pady=5)
        
        # --- Time Period Checkbox and Entry ---
        self.time_period_var = tk.BooleanVar(value=False)  # Default to unchecked
        self.time_period_checkbox = ttk.Checkbutton(query_frame, text="Time Period (hours):", 
                                                   variable=self.time_period_var,
                                                   command=self.toggle_time_period)
        self.time_period_checkbox.grid(row=11, column=0, sticky=tk.E, padx=5, pady=5)

        self.time_period_entry_var = tk.StringVar(value="24")  # Default to 24 hours
        self.time_period_entry = ttk.Entry(query_frame, textvariable=self.time_period_entry_var, width=10)
        self.time_period_entry.grid(row=11, column=1, sticky=tk.W, padx=5, pady=5)

        # --- Player Flop Checkbox and Entry ---
        self.player_flop_var = tk.BooleanVar(value=False)  # Default to unchecked
        self.player_flop_checkbox = ttk.Checkbutton(query_frame, text="Player Saw Flop:", 
                                                   variable=self.player_flop_var,
                                                   command=self.toggle_player_flop)
        self.player_flop_checkbox.grid(row=11, column=2, sticky=tk.E, padx=5, pady=5)

        self.player_flop_entry_var = tk.StringVar(value="")  # Default to empty
        self.player_flop_entry = ttk.Entry(query_frame, textvariable=self.player_flop_entry_var, width=30)
        self.player_flop_entry.grid(row=11, column=3, sticky=tk.W, padx=5, pady=5)
        self.player_flop_entry.config(state=tk.DISABLED)  # Initially disabled
        
        ttk.Label(query_frame, text="Review Status:").grid(row=12, column=0, sticky=tk.E, padx=5, pady=5)
        self.review_status_filter_var = tk.StringVar(value="All")
        status_filter_options = ["All", 'unreviewed', 'eyeballed', 'marked_for_review', 'waiting_on_gto', 'completed']
        self.review_status_filter_combo = ttk.Combobox(query_frame, textvariable=self.review_status_filter_var,
                                                       values=status_filter_options, state="readonly", width=20)
        self.review_status_filter_combo.grid(row=12, column=1, sticky=tk.W, padx=5, pady=5)
        # (You may need to renumber grid rows for widgets below this)

        self.query_button = ttk.Button(query_frame, text="Run Query", command=self.run_query)
        self.query_button.grid(row=13, column=0, columnspan=2, pady=10, sticky=tk.W)
        
        # Add Show Query button next to Run Query button
        self.show_query_button = ttk.Button(query_frame, text="Show Query", command=self.show_query)
        self.show_query_button.grid(row=13, column=2, pady=10, sticky=tk.W)
        
        # Add after the query button
        refresh_btn = ttk.Button(query_frame, text="↻ Refresh Dropdowns", command=self.refresh_all_dropdowns)
        refresh_btn.grid(row=13, column=3, pady=10, sticky=tk.E)
        
        # --- New: State Name Display ---
        state_display_frame = ttk.LabelFrame(query_frame, text="Current Hand State")
        state_display_frame.grid(row=14, column=0, columnspan=4, sticky=tk.EW, padx=5, pady=5)
        
        ttk.Label(state_display_frame, text="Matching State Name:").grid(row=0, column=0, sticky=tk.E, padx=5, pady=5)
        self.matching_state_var = tk.StringVar(value="No hand loaded")
        self.matching_state_entry = ttk.Entry(state_display_frame, textvariable=self.matching_state_var, 
                                             width=50, state="readonly")
        self.matching_state_entry.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)
        
        # --- New: Betting Opportunities Button ---
        opp_btn = ttk.Button(parent, text="Show Betting Opportunities", command=self.show_betting_opportunities)
        opp_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- New: Combined Actions and Opportunities Button ---
        combined_btn = ttk.Button(parent, text="Show Combined Actions & Opportunities", command=self.show_combined_view)
        combined_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- New: Hand Actions Button ---
        actions_btn = ttk.Button(parent, text="Show Hand Actions", command=self.show_hand_actions)
        actions_btn.pack(fill=tk.X, padx=5, pady=5)
        
        # --- New: Manage Spot Profiles Button ---
        spot_profiles_btn = ttk.Button(parent, text="Manage Spot Profiles", command=self.open_spot_profile_manager)
        spot_profiles_btn.pack(fill=tk.X, padx=5, pady=5)
        
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
    
    def toggle_review_panel(self):
        if self.review_visible:
            self.main_paned.forget(self.review_panel)
            self.toggle_review_btn.config(text="Show Review Panel")
            self.review_visible = False
        else:
            self.main_paned.add(self.review_panel, weight=1)
            self.toggle_review_btn.config(text="Hide Review Panel")
            self.review_visible = True
    
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
            sql_pattern = self.all_spots.get('postflop', {}).get(selected, "")
            self.flop_sql_pattern_var.set(sql_pattern)
    
    def on_turn_pattern_selection(self, event):
        selected = self.turn_pattern_var.get().strip()
        if selected == "None":
            self.turn_sql_pattern_var.set("")
        else:
            sql_pattern = self.all_spots.get('postflop', {}).get(selected, "")
            self.turn_sql_pattern_var.set(sql_pattern)
    
    def on_river_pattern_selection(self, event):
        selected = self.river_pattern_var.get().strip()
        if selected == "None":
            self.river_sql_pattern_var.set("")
        else:
            sql_pattern = self.all_spots.get('postflop', {}).get(selected, "")
            self.river_sql_pattern_var.set(sql_pattern)
    
    def run_query(self):
        try:
            # Use LEFT JOIN to hand_reviews and filter by status if needed
            base_select = """
                SELECT hh.id, hh.game_type, hh.pf_action_seq, hh.flop_action_seq, 
                       hh.turn_action_seq, hh.river_action_seq, hh.raw_text 
                FROM hand_histories hh
                LEFT JOIN hand_reviews hr ON hh.id = hr.hand_id
            """
            qb = QueryBuilder(base_select)
            
            # Add structured format conditions if specified
            game_class = self.game_class_var.get().strip()
            game_variant = self.game_variant_var.get().strip()
            table_size = self.table_size_var.get().strip()
            
            # Use structured format fields if any are specified, otherwise fall back to game_type
            if game_class or game_variant or table_size:
                if game_class:
                    qb.add_condition(Condition("game_class", "=", game_class))
                if game_variant:
                    qb.add_condition(Condition("game_variant", "=", game_variant))
                if table_size:
                    qb.add_condition(Condition("table_size", "=", table_size))
            else:
                # Fall back to legacy game_type pattern
                game_type = self.pf_game_type_var.get().strip()
                qb.add_condition(Condition("game_type", "LIKE", f"{game_type}%"))
            
            # Add time period condition if enabled
            if self.time_period_var.get():
                try:
                    time_period = int(self.time_period_entry_var.get().strip())
                    if time_period > 0:  # Only add condition if time period is positive
                        qb.add_condition(Condition("created_at", ">=", f"NOW() - INTERVAL '{time_period} hours'"))
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number of hours.")
                    return
            
            # Add player flop condition if enabled
            if self.player_flop_var.get():
                player_name = self.player_flop_entry_var.get().strip()
                print(f"Searching for player: {player_name}")  # Debug log
                if not player_name:
                    messagebox.showerror("Error", "Please enter a player name.")
                    return
                
                # Add condition to check if hand reached flop
                qb.add_condition(Condition("flop_action_seq", "IS NOT NULL", ""))
                
                # Get the preflop sequence to optimize the query
                pf_selected = self.pf_seq_var.get().strip()
                pf_action_str = self.pf_action_str_var.get().strip()
                
                # Try to use preflop sequence analysis for optimization
                use_optimized_conditions = False
                if pf_selected != "Unnamed" and pf_action_str:
                    # We have a specific preflop sequence, analyze it
                    flop_conditions = self.construct_flop_query_conditions(pf_action_str, player_name)
                    if flop_conditions:
                        # Use the optimized conditions with OR logic
                        print(f"Using optimized flop conditions for positions: {[self.get_position_name_from_number(pos) for pos in self.analyze_pf_sequence_for_flop_positions(pf_action_str)]}")
                        
                        # Build OR condition manually since QueryBuilder doesn't support OR
                        position_conditions = []
                        for condition in flop_conditions:
                            position_conditions.append(f"{condition.field} = '{condition.value}'")
                        
                        if position_conditions:
                            or_condition = " OR ".join(position_conditions)
                            # Add as a raw condition
                            qb.add_condition(Condition(f"({or_condition})", "", ""))
                            use_optimized_conditions = True
                    
                if not use_optimized_conditions:
                    # Fall back to the general position check
                    qb.add_condition(Condition("positions::text", "LIKE", f"%{player_name}%"))
            
            # Add existing conditions
            pf_selected = self.pf_seq_var.get().strip()
            pf_action_str = self.pf_action_str_var.get().strip()
            print(f"DEBUG: pf_selected = '{pf_selected}', pf_action_str = '{pf_action_str}' (type: {type(pf_action_str)})")
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
                    # If no values specified, don't add any condition - let it match all
                elif pf_action_str:  # Only add condition if pf_action_str is not empty
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
            
            selected_status = self.review_status_filter_var.get()
            if selected_status != "All":
                if selected_status == 'unreviewed':
                    qb.add_condition(Condition("(hr.review_status IS NULL OR hr.review_status = 'unreviewed')", "", ""))
                else:
                    qb.add_condition(Condition("hr.review_status", "=", selected_status))
            
            # Add sorting by created_at in descending order
            qb.add_sort(SortCriterion("created_at", "DESC"))
            query = qb.build_query()
            
            # Print the query for debugging
            print("Generated SQL Query:", query)
            
            # Reset any failed transaction
            self.db.conn.rollback()
            
            with self.db.conn.cursor() as cur:
                # First, let's check how many hands match just the basic conditions
                game_class = self.game_class_var.get().strip()
                game_variant = self.game_variant_var.get().strip()
                table_size = self.table_size_var.get().strip()
                
                if game_class or game_variant or table_size:
                    # Build structured format query
                    conditions = []
                    if game_class:
                        conditions.append(f"game_class = '{game_class}'")
                    if game_variant:
                        conditions.append(f"game_variant = '{game_variant}'")
                    if table_size:
                        conditions.append(f"table_size = '{table_size}'")
                    
                    basic_query = f"SELECT COUNT(*) FROM hand_histories WHERE {' AND '.join(conditions)}"
                else:
                    # Fall back to legacy game_type pattern
                    game_type = self.pf_game_type_var.get().strip()
                    basic_query = f"SELECT COUNT(*) FROM hand_histories WHERE game_type LIKE '{game_type}%'"
                
                cur.execute(basic_query)
                basic_count = cur.fetchone()[0]
                print(f"Total hands matching basic conditions: {basic_count}")
                
                # Now execute the full query
                cur.execute(query)
                rows = cur.fetchall()
                print(f"Total hands matching all conditions: {len(rows)}")
                
                # If player flop filter is enabled, filter results to only include hands where player saw the flop
                if self.player_flop_var.get():
                    # Check if we used optimized conditions
                    if 'use_optimized_conditions' in locals() and use_optimized_conditions:
                        print("Using optimized conditions - skipping post-processing")
                        self.query_results = rows
                    else:
                        filtered_rows = []
                        player_name = self.player_flop_entry_var.get().strip()  # Get the player name again
                        print(f"Filtering for player: {player_name}")  # Debug log
                        for row in rows:
                            try:
                                # Parse the hand history
                                parser = get_hand_history_parser(row[6])
                                hh_data = parser.parse(row[6])
                                
                                # Check if player was active on the flop
                                flop_node = None
                                for node in hh_data.hand_history_tree.get_all_nodes():
                                    if isinstance(node, StreetChange) and node.street == "flop":
                                        flop_node = node
                                        break
                                
                                if flop_node:
                                    # Check if player was active at the flop
                                    player_active = False
                                    for player in flop_node.active_players:
                                        if player and player.player == player_name and player.is_active:
                                            player_active = True
                                            break
                                    
                                    if player_active:
                                        filtered_rows.append(row)
                            except Exception as e:
                                print(f"Error processing hand {row[0]}: {e}")
                                continue
                        
                        print(f"Total hands after flop filtering: {len(filtered_rows)}")
                        self.query_results = filtered_rows
                else:
                    self.query_results = rows
                
                self.current_index = 0
                self.display_current_result()
                
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error executing query: {e}\n")
            # Reset any failed transaction
            self.db.conn.rollback()
            return
    
    def display_current_result(self):
        try:
            self.result_text.delete("1.0", tk.END)
            if not self.query_results:
                self.result_text.insert(tk.END, "No matching hand histories found.\n")
                self.matching_state_var.set("No hand loaded")
            else:
                row = self.query_results[self.current_index]
                (hand_id, game_type, pf_seq, flop_seq, turn_seq, river_seq, raw_text) = row
                
                # Parse the hand history to get HandHistoryData
                try:
                    parser = get_hand_history_parser(raw_text)
                    hh_data = parser.parse(raw_text)
                except Exception as parse_error:
                    print(f"Error parsing hand history: {parse_error}")
                    # Create a minimal hh_data object to prevent crashes
                    class MinimalHandData:
                        def get_simple_action_sequence(self, street):
                            return "Error parsing hand"
                    hh_data = MinimalHandData()
                
                # Generate action sequences on the fly
                try:
                    pf_seq = hh_data.get_simple_action_sequence("preflop")
                    flop_seq = hh_data.get_simple_action_sequence("flop")
                    turn_seq = hh_data.get_simple_action_sequence("turn")
                    river_seq = hh_data.get_simple_action_sequence("river")
                except Exception as seq_error:
                    print(f"Error generating action sequences: {seq_error}")
                    pf_seq = "Error"
                    flop_seq = "Error"
                    turn_seq = "Error"
                    river_seq = "Error"
                
                display_text = (f"Result {self.current_index+1} of {len(self.query_results)}\n"
                              f"ID: {hand_id}\nGame Type: {game_type}\n"
                              f"Preflop: {pf_seq}\nFlop: {flop_seq}\nTurn: {turn_seq}\nRiver: {river_seq}\n\n"
                              f"Raw Hand History:\n{raw_text}\n")
                self.result_text.insert(tk.END, display_text)
                # Load the hand data
                self.load_hand(row)
                
                # --- Add this line to link the main app to the review panel ---
                if self.current_hand:
                    self.review_panel.load_hand_data(self.current_hand["hand_id"], hh_data)
            
            self.prev_button.config(state=tk.NORMAL if self.current_index > 0 else tk.DISABLED)
            self.next_button.config(state=tk.NORMAL if self.current_index < len(self.query_results)-1 else tk.DISABLED)
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error displaying result: {e}\n")
            self.matching_state_var.set("Error displaying result")
    
    def next_result(self):
        try:
            if self.current_index < len(self.query_results)-1:
                self.current_index += 1
                self.display_current_result()
        except Exception as e:
            self.result_text.delete("1.0", tk.END)
            self.result_text.insert(tk.END, f"Error navigating to next result: {e}\n")
            self.matching_state_var.set("Error navigating")
    
    def prev_result(self):
        try:
            if self.current_index > 0:
                self.current_index -= 1
                self.display_current_result()
        except Exception as e:
            messagebox.showerror("Error", f"Error navigating to previous result: {str(e)}\nThe application will continue running.")
            # Reset to a safe state
            self.current_index = max(0, min(self.current_index, len(self.query_results)-1))
            self.matching_state_var.set("Error navigating")
    
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
            "game_class": self.game_class_var.get().strip(),
            "game_variant": self.game_variant_var.get().strip(),
            "table_size": self.table_size_var.get().strip(),
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
            self.game_class_var.set(state_data.get("game_class", ""))
            self.game_variant_var.set(state_data.get("game_variant", ""))
            self.table_size_var.set(state_data.get("table_size", ""))
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
            hh_data.raw_text = row[6]  # Add raw text for board texture matching
            
            # Try to compute betting opportunities, but don't fail if it doesn't work
            try:
                hh_data.compute_betting_opportunities()  # Compute betting opportunities
            except Exception as opp_error:
                print(f"Warning: Could not compute betting opportunities: {opp_error}")
                # Continue without betting opportunities
                # Set an empty list to prevent further errors
                if hasattr(hh_data, 'betting_opportunities'):
                    hh_data.betting_opportunities = []
                
            self.current_hand["hand_history_data"] = hh_data
            
        except Exception as e:
            messagebox.showerror("Error", f"Error loading hand: {str(e)}\nThe application will continue running.")
            self.current_hand = None
            self.matching_state_var.set("Error loading hand")

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
                if player:  # Check if player is not None
                    try:
                        text_widget.insert(tk.END, f"{indent}  - {player.player} (Stack: ${player.stack:.2f}, "
                                                 f"Remaining: ${player.remaining_stack:.2f}, "
                                                 f"Contribution: ${player.total_contribution:.2f}, "
                                                 f"Position: {player.position or 'N/A'}, "
                                                 f"Active: {player.is_active})\n")
                    except AttributeError as e:
                        text_widget.insert(tk.END, f"{indent}  - Invalid player object: {e}\n")
            
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

    def analyze_pf_sequence_for_flop_positions(self, pf_sequence):
        """
        Analyze a preflop action sequence to determine which positions are likely to see the flop.
        
        Args:
            pf_sequence (str): Preflop action sequence like "1f2f3f4r5r6r5c"
        
        Returns:
            list: List of position numbers (1-6) that are likely to see the flop
        """
        if not pf_sequence:
            return []
        
        # Parse the sequence into actions
        actions = []
        i = 0
        while i < len(pf_sequence):
            if pf_sequence[i].isdigit():
                position = int(pf_sequence[i])
                if i + 1 < len(pf_sequence):
                    action = pf_sequence[i + 1]
                    actions.append((position, action))
                i += 2
            else:
                i += 1
        
        # Track which positions are still active
        active_positions = set(range(1, 7))  # Start with all positions 1-6
        
        for position, action in actions:
            if action == 'f':  # fold
                active_positions.discard(position)
            elif action == 'r':  # raise
                # Position is still active after raising
                pass
            elif action == 'c':  # call
                # Position is still active after calling
                pass
            elif action == 'k':  # check
                # Position is still active after checking
                pass
        
        return sorted(list(active_positions))

    def get_position_name_from_number(self, position_num):
        """Convert position number to position name."""
        position_map = {
            1: "UTG",
            2: "MP", 
            3: "CO",
            4: "BN",
            5: "SB",
            6: "BB"
        }
        return position_map.get(position_num, f"P{position_num}")

    def construct_flop_query_conditions(self, pf_sequence, player_name):
        """
        Construct SQL conditions to check if a player is likely to see the flop
        based on the preflop action sequence.
        
        Args:
            pf_sequence (str): Preflop action sequence
            player_name (str): Name of the player to check
        
        Returns:
            list: List of Condition objects to add to the query
        """
        flop_positions = self.analyze_pf_sequence_for_flop_positions(pf_sequence)
        
        if not flop_positions:
            return []
        
        # Create conditions to check if the player is in any of the flop positions
        conditions = []
        for pos_num in flop_positions:
            pos_name = self.get_position_name_from_number(pos_num)
            conditions.append(Condition(f"positions->>'{pos_name}'", "=", player_name))
        
        return conditions

    def show_query(self):
        """Show the SQL query that would be executed in a popup window."""
        try:
            # Build the query using the same logic as run_query but don't execute it
            qb = QueryBuilder(
                "SELECT id, game_type, pf_action_seq, flop_action_seq, turn_action_seq, river_action_seq, raw_text FROM hand_histories"
            )
            
            # Add structured format conditions if specified
            game_class = self.game_class_var.get().strip()
            game_variant = self.game_variant_var.get().strip()
            table_size = self.table_size_var.get().strip()
            
            # Use structured format fields if any are specified, otherwise fall back to game_type
            if game_class or game_variant or table_size:
                if game_class:
                    qb.add_condition(Condition("game_class", "=", game_class))
                if game_variant:
                    qb.add_condition(Condition("game_variant", "=", game_variant))
                if table_size:
                    qb.add_condition(Condition("table_size", "=", table_size))
            else:
                # Fall back to legacy game_type pattern
                game_type = self.pf_game_type_var.get().strip()
                qb.add_condition(Condition("game_type", "LIKE", f"{game_type}%"))
            
            # Add time period condition if enabled
            if self.time_period_var.get():
                try:
                    time_period = int(self.time_period_entry_var.get().strip())
                    if time_period > 0:  # Only add condition if time period is positive
                        qb.add_condition(Condition("created_at", ">=", f"NOW() - INTERVAL '{time_period} hours'"))
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number of hours.")
                    return
            
            # Add player flop condition if enabled
            if self.player_flop_var.get():
                player_name = self.player_flop_entry_var.get().strip()
                if not player_name:
                    messagebox.showerror("Error", "Please enter a player name.")
                    return
                
                # Add condition to check if hand reached flop
                qb.add_condition(Condition("flop_action_seq", "IS NOT NULL", ""))
                
                # Get the preflop sequence to optimize the query
                pf_selected = self.pf_seq_var.get().strip()
                pf_action_str = self.pf_action_str_var.get().strip()
                
                # Try to use preflop sequence analysis for optimization
                use_optimized_conditions = False
                if pf_selected != "Unnamed" and pf_action_str:
                    # We have a specific preflop sequence, analyze it
                    flop_conditions = self.construct_flop_query_conditions(pf_action_str, player_name)
                    if flop_conditions:
                        # Use the optimized conditions with OR logic
                        position_conditions = []
                        for condition in flop_conditions:
                            position_conditions.append(f"{condition.field} = '{condition.value}'")
                        
                        if position_conditions:
                            or_condition = " OR ".join(position_conditions)
                            # Add as a raw condition
                            qb.add_condition(Condition(f"({or_condition})", "", ""))
                            use_optimized_conditions = True
                    
                if not use_optimized_conditions:
                    # Fall back to the general position check
                    qb.add_condition(Condition("positions::text", "LIKE", f"%{player_name}%"))
            
            # Add existing conditions
            pf_selected = self.pf_seq_var.get().strip()
            pf_action_str = self.pf_action_str_var.get().strip()
            print(f"DEBUG: pf_selected = '{pf_selected}', pf_action_str = '{pf_action_str}' (type: {type(pf_action_str)})")
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
                    # If no values specified, don't add any condition - let it match all
                elif pf_action_str:  # Only add condition if pf_action_str is not empty
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
            
            selected_status = self.review_status_filter_var.get()
            if selected_status != "All":
                if selected_status == 'unreviewed':
                    qb.add_condition(Condition("(hr.review_status IS NULL OR hr.review_status = 'unreviewed')", "", ""))
                else:
                    qb.add_condition(Condition("hr.review_status", "=", selected_status))
            
            # Add sorting by created_at in descending order
            qb.add_sort(SortCriterion("created_at", "DESC"))
            query = qb.build_query()
            
            # Create popup window
            popup = tk.Toplevel(self)
            popup.title("Generated SQL Query")
            popup.geometry("800x600")
            popup.transient(self)  # Make popup modal to main window
            popup.grab_set()  # Make popup modal
            
            # Create frame for the popup content
            frame = ttk.Frame(popup, padding="10")
            frame.pack(fill=tk.BOTH, expand=True)
            
            # Add label
            label = ttk.Label(frame, text="SQL Query that would be executed:", font=("Arial", 12, "bold"))
            label.pack(pady=(0, 10))
            
            # Create text widget with scrollbar
            text_frame = ttk.Frame(frame)
            text_frame.pack(fill=tk.BOTH, expand=True)
            
            text_widget = tk.Text(text_frame, wrap=tk.WORD, font=("Courier", 10), 
                                 background="white", relief=tk.SUNKEN, borderwidth=1)
            scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=text_widget.yview)
            text_widget.configure(yscrollcommand=scrollbar.set)
            
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            
            # Insert the query text
            text_widget.insert(tk.END, query)
            text_widget.config(state=tk.DISABLED)  # Make it read-only
            
            # Add close button
            close_button = ttk.Button(frame, text="Close", command=popup.destroy)
            close_button.pack(pady=(10, 0))
            
            # Center the popup on the main window
            popup.update_idletasks()
            x = self.winfo_x() + (self.winfo_width() // 2) - (popup.winfo_width() // 2)
            y = self.winfo_y() + (self.winfo_height() // 2) - (popup.winfo_height() // 2)
            popup.geometry(f"+{x}+{y}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating query: {e}")

    def toggle_time_period(self):
        if self.time_period_var.get():
            self.time_period_entry.config(state=tk.NORMAL)
        else:
            self.time_period_entry.config(state=tk.DISABLED)

    def toggle_player_flop(self):
        if self.player_flop_var.get():
            self.player_flop_entry.config(state=tk.NORMAL)
        else:
            self.player_flop_entry.config(state=tk.DISABLED)

    def _on_profile_selected(self, event=None):
        """Called when a game profile is selected. Updates the other dropdowns."""
        profile_name = self.game_profile_var.get()
        profile = self.game_profiles.get(profile_name)
        if not profile:
            return

        # Set the values of the underlying format dropdowns
        self.game_class_var.set(profile['class'])
        self.game_variant_var.set(profile['variant'])
        self.table_size_var.set(profile['size'])
        
        # Trigger the spot dropdown to update
        self._update_spot_dropdown()

    def _update_spot_dropdown(self, event=None):
        """Refreshes the Preflop Spot dropdown with spots filtered by the selected game profile."""
        # Get the selected game profile
        profile_name = self.game_profile_var.get()
        
        if profile_name:
            # Filter spots by the selected profile
            filtered_spots = self.db.get_spots_for_dropdowns(profile_name)
        else:
            # Get all spots if no profile is selected
            filtered_spots = self.db.get_spots_for_dropdowns()
        
        self.pf_actions = filtered_spots.get('preflop', {}) # Update the source
        pf_options = sorted(self.pf_actions.keys(), key=lambda x: int(x) if x.isdigit() else 999)
        self.pf_seq_combo['values'] = ["Unnamed"] + pf_options
        
        # Try to maintain the "37" default if it exists in the options, otherwise reset to "Unnamed"
        current_value = self.pf_seq_var.get()
        if current_value == "37" and "37" in pf_options:
            # Keep the "37" selection
            pass
        else:
            # Reset to "Unnamed" if "37" is not available
            self.pf_seq_var.set("Unnamed")

    def open_spot_profile_manager(self):
        """Open the Spot Profile Manager window."""
        try:
            manager = open_spot_profile_manager(self, self.db)
            # When the manager window is closed, refresh the spot dropdown
            manager.protocol("WM_DELETE_WINDOW", lambda: self._on_manager_closed(manager))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open Spot Profile Manager: {e}")

    def _initialize_defaults(self):
        """Initialize the default values for game profile and preflop spot."""
        # Set the default game profile and trigger the profile selection
        if "zoom 6-max" in self.game_profiles:
            self.game_profile_var.set("zoom 6-max")
            self._on_profile_selected()
        
        # Set the default preflop spot to "37" if it exists
        if "37" in self.pf_actions:
            self.pf_seq_var.set("37")
            # Trigger the preflop selection to load the action string
            self.on_pf_selection(None)

    def _on_manager_closed(self, manager):
        """Called when the spot profile manager is closed."""
        manager.destroy()
        # Refresh the spot dropdown to show any changes
        self._update_spot_dropdown()

if __name__ == "__main__":
    app = HandHistoryExplorer()
    app.mainloop()
