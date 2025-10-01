from typing import List, Tuple, override

import pandas as pd

from employee_events.query_base import QueryBase


class Employee(QueryBase):
    """Query class for retrieving employee-specific data from the employee events database."""

    @property
    @override
    def name(self) -> str:
        """Returns the name used for dynamic SQL filtering.

        Returns:
            str: The string `"employee"`.
        """
        return "employee"

    @override
    def names(self) -> List[Tuple[str, ...]]:
        """Retrieves the full names and IDs of all employees in the database.

        Returns:
            List[Tuple[str, ...]]: A list of tuples containing full name and employee ID.
        """
        sql_query = """
                    SELECT 
                        first_name || ' ' || last_name AS full_name,
                        employee_id
                    FROM employee
                    ORDER BY employee_id;
                    """

        return self.query(sql_query)

    @override
    def username(self, id: int) -> List[Tuple[str, ...]]:
        """Retrieves the full name of a specific employee by ID.

        Args:
            id (int): The employee ID to filter by.

        Returns:
            List[Tuple[str, ...]]: A list containing a single tuple with the employee's full name.
        """
        sql_query = f"""
                    SELECT 
                        first_name || ' ' || last_name AS full_name
                    FROM employee
                    WHERE employee_id = {id};
                    """
        return self.query(sql_query)

    @override
    def model_data(self, id: int) -> pd.DataFrame:
        """Aggregates positive and negative events for a specific employee.

        Args:
            id (int): The employee ID to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing the total positive and negative events.
        """
        sql_query = f"""
                    SELECT SUM(positive_events) positive_events
                         , SUM(negative_events) negative_events
                    FROM {self.name}
                    JOIN employee_events
                        USING({self.name}_id)
                    WHERE {self.name}.{self.name}_id = {id}
                """
        return self.pandas_query(sql_query)
