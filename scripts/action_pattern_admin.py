#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
from db_access import DatabaseAccess

# Database connection parameters.
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "HolidayBrowser"
DB_USER = "postgres"
DB_PASS = "Holidayedy123"

class ActionPatternAdmin(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Action Pattern Admin")
        self.geometry("800x400")
        self.db = DatabaseAccess(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS)
        self.selected_pattern_id = None

        self.create_widgets()
        self.load_patterns()

    def create_widgets(self):
        # Left frame: listbox to show existing patterns.
        left_frame = ttk.Frame(self)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(left_frame, text="Existing Action Patterns:").pack(anchor=tk.W)
        self.pattern_listbox = tk.Listbox(left_frame)
        self.pattern_listbox.pack(fill=tk.BOTH, expand=True)
        self.pattern_listbox.bind("<<ListboxSelect>>", self.on_pattern_select)

        # Right frame: form to add/update patterns.
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        ttk.Label(right_frame, text="Pattern Name:").pack(anchor=tk.W)
        self.pattern_name_var = tk.StringVar()
        self.pattern_name_entry = ttk.Entry(right_frame, textvariable=self.pattern_name_var, width=40)
        self.pattern_name_entry.pack(anchor=tk.W, pady=5)

        ttk.Label(right_frame, text="Applies To:").pack(anchor=tk.W)
        self.applies_to_var = tk.StringVar()
        self.applies_to_entry = ttk.Entry(right_frame, textvariable=self.applies_to_var, width=40)
        self.applies_to_entry.pack(anchor=tk.W, pady=5)

        ttk.Label(right_frame, text="SQL Pattern:").pack(anchor=tk.W)
        self.sql_pattern_var = tk.StringVar()
        self.sql_pattern_entry = ttk.Entry(right_frame, textvariable=self.sql_pattern_var, width=40)
        self.sql_pattern_entry.pack(anchor=tk.W, pady=5)

        ttk.Label(right_frame, text="Description:").pack(anchor=tk.W)
        self.description_var = tk.StringVar()
        self.description_entry = ttk.Entry(right_frame, textvariable=self.description_var, width=40)
        self.description_entry.pack(anchor=tk.W, pady=5)

        # Buttons.
        button_frame = ttk.Frame(right_frame)
        button_frame.pack(anchor=tk.CENTER, pady=10)

        self.add_button = ttk.Button(button_frame, text="Add Pattern", command=self.add_pattern)
        self.add_button.pack(side=tk.LEFT, padx=5)
        self.update_button = ttk.Button(button_frame, text="Update Pattern", command=self.update_pattern)
        self.update_button.pack(side=tk.LEFT, padx=5)
        self.delete_button = ttk.Button(button_frame, text="Delete Pattern", command=self.delete_pattern)
        self.delete_button.pack(side=tk.LEFT, padx=5)
        self.clear_button = ttk.Button(button_frame, text="Clear", command=self.clear_form)
        self.clear_button.pack(side=tk.LEFT, padx=5)

    def load_patterns(self):
        """Load patterns from the database into the listbox."""
        self.pattern_listbox.delete(0, tk.END)
        query = "SELECT id, pattern_name, applies_to, sql_pattern, description FROM action_patterns ORDER BY id"
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()
            self.patterns = rows  # Save fetched rows for lookup.
            for row in rows:
                pattern_id, pattern_name, applies_to, sql_pattern, description = row
                display_text = f"{pattern_id}: {pattern_name} ({applies_to}) -> {sql_pattern}"
                self.pattern_listbox.insert(tk.END, display_text)
        except Exception as e:
            messagebox.showerror("Error", f"Error loading patterns: {e}")

    def on_pattern_select(self, event):
        """When a pattern is selected, populate the form with its data."""
        selection = self.pattern_listbox.curselection()
        if selection:
            index = selection[0]
            pattern = self.patterns[index]
            self.selected_pattern_id = pattern[0]
            self.pattern_name_var.set(pattern[1])
            self.applies_to_var.set(pattern[2])
            self.sql_pattern_var.set(pattern[3])
            self.description_var.set(pattern[4] if pattern[4] else "")
        else:
            self.selected_pattern_id = None

    def add_pattern(self):
        """Insert a new pattern into the database."""
        pattern_name = self.pattern_name_var.get().strip()
        applies_to = self.applies_to_var.get().strip()
        sql_pattern = self.sql_pattern_var.get().strip()
        description = self.description_var.get().strip()

        if not pattern_name or not applies_to or not sql_pattern:
            messagebox.showerror("Error", "Pattern name, applies to, and SQL pattern are required.")
            return

        query = """
            INSERT INTO action_patterns (pattern_name, applies_to, sql_pattern, description)
            VALUES (%s, %s, %s, %s)
        """
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query, (pattern_name, applies_to, sql_pattern, description))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Pattern added successfully.")
            self.load_patterns()
            self.clear_form()
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Error adding pattern: {e}")

    def update_pattern(self):
        """Update the selected pattern in the database."""
        if not self.selected_pattern_id:
            messagebox.showerror("Error", "No pattern selected for update.")
            return

        pattern_name = self.pattern_name_var.get().strip()
        applies_to = self.applies_to_var.get().strip()
        sql_pattern = self.sql_pattern_var.get().strip()
        description = self.description_var.get().strip()

        if not pattern_name or not applies_to or not sql_pattern:
            messagebox.showerror("Error", "Pattern name, applies to, and SQL pattern are required.")
            return

        query = """
            UPDATE action_patterns
            SET pattern_name = %s,
                applies_to = %s,
                sql_pattern = %s,
                description = %s,
                updated_at = NOW()
            WHERE id = %s
        """
        try:
            with self.db.conn.cursor() as cur:
                cur.execute(query, (pattern_name, applies_to, sql_pattern, description, self.selected_pattern_id))
            self.db.conn.commit()
            messagebox.showinfo("Success", "Pattern updated successfully.")
            self.load_patterns()
            self.clear_form()
        except Exception as e:
            self.db.conn.rollback()
            messagebox.showerror("Error", f"Error updating pattern: {e}")

    def delete_pattern(self):
        """Delete the selected pattern from the database."""
        if not self.selected_pattern_id:
            messagebox.showerror("Error", "No pattern selected for deletion.")
            return

        if messagebox.askyesno("Confirm", "Are you sure you want to delete the selected pattern?"):
            query = "DELETE FROM action_patterns WHERE id = %s"
            try:
                with self.db.conn.cursor() as cur:
                    cur.execute(query, (self.selected_pattern_id,))
                self.db.conn.commit()
                messagebox.showinfo("Success", "Pattern deleted successfully.")
                self.load_patterns()
                self.clear_form()
            except Exception as e:
                self.db.conn.rollback()
                messagebox.showerror("Error", f"Error deleting pattern: {e}")

    def clear_form(self):
        """Clear the form fields."""
        self.selected_pattern_id = None
        self.pattern_name_var.set("")
        self.applies_to_var.set("")
        self.sql_pattern_var.set("")
        self.description_var.set("")
        self.pattern_listbox.selection_clear(0, tk.END)

    def on_close(self):
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = ActionPatternAdmin()
    app.mainloop()
