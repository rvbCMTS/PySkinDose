import logging
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd

from pyskindose import constants as c
from pyskindose.calculate_dose.calculate_irradiation_event_result import (
    calculate_irradiation_event_result,
)
from pyskindose.corrections import calculate_k_bs, calculate_k_tab
from pyskindose.geom_calc import (
    check_new_geometry,
    fetch_and_append_hvl,
    position_patient_phantom_on_table,
)
from pyskindose.phantom_class import Phantom
from pyskindose.settings_pyskindose import PyskindoseSettings

logger = logging.getLogger(__name__)


def calculate_dose(
    normalized_data: pd.DataFrame,
    settings: PyskindoseSettings,
    table: Phantom,
    pad: Phantom,
) -> Tuple[Phantom, Optional[Dict[str, Any]]]:
    """Calculate skin dose.

    This function initializes the skin dose calculations.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    settings : PyskindoseSettings
        Settings class for PySkinDose
    table : Phantom
        Patient support table phantom
    pad : Phantom
        Patient support pad phantom

    Returns
    -------
    Tuple[Phantom, Optional[Dict[str, Any]]]
        [description]

    """
    if settings.mode != c.MODE_CALCULATE_DOSE:
        logger.debug("Mode not set to calculate dose. Returning without doing anything")
        return None, None

    logger.info("Start performing dose calculations")
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

    normalized_data = fetch_and_append_hvl(data_norm=normalized_data)

    # Check which irradiation events that contains updated
    # geometry parameters since the previous irradiation event
    new_geometry = check_new_geometry(normalized_data)

    # fetch of k_bs interpolation object (k_bs=f(field_size))for all events
    back_scatter_interpolation = calculate_k_bs(data_norm=normalized_data)

    k_tab = calculate_k_tab(
        data_norm=normalized_data,
        estimate_k_tab=settings.estimate_k_tab,
        k_tab_val=settings.k_tab_val,
    )

    total_number_of_events = len(normalized_data)

    if settings.plot.notebook_mode:
        from tqdm import tqdm_notebook as pbar
    else:
        from tqdm import tqdm as pbar

    output_template = {
        c.OUTPUT_KEY_HITS: [[]] * total_number_of_events,
        c.OUTPUT_KEY_KERMA: [np.array] * total_number_of_events,
        c.OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW: [[]] * total_number_of_events,
        c.OUTPUT_KEY_CORRECTION_BACK_SCATTER: [[]] * total_number_of_events,
        c.OUTPUT_KEY_CORRECTION_MEDIUM: [[]] * total_number_of_events,
        c.OUTPUT_KEY_CORRECTION_TABLE: [[]] * total_number_of_events,
        c.OUTPUT_KEY_DOSE_MAP: np.zeros(len(patient.r)),
    }

    output = calculate_irradiation_event_result(
        normalized_data=normalized_data,
        event=0,
        total_events=len(normalized_data),
        new_geometry=new_geometry,
        k_tab=k_tab,
        hits=[],
        patient=patient,
        table=table,
        pad=pad,
        back_scatter_interpolation=back_scatter_interpolation,
        output=output_template,
        pbar=pbar(total=total_number_of_events, leave=False, desc="calculating skindose"),
    )

    return patient, output
