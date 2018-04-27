import pandas as pd
import numpy as np
from datetime import datetime as dt
from db_connect import db_connect


def parse(ds, log=None):
    """ Parse DICOM-RDSR data, intended for PSD calculations from fluoroscopic procedures

    :param ds: RDSR file of type <class 'dicom.dataset.FileDataset'>. Contains 'Irradiation Event X-Ray Data'
    (structured report). Containing parameter to be used for patient specific post intervention PSD calculations.
    :param log: Logging instance
    :return:
    df: Table of type <class 'pandas.core.frame.DataFrame'>. Contains parsed irradiation event data.
    model: string containing 'Manufacturer Model Name'. To be used for machine specific corrections.
    """
    # Declare pandas DataFrame for storage of parsed RDSR data
    df = pd.DataFrame(columns=[])

    # Obtain 'Manufacturer Model Name'
    if log is not None:
        log.debug('Get manufacturer model name')
    model = ds.ManufacturerModelName \
        .replace(" ", "").replace("-", "").replace("(", "").replace(")", "").replace(".", "")
    # For each content in RDSR file
    for RDSR_content in ds.ContentSequence:
        # If content = irradiation event
        if RDSR_content.ConceptNameCodeSequence[0].CodeMeaning == 'Irradiation Event X-Ray Data':
            # Declare dictionary (to be assigned to df)
            df_dict = {}
            # For each content in 'Irradiation Event X-Ray Data'
            for xray_event_content in RDSR_content.ContentSequence:
                # Reformat 'Concept Name'
                tag = (xray_event_content.ConceptNameCodeSequence[0].CodeMeaning
                       .replace(" ", "")).replace("-", "").replace("(", "").replace(")", "").replace(".", "")
                # Save 'Concept Name' to dictionary and assign corresponding value.
                if 'ConceptCodeSequence' in xray_event_content:
                    if tag in df_dict.keys():
                        df_dict[tag] = [df_dict[tag], xray_event_content.ConceptCodeSequence[0].CodeMeaning]
                    else:
                        df_dict[tag] = xray_event_content.ConceptCodeSequence[0].CodeMeaning
                elif 'MeasuredValueSequence' in xray_event_content:
                    # If the content contains a 'Measured Value Sequence'
                    # Reformat 'Concept Name' to include unit of measurement
                    unit = xray_event_content.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[
                        0].CodeValue.replace(".", "")
                    tag = '_'.join([tag, unit])
                    if tag in df_dict.keys():
                        df_dict[tag] = [df_dict[tag], xray_event_content.MeasuredValueSequence[0].NumericValue]
                    else:
                        df_dict[tag] = xray_event_content.MeasuredValueSequence[0].NumericValue
                elif 'TextValue' in xray_event_content:
                    # This loop extracts detector size for static acquisitions, which is hidden in a 'Comment'
                    # for the siemens artis zee unit.
                    if tag == 'Comment':
                        comment = xray_event_content.TextValue.split('/')
                        if 'AcquisitionData' in comment[0]:
                            for index in comment:
                                if 'iiDiameter SRData' in index:
                                    df_dict['DetectorSize_mm'] = index.split('=')[1].replace('"', '')
                    elif tag in df_dict.keys():
                        df_dict[tag] = [df_dict[tag], xray_event_content.TextValue]
                    else:
                        df_dict[tag] = xray_event_content.TextValue
                elif 'DateTime' in xray_event_content:
                    if tag in df_dict.keys():
                        df_dict[tag] = [df_dict[tag], dt.strptime(str(round(float(xray_event_content.DateTime))),
                                                                  '%Y%m%d%H%M%S')]
                    else:
                        df_dict[tag] = dt.strptime(str(round(float(xray_event_content.DateTime))), '%Y%m%d%H%M%S')
                elif 'UID' in xray_event_content:
                    if tag in df_dict.keys():
                        df_dict[tag] = [df_dict[tag], xray_event_content.UID]
                    else:
                        df_dict[tag] = xray_event_content.UID
                # If the 'Irradiation Event X-Ray Data' contains subcontent
                elif 'ContentSequence' in xray_event_content:
                    # For each subcontent
                    for xray_event_subcontent in xray_event_content.ContentSequence:
                        # Reformat 'Concept Name'
                        tag = (xray_event_subcontent.ConceptNameCodeSequence[0].CodeMeaning.replace(
                            " ", "")).replace("-", "").replace("(", "").replace(")", "").replace(".", "")
                        # Save 'Concept Name' to dictionary and assign corresponding value
                        if 'ConceptCodeSequence' in xray_event_subcontent:
                            if tag in df_dict.keys():
                                df_dict[tag] = [df_dict[tag], xray_event_subcontent.ConceptCodeSequence[0].CodeMeaning]
                            else:
                                df_dict[tag] = xray_event_subcontent.ConceptCodeSequence[0].CodeMeaning
                        elif 'DateTime' in xray_event_subcontent:
                            if tag in df_dict.keys():
                                df_dict[tag] = [df_dict[tag], dt.strptime(str(round(float(xray_event_subcontent.
                                                                                          DateTime))), '%Y%m%d%H%M%S')]
                            else:
                                df_dict[tag] = dt.strptime(str(round(float(xray_event_subcontent.
                                                                           DateTime))), '%Y%m%d%H%M%S')
                        elif 'TextValue' in xray_event_subcontent:
                            if tag in df_dict.keys():
                                df_dict[tag] = [df_dict[tag], xray_event_subcontent.TextValue]
                            else:
                                df_dict[tag] = xray_event_subcontent.TextValue
                        elif 'UID' in xray_event_subcontent:
                            if tag in df_dict.keys():
                                df_dict[tag] = [df_dict[tag], xray_event_subcontent.UID]
                            else:
                                df_dict[tag] = xray_event_subcontent.UID
                        elif 'MeasuredValueSequence' in xray_event_subcontent:
                            # If the content contains a 'Measured Value Sequence'
                            # Reformat 'Concept Name' to include unit of measurement
                            unit = xray_event_subcontent.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[
                                0].CodeValue
                            tag = '_'.join([tag, unit])
                            if tag in df_dict.keys():
                                df_dict[tag] = [df_dict[tag],
                                                xray_event_subcontent.MeasuredValueSequence[0].NumericValue]
                            else:
                                df_dict[tag] = xray_event_subcontent.MeasuredValueSequence[0].NumericValue
                        # Assign None to 'Concept Name' if nothing relevant to parse in RDSR subcontent
                        else:
                            df_dict[tag] = None
                # Assign None to 'Concept Name' if nothing relevant to parse in RDSR content
                else:
                    df_dict[tag] = None
            # Append dictionary to DataFrame
            df = df.append(df_dict, ignore_index=True)
    # Return DataFrame containing parsed RDSR data
    if log is not None:
        log.debug('Finished parsing RDSR DICOM file')
    return df, model


