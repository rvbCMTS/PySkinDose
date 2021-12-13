import logging
from typing import List

import plotly.graph_objects as go

from ..beam_class import Beam
from ..constants import (
    COLOR_BEAM,
    COLOR_DETECTOR,
    COLOR_PAD,
    COLOR_PATIENT,
    COLOR_SOURCE,
    COLOR_TABLE,
    MESH_NAME_PAD,
    MESH_OPACITY_BEAM,
    PLOT_ASPECTMODE_SETUP_AND_EVENT,
    PLOT_AXIS_TITLE_X,
    PLOT_AXIS_TITLE_Y,
    PLOT_AXIS_TITLE_Z,
    PLOT_DRAGMODE,
    PLOT_FONT_FAMILY,
    PLOT_FONT_SIZE,
    PLOT_HOVERLABEL_FONT_FAMILY,
    PLOT_HOVERLABEL_FONT_SIZE,
    PLOT_LIGHTNING_AMBIENT,
    PLOT_LIGHTNING_DIFFUSE,
    PLOT_SOURCE_SIZE,
    PLOT_TITLE_FONT_FAMILY,
    PLOT_TITLE_FONT_SIZE,
    PLOT_WIREFRAME_LINE_WIDTH,
    PLOT_ZERO_LINE_WIDTH,
)
from ..phantom_class import Phantom
from .create_mesh3d import create_mesh_3d_general
from .create_plot_and_save_to_file import create_plot_and_save_to_file
from .create_wireframes import create_wireframes
from .get_camera_view import get_camera_view
from .plot_settings import fetch_plot_colors, fetch_plot_margin, fetch_plot_size

logger = logging.getLogger(__name__)


def create_setup_and_event_plot(
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    beam: Beam,
    mode: str,
    patient_text: List[str],
    source_text: List[str],
    table_text: List[str],
    detectors_text: List[str],
    pad_text: List[str],
    beam_text: List[str],
    title: str,
    dark_mode=True,
    notebook_mode: bool = False,
):

    logger.debug("Creating meshes for plot")

    COLOR_CANVAS, COLOR_PLOT_TEXT, COLOR_GRID, COLOR_ZERO_LINE = fetch_plot_colors(dark_mode=dark_mode)

    PLOT_WIDTH, PLOT_HEIGHT = fetch_plot_size(notebook_mode=notebook_mode)

    PLOT_MARGIN = fetch_plot_margin(notebook_mode=notebook_mode)

    patient_mesh = create_mesh_3d_general(
        obj=patient,
        color=COLOR_PATIENT,
        mesh_text=patient_text,
        lighting=dict(diffuse=PLOT_LIGHTNING_DIFFUSE, ambient=PLOT_LIGHTNING_AMBIENT),
    )

    source_mesh = go.Scatter3d(
        x=[beam.r[0, 0], beam.r[0, 0]],
        y=[beam.r[0, 1], beam.r[0, 1]],
        z=[beam.r[0, 2], beam.r[0, 2]],
        hoverinfo="text",
        mode="markers",
        marker=dict(size=PLOT_SOURCE_SIZE, color=COLOR_SOURCE),
        text=source_text,
    )

    table_mesh = create_mesh_3d_general(obj=table, color=COLOR_TABLE, mesh_text=table_text)

    detector_mesh = create_mesh_3d_general(obj=beam, color=COLOR_DETECTOR, mesh_text=detectors_text, detector_mesh=True)

    pad_mesh = create_mesh_3d_general(obj=pad, color=COLOR_PAD, mesh_text=pad_text, mesh_name=MESH_NAME_PAD)

    beam_mesh = create_mesh_3d_general(obj=beam, color=COLOR_BEAM, opacity=MESH_OPACITY_BEAM, mesh_text=beam_text)

    logger.debug("Create wireframes")
    wf_beam, wf_table, wf_pad, wf_detector = create_wireframes(
        beam=beam,
        table=table,
        pad=pad,
        line_width=PLOT_WIREFRAME_LINE_WIDTH,
        visible=True,
    )

    logger.debug("Setting up plot layout settings")
    layout = go.Layout(
        height=PLOT_HEIGHT,
        width=PLOT_WIDTH,
        margin=PLOT_MARGIN,
        font=dict(family=PLOT_FONT_FAMILY, size=PLOT_FONT_SIZE, color=COLOR_PLOT_TEXT),
        title=dict(
            font=dict(
                family=PLOT_TITLE_FONT_FAMILY,
                size=PLOT_TITLE_FONT_SIZE,
                color=COLOR_PLOT_TEXT,
            ),
            text=title,
        ),
        hoverlabel=dict(
            font=dict(
                family=PLOT_HOVERLABEL_FONT_FAMILY,
                size=PLOT_HOVERLABEL_FONT_SIZE,
                color=COLOR_PLOT_TEXT,
            )
        ),
        paper_bgcolor=COLOR_CANVAS,
        showlegend=False,
        dragmode=PLOT_DRAGMODE,
        scene=dict(
            aspectmode=PLOT_ASPECTMODE_SETUP_AND_EVENT,
            camera=get_camera_view(),
            xaxis=dict(
                title=PLOT_AXIS_TITLE_X,
                backgroundcolor=COLOR_CANVAS,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
            yaxis=dict(
                title=PLOT_AXIS_TITLE_Y,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                backgroundcolor=COLOR_CANVAS,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
            zaxis=dict(
                title=PLOT_AXIS_TITLE_Z,
                gridcolor=COLOR_GRID,
                linecolor=COLOR_GRID,
                backgroundcolor=COLOR_CANVAS,
                zerolinecolor=COLOR_ZERO_LINE,
                zerolinewidth=PLOT_ZERO_LINE_WIDTH,
            ),
        ),
    )

    data = [
        patient_mesh,
        source_mesh,
        table_mesh,
        detector_mesh,
        pad_mesh,
        beam_mesh,
        wf_beam,
        wf_table,
        wf_pad,
        wf_detector,
    ]

    create_plot_and_save_to_file(mode=mode, data=data, layout=layout)
