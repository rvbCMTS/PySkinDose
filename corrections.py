import numpy as np
import pandas as pd
from db_connect import db_connect
from scipy.interpolate import CubicSpline
from typing import List


def calculate_k_isq(source: np.array, cells: np.array, dref: float) -> np.array:
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
        reference distance source to IRP, i.e. the distance where the IRP air
        kerma is stated.

    Returns
    -------
    np.array
        Inverse-square law correction for all cells that are hit by the beam.

    """
    # Scale X-ray fluence according to the inverse square law
    k_isq = [np.sqrt(dref / np.linalg.norm((cell - source))) for cell in cells]

    return np.asarray(k_isq)


def calculate_k_bs(data_norm: pd.DataFrame, field_area: List[float], event: int) -> np.array:
    """Calculate backscatter correction.

    This function calculates and appends the backscatter correction factor
    for all skin cells that are hit by the X-ray beam in an event. The function
    uses the non-linear interpolation method presented by Benmakhlouf et al. in
    the article "Influence of phantom thickness and material on the backscatter
    factors for diagnostic x-ray beam dosimetry",
    [doi:10.1088/0031-9155/58/2/247]

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
    np.array
        backscatter correction k_bs for all cells that are hit by the beam.

    """
    # Tabulated field side length in cm
    FSL_tab = [5, 10, 20, 25, 35]

    #
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

    k_bs = []

    # Fetch kVp and HVL from data_norm
    kVp = data_norm.kVp
    HVL = data_norm.HVL

    # For every skin cell
    for cell in range(len(field_area)):

        # calculate k_bs for field side length [5, 10, 20, 25, 35] cm
        # This is eq. (8) in doi:10.1088/0031-9155/58/2/247.
        corr = (c[0, :] + c[1, :] * kVp[event] + c[2, :] * np.square(kVp[event])) + \
               (c[3, :] + c[4, :] * kVp[event] + c[5, :] * np.square(kVp[event])) * HVL[event] + \
               (c[6, :] + c[7, :] * kVp[event] + c[8, :] * np.square(kVp[event])) * np.square(HVL[event])

        # Conduct cubic spline interpolation to furter improve the resolution.
        interp = CubicSpline(FSL_tab, corr)

        # interpolate to find k_bs for the actual field size in data_norm.
        k_bs.append(interp(np.sqrt(field_area[cell])))

    return np.asarray(k_bs)


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
        Medium correction k_k_med for all cells that are hit by the beam.

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
    # Select closest tabulated kVp (stongest dependance for k_med)
    KVP_round = min(KVP_data, key=lambda x: abs(x - kVp))

    # Fetch HVL entries from table
    HVL_data = df.loc[(df['field_side_length_cm'] == FSL) & (df['kvp_kV'] == KVP_round), "hvl_mmAl"]

    # Select closest tabulated HVL (second stongest dependance for k_med)
    HVL_round = min(HVL_data, key=lambda x: abs(x - HVL))

    # Fetch corresponding k_med
    corr = df.loc[(df['hvl_mmAl'] == HVL_round) & (df['kvp_kV'] == KVP_round) &
                  (df['field_side_length_cm'] == 20), "mu_en_quotient"]

    k_med = float(corr)

    return k_med


# # TBR
# # def k_bs(model, PD_norm, verbose=False, log=None):
#     """Calculates and appends correction for backscattered photons
#     (from within the body of the patient to the skin entrance surface).
#     :param
#     PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
#     containing parsed irradiation event data, including generalized parameters
#     for distances and field sizes etc
#     :return:
#     Backscatter correction factor B_air(Q) for each pedal depression in PD_norm
#     """

#     output = []

#     # Establish database correction
#     [conn, c] = db_connect()

#     # For each pedal depression
#     for depression in range(0, len(PD_norm)):

#         # Print correction log
#         if verbose:
#             print('\n')
#             print('B-correction nr:    {}'.format(depression + 1))
#             print('model:              {}'.format(model))
#             print('Acq plane:          {}'.format(PD_norm.AcquisitionPlane[depression]))
#             print('Cu:                 {} mm'.format(PD_norm.AddedFiltration_mmCu[depression]))
#             print('Al:                 {} mm'.format(PD_norm.AddedFiltration_mmAl[depression]))
#             print('kVp:                {} kV'.format(PD_norm.KVP_kV[depression]))
#             print('FieldSize:          {} cm^2'.format(round(PD_norm.SurfaceFieldArea_cm[depression], 2)))

#         # Try to fetch k_backscatter from database:
#         try:

#             # Fetch HVL_mmAl from database
#             c.execute(("SELECT HVL_mmAl FROM HVL_simulated WHERE "
#                        "AddedFiltration_mmAl = ? AND "
#                        "AddedFiltration_mmCu = ? AND "
#                        "DeviceModel = ? AND "
#                        "AcquisitionPlane = ? AND "
#                        "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM HVL_simulated)"),
#                       (PD_norm.AddedFiltration_mmAl[depression],
#                        PD_norm.AddedFiltration_mmCu[depression],
#                        model,
#                        PD_norm.AcquisitionPlane[depression],
#                        PD_norm.KVP_kV[depression],
#                        PD_norm.KVP_kV[depression]))

#             # Save HVL
#             ActualHVL_mmAl = round(c.fetchall()[0][0], 4)
#             # Print HVL to correction log
#             if verbose:
#                 print('HVL from query:     {} mmAl'.format(ActualHVL_mmAl))

