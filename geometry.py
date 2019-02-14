from geom_plot import *
from geom_calc import *
from phantom_class import *
from parse_data import *
import pandas as pd
import numpy as np
from mayavi import mlab
from mayavi.mlab import *
import pydicom
import time
import sys
import os
from beam_class import *

# Default parameters:

patient_type = "cylinder"
human_model = "Tman_flat"

plot_events = False  # select if the sequence should be plotted for debugging
calculate_dose = True
plot_setup = False

# create phantom and table and pad
table = Phantom(phantom_type="table")
pad = Phantom(phantom_type="pad")
patient = Phantom(phantom_type=patient_type, human_model=human_model)


# rotate to get in z dir
table._rotate(rotation=[90, 0, 0])
pad._rotate(rotation=[90, 0, 0])
patient._rotate(rotation=[90, 0, 0])

# translate to get origin at the head end of the table
table._translate(dr=[0, 0, -max(table.z)])
pad._translate(dr=[0, 0, -max(pad.z)])
patient._translate(dr=[0, 0, -max(patient.z)])

# offset patient 15 cm from head end of table
offset_from_tabletop = -15
patient._translate(dr=[0, 0, offset_from_tabletop])

# place phantom directly on top of the pad
patient._translate(
    dr=[0, -(max(patient.y) + DEFAULT_PHANTOM_DIM["pad_thickness"]), 0])
pad._translate(dr=[0, 0, -5])

# Save reference table position:
table._save_position()
pad._save_position()
patient._save_position()

if plot_setup:
    p1 = plot_phantom(patient)
    p2 = plot_phantom(table)
    p3 = plot_phantom(pad)
    mlab.show()
    sys.exit

# choose RDSR data file (from RDSR_data folder)
data_filename = "S1"
data_path = os.path.join(os.path.dirname(__file__),
                         'RDSR_data', f"{data_filename}.dcm")

# read and parse RDSR file
data_raw = pydicom.read_file(data_path)

data_parsed, model = rdsr_parser(data_raw)
data_parsed = tempname(data_parsed)  # Ad temp names (to be included in parse()

if plot_events:
    # Initialize
    i = 0
    beam = Beam(data_parsed, 0)

    position_phantom(patient, data_parsed, i)
    position_phantom(table, data_parsed, i)
    position_phantom(pad, data_parsed, i)

    p1 = plot_phantom(patient)
    p2 = plot_phantom(table)
    p3 = plot_phantom(pad)
    p4 = plot_detector(beam)
    p5 = plot_beam(beam, "volume")
    p7 = plot_beam(beam, "wireframe")
    T1 = mlab.text(0.006, 0.75, text=f"Event: 1", width=0.15, opacity=0.7)
    p6 = plot_source(beam)

    @mlab.animate(delay=1000)
    def anim():

        f = mlab.gcf()
        for i in range(0, len(data_parsed.DoseRP_Gy)):

            print(f"processing event: {i}")
            T1.text = f"    Event: {i+1} of {len(data_parsed.CFA)}"
            beam = Beam(data_parsed, i)
            position_phantom(patient, data_parsed, i)
            position_phantom(table, data_parsed, i)
            position_phantom(pad, data_parsed, i)

            p1.mlab_source.set(x=patient.x, y=patient.y, z=patient.z)
            p2.mlab_source.set(x=table.x, y=table.y, z=table.z)
            p3.mlab_source.set(x=pad.x, y=pad.y, z=pad.z)

            p4.mlab_source.set(x=beam.x_det,
                               y=beam.y_det,
                               z=beam.z_det)

            p5.mlab_source.set(x=np.append(beam.source[0], beam.x_edge),
                               y=np.append(beam.source[1], beam.y_edge),
                               z=np.append(beam.source[2], beam.z_edge))

            p7.mlab_source.set(x=np.append(beam.source[0], beam.x_edge),
                               y=np.append(beam.source[1], beam.y_edge),
                               z=np.append(beam.source[2], beam.z_edge))

            p6.mlab_source.set(x=beam.source[0],
                               y=beam.source[1],
                               z=beam.source[2])

            yield

    # plot settings
    # title(f"PySkinDose [dev]", opacity=0.5)
    title(f"    PySkinDose [dev]\n \n    device: {model}", opacity=0.5)
    ax = mlab.axes(xlabel='x', ylabel='y', zlabel='z', nb_labels=11,
                   extent=[-100, 100, -100, 100, -100, 100])
    ax.axes.font_factor = 0.5

    anim()
    mlab.show()

if calculate_dose:

    # preallocate memory for skindose accumulation
    dose_sum = np.asarray([0] * len(patient.r))

    for i in range(0, len(data_parsed.DoseRP_Gy)):
        print(f"calculations skin dose, event: {i}")
        beam = Beam(data_parsed, i)
        position_phantom2(patient, data_parsed, i)
        position_phantom2(table, data_parsed, i)
        position_phantom2(pad, data_parsed, i)

        hits = CheckHit(beam.source, beam.r_edge, patient.r, patient.normals)
        dose_sum[hits] = dose_sum[hits] + 1000 * data_parsed.DoseRP_Gy[i]

    result_patient = Phantom(phantom_type=patient_type,
                             human_model=human_model)

    result_patient.dose = dose_sum

    result_patient.plot()
