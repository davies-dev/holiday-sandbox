import tkinter as tk
from tkinter import messagebox
from db_access import DatabaseAccess
from query_builder import QueryBuilder, Condition
from config import DB_PARAMS

class UncalledBetFinder(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Uncalled Bet Finder")
        self.geometry("400x200")
        
        # Create our database access instance.
        self.db = DatabaseAccess(**DB_PARAMS)
        
        # Create a button to trigger the search and file writing.
        self.search_button = tk.Button(self, text="Find Uncalled Bets", command=self.find_uncalled_bets)
        self.search_button.pack(pady=20)
        
        # Create a label to display status messages.
        self.status_label = tk.Label(self, text="")
        self.status_label.pack(pady=10)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def find_uncalled_bets(self):
        # Build a query to retrieve hand histories.
        qb = QueryBuilder("SELECT id, raw_text FROM hand_histories")
        # Optionally, you can add conditions here if needed.
        query = qb.build_query()
        
        try:
            with self.db.conn.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            
            # Filter rows to find those with a line starting with "Uncalled bet".
            uncalled_bet_hands = []
            for row in rows:
                hand_id, raw_text = row
                if raw_text and any(line.strip().startswith("Uncalled bet") for line in raw_text.splitlines()):
                    uncalled_bet_hands.append(row)
                    if len(uncalled_bet_hands) >= 50:
                        break
            
            # Write the filtered hand histories to a text file.
            if uncalled_bet_hands:
                with open("uncalled_bet_hands.txt", "w") as f:
                    for hand_id, raw_text in uncalled_bet_hands:
                        f.write(f"Hand ID: {hand_id}\n")
                        f.write(raw_text)
                        f.write("\n\n")
                self.status_label.config(text=f"Found {len(uncalled_bet_hands)} hand histories. Written to uncalled_bet_hands.txt.")
            else:
                self.status_label.config(text="No hand histories found with 'Uncalled bet'.")
        except Exception as e:
            messagebox.showerror("Error", f"Error: {e}")
            self.status_label.config(text="Error occurred.")
    
    def on_close(self):
        self.db.close()
        self.destroy()

if __name__ == "__main__":
    app = UncalledBetFinder()
    app.mainloop() 