from typing import List, Dict, Any

import numpy as np
import pandas as pd
from pyskindose import Phantom, constants as const

# from pyskindose.calculate_dose.calculate_dose import logger
from pyskindose.corrections import calculate_k_med
from scipy.interpolate import CubicSpline


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
    event_dose = np.zeros(len(patient.r))
    if not sum(hits):
        output[const.OUTPUT_KEY_DOSE_MAP] += event_dose
        return output

    # logger.debug("Calculating back scatter correction factor")
    k_bs = back_scatter_interpolation[event](np.sqrt(field_area))

    # logger.debug("Calculating reference point medium correction (air -> water)")
    k_med = calculate_k_med(
        data_norm=normalized_data, field_area=field_area, event=event
    )

    output[const.OUTPUT_KEY_CORRECTION_BACK_SCATTER][event] = k_bs
    output[const.OUTPUT_KEY_CORRECTION_MEDIUM][event] = k_med
    output[const.OUTPUT_KEY_CORRECTION_TABLE][event] = k_tab[event]

    # logger.debug("Calculating event skin dose by applying each correction factor to the reference point air kerma")
    event_dose[hits] += normalized_data.K_IRP[event]
    event_dose[hits] *= output[const.OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW][event]
    event_dose[hits] *= k_med
    event_dose[hits] *= k_bs

    temp = np.ones(len(table_hits))
    temp[table_hits] = k_tab[event]
    event_dose[hits] *= temp

    output[const.OUTPUT_KEY_DOSE_MAP] += event_dose

    return output
