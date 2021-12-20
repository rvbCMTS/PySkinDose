from typing import Dict, List, Optional, Union

import plotly.graph_objects as go

from ..beam_class import Beam
from ..phantom_class import Phantom
from .get_visual_offset import _get_visual_offset


def create_mesh_3d_general(
    obj: Union[Phantom, Beam],
    color: str,
    mesh_text: List[str],
    opacity: Optional[float] = None,
    mesh_name: Optional[str] = None,
    lighting: Optional[Dict] = None,
    detector_mesh: bool = False,
    visible_status: Optional[bool] = True,
) -> go.Mesh3d:

    if opacity is None:
        opacity = 1.0

    visual_offset = _get_visual_offset(patient=obj)

    mesh_x = obj.r[:, 0]
    mesh_y = obj.r[:, 1] + visual_offset
    mesh_z = obj.r[:, 2]
    mesh_i = obj.ijk[:, 0]
    mesh_j = obj.ijk[:, 1]
    mesh_k = obj.ijk[:, 2]

    if detector_mesh:
        mesh_x = obj.det_r[:, 0]
        mesh_y = obj.det_r[:, 1] + visual_offset
        mesh_z = obj.det_r[:, 2]
        mesh_i = obj.det_ijk[:, 0]
        mesh_j = obj.det_ijk[:, 1]
        mesh_k = obj.det_ijk[:, 2]

    if lighting is None and mesh_name is None:
        return go.Mesh3d(
            x=mesh_x,
            y=mesh_y,
            z=mesh_z,
            i=mesh_i,
            j=mesh_j,
            k=mesh_k,
            color=color,
            hoverinfo="text",
            text=mesh_text,
            opacity=opacity,
            visible=visible_status,
        )

    if mesh_name is None:
        return go.Mesh3d(
            x=mesh_x,
            y=mesh_y,
            z=mesh_z,
            i=mesh_i,
            j=mesh_j,
            k=mesh_k,
            color=color,
            hoverinfo="text",
            text=mesh_text,
            opacity=opacity,
            lighting=lighting,
            visible=visible_status,
        )

    if lighting is None:
        return go.Mesh3d(
            x=mesh_x,
            y=mesh_y,
            z=mesh_z,
            i=mesh_i,
            j=mesh_j,
            k=mesh_k,
            color=color,
            hoverinfo="text",
            text=mesh_text,
            name=mesh_name,
            opacity=opacity,
            visible=visible_status,
        )

    return go.Mesh3d(
        x=mesh_x,
        y=mesh_y,
        z=mesh_z,
        i=mesh_i,
        j=mesh_j,
        k=mesh_k,
        color=color,
        hoverinfo="text",
        text=mesh_text,
        name=mesh_name,
        lighting=lighting,
        opacity=opacity,
        visible=visible_status,
    )
