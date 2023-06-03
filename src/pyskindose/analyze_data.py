from typing import Any, Dict, Union

import pandas as pd

from pyskindose import constants as c
from pyskindose.calculate_dose.calculate_dose import calculate_dose
from pyskindose.format_export_data import format_analysis_result_for_export, PySkinDoseOutput
from pyskindose.phantom_class import Phantom
from pyskindose.plotting.create_dose_map_plot import create_dose_map_plot
from pyskindose.plotting.create_geometry_plot import create_geometry_plot
from pyskindose.settings import PyskindoseSettings, initialize_settings


def analyze_data(
    normalized_data: pd.DataFrame,
    settings: Union[str, dict, PyskindoseSettings],
) -> Union[Dict[str, Any], str]:
    """Analyze data och settings, and runs PySkinDose in desired mode.

    Parameters
    ----------
    normalized_data : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    settings : Union[str, dict, PyskindoseSettings]
        Settings class for PySkinDose

    Returns
    -------
    Dict[str, Any]
        output dictionary containing calculation specifics such as dose map, correction
        factors, etc.

    """
    settings = initialize_settings(settings)

    if settings.output_format not in c.RUN_ARGUMENTS_VALID_OUTPUT_FORMATS:
        raise ValueError(
            f"Invalid output format specified. Must be one of {'.'.join(c.RUN_ARGUMENTS_VALID_OUTPUT_FORMATS)}")

    # create table, pad and patient phantoms.
    table = Phantom(phantom_model=c.PHANTOM_MODEL_TABLE, phantom_dim=settings.phantom.dimension)

    pad = Phantom(phantom_model=c.PHANTOM_MODEL_PAD, phantom_dim=settings.phantom.dimension)

    create_geometry_plot(normalized_data=normalized_data, table=table, pad=pad, settings=settings)

    patient, output = calculate_dose(normalized_data=normalized_data, settings=settings, table=table, pad=pad)

    if settings.output_format in [c.RUN_ARGUMENTS_OUTPUT_DICT, c.RUN_ARGUMENTS_OUTPUT_JSON]:
        pyskindose_output: PySkinDoseOutput = format_analysis_result_for_export(
            output,
            patient=patient,
            table=table,
            pad=pad,
            data_norm=normalized_data,
            settings=settings
        )

        return pyskindose_output

    create_dose_map_plot(
        patient=patient,
        settings=settings,
        dose_map=output[c.OUTPUT_KEY_DOSE_MAP] if settings.mode == c.MODE_CALCULATE_DOSE else None
    )

    if settings.output_format == c.RUN_ARGUMENTS_OUTPUT_HTML:
        return output
