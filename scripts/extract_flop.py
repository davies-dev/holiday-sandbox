import tkinter as tk
from tkinter import scrolledtext
import re

class ExtractFlopApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Extract Board Cards")
        self.root.geometry("800x600")
        
        # Create input text area
        self.input_label = tk.Label(root, text="Paste Hand History Here:")
        self.input_label.pack(pady=5)
        
        self.input_text = scrolledtext.ScrolledText(root, width=80, height=20)
        self.input_text.pack(pady=5)
        
        # Create button frame
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)
        
        # Create extract buttons
        self.extract_flop_button = tk.Button(button_frame, text="Extract Flop", command=lambda: self.extract_cards("flop"))
        self.extract_flop_button.pack(side=tk.LEFT, padx=5)
        
        self.extract_turn_button = tk.Button(button_frame, text="Extract Turn", command=lambda: self.extract_cards("turn"))
        self.extract_turn_button.pack(side=tk.LEFT, padx=5)
        
        self.extract_river_button = tk.Button(button_frame, text="Extract River", command=lambda: self.extract_cards("river"))
        self.extract_river_button.pack(side=tk.LEFT, padx=5)
        
        # Create output text area
        self.output_label = tk.Label(root, text="Board Cards:")
        self.output_label.pack(pady=5)
        
        self.output_text = scrolledtext.ScrolledText(root, width=80, height=5)
        self.output_text.pack(pady=5)
        
    def extract_cards(self, street):
        # Get the input text
        hand_history = self.input_text.get("1.0", tk.END)
        
        # Clear the output text
        self.output_text.delete("1.0", tk.END)
        
        # Find the street line
        if street == "flop":
            pattern = r'\*\*\* FLOP \*\*\* \[([^\]]+)\]'
        elif street == "turn":
            pattern = r'\*\*\* TURN \*\*\* \[[^\]]+\] \[([^\]]+)\]'
        else:  # river
            pattern = r'\*\*\* RIVER \*\*\* \[[^\]]+ [^\]]+\] \[([^\]]+)\]'
            
        match = re.search(pattern, hand_history)
        
        if match:
            cards = match.group(1)
            self.output_text.insert("1.0", f"{street.upper()} Cards: {cards}")
        else:
            self.output_text.insert("1.0", f"No {street} found in the hand history")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExtractFlopApp(root)
    root.mainloop() 