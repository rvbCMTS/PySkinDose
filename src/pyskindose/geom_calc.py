import logging
from typing import Any, List

import numpy as np
import pandas as pd

import pyskindose.constants as c

from .db_connect import db_connect
from .phantom_class import Phantom

logger = logging.getLogger(__name__)


def calculate_field_size(field_size_mode, data_parsed, data_norm):
    """Calculate X-ray field size at image recepter plane.

    Parameters
    ----------
    field_size_mode : str
        Choose either 'CFA' ('collimated field area) or 'ASD' (actual shutter
        distance).

        If field_size_mode = 'CFA', the field side in lateral- and
        longutudinal direction are set equal to the square root of the
        collimated field area. NOTE, this should only be used when actual
        shutter distances are unavailabe.

        If field_size_mode = 'ASD', the function calculates the field size
        by distance scaling the actual shutter distance to the detector plane

    data_parsed : pd.DataFrame
        Parsed RDSR data from all irradiation events in the RDSR input file,
        i.e. output of function rdsr_parser
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.

    Returns
    -------
    FS_lat, FS_long : float
        Field size in lat- and long direction in cm at the detector plane.

    """
    # if collimated field are mode, set FS_lat = FS_long =
    # sqrt(collimate field area). NOTE: This should only be used when actual
    # shutter distances are unavailable.
    if field_size_mode == c.FIELD_SIZE_MODE_COLLIMATED_FIELD_AREA:

        # Field size in lat direction in metres
        FS_lat_m = np.sqrt(data_parsed.CollimatedFieldArea_m2)
        # Field size in long direction in metres
        FS_long_m = FS_lat_m

        # convert to cm
        FS_lat = round(convert_from_m_to_cm(FS_lat_m), 3)
        FS_long = round(convert_from_m_to_cm(FS_long_m), 3)

        return FS_lat, FS_long

    if field_size_mode == c.FIELD_SIZE_MODE_ACTUAL_SHUTTER_DISTANCE:

        # distance (from source) at which shutter distances are presented in
        # dicom tags
        d_shutter_in_dcm_cm = 100

        # field size in long direction at d = d_shutter_in_dcm_cm
        FS_long_at_d_shutter = convert_from_mm_to_cm(data_parsed.LeftShutter_mm + data_parsed.RightShutter_mm)
        # field size in lat direction at d = d_shutter_in_dcm_cm
        FS_lat_at_d_shutter = convert_from_mm_to_cm(data_parsed.TopShutter_mm + data_parsed.BottomShutter_mm)
        # scale factor to get field size at detector plane
        scale = data_norm.DSD / d_shutter_in_dcm_cm

        FS_lat = scale * FS_lat_at_d_shutter
        FS_long = scale * FS_long_at_d_shutter

        return FS_lat, FS_long


def position_patient_phantom_on_table(
    patient: Phantom,
    table: Phantom,
    pad: Phantom,
    pad_thickness: Any,
    patient_offset: List[int],
    patient_orientation: c.PATIENT_ORIENTATION_HEAD_FIRST_SUPINE,
) -> None:
    """Places the patient phantom upon the patient support table.

    In this function, the patient phantom is positioned to the starting
    position for the procedure. This is done by rotating and translating the
    patient so that the correct starting position is achieved.

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
        table top, given as [Tx: <int>, "Ty": <int>, "Tz": <int>] in cm.
    patient_orientation : str
        patient orientation upon table. Choose between
        c.PATIENT_ORIENTATION_HEAD_FIRST_SUPINE and
        c.PATIENT_ORIENTATION_FEET_FIRST_SUPINE.

    """
    # if feet-first, rotate patient 180 degrees about y-axis
    if patient_orientation == c.PATIENT_ORIENTATION_FEET_FIRST_SUPINE:

        offset_to_rotation_center = abs(patient.r[:, 2].min()) / 2

        patient.translate(dr=[0, 0, +offset_to_rotation_center])
        patient.rotate(angles=[0, 180, 0])
        patient.translate(dr=[0, 0, -offset_to_rotation_center])

    # place the phantom on top of the support pad
    patient.translate(dr=[0, -pad_thickness, 0])
    # add user specified patient offset
    patient.translate(dr=patient_offset)

    # Save reference table position:
    for phantom in [table, pad, patient]:
        phantom.save_position()


def vector(start: np.array, stop: np.array, normalization=False) -> np.array:
    """Create a vector between two points in carthesian space.

    This function creates a simple vector between point <start> and point
    <stop> The function can also create a unit vector from <start>, in the
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
    vec = stop - start

    # Normalize if requested
    if normalization:
        # Normalize vector
        mag = np.sqrt(vec.dot(vec))
        vec = vec / mag

    return vec


def scale_field_area(
    data_norm: pd.DataFrame, event: int, patient: Phantom, hits: List[bool], source: np.array
) -> List[float]:
    """Scale X-ray field area from image detector, to phantom skin cells.

    This function scales the X-ray field size from the point where it is stated
    in data_norm, i.e. at the image detector plane, to the plane at the phantom
    skin cell. This is the field size of interest since this area is required
    as input for k_med and k_bs correction factor calculations. This function
    conducts this scaling for all skin cells that are hit by the X-ray beam in
    a specific irradiation event.

    Parameters
    ----------
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.
    event : int
        Irradiation event index.
    patient : Phantom
        Patient phantom, i.e. instance of class Phantom.
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
    field_area = [round(field_area_ref * np.square(scale), 1) for scale in scale_factor]

    return field_area


