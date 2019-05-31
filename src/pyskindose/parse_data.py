from datetime import datetime as dt
import numpy as np
import pandas as pd
import pydicom


def rdsr_parser(data_raw: pydicom.FileDataset) -> pd.DataFrame:
    """Parse event data from radiation dose structure reports (RDSR).

    Parameters
    ----------
    data_raw : pydicom.FileDataset
        RDSR file from fluoroscopic device, opened with package pydicom.

    Returns
    -------
    pd.DataFrame
        Parsed RDSR data from all irradiation events in the RDSR input file

    """
    # Declare pandas DataFrame for storage of parsed RDSR data
    data_parsed = pd.DataFrame(columns=[])

    # For each content in RDSR file
    for RDSR_content in data_raw.ContentSequence:

        # If content = irradiation event
        if RDSR_content.ConceptNameCodeSequence[0].CodeMeaning\
                == 'Irradiation Event X-Ray Data':

            # Declare temporary dictionary
            data_parsed_dict = dict()

            # Save manufacturer model name
            data_parsed_dict["model"] = data_raw.ManufacturerModelName\
                .replace(" ", "").replace("-", "").replace("(", "")\
                .replace(")", "").replace(".", "")

            # For each content in 'Irradiation Event X-Ray Data'
            for xray_event_content in RDSR_content.ContentSequence:
                # Reformat 'Concept Name'
                tag = (xray_event_content.ConceptNameCodeSequence[0]
                                         .CodeMeaning.replace(" ", ""))\
                    .replace("-", "")\
                    .replace("(", "")\
                    .replace(")", "")\
                    .replace(".", "")

                # Save 'Concept Name' to dictionary, assign corresponding value
                if 'ConceptCodeSequence' in xray_event_content:
                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] =\
                            [data_parsed_dict[tag],
                                xray_event_content.ConceptCodeSequence
                                [0].CodeMeaning]
                    else:
                        data_parsed_dict[tag] = xray_event_content\
                            .ConceptCodeSequence[0].CodeMeaning

                elif 'MeasuredValueSequence' in xray_event_content:
                    # If the content contains a 'Measured Value Sequence'
                    # Reformat 'Concept Name' to include unit of measurement
                    unit = xray_event_content.MeasuredValueSequence[0]\
                        .MeasurementUnitsCodeSequence[0]\
                        .CodeValue.replace(".", "")

                    tag = '_'.join([tag, unit])

                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] =\
                            [data_parsed_dict[tag],
                                xray_event_content.MeasuredValueSequence[0].
                                NumericValue]

                    else:
                        data_parsed_dict[tag] = xray_event_content\
                            .MeasuredValueSequence[0].NumericValue

                elif 'TextValue' in xray_event_content:

                    # This loop extracts detector size for static acquisitions,
                    # which is given as a 'Comment' for siemens artis zee units
                    if tag == 'Comment':
                        comment = xray_event_content.TextValue.split('/')
                        if 'AcquisitionData' in comment[0]:
                            for index in comment:
                                if 'iiDiameter SRData' in index:
                                    data_parsed_dict['DetectorSize_mm']\
                                        = index.split('=')[1].replace('"', '')

                    elif tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] =\
                            [data_parsed_dict[tag],
                                xray_event_content.TextValue]
                    else:
                        data_parsed_dict[tag] = xray_event_content.TextValue

                elif 'DateTime' in xray_event_content:
                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] =\
                            [data_parsed_dict[tag],
                                dt.strptime(str(round(float(
                                            xray_event_content.DateTime))),
                                            '%Y%m%d%H%M%S')]
                    else:
                        data_parsed_dict[tag] = dt.strptime(str(round(float(
                            xray_event_content.DateTime))), '%Y%m%d%H%M%S')

                elif 'UID' in xray_event_content:
                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] =\
                            [data_parsed_dict[tag], xray_event_content.UID]
                    else:
                        data_parsed_dict[tag] = xray_event_content.UID

                # If the 'Irradiation Event X-Ray Data' contains subcontent
                elif 'ContentSequence' in xray_event_content:
                    # For each subcontent
                    for xray_event_subcontent in xray_event_content.\
                            ContentSequence:
                        # Reformat 'Concept Name'
                        tag = (xray_event_subcontent.ConceptNameCodeSequence[0].CodeMeaning.replace(" ", "")).replace("-", "").replace("(", "").replace(")", "").replace(".", "")

                        # Save 'Concept Name' to dictionary and assign
                        # corresponding value
                        if 'ConceptCodeSequence' in xray_event_subcontent:
                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] =\
                                    [data_parsed_dict[tag],
                                        xray_event_subcontent
                                        .ConceptCodeSequence[0]
                                        .CodeMeaning]
                            else:
                                data_parsed_dict[tag] = xray_event_subcontent.\
                                    ConceptCodeSequence[0].CodeMeaning

                        elif 'DateTime' in xray_event_subcontent:
                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] =\
                                    [data_parsed_dict[tag],
                                        dt.strptime(str(round(float(
                                            xray_event_subcontent
                                            .DateTime))),
                                            '%Y%m%d%H%M%S')]
                            else:
                                data_parsed_dict[tag] =\
                                    dt.strptime(str(round(float(
                                        xray_event_subcontent.DateTime))),
                                        '%Y%m%d%H%M%S')

                        elif 'TextValue' in xray_event_subcontent:

                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] =\
                                    [data_parsed_dict[tag],
                                        xray_event_subcontent.TextValue]

                            else:
                                data_parsed_dict[tag] =\
                                    xray_event_subcontent.TextValue

                        elif 'UID' in xray_event_subcontent:
                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] =\
                                    [data_parsed_dict[tag],
                                        xray_event_subcontent.UID]
                            else:
                                data_parsed_dict[tag] =\
                                    xray_event_subcontent.UID
                        elif 'MeasuredValueSequence' in xray_event_subcontent:
                            # Reformat 'Concept Name' to include unit of
                            # measurement
                            unit = xray_event_subcontent\
                                .MeasuredValueSequence[0]\
                                .MeasurementUnitsCodeSequence[0].CodeValue

                            tag = '_'.join([tag, unit])

                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] =\
                                    data_parsed_dict[tag],
                                xray_event_subcontent.MeasuredValueSequence[0]\
                                                     .NumericValue
                            else:
                                data_parsed_dict[tag] =\
                                    xray_event_subcontent.\
                                    MeasuredValueSequence[0].NumericValue

                        # Assign None to 'Concept Name' if nothing relevant to
                        # parse in RDSR subcontent
                        else:
                            data_parsed_dict[tag] = None

                # Assign None to 'Concept Name' if nothing relevant to parse
                # in RDSR content
                else:
                    data_parsed_dict[tag] = None

            # Append dictionary to DataFrame
            data_parsed = data_parsed.append(data_parsed_dict,
                                             ignore_index=True)

    return data_parsed


