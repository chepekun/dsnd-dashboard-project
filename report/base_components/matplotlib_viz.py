import base64
import io
from abc import ABC, abstractmethod
from typing import override

import matplotlib
import matplotlib.pylab as plt
from employee_events import QueryBase
from fasthtml.common import Img
from matplotlib.axes import Axes

from .base_component import BaseComponent

# This is necessary to prevent matplotlib from causing memory leaks
# https://stackoverflow.com/questions/31156578/matplotlib-doesnt-release-memory-after-savefig-and-close
matplotlib.use("Agg")
matplotlib.rcParams["savefig.transparent"] = True
matplotlib.rcParams["savefig.format"] = "png"


def matplotlib2fasthtml(func):
    """
    Copy of https://github.com/koaning/fh-matplotlib, which is currently hardcoding the
    image format as jpg. png or svg is needed here.
    """

    def wrapper(*args, **kwargs):
        # Reset the figure to prevent accumulation. Maybe we need a setting for this?
        fig = plt.figure()

        # Run function as normal
        func(*args, **kwargs)

        # Store it as base64 and put it into an image.
        my_string_io_bytes = io.BytesIO()
        plt.savefig(my_string_io_bytes)
        my_string_io_bytes.seek(0)
        my_base64_jpg_data = base64.b64encode(my_string_io_bytes.read()).decode()

        # Close the figure to prevent memory leaks
        plt.close(fig)
        plt.close("all")
        return Img(
            src=f"data:image/jpg;base64, {my_base64_jpg_data}", style="margin: 0 auto; width: auto; height: auto;"
        )

    return wrapper


class MatplotlibViz(BaseComponent, ABC):
    @override
    @matplotlib2fasthtml
    def build_component(self, entity_id: int, model: QueryBase):
        return self.visualization(entity_id, model)

    @abstractmethod
    def visualization(self, entity_id: int, model: QueryBase): ...

    def set_axis_styling(self, ax: Axes, bordercolor: str = "white", fontcolor: str = "white"):
        ax.title.set_color(fontcolor)
        ax.xaxis.label.set_color(fontcolor)
        ax.yaxis.label.set_color(fontcolor)

        ax.tick_params(color=bordercolor, labelcolor=fontcolor)
        for spine in ax.spines.values():
            spine.set_edgecolor(bordercolor)

        for line in ax.get_lines():
            line.set_linewidth(4)
            line.set_linestyle("dashdot")
