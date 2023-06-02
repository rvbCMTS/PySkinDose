import pandas as pd

from pyskindose.geom_calc import fetch_and_append_hvl
from pyskindose.rdsr_normalizer import rdsr_normalizer

def test_that_hvl_can_be_fetched_from_correction_database(
    allura_parsed, axiom_artis_parsed):

    data_norm_philips: pd.DataFrame = rdsr_normalizer(data_parsed=allura_parsed)
    data_norm_siemens: pd.DataFrame = rdsr_normalizer(data_parsed=axiom_artis_parsed)

    datas = [data_norm_philips, data_norm_siemens]
    actual = []

    expected = [True, True]

    for i in range(len(datas)):
        try: 
            fetch_and_append_hvl(data_norm=datas[i], inherent_filtration=3.1)
            actual.append(True)
    #
        except Exception:
            actual.append(False)

    assert actual == expected

