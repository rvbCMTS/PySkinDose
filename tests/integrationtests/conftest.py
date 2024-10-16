from pathlib import Path
from typing import Dict

import pandas as pd
import pydicom
import pytest

import pyskindose.constants as c
from pyskindose import rdsr_normalizer
from pyskindose.rdsr_parser import rdsr_parser
from pyskindose.settings import PyskindoseSettings


@pytest.fixture(scope="function")
def example_settings() -> PyskindoseSettings:
    settings_dict: Dict = {
        "mode": c.MODE_PLOT_PROCEDURE,
        "rdsr_filename": "siemens_axiom_example_procedure.dcm",
        "plot_event_index": 12,
        "estimate_k_tab": False,
        "inherent_filtration": 3.1,
        "silence_pydicom_warnings": True,
        "k_tab_val": 0.8,
        "plot": {
            "interactivity": True,
            c.MODE_DARK_MODE: True,
            c.MODE_NOTEBOOK_MODE: False,
            c.MODE_PLOT_DOSEMAP: False,
            c.DOSEMAP_COLORSCALE_KEY: c.DOSEMAP_COLORSCALE,
            c.MAX_EVENT_FOR_PATIENT_INCLUSION_IN_PROCEDURE_KEY: 0,
            c.PLOT_EVENT_INDEX_KEY: 12,
        },
        "phantom": {
            "model": c.PHANTOM_MODEL_HUMAN,
            "human_mesh": c.PHANTOM_MESH_ADULT_MALE,
            "patient_offset": {
                c.OFFSET_LONGITUDINAL_KEY: 0,
                c.OFFSET_VERTICAL_KEY: 0,
                c.OFFSET_LATERAL_KEY: -35,
            },
            "patient_orientation": c.PATIENT_ORIENTATION_HEAD_FIRST_SUPINE,
            "dimension": {
                c.DIMENSION_PLANE_LENGTH: 120,
                c.DIMENSION_PLANE_WIDTH: 40,
                c.DIMENSION_PLANE_RESOLUTION: c.RESOLUTION_SPARSE,
                c.DIMENSION_CYLINDER_LENGTH: 150,
                c.DIMENSION_CYLINDER_RADII_A: 20,
                c.DIMENSION_CYLINDER_RADII_B: 10,
                c.DIMENSION_CYLINDER_RESOLUTION: c.RESOLUTION_DENSE,
                c.DIMENSION_TABLE_LENGTH: 281.5,
                c.DIMENSION_TABLE_WIDTH: 45,
                c.DIMENSION_TABLE_THICKNESS: 5,
                c.DIMENSION_PAD_LENGTH: 281.5,
                c.DIMENSION_PAD_WIDTH: 45,
                c.DIMENSION_PAD_THICKNESS: 4,
            },
        },
    }
    return PyskindoseSettings(settings=settings_dict)


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


@pytest.fixture(scope="function")
def axiom_artis_normalized(axiom_artis_parsed, example_settings) -> pd.DataFrame:
    return rdsr_normalizer(data_parsed=axiom_artis_parsed, settings=example_settings)
