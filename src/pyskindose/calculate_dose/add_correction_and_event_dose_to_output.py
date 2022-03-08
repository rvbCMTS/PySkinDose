import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline

from pyskindose import Phantom
from pyskindose import constants as c
from pyskindose.corrections import calculate_k_med

logger = logging.getLogger(__name__)


def add_corrections_and_event_dose_to_output(
    normalized_data: pd.DataFrame,
    event: int,
    hits: List[bool],
    table_hits: List[bool],
    patient: Phantom,
    back_scatter_interpolation: List[CubicSpline],
    field_area: List[float],
    k_tab: List[float],
    output: Dict[str, Any],
) -> Dict[str, Any]:
    """Add correction factors and event dose to output dictionary.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    event : int
        Irradiation event index.
    hits : List[bool]
        A boolean list of the same length as the number of patient skin cells. True for
        all entrance skin cells that are hit by the beam for a specific irradiation
        event.
    table_hits : List[bool]
        A boolean list that specfies (for each hit), if the bean passes through the
        patient support table, by default None
    patient : Phantom
        Patient phantom, either of type plane, cylinder or human, i.e. instance of class
        Phantom
    back_scatter_interpolation : List[CubicSpline]
        List of interpolation objects to used to estimate backscatter correction from
        the correction database
    field_area : List[float]
        X-ray field area in (cm^2) for each phantom skin cell that are hit by the X-ray
        beam
    k_tab : List[float]
        List of table correction factors
    output : Dict[str, Any]
        Dictionary containing outputs to store from the calculations. E.g. dose map and
        correction factors.

    Returns
    -------
    Dict[str, Any]
        Dictionary containing outputs to store from the calculations. E.g. dose map and
        correction factors.

    """
    event_dose = np.zeros(len(patient.r))
    if not sum(hits):
        output[c.OUTPUT_KEY_DOSE_MAP] += event_dose
        return output

    logger.debug("Calculating back scatter correction factor")
    k_bs = back_scatter_interpolation[event](np.sqrt(field_area))

    logger.debug("Calculating reference point medium correction (air -> water)")
    k_med = calculate_k_med(data_norm=normalized_data, field_area=field_area, event=event)

    output[c.OUTPUT_KEY_CORRECTION_BACK_SCATTER][event] = k_bs
    output[c.OUTPUT_KEY_CORRECTION_MEDIUM][event] = k_med
    output[c.OUTPUT_KEY_CORRECTION_TABLE][event] = k_tab[event]

    logger.debug("Calculating event skin dose by applying each correction" "factor to the reference point air kerma")

    event_dose[hits] += normalized_data.K_IRP[event]
    event_dose[hits] *= output[c.OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW][event]

    event_dose[hits] *= k_med
    event_dose[hits] *= k_bs

    temp = np.ones(len(table_hits))
    temp[table_hits] = k_tab[event]
    event_dose[hits] *= temp

    output[c.OUTPUT_KEY_DOSE_MAP] += event_dose

    return output
