# librarian_app.py
import tkinter as tk
from tkinter import ttk, filedialog, simpledialog, messagebox
from scripts.db_access import DatabaseAccess # Fixed import path
from scripts.config import DB_PARAMS # Fixed import path

class LibrarianApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Study Librarian")
        self.geometry("800x600")

        self.db = DatabaseAccess(**DB_PARAMS)

        # --- Main Frame ---
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Document List ---
        tree_frame = ttk.LabelFrame(main_frame, text="Study Documents")
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.docs_tree = ttk.Treeview(tree_frame, columns=("id", "title", "path"), show="headings")
        self.docs_tree.heading("id", text="ID")
        self.docs_tree.heading("title", text="Title")
        self.docs_tree.heading("path", text="File Path")
        self.docs_tree.column("id", width=50, anchor='center')
        self.docs_tree.column("title", width=300)
        self.docs_tree.column("path", width=400)
        self.docs_tree.pack(fill=tk.BOTH, expand=True)

        # --- Button Panel ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=5)

        add_btn = ttk.Button(button_frame, text="Add New Document", command=self.add_new_document)
        add_btn.pack(side=tk.LEFT, padx=5)
        
        refresh_btn = ttk.Button(button_frame, text="Refresh List", command=self.populate_docs_tree)
        refresh_btn.pack(side=tk.LEFT, padx=5)

        # Initial load of data
        self.populate_docs_tree()

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

        title = simpledialog.askstring("Document Title", "Enter the title for this document:")
        if not title:
            return # User cancelled

        if self.db.add_study_document(title, file_path):
            messagebox.showinfo("Success", "Document added successfully.")
            self.populate_docs_tree()
        else:
            messagebox.showerror("Error", "Failed to add document. Is the file path already in the library?")

    def on_close(self):
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = LibrarianApp()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop() 