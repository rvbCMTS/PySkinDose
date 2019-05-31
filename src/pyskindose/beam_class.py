import numpy as np
import pandas as pd
from typing import List

from .geom_calc import vector
from .phantom_class import Phantom


class Beam:
    """A class used to create an X-ray beam and detector.

    Attributes
    ----------
    r : np.array
        5*3 array, locates the xyz coordinates of the apex and verticies of a
        pyramid shaped X-ray beam, where the apex represents the X-ray focus
        (row 1) and the vertices where the beam intercepts the X-ray detector
        (row 2-5)
    ijk : np.array
        A matrix containing vertex indices. This is required in order to
        plot the beam using plotly Mesh3D. For more info, see "i", "j", and "k"
        at https://plot.ly/python/reference/#mesh3d
    det_r: np.array
        8*3 array, where each row locates the xyz coordinate of one of the 8
        corners of the cuboid shaped X-ray detector
    det_ijk : np.array
        same as ijk, but for plotting the X-ray detector
    N : np.array
        4*3 array, where each row contains a normal vector to one of the four
        faces of the beam.

    Methods
    -------
    check_hit(patient)
        Calculates which of the patient phantom's entrance skin cells are hit
        by be X-ray beam

    """

    def __init__(self, data_norm: pd.DataFrame, event: int = 0,
                 plot_setup: bool = False) -> None:
        """Initialize the beam and detector for a specific irradiation event.

        Parameters
        ----------
        data_norm : pd.DataFrame
            Dicom RDSR information from each irradiation event. See
            parse_data.py for more information.
        event : int, optional
            Specifies the index of the irradiation event in the procedure
            (the default is 0, which is the first event).
        plot_setup : bool, optional
            If True, the beam angulation info from data_norm is neglected,
            and a beam of zero angulation is created insted. This is a
            debugging feature used when positioning new phantoms or
            implementing currently unsupported venor RDSR files (the default is
            False).

        """
        # Override beam angulation if plot_setup
        if plot_setup:
            ap1 = ap2 = ap3 = 0

        else:
            # Fetch rotation angles of the X-ray tube

            # Positioner isocenter primary angle (Ap1)
            ap1 = np.deg2rad(data_norm.PPA[event])
            # Positioner isocenter secondary angle (Ap2)
            ap2 = np.deg2rad(data_norm.PSA[event])
            # Positioner isocenter detector rotation angle (Ap3)
            ap3 = 0  # PySkinDose does not yet Ap3 rotation

        # Define ratation matrix about Ap1 and Ap2 and Ap3
        R1 = np.array([[+np.cos(ap1), +np.sin(ap1), +0],
                       [-np.sin(ap1), +np.cos(ap1), +0],
                       [+0, +0, +1]])

        R2 = np.array([[+1, +0, +0],
                       [+0, +np.cos(ap2), -np.sin(ap2)],
                       [+0, +np.sin(ap2), +np.cos(ap2)]])

        R3 = np.array([[+np.cos(ap3), +0, -np.sin(ap3)],
                       [+0, +1, +0],
                       [+np.sin(ap3), +0, +np.cos(ap3)]])

        # Located X-ray source
        source = np.array([0, data_norm.DSI[event], 0])

        # Create beam-detector interception point for a beam of side length 1
        r = np.array([[+0.5, -1.0, +0.5],
                      [+0.5, -1.0, -0.5],
                      [-0.5, -1.0, -0.5],
                      [-0.5, -1.0, +0.5]])

        r[:, 0] *= data_norm.FS_long[event]  # Longitudinal collimation
        r[:, 1] *= data_norm.DID[event]  # Set source-detector distance
        r[:, 2] *= data_norm.FS_lat[event]  # Lateral collimation

        r = np.vstack([source, r])

        # Rotate beam about ap1, ap2 and ap3
        r = np.matmul(np.matmul(R2, R1).T, np.matmul(R3.T, r.T)).T

        self.r = r

        # Manually construct vertex index vector for the X-ray beam
        i = np.array([0, 0, 0, 0, 1, 1])
        j = np.array([1, 1, 3, 3, 2, 3])
        k = np.array([2, 4, 2, 4, 3, 4])
        self.ijk = np.column_stack((i, j, k))

        # Construct unit vectors from X-ray source beam verticies
        v1 = vector(r[0, :], r[1, :], normalization=True)
        v2 = vector(r[0, :], r[2, :], normalization=True)
        v3 = vector(r[0, :], r[3, :], normalization=True)
        v4 = vector(r[0, :], r[4, :], normalization=True)

        # Create the four normal vectors to the faces of the beam.
        self.N = np.vstack([np.cross(v1, v2), np.cross(v2, v3),
                            np.cross(v3, v4), np.cross(v4, v1)])

        # Create detector corners for with side length 1
        # The first four rows represent the X-ray detector surface, the last
        # four are there to give the detector some depth for 3D visualization.
        det_r = np.array([[+0.5, -1.0, +0.5],
                          [+0.5, -1.0, -0.5],
                          [-0.5, -1.0, -0.5],
                          [-0.5, -1.0, +0.5],
                          [+0.5, -1.2, +0.5],
                          [+0.5, -1.2, -0.5],
                          [-0.5, -1.2, -0.5],
                          [-0.5, -1.2, +0.5]])

        # Add detector dimensions
        detector_width = data_norm.DSL[0]
        det_r[:, 0] *= detector_width
        det_r[:, 2] *= detector_width
        # Place detector at actual distance
        det_r[:, 1] *= data_norm.DID[event]

        # Rotate detector about ap1, ap2 and ap3

        det_r = np.matmul(np.matmul(R2, R1).T, np.matmul(R3.T, det_r.T)).T
        self.det_r = det_r

        # Manually construct vertex index vector for the X-ray detector
        det_i = np.array([0, 0, 4, 4, 0, 1, 0, 3, 3, 7, 1, 1])
        det_j = np.array([1, 2, 5, 6, 1, 5, 3, 7, 2, 2, 2, 6])
        det_k = np.array([2, 3, 6, 7, 4, 4, 4, 4, 7, 6, 6, 5])
        self.det_ijk = np.column_stack((det_i, det_j, det_k))

    def check_hit(self, patient: Phantom) -> List[bool]:
        """Calculate which patient entrance skin cells are hit by the beam.

        Here, I am going to present a clearer description of this algorithm.

        Parameters
        ----------
        patient : Phantom
            Patient phantom, either of type plane, cylinder or human, i.e.
            instance of class Phantom

        Returns
        -------
        List[bool]
            A boolean list of the same length as the number of patient skin
            cells. True for all entrance skin cells that are hit by the beam.

        """
        source = self.r[0, :]
        # Create vectors from X-ray source to each phantom skin cell
        cells_vectors = [vector(source, cell) for cell in patient.r]

        # If phantom type is plane, do not controll if cell is entrance or
        # exit, since the plane is 1D
        if patient.phantom_model == "plane":
            hits = [True if
                    np.dot(cells_vectors[ind], self.N[0, :]) <= 0 and
                    np.dot(cells_vectors[ind], self.N[1, :]) <= 0 and
                    np.dot(cells_vectors[ind], self.N[2, :]) <= 0 and
                    np.dot(cells_vectors[ind], self.N[3, :]) <= 0
                    else False
                    for ind in range(len(cells_vectors))]
            return hits

        # Else if patient phantom is 3D, neglect the  skin cells that are on
        # the exit side
        hits = [True if
                np.dot(cells_vectors[ind], self.N[0, :]) <= 0 and
                np.dot(cells_vectors[ind], self.N[1, :]) <= 0 and
                np.dot(cells_vectors[ind], self.N[2, :]) <= 0 and
                np.dot(cells_vectors[ind], self.N[3, :]) <= 0 and
                np.dot(cells_vectors[ind], patient.n[ind]) <= 0
                else False
                for ind in range(len(cells_vectors))]
        return hits
