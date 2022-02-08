import os
import sys
from pathlib import Path

import numpy as np
import pydicom

from pyskindose.rdsr_normalizer import rdsr_normalizer
from pyskindose.rdsr_parser import rdsr_parser

phantom_path = Path(__file__).parent.parent.parent / "src" / "pyskindose" / "example_data" / "RDSR"


def test_that_all_rdst_events_are_extracted_during_parsing():

    # load SR file with known number of irradiation events
    RDSR_file = pydicom.dcmread(phantom_path / "s1.dcm")

    expected = 24

    # parse raw rdsr file
    data_parsed = rdsr_parser(data_raw=RDSR_file)

    actual = len(data_parsed)

    assert actual == expected


def test_that_multple_xray_filter_materials_are_extracted_during_normalization_if_present():

    # knowns filter thicknesses
    expected = [1.0, 0.4, 0.0, 0.6]
    actual = []

    RDSR_philips = pydicom.dcmread(phantom_path / "philips_allura_clarity_u104.dcm")
    RDSR_siemens = pydicom.dcmread(phantom_path / "siemens_axiom_artis.dcm")

    data_parsed_philips = rdsr_parser(data_raw=RDSR_philips)
    data_parsed_siemens = rdsr_parser(data_raw=RDSR_siemens)

    data_norm_philips = rdsr_normalizer(data_parsed=data_parsed_philips)
    data_norm_siemens = rdsr_normalizer(data_parsed=data_parsed_siemens)

    actual.append(data_norm_philips["filter_thickness_Al"][0])
    actual.append(data_norm_philips["filter_thickness_Cu"][0])
    actual.append(data_norm_siemens["filter_thickness_Al"][0])
    actual.append(data_norm_siemens["filter_thickness_Cu"][0])

    assert actual == expected


def test_xray_filter_mean_thickness_calculated_for_each_filter_material_separately():

    RDSR_file = pydicom.dcmread(phantom_path / "philips_allura_clarity_u104.dcm")

    data_parsed = rdsr_parser(data_raw=RDSR_file)
    data_norm = rdsr_normalizer(data_parsed=data_parsed)

    actual_event = 0

    # manually calculate mean filter thickness
    expected_min_thickness = data_parsed["XRayFilterThicknessMinimum_mm"][actual_event]
    expected_max_thickness = data_parsed["XRayFilterThicknessMaximum_mm"][actual_event]

    expected_mean_Al_thickness = np.mean([float(expected_min_thickness[1]), float(expected_max_thickness[1])])
    expected_mean_Cu_thickness = np.mean([float(expected_min_thickness[0]), float(expected_max_thickness[0])])

    # compare to the rdsr normalizer
    actual_mean_Al_thickness = data_norm["filter_thickness_Al"][actual_event]
    actual_mean_Cu_thickness = data_norm["filter_thickness_Cu"][actual_event]

    expected = [expected_mean_Al_thickness, expected_mean_Cu_thickness]
    actual = [actual_mean_Al_thickness, actual_mean_Cu_thickness]

    assert actual == expected
