from abc import ABC, abstractmethod
from typing import Any, List

import pandas as pd
from employee_events import QueryBase


class BaseComponent(ABC):
    @abstractmethod
    def build_component(self, entity_id: int, model: QueryBase) -> None | Any | List[Any]: ...

    def component_data(self, entity_id: int, model: QueryBase) -> pd.DataFrame:
        return pd.DataFrame()

    def outer_div(self, component):
        return component

    def __call__(self, entity_id: int, model: QueryBase):
        component = self.build_component(entity_id, model)

        return self.outer_div(component)
