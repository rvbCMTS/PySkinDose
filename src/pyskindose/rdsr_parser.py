from datetime import datetime as dt

import pandas as pd
import pydicom

from pyskindose.constants import (
    KEY_RDSR_ACQUISITION_DATA,
    KEY_RDSR_COMMENT,
    KEY_RDSR_CONCEPT_CODE_SEQUENCE,
    KEY_RDSR_CONTENT_SEQUENCE,
    KEY_RDSR_DATE_TIME,
    KEY_RDSR_DETECTORSIZE_MM,
    KEY_RDSR_EVENT_XRAY_DATA,
    KEY_RDSR_II_DIAMETER_SRDATA,
    KEY_RDSR_MANUFACTURER,
    KEY_RDSR_MANUFACTURER_MODEL_NAME,
    KEY_RDSR_MEASURED_VALUE_SEQUENCE,
    KEY_RDSR_TEXT_VALUE,
    KEY_RDSR_UID,
)


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
    # create list to store rdsr content from each irradiation event
    prodcedure_dicts = []
    # For each content in RDSR file
    for rdsr_content in data_raw.ContentSequence:

        # If content = irradiation event
        if rdsr_content.ConceptNameCodeSequence[0].CodeMeaning == KEY_RDSR_EVENT_XRAY_DATA:

            # Declare temporary dictionary
            data_parsed_dict = dict()

            # Save manufacturer, and manufacturer model name
            data_parsed_dict[KEY_RDSR_MANUFACTURER] = data_raw.Manufacturer
            data_parsed_dict[KEY_RDSR_MANUFACTURER_MODEL_NAME] = data_raw.ManufacturerModelName

            # For each content in 'Irradiation Event X-Ray Data'
            for xray_event_content in rdsr_content.ContentSequence:
                # Reformat 'Concept Name'
                tag = (
                    xray_event_content.ConceptNameCodeSequence[0]
                    .CodeMeaning.replace(" ", "")
                    .replace("-", "")
                    .replace("(", "")
                    .replace(")", "")
                    .replace(".", "")
                )

                # Save 'Concept Name' to dictionary, assign corresponding value
                if KEY_RDSR_CONCEPT_CODE_SEQUENCE in xray_event_content:
                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] = [
                            data_parsed_dict[tag],
                            xray_event_content.ConceptCodeSequence[0].CodeMeaning,
                        ]
                    else:
                        data_parsed_dict[tag] = xray_event_content.ConceptCodeSequence[0].CodeMeaning

                elif KEY_RDSR_MEASURED_VALUE_SEQUENCE in xray_event_content:
                    # If the content contains a 'Measured Value Sequence'
                    # Reformat 'Concept Name' to include unit of measurement
                    unit = (
                        xray_event_content.MeasuredValueSequence[0]
                        .MeasurementUnitsCodeSequence[0]
                        .CodeValue.replace(".", "")
                    )

                    tag = "_".join([tag, unit])

                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] = [
                            data_parsed_dict[tag],
                            xray_event_content.MeasuredValueSequence[0].NumericValue,
                        ]

                    else:
                        data_parsed_dict[tag] = xray_event_content.MeasuredValueSequence[0].NumericValue

                elif KEY_RDSR_TEXT_VALUE in xray_event_content:

                    # This loop extracts detector size for static acquisitions,
                    # which is given as a 'Comment' for siemens artis zee units
                    if tag == KEY_RDSR_COMMENT:
                        comment = xray_event_content.TextValue.split("/")
                        if KEY_RDSR_ACQUISITION_DATA in comment[0]:
                            for index in comment:
                                if KEY_RDSR_II_DIAMETER_SRDATA in index:
                                    data_parsed_dict[KEY_RDSR_DETECTORSIZE_MM] = index.split("=")[1].replace('"', "")

                    elif tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] = [data_parsed_dict[tag], xray_event_content.TextValue]
                    else:
                        data_parsed_dict[tag] = xray_event_content.TextValue

                elif KEY_RDSR_UID in xray_event_content:
                    if tag in data_parsed_dict.keys():
                        data_parsed_dict[tag] = [data_parsed_dict[tag], xray_event_content.UID]
                    else:
                        data_parsed_dict[tag] = xray_event_content.UID

                # If the 'Irradiation Event X-Ray Data' contains subcontent
                elif KEY_RDSR_CONTENT_SEQUENCE in xray_event_content:
                    # For each subcontent
                    for xray_event_subcontent in xray_event_content.ContentSequence:
                        # Reformat 'Concept Name'
                        tag = (
                            xray_event_subcontent.ConceptNameCodeSequence[0]
                            .CodeMeaning.replace(" ", "")
                            .replace("-", "")
                            .replace("(", "")
                            .replace(")", "")
                            .replace(".", "")
                        )

                        # corresponding value
                        if KEY_RDSR_CONCEPT_CODE_SEQUENCE in xray_event_subcontent:
                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] = [
                                    data_parsed_dict[tag],
                                    xray_event_subcontent.ConceptCodeSequence[0].CodeMeaning,
                                ]
                            else:
                                data_parsed_dict[tag] = xray_event_subcontent.ConceptCodeSequence[0].CodeMeaning

                        elif KEY_RDSR_TEXT_VALUE in xray_event_subcontent:

                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] = [data_parsed_dict[tag], xray_event_subcontent.TextValue]

                            else:
                                data_parsed_dict[tag] = xray_event_subcontent.TextValue

                        elif KEY_RDSR_UID in xray_event_subcontent:
                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] = [data_parsed_dict[tag], xray_event_subcontent.UID]
                            else:
                                data_parsed_dict[tag] = xray_event_subcontent.UID
                        elif KEY_RDSR_MEASURED_VALUE_SEQUENCE in xray_event_subcontent:
                            # Reformat 'Concept Name' to include unit of
                            # measurement
                            unit = (
                                xray_event_subcontent.MeasuredValueSequence[0].MeasurementUnitsCodeSequence[0].CodeValue
                            )

                            tag = "_".join([tag, unit])

                            if tag in data_parsed_dict.keys():
                                data_parsed_dict[tag] = (
                                    data_parsed_dict[tag],
                                    xray_event_subcontent.MeasuredValueSequence[0].NumericValue,
                                )
                            else:
                                data_parsed_dict[tag] = xray_event_subcontent.MeasuredValueSequence[0].NumericValue

                        # Assign None to 'Concept Name' if nothing relevant to
                        # parse in RDSR subcontent
                        else:
                            data_parsed_dict[tag] = None

                # Assign None to 'Concept Name' if nothing relevant to parse
                # in RDSR content
                else:
                    data_parsed_dict[tag] = None

            # Store event info
            prodcedure_dicts.append(data_parsed_dict)

    data_parsed = pd.DataFrame(prodcedure_dicts)

    return data_parsed
