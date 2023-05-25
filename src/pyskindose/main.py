import argparse
import logging
import os
import sys
from typing import Optional, Union

import pandas as pd
import pydicom

from pyskindose.analyze_data import analyze_data
from pyskindose.constants import RUN_ARGUMENTS_MODE_HEADLESS, RUN_ARGUMENTS_MODE_GUI
from pyskindose.dev_data import DEVELOPMENT_PARAMETERS
from pyskindose.rdsr_normalizer import rdsr_normalizer
from pyskindose.rdsr_parser import rdsr_parser
from pyskindose.settings import PyskindoseSettings, initialize_settings

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
    settings = _parse_settings_to_settings_class(settings=settings)

    data_norm = _read_and_normalise_rdsr_data(rdsr_filepath=file_path, settings=settings)

    _ = analyze_data(normalized_data=data_norm, settings=settings)


def _parse_settings_to_settings_class(settings: Optional[str] = None):
    try:
        return initialize_settings(settings)
    except ValueError:
        logger.debug("Tried initializing settings without any settings")

    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")

    if not os.path.exists(settings_path):
        logger.warning("Settings path not specified. Using example settings.")
        settings_path = os.path.join(os.path.dirname(__file__), "settings_example.json")

    with open(settings_path, "r") as fp:
        output = fp.read()

    return PyskindoseSettings(output)


def _read_and_normalise_rdsr_data(rdsr_filepath: str, settings: PyskindoseSettings):

    if not rdsr_filepath:
        rdsr_filepath = os.path.join(os.path.dirname(__file__), "example_data", "RDSR", settings.rdsr_filename)

    logger.debug(rdsr_filepath)

    "If provided, load preparsed rdsr data in .json format"
    if ".json" in rdsr_filepath:
        return pd.read_json(rdsr_filepath)

    # else load RDSR data with pydicom
    data_raw = pydicom.dcmread(rdsr_filepath)

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw)

    # normalized rdsr for compliance with PySkinDose
    normalized_data = rdsr_normalizer(data_parsed, settings=settings)

    return normalized_data


def get_argument_parser(args) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="PySkinDose",
        description=(
            "PySkinDose is a Python version 3.7 based program for patient peak"
            " skin dose (PSD) estimations from fluoroscopic procedures in"
            " interventional radiology."
        ),
    )
    parser.add_argument(
        "--mode", "-m",
        choices=(
            RUN_ARGUMENTS_MODE_HEADLESS,
            RUN_ARGUMENTS_MODE_GUI
        ),
        default=RUN_ARGUMENTS_MODE_HEADLESS,
    )
    headless = parser.add_subparsers(title="headless", help="headless parameters")

    parser.add_argument(
        "--file-path", "-f",
        required=False,
        dest="file_path",
        help="Path to RDSR DICOM file (required in headless mode)"
    )

    parser.add_argument(
        "--settings", "-s",
        required=False,
        dest="settings",
        help="Path to the settings file to use if a specific settings file is required"
    )

    return parser.parse_args(args)


if __name__ == "__main__":
    args = get_argument_parser(sys.argv)

    main(file_path=args.file_path, settings=DEVELOPMENT_PARAMETERS)
