import logging
import os

import pandas as pd
import pydicom

from pyskindose import rdsr_parser, rdsr_normalizer
from pyskindose.settings import PyskindoseSettings

logger = logging.getLogger(__name__)


def read_and_normalise_rdsr_data(rdsr_filepath: str, settings: PyskindoseSettings):

    if not rdsr_filepath:
        rdsr_filepath = os.path.join(os.path.dirname(__file__), "example_data", "RDSR", settings.rdsr_filename)

    logger.debug(rdsr_filepath)

    # If provided, load preparsed rdsr data in .json format
    if ".json" in rdsr_filepath:
        return pd.read_json(rdsr_filepath)

    # else load RDSR data with pydicom
    data_raw = pydicom.dcmread(rdsr_filepath)

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw)

    # normalized rdsr for compliance with PySkinDose
    normalized_data = rdsr_normalizer(data_parsed, settings=settings)

    return normalized_data
