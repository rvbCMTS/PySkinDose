import logging
from typing import Any, Dict, List, Optional

import pandas as pd
import plotly.graph_objs as go

from ..constants import (
    COLOR_CANVAS_DARK,
    COLOR_CANVAS_LIGHT,
    COLOR_PLOT_TEXT_LIGHT,
    COLOR_PLOT_TEXT_DARK,
    COLOR_ZERO_LINE_LIGHT,
    COLOR_ZERO_LINE_DARK,
    COLOR_BEAM,
    COLOR_DETECTOR,
    COLOR_PAD,
    COLOR_PATIENT,
    COLOR_SOURCE,
    COLOR_TABLE,
    COLOR_SLIDER_BACKGROUND,
    COLOR_SLIDER_BORDER_LIGHT,
    COLOR_SLIDER_BORDER_DARK,
    COLOR_SLIDER_TICK_LIGHT,
    COLOR_SLIDER_TICK_DARK,
    IRRADIATION_EVENT_STEP_KEY_ARGUMENTS,
    IRRADIATION_EVENT_STEP_KEY_LABEL,
    IRRADIATION_EVENT_STEP_KEY_METHOD,
    MODE_PLOT_PROCEDURE,
    PLOT_AXIS_TITLE_X,
    PLOT_AXIS_TITLE_Y,
    PLOT_AXIS_TITLE_Z,
    PLOT_FONT_FAMILY,
    PLOT_HOVER_LABEL_FONT_FAMILY,
    PLOT_SLIDER_BORDER_WIDTH,
    PLOT_SLIDER_FONT_SIZE_CURRENT,
    PLOT_SLIDER_FONT_SIZE_GENERAL,
    PLOT_SLIDER_PADDING,
    PLOT_SLIDER_TRANSITION,
    PLOT_TITLE_FONT_FAMILY,
    PLOT_TITLE_FONT_SIZE
)
from .create_irradiation_event_procedure_plot_data import create_irradiation_event_procedure_plot_data
from .create_plot_and_save_to_file import create_plot_and_save_to_file
from .get_camera_view import get_camera_view
from ..phantom_class import Phantom

logger = logging.getLogger(__name__)


def plot_procedure(mode: str, data_norm: pd.DataFrame, table: Phantom, pad: Phantom, include_patient: bool, patient: Optional[Phantom] = None, dark_mode: bool=True):
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
            pad=pad
        )
        for ind in range(len(data_norm))
    ]

    # data = [val for el in meshes for _, val in el.items()]
    data = [event.get(plot_object) 
            for plot_object in meshes[0].keys()
            for event in meshes]

    layout = _create_procedure_layout(title=title, total_events=len(data_norm), dark_mode=dark_mode)

    create_plot_and_save_to_file(mode=mode, data=data, layout=layout)


def _create_event_slider_step(total_events: int, event: int) -> Dict[str, Any]:
    step = {
        IRRADIATION_EVENT_STEP_KEY_METHOD: "restyle",
        IRRADIATION_EVENT_STEP_KEY_ARGUMENTS: ['visible', [False] * total_events],
        IRRADIATION_EVENT_STEP_KEY_LABEL: event + 1
    }
    step[IRRADIATION_EVENT_STEP_KEY_ARGUMENTS][1][event] = True

    return step


def _create_sliders(steps: List[Dict], total_events: int, dark_mode: bool=True) -> List[Dict[str, Any]]:

    if dark_mode:
        COLOR_PLOT_TEXT = COLOR_PLOT_TEXT_DARK
        COLOR_SLIDER_TICK = COLOR_SLIDER_TICK_DARK
        COLOR_SLIDER_BORDER = COLOR_SLIDER_BORDER_DARK

    if not dark_mode:
        COLOR_PLOT_TEXT = COLOR_PLOT_TEXT_LIGHT
        COLOR_SLIDER_TICK = COLOR_SLIDER_TICK_LIGHT
        COLOR_SLIDER_BORDER = COLOR_SLIDER_BORDER_LIGHT
    return [
        dict(
            active=0,
            transition=PLOT_SLIDER_TRANSITION,
            bordercolor=COLOR_SLIDER_BORDER,
            borderwidth=PLOT_SLIDER_BORDER_WIDTH,
            tickcolor=COLOR_SLIDER_TICK,
            bgcolor=COLOR_SLIDER_BACKGROUND,
            currentvalue=dict(prefix="Active event: ",
                              suffix=f" of {total_events}",
                              font=dict(color=COLOR_PLOT_TEXT, size=PLOT_SLIDER_FONT_SIZE_CURRENT)),
            font=dict(family=PLOT_FONT_FAMILY, color=COLOR_PLOT_TEXT, size=PLOT_SLIDER_FONT_SIZE_GENERAL),
            pad=PLOT_SLIDER_PADDING,
            steps=steps
        )
    ]


def _create_procedure_layout(title: str, total_events: int, dark_mode: bool=True) -> go.Layout:
    steps = [_create_event_slider_step(total_events=total_events, event=ind) for ind in range(total_events)]

    if dark_mode:
        COLOR_CANVAS = COLOR_CANVAS_DARK
        COLOR_PLOT_TEXT = COLOR_PLOT_TEXT_DARK
        COLOR_ZERO_LINE = COLOR_ZERO_LINE_DARK

    if not dark_mode:
        COLOR_CANVAS = COLOR_CANVAS_LIGHT
        COLOR_PLOT_TEXT = COLOR_PLOT_TEXT_LIGHT
        COLOR_ZERO_LINE = COLOR_ZERO_LINE_LIGHT
        

    return go.Layout(
        sliders=_create_sliders(steps=steps, total_events=total_events, dark_mode=dark_mode),
        font=dict(family=PLOT_FONT_FAMILY, size=14),
        hoverlabel=dict(font=dict(family=PLOT_HOVER_LABEL_FONT_FAMILY, size=PLOT_SLIDER_FONT_SIZE_GENERAL)),
        showlegend=False,
        dragmode="orbit",
        title=title,
        titlefont=dict(family=PLOT_TITLE_FONT_FAMILY, size=PLOT_TITLE_FONT_SIZE,
                       color=COLOR_PLOT_TEXT),
        plot_bgcolor=COLOR_CANVAS,
        paper_bgcolor=COLOR_CANVAS,
        scene=dict(aspectmode="cube",
                   camera=get_camera_view(),
                   xaxis=dict(title=PLOT_AXIS_TITLE_X,
                              range=[-150, 150],
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3),

                   yaxis=dict(title=PLOT_AXIS_TITLE_Y,
                              range=[-150, 150],
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3),

                   zaxis=dict(title=PLOT_AXIS_TITLE_Z,
                              range=[-150, 150],
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3)
                   )
    )




