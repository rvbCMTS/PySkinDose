import numpy as np

from pyskindose import constants as const
from pyskindose.phantom_class import Phantom
from pyskindose.settings import PyskindoseSettings


def create_dose_map_plot(
    patient: Phantom, settings: PyskindoseSettings, dose_map: np.ndarray
) -> None:
    # Fix error with plotly layout for 2D plane patient.
    if patient.phantom_model == const.PHANTOM_MODEL_PLANE:
        patient = Phantom(
            phantom_model=settings.phantom.model, phantom_dim=settings.phantom.dimension
        )

    # Append and plot dose map
    patient.dose = dose_map
    patient.plot_dosemap()
