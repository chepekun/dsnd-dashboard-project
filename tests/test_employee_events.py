from pathlib import Path
from sqlite3 import connect
from typing import List

import pandas as pd
import pytest
from employee_events import Employee, QueryBase, QueryMixin, Team

project_root = Path(__file__).parents[1]

# ===== tests database


@pytest.fixture
def db_path() -> Path:
    return project_root / "python-package" / "employee_events" / "employee_events.db"


@pytest.fixture
def table_names(db_path: Path) -> List[str]:
    with connect(db_path) as db_conn:
        name_tuples = db_conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        return [x[0] for x in name_tuples]


def test_db_exists(db_path: Path) -> None:
    assert db_path.is_file


def test_employee_table_exists(table_names: List[str]) -> None:
    assert "employee" in table_names


def test_team_table_exists(table_names: List[str]) -> None:
    assert "team" in table_names


def test_employee_events_table_exists(table_names: List[str]) -> None:
    assert "employee_events" in table_names


# ===== test employee events


def test_query_mixin() -> None:
    query_mixin = QueryMixin()

    # test employee table
    sql_query = "SELECT * FROM employee;"
    df = query_mixin.pandas_query(sql_query)
    assert all(x in df.columns for x in ["employee_id", "first_name", "last_name", "team_id"])
    assert list(df.itertuples(index=False, name=None))[0] == query_mixin.query(sql_query)[0]

    # test team table
    sql_query = "SELECT * FROM team;"
    df = query_mixin.pandas_query(sql_query)
    assert all(x in df.columns for x in ["team_id", "team_name", "shift", "manager_name"])
    assert list(df.itertuples(index=False, name=None))[0] == query_mixin.query(sql_query)[0]

    # test events_table
    sql_query = "SELECT * FROM employee_events;"
    df = query_mixin.pandas_query(sql_query)
    assert all(x in df.columns for x in ["event_date", "employee_id", "team_id", "positive_events", "negative_events"])
    assert list(df.itertuples(index=False, name=None))[0] == query_mixin.query(sql_query)[0]

    # test notes table
    sql_query = "SELECT * FROM notes;"
    df = query_mixin.pandas_query(sql_query)
    assert all(x in df.columns for x in ["employee_id", "team_id", "note", "note_date"])
    assert list(df.itertuples(index=False, name=None))[0] == query_mixin.query(sql_query)[0]


def test_employee() -> None:
    employee = Employee()
    assert employee.name == "employee"
    query_base_helper(employee)

    # test model data
    df = QueryMixin().pandas_query("SELECT * FROM employee_events;")
    df_model_data = (
        df[df["employee_id"] == 1].groupby(["employee_id"]).sum().reset_index()[["positive_events", "negative_events"]]
    )
    assert all(df_model_data == employee.model_data(1))


def test_team() -> None:
    team = Team()
    assert team.name == "team"
    query_base_helper(team)

    # test model data
    df = QueryMixin().pandas_query("SELECT * FROM employee_events;")
    df_model_data = (
        df[df["team_id"] == 1]
        .groupby(["employee_id"])
        .sum()
        .sort_index()
        .reset_index()[["positive_events", "negative_events"]]
    )
    assert all(df_model_data == team.model_data(1))


def query_base_helper(query_base: QueryBase) -> None:
    # get all employee/team names and ids
    df_names = pd.DataFrame(query_base.names())
    assert df_names.shape[1] == 2
    assert df_names.dtypes.to_list() == [object, int]

    # for given id, get employee/team name
    df_username = pd.DataFrame(query_base.username(1))
    assert df_username.shape[1] == 1
    assert df_username.shape == (1, 1)
    assert df_username[0][0] == df_names[0][0]

    # for given id, get employee/team's sum of positive and negative events
    df_model_data = query_base.model_data(1)
    assert all(df_model_data.columns == ["positive_events", "negative_events"])
    assert df_model_data.dtypes.to_list() == [int, int]

    # for given id, get employee/team's positive and negative events across dates
    df_event_counts = query_base.event_counts(1)
    assert all(df_event_counts.columns == ["event_date", "positive_events", "negative_events"])
    assert df_event_counts.dtypes.to_list() == [object, int, int]

    # for a given id, get employee/team's notes
    df_notes = query_base.notes(1)
    assert all(df_notes.columns == ["note_date", "note"])
    assert df_notes.dtypes.to_list() == [object, object]

    # test SQL queries on event_count table
    df = QueryMixin().pandas_query("SELECT * FROM employee_events;")
    df_event_count = (
        df[df[query_base.name + "_id"] == 1]
        .groupby(["event_date"])
        .sum()
        .sort_index()
        .reset_index()[["event_date", "positive_events", "negative_events"]]
    )
    assert all(df_event_count == query_base.event_counts(1))
