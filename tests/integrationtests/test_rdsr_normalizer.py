import numpy as np
import pandas as pd

from pyskindose.constants import (
    KEY_NORMALIZATION_FILTER_SIZE_ALUMINUM,
    KEY_NORMALIZATION_FILTER_SIZE_COPPER,
    KEY_RDSR_FILTER_MATERIAL,
    KEY_RDSR_FILTER_MAX,
    KEY_RDSR_FILTER_MIN,
    KEY_RDSR_FILTER_TYPE,
)
from pyskindose.rdsr_normalizer import rdsr_normalizer


def test_that_multiple_xray_filter_materials_are_extracted_during_normalization_if_present(
    allura_parsed, axiom_artis_parsed, example_settings
):
    # Arrange
    expected = [1.0, 0.4, 0.0, 0.6]

    # Act
    data_norm_philips: pd.DataFrame = rdsr_normalizer(data_parsed=allura_parsed, settings=example_settings)
    data_norm_siemens: pd.DataFrame = rdsr_normalizer(data_parsed=axiom_artis_parsed, settings=example_settings)

    actual = [
        data_norm_philips[KEY_NORMALIZATION_FILTER_SIZE_ALUMINUM][0],
        data_norm_philips[KEY_NORMALIZATION_FILTER_SIZE_COPPER][0],
        data_norm_siemens[KEY_NORMALIZATION_FILTER_SIZE_ALUMINUM][0],
        data_norm_siemens[KEY_NORMALIZATION_FILTER_SIZE_COPPER][0],
    ]

    # Assert
    assert actual == expected


def test_xray_filter_mean_thickness_calculated_for_each_filter_material_separately(allura_parsed, example_settings):
    # Arrange
    expected_mean_aluminium_thickness = np.mean(
        [
            float(allura_parsed[KEY_RDSR_FILTER_MIN][0][1]),
            float(allura_parsed[KEY_RDSR_FILTER_MAX][0][1]),
        ]
    )
    expected_mean_copper_thickness = np.mean(
        [
            float(allura_parsed[KEY_RDSR_FILTER_MIN][0][0]),
            float(allura_parsed[KEY_RDSR_FILTER_MAX][0][0]),
        ]
    )

    # Act
    data_norm = rdsr_normalizer(data_parsed=allura_parsed, settings=example_settings)
    actual_mean_aluminium_thickness = data_norm[KEY_NORMALIZATION_FILTER_SIZE_ALUMINUM][0]
    actual_mean_copper_thickness = data_norm[KEY_NORMALIZATION_FILTER_SIZE_COPPER][0]

    # Assert
    assert actual_mean_aluminium_thickness == expected_mean_aluminium_thickness
    assert actual_mean_copper_thickness == expected_mean_copper_thickness


def test_rdsr_normalizer_correctly_handles_events_without_filter(axiom_artis_parsed, example_settings):
    # Arrange
    expected_aluminium_filter_thicknesses = [0.0] * 21
    expected_copper_filter_thicknesses = [
        0.0,
        0.9,
        0.9,
        0.9,
        0.9,
        0.9,
        0.6,
        0.9,
        0.9,
        0.9,
        0.9,
        0.9,
        0.6,
        0.9,
        0.9,
        0.3,
        0.6,
        0.3,
        0.9,
        0.9,
        0.6,
    ]
    parsed_data_with_nofilter_events: pd.DataFrame = axiom_artis_parsed.copy()
    parsed_data_with_nofilter_events.loc[0, KEY_RDSR_FILTER_MATERIAL] = np.nan
    parsed_data_with_nofilter_events.loc[0, KEY_RDSR_FILTER_TYPE] = "NoFilter"
    parsed_data_with_nofilter_events.loc[0, KEY_RDSR_FILTER_MIN] = 0.0
    parsed_data_with_nofilter_events.loc[0, KEY_RDSR_FILTER_MAX] = 0.0

    # Act
    normalized_data = rdsr_normalizer(data_parsed=parsed_data_with_nofilter_events, settings=example_settings)
    actual_aluminium_filter_thicknesses = normalized_data[KEY_NORMALIZATION_FILTER_SIZE_ALUMINUM].tolist()
    actual_copper_filter_thicknesses = normalized_data[KEY_NORMALIZATION_FILTER_SIZE_COPPER].tolist()

    # Assert
    assert actual_aluminium_filter_thicknesses == expected_aluminium_filter_thicknesses
    assert actual_copper_filter_thicknesses == expected_copper_filter_thicknesses


def test_rdsr_normalizer_correctly_applies_table_offset_from_normalization_settings(
    axiom_artis_parsed, example_settings
):
    # Arrange
    expected = [13.78, -9.41, 34.06]
    example_settings.normalization_settings.normalization_settings_list[0]["translation_offset"] = {
        "x": 10.0,
        "y": 20.0,
        "z": 30.0,
    }
    example_settings.normalization_settings.normalization_settings_list[0]["translation_direction"] = {
        "x": "+",
        "y": "-",
        "z": "+",
    }

    # Act
    normalized_data = rdsr_normalizer(data_parsed=axiom_artis_parsed, settings=example_settings)
    actual = [round(normalized_data.Tx[0], 4), round(normalized_data.Ty[0], 3), round(normalized_data.Tz[0], 4)]

    # Assert
    assert actual == expected
