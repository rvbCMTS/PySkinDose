from typing import List

import plotly.graph_objs as go

from ..beam_class import Beam
from ..constants import (
    COLOR_WIRE_FRAME_BEAM,
    COLOR_WIRE_FRAME_DETECTOR,
    COLOR_WIRE_FRAME_PAD,
    COLOR_WIRE_FRAME_TABLE,
)
from ..phantom_class import Phantom


def create_wireframes(beam: Beam, table: Phantom, pad: Phantom,
                      line_width: int = 4, visible: bool = True):
    """Create wireframe versions of the mesh3d objects in plot_geometry.

    The purpose of this function is to enhance the plot_geometry plot by
    adding wireframes.

    Parameters
    ----------
    beam: Beam
        X-ray beam, i.e. instance of class Beam. See beam_class for more info
    table: Phantom
        Table phantom from instance of class Phantom. phantom_type must be
        "table"
    pad: Phantom
        Table phantom from instance of class Phantom. phantom_type must be
        "pad"
    line_width : int, optional
        Line width of the wireframes. Default value is 4.
    visible : bool, optional
        Set the visibility of each of the wireframe traces

    """
    # The following section creates a wireframe plot for the X-ray beam
    wf_beam = _create_beam_wireframe(beam=beam, line_width=line_width, visible=visible)

    wf_table = _create_phantom_object_wireframe(obj=table, color=COLOR_WIRE_FRAME_TABLE, line_width=line_width,
                                                visible=visible)

    wf_pad = _create_phantom_object_wireframe(obj=pad, color=COLOR_WIRE_FRAME_PAD, line_width=line_width,
                                              visible=visible)

    wf_detector = _create_detector_wire_frame(beam=beam, line_width=line_width, visible=visible)

    return wf_beam, wf_table, wf_pad, wf_detector


def _create_beam_wireframe(beam: Beam, line_width: int, visible: bool) -> go.Scatter3d:
    temp_x = [beam.r[0, 0], beam.r[1, 0], beam.r[0, 0], beam.r[2, 0],
              beam.r[0, 0], beam.r[3, 0], beam.r[0, 0], beam.r[4, 0],
              beam.r[1, 0], beam.r[2, 0], beam.r[3, 0], beam.r[4, 0],
              beam.r[1, 0]]

    temp_y = [beam.r[0, 1], beam.r[1, 1], beam.r[0, 1], beam.r[2, 1],
              beam.r[0, 1], beam.r[3, 1], beam.r[0, 1], beam.r[4, 1],
              beam.r[1, 1], beam.r[2, 1], beam.r[3, 1], beam.r[4, 1],
              beam.r[1, 1]]

    temp_z = [beam.r[0, 2], beam.r[1, 2], beam.r[0, 2], beam.r[2, 2],
              beam.r[0, 2], beam.r[3, 2], beam.r[0, 2], beam.r[4, 2],
              beam.r[1, 2], beam.r[2, 2], beam.r[3, 2], beam.r[4, 2],
              beam.r[1, 2]]

    return _create_wireframe_scatter3d(x=temp_x, y=temp_y, z=temp_z,
                                       line_width=line_width, visible=visible,
                                       color=COLOR_WIRE_FRAME_BEAM)


def _create_phantom_object_wireframe(obj: Phantom, color: str, line_width: int, visible: bool) -> go.Scatter3d:
    # The following section creates a wireframe plot for the support table
    x1 = obj.r[0:8, 0].tolist() + [obj.r[0, 0]]
    y1 = obj.r[0:8, 1].tolist() + [obj.r[0, 1]]
    z1 = obj.r[0:8, 2].tolist() + [obj.r[0, 2]]

    x2 = obj.r[8:16, 0].tolist() + [obj.r[8, 0]]
    y2 = obj.r[8:16, 1].tolist() + [obj.r[8, 1]]
    z2 = obj.r[8:16, 2].tolist() + [obj.r[8, 2]]

    x3 = [obj.r[8, 0], obj.r[9, 0], obj.r[10, 0], obj.r[2, 0],
          obj.r[3, 0], obj.r[11, 0], obj.r[12, 0], obj.r[13, 0],
          obj.r[5, 0], obj.r[6, 0], obj.r[14, 0], obj.r[15, 0],
          obj.r[7, 0]]

    y3 = [obj.r[8, 1], obj.r[9, 1], obj.r[10, 1], obj.r[2, 1],
          obj.r[3, 1], obj.r[11, 1], obj.r[12, 1], obj.r[13, 1],
          obj.r[5, 1], obj.r[6, 1], obj.r[14, 1], obj.r[15, 1],
          obj.r[7, 1]]

    z3 = [obj.r[8, 2], obj.r[9, 2], obj.r[10, 2], obj.r[2, 2],
          obj.r[3, 2], obj.r[11, 2], obj.r[12, 2], obj.r[13, 2],
          obj.r[5, 2], obj.r[6, 2], obj.r[14, 2], obj.r[15, 2],
          obj.r[7, 2]]

    temp_x = x1 + x2 + x3
    temp_y = y1 + y2 + y3
    temp_z = z1 + z2 + z3

    return _create_wireframe_scatter3d(x=temp_x, y=temp_y, z=temp_z,
                                       line_width=line_width, visible=visible,
                                       color=color)


def _create_detector_wire_frame(beam: Beam, line_width: int, visible: bool) -> go.Scatter3d:
    x1 = beam.det_r[0:4, 0].tolist() + [beam.det_r[0, 0]]
    y1 = beam.det_r[0:4, 1].tolist() + [beam.det_r[0, 1]]
    z1 = beam.det_r[0:4, 2].tolist() + [beam.det_r[0, 2]]

    x2 = beam.det_r[4:8, 0].tolist() + [beam.det_r[4, 0]]
    y2 = beam.det_r[4:8, 1].tolist() + [beam.det_r[4, 1]]
    z2 = beam.det_r[4:8, 2].tolist() + [beam.det_r[4, 2]]

    x3 = [beam.det_r[4, 0], beam.det_r[5, 0], beam.det_r[1, 0],
          beam.det_r[2, 0], beam.det_r[6, 0], beam.det_r[7, 0],
          beam.det_r[3, 0]]

    y3 = [beam.det_r[4, 1], beam.det_r[5, 1], beam.det_r[1, 1],
          beam.det_r[2, 1], beam.det_r[6, 1], beam.det_r[7, 1],
          beam.det_r[3, 1]]

    z3 = [beam.det_r[4, 2], beam.det_r[5, 2], beam.det_r[1, 2],
          beam.det_r[2, 2], beam.det_r[6, 2], beam.det_r[7, 2],
          beam.det_r[3, 2]]

    temp_x = x1 + x2 + x3
    temp_y = y1 + y2 + y3
    temp_z = z1 + z2 + z3

    return _create_wireframe_scatter3d(x=temp_x, y=temp_y, z=temp_z,
                                       line_width=line_width, visible=visible,
                                       color=COLOR_WIRE_FRAME_DETECTOR)


def _create_wireframe_scatter3d(x: List[float], y: List[float], z: List[float],
                                line_width: int, visible: bool,
                                color: str) -> go.Scatter3d:
    return go.Scatter3d(x=x, y=y, z=z, mode="lines",
                        hoverinfo="skip", visible=visible,
                        line=dict(color=color, width=line_width))