def fetch_and_append_hvl(data_norm: pd.DataFrame) -> pd.DataFrame:
    """Add event HVL to RDSR event data from database.

    Parameters
    ----------
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.

    Returns
    -------
    data_norm
        This function appends event specific HVL (mmAl) as a function of device
        model, kVp, and copper- and aluminum filtration to the normalized RDSR
        data in data_norm and returns the DataFrame with the HVL info appended.

    """
    # Open connection to database
    conn = db_connect()[0]

    # Fetch entire HVL table
    hvl_data = pd.read_sql_query("SELECT * FROM HVL_simulated", conn)

    hvl = [
        float(
            hvl_data.loc[
                (hvl_data["DeviceModel"] == data_norm.model[event])
                & (hvl_data["kVp_kV"] == round(data_norm.kVp[event]))
                & (hvl_data["AcquisitionPlane"] == data_norm.acquisition_plane[event])
                & (hvl_data["AddedFiltration_mmCu"] == data_norm.filter_thickness_Cu[event])
                & (hvl_data["AddedFiltration_mmAl"] == round(data_norm.filter_thickness_Al[event])),
                "HVL_mmAl",
            ]
        )
        for event in range(len(data_norm))
    ]

    # Append HVL data to data_norm
    data_norm["HVL"] = hvl

    # close database connection
    conn.commit()
    conn.close()

    return data_norm


def check_new_geometry(data_norm: pd.DataFrame) -> List[bool]:
    """Check which events has unchanged geometry since the event before.

    This function is intented to calculate if new geometry parameters needs
    to be calculated, i.e., new beam, geometry positioning, field area and
    cell hit calculation.

    Parameters
    ----------
    data_norm : pd.DataFrame
        RDSR data, normalized for compliance with PySkinDose.

    Returns
    -------
    List[bool]
        List of booleans where True[event] means that the event has updated
        geometry since the preceding irradiation event.

    """
    logger.info("Checking which irradiation events contain changes in geometry" "compared to previous event")

    logger.debug("Listing all RDSR geometry parameters")
    geom_params = data_norm[["Tx", "Ty", "Tz", "FS_lat", "FS_long", "Ap1", "Ap2", "Ap3", "At1", "At2", "At3"]]

    logger.debug("Checking which irradiation events that does not have same" "parameters as previous")
    changed_geometry = [
        not geom_params.iloc[event].equals(geom_params.iloc[event - 1]) for event in range(1, len(geom_params))
    ]

    logger.debug("Insert True to the first event to indicate that it has a" "new geometry")

    changed_geometry.insert(0, True)

    return changed_geometry


class Triangle:
    """A class used to create triangles.

    This class creates a triangle from a set of three coordinates in 3D
    carthesian space. The purpose of this class is to use it to calculate if a
    3D segment intercepts the triangle.

    Attributes
    ----------
    p: np.array
        Carthesian 3D coordinates to the central vertex of the triangle
    p1: np.array
        Vector from p to first vertex
    p2: np.array
        Vector from p to second vertex
    n: np.array
        normal vector to the triangle, pointing upwards (negative y direction).

    Methods
    -------
        check_intersection
            check if a 3D segment intercepts with the triangle. For our
            purpose, the 3D segment represents an X-ray beam from the X-ray
            source to the phantom skin cell. If the beam intercepts, table- and
            pad fluence correction should be conducted when calculating skin
            dose for that particular cell. Please visit project documentation
            (https://dev.azure.com/Sjukhusfysiker/PySkinDose/_wiki/) for a
            clearer description and illustration for this method.

    """

    def __init__(self, p: np.array, p1: np.array, p2: np.array):
        """Initialize class attributes."""
        self.p = p
        self.p1 = vector(self.p, p1)
        self.p2 = vector(self.p, p2)
        n = np.cross(self.p1, self.p2)
        self.n = n / np.sqrt(n.dot(n))

    def check_intersection(self, start: np.array, stop: np.array) -> List[bool]:
        """Check if a 3D segment intercepts with the triangle.

        Check if a 3D segment intercepts with the triangle. For our purpose,
        the 3D segment represents an X-ray beam from the X-ray source to the
        phantom skin cell and the triangle represent parts of the patient
        support table. If the beam intercepts, table- and pad fluence
        correction should be conducted when calculating skin dose for that
        particular cell.

        Parameters
        ----------
        start : np.array
            Carthesian 3D coordinates to the starting point of the segment.
        stop : np.array
            Carthesian 3D coordinates to the end points of the segment. Note,
            can be several points, e.g, several skin cells.

        Returns
        -------
            List[bool]
            Boolean list which specifies whether each segment between start
            and each of coordinates in stop are intercepted by the triangle.

        """
        # Vector from source to central vertex
        # w = vector(start, self.p)
        w = self.p - start

        # List of unit vectors from start, to each of the coordinates in stop.
        v = ((stop - start).T / np.linalg.norm(stop - start, axis=stop.ndim - 1)).T

        # Distances from start to the plane of the triangle, in the direction
        # along the vector v.
        k = (np.dot(w, self.n)) / (np.dot(v, self.n))
        # Vector from origin to beam-table interceptions.
        i = start + (k * v.T).T

        # Vector from central vertex p to i
        p_i = i - self.p

        d = np.square(np.dot(self.p1, self.p2)) - np.dot(self.p1, self.p1) * np.dot(self.p2, self.p2)

        d1 = (np.dot(self.p1, self.p2) * np.dot(p_i, self.p2) - np.dot(self.p2, self.p2) * np.dot(p_i, self.p1)) / d

        d2 = (np.dot(self.p1, self.p2) * np.dot(p_i, self.p1) - np.dot(self.p1, self.p1) * np.dot(p_i, self.p2)) / d

        # Now we have p_i = d1/d * p1 + d2/d * p2, thus,
        # if 0 <= d1/d <= 1, and 0 <= d2/d <= 1, and d1 + d2 <= 1, the beam
        # intercepts the triangle.
        hits = np.array([d1 >= 0, d1 <= 1, d2 >= 0, d2 <= 1, d1 + d2 <= 1]).all(axis=0)

        return hits.tolist()


