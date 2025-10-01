from typing import override

from employee_events import QueryBase
from fasthtml.common import Div, Label, Option, Select

from .base_component import BaseComponent


class Dropdown(BaseComponent):
    def __init__(self, id: str = "selector", name: str = "entity-selection", label: str = ""):
        self.id = id
        self.name = name
        self.label = label

    @override
    def build_component(self, entity_id: int, model: QueryBase):
        options = []
        for _, (text, value) in self.component_data(entity_id, model).iterrows():
            option = Option(text, value=value, selected="selected" if value == entity_id else "")
            options.append(option)

        return Select(*options, name=self.name)

    @override
    def outer_div(self, component):
        return Div(
            Label(self.label, _for=self.id),
            component,
            id=self.id,
        )
