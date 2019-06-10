import argparse
import numpy as np
import os
import pydicom
from typing import Union, Optional

from pyskindose.beam_class import Beam
from pyskindose.corrections import calculate_k_bs
from pyskindose.corrections import calculate_k_isq
from pyskindose.corrections import calculate_k_med
from pyskindose.corrections import calculate_k_tab
from pyskindose.geom_calc import check_new_geometry
from pyskindose.geom_calc import check_table_hits
from pyskindose.geom_calc import fetch_hvl
from pyskindose.geom_calc import position_geometry
from pyskindose.geom_calc import scale_field_area
from pyskindose.parse_data import rdsr_parser
from pyskindose.parse_data import rdsr_normalizer
from pyskindose.phantom_class import Phantom
from pyskindose.plots import plot_geometry
from pyskindose.settings import PyskindoseSettings

PARSER = argparse.ArgumentParser()

PARSER.add_argument('--file-path', help='Path to RDSR DICOM file')
ARGS = PARSER.parse_args()


PARAM_DEV = dict(
    # modes: 'calculate_dose', 'plot_setup', 'plot_event', 'plot_procedure'
    mode='calculate_dose',
    # RDSR filename
    rdsr_filename='S1.dcm',
    # Irrading event index for mode='plot_event'
    plot_event_index=12,
    # Set True to estimate table correction, or False to use measured k_tab
    # from /table_data/table_transmission.csv
    estimate_k_tab=False,
    # Numeric value of estimated table correction
    k_tab_val=0.8,
    # Phantom settings:
    phantom=dict(
        # Phantom model, valid selections: 'plane', 'cylinder', or 'human'
        model='human',
        # Human phantom .stl filename, without .stl ending.
        human_mesh='adult_male',
        # Patient offset from table isocenter (centered at head end side).
        patient_offset={'d_lat': 0,
                        'd_ver': 0,
                        'd_lon': -15,
                        'units': 'cm'},
        # Dimensions of matematical phantoms (except model='human')
        dimension={
            'plane_length': 120,  # Length of plane phantom
            'plane_width': 40,  # Width of plane phantom
            'plane_resolution': 'sparse',  # Resolution of plane phantom
            'cylinder_length': 150,  # Length of cylinder phantom
            'cylinder_radii_a': 20,  # First radii of cylinder phantom
            'cylinder_radii_b': 10,  # Second radii of cylinder phantom
            'cylinder_resolution': 'sparse',  # Resolution of cylinder.
            'table_thickness': 5,  # Support table thickness
            'table_length': 210,  # Support table length
            'table_width': 50,  # Support table width
            'pad_thickness': 4,  # Support pad thickness
            'pad_length': 210,  # Support pad length
            'pad_width': 50,  # Support pad width
            'units': 'cm'}))  # unit of dimension. Only 'cm' is supported.


