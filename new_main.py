from phantom_class import Phantom
from phantom_class import DEFAULT_PHANTOM_DIM
from beam_class import Beam
from plotly_plots import plot_geometry
from geom_calc import position_geometry
from geom_calc import scale_field_area
from geom_calc import fetch_HVL
from corrections import calculate_k_isq
from corrections import calculate_k_med
from corrections import calculate_k_bs
from parse_data import rdsr_parser
from parse_data import rdsr_normalizer
from db_connect import db_connect
import numpy as np
import pydicom
import os

# MODES = ["plot_setup", "plot_event", "plot_procedure", "calculate_dose"]

# Default parameters:
phantom_dim = DEFAULT_PHANTOM_DIM
patient_type = "cylinder"  # DEFAULT_PHANTOM_TYPE
human_model = "Tman_flat"  # DEFAULT_HUMAN_MODEL
rdsr_filename = "S1"
mode = "calculate_dose"
event = 22

# set path to RDSR file
rdsr_path = os.path.join(os.path.dirname(__file__),
                         'RDSR_data', f"{rdsr_filename}.dcm")
# read and parse RDSR file
data_raw = pydicom.read_file(rdsr_path)
data_parsed = rdsr_parser(data_raw)
data_norm = rdsr_normalizer(data_parsed)

# create phantom, table and pad
table = Phantom(phantom_type="table")
pad = Phantom(phantom_type="pad")
patient = Phantom(phantom_type=patient_type,
                  human_model=human_model)

# position objects in starting position
position_geometry(patient=patient, table=table, pad=pad,
                  pad_thickness=phantom_dim["pad_thickness"],
                  patient_offset=[0, 0, -15])

if mode in ["plot_setup", "plot_event", "plot_procedure"]:

    plot_geometry(patient, table, pad, data_norm,
                  mode=mode, event=event, include_patient=False)

elif mode == "calculate_dose":

    print("Calculating skin dose...")

    output = dict(hits=[[]] * len(data_norm),
                  kerma=[np.array] * len(data_norm),
                  k_isq=[[]] * len(data_norm),
                  k_bs=[[]] * len(data_norm),
                  k_med=[[]] * len(data_norm),
                  dose_map=np.zeros(len(patient.r)))

    fetch_HVL(data_norm)

    for event in range(0, len(data_norm)):
        print(f"Calculating event: {event + 1} of {len(data_norm)}")

        # create event beam
        beam = Beam(data_norm, event=event, plot_setup=False)

        # position geometry in relation to the X-ray beam
        patient.position_phantom(data_norm, event)
        table.position_phantom(data_norm, event)
        pad.position_phantom(data_norm, event)

        hits = beam.check_hit(patient)

        field_area = scale_field_area(data_norm, event, patient, hits,
                                      beam.r[0, :])

        k_isq = calculate_k_isq(source=beam.r[0, :], cells=patient.r[hits],
                                dref=data_norm["DSIRP"][0])

        k_bs = calculate_k_bs(data_norm, field_area, event)

        k_med = calculate_k_med(data_norm, field_area, event)

        # save event data
        output["hits"][event] = hits
        output["kerma"][event] = data_norm.K_IRP[event]
        output["k_isq"][event] = k_isq
        output["k_bs"][event] = k_bs
        output["k_med"][event] = k_med

        # Calculate dosemap:
        event_dose = np.zeros(len(patient.r))

        event_dose[hits] += data_norm.K_IRP[event]
        event_dose[hits] *= k_isq
        event_dose[hits] *= k_med
        event_dose[hits] *= k_bs

        output["dose_map"] += event_dose

    # Save dosemap to patient
    patient.dose = output["dose_map"]

    # Plot dosemap
    patient.plot_dosemap()

    # kerma/+isq/+k_med/+k_bs: 7.85
    # + k_isq                  7.94
    # + k_med                  8.15
    # + k_bs                   12.12