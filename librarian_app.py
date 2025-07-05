# librarian_app.py
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from scripts.db_access import DatabaseAccess # Fixed import path
from scripts.config import DB_PARAMS # Fixed import path

class RuleEditorWindow(tk.Toplevel):
    def __init__(self, parent, db, rule_data, callback):
        super().__init__(parent)
        self.title("Rule Editor")
        self.geometry("600x520")  # Made window taller for the new fields
        self.db = db
        self.rule_data = rule_data  # This is a dictionary
        self.callback = callback  # Function to call when saved

        # Make dialog modal
        self.transient(parent)
        self.grab_set()

        self.desc_var = tk.StringVar(value=self.rule_data.get('rule_description', ''))
        self.pf_var = tk.StringVar(value=self.rule_data.get('pf_pattern', ''))
        self.flop_var = tk.StringVar(value=self.rule_data.get('flop_pattern', ''))
        self.turn_var = tk.StringVar(value=self.rule_data.get('turn_pattern', ''))
        self.river_var = tk.StringVar(value=self.rule_data.get('river_pattern', ''))
        self.board_var = tk.StringVar(value=self.rule_data.get('board_texture', ''))
        self.min_stack_var = tk.StringVar(value=str(self.rule_data.get('min_stack_bb', '') or ''))
        self.max_stack_var = tk.StringVar(value=str(self.rule_data.get('max_stack_bb', '') or ''))
        # New structured format fields
        self.game_class_var = tk.StringVar(value=self.rule_data.get('game_class_pattern', ''))
        self.game_variant_var = tk.StringVar(value=self.rule_data.get('game_variant_pattern', ''))
        self.table_size_var = tk.StringVar(value=self.rule_data.get('table_size_pattern', ''))
        # Legacy fields for backward compatibility
        self.game_type_var = tk.StringVar(value=self.rule_data.get('game_type_pattern', ''))
        self.num_players_var = tk.StringVar(value=str(self.rule_data.get('num_players', '') or ''))

        # Create main frame with padding
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create labels and entry widgets
        fields = [
            ("Description", self.desc_var, "Brief description of the rule (e.g., 'OOP Check/Call, Turn Bet')"),
            ("Preflop Pattern", self.pf_var, "Regex pattern for preflop action sequence"),
            ("Flop Pattern", self.flop_var, "Regex pattern for flop action sequence"),
            ("Turn Pattern", self.turn_var, "Regex pattern for turn action sequence"),
            ("River Pattern", self.river_var, "Regex pattern for river action sequence"),
            ("Board Texture", self.board_var, "Comma-separated board textures (e.g., 'paired,A-high,monotone')"),
            ("Min Stack (bb)", self.min_stack_var, "Minimum effective stack in big blinds (optional)"),
            ("Max Stack (bb)", self.max_stack_var, "Maximum effective stack in big blinds (optional)"),
            ("Game Class (cash, tournament)", self.game_class_var, "Game class pattern (e.g., 'cash', 'tournament')"),
            ("Game Variant (zoom, regular)", self.game_variant_var, "Game variant pattern (e.g., 'zoom', 'regular')"),
            ("Table Size (6-max, 2-max)", self.table_size_var, "Table size pattern (e.g., '6-max', '2-max', '9-max')"),
            ("Legacy Game Type Pattern", self.game_type_var, "Legacy game type pattern (e.g., 'spingo%', 'holdem%')"),
            ("Legacy Num Players", self.num_players_var, "Legacy number of players (e.g., 6, 9, 2)")
        ]
        
        for i, (text, var, help_text) in enumerate(fields):
            # Label
            ttk.Label(main_frame, text=text + ":", font=("Arial", 10, "bold")).grid(
                row=i*2, column=0, padx=5, pady=(10,2), sticky='w'
            )
            
            # Help text
            ttk.Label(main_frame, text=help_text, font=("Arial", 8), foreground="gray").grid(
                row=i*2+1, column=0, padx=5, pady=(0,5), sticky='w'
            )
            
            # Entry widget
            entry = ttk.Entry(main_frame, textvariable=var, width=60)
            entry.grid(row=i*2+1, column=1, padx=5, pady=(0,5), sticky='ew')

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=len(fields)*2, column=0, columnspan=2, pady=20)
        
        save_btn = ttk.Button(button_frame, text="Save Rule", command=self.save_and_close)
        save_btn.pack(side=tk.LEFT, padx=5)
        
        cancel_btn = ttk.Button(button_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        
        # Focus on first entry
        main_frame.focus_set()

    def save_and_close(self):
        # Update the dictionary with values from the UI
        self.rule_data['rule_description'] = self.desc_var.get()
        self.rule_data['pf_pattern'] = self.pf_var.get()
        self.rule_data['flop_pattern'] = self.flop_var.get()
        self.rule_data['turn_pattern'] = self.turn_var.get()
        self.rule_data['river_pattern'] = self.river_var.get()
        self.rule_data['board_texture'] = self.board_var.get()
        
        # New structured format fields
        self.rule_data['game_class_pattern'] = self.game_class_var.get()
        self.rule_data['game_variant_pattern'] = self.game_variant_var.get()
        self.rule_data['table_size_pattern'] = self.table_size_var.get()
        
        # Legacy fields for backward compatibility
        self.rule_data['game_type_pattern'] = self.game_type_var.get()
        
        # Validate and save stack depth fields
        try:
            min_val = self.min_stack_var.get().strip()
            max_val = self.max_stack_var.get().strip()
            self.rule_data['min_stack_bb'] = int(min_val) if min_val else None
            self.rule_data['max_stack_bb'] = int(max_val) if max_val else None
            players_val = self.num_players_var.get().strip()
            self.rule_data['num_players'] = int(players_val) if players_val else None
        except ValueError:
            messagebox.showerror("Validation Error", "Stack depth and number of players must be valid numbers.")
            return
        if self.db.save_rule(self.rule_data):
            self.callback()  # Refresh the list in the main window
            messagebox.showinfo("Success", "Rule saved successfully!")
            self.destroy()
        else:
            messagebox.showerror("Error", "Failed to save rule. Please check your input.")

class LibrarianApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Study Librarian")
        self.geometry("1200x800")  # Made window wider for the new layout

        self.db = DatabaseAccess(**DB_PARAMS)
        self.selected_doc_id = None

        # --- Main Paned Window Layout ---
        self.main_paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # --- Left Panel: Document List ---
        left_frame = ttk.Frame(self.main_paned)
        self.build_left_panel(left_frame)
        self.main_paned.add(left_frame, weight=2)

        # --- Right Panel: Document Details, Tags, and Rules ---
        right_frame = ttk.Frame(self.main_paned)
        self.build_right_panel(right_frame)
        self.main_paned.add(right_frame, weight=2)

        # Initial load of data
        self.populate_docs_tree()

    def build_left_panel(self, parent):
        docs_frame = ttk.LabelFrame(parent, text="All Study Documents")
        docs_frame.pack(fill=tk.BOTH, expand=True)

        self.docs_tree = ttk.Treeview(docs_frame, columns=("id", "title", "path"), show="headings", selectmode="browse")
        self.docs_tree.heading("id", text="ID")
        self.docs_tree.heading("title", text="Title")
        self.docs_tree.heading("path", text="File Path")
        self.docs_tree.column("id", width=50, anchor='center')
        self.docs_tree.column("title", width=300)
        self.docs_tree.column("path", width=400)
        self.docs_tree.pack(fill=tk.BOTH, expand=True, side=tk.TOP)
        self.docs_tree.bind("<<TreeviewSelect>>", self.on_document_select)

        button_frame = ttk.Frame(docs_frame)
        button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        ttk.Button(button_frame, text="Add New Document", command=self.add_new_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Remove Document", command=self.remove_document).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Refresh List", command=self.populate_docs_tree).pack(side=tk.LEFT, padx=5)

    def build_right_panel(self, parent):
        # --- Tags Section ---
        tags_frame = ttk.LabelFrame(parent, text="Tags for Selected Document")
        tags_frame.pack(fill=tk.X, pady=5)

        self.tags_tree = ttk.Treeview(tags_frame, columns=("id", "name"), show="headings", selectmode="browse", height=6)
        self.tags_tree.heading("id", text="ID")
        self.tags_tree.column("id", width=40, anchor='center')
        self.tags_tree.heading("name", text="Tag Name")
        self.tags_tree.column("name", width=150)
        self.tags_tree.pack(fill=tk.X, side=tk.TOP)
        self.tags_tree.bind("<<TreeviewSelect>>", self.on_tag_select)

        tags_button_frame = ttk.Frame(tags_frame)
        tags_button_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        ttk.Button(tags_button_frame, text="Assign Tag", command=self.assign_tag).pack(side=tk.LEFT, padx=5)
        ttk.Button(tags_button_frame, text="Remove Tag", command=self.remove_tag).pack(side=tk.LEFT, padx=5)
        ttk.Button(tags_button_frame, text="Create New Tag", command=self.create_new_tag).pack(side=tk.RIGHT, padx=5)

        # --- Rules Section ---
        rules_frame = ttk.LabelFrame(parent, text="Rules for Selected Tag")
        rules_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.rules_tree = ttk.Treeview(rules_frame, columns=("id", "description"), show="headings", selectmode="browse")
        self.rules_tree.heading("id", text="ID")
        self.rules_tree.column("id", width=40, anchor='center')
        self.rules_tree.heading("description", text="Rule Description")
        self.rules_tree.column("description", width=300)
        self.rules_tree.pack(fill=tk.BOTH, expand=True, side=tk.TOP)

        rules_btn_frame = ttk.Frame(rules_frame)
        rules_btn_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=5)
        ttk.Button(rules_btn_frame, text="Add Rule", command=self.add_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rules_btn_frame, text="Edit Rule", command=self.edit_rule).pack(side=tk.LEFT, padx=5)
        ttk.Button(rules_btn_frame, text="Delete Rule", command=self.delete_rule).pack(side=tk.LEFT, padx=5)

    def on_document_select(self, event):
        selection = self.docs_tree.selection()
        if not selection: 
            return
        
        doc_item = self.docs_tree.item(selection[0])
        self.selected_doc_id = doc_item['values'][0]
        self.populate_tags_tree()
        
        # Clear the rules tree since the tag selection is now invalid
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)

    def populate_tags_tree(self):
        for item in self.tags_tree.get_children():
            self.tags_tree.delete(item)
        if self.selected_doc_id:
            tags = self.db.get_tags_for_document(self.selected_doc_id)
            for tag_id, tag_name in tags:
                self.tags_tree.insert("", tk.END, values=(tag_id, tag_name))

    def on_tag_select(self, event):
        self.populate_rules_tree()

    def populate_rules_tree(self):
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        selection = self.tags_tree.selection()
        if not selection: 
            return
        
        tag_id = self.tags_tree.item(selection[0])['values'][0]
        rules = self.db.get_rules_for_tag(tag_id)
        for rule_id, desc in rules:
            self.rules_tree.insert("", tk.END, values=(rule_id, desc))

    def assign_tag(self):
        if not self.selected_doc_id:
            messagebox.showwarning("Warning", "Please select a document first.")
            return
        
        # Create a simple dialog with a dropdown of all available tags
        all_tags = self.db.get_all_tags()
        tag_names = {name: tag_id for tag_id, name in all_tags}

        if not tag_names:
            messagebox.showinfo("Info", "No tags exist. Please create one first.")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Assign Tag")
        dialog.geometry("300x150")
        dialog.transient(self)  # Make dialog modal to main window
        dialog.grab_set()  # Make dialog modal
        
        tk.Label(dialog, text="Select a tag to assign:").pack(padx=10, pady=5)
        
        tag_var = tk.StringVar(dialog)
        tag_dropdown = ttk.Combobox(dialog, textvariable=tag_var, values=list(tag_names.keys()), state="readonly")
        tag_dropdown.pack(padx=10, pady=5)
        
        def on_ok():
            selected_tag_name = tag_var.get()
            if selected_tag_name:
                selected_tag_id = tag_names[selected_tag_name]
                if self.db.assign_tag_to_document(self.selected_doc_id, selected_tag_id):
                    self.populate_tags_tree()
                    messagebox.showinfo("Success", f"Tag '{selected_tag_name}' assigned successfully.")
                else:
                    messagebox.showerror("Error", "Failed to assign tag. It may already be assigned.")
            dialog.destroy()
        
        def on_cancel():
            dialog.destroy()
        
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=on_ok).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel).pack(side=tk.LEFT, padx=5)

    def remove_tag(self):
        selection = self.tags_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tag to remove.")
            return
        
        tag_id = self.tags_tree.item(selection[0])['values'][0]
        tag_name = self.tags_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Removal", f"Are you sure you want to remove the tag '{tag_name}' from this document?"):
            if self.db.remove_tag_from_document(self.selected_doc_id, tag_id):
                self.populate_tags_tree()
                messagebox.showinfo("Success", f"Tag '{tag_name}' removed successfully.")
            else:
                messagebox.showerror("Error", "Failed to remove tag.")

    def create_new_tag(self):
        tag_name = simpledialog.askstring("Create Tag", "Enter the new tag name (e.g., DelayedCBetOOP):")
        if tag_name:
            if self.db.create_tag(tag_name):
                messagebox.showinfo("Success", f"Tag '{tag_name}' created.")
            else:
                messagebox.showerror("Error", "Could not create tag. Does it already exist?")

    def add_rule(self):
        selection = self.tags_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a tag to add a rule to.")
            return
        tag_id = self.tags_tree.item(selection[0])['values'][0]
        rule_data = {"tag_id": tag_id}  # New rule with its parent tag_id
        RuleEditorWindow(self, self.db, rule_data, self.populate_rules_tree)

    def edit_rule(self):
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a rule to edit.")
            return
        rule_id = self.rules_tree.item(selection[0])['values'][0]
        rule_data = self.db.get_rule_details(rule_id)
        if rule_data:
            RuleEditorWindow(self, self.db, rule_data, self.populate_rules_tree)
        else:
            messagebox.showerror("Error", "Could not load rule details.")
            
    def delete_rule(self):
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a rule to delete.")
            return
        
        rule_id = self.rules_tree.item(selection[0])['values'][0]
        rule_desc = self.rules_tree.item(selection[0])['values'][1]
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the rule '{rule_desc}'?"):
            if self.db.delete_rule(rule_id):
                self.populate_rules_tree()
                messagebox.showinfo("Success", "Rule deleted successfully.")
            else:
                messagebox.showerror("Error", "Failed to delete rule.")

    def populate_docs_tree(self):
        """Clears and re-populates the document list from the database."""
        for item in self.docs_tree.get_children():
            self.docs_tree.delete(item)
        
        documents = self.db.get_all_study_documents()
        for doc in documents:
            self.docs_tree.insert("", tk.END, values=doc)

    def add_new_document(self):
        """Opens dialogs to add a new study document to the database."""
        file_path = filedialog.askopenfilename(
            title="Select Obsidian Note",
            filetypes=(("Markdown files", "*.md"), ("All files", "*.*"))
        )
        if not file_path:
            return # User cancelled

        # Extract filename without extension as default title
        import os
        filename = os.path.basename(file_path)
        default_title = os.path.splitext(filename)[0]

        title = simpledialog.askstring("Document Title", "Enter the title for this document:", initialvalue=default_title)
        if not title:
            return # User cancelled

        if self.db.add_study_document(title, file_path):
            messagebox.showinfo("Success", "Document added successfully.")
            self.populate_docs_tree()
        else:
            messagebox.showerror("Error", "Failed to add document. Is the file path already in the library?")

    def remove_document(self):
        """Removes the selected document from the library."""
        selection = self.docs_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a document to remove.")
            return
        
        doc_item = self.docs_tree.item(selection[0])
        doc_id = doc_item['values'][0]
        doc_title = doc_item['values'][1]
        doc_path = doc_item['values'][2]
        
        # Show confirmation dialog with document details
        confirm_message = f"Are you sure you want to remove this document?\n\nTitle: {doc_title}\nPath: {doc_path}\n\nThis will also remove all tag associations for this document."
        
        if messagebox.askyesno("Confirm Document Removal", confirm_message):
            if self.db.delete_study_document(doc_id):
                messagebox.showinfo("Success", f"Document '{doc_title}' removed successfully.")
                # Clear the selected document if it was the one being removed
                if self.selected_doc_id == doc_id:
                    self.selected_doc_id = None
                    # Clear the tags tree
                    for item in self.tags_tree.get_children():
                        self.tags_tree.delete(item)
                    # Clear the rules tree
                    for item in self.rules_tree.get_children():
                        self.rules_tree.delete(item)
                self.populate_docs_tree()
            else:
                messagebox.showerror("Error", "Failed to remove document.")

    def on_close(self):
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = LibrarianApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop() 