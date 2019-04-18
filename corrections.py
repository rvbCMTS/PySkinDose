import numpy as np
import pandas as pd
from db_connect import db_connect
from typing import List


def k_isq(source: np.array, cells: np.array, dref: float) -> List[np.float64]:
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
    List[np.float64]
        Inverse-square law correction for all cells that are hit by the beam

    """
    # Scale X-ray fluence according to the inverse square law
    k_isq = [np.sqrt(dref / np.linalg.norm((cell - source))) for cell in cells]

    return k_isq


def k_med_new(data_norm: pd.DataFrame, event: int) -> None:

    print('\n')
    print('med-correction nr:  {}'.format(event + 1))
    print('model:              {}'.format(data_norm.model[event]))
    print('Cu:                 {} mm'.format(data_norm.filter_thickness_Cu[event]))
    print('Al:                 {} mm'.format(data_norm.filter_thickness_Al[event]))
    print('kVp:                {} kV'.format(data_norm.kVp[event]))
    print('FieldSize:          {} cm^2'.format(round(data_norm.FS_lat[event]*data_norm.FS_long[event], 1)))




# WIP
def k_med(data_norm: pd.DataFrame) -> np.array:
    """Calculate the medium correction factor.

    This function corrects the medium in the reference point from air to
    water so that K_air -> K_water. This is done  because water is more similar
    to skin tissue then air in terms of X-ray dose absorption. This is
    conducted by multiplication of the the medium correction factor
    k_med = (mu_en/rho)_water/(mu_en/rho)_air, which is the quotient
    of mass energy absorption coefficient water to air.

    Parameters
    ----------
    data_norm : pd.DataFrame
        [description]

    Returns
    -------
    np.array
        Array of medium correc

    """
    output = []

    # Establish database correction
    [conn, c] = db_connect()

    # For each pedal depression
    for depression in range(0, len(PD_norm)):

        # Print correction log
        print('\n')
        print('med-correction nr:  {}'.format(depression+1))
        print('model:              {}'.format(model))
        print('Acq plane:          {}'.format(PD_norm.AcquisitionPlane[depression]))
        print('Cu:                 {} mm'.format(PD_norm.AddedFiltration_mmCu[depression]))
        print('Al:                 {} mm'.format(PD_norm.AddedFiltration_mmAl[depression]))
        print('kVp:                {} kV'.format(PD_norm.KVP_kV[depression]))
        print('FieldSize:          {} cm^2'.format(round(PD_norm.SurfaceFieldArea_cm[depression], 1)))

        # Try to fetch k_med from database:
        try:

            # Fetch HVL_mmAl from database
            c.execute(("SELECT HVL_mmAl FROM HVL_simulated WHERE "
                       "AddedFiltration_mmAl = ? AND "
                       "AddedFiltration_mmCu = ? AND "
                       "DeviceModel = ? AND "
                       "AcquisitionPlane = ? AND "
                       "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM HVL_simulated)"),
                      (PD_norm.AddedFiltration_mmAl[depression],
                       PD_norm.AddedFiltration_mmCu[depression],
                       model,
                       PD_norm.AcquisitionPlane[depression],
                       PD_norm.KVP_kV[depression],
                       PD_norm.KVP_kV[depression]))

            # Save HVL
            ActualHVL_mmAl = round(c.fetchall()[0][0], 4)
            # Print HVL to correction log
            print('HVL from query:     {} mmAl'.format(ActualHVL_mmAl))

            # Fetch k_med from database
            c.execute(("SELECT UdivRho FROM u_interpolated WHERE "
                       "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM u_interpolated) AND "
                       "abs(FieldSize_cm - ?) = (SELECT min(abs(FieldSize_cm - ?)) FROM u_interpolated) "
                       "ORDER BY abs(HVL_mmAl - ?) ASC LIMIT 1 "),
                      (PD_norm.KVP_kV[depression],
                       PD_norm.KVP_kV[depression],
                       PD_norm.SurfaceFieldArea_cm[depression],
                       PD_norm.SurfaceFieldArea_cm[depression],
                       ActualHVL_mmAl))

            # Save k_med
            u = round(c.fetchall()[0][0], 4)
            # Print k_med to correction log
            print('k_med from query:   {}'.format(u))
            output.append(u)

        # If not able to fetch k_med, raise error and set k_med = 1
        except IndexError as e:
            if log is not None:
                log.warning('No medium correction found. Therefore, k_med = 1. Troubleshoot k_med(model, PD_norm)')
            else:
                print('Warning: No medium correction found. Therefore, k_med = 1'
                      'Troubleshoot k_med(model, PD_norm) in corrections.py')
            output.append(1)

    # Close database correction
    conn.commit()
    conn.close()

    return output


def k_bs(model, PD_norm, verbose=False, log=None):
    """Calculates and appends correction for backscattered photons
    (from within the body of the patient to the skin entrance surface).
    :param
    PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
    containing parsed irradiation event data, including generalized parameters
    for distances and field sizes etc
    :return:
    Backscatter correction factor B_air(Q) for each pedal depression in PD_norm
    """

    output = []

    # Establish database correction
    [conn, c] = db_connect()

    # For each pedal depression
    for depression in range(0, len(PD_norm)):

        # Print correction log
        if verbose:
            print('\n')
            print('B-correction nr:    {}'.format(depression + 1))
            print('model:              {}'.format(model))
            print('Acq plane:          {}'.format(PD_norm.AcquisitionPlane[depression]))
            print('Cu:                 {} mm'.format(PD_norm.AddedFiltration_mmCu[depression]))
            print('Al:                 {} mm'.format(PD_norm.AddedFiltration_mmAl[depression]))
            print('kVp:                {} kV'.format(PD_norm.KVP_kV[depression]))
            print('FieldSize:          {} cm^2'.format(round(PD_norm.SurfaceFieldArea_cm[depression], 2)))

        # Try to fetch k_backscatter from database:
        try:

            # Fetch HVL_mmAl from database
            c.execute(("SELECT HVL_mmAl FROM HVL_simulated WHERE "
                       "AddedFiltration_mmAl = ? AND "
                       "AddedFiltration_mmCu = ? AND "
                       "DeviceModel = ? AND "
                       "AcquisitionPlane = ? AND "
                       "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM HVL_simulated)"),
                      (PD_norm.AddedFiltration_mmAl[depression],
                       PD_norm.AddedFiltration_mmCu[depression],
                       model,
                       PD_norm.AcquisitionPlane[depression],
                       PD_norm.KVP_kV[depression],
                       PD_norm.KVP_kV[depression]))

            # Save HVL
            ActualHVL_mmAl = round(c.fetchall()[0][0], 4)
            # Print HVL to correction log
            if verbose:
                print('HVL from query:     {} mmAl'.format(ActualHVL_mmAl))

            # Fetch k_backscatter from database
            c.execute(("SELECT Backscatter FROM B_interpolated WHERE "
                       "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM B_interpolated) AND "
                       "abs(FieldSize_cm - ?) = (SELECT min(abs(FieldSize_cm - ?)) FROM B_interpolated) "
                       "ORDER BY abs(HVL_mmAl - ?) ASC LIMIT 1 "),
                        (PD_norm.KVP_kV[depression],
                         PD_norm.KVP_kV[depression],
                         PD_norm.SurfaceFieldArea_cm[depression],
                         PD_norm.SurfaceFieldArea_cm[depression],
                         ActualHVL_mmAl))

            # Save k_backscatter
            backscatter = round(c.fetchall()[0][0], 4)
            # Print k_backscatter to correction log
            if verbose:
                print('k_bs from query:    {}'.format(backscatter))
            output.append(backscatter)

        # If not able to fetch k_backscatter, raise error and set k_backscatter = 1
        except IndexError:
            output.append(1)
            if log is not None:
                log.warning('No backscatter correction found. Therefore, k_bs = 1.')
            else:
                print('Warning: No backscatter correction found. Therefore, k_bs = 1'
                      'Troubleshoot k_bs(model, PD_norm) in corrections.py')

    # Close database correction
    conn.commit()
    conn.close()

    return output


def k_patient_support(model, PD_norm):
    """Calculates and appends correction for attenuation and forward scatter in patient support table and pad.
    :param
    PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
    containing parsed irradiation event data, including generalized parameters
    for distances and field sizes etc.
    :return:
    Table and pad transmission factor k_(T+P) for each pedal depression in PD_norm. No angulation
    dependence is yet implemented, therefore, all irradiations are assumed in PA projection, where the table+tap blocks
    the beam path.
    """

    output = []

    # Establish database correction
    [conn, c] = db_connect()

    # For each pedal depression
    for depression in range(0, len(PD_norm)):

        # Print correction log
        print('\n')
        print('T+P correction nr:  {}'.format(depression + 1))
        print('model:              {}'.format(model))
        print('Acq plane:          {}'.format(PD_norm.AcquisitionPlane[depression]))
        print('Cu:                 {} mm'.format(PD_norm.AddedFiltration_mmCu[depression]))
        print('Al:                 {} mm'.format(PD_norm.AddedFiltration_mmAl[depression]))
        print('kVp:                {} kV'.format(PD_norm.KVP_kV[depression]))
        print('FieldSize:          {} cm^2'.format(round(PD_norm.SurfaceFieldArea_cm[depression], 2)))

        # Try to fetch k_(T+P) from database:
        try:

            # Fetch k_(T+P) from database
            c.execute(("SELECT k_patient_support FROM patient_support_transmission WHERE "
                       "DeviceModel = ? AND "
                       "AcquisitionPlane = ? AND "
                       "AddedFiltration_mmAl = ? AND "
                       "AddedFiltration_mmCu = ? AND "
                       "abs(kVp_kV - ?) = (SELECT min(abs(kVp_kV - ?)) FROM HVL_simulated)"),
                       (model,
                        PD_norm.AcquisitionPlane[depression],
                        PD_norm.AddedFiltration_mmAl[depression],
                        PD_norm.AddedFiltration_mmCu[depression],
                        PD_norm.KVP_kV[depression],
                        PD_norm.KVP_kV[depression]))

            patient_support = c.fetchall()[0][0]

            # Save k_(T+P)
            output.append(patient_support)

            # Print k_(T+P) to correction log
            print('k_(T+P):            {}'.format(patient_support))

        # If not able to fetch k_(T+P), raise error and set k_(T+P) = 1
        except IndexError:

            output.append(1)
            print('Warning: No patient support correction found. Therefore, k_patient_support = 1 '
                  'Troubleshoot k_patient_support(model, PD_norm) in corrections.py')

    # Close database correction
    conn.commit()
    conn.close()

    return output


def k_angle(model, PD_norm):
    """Calculates and appends correction for increased path length through the patient support table and pad
    when oblique angles are used. (Primary- and secondary angle not equal to 0 deg).
    :param
    PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
    containing parsed irradiation event data, including generalized parameters for distances and field sizes
    :return:
    angle correction factor k_(alpha, beta) for each pedal depression in PD_norm.
    """

    output = []

    # For each pedal depression
    for i in range(0, len(PD_norm)):

        # Print correction log
        print('\n')
        print('ang correction nr: {}'.format(i + 1))
        print('model:             {}'.format(model))
        print('Acq plane:         {}'.format(PD_norm.AcquisitionPlane[i]))
        print('Primary angle:     {} deg'.format(PD_norm.PositionerPrimaryAngle_deg[i]))
        print('Secondary angle:   {} deg'.format(PD_norm.PositionerSecondaryAngle_deg[i]))
        print('kVp:               {} kV'.format(PD_norm.KVP_kV[i]))

        # Set k_angle = 1, since this correction is not yet implemented.
        output.append(1)
        print('\nWarning: No oblique transmission \ncorrection implemented. -> k_angle = 1')

    return output
