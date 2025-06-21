import json
import os

class SavedStateManager:
    """
    A simple manager for saving and loading UI or query states.
    This class abstracts the persistence details (using a JSON file) so that
    the rest of your application can simply use get_state, set_state, delete_state,
    and list_states.
    """
    def __init__(self, filename="saved_states.json"):
        self.filename = filename
        self.states = {}
        self.load_states()
        
    def load_states(self):
        """Load saved states from the JSON file, if it exists."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r") as f:
                    self.states = json.load(f)
            except Exception as e:
                print(f"Error loading states from {self.filename}: {e}")
                self.states = {}
        else:
            self.states = {}
            
    def save_states(self):
        """Persist the current states to the JSON file."""
        try:
            with open(self.filename, "w") as f:
                json.dump(self.states, f, indent=2)
        except Exception as e:
            print(f"Error saving states to {self.filename}: {e}")
    
    def set_state(self, name, state_data):
        """
        Save or update a state.
        
        Args:
            name (str): A unique name for the state.
            state_data (dict): A dictionary representing the state.
        """
        self.states[name] = state_data
        self.save_states()
    
    def get_state(self, name):
        """
        Retrieve a saved state by its name.
        
        Returns:
            dict or None: The state data if it exists, or None if not found.
        """
        return self.states.get(name)
    
    def delete_state(self, name):
        """Delete a saved state by its name."""
        if name in self.states:
            del self.states[name]
            self.save_states()
    
    def list_states(self):
        """Return a list of all saved state names."""
        return list(self.states.keys())

# Example usage:
if __name__ == "__main__":
    # Create an instance of the state manager.
    sm = SavedStateManager()
    
    # Example state data for a query (this could be UI settings, query conditions, etc.)
    state_data = {
        "query_conditions": [
            {"field": "game_type", "operator": "LIKE", "value": "zoom_cash_6max%"},
            {"field": "pf_action_seq", "operator": "=", "value": "1f2f3f4r5r6r5c"}
        ],
        "other_settings": {
            "display_mode": "detailed"
        }
    }
    
    # Save a state.
    sm.set_state("ExampleQuery", state_data)
    
    # List saved states.
    print("Saved states:", sm.list_states())
    
    # Retrieve a state.
    retrieved_state = sm.get_state("ExampleQuery")
    print("Retrieved state 'ExampleQuery':", retrieved_state)
    
    # Uncomment the following line to delete the state.
    # sm.delete_state("ExampleQuery")
