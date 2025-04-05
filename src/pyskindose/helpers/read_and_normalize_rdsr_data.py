import logging
import os
from pathlib import Path

import pandas as pd
import pydicom

from pyskindose import rdsr_normalizer, rdsr_parser
from pyskindose.settings import PyskindoseSettings

logger = logging.getLogger(__name__)


def read_and_normalise_rdsr_data(rdsr_filepath: str, settings: PyskindoseSettings):

    rdsr_filepath = (
        Path(rdsr_filepath)
        if rdsr_filepath
        else Path(__file__).parent.parent / "example_data/RDSR" / settings.rdsr_filename
    )

    logger.debug(str(rdsr_filepath.absolute()))

    # If provided, load preparsed rdsr data in .json format
    if ".json" == rdsr_filepath.suffix.lower():
        return pd.read_json(rdsr_filepath)

    # else load RDSR data with pydicom
    data_raw = pydicom.dcmread(rdsr_filepath)

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw, silence_pydicom_warnings=settings.silence_pydicom_warnings)

    # normalized rdsr for compliance with PySkinDose
    normalized_data = rdsr_normalizer(data_parsed, settings=settings)

    if settings.remove_invalid_rows:
        if invalid_kvp_rows := len(normalized_data[normalized_data.kVp == 0]):
            print(f"Removing {invalid_kvp_rows} rows with kVp value = 0")
            normalized_data = normalized_data[normalized_data.kVp != 0].reset_index(drop=True)

    return normalized_data
