import pandas as pd

from pyskindose.phantom_class import Phantom

from .plot_event import plot_event
from .plot_procedure import plot_procedure
from .plot_setup import plot_setup


def plot_geometry(
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    data_norm: pd.DataFrame,
    mode: str,
    event: int = 0,
    dark_mode: bool = True,
    notebook_mode: bool = False,
    include_patient: bool = False,
) -> None:
    """Visualize the geometry from the irradiation events.

    This function plots the phantom, table, pad, beam and detector. The type of plot is
    specified in the parameter mode.

    Parameters
    ----------
    patient : Phantom
        Patient phantom from instance of class Phantom. Can be of phantom_model "plane",
        "cylinder" or "human"
    table : Phantom
        Table phantom from instance of class Phantom. phantom_model must be "table"
    pad : Phantom
        Pad phantom from instance of class Phantom. phantom_model must be "pad"
    data_norm : pd.DataFrame
        Table containing dicom RDSR information from each irradiation event. See
        rdsr_normalizer.py for more information.
    mode : str
        Choose between "plot_setup", "plot_event" and "plot_procedure".

         "plot_setup" plots the patient, table and pad in reference position together
         with the X-ray system with zero angulation. This is a debugging feature

        "plot_event" plots a specific irradiation event, in which the patient, table,
        pad, and beam are positioned according to the irradiation event specified by the
        parameter event

        "plot_procedure" plots out the X-ray system, table and pad for all irradiation
        events in the procedure The visible event are chosen by a event slider

    event : int, optional
        choose specific irradiation event if mode "plot_event" are used. Default is 0,
        in which the first irradiation event is considered.

    dark_mode : bool, optional
        set dark mode for plots

    notebook_mode : bool, optional
        optimize plot size for notebooks, default is True.

    include_patient : bool, optional
        Choose if the patient phantom should be included in the plot_procedure function.
        WARNING, very heavy on memory. Default is False.

    """
    plot_setup(
        mode=mode,
        data_norm=data_norm,
        patient=patient,
        table=table,
        pad=pad,
        dark_mode=dark_mode,
        notebook_mode=notebook_mode,
    )

    plot_event(
        mode=mode,
        data_norm=data_norm,
        event=event,
        patient=patient,
        table=table,
        pad=pad,
        dark_mode=dark_mode,
        notebook_mode=notebook_mode,
    )

    plot_procedure(
        mode=mode,
        data_norm=data_norm,
        include_patient=include_patient,
        patient=patient,
        table=table,
        pad=pad,
        dark_mode=dark_mode,
        notebook_mode=notebook_mode,
    )
