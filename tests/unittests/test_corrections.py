import sys
from pathlib import Path

import numpy as np
import pandas as pd
from pyskindose.corrections import calculate_k_bs, calculate_k_isq, calculate_k_med
from pyskindose.db_connect import db_connect

P = Path(__file__).parent.parent.parent
sys.path.insert(1, str(P.absolute()))


def test_calculate_unchanged_fluence_at_refernce_distance():
    expected = 1
    test = calculate_k_isq(source=np.array([0, 0, 0]), cells=np.array([0, 100, 0]), dref=100)
    assert expected == test


def test_calculate_increased_fluence_at_decreased_distance():
    expected = 4
    test = calculate_k_isq(source=np.array([0, 0, 0]), cells=np.array([0, 50, 0]), dref=100)
    assert expected == test


def test_calculate_decreased_fluence_at_increased_distance():
    expected = 0.25
    test = calculate_k_isq(source=np.array([0, 0, 0]), cells=np.array([0, 200, 0]), dref=100)
    assert expected == test


def test_fetch_correct_backscatter_correction_from_database():
    expected = 5 * [True]

    # Tabulated backscatter factor for param in data_norm
    tabulated_k_bs = [1.3, 1.458, 1.589, 1.617, 1.639]

    data_norm = pd.DataFrame({"kVp": 5 * [80], "HVL": 5 * [7.88], "FSL": [5, 10, 20, 25, 35]})

    # create interpolation object
    bs_interp = calculate_k_bs(data_norm)

    # interpolate at tabulated filed sizes
    k_bs = bs_interp[0](data_norm.FSL)

    diff = [100 * (abs(k_bs[i] - tabulated_k_bs[i])) / tabulated_k_bs[i] for i in range(len(tabulated_k_bs))]

    test = [percent_difference <= 1 for percent_difference in diff]

    assert expected == test


def test_fetch_correct_medium_correction_from_database():
    expected = [1.027, 1.026, 1.025, 1.025, 1.025]

    data = {"kVp": [80], "HVL": [4.99]}
    data_norm = pd.DataFrame(data)

    # Tests if we get a value in expected, for cells with different field
    # sizes with filed side length in [5 to 35] cm.
    test = calculate_k_med(data_norm, np.square([6, 10, 20, 22, 32]), 0)

    assert test in expected


def test_fetch_correct_table_correction_from_database():
    expected = 0.7319

    [conn, c] = db_connect()

    # Set paramets for fetching table transmission correction factor.
    params = (
        80,  # kVp, rounded to nearest integer
        0.3,  # Filter thickness Cu
        0,  # Filter thicknes Al
        "AXIOM-Artis",  # device model
        "Single Plane",
    )  # acquisition plane

    # Fetch k_tab
    c.execute(
        "SELECT k_patient_support FROM table_transmission WHERE \
                kVp_kV=? AND AddedFiltration_mmCu=? AND \
                AddedFiltration_mmAl=? AND DeviceModel=? AND \
                AcquisitionPlane=?",
        params,
    )

    test = c.fetchone()[0]

    conn.commit()
    conn.close()

    assert expected == test
