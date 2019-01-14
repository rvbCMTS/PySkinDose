from geomplot import *
from geomtrack import *
from PhantomImport import *
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from parse_data import parse
import pandas as pd
import numpy as np
import pydicom

# Pandas properties
desired_width = 180
pd.set_option('display.max_columns', None)
pd.set_option('display.width', desired_width)

# Load dicom RDSR
filename = r"S1.dcm"
ds = pydicom.read_file(filename)
pd, model = parse(ds)

# Ad temp names
pd = tempname(pd)

# Create table
TablePhantom = CreateTable(TL=250, TW=50)

# Load Phantom
phantom_measurements = {'width': 50, 'length': 200, "a": 20, "b": 10}

ptm = create_phantom(phantom_type='human',
                     human_model='ttt',
                     phantom_dim=phantom_measurements)

ptm = PositionPatient(ptm, 90, TablePhantom)

# Create source
src = np.array([0, pd.DSI[0], 0])

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for i in range(10, 11):
    # Fetch rotation
    Ra, Rb = FetchRotation(pd.PPA[i], pd.PSA[i])
    # Position objects:
    source = PositionSource(src, Ra, Rb)
    detector = CreateDetector(40, pd, Ra, Rb, i)
    table = PositionTable(TablePhantom, pd, i)
    phantom = PositionPhantom(ptm, pd, i)
    ray = CreateRay(pd, Ra, Rb, i)

    # Plot geometry:
    # PlotPhantom(phantom, ax, "blue")  # Phantom
    ax.scatter(phantom["x"], phantom["z"], phantom["y"], alpha=0.5, s=0.5)

    PlotObject(table, ax, "blue")  # Table
    PlotObject(detector, ax, "black")  # Detector
    PlotPoint(source, ax, "black")  # Source
    PlotRay(ray, source, ax, "red")  # X-ray field

    # Plot settings
    ax.set_title("Irradiation event {}".format(i + 1))
    ax.set_xlim(-100, 100)
    ax.set_ylim(-100, 100)
    ax.set_zlim(-60, 100)
    ax.set_xlabel('$X_{iso}$')
    ax.set_ylabel('$Z_{iso}$')
    ax.set_zlabel('$Y_{iso}$')
    plt.gca().invert_zaxis()

plt.show()