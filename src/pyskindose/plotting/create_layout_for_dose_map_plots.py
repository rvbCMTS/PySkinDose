import logging

import plotly.graph_objects as go

from ..constants import (
    PLOT_ASPECTMODE_PLOT_DOSEMAP,
    PLOT_FONT_FAMILY,
    PLOT_FONT_SIZE,
    PLOT_HOVERLABEL_FONT_FAMILY,
    PLOT_HOVERLABEL_FONT_SIZE,
)

logger = logging.getLogger(__name__)


def create_layout_for_dose_map_plots(
    PLOT_MARGINS,
    PLOT_HEIGHT,
    PLOT_WIDTH,
    COLOR_PLOT_TEXT,
    COLOR_CANVAS,
):

    layout = go.Layout(
        height=PLOT_HEIGHT,
        width=PLOT_WIDTH,
        margin=PLOT_MARGINS,
        font=dict(family=PLOT_FONT_FAMILY, color=COLOR_PLOT_TEXT, size=PLOT_FONT_SIZE),
        hoverlabel=dict(font=dict(family=PLOT_HOVERLABEL_FONT_FAMILY, size=PLOT_HOVERLABEL_FONT_SIZE)),
        titlefont=dict(family=PLOT_FONT_FAMILY, size=PLOT_FONT_SIZE, color=COLOR_PLOT_TEXT),
        paper_bgcolor=COLOR_CANVAS,
        scene=dict(
            aspectmode=PLOT_ASPECTMODE_PLOT_DOSEMAP,
            xaxis=dict(
                title="",
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            yaxis=dict(
                title="",
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
            zaxis=dict(
                title="",
                backgroundcolor=COLOR_CANVAS,
                showgrid=False,
                zeroline=False,
                showticklabels=False,
            ),
        ),
    )

    return layout
