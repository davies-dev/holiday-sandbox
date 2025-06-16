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


class SortCriterion:
    def __init__(self, field: str, direction: str = "ASC"):
        """
        Initializes a sort criterion.
        
        Args:
            field (str): The database field to sort by.
            direction (str): The sort direction, either "ASC" or "DESC".
        """
        if direction.upper() not in ["ASC", "DESC"]:
            raise ValueError("Sort direction must be either 'ASC' or 'DESC'")
        self.field = field
        self.direction = direction.upper()

    def to_sql(self) -> str:
        """
        Converts the sort criterion to a SQL snippet.
        """
        return f"{self.field} {self.direction}"


class QueryBuilder:
    def __init__(self, base_query: str = "SELECT * FROM hand_histories"):
        """
        Initializes the query builder.
        
        Args:
            base_query (str): The base query without conditions.
        """
        self.base_query = base_query
        self.conditions = []
        self.sort_criteria = []
    
    def add_condition(self, condition: Condition):
        """
        Adds a condition to the query.
        
        Args:
            condition (Condition): A condition object.
        """
        self.conditions.append(condition)
    
    def add_sort(self, sort_criterion: SortCriterion):
        """
        Adds a sort criterion to the query.
        
        Args:
            sort_criterion (SortCriterion): A sort criterion object.
        """
        self.sort_criteria.append(sort_criterion)
    
    def build_query(self) -> str:
        """
        Builds and returns the final query string.
        If conditions exist, they are appended using a WHERE clause.
        If sort criteria exist, they are appended using an ORDER BY clause.
        """
        query = self.base_query
        
        # Add WHERE clause if there are conditions
        if self.conditions:
            cond_sql = " AND ".join([cond.to_sql() for cond in self.conditions])
            query += f" WHERE {cond_sql}"
        
        # Add ORDER BY clause if there are sort criteria
        if self.sort_criteria:
            sort_sql = ", ".join([sort.to_sql() for sort in self.sort_criteria])
            query += f" ORDER BY {sort_sql}"
            
        return query


# Example usage:
if __name__ == "__main__":
    # Create some conditions
    cond1 = Condition("game_type", "=", "zoom_cash_6max")
    cond2 = Condition("actions", "LIKE", "%raise%")
    cond3 = Condition("player_names", "LIKE", "%HumptyD%")
    
    # Create sort criteria
    sort1 = SortCriterion("id", "DESC")
    sort2 = SortCriterion("game_type", "ASC")
    
    # Build the query
    qb = QueryBuilder("SELECT * FROM hand_histories")
    qb.add_condition(cond1)
    qb.add_condition(cond2)
    qb.add_condition(cond3)
    qb.add_sort(sort1)
    qb.add_sort(sort2)
    
    query = qb.build_query()
    print("Generated Query:")
    print(query)
