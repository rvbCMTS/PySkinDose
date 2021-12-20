from typing import Union

from ..beam_class import Beam
from ..constants import PHANTOM_MODEL_PLANE
from ..phantom_class import Phantom


def _get_visual_offset(patient: Union[Phantom, Beam]) -> float:
    """Set visual offset of phantom objects.

    Determines the visual offset needed for visualizing the phantom correctly in the
    plot.

    Parameters
    ----------
    patient : Phantom
        Patient phantom from instance of class Phantom. Can be of phantom_model "plane",
        "cylinder" or "human"

    """
    if not isinstance(patient, Phantom):
        return 0.0

    if patient.phantom_model == PHANTOM_MODEL_PLANE:
        return -0.01

    return 0.0
