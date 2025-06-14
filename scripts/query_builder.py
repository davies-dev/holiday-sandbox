class Condition:
    def __init__(self, field: str, operator: str, value):
        """
        Initializes a condition.
        
        Args:
            field (str): The database field (or domain attribute) to filter on.
            operator (str): The operator (e.g., '=', '<', '>', 'LIKE', etc.).
            value: The value to compare against.
        """
        self.field = field
        self.operator = operator
        self.value = value

    def to_sql(self) -> str:
        """
        Converts the condition to a SQL snippet.
        If the value is a string, it is quoted.
        """
        if isinstance(self.value, str):
            value_str = f"'{self.value}'"
        else:
            value_str = str(self.value)
        return f"{self.field} {self.operator} {value_str}"


class QueryBuilder:
    def __init__(self, base_query: str = "SELECT * FROM hand_histories"):
        """
        Initializes the query builder.
        
        Args:
            base_query (str): The base query without conditions.
        """
        self.base_query = base_query
        self.conditions = []
    
    def add_condition(self, condition: Condition):
        """
        Adds a condition to the query.
        
        Args:
            condition (Condition): A condition object.
        """
        self.conditions.append(condition)
    
    def build_query(self) -> str:
        """
        Builds and returns the final query string.
        If conditions exist, they are appended using a WHERE clause.
        """
        if not self.conditions:
            return self.base_query
        cond_sql = " AND ".join([cond.to_sql() for cond in self.conditions])
        return f"{self.base_query} WHERE {cond_sql}"


# Example usage:
if __name__ == "__main__":
    # Create some conditions
    cond1 = Condition("game_type", "=", "zoom_cash_6max")
    cond2 = Condition("actions", "LIKE", "%raise%")
    cond3 = Condition("player_names", "LIKE", "%HumptyD%")
    
    # Build the query
    qb = QueryBuilder("SELECT * FROM hand_histories")
    qb.add_condition(cond1)
    qb.add_condition(cond2)
    qb.add_condition(cond3)
    
    query = qb.build_query()
    print("Generated Query:")
    print(query)
