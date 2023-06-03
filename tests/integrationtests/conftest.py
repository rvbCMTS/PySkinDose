from pathlib import Path

import pandas as pd
import pydicom
import pytest

from pyskindose.rdsr_parser import rdsr_parser


@pytest.fixture(scope="function")
def example_rdsr_path() -> Path:
    return Path(__file__).parent.parent.parent / "src/pyskindose/example_data/RDSR"


@pytest.fixture(scope="function")
def phantom_path(example_rdsr_path) -> Path:
    return example_rdsr_path / "siemens_axiom_example_procedure.dcm"


@pytest.fixture(scope="function")
def phantom_dataset(phantom_path) -> pydicom.FileDataset:
    return pydicom.dcmread(phantom_path)


@pytest.fixture(scope="function")
def allura_rdsr_path(example_rdsr_path) -> Path:
    return example_rdsr_path / "philips_allura_clarity_u104.dcm"


@pytest.fixture(scope="function")
def allura_dataset(allura_rdsr_path) -> pydicom.FileDataset:
    return pydicom.dcmread(allura_rdsr_path)


@pytest.fixture(scope="function")
def axiom_artis_rdsr_path(example_rdsr_path) -> Path:
    return example_rdsr_path / "siemens_axiom_artis.dcm"


@pytest.fixture(scope="function")
def axiom_artis_dataset(axiom_artis_rdsr_path) -> pydicom.FileDataset:
    return pydicom.dcmread(axiom_artis_rdsr_path)


@pytest.fixture(scope="function")
def axiom_artis_parsed(axiom_artis_dataset) -> pd.DataFrame:
    return rdsr_parser(axiom_artis_dataset)


@pytest.fixture(scope="function")
def allura_parsed(allura_dataset) -> pd.DataFrame:
    return rdsr_parser(allura_dataset)