def main(file_path: Optional[str] = None, settings: Union[str, dict] = None):
    """Run PySkinDose.

    Copy settings_examples.json and save it as settings.json.
    Set all you parameters in this file. For debugging and developement,
    the PARAM_dev settings dictionary can be used by calling
    main(settings=PARAM_DEV).

    See settings.py for a description of all the parameters. Please visit
    https://dev.azure.com/Sjukhusfysiker/PySkinDose for info on how to run
    PySkinDose.

    Parameters
    ----------
    file_path : str, optional
        file path to RDSR file
    settings : Union[str, dict], optional
        Setting file in either dict or json string format, by default
        settings_examples.json is enabled.

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

    # If no file path to RDSR file is specified, check for file path to the
    # folder /RDSR_data
    if not file_path:
        file_path = os.path.join(
            os.path.dirname(__file__), 'example_data', 'RDSR',
            param.rdsr_filename)

    # Read RDSR data with pydicom
    data_raw = pydicom.read_file(file_path)

    # parse RDSR data from raw .dicom file
    data_parsed = rdsr_parser(data_raw)

    # normalized rdsr for compliance with PySkinDose
    data_norm = rdsr_normalizer(data_parsed)
    
    # create table, pad and patient phantoms.
    table = Phantom(phantom_model='table', phantom_dim=param.phantom.dimension)
    pad = Phantom(phantom_model='pad', phantom_dim=param.phantom.dimension)

    # override dense mathematical phantom in .html plotting
    if param.mode in ["plot_setup", "plot_event", "plot_procedure"]:
        if param.phantom.model == 'plane':
            param.phantom.dimension.plane_resolution = 'sparse'
        elif param.phantom.model == 'cylinder':
            param.phantom.dimension.cylinder_resolution = 'sparse'

    patient = Phantom(
        phantom_model=param.phantom.model,
        phantom_dim=param.phantom.dimension,
        human_mesh=param.phantom.human_mesh)
    # position objects in starting position
    position_geometry(
        patient=patient, table=table, pad=pad,
        pad_thickness=param.phantom.dimension.pad_thickness,
        patient_offset=[
            param.phantom.patient_offset.d_lat,
            param.phantom.patient_offset.d_ver,
            param.phantom.patient_offset.d_lon])

    if param.mode in ["plot_setup", "plot_event", "plot_procedure"]:

        plot_geometry(patient, table, pad, data_norm,
                      mode=param.mode, event=param.plot_event_index,
                      include_patient=patient.phantom_model != 'human')

    elif param.mode == "calculate_dose":

        # Append HVL for all events to data_norm
        fetch_hvl(data_norm)
        # Check which irradiation events that contains updated
        # geometry parameters since the previous irradiation event
        new_geom = check_new_geometry(data_norm)
        # fetch of k_bs interpolation object (k_bs=f(field_size))for all events
        bs_interp = calculate_k_bs(data_norm)
        # Calculate table correction factors
        k_tab = calculate_k_tab(data_norm,
                                estimate_k_tab=param.estimate_k_tab,
                                k_tab_val=param.k_tab_val)

        nr_events = len(data_norm)

        output = dict(hits=[[]] * nr_events,
                      kerma=[np.array] * nr_events,
                      k_isq=[[]] * nr_events,
                      k_bs=[[]] * nr_events,
                      k_med=[[]] * nr_events,
                      k_tab=[[]] * nr_events,
                      dose_map=np.zeros(len(patient.r)))

        print('Calculating event: ')
        # For each irradiation event
        for event in range(0, nr_events):
            print(f"{event + 1} of {nr_events}")

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
                # If any skin cell is hit
                if sum(hits):

                    # Check which skin cells need table correction
                    table_hits = check_table_hits(
                        source=beam.r[0, :], table=table, beam=beam,
                        cells=patient.r[hits])

                    # Calculate X-ray field area at the location
                    # of each skin cell
                    field_area = scale_field_area(data_norm, event, patient,
                                                  hits, beam.r[0, :])

                    # Calculate inverse-square law fluece correction
                    k_isq = calculate_k_isq(source=beam.r[0, :],
                                            cells=patient.r[hits],
                                            dref=data_norm["DSIRP"][0])

            if sum(hits):
                # Interpolate backscatter factor to actual cell field sizes
                k_bs = bs_interp[event](np.sqrt(field_area))

                # Calculate reference point medium correction (air -> water)
                k_med = calculate_k_med(data_norm, field_area, event)

            # Save event data
            event_dose = np.zeros(len(patient.r))

            output["hits"][event] = hits
            output["kerma"][event] = data_norm.K_IRP[event]

            if sum(hits):
                output["k_isq"][event] = k_isq
                output["k_bs"][event] = k_bs
                output["k_med"][event] = k_med
                output["k_tab"][event] = k_tab[event]

                # Calculate event skin dose by appending each of the correction
                # factors to the reference point air kerma.
                event_dose[hits] += data_norm.K_IRP[event]
                event_dose[hits] *= k_isq
                event_dose[hits] *= k_med
                event_dose[hits] *= k_bs

                temp = np.ones(len(table_hits))
                temp[table_hits] = k_tab[event]
                event_dose[hits] *= temp

            # Add event dose to procedure dosemap
            output["dose_map"] += event_dose

        # Fix error with plotly layout for 2D plane patient.
        if patient.phantom_model == "plane":
            patient = Phantom(
                phantom_model=param.phantom.model,
                phantom_dim=param.phantom.dimension)

        # Append and plot dosemap
        patient.dose = output["dose_map"]
        patient.plot_dosemap()


main(file_path=ARGS.file_path, settings=PARAM_DEV)
