import pandas as pd

from pyskindose import constants as c
from pyskindose import position_patient_phantom_on_table
from pyskindose.phantom_class import Phantom
from pyskindose.plotting.plot_geometry import plot_geometry
from pyskindose.settings_pyskindose import PyskindoseSettings


def create_geometry_plot(
    normalized_data: pd.DataFrame,
    table: Phantom,
    pad: Phantom,
    settings: PyskindoseSettings,
) -> None:
    """Create any of the geometry plots available in PySkinDose.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose
    table : Phantom
        Patient support table phantom
    pad : Phantom
        Patient support pad phantom
    settings : PyskindoseSettings
        Settings class for PySkinDose

    """
    if settings.mode not in [
        c.MODE_PLOT_SETUP,
        c.MODE_PLOT_EVENT,
        c.MODE_PLOT_PROCEDURE,
    ]:
        return

    # override dense mathematical phantom in .html plotting
    if settings.phantom.model == c.PHANTOM_MODEL_PLANE:
        settings.phantom.dimension.plane_resolution = c.RESOLUTION_SPARSE
    elif settings.phantom.model == c.PHANTOM_MODEL_CYLINDER:
        settings.phantom.dimension.cylinder_resolution = c.RESOLUTION_SPARSE

    # override dense .stl phantoms in plot_procedure .html plotting
    if settings.mode == c.MODE_PLOT_PROCEDURE and settings.phantom.model == c.PHANTOM_MODEL_HUMAN:
        settings.phantom.human_mesh += c.PHANTOM_HUMAN_MESH_SPARSE_MODEL_ENDING

    patient = Phantom(
        phantom_model=settings.phantom.model,
        phantom_dim=settings.phantom.dimension,
        human_mesh=settings.phantom.human_mesh,
    )

    # position objects in starting position
    position_patient_phantom_on_table(
        patient=patient,
        table=table,
        pad=pad,
        pad_thickness=settings.phantom.dimension.pad_thickness,
        patient_offset=[
            settings.phantom.patient_offset.d_lon,
            settings.phantom.patient_offset.d_ver,
            settings.phantom.patient_offset.d_lat,
        ],
        patient_orientation=settings.phantom.patient_orientation,
    )

    plot_geometry(
        patient=patient,
        table=table,
        pad=pad,
        data_norm=normalized_data,
        mode=settings.mode,
        event=settings.plot.plot_event_index,
        dark_mode=settings.plot.dark_mode,
        notebook_mode=settings.plot.notebook_mode,
        include_patient=len(normalized_data) <= settings.plot.max_events_for_patient_inclusion,
    )