def rdsr_normalizer(data_parsed: pd.DataFrame) -> pd.DataFrame:
    """Normalize the vendor specific RDSR conventions.

    Parameters
    ----------
    data_parsed : pd.DataFrame
        parsed RDSR data.

    Returns
    -------
    pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.

    """
    data_norm = pd.DataFrame()

    if data_parsed.model[0] == "AXIOMArtis":

        # Device
        data_norm["model"] = data_parsed.model
        # Field size in cm at detector plane, in lateral direction
        data_norm["acquisition_plane"] = data_parsed.AcquisitionPlane
        data_norm["FS_lat"] = \
            round(100 * np.sqrt(data_parsed.CollimatedFieldArea_m2), 3)
        # Field size in cm at detector plane, in longitudinal direction
        data_norm["FS_long"] = \
            round(100 * np.sqrt(data_parsed.CollimatedFieldArea_m2), 3)
        # Distance source to detector in cm
        data_norm["DSD"] = \
            data_parsed.DistanceSourcetoDetector_mm / 10
        # Distance source to isocenter in cm
        data_norm["DSI"] = data_parsed.DistanceSourcetoIsocenter_mm / 10
        # Distance isocenter to detector, in cm
        data_norm["DID"] = data_norm.DSD - data_norm.DSI
        # Distance source to IRP, in cm
        data_norm["DSIRP"] = data_norm.DSI - 15
        # Reference point (IRP) air kerma in mGy
        data_norm["K_IRP"] = 1000 * data_parsed.DoseRP_Gy
        # Tube peak voltage in kV
        data_norm["kVp"] = data_parsed.KVP_kV
        # Positioner primary angle in degress
        data_norm["PPA"] = data_parsed.PositionerPrimaryAngle_deg
        # Positioner secondary angle in degress
        data_norm["PSA"] = data_parsed.PositionerSecondaryAngle_deg
        # Table increment in lateral direction, in cm
        data_norm["dLAT"] = + data_parsed.TableLateralPosition_mm / 10
        # Table increment in longitudinal direction, in cm
        data_norm["dLONG"] = + data_parsed.TableLongitudinalPosition_mm / 10
        # Table increment in vertical direction, in cm
        data_norm["dVERT"] = + data_parsed.TableHeightPosition_mm / 10
        # Detector size lenth, in cm
        data_norm["DSL"] = 40
        # X-ray filter material
        data_norm["filter_type"] = data_parsed.XRayFilterType
        # X-ray filter thickness
        data_norm["filter_thickness_Cu"] = data_parsed.XRayFilterThicknessMaximum_mm
        data_norm["filter_thickness_Al"] = [0.0] * len(data_parsed.XRayFilterThicknessMaximum_mm)
        data_norm.filter_thickness_Cu = data_norm.filter_thickness_Cu.fillna(0.0)
        # more to be added

    return data_norm

