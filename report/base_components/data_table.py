from typing import override

import pandas as pd
from employee_events import QueryBase
from fasthtml.common import Table, Td, Th, Tr

from .base_component import BaseComponent


class DataTable(BaseComponent):
    @override
    def build_component(self, entity_id: int, model: QueryBase):
        if model.name:
            data: pd.DataFrame = self.component_data(entity_id, model)

            table = Table(Tr(Th(column) for column in data.columns))

            for data_row in data.to_numpy():
                table_row = Tr(Td(val) for val in data_row)

                children = (*table.children, table_row)
                table.children = children

            return table