def normalize(model, PD, ds, log=None):
    """ Add generalized parameters needed for dose calculation to the parsed data.

    :param
    PD: Table of type <class 'pandas.core.frame.DataFrame'>
    containing parsed irradiation event data.
    model: string containing 'Manufacturer Model Name'. To be used for machine specific corrections.
    :return:
    PD_norm: Table of type <class 'pandas.core.frame.DataFrame'>
    which in addition to the data in PD, also contains generalized parameters for dose calculations, which are:
    -PadThickness_mm
    -LabNumber (e.g: U106)
    -DistanceSourcetoIRP_mm
    -DistanceSourcetoTabletop_mm
    -DistanceSourcetoSkin_mm
    -SurfaceFieldArea_cm
    -AddedFiltration_mmAl
    -AddedFiltration_mmCu
    """

    PD_norm = PD

    # Establish database correction
    [conn, c] = db_connect()

    # Fetch pad thickness and lab number from database
    c.execute(("SELECT PadThickness_mm, Lab FROM device_info WHERE DeviceObserverSerialNumber = {}"
               .format(ds.ContentSequence[6].TextValue).replace("-", "")))

    query = c.fetchall()

    PadThickness_mm = query[0][0]
    LabNumber = query[0][1]

    # Add columns of Pad Thickness and "lab number (ex: U106) to PD_norm
    PD_norm['PadThickness_mm'] = PadThickness_mm
    PD_norm['LabNumber'] = LabNumber

    # Conduct generalize procedure for AlluraClarity systems
    if model == 'AlluraClarity':
        # Calculating distance source-to-IRP
        PD_norm['DistanceSourcetoIRP_mm'] = PD.DistanceSourcetoIsocenter_mm - 150

        # Calculating distance source-to-tabletop
        # based upon measurements conducted in lab. 601
        PD_norm['DistanceSourcetoTabletop_mm'] = PD.FinalTableHeightPosition_mm - 261

        # If single plan AlluraClarity system, assume all projections in PA mode
        if PD.AcquisitionPlane[0] in ['Single Plane']:

            # +0,5 * PadThickness_mm is the (estimated) depression of the pad when a patient lies on it
            PD_norm['DistanceSourcetoSkin_mm'] = PD_norm.DistanceSourcetoTabletop_mm + \
                                                 0.5 * PadThickness_mm
        # If bi-plane AlluraClarity system,
        # assume all Plane A projections in PA mode,
        # assume all Plane B projections in lateral mode,
        elif PD.AcquisitionPlane[0] in ['Plane A', 'Plane B']:

            DistanceSourcetoSkin_mm = []

            # For each pedal depression
            for depression in range(0, len(PD)):

                # If plane A (frontal)
                if PD.AcquisitionPlane[depression] == 'Plane A':

                    # Measurement of DistanceSourcetoTabletop_mm is conducted in lab 601.
                    # Needs to be verified in lab U104 (INR).
                    # + 110 mm is the distance from table to the bottom of the head cradle.
                    DistanceSourcetoSkin_mm.append(PD.DistanceSourcetoTabletop_mm[depression] + 110)

                # If plane B (lateral)
                elif PD.AcquisitionPlane[depression] == 'Plane B':

                    # Measurements conducted in INR lab, lateral position is assumed to be along the longitudinal axis.
                    # which is the most common placement.
                    # - 90 mm is the distance from the middle of the head cradle to the head surface (laterally)
                    DistanceSourcetoSkin_mm.append(PD.DistanceSourcetoIsocenter_mm[depression] - 90)

                else:
                    if log is not None:
                        log.error(('Unknown plane configuration ({}). '
                                   'Debug normalize(model, PD, ds) in parse_data.py').format(
                            PD.AcquisitionPlane[depression]
                        ))
                    raise ValueError('Unknown plane configuration. Debug normalize(model, PD, ds) in parse_data.py')

            # Append DistanceSourcetoSkin_mm to PD_norm
            PD_norm['DistanceSourcetoSkin_mm'] = DistanceSourcetoSkin_mm

        # Calculate collimated field area at 'DistanceSourcetoSkin' to be used for input to correction factors
        # 0.01 is mm^2 to cm^2 conversion factor

        PD_norm['SurfaceFieldArea_cm'] = np.sqrt(
            0.01 * (PD.BottomShutter_mm + PD.TopShutter_mm) *
            (PD.LeftShutter_mm + PD.RightShutter_mm)) * (PD_norm.DistanceSourcetoSkin_mm / 1000)

        # Calculated added filtration
        AddedFiltration_mmCu = []
        AddedFiltration_mmAl = []

        # For each pedal depression
        for depression in range(0, len(PD_norm)):
            # If no filter is used:
            if PD_norm.XRayFilterType[depression][0] == 'No Filter':
                # Set added filtration (Cu and Al) to zero.
                AddedFiltration_mmCu.append(0)
                AddedFiltration_mmAl.append(0)

            # Else if different maximum- and minimum filtration
            elif PD_norm.XRayFilterThicknessMaximum_mm[depression] != PD_norm.XRayFilterThicknessMinimum_mm[depression]:
                if log is not None:
                    log.error(('RDSR contains events with different maximum- and minimum filter thickness, '
                               'which is not (yet) implemented in this program.'))
                # Abort and raise error, since not different maximum-and minimum filter thickness is not supported.
                raise ValueError(('RDSR contains events with different maximum- and minimum filter thickness, '
                                  'which is not (yet) implemented in this program.'))

            # Append filter thickness mmAl and mmCu to PD_norm
            elif PD.XRayFilterMaterial[depression][0] == 'Copper or Copper compound' and \
                    PD.XRayFilterMaterial[depression][1] == 'Aluminum or Aluminum compound':

                AddedFiltration_mmCu.append(float(PD.XRayFilterThicknessMaximum_mm[depression][0]))
                AddedFiltration_mmAl.append(float(PD.XRayFilterThicknessMaximum_mm[depression][1]))

            # Raise error if unknown filter combination
            else:
                if log is not None:
                    log.error(('RDSR contains unknown filter combination ({}). '
                               'Debug normalize(model, PD, ds) in parse_data.py').format(
                        PD.XRayFilterMaterial[depression][0]))
                raise ValueError(('RDSR contains unknown filter combination ({}). '
                                  'Debug normalize(model, PD, ds) in parse_data.py').format(
                    PD.XRayFilterMaterial[depression][0]))

        # Append filtration mmCu & mmAl to PD_norm
        PD_norm['AddedFiltration_mmCu'] = AddedFiltration_mmCu
        PD_norm['AddedFiltration_mmAl'] = AddedFiltration_mmAl

    # Conduct generalize procedure for AXIOMArtis systems
    elif model == 'AXIOMArtis':

        # If single plan AXIOMArtis system, assume all projections in PA mode
        if PD.AcquisitionPlane[0] in ['Single Plane']:

            # Calculate distance source-to-IRP
            PD_norm['DistanceSourcetoIRP_mm'] = PD.DistanceSourcetoIsocenter_mm - 150

            # Calculate distance source-to-tabletop
            # based upon measurements conducted in lab. 106
            PD_norm['DistanceSourcetoTabletop_mm'] = -PD.TableHeightPosition_mm + 775.4

            # Calculate distance source-to-skin
            # +0,5 * PadThickness_mm is the (estimated) depression of the pad when a patient lies on it
            PD_norm['DistanceSourcetoSkin_mm'] = PD_norm.DistanceSourcetoTabletop_mm + \
                                                 0.5 * PadThickness_mm

            # Calculate collimated field area at 'DistanceSourcetoSkin'
            # 10000 is m^2 -> cm^2 conversion
            PD_norm['SurfaceFieldArea_cm'] = np.sqrt(10000 * PD.CollimatedFieldArea_m2) * \
                                             (PD_norm.DistanceSourcetoSkin_mm /
                                              PD.DistanceSourcetoDetector_mm)

        elif PD.AcquisitionPlane[0] in ['Plane A', 'Plane B']:
            if log is not None:
                log.error('RDSR contains AXIOMArtis bi-plane information. Which is not supported')
            raise ValueError('RDSR contains AXIOMArtis bi-plane information. Which is not supported')

        # Calculating added filtration
        AddedFiltration_mmCu = []

        # For each pedal depression
        for depression in range(0, len(PD_norm)):

            # If no filter used, set 0 mm to AddedFiltration_mmCu
            if PD_norm.XRayFilterType[depression] == 'No Filter':
                AddedFiltration_mmCu.append(0)

            # Else if different maximum- and minimum filtration
            elif PD_norm.XRayFilterThicknessMaximum_mm[depression] != PD_norm.XRayFilterThicknessMinimum_mm[depression]:
                if log is not None:
                    log.error(('RDSR contains events with different maximum- and minimum filter thickness, '
                              'which is not yet implemented in this program.'))
                # Abort and raise error, since not different maximum-and minimum filter thickness is not supported.
                raise ValueError(('RDSR contains events with different maximum- and minimum filter thickness, '
                                  'which is not yet implemented in this program.'))
            else:
                AddedFiltration_mmCu.append(PD_norm.XRayFilterThicknessMaximum_mm[depression])

        # Append filtration mmCu & mmAl to PD_norm
        # (Always 0 mmAl for AXIOMArtis systems)
        PD_norm['AddedFiltration_mmCu'] = AddedFiltration_mmCu
        PD_norm['AddedFiltration_mmAl'] = float(0)

    # If neither AlluraClarity or AXIOMArtis, raise error since not supported
    else:
        if log is not None:
            log.error(('Device model {} are not yet supported by this function. Accepted device models are '
                       'Allura Clarity and AXIOM-Artis.').format(model))
        raise ValueError(('Device model {} are not yet supported by this function. Accepted device models are '
                          'Allura Clarity and AXIOM-Artis.').format(model))

    # Close database correction
    conn.commit()
    conn.close()

    return PD_norm
