import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objects as go

from ..constants import (
    COLOR_SLIDER_BACKGROUND,
    IRRADIATION_EVENT_STEP_KEY_ARGUMENTS,
    IRRADIATION_EVENT_STEP_KEY_LABEL,
    IRRADIATION_EVENT_STEP_KEY_METHOD,
    MODE_PLOT_PROCEDURE,
    PLOT_ASPECTMODE_PLOT_PROCEDURE,
    PLOT_AXIS_TITLE_X,
    PLOT_AXIS_TITLE_Y,
    PLOT_AXIS_TITLE_Z,
    PLOT_DRAGMODE,
    PLOT_FONT_FAMILY,
    PLOT_FONT_SIZE,
    PLOT_HOVERLABEL_FONT_FAMILY,
    PLOT_PROCEDURE_AXIS_RANGE_X,
    PLOT_PROCEDURE_AXIS_RANGE_Y,
    PLOT_PROCEDURE_AXIS_RANGE_Z,
    PLOT_SLIDER_BORDER_WIDTH,
    PLOT_SLIDER_FONT_SIZE_CURRENT,
    PLOT_SLIDER_FONT_SIZE_GENERAL,
    PLOT_SLIDER_TRANSITION,
    PLOT_TITLE_FONT_FAMILY,
    PLOT_TITLE_FONT_SIZE,
    PLOT_ZERO_LINE_WIDTH,
)
from ..phantom_class import Phantom
from .create_irradiation_event_procedure_plot_data import (
    create_irradiation_event_procedure_plot_data,
)
from .create_plot_and_save_to_file import create_plot_and_save_to_file
from .get_camera_view import get_camera_view
from .plot_settings import (
    fetch_plot_colors,
    fetch_plot_margin,
    fetch_plot_size,
    fetch_slider_colors,
    fetch_slider_padding,
)

logger = logging.getLogger(__name__)


def plot_procedure(
    mode: str,
    data_norm: pd.DataFrame,
    table: Phantom,
    pad: Phantom,
    include_patient: bool,
    patient: Optional[Phantom] = None,
    dark_mode: bool = True,
    notebook_mode: bool = False,
):
    """Create plot_procedure plot.

    Parameters
    ----------
    mode : str
        The function will only run if this is set to "plot_procedure".
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    table : Phantom
        Patient support table phantom
    pad : Phantom
        Patient support pad phantom
    include_patient : bool
        Choose if the patient phantom should be included
    patient : Optional[Phantom], optional
        patient phantom, by default None
    dark_mode : bool, optional
        set dark mode for plots, by default True
    notebook_mode : bool, optional
        optimize plot size for notebooks, default is True.

    Raises
    ------
    IOError
        Raises error if patient not provided when include_patient = True

    """
    if mode != MODE_PLOT_PROCEDURE:
        return

    if include_patient and patient is None:
        logger.error("Plot procedure called with include patient but no patient input")
        raise IOError("Patient object must be given when include_patient set to True")

    logger.info(f"Plotting entire procedure with {len(data_norm)} irradiation events")

    title = f"<b>P</b>y<b>S</b>kin<b>D</b>ose [mode: {mode}]"

    meshes = [
        create_irradiation_event_procedure_plot_data(
            data_norm=data_norm,
            include_patient=include_patient,
            visible_status=(ind == 0),
            event=ind,
            patient=(patient if include_patient else None),
            table=table,
            pad=pad,
        )
        for ind in range(len(data_norm))
    ]

    data = [event.get(plot_object) for plot_object in meshes[0].keys() for event in meshes]

    layout = _create_procedure_layout(
        title=title,
        total_events=len(data_norm),
        dark_mode=dark_mode,
        notebook_mode=notebook_mode,
    )

    create_plot_and_save_to_file(mode=mode, data=data, layout=layout)


def _create_event_slider_step(total_events: int, event: int) -> Dict[str, Any]:

    step = {
        IRRADIATION_EVENT_STEP_KEY_METHOD: "restyle",
        IRRADIATION_EVENT_STEP_KEY_ARGUMENTS: ["visible", [False] * total_events],
        IRRADIATION_EVENT_STEP_KEY_LABEL: event + 1,
    }
    step[IRRADIATION_EVENT_STEP_KEY_ARGUMENTS][1][event] = True

    return step


