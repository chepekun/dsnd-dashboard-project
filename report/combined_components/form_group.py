from abc import ABC
from typing import override

from employee_events import QueryBase
from fasthtml.common import Button, Form, Group

from .combined_component import CombinedComponent


class FormGroup(CombinedComponent, ABC):
    id = ""
    action = ""
    method = ""
    button_label = "Submit"

    @override
    def call_children(self, userid: int, model: QueryBase):
        children = super().call_children(userid, model)
        children.append(Button(self.button_label, type="submit"))

        return children

    @override
    def div_args(self, userid: int, model: QueryBase):
        return {
            "id": self.id,
            "action": self.action,
            "method": self.method,
        }

    @override
    def outer_div(self, children, div_args):
        return Form(Group(*children), **div_args)
