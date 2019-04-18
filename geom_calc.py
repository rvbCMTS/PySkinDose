from phantom_class import Phantom
from typing import List, Any
import numpy as np
import pandas as pd


def position_geometry(patient: Phantom, table: Phantom, pad: Phantom,
                      pad_thickness: Any, patient_offset: List[int]) -> None:
    """Manual positioning of the phantoms before procedure starts.

    In this function, the patient phantom, support table, and pad are
    positioned to the starting position for the procedure. This is done by
    rotating and translating the patient, table and pad phantoms so that
    the correct starting position is achieved. Currently, the patient is
    assumed to lie in supine position. The effect of this positioning can be
    displayed by running mode == "plot_setup" in main.py.

    Parameters
    ----------
    patient : Phantom
        Patient phantom, either plane, cylinder or human.
    table : Phantom
        Table phantom to represent the patient support table
    pad : Phantom
        Pad phantom to represent the patient support pad
    pad_thickness: Any
        Patient support pad thickness
    patient_offset : List[int]
        Offsets the patient phantom from the centered along the head end of the
        table top, given as [dLON: <int>, "dVER": <int>, "dLAT": <int>] in cm.

    """
    # rotate 90 deg about LON axis to get head end in positive LAT direction
    table.rotate(angles=[90, 0, 0])
    pad.rotate(angles=[90, 0, 0])
    patient.rotate(angles=[90, 0, 0])

    # translate to get origin centered along the head end of the table
    table.translate(dr=[0, 0, -max(table.r[:, 2])])
    pad.translate(dr=[0, 0, -max(pad.r[:, 2])])
    patient.translate(dr=[0, 0, -max(patient.r[:, 2])])

    # place phantom directly on top of the pad
    patient.translate(dr=[0, -(max(patient.r[:, 1] + pad_thickness)), 0])

    # offset patient 15 cm from head end
    patient.translate(dr=patient_offset)

    # Save reference table position:
    table.save_position()
    pad.save_position()
    patient.save_position()


def vector(start: np.array, stop: np.array, normalization=False) -> np.array:
    """Create a vector between two points in carthesian space.

    This function creates a simple vector between point <start> and point
    <stop"> The function can also create a unit vector from <start>, in the
    direction to <stop>.

    Parameters
    ----------
    start : np.array
        Starting point of the vector
    stop : np.array
        Stopping point of the vector
    normalization : bool, optional
        Toggle normalization (the default is False, which implies no
        normalization)

    Returns
    -------
    np.array
        A vector from "start" to "stop", or if normalization=True, a unit
        vector from "start" in the direction towards "stop".

    """
    # Calculate vector from start to stop
    v = stop - start

    # Normalize if requested
    if normalization:
        # Normalize vector
        mag = np.sqrt(v.dot(v))
        v = v / mag

    return v


def scale_field_area(data_norm: pd.DataFrame, event: int, patient: Phantom, hits: List[bool], source: np.array) -> List[float]:
    """Scale X-ray field size from image detector, to phantom skin cells.

    This function scales the X-ray field size from the point where it is stated
    in data_norm, i.e. at the image detector plane, to the plane at the phantom
    skin cell. This is the field size of interest since this area is required
    as input for k_med and k_bs correction factor calculations. This function
    conducts this scaling for all skin cells that are hit struck by the X-ray
    beam in a specific irradiation event.

    Parameters
    ----------
    data_norm : pd.DataFrame
        [description]
    event : int
        [description]
    patient : Phantom
        [description]
    hits : List[bool]
        A boolean list of the same length as the number of patient skin
        cells. True for all entrance skin cells that are hit by the beam for a
        specific irradiation event.
    source : np.array
        (x,y,z) coordinates to the X-ray source

    Returns
    -------
    List[float]
        X-ray field area in (cm^2) for each phantom skin cell that are hit by 
        X-ray the beam

    """
    # Fetch reference distance for field size scaling,
    # i.e. distance source to detector
    d_ref = data_norm.DSD[event]

    cells = patient.r[hits]

    # Calculate distance scale factor
    scale_factor = [np.linalg.norm(cell - source) / d_ref for cell in cells]

    # Fetch field side lenth lateral and longitudinal at detector plane
    # Fetch field area at image detector plane
    field_area_ref = data_norm.FS_lat[event] * data_norm.FS_long[event]


    # Calculate field area at distance source to skin cell for all cells
    # that are hit by the beam.
    field_area = [field_area_ref * np.square(scale)
                  for scale in scale_factor]

    return field_area
