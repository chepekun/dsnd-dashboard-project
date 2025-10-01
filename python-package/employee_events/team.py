from typing import List, Tuple, override

import pandas as pd

from employee_events.query_base import QueryBase


class Team(QueryBase):
    """Query class for retrieving team-specific data from the employee events database."""

    @property
    @override
    def name(self) -> str:
        """Returns the name used for dynamic SQL filtering.

        Returns:
            str: The string `"team"`.
        """
        return "team"

    @override
    def names(self) -> List[Tuple[str, ...]]:
        """Retrieves the names and IDs of all teams in the database.

        Returns:
            List[Tuple[str, ...]]: A list of tuples containing team name and team ID.
        """
        sql_query = """
                    SELECT 
                        team_name,
                        team_id
                    FROM team
                    ORDER BY team_id
                    """
        return self.query(sql_query)

    @override
    def username(self, id: int) -> List[Tuple[str, ...]]:
        """Retrieves the name of a specific team by ID.

        Args:
            id (int): The team ID to filter by.

        Returns:
            List[Tuple[str, ...]]: A list containing a single tuple with the team name.
        """
        sql_query = f"""
                    SELECT 
                        team_name
                    FROM {self.name}
                    WHERE team_id = {id};
                    """
        return self.query(sql_query)

    @override
    def model_data(self, id: int) -> pd.DataFrame:
        """Aggregates positive and negative events per employee within a specific team.

        Args:
            id (int): The team ID to filter by.

        Returns:
            pd.DataFrame: A DataFrame containing employee-level sums of positive and negative events.
        """
        sql_query = f"""
                    SELECT positive_events, negative_events FROM (
                        SELECT employee_id
                            , SUM(positive_events) positive_events
                            , SUM(negative_events) negative_events
                        FROM {self.name}
                        JOIN employee_events
                            USING({self.name}_id)
                        WHERE {self.name}.{self.name}_id = {id}
                        GROUP BY employee_id
                    )
                    """
        return self.pandas_query(sql_query)
