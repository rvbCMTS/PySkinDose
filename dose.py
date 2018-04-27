from __future__ import print_function
from corrections import *
from parse_data import *
from datetime import datetime as dt
import logging
import os
import pandas as pd
import pydicom as dicom
import settings


def skin_dose(file_path: str, print_result: bool=False, verbose: bool=False, save2db: bool=False):
    """ Import RDSR DICOM file specified in file_path. Parse the data. Calculate corrections. Calculate corrected skin
    dose. Return dataframe with parsed data and calculated skin dose

    :param file_path: Path to the RDSR DICOM file to parse
    :param print_result: Boolean specifying if result should be printed to console
    :param verbose:
    :param save2db:
    :return:
    """
    log = create_logger(log2console=verbose)

    if not isinstance(file_path, str) or not os.path.isfile(file_path):
        log.error('The specified file path is not a file {}'.format(file_path))
        raise IOError('The specified file path is not a file')

    # Import DICOM file
    log.debug('Import DICOM file')
    ds = dicom.read_file(file_path)

    # parse RDSR data in DICOM file ds, return PE (=Parsed Data) in pandas DataFrame.
    # Return device name as a string in model
    log.debug('Parse DICOM file')
    [PD, model] = parse(ds, log=log)

    # Send the parse data through the normalize script which adds generalized parameters
    log.debug('Normalize data parsed data')
    PD_norm = normalize(model, PD, ds)

    # Calculated and append correction factors to PD:
    #
    # calibration correction for vendor stated air kerma.
    log.debug('Calculate and add calibration correction')
    PD_norm['k_cal'] = k_cal(model, PD_norm)

    # Calculate inverse-square-law correction
    log.debug('Calculate and add inverse-square-law correction')
    PD_norm['k_isq'] = k_isq(PD_norm)

    # Calculate medium correction (f-factor, mu_en/rho)
    log.debug('Calculate and add medium correction')
    PD_norm['k_med'] = k_med(model, PD_norm)

    # Calculate backscatter correction
    log.debug('Calculate and add backscatter correction')
    PD_norm['k_bs'] = k_bs(model, PD_norm)

    # Calculate patient support table and pad correction
    log.debug('Calculate and add patient support correction')
    PD_norm['k_patientsupport'] = k_patient_support(model, PD_norm)

    # Calculate beam angle of incidence correction
    log.debug('Calculate and add beam angle incidence correction')
    PD_norm['k_angle'] = k_angle(model, PD_norm)

    # Calculated corrected skin dose by applying the multiplicative
    # correction factors to the reference air kerma k_a:
    # k_skin = k_a * prod(k_i) (by list comprehension)
    log.debug('Calculate and the corrected skin dose')
    PD_norm['DoseCorrected_Gy'] = [row.DoseRP_Gy * row.k_cal * row.k_isq * row.k_med * row.k_bs * row.k_angle for _, row
                                   in PD_norm.iterrows()]

    if print_result:
        # option for displaying data
        desired_width = 180
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.width', desired_width)

        print('')
        #########################
        # Presentation of results
        print(PD_norm)

        # Print dose report for single plane systems
        if PD_norm.AcquisitionPlane[0] in ['Single Plane']:
            print('\n')
            print('---------------------------------------')
            print('SINGLE PLANE {} DOSE REPORT:\n'.format(model))

            print('PROCEDURE INFORMATION:\n')
            print('Lab:               {}'.format(PD_norm.LabNumber[0]))
            print('Date:              {}'.format(ds.StudyDate))
            print('Duration:          {}'.format(PD_norm['DateTimeStarted'][PD_norm.index[-1]] -
                                                 PD_norm['DateTimeStarted'][PD_norm.index[0]]))

            print('K_air_IRP:         {} mGy'.format(round(1000 * sum(PD_norm.DoseRP_Gy), 1)))
            print('# fluoro events:   {}'.format(len(PD_norm[PD_norm['IrradiationEventType']
                                                     .str.contains('Fluoroscopy')])))

            print('# stat. acq:       {}'.format(len(PD_norm[PD_norm['IrradiationEventType']
                                                     .str.contains('Stationary Acquisition')])))

            print('# rot. acq:        {}'.format(len(PD_norm[PD_norm['IrradiationEventType']
                                                     .str.contains('Rotational Acquisition')])))
            print('\n')
            # Add more general info on procedure here if wanted

            print('ESD_max CALCULATION MODEL:\n')

            if len(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Rotational Acquisition')]) > 0:
                print('K_air_IRP (rotational acq): {} mGy \n(not included in ESD_max calculations)\n'
                      .format(round(1000 * sum(PD_norm[PD_norm['IrradiationEventType']
                                               .str.contains('Rotational Acquisition')].DoseRP_Gy), 2)))

            print('ESD_max (fluoroscopy):      {} mGy'.format(round(1000 * sum(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Fluoroscopy')].DoseCorrected_Gy), 2)))

            print('ESD_max (stationary acq):   {} mGy'.format(round(1000 * sum(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Stationary Acquisition')].DoseCorrected_Gy), 2)))

            print('ESD_max (Total):            {} mGy'.format(round(1000 * sum(PD_norm[~PD_norm
            ['IrradiationEventType'].str.contains('Rotational Acquisition')].DoseCorrected_Gy), 2)))

            print('---------------------------------------')
            print('\n')

        # Print dose report for bi-plane systems. NOTE: only alluraClarity bi-plane supported
        elif PD_norm.AcquisitionPlane[0] in ['Plane A', 'Plane B']:

            # Separate PD_norm into components for each X-ray tube
            PD_norm_A = PD_norm[PD_norm.AcquisitionPlane != 'Plane B']
            PD_norm_B = PD_norm[PD_norm.AcquisitionPlane != 'Plane A']

            print('\n')
            print('-----------------------------------')
            print('BI-PLANE {} DOSE REPORT:\n'.format(model))

            print('PROCEDURE INFORMATION:\n')
            print('Lab:               {}'.format(PD_norm.LabNumber[0]))
            print('Date:              {}'.format(ds.StudyDate))
            print('Duration:          {}'.format(PD_norm['DateTimeStarted'][PD_norm.index[-1]]
                                                 - PD_norm['DateTimeStarted'][PD_norm.index[0]]))

            print('K_air_IRP:         {} mGy'.format(round(1000 * sum(PD_norm.DoseRP_Gy), 1)))

            print('# fluoro events:   {}'.format(len(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Fluoroscopy')])))

            print('# stat. acq:       {}'.format(len(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Stationary Acquisition')])))

            print('# rot. acq:        {}'.format(len(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Rotational Acquisition')])))

            print('\n')
            # Add more general info on procedure here

            print('ESD_max CALCULATION MODEL:\n')

            # If PD_norm contains rotational acquisitions, print K_air_IRP (rotational separately)
            # NOTE Rotational acquisitions are not (yet) included in ESD_max calculations.
            if len(PD_norm[PD_norm
            ['IrradiationEventType'].str.contains('Rotational Acquisition')]) > 0:
                raise ValueError('RDSR contains Rotational Acquisition entries, which is not yet'
                                 'implemented for Allura Clarity.')

            print("PLANE A (FRONTAL):\n")

            print('K_air_IRP:                  {} mGy'.format(round(1000 * sum(PD_norm_A.DoseRP_Gy), 1)))

            print('ESD_max (fluoroscopy):      {} mGy'.format(round(1000 * sum(PD_norm_A[PD_norm_A
            ['IrradiationEventType'].str.contains('Fluoroscopy')].DoseCorrected_Gy), 2)))

            print('ESD_max (stationary acq):   {} mGy'.format(round(1000 * sum(PD_norm_A[PD_norm_A
            ['IrradiationEventType'].str.contains('Stationary Acquisition')].DoseCorrected_Gy), 2)))

            print('ESD_max (Total):            {} mGy\n'.format(round(1000 * sum(PD_norm_A[~PD_norm_A
            ['IrradiationEventType'].str.contains('Rotational Acquisition')].DoseCorrected_Gy), 2)))

            print("PLANE B (LATERAL):\n")

            print('K_air_IRP:                  {} mGy'.format(round(1000 * sum(PD_norm_B.DoseRP_Gy), 1)))

            print('ESD_max (fluoroscopy):      {} mGy'.format(round(1000 * sum(PD_norm_B[PD_norm_B
            ['IrradiationEventType'].str.contains('Fluoroscopy')].DoseCorrected_Gy), 2)))

            print('ESD_max (stationary acq):   {} mGy'.format(round(1000 * sum(PD_norm_B[PD_norm_B
            ['IrradiationEventType'].str.contains('Stationary Acquisition')].DoseCorrected_Gy), 2)))

            print('ESD_max (Total):            {} mGy\n'.format(round(1000 * sum(PD_norm_B[~PD_norm_B
            ['IrradiationEventType'].str.contains('Rotational Acquisition')].DoseCorrected_Gy), 2)))

            print('-----------------------------------')

        print('')

    return PD_norm


def create_logger(log2console):
    if not os.path.exists(settings.LOG_FOLDER):
        try:
            os.makedirs(settings.LOG_FOLDER)
        except OSError as e:
            print('Could not create the logging folder {}'.format(settings.LOG_FOLDER))

    logging.basicConfig(
        level=settings.LOG_LEVEL.upper(),
        format=('{"logtime": "%(asctime)s", "loglevel": "%(levelname)s", "process": "%(process)d", '
                '"function": "%(funcName)s", "filename": "%(filename)s", "lineno": "%(lineno)d", '
                '"message": "%(message)s"}'),
        datefmt='%Y-%m-%d %H:%M:S',
        filename=os.path.join(settings.LOG_FOLDER, '_'.join([dt.now().strftime('%Y%m'), 'pyskindose.log'])),
        filemode='w')

    logger = logging.getLogger('pyskindose')

    if log2console:
        ch = logging.StreamHandler()
        ch.setLevel(settings.LOG_LEVEL.upper())
        ch.setFormatter(logging.Formatter(
            ('logtime: %(asctime)s | level: %(levelname)s | filename: %(filename)s | function: %(funcName)s | '
             'line: %(lineno)d | message: %(message)s')
        ))
        logger.addHandler(ch)

    return logger
