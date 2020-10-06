import logging
from typing import List, Union

import plotly.graph_objs as go
import plotly.offline as ply

logger = logging.getLogger(__name__)


def create_plot_and_save_to_file(mode: str, data: List[Union[go.Mesh3d, go.Scatter3d]], layout: go.Layout):
    """

    :param mode:
    :param data:
    :param layout:
    :return:
    """
    plot_filename = f"{mode}.html"

    logger.debug(f"Creating plot and savint to file {plot_filename}")

    fig = go.Figure(data=data, layout=layout)
    ply.plot(fig, filename=plot_filename)
