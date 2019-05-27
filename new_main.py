import time
import json
import os
import numpy as np
import pydicom
from typing import Union
from phantom_class import Phantom
from beam_class import Beam
from plots import plot_geometry
from geom_calc import position_geometry
from geom_calc import scale_field_area
from geom_calc import fetch_hvl
from geom_calc import check_new_geometry
from corrections import calculate_k_isq
from corrections import calculate_k_med
from corrections import calculate_k_bs
from parse_data import rdsr_parser
from parse_data import rdsr_normalizer
from settings import PyskindoseSettings

PARAM_DEV = dict(
    # Valid modes: 'calculate_dose', 'plot_setup', 'plot_procedure'
    mode='calculate_dose',
    # RDSR filename
    rdsr_filename='S1.dcm',
    # Irrading event index for mode='plot_event'
    plot_event_index=21,
    # Phantom settings:
    phantom=dict(
        # Phantom model,valid selections: 'plane', 'cylinder', or 'human'
        model='cylinder',
        # Human phantom .stl filename, without .stl ending.
        human_model='Tman_flat',
        # Dimensions of matematical phantoms (except model='human')
        dimension={
            'plane_length': 180,  # Length of plane phantom
            'plane_width': 50,  # Width of plane phantom
            'cylinder_length': 150,  # Length of cylinder phantom
            'cylinder_radii_a': 20,  # First radii of cylinder phantom
            'cylinder_radii_b': 10,  # Second radii of cylinder phantom
            'cylinder_resolution': 'coarse',  # Resolution of cylinder.
            'table_thickness': 5,  # Support table thickness
            'table_length': 210,  # Support table length
            'table_width': 50,  # Support table width
            'pad_thickness': 4,  # Support pad thickness
            'pad_length': 210,  # Support pad length
            'pad_width': 50,  # Support pad width
            'units': 'cm'}))  # unit of dimension. Only 'cm' is supported.


def main(settings: Union[str, dict]=None):
    """Run PySkinDose.

    Copy settings_examples.json and save it as settings.json.
    Set all you parameters in this file. Then run PySkinDose by calling
    main() in the end of this script. For debugging and developement,
    the PARAM_dev settings dictionary can be used by calling main(PARAM_DEV)
    insted of just main().

    See settings.py for a description of all the parameters. Please visit
    https://dev.azure.com/Sjukhusfysiker/PySkinDose for info on how to run
    PySkinDose.

    Parameters
    ----------
    settings : Union[str, dict], optional
        Setting file in either dict or json string format, by default
        settings.json is enabled.

    """
    if settings is None:

        settings_path = os.path.join(os.path.dirname(__file__),
                                     'settings.json')
        settings_example_path = \
            os.path.join(os.path.dirname(__file__), 'settings_example.json')

        if os.path.exists(settings_path):
            settings = open(settings_path, 'r').read()

        else:
            settings = open(settings_example_path, 'r').read()

    # Fetch all parameters
    param = PyskindoseSettings(settings)

    # read and parse RDSR file
    data_raw = pydicom.read_file(os.path.join(
        os.path.dirname(__file__), 'RDSR_data', param.rdsr_filename))

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw)
    # normalized rdsr for compliance with PySkinDose
    data_norm = rdsr_normalizer(data_parsed)

    # create table, pad and patient phantoms.
    table = Phantom(phantom_model='table', phantom_dim=param.phantom.dimension)
    pad = Phantom(phantom_model='pad', phantom_dim=param.phantom.dimension)

    patient = Phantom(
        phantom_model=param.phantom.model,
        phantom_dim=param.phantom.dimension,
        human_model=param.phantom.human_model)

    # position objects in starting position
    position_geometry(
        patient=patient, table=table, pad=pad,
        pad_thickness=param.phantom.dimension.pad_thickness,
        patient_offset=[0, 0, -35])

    if param.mode in ["plot_setup", "plot_event", "plot_procedure"]:

        plot_geometry(patient, table, pad, data_norm,
                      mode=param.mode, event=param.plot_event_index,
                      include_patient=patient.phantom_model != 'human')

    elif param.mode == "calculate_dose":

        start = time.time()

        # Append HVL for all events to data_norm
        fetch_hvl(data_norm)
        # Check which irradiation events that contains updated
        # geometry parameters since the previous irradiation event
        new_geom = check_new_geometry(data_norm)
        # fetch of k_bs interpolation object (k_bs=f(field_size))for all events
        bs_interp = calculate_k_bs(data_norm)

        output = dict(hits=[[]] * len(data_norm),
                      kerma=[np.array] * len(data_norm),
                      k_isq=[[]] * len(data_norm),
                      k_bs=[[]] * len(data_norm),
                      k_med=[[]] * len(data_norm),
                      dose_map=np.zeros(len(patient.r)))

        # For each irradiation event
        for event in range(0, len(data_norm)):
            print(f"Calculating event: {event + 1} of {len(data_norm)}")

            # If the geometry has changed since preceding event,
            # of if it is the first event
            if new_geom[event]:
                # create event beam
                beam = Beam(data_norm, event=event, plot_setup=False)

                # position geometry in relation to the X-ray beam
                patient.position(data_norm, event)
                table.position(data_norm, event)
                pad.position(data_norm, event)

                # Check which skin cells are hit by the beam
                hits = beam.check_hit(patient)

                # Calculate X-ray field area at the location of the skin cells
                field_area = scale_field_area(data_norm, event, patient, hits,
                                              beam.r[0, :])

                # Calculate inverse-square law fluece correction
                k_isq = calculate_k_isq(source=beam.r[0, :],
                                        cells=patient.r[hits],
                                        dref=data_norm["DSIRP"][0])

            # Interpolate backscatter factor to actual cell field sizes
            k_bs = bs_interp[event](np.sqrt(field_area))

            # Calculate reference point medium correction (air -> water)
            k_med = calculate_k_med(data_norm, field_area, event)

            # Save event data
            output["hits"][event] = hits
            output["kerma"][event] = data_norm.K_IRP[event]
            output["k_isq"][event] = k_isq
            output["k_bs"][event] = k_bs
            output["k_med"][event] = k_med

            # Calculate dosemap:
            event_dose = np.zeros(len(patient.r))

            # Calculate event skin dose by appending each of the correction
            # factors to the reference point air kerma.
            event_dose[hits] += data_norm.K_IRP[event]
            event_dose[hits] *= k_isq
            event_dose[hits] *= k_med
            event_dose[hits] *= k_bs

            # Add event dose to procedure dosemap
            output["dose_map"] += event_dose

        end = time.time()
        elapsed = round(end - start, 1)
        print(elapsed)

        # Fix error with plotly layout for 2D plane patient.
        if patient.type == "plane":
            patient = Phantom(
                phantom_model=param.phantom.model,
                phantom_dim=param.phantom.dimension)

        # Append and plot dosemap
        patient.dose = output["dose_map"]
        patient.plot_dosemap()


main(PARAM_DEV)
