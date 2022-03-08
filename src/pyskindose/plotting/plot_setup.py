import logging

import pandas as pd

from ..beam_class import Beam
from ..constants import MODE_PLOT_SETUP
from ..phantom_class import Phantom
from .create_geometry_plot_texts import create_geometry_plot_texts
from .create_setup_and_event_plot import create_setup_and_event_plot

logger = logging.getLogger(__name__)


def plot_setup(
    mode: str,
    data_norm: pd.DataFrame,
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    dark_mode: bool = True,
    notebook_mode: bool = False,
):
    """Debugging feature for visualizing the geometry setup.

    This function plots the patient, table and pad in reference position together with
    the X-ray system with zero angulation.

    Parameters
    ----------
    mode : str
        The function will only run if this is set to "plot_setup".
    data_norm : pd.DataFrame
        Table containing dicom RDSR information from each irradiation event. See
        rdsr_normalizer.py for more information.
    patient : Phantom
        Patient phantom from instance of class Phantom. Can be of phantom_model "plane",
        "cylinder" or "human"
    table : Phantom
        Table phantom from instance of class Phantom. phantom_model must be "table"
    pad : Phantom
        Pad phantom from instance of class Phantom. phantom_model must be "pad"
    dark_mode : bool, optional
        set dark mode for plot
    notebook_mode : bool, optional
        optimize plot size for notebooks, default is True.

    """
    if mode != MODE_PLOT_SETUP:
        return

    logger.info("plotting geometry setup...")

    logger.debug("Creating beam")
    beam = Beam(data_norm, event=0, plot_setup=True)

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
        notebook_mode=notebook_mode,
    )
