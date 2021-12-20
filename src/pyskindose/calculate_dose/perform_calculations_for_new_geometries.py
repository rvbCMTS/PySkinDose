import logging
from typing import List

import numpy as np
import pandas as pd

from pyskindose import Beam, Phantom
from pyskindose import constants as c
from pyskindose import scale_field_area
from pyskindose.corrections import calculate_k_isq
from pyskindose.geom_calc import check_table_hits

logger = logging.getLogger(__name__)


def perform_calculations_for_new_geometries(
    normalized_data: pd.DataFrame,
    event: int,
    new_geometry: bool,
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    hits: List[bool],
    table_hits: List[bool],
    field_area: List[float],
    k_isq: np.array,
):
    if not new_geometry:
        return hits, table_hits, field_area, k_isq

    beam = Beam(data_norm=normalized_data, event=event, plot_setup=False)

    patient.position(data_norm=normalized_data, event=event)
    table.position(data_norm=normalized_data, event=event)
    pad.position(data_norm=normalized_data, event=event)

    logger.debug("Checking which skin cells are hit by the beam")
    hits = beam.check_hit(patient=patient)

    if sum(hits):
        logger.debug("Checking which hit skin cells need table correction")
        table_hits = check_table_hits(source=beam.r[0, :], table=table, beam=beam, cells=patient.r[hits])

        logger.debug("Calculating X-Ray field area at the location of each skin cell")
        field_area = scale_field_area(
            data_norm=normalized_data,
            event=event,
            patient=patient,
            hits=hits,
            source=beam.r[0, :],
        )

        logger.debug("Calculating inverse-square law fluence correction")
        k_isq = calculate_k_isq(
            source=beam.r[0, :],
            cells=patient.r[hits],
            dref=normalized_data[c.DATA_DS_IRP][0],
        )

    return hits, table_hits, field_area, k_isq
