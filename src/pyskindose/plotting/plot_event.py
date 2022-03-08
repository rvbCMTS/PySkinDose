import logging

import pandas as pd

from ..beam_class import Beam
from ..constants import MODE_PLOT_EVENT
from ..phantom_class import Phantom
from .create_geometry_plot_texts import create_geometry_plot_texts
from .create_setup_and_event_plot import create_setup_and_event_plot

logger = logging.getLogger(__name__)


def plot_event(
    mode: str,
    data_norm: pd.DataFrame,
    event: int,
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    dark_mode: bool = True,
    notebook_mode: bool = False,
):
    """Visualize the geometry from a specific irradiation event.

    This function plots an irradiation event with the patient, table, pad, and beam
    positioned according to the irradiation event specified by the parameter event

    Parameters
    ----------
    mode : str
        The function will only run if this is set to "plot_event".
    data_norm : pd.DataFrame
        Table containing dicom RDSR information from each irradiation event. See
        rdsr_normalizer.py for more information.
    event : int, optional
        choose specific irradiation event if mode "plot_event" are used. Default is 0,
        in which the first irradiation event is considered.
    patient : Phantom
        Patient phantom from instance of class Phantom. Can be of phantom_model "plane",
        "cylinder" or "human"
    table : Phantom
        Table phantom from instance of class Phantom. phantom_model must be "table"
    pad : Phantom
        Pad phantom from instance of class Phantom. phantom_model must be "pad"
    dark_mode : bool, optional
        Set dark mode for plot, default is True
    notebook_mode : bool, optional
        optimize plot size for notebooks, default is False.

    """
    if mode != MODE_PLOT_EVENT:
        return

    logger.info(f"Plotting event {event + 1} of {len(data_norm)}")

    # Create beam
    beam = Beam(data_norm, event=event, plot_setup=False)

    # Position geometry
    patient.position(data_norm, event)
    table.position(data_norm, event)
    pad.position(data_norm, event)

    (
        source_text,
        beam_text,
        detectors_text,
        table_text,
        pad_text,
        patient_text,
    ) = create_geometry_plot_texts(beam=beam, table=table, pad=pad, patient=patient)

    # Define plot title
    title = f"<b>P</b>y<b>S</b>kin<b>D</b>ose [mode: {mode}]"

    create_setup_and_event_plot(
        mode=mode,
        title=title,
        patient=patient,
        patient_text=patient_text,
        table=table,
        table_text=table_text,
        pad=pad,
        pad_text=pad_text,
        beam=beam,
        beam_text=beam_text,
        source_text=source_text,
        detectors_text=detectors_text,
        dark_mode=dark_mode,
    )
