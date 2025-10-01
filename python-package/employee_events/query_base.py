from abc import ABC, abstractmethod
from typing import List, Tuple

import pandas as pd

from employee_events.sql_execution import QueryMixin


class QueryBase(QueryMixin, ABC):
    """Base class for executing SQL queries on the employee events database."""

    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def names(self) -> List[Tuple[str, ...]]: ...

    @abstractmethod
    def username(self, id: int) -> List[Tuple[str, ...]]: ...

    @abstractmethod
    def model_data(self, id: int) -> pd.DataFrame: ...

    def event_counts(self, id: int) -> pd.DataFrame:
        """Retrieves the sum of positive and negative events grouped by event date
        for a given employee or team ID.

        Args:
            id (int): The employee_id or team_id to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing event_date, positive_events, and negative_events.
        """
        sql_query = f"""
                    SELECT 
                        event_date,
                        SUM(positive_events) AS positive_events,
                        SUM(negative_events) AS negative_events
                    FROM employee_events
                    WHERE {self.name}_id = {id}
                    GROUP BY event_date
                    ORDER BY event_date;
                    """
        return self.pandas_query(sql_query)

    def notes(self, id: int) -> pd.DataFrame:
        """Retrieves notes and their dates for a given employee or team ID.

        Args:
            id (int): The employee_id or team_id to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing note_date and note.
        """
        sql_query = f"""
                    SELECT 
                        note_date,
                        note
                    FROM notes
                    WHERE {self.name}_id = {id}            
                    ORDER BY note_date;
                    """
        return self.pandas_query(sql_query)
