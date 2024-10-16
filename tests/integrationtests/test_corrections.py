import pandas as pd

from pyskindose.geom_calc import fetch_and_append_hvl
from pyskindose.rdsr_normalizer import rdsr_normalizer


def test_that_hvl_can_be_fetched_from_correction_database(allura_parsed, axiom_artis_parsed, example_settings):

    data_norm_philips: pd.DataFrame = rdsr_normalizer(data_parsed=allura_parsed, settings=example_settings)
    data_norm_siemens: pd.DataFrame = rdsr_normalizer(data_parsed=axiom_artis_parsed, settings=example_settings)

    datas = [data_norm_philips, data_norm_siemens]
    actual = []

    expected = [True, True]

    for i in range(len(datas)):
        try:
            fetch_and_append_hvl(
                data_norm=datas[i], inherent_filtration=3.1, corrections_db=example_settings.corrections_db_path
            )
            actual.append(True)
        #
        except Exception:
            actual.append(False)

    assert actual == expected
