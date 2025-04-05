import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from pyskindose.analyze_data import analyze_data
from pyskindose.constants import (
    RUN_ARGUMENTS_MODE_GUI,
    RUN_ARGUMENTS_MODE_HEADLESS,
    RUN_ARGUMENTS_OUTPUT_DICT,
    RUN_ARGUMENTS_OUTPUT_HTML,
    RUN_ARGUMENTS_OUTPUT_JSON,
)
from pyskindose.dev_data import DEVELOPMENT_PARAMETERS
from pyskindose.helpers.parse_settings_to_settings_class import (
    parse_settings_to_settings_class,
)
from pyskindose.helpers.read_and_normalize_rdsr_data import read_and_normalise_rdsr_data
from pyskindose.settings import PyskindoseSettings

logger = logging.getLogger(__name__)


def main(file_path: Optional[str] = None, settings: Union[str, dict, PyskindoseSettings] = None):
    """Run PySkinDose.

    Copy settings_examples.json and save it as settings.json.
    Set all you parameters in this file. For debugging and developement,
    the PARAM_dev settings dictionary can be used by calling
    main(settings=PARAM_DEV).

    See settings.py for a description of all the parameters. Please visit
    https://github.com/rvbCMTS/PySkinDose for info on how to run
    PySkinDose.

    Parameters
    ----------
    file_path : str, optional
        file path to RDSR file or preparsed RDSR data in .json format
    settings : Union[str, dict, PyskindoseSettings], optional
        Setting file in either dict, json string format, or as a
        PyskindoseSettings object. By default, settings_examples.json is
        enabled.

    """
    settings = parse_settings_to_settings_class(settings=settings)

    data_norm = read_and_normalise_rdsr_data(rdsr_filepath=file_path, settings=settings)

    output = analyze_data(normalized_data=data_norm, settings=settings)

    if settings.output_format in ("dict", "json"):
        return output

def analyze_normalized_data_with_custom_settings_object(
    data_norm: pd.DataFrame,
    settings: Union[PyskindoseSettings, str, dict],
    output_format: Optional[str] = RUN_ARGUMENTS_OUTPUT_JSON,
) -> Union[str, dict]:
    """Run PySkinDose with custom normalized data and a custom specified settings objects.

    See the

    Parameters
    ----------
    data_norm : pd.DataFrame
        A pandas DataFrame containing the normalized data
    settings : Union[PySkinDoseSettings, str, dict]
        The settings for the PySkinDose analysis given as a PySKinDoseSettings object, a json-formatted string or a dict
    output_format : str, optional
        String specifying the output format. Valid values are "json"(default) and "dict"
    """
    if not isinstance(settings, (PyskindoseSettings, str, dict)):
        raise TypeError("Invalid type for input settings")

    if not isinstance(output_format, str) or not output_format.casefold() in [
        RUN_ARGUMENTS_OUTPUT_JSON,
        RUN_ARGUMENTS_OUTPUT_DICT,
        RUN_ARGUMENTS_OUTPUT_HTML,
    ]:
        raise ValueError(
            f"The output_format must be specified as a string with one of the valid values {RUN_ARGUMENTS_OUTPUT_JSON} "
            f"or {RUN_ARGUMENTS_OUTPUT_DICT}"
        )

    settings = parse_settings_to_settings_class(settings=settings)
    settings.output_format = output_format.casefold()

    return analyze_data(normalized_data=data_norm, settings=settings)


def get_argument_parser(arguments) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="PySkinDose",
        description=(
            "PySkinDose is a Python version 3.8 based program for patient peak"
            " skin dose (PSD) estimations from fluoroscopic procedures in"
            " interventional radiology."
        ),
    )
    parser.add_argument(
        "--mode",
        "-m",
        dest="mode",
        choices=(RUN_ARGUMENTS_MODE_HEADLESS, RUN_ARGUMENTS_MODE_GUI),
        default=RUN_ARGUMENTS_MODE_HEADLESS,
    )

    parser.add_argument(
        "--file-path",
        "-f",
        required=False,
        dest="file_path",
        help="Path to RDSR DICOM file (required in headless mode)",
    )

    parser.add_argument(
        "--settings",
        "-s",
        required=False,
        type=Path,
        default=None,
        dest="settings",
        help="Path to the settings file to use if a specific settings file is required",
    )

    return parser.parse_args(arguments)


if __name__ == "__main__":
    args = get_argument_parser(sys.argv)

    if (run_settings := args.settings) is None:
        logger.warning("No settings specified. Running with development parameters")
        run_settings = DEVELOPMENT_PARAMETERS

    main(file_path=args.file_path, settings=run_settings)
