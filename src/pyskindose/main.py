import argparse
import logging
import os
import pydicom
from typing import Union, Optional

from pyskindose.analyze_data import analyze_data
from pyskindose.dev_data import DEVELOPMENT_PARAMETERS
from pyskindose.parse_data import rdsr_parser
from pyskindose.parse_data import rdsr_normalizer
from pyskindose.settings import PyskindoseSettings

# logger = logging.getLogger(__name__)

DESCRIPTION = (
    "PySkinDose is a Python version 3.7 based program for patient peak skin dose (PSD)"
    "estimations from fluoroscopic procedures in interventional radiology."
)

PARSER = argparse.ArgumentParser(description=DESCRIPTION)

PARSER.add_argument("--file-path", help="Path to RDSR DICOM file")
ARGS = PARSER.parse_args()


def main(file_path: Optional[str] = None, settings: Union[str, dict] = None):
    """Run PySkinDose.

    Copy settings_examples.json and save it as settings.json.
    Set all you parameters in this file. For debugging and developement,
    the PARAM_dev settings dictionary can be used by calling
    main(settings=PARAM_DEV).

    See settings.py for a description of all the parameters. Please visit
    https://dev.azure.com/Sjukhusfysiker/PySkinDose for info on how to run
    PySkinDose.

    Parameters
    ----------
    file_path : str, optional
        file path to RDSR file
    settings : Union[str, dict], optional
        Setting file in either dict or json string format, by default
        settings_examples.json is enabled.

    """
    settings = _parse_settings_to_settings_class(settings=settings)

    data_norm = _read_and_normalise_data_from_rdsr_file(
        rdsr_filepath=file_path, settings=settings
    )

    _ = analyze_data(normalized_data=data_norm, settings=settings, plot_dose_map=False)

def _parse_settings_to_settings_class(settings: Optional[str] = None):
    if settings is not None:
        return PyskindoseSettings(settings)

    settings_path = os.path.join(os.path.dirname(__file__), "settings.json")

    if not os.path.exists(settings_path):
        # logger.warning("The give settings path does not exist. Using example settings.")
        settings_path = os.path.join(os.path.dirname(__file__), "settings_example.json")

    with open(settings_path, "r") as fp:
        output = fp.read()

    return PyskindoseSettings(output)


def _read_and_normalise_data_from_rdsr_file(
    rdsr_filepath: str, settings: PyskindoseSettings
):
    if not rdsr_filepath:
        rdsr_filepath = os.path.join(
            os.path.dirname(__file__), "example_data", "RDSR", settings.rdsr_filename
        )
        # logger.debug(rdsr_filepath)
    # Read RDSR data with pydicom
    data_raw = pydicom.read_file(rdsr_filepath)

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw)

    # normalized rdsr for compliance with PySkinDose
    normalized_data = rdsr_normalizer(data_parsed)

    return normalized_data


main(file_path=ARGS.file_path, settings=DEVELOPMENT_PARAMETERS)