def _create_sliders(
    steps: List[Dict],
    total_events: int,
    dark_mode: bool = True,
    notebook_mode: bool = False,
) -> List[Dict[str, Any]]:

    COLOR_PLOT_TEXT, COLOR_SLIDER_TICK, COLOR_SLIDER_BORDER = fetch_slider_colors(dark_mode=dark_mode)

    PLOT_SLIDER_PADDING = fetch_slider_padding(notebook_mode=notebook_mode)

    return [
        dict(
            active=0,
            transition=PLOT_SLIDER_TRANSITION,
            bordercolor=COLOR_SLIDER_BORDER,
            borderwidth=PLOT_SLIDER_BORDER_WIDTH,
            tickcolor=COLOR_SLIDER_TICK,
            bgcolor=COLOR_SLIDER_BACKGROUND,
            currentvalue=dict(
                prefix="Active event: ",
                suffix=f" of {total_events}",
                font=dict(color=COLOR_PLOT_TEXT, size=PLOT_SLIDER_FONT_SIZE_CURRENT),
            ),
            font=dict(
                family=PLOT_FONT_FAMILY,
                color=COLOR_PLOT_TEXT,
                size=PLOT_SLIDER_FONT_SIZE_GENERAL,
            ),
            pad=PLOT_SLIDER_PADDING,
            steps=steps,
        )
    ]


def _create_procedure_layout(
    title: str, total_events: int, dark_mode: bool = True, notebook_mode: bool = False
) -> go.Layout:

    steps = [_create_event_slider_step(total_events=total_events, event=ind) for ind in range(total_events)]

    COLOR_CANVAS, COLOR_PLOT_TEXT, COLOR_GRID, COLOR_ZERO_LINE = fetch_plot_colors(dark_mode=dark_mode)

    PLOT_HEIGHT, PLOT_WIDTH = fetch_plot_size(notebook_mode=notebook_mode)

    PLOT_MARGIN = fetch_plot_margin(notebook_mode=notebook_mode)

    layout = go.Layout(
        height=PLOT_HEIGHT,
        width=PLOT_WIDTH,
        margin=PLOT_MARGIN,
        sliders=_create_sliders(
            steps=steps,
            total_events=total_events,
            dark_mode=dark_mode,
            notebook_mode=notebook_mode,
        ),
        font=dict(family=PLOT_FONT_FAMILY, size=PLOT_FONT_SIZE, color=COLOR_PLOT_TEXT),
        hoverlabel=dict(font=dict(family=PLOT_HOVERLABEL_FONT_FAMILY, size=PLOT_SLIDER_FONT_SIZE_GENERAL)),
        showlegend=False,
        dragmode=PLOT_DRAGMODE,
        title=title,
        titlefont=dict(
            family=PLOT_TITLE_FONT_FAMILY,
            size=PLOT_TITLE_FONT_SIZE,
            color=COLOR_PLOT_TEXT,
        ),
        paper_bgcolor=COLOR_CANVAS,
        scene=dict(
            aspectmode=PLOT_ASPECTMODE_PLOT_PROCEDURE,
            camera=get_camera_view(),
            xaxis=dict(
                title=PLOT_AXIS_TITLE_X,
                range=PLOT_PROCEDURE_AXIS_RANGE_X,
                color=COLOR_PLOT_TEXT,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                backgroundcolor=COLOR_CANVAS,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
            yaxis=dict(
                title=PLOT_AXIS_TITLE_Y,
                range=PLOT_PROCEDURE_AXIS_RANGE_Y,
                color=COLOR_PLOT_TEXT,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                backgroundcolor=COLOR_CANVAS,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
            zaxis=dict(
                title=PLOT_AXIS_TITLE_Z,
                range=PLOT_PROCEDURE_AXIS_RANGE_Z,
                color=COLOR_PLOT_TEXT,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                backgroundcolor=COLOR_CANVAS,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
        ),
    )

    return layout
