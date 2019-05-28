import numpy as np
import pandas as pd
from db_connect import db_connect
from scipy.interpolate import CubicSpline
import scipy.interpolate
from typing import List


def calculate_k_isq(source: np.array, cells: np.array, dref: float)-> np.array:
    """Calculate the IRP air kerma inverse-square law correction.

    This function corrects the X-ray fluence from the interventionl reference
    point (IRP), to the actual source to skin distance, so that the IRP air
    kerma is converted to air kerma at the patient skin surface.

    Parameters
    ----------
    source : np.array
        location of the X-ray source
    cells : np.array
        location of all the cells that are hit by the beam
    dref : float
        reference distance source to IRP, i.e. the distance at which the IRP
        air kerma is stated.

    Returns
    -------
    np.array
        Inverse-square law correction for all cells that are hit by the beam.

    """
    if len(cells) > 3:
        return np.square(dref / np.linalg.norm(cells - source, axis=1))

    return np.square(dref / np.linalg.norm(cells - source, axis=0))


def calculate_k_bs(data_norm: pd.DataFrame) -> List[CubicSpline]:
    """Calculate backscatter correction.

    This function calculates the backscatter correction factor
    for all events, at field sizes [5, 10, 20, 25, 35] cm^2.
    The function uses the non-linear interpolation method presented by
    Benmakhlouf et al. in the article "Influence of phantom thickness and
    material on the backscatter factors for diagnostic x-ray beam dosimetry",
    [doi:10.1088/0031-9155/58/2/247]

    Parameters
    ----------
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.

    Returns
    -------
    List[CubicSpline]
        List of scipy cubic spline interpolation object for all events.

    """
    # Tabulated field side length in cm
    fsl_tab = [5, 10, 20, 25, 35]

    # polynomial coefficents
    c = np.array([
        [+1.00870e+0, +9.29969e-1, +8.65442e-1, +8.58665e-1, +8.57065e-1],
        [+2.35816e-3, +4.08549e-3, +5.36739e-3, +5.51579e-3, +5.55933e-3],
        [-9.48937e-6, -1.66271e-5, -2.21494e-5, -2.27532e-5, -2.28004e-5],
        [+1.03143e-1, +1.53605e-1, +1.72418e-1, +1.70826e-1, +1.66418e-1],
        [-1.04881e-3, -1.45187e-3, -1.46088e-3, -1.38540e-3, -1.28180e-3],
        [+3.59731e-6, +5.05312e-6, +5.17430e-6, +4.91192e-6, +4.53036e-6],
        [-7.31303e-3, -9.32427E-3, -8.30138E-3, -7.64330e-3, -6.81574e-3],
        [+7.93272E-5, +9.40568E-5, +7.13576E-5, +6.13126e-5, +4.94197e-5],
        [-2.74296e-7, -3.28449e-7, -2.54885e-7, -2.21399e-7, -1.79074e-7]])

    # Fetch kVp and HVL from data_norm
    kVp = data_norm.kVp
    HVL = data_norm.HVL

    # Calculate k_bs for field side length [5, 10, 20, 25, 35] cm
    # This is eq. (8) in doi:10.1088/0031-9155/58/2/247.
    bs_corr = [(c[0, :] + c[1, :] * kVp[event] + c[2, :] *
               np.square(kVp[event])) + (c[3, :] + c[4, :] * kVp[event] +
               c[5, :] * np.square(kVp[event])) * HVL[event] + (c[6, :] +
               c[7, :] * kVp[event] + c[8, :] * np.square(kVp[event])) *
               np.square(HVL[event])
               for event in range(len(kVp))]

    # Create interpolation object for bs_corr
    bs_interp = [scipy.interpolate.CubicSpline(fsl_tab, bs_corr[event])
                 for event in range(len(kVp))]

    return bs_interp


def calculate_k_med(data_norm: pd.DataFrame, field_area: List[float], event: int) -> float:
    """Calculate medium correction.

    This function calculates and appends the medium correction factor
    for all skin cells that are hit by the X-ray beam in an event. The
    correction factors are from the article "Backscatter factors and mass
    energy-absorption coefficient ratios for surface dose determination in
    diagnostic radiology".

    Parameters
    ----------
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    field_area : List[float]
        X-ray field area in (cm^2) for each phantom skin cell that are hit by
        X-ray the beam.
    event : int
        Irradiation event index.

    Returns
    -------
    float
        Medium correction k_med for all cells that are hit by the beam.

    """
    # Tabulated field side length in cm
    FSL_tab = [5, 10, 20, 25, 35]

    # Fetch kVp and HVL from data_norm
    kVp = data_norm.kVp[event]
    HVL = data_norm.HVL[event]

    # Calculate mean side length for all cells that are hit by the beam.
    # This field size dependance of k_med is negligible (<= 1%), therefore,
    # independep field size resolution is omitted for computational speed.
    FSL_mean = np.mean(np.sqrt(field_area))

    # Select the closest available tabulated field size length.
    FSL = min(FSL_tab, key=lambda x: abs(x - FSL_mean))

    # Connect to database
    [conn, c] = db_connect()

    # Fetch k_med = f(kVp, HVL) from database. This is table 2 in
    # [doi:10.1088/0031-9155/58/2/247]
    df = pd.read_sql_query("""SELECT kvp_kV, hvl_mmAl, field_side_length_cm,
                           mu_en_quotient FROM ks_table_concatenated""", conn)

    conn.commit()
    conn.close()

    # Fetch kVp entries from table
    KVP_data = df.loc[(df['field_side_length_cm'] == FSL), "kvp_kV"]
    # Select closest tabulated kVp (strongest dependence for k_med)
    KVP_round = min(KVP_data, key=lambda x: abs(x - kVp))

    # Fetch HVL entries from table
    HVL_data = df.loc[(df['field_side_length_cm'] == FSL) & (df['kvp_kV'] == KVP_round), "hvl_mmAl"]

    # Select closest tabulated HVL (second strongest dependence for k_med)
    HVL_round = min(HVL_data, key=lambda x: abs(x - HVL))

    # Fetch corresponding k_med
    k_med = float(df.loc[(df['hvl_mmAl'] == HVL_round) & (df['kvp_kV'] == KVP_round) &
                         (df['field_side_length_cm'] == FSL), "mu_en_quotient"])

    return k_med
