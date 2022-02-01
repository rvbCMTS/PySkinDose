import os
import sys
from pathlib import Path

import numpy as np
import pydicom

from pyskindose.rdsr_normalizer import rdsr_normalizer
from pyskindose.rdsr_parser import rdsr_parser

phantom_path = Path(__file__).parent.parent.parent / "src" / "pyskindose" / "example_data" / "RDSR"


def test_nr_irradiation_events_parsing_in_rdsr_parser():

    # load SR file with known number of irradiation events
    RDSR_file = pydicom.read_file(phantom_path / "s1.dcm")

    expected = 24

    # parse raw rdsr file
    data_parsed = rdsr_parser(data_raw=RDSR_file)

    test = len(data_parsed)

    assert expected == test


def test_xray_filter_material_parsing():
    # knowns filter thicknesses
    expected = [1.0, 0.4, 0.0, 0.6]
    test = []

    RDSR_philips = pydicom.read_file(phantom_path / "philips_allura_clarity_u104.dcm")
    RDSR_siemens = pydicom.read_file(phantom_path / "siemens_axiom_artis.dcm")

    data_parsed_philips = rdsr_parser(data_raw=RDSR_philips)
    data_parsed_siemens = rdsr_parser(data_raw=RDSR_siemens)

    data_norm_philips = rdsr_normalizer(data_parsed=data_parsed_philips)
    data_norm_siemens = rdsr_normalizer(data_parsed=data_parsed_siemens)

    test.append(data_norm_philips["filter_thickness_Al"][0])
    test.append(data_norm_philips["filter_thickness_Cu"][0])
    test.append(data_norm_siemens["filter_thickness_Al"][0])
    test.append(data_norm_siemens["filter_thickness_Cu"][0])

    a = 1

    assert expected == test


def test_xray_filter_mean_value_calculation():

    RDSR_file = pydicom.read_file(phantom_path / "philips_allura_clarity_u104.dcm")

    data_parsed = rdsr_parser(data_raw=RDSR_file)
    data_norm = rdsr_normalizer(data_parsed=data_parsed)

    test_event = 0

    # manually calculate mean filter thickness
    min_thickness = data_parsed["XRayFilterThicknessMinimum_mm"][test_event]
    max_thickness = data_parsed["XRayFilterThicknessMaximum_mm"][test_event]

    expected_mean_Al_thickness = np.mean([float(min_thickness[1]), float(max_thickness[1])])
    expected_mean_Cu_thickness = np.mean([float(min_thickness[0]), float(max_thickness[0])])

    # compare to the rdsr normalizer
    test_mean_Al_thickness = data_norm["filter_thickness_Al"][test_event]
    test_mean_Cu_thickness = data_norm["filter_thickness_Cu"][test_event]

    expected = [expected_mean_Al_thickness, expected_mean_Cu_thickness]
    test = [test_mean_Al_thickness, test_mean_Cu_thickness]

    assert expected == test
