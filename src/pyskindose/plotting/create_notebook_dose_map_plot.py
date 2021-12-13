import logging

import plotly.graph_objects as go
from PIL import Image

from ..constants import (
    PLOT_BASE_SIZE_STATIC,
    PLOT_GROUND_SHIFT_X_STATIC,
    PLOT_SHIFT_X_STATIC,
)

logger = logging.getLogger(__name__)


def create_notebook_dose_map_plot(names, file_type_static):

    fig = go.Figure()

    # Constants
    ground_shift_x = PLOT_GROUND_SHIFT_X_STATIC
    shift_x = PLOT_SHIFT_X_STATIC
    base_size_static = PLOT_BASE_SIZE_STATIC

    img_width = base_size_static + ground_shift_x / 4
    img_height = base_size_static + ground_shift_x / 4
    nrows = 1
    ncols = 4

    total_width = ncols * img_width - ground_shift_x
    total_height = nrows * img_height

    fig.add_trace(go.Scatter(x=[0, total_width], y=[0, img_height], mode="lines", visible=False))

    placements = [0, 1, 2, 3]
    placements = [img_width * place for place in placements]
    placements = [place - ground_shift_x for place in placements]
    placements = [placements[i] - shift_x[i] for i in range(len(shift_x))]

    images = [name + file_type_static for name in names]

    for i in range(len(placements)):

        source = Image.open(images[i])

        # Add image
        fig.add_layout_image(
            dict(
                x=placements[i],
                sizex=img_width,
                y=1 * img_height,
                sizey=img_height,
                xref="x",
                yref="y",
                opacity=1,
                layer="above",
                sizing="stretch",
                source=source,
            )
        )

    axes_visability = False

    # Configure axes
    fig.update_xaxes(
        visible=axes_visability,
        range=[0, total_width],
    )

    fig.update_yaxes(visible=axes_visability, range=[0, total_height], scaleanchor="x")

    fig.update_layout(
        width=total_width,
        height=total_height,
        margin={"l": 0, "r": 0, "t": 0, "b": 0},
    )

    fig.show(config={"doubleClick": "reset"})

    return