def check_table_hits(source: np.array, table: Phantom, beam, cells: np.array) -> List[bool]:
    """Check which skin cells are blocket by the patient support table.

    This fuctions creates two triangles covering the entire surface of the
    patient support table, and checks if the skin cells are blocked by the
    table. This is conducted in order to be able to append table and pad
    correction factor k_(T+P) when required.

    Parameters
    ----------
    source : np.array
        Carthesian 3D coordinates to the X-ray souce
    table : Phantom
        Patient support table, i.e., instance of class phantom with
        phantom_type="table"
    beam : Beam
         X-ray beam, i.e., instance of class Beam.
    cells : np.array
        List of skin cells to be controlled if the patient support table and
        pad blocks the beam before it reached the them.

    Returns
    -------
    List[bool]
        Boolean list of the statuses of each skin cell. True if the path from
        X-ray source to skin cell is blocked by the table (any of the two
        triangles), else false. Start points above triangle returns False,
        to not include hits where the table does not block the beam.

    """
    # Create triangles:

    # Define edges of table (see illustration in project documentation)
    a = table.r[0 + 4, :]
    a1 = table.r[3 + 4, :]
    a2 = table.r[1 + 4, :]

    b = table.r[2 + 4, :]
    b1 = table.r[1 + 4, :]
    b2 = table.r[3 + 4, :]

    # triangle spanning the "top right" part of the support table
    # (viewed from above)
    triangle_b_l = Triangle(p=a, p1=a1, p2=a2)
    # triangle spanning the "bottom left" part of the support table
    # (viewed from above)
    triangle_t_r = Triangle(p=b, p1=b1, p2=b2)

    # If over-table irradiation, return false for all points in cells
    if np.dot(np.array([0, 0, 0]) - beam.r[0, :], triangle_b_l.n) < 0:
        if cells.ndim == 1:
            return [False]
        return [False] * cells.shape[0]

    # Check if beam vertices hits table on either of the triangles
    hit_t_r = triangle_t_r.check_intersection(start=source, stop=beam.r[1:, :])
    hit_b_l = triangle_b_l.check_intersection(start=source, stop=beam.r[1:, :])

    # If all four beam verices hits the table, all cells are blocket by the
    # table, and all cells should be corrected for table and pad attenuation.
    if sum(hit_t_r + hit_b_l) == 4:
        if cells.ndim == 1:
            return [True]
        return [True] * cells.shape[0]

    # Else, check individually for all skin cells that are hit by the beam
    hit_t_r = triangle_t_r.check_intersection(start=source, stop=cells)
    hit_b_l = triangle_b_l.check_intersection(start=source, stop=cells)

    hits = np.asarray([False] * len(cells))
    # save results
    hits[hit_t_r] = True
    hits[hit_b_l] = True

    return hits.tolist()


def convert_from_mm_to_cm(val_in_mm: float) -> float:
    """Convert a length from millimeters to centimeters.

    Parameters
    ----------
    val_in_mm : float
        A length in mm

    Returns
    -------
    float
        The same length in cm

    """
    val_in_cm = val_in_mm / 10.0

    return val_in_cm


def convert_from_m_to_cm(val_in_m: float) -> float:
    """Convert a length from centimeters to millimeters.

    Parameters
    ----------
    val_in_m : float
        A length in m

    Returns
    -------
    float
        The same length in cm

    """
    val_in_cm = val_in_m * 100.0

    return val_in_cm
