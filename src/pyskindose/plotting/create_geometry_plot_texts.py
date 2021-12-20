import logging
from typing import List, Optional, Tuple

import numpy as np

from ..beam_class import Beam
from ..phantom_class import Phantom

logger = logging.getLogger(__name__)


def create_geometry_plot_texts(
    beam: Beam,
    table: Phantom,
    pad: Phantom,
    patient: Optional[Phantom] = None,
) -> Tuple[List[str], List[str], List[str], List[str], List[str], Optional[List[str]]]:
    """Create lists text strings to show when hovering in geometry plots

    Parameters
    ----------
    beam : Beam
        Instance of the Beam class containing info needed for the X-ray source, beam and
        detector texts
    table : Phantom
        Table phantom from instance of class Phantom. phantom_model must be "table"
    pad : Phantom
        Pad phantom from instance of class Phantom. phantom_model must be "pad"
    patient : Optional[Phantom]
        Patient phantom from instance of class Phantom. Can be of phantom_model "plane",
        "cylinder" or "human"
    """
    logger.debug("Creating geometry plot (and hover) texts")
    source_text = [
        (
            "<b>X-ray source</b>"
            "<br><br>"
            f"<b>LAT : </b>{np.around(beam.r[0, 2])} cm"
            "<br>"
            f"<b>LON : </b>{np.around(beam.r[0, 0])} cm"
            "<br>"
            f"<b>VER : </b>{np.around(beam.r[0, 1])} cm"
        )
    ]

    beam_text = [
        (
            "<b>X-ray beam vertex</b>"
            "<br><br>"
            f"<b>LAT : </b>{np.around(beam.r[ind, 2])} cm"
            "<br>"
            f"<b>LON : </b>{np.around(beam.r[ind, 0])} cm"
            "<br>"
            f"<b>VER : </b>{np.around(beam.r[ind, 1])} cm"
        )
        for ind in range(len(beam.r))
    ]

    detectors_text = [
        (
            "<b>X-ray detector</b>"
            "<br><br>"
            f"<b>LAT : </b>{np.around(beam.det_r[ind, 2])} cm"
            "<br>"
            f"<b>LON : </b>{np.around(beam.det_r[ind, 0])} cm"
            "<br>"
            f"<b>VER : </b>{np.around(beam.det_r[ind, 1])} cm"
        )
        for ind in range(len(beam.det_r))
    ]

    table_text = [
        (
            "<b>Support table</b>"
            "<br><br>"
            f"<b>LAT : </b>{np.around(table.r[ind, 2])} cm"
            "<br>"
            f"<b>LON : </b>{np.around(table.r[ind, 0])} cm"
            "<br>"
            f"<b>VER : </b>{np.around(table.r[ind, 1])} cm"
        )
        for ind in range(len(table.r))
    ]

    pad_text = [
        (
            "<b>Support pad</b>"
            f"<br><br><b>LAT : </b>{np.around(pad.r[ind, 2])} cm"
            "<br>"
            f"<b>LON : </b>{np.around(pad.r[ind, 0])} cm"
            "<br>"
            f"<b>VER : </b>{np.around(pad.r[ind, 1])} cm"
        )
        for ind in range(len(pad.r))
    ]

    patient_text = None
    if patient is not None:
        patient_text = [
            (
                "<b>Patient phantom</b>"
                f"<br><br><b>LAT : </b>{np.around(patient.r[ind, 2])} cm"
                "<br>"
                f"<b>LON : </b>{np.around(patient.r[ind, 0])} cm"
                "<br>"
                f"<b>VER : </b>{np.around(patient.r[ind, 1])} cm"
            )
            for ind in range(len(patient.r))
        ]

    return source_text, beam_text, detectors_text, table_text, pad_text, patient_text
