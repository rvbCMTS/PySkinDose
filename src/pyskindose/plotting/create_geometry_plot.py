import pandas as pd

from pyskindose import constants as const, position_geometry
from pyskindose.phantom_class import Phantom
from pyskindose.settings import PyskindoseSettings
from pyskindose.plotting.plot_geometry import plot_geometry

def create_geometry_plot(normalized_data: pd.DataFrame, table: Phantom, pad: Phantom,
                          settings: PyskindoseSettings) -> None:
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
    if settings.mode not in [const.MODE_PLOT_SETUP, const.MODE_PLOT_EVENT, const.MODE_PLOT_PROCEDURE]:
        return

    # override dense mathematical phantom in .html plotting
    if settings.phantom.model == const.PHANTOM_MODEL_PLANE:
        settings.phantom.dimension.plane_resolution = const.RESOLUTION_SPARSE
    elif settings.phantom.model == const.PHANTOM_MODEL_CYLINDER:
        settings.phantom.dimension.cylinder_resolution = const.RESOLUTION_SPARSE

    # override dense .stl phantoms in plot_procedure .html plotting
    if settings.mode == const.MODE_PLOT_PROCEDURE and settings.phantom.model == const.PHANTOM_MODEL_HUMAN:
        settings.phantom.human_mesh += const.PHANTOM_HUMAN_MESH_SPARSE_MODEL_ENDING

    patient = Phantom(
        phantom_model=settings.phantom.model,
        phantom_dim=settings.phantom.dimension,
        human_mesh=settings.phantom.human_mesh)

    # position objects in starting position
    position_geometry(
        patient=patient, table=table, pad=pad,
        pad_thickness=settings.phantom.dimension.pad_thickness,
        patient_offset=[
            settings.phantom.patient_offset.d_lat,
            settings.phantom.patient_offset.d_ver,
            settings.phantom.patient_offset.d_lon])

    plot_geometry(patient=patient, table=table, pad=pad, data_norm=normalized_data,
                  mode=settings.mode, event=settings.plot_event_index, 
                  include_patient=len(normalized_data) <= const.MAXIMUM_NUMBER_OF_EVENTS_FOR_INCLUDING_PHANTOM_IN_EVENT_PLOT)