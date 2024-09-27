from typing import List

import plotly.graph_objects as go

from ..beam_class import Beam
from ..constants import (
    COLOR_WIRE_FRAME_BEAM,
    COLOR_WIRE_FRAME_DETECTOR,
    COLOR_WIRE_FRAME_PAD,
    COLOR_WIRE_FRAME_TABLE,
    PLOT_TRACE_ORDER_BEAM_WIREFRAME,
    PLOT_TRACE_ORDER_DETECTOR_WIREFRAME,
    PLOT_TRACE_ORDER_PHANTOM_WIREFRAME,
)
from ..phantom_class import Phantom


def create_wireframes(beam: Beam, table: Phantom, pad: Phantom, line_width: int = 4, visible: bool = True):
    """Create wireframe versions of the mesh3d objects in plot_geometry.

    The purpose of this function is to enhance the plot_geometry plot by adding
    wireframes.

    Parameters
    ----------
    beam: Beam
        X-ray beam, i.e. instance of class Beam. See beam_class for more info
    table: Phantom
        Table phantom from instance of class Phantom. phantom_type must be "table"
    pad: Phantom
        Table phantom from instance of class Phantom. phantom_type must be "pad"
    line_width : int, optional
        Line width of the wireframes. Default value is 4.
    visible : bool, optional
        Set the visibility of each of the wireframe traces

    """
    wf_beam = _create_beam_wireframe(beam=beam, line_width=line_width, visible=visible)

    wf_table = _create_phantom_object_wireframe(
        obj=table, color=COLOR_WIRE_FRAME_TABLE, line_width=line_width, visible=visible
    )

    wf_pad = _create_phantom_object_wireframe(
        obj=pad, color=COLOR_WIRE_FRAME_PAD, line_width=line_width, visible=visible
    )

    wf_detector = _create_detector_wire_frame(beam=beam, line_width=line_width, visible=visible)

    return wf_beam, wf_table, wf_pad, wf_detector


def _create_beam_wireframe(beam: Beam, line_width: int, visible: bool) -> go.Scatter3d:
    # This funciton creates a wireframe plot for the X-ray beam

    x = beam.r[:, 0].tolist()
    y = beam.r[:, 1].tolist()
    z = beam.r[:, 2].tolist()

    temp_x = []
    temp_y = []
    temp_z = []

    # connect trace by using a plot trace order (trace out path of wireframe by index of each point)
    for trace in PLOT_TRACE_ORDER_BEAM_WIREFRAME:
        temp_x.append(x[trace])
        temp_y.append(y[trace])
        temp_z.append(z[trace])

    return _create_wireframe_scatter3d(
        x=temp_x,
        y=temp_y,
        z=temp_z,
        line_width=line_width,
        visible=visible,
        color=COLOR_WIRE_FRAME_BEAM,
    )


def _create_phantom_object_wireframe(obj: Phantom, color: str, line_width: int, visible: bool) -> go.Scatter3d:
    # This function creates a wireframe plot for the X-ray table or pad

    x = obj.r[:, 0].tolist()
    y = obj.r[:, 1].tolist()
    z = obj.r[:, 2].tolist()

    temp_x = []
    temp_y = []
    temp_z = []

    # connect trace by using a plot trace order (trace out path of wireframe by index of each point)
    for trace in PLOT_TRACE_ORDER_PHANTOM_WIREFRAME:
        temp_x.append(x[trace])
        temp_y.append(y[trace])
        temp_z.append(z[trace])

    return _create_wireframe_scatter3d(
        x=temp_x,
        y=temp_y,
        z=temp_z,
        line_width=line_width,
        visible=visible,
        color=color,
    )


def _create_detector_wire_frame(beam: Beam, line_width: int, visible: bool) -> go.Scatter3d:
    # This funciton creates a wireframe plot for the X-ray detector

    x = beam.det_r[:, 0].tolist()
    y = beam.det_r[:, 1].tolist()
    z = beam.det_r[:, 2].tolist()

    temp_x = []
    temp_y = []
    temp_z = []

    # connect trace by using a plot trace order (trace out path of wireframe by index of each point)
    for trace in PLOT_TRACE_ORDER_DETECTOR_WIREFRAME:
        temp_x.append(x[trace])
        temp_y.append(y[trace])
        temp_z.append(z[trace])

    return _create_wireframe_scatter3d(
        x=temp_x,
        y=temp_y,
        z=temp_z,
        line_width=line_width,
        visible=visible,
        color=COLOR_WIRE_FRAME_DETECTOR,
    )


def _create_wireframe_scatter3d(
    x: List[float],
    y: List[float],
    z: List[float],
    line_width: int,
    visible: bool,
    color: str,
) -> go.Scatter3d:
    return go.Scatter3d(
        x=x,
        y=y,
        z=z,
        mode="lines",
        hoverinfo="skip",
        visible=visible,
        line=dict(color=color, width=line_width),
    )
