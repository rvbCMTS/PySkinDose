import logging
from typing import List

import plotly.graph_objs as go
import plotly.offline as ply

from ..beam_class import Beam
from ..constants import (
    COLOR_AZURE_DARK,
    COLOR_BEAM,
    COLOR_DETECTOR,
    COLOR_PAD,
    COLOR_PATIENT,
    COLOR_PLOT_TEXT,
    COLOR_SOURCE,
    COLOR_TABLE,
    COLOR_ZERO_LINE,
    MESH_NAME_PAD,
    MESH_OPACITY_BEAM,
    PLOT_AXIS_TITLE_X,
    PLOT_AXIS_TITLE_Y,
    PLOT_AXIS_TITLE_Z,
    PLOT_FONT_FAMILY,
    PLOT_HOVER_LABEL_FONT_FAMILY
)
from .create_mesh3d import create_mesh_3d_general
from .create_plot_and_save_to_file import create_plot_and_save_to_file
from .create_wireframes import create_wireframes
from .get_camera_view import get_camera_view
from ..phantom_class import Phantom

logger = logging.getLogger(__name__)


def create_setup_and_event_plot(patient: Phantom, table: Phantom, pad: Phantom, beam: Beam, mode: str,
                                patient_text: List[str], source_text: List[str], table_text: List[str],
                                detectors_text: List[str], pad_text: List[str], beam_text: List[str],
                                title: str):
    logger.debug("Creating meshes for plot")
    patient_mesh = create_mesh_3d_general(obj=patient, color=COLOR_PATIENT,
                                          mesh_text=patient_text, lighting=dict(diffuse=0.5, ambient=0.5))

    source_mesh = go.Scatter3d(
        x=[beam.r[0, 0], beam.r[0, 0]],
        y=[beam.r[0, 1], beam.r[0, 1]],
        z=[beam.r[0, 2], beam.r[0, 2]],
        hoverinfo="text",
        mode="markers",
        marker=dict(size=8, color=COLOR_SOURCE),
        text=source_text)

    table_mesh = create_mesh_3d_general(obj=table, color=COLOR_TABLE,
                                        mesh_text=table_text)

    detector_mesh = create_mesh_3d_general(obj=beam, color=COLOR_DETECTOR,
                                           mesh_text=detectors_text, detector_mesh=True)

    pad_mesh = create_mesh_3d_general(obj=pad, color=COLOR_PAD,
                                      mesh_text=pad_text, mesh_name=MESH_NAME_PAD)

    beam_mesh = create_mesh_3d_general(obj=beam, color=COLOR_BEAM, opacity=MESH_OPACITY_BEAM,
                                       mesh_text=beam_text)

    logger.debug("Create wireframes")
    wf_beam, wf_table, wf_pad, wf_detector = create_wireframes(
        beam=beam, table=table, pad=pad, line_width=4, visible=True)

    logger.debug("Setting up plot layout settings")
    layout = go.Layout(
        font=dict(family=PLOT_FONT_FAMILY, size=14),
        showlegend=False,
        hoverlabel=dict(font=dict(size=16, family=PLOT_HOVER_LABEL_FONT_FAMILY)),
        dragmode="orbit",
        title=title,
        titlefont=dict(family=PLOT_FONT_FAMILY, size=35,
                       color=COLOR_PLOT_TEXT),
        plot_bgcolor=COLOR_AZURE_DARK,
        paper_bgcolor=COLOR_AZURE_DARK,

        scene=dict(aspectmode="data", camera=get_camera_view(),

                   xaxis=dict(title=PLOT_AXIS_TITLE_X,
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3),

                   yaxis=dict(title=PLOT_AXIS_TITLE_Y,
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3),

                   zaxis=dict(title=PLOT_AXIS_TITLE_Z,
                              color=COLOR_PLOT_TEXT,
                              zerolinecolor=COLOR_ZERO_LINE, zerolinewidth=3)))

    data = [patient_mesh, source_mesh, table_mesh, detector_mesh, pad_mesh,
            beam_mesh, wf_beam, wf_table, wf_pad, wf_detector]

    create_plot_and_save_to_file(mode=mode, data=data, layout=layout)
