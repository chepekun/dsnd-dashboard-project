from typing import override

import fasthtml.common as fh
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from base_components import BaseComponent, DataTable, Dropdown, MatplotlibViz, Radio
from combined_components import CombinedComponent, FormGroup
from employee_events import Employee, QueryBase, Team
from utils import ClassifierModel, load_model


class Report(CombinedComponent):
    """Contains all components in the dashboard"""

    @property
    @override
    def children(self):
        return [DashboardFilters(), Header(), Visualizations(), NotesTable()]


class Header(BaseComponent):
    """Displays the level used for the analysis, employee or team"""

    @override
    def build_component(self, entity_id: int, model: QueryBase):
        return fh.H1(
            model.name.capitalize() + " Performance",
            style="text-align: center;",
        )


class DashboardFilters(FormGroup):
    """Selects the employee or team to analyze"""

    id = "top-filters"
    action = "/update_data/"
    method = "POST"

    @property
    @override
    def children(self):
        return [
            Radio(  # switch between employee or team
                values=["Employee", "Team"],
                name="profile_type",
                hx_get="/update_dropdown/",
                hx_target="#selector",
            ),
            ReportDropdown(  # select employee or team name
                id="selector",
                name="user-selection",
            ),
        ]


class ReportDropdown(Dropdown):
    """Dropdown used to select employee's or team's name"""

    @override
    def build_component(self, entity_id: int, model: QueryBase):
        self.label = model.name.capitalize()
        return super().build_component(entity_id, model)

    @override
    def component_data(self, entity_id: int, model: QueryBase):
        return pd.DataFrame(model.names())


class Visualizations(CombinedComponent):
    """Contains the line plot with the events and the predicted recruitment risk"""

    @property
    @override
    def children(self):
        return [LineChart(), BarChart()]

    outer_div_type = fh.Div(cls="grid")


class LineChart(MatplotlibViz):
    """Displays a line plot of the positive and negative events for the employee/team"""

    @override
    def visualization(self, entity_id: int, model: QueryBase):
        df = model.event_counts(entity_id)
        df.fillna(0, inplace=True)
        df.set_index("event_date", inplace=True)
        df.sort_index(inplace=True)
        df = df.cumsum()
        df.columns = ["Positive", "Negative"]

        _, ax = plt.subplots()
        df.plot(ax=ax, kind="line", style=["-g", "-r"])
        self.set_axis_styling(ax, bordercolor="black", fontcolor="black")
        ax.set_xlabel("Event date")
        ax.set_ylabel("Cumulative Sum of Events")
        ax.set_title(model.username(entity_id)[0][0])


class BarChart(MatplotlibViz):
    """Displays a bar plot with the predicted recruitment risk for the employee/team"""

    @property
    def predictor(self) -> ClassifierModel:
        return load_model()

    @override
    def visualization(self, entity_id: int, model: QueryBase):
        data = model.model_data(entity_id)

        probabilities = self.predictor.predict_proba(data)
        if model.name == "team":
            pred = np.mean(probabilities, axis=0)[1]
        else:
            pred = probabilities[0][1]

        _, ax = plt.subplots()
        ax.barh(y=[""], width=[pred], edgecolor="black")
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, 0.5)
        ax.set_title("Predicted Recruitment Risk")
        ax.set_xlabel("Probability")
        self.set_axis_styling(ax, bordercolor="black", fontcolor="black")


class NotesTable(DataTable):
    """Displays a table of all the notes for the employee/team"""

    @override
    def component_data(self, entity_id: int, model: QueryBase):
        return model.notes(entity_id)


# ============== App

app, route = fh.fast_app()

report = Report()


@app.get("/")
def get_home():
    """Initiate view for employee 1"""
    return report.call_children(userid=1, model=Employee())


@app.get("/employee/{employee_id}")
def get_employee(employee_id: int):
    """Update view for employee 'employee_id'"""
    return report.call_children(employee_id, Employee())


@app.get("/team/{team_id}")
def get_team(team_id: int):
    """Update view for team 'team_id'"""
    return report.call_children(team_id, Team())


@app.get("/update_dropdown/{r}")
def update_dropdown(request: fh.Request):
    """Update dropdown to switch between employee and team"""
    dropdown = DashboardFilters().children[1]
    profile_type = request.query_params["profile_type"]
    if profile_type == "Team":
        return dropdown(None, Team())
    elif profile_type == "Employee":
        return dropdown(None, Employee())


@app.post("/update_data/")
async def update_data(request: fh.Request):
    """Update data (plots + table) for selected employee or team"""
    data: fh.FormData = await request.form()
    profile_type = data._dict["profile_type"]
    id = data._dict["user-selection"]
    if profile_type == "Employee":
        return fh.RedirectResponse(f"/employee/{id}", status_code=303)
    elif profile_type == "Team":
        return fh.RedirectResponse(f"/team/{id}", status_code=303)


fh.serve()