#             # Fetch k_backscatter from database
#             c.execute(("SELECT Backscatter FROM B_interpolated WHERE "
#                        "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM B_interpolated) AND "
#                        "abs(FieldSize_cm - ?) = (SELECT min(abs(FieldSize_cm - ?)) FROM B_interpolated) "
#                        "ORDER BY abs(HVL_mmAl - ?) ASC LIMIT 1 "),
#                         (PD_norm.KVP_kV[depression],
#                          PD_norm.KVP_kV[depression],
#                          PD_norm.SurfaceFieldArea_cm[depression],
#                          PD_norm.SurfaceFieldArea_cm[depression],
#                          ActualHVL_mmAl))

#             # Save k_backscatter
#             backscatter = round(c.fetchall()[0][0], 4)
#             # Print k_backscatter to correction log
#             if verbose:
#                 print('k_bs from query:    {}'.format(backscatter))
#             output.append(backscatter)

#         # If not able to fetch k_backscatter, raise error and set k_backscatter = 1
#         except IndexError:
#             output.append(1)
#             if log is not None:
#                 log.warning('No backscatter correction found. Therefore, k_bs = 1.')
#             else:
#                 print('Warning: No backscatter correction found. Therefore, k_bs = 1'
#                       'Troubleshoot k_bs(model, PD_norm) in corrections.py')

#     # Close database correction
#     conn.commit()
#     conn.close()

#     return output


# # TBR
# # def k_patient_support(model, PD_norm):
#     """Calculates and appends correction for attenuation and forward scatter in patient support table and pad.
#     :param
#     PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
#     containing parsed irradiation event data, including generalized parameters
#     for distances and field sizes etc.
#     :return:
#     Table and pad transmission factor k_(T+P) for each pedal depression in PD_norm. No angulation
#     dependence is yet implemented, therefore, all irradiations are assumed in PA projection, where the table+tap blocks
#     the beam path.
#     """

#     output = []

#     # Establish database correction
#     [conn, c] = db_connect()

#     # For each pedal depression
#     for depression in range(0, len(PD_norm)):

#         # Print correction log
#         print('\n')
#         print('T+P correction nr:  {}'.format(depression + 1))
#         print('model:              {}'.format(model))
#         print('Acq plane:          {}'.format(PD_norm.AcquisitionPlane[depression]))
#         print('Cu:                 {} mm'.format(PD_norm.AddedFiltration_mmCu[depression]))
#         print('Al:                 {} mm'.format(PD_norm.AddedFiltration_mmAl[depression]))
#         print('kVp:                {} kV'.format(PD_norm.KVP_kV[depression]))
#         print('FieldSize:          {} cm^2'.format(round(PD_norm.SurfaceFieldArea_cm[depression], 2)))

#         # Try to fetch k_(T+P) from database:
#         try:

#             # Fetch k_(T+P) from database
#             c.execute(("SELECT k_patient_support FROM patient_support_transmission WHERE "
#                        "DeviceModel = ? AND "
#                        "AcquisitionPlane = ? AND "
#                        "AddedFiltration_mmAl = ? AND "
#                        "AddedFiltration_mmCu = ? AND "
#                        "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM HVL_simulated)"),
#                        (model,
#                         PD_norm.AcquisitionPlane[depression],
#                         PD_norm.AddedFiltration_mmAl[depression],
#                         PD_norm.AddedFiltration_mmCu[depression],
#                         PD_norm.KVP_kV[depression],
#                         PD_norm.KVP_kV[depression]))

#             patient_support = c.fetchall()[0][0]

#             # Save k_(T+P)
#             output.append(patient_support)

#             # Print k_(T+P) to correction log
#             print('k_(T+P):            {}'.format(patient_support))

#         # If not able to fetch k_(T+P), raise error and set k_(T+P) = 1
#         except IndexError:

#             output.append(1)
#             print('Warning: No patient support correction found. Therefore, k_patient_support = 1 '
#                   'Troubleshoot k_patient_support(model, PD_norm) in corrections.py')

#     # Close database correction
#     conn.commit()
#     conn.close()

#     return output

# # TBR
# # def k_angle(model, PD_norm):
#     """Calculates and appends correction for increased path length through the patient support table and pad
#     when oblique angles are used. (Primary- and secondary angle not equal to 0 deg).
#     :param
#     PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
#     containing parsed irradiation event data, including generalized parameters for distances and field sizes
#     :return:
#     angle correction factor k_(alpha, beta) for each pedal depression in PD_norm.
#     """

#     output = []

#     # For each pedal depression
#     for i in range(0, len(PD_norm)):

#         # Print correction log
#         print('\n')
#         print('ang correction nr: {}'.format(i + 1))
#         print('model:             {}'.format(model))
#         print('Acq plane:         {}'.format(PD_norm.AcquisitionPlane[i]))
#         print('Primary angle:     {} deg'.format(PD_norm.PositionerPrimaryAngle_deg[i]))
#         print('Secondary angle:   {} deg'.format(PD_norm.PositionerSecondaryAngle_deg[i]))
#         print('kVp:               {} kV'.format(PD_norm.KVP_kV[i]))

#         # Set k_angle = 1, since this correction is not yet implemented.
#         output.append(1)
#         print('\nWarning: No oblique transmission \ncorrection implemented. -> k_angle = 1')

#     return output
