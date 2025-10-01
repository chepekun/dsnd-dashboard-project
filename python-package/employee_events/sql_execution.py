from pathlib import Path
from sqlite3 import connect
from typing import List, Tuple

import pandas as pd

db_path = Path(__file__).parent / "employee_events.db"


class QueryMixin:
    def pandas_query(self, sql_query: str) -> pd.DataFrame:
        """Executes an SQL query using pandas and returns the result as a DataFrame.

        Args:
            sql_query (str): A valid SQL query.

        Returns:
            A pandas DataFrame containing the query results.
        """
        return pd.read_sql_query(sql_query, connect(db_path))

    def query(self, sql_query: str) -> List[Tuple[str, ...]]:
        """Executes an SQL query and returns the result as a list of tuples.

        Args:
            sql_query (str): A valid SQL query.

        Returns:
            A list of tuples containing the query results.
        """
        with connect(db_path) as db_conn:
            cursor = db_conn.cursor()
            result = cursor.execute(sql_query).fetchall()
            return list(result)
