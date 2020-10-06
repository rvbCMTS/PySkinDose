from typing import Any, Dict, Optional
import pandas as pd

from pyskindose import constants as const
from pyskindose.calculate_dose.calculate_dose import calculate_dose
from pyskindose.phantom_class import Phantom
from pyskindose.plotting.create_dose_map_plot import create_dose_map_plot
from pyskindose.plotting.create_geometry_plot import create_geometry_plot
from pyskindose.settings import PyskindoseSettings


def analyze_data(
    normalized_data: pd.DataFrame,
    settings: PyskindoseSettings,
    plot_dose_map: Optional[bool] = False,
) -> Dict[str, Any]:
    """Analyze data och settings, and runs PySkinDose in desired mode.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    settings : PyskindoseSettings
        Settings class for PySkinDose
    plot_dose_map : Optional[bool], optional
        Wheter or not to plot dose map, by default False

    Returns
    -------
    Dict[str, Any]
        output dictionary containing calculation specifics such as dose map, correction
        factors, etc..

    """
    # create table, pad and patient phantoms.
    table = Phantom(
        phantom_model=const.PHANTOM_MODEL_TABLE, phantom_dim=settings.phantom.dimension
    )

    pad = Phantom(
        phantom_model=const.PHANTOM_MODEL_PAD, phantom_dim=settings.phantom.dimension
    )

    create_geometry_plot(
        normalized_data=normalized_data, table=table, pad=pad, settings=settings
    )

    patient, output = calculate_dose(
        normalized_data=normalized_data, settings=settings, table=table, pad=pad
    )

    if not plot_dose_map:
        return output

    create_dose_map_plot(
        patient=patient, settings=settings, dose_map=output[const.OUTPUT_KEY_DOSE_MAP]
    )

    return output
