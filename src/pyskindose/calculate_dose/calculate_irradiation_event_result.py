import logging
from typing import Any, Dict, List

import numpy as np
import pandas as pd
from scipy.interpolate import CubicSpline
from tqdm import tqdm

from pyskindose import Phantom
from pyskindose import constants as c
from pyskindose.calculate_dose.add_correction_and_event_dose_to_output import (
    add_corrections_and_event_dose_to_output,
)
from pyskindose.calculate_dose.perform_calculations_for_new_geometries import (
    perform_calculations_for_new_geometries,
)

logger = logging.getLogger(__name__)


def calculate_irradiation_event_result(
    normalized_data: pd.DataFrame,
    event: int,
    total_events: int,
    new_geometry: List[bool],
    k_tab: List[float],
    hits: List[bool],
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    back_scatter_interpolation: List[CubicSpline],
    output: Dict[str, Any],
    table_hits: List[bool] = None,
    field_area: List[float] = None,
    k_isq: np.array = None,
    pbar: tqdm = None,
) -> Dict[str, Any]:
    """Conducts skin dose calculation.

    This function loops though all irradiation events in the the normalized data, and
    calculates the skin dose contribution from each event.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    event : starting event index
        Index of starting irradiation event
    total_events :
        Total number of irradiation events
    new_geometry : List[bool]
        A boolean list that specifies whether the irradiation geometry has changes since
        the preceding event. See the function check_new_geometry
    k_tab : List[float]
        List of table correction factors
    hits : List[bool]
        A boolean list that specifies (for a single event) the hit/miss status of each
        skin cell upon the patient phantom.
    patient : Phantom
        Patient skin surface phantom
    table : Phantom
        Patient support table phantom
    pad : Phantom
        Patient support pad phantom
    back_scatter_interpolation : List[CubicSpline]
        List of interpolation objects to used to estimate backscatter correction from
        the correction database
    output : Dict[str, Any]
        Dictionary containing outputs to store from the calculations. E.g. dose map and
        correction factors.
    table_hits : List[bool], optional
        A boolean list that specfies (for each hit), if the bean passes through the
        patient support table, by default None
    field_area : List[float], optional
        X-ray field area in (cm^2) for each phantom skin cell that are hit by the X-ray
        beam, by default None
    k_isq : np.array, optional
        Inverse-square-law correction factors, by default None
    pbar : tqdm
        progress bar object

    Returns
    -------
    Dict[str, Any]
        Dictionary containing skin dose calculation results.

    """
    logger.debug(f"Calculating irradiation event {event + 1} out of {total_events}")

    hits, table_hits, field_area, k_isq = perform_calculations_for_new_geometries(
        normalized_data=normalized_data,
        event=event,
        new_geometry=new_geometry[event],
        patient=patient,
        table=table,
        pad=pad,
        hits=hits,
        table_hits=table_hits,
        field_area=field_area,
        k_isq=k_isq,
    )

    logger.debug("Saving event data")

    output[c.OUTPUT_KEY_HITS][event] = hits
    output[c.OUTPUT_KEY_KERMA][event] = normalized_data.K_IRP[event]
    output[c.OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW][event] = k_isq

    output = add_corrections_and_event_dose_to_output(
        normalized_data=normalized_data,
        event=event,
        hits=hits,
        table_hits=table_hits,
        patient=patient,
        back_scatter_interpolation=back_scatter_interpolation,
        field_area=field_area,
        k_tab=k_tab,
        output=output,
    )

    event += 1
    if event < total_events:

        pbar.update()

        output = calculate_irradiation_event_result(
            normalized_data=normalized_data,
            event=event,
            total_events=total_events,
            new_geometry=new_geometry,
            k_tab=k_tab,
            hits=hits,
            patient=patient,
            table=table,
            pad=pad,
            back_scatter_interpolation=back_scatter_interpolation,
            output=output,
            table_hits=table_hits,
            field_area=field_area,
            k_isq=k_isq,
            pbar=pbar,
        )

        if event == total_events - 1:
            pbar.update()
            pbar.refresh()
    return output
