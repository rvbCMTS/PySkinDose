from typing import List

import numpy as np
import pandas as pd

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
        by the X-ray beam. For 3D phantoms, skin cells on the beams exit path
        are neglected.

    """

    def __init__(self, data_norm: pd.DataFrame, event: int = 0, plot_setup: bool = False) -> None:
        """Initialize the beam and detector for a specific irradiation event.

        Parameters
        ----------
        data_norm : pd.DataFrame
            Dicom RDSR information from each irradiation event. See
            rdsr_normalizer.py for more information.
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
            # i.e. rotation of the X-ray beam and detector about the z
            # axis (LAT)
            ap1 = np.deg2rad(data_norm.Ap1[event])
            # Positioner isocenter secondary angle (Ap2)
            # i.e. rotation of the X-ray beam and detector about the x axis
            # (LON)
            ap2 = np.deg2rad(data_norm.Ap2[event])
            # Positioner isocenter detector rotation angle (Ap3)
            # i.e. rotation of the X-ray detector about the y axis (VERT)
            ap3 = np.deg2rad(data_norm.Ap3[event])

        # calculate rotation about x axis
        angle = ap2
        Rx = np.array(
            [
                [+1, +0, +0],
                [+0, +np.cos(angle), -np.sin(angle)],
                [+0, +np.sin(angle), +np.cos(angle)],
            ]
        )

        # calculate rotation about y axis
        angle = ap3
        Ry = np.array(
            [
                [+np.cos(angle), +0, +np.sin(angle)],
                [+0, +1, +0],
                [-np.sin(angle), +0, +np.cos(angle)],
            ]
        )

        # calculate rotation about z axis
        angle = ap1
        Rz = np.array(
            [
                [+np.cos(angle), -np.sin(angle), +0],
                [+np.sin(angle), +np.cos(angle), +0],
                [+0, +0, +1],
            ]
        )

        # calculate source-isocenter displacement at ap1 = ap2 = 0
        delta_r = np.array([0, data_norm.DSI[event], 0])

        # Create unit-beam in the positioner coordinate system
        r = np.array(
            [
                [0, 0, 0],  # r0 (i.e. X-ray source)
                [+0.5, -1.0, +0.5],  # r+
                [+0.5, -1.0, -0.5],  # r+-
                [-0.5, -1.0, -0.5],  # r-
                [-0.5, -1.0, +0.5],  # r-+
            ]
        )
        r[1:, 1] *= data_norm.DSD[event]
        r[1:, 0] *= data_norm.FS_long[event]  # Append longitudinal collimation
        r[1:, 2] *= data_norm.FS_lat[event]  # Append lateral collimation

        # Transform the beam from the positioner coordinate system to the
        # isocenter coordinate system. Note! The transpose operations are
        # needed to broadcast over all vectors in r
        r = np.matmul(Rz, np.matmul(Rx, (r + delta_r).T)).T

        self.r = r

        # Manually create vertex index vector for the X-ray beam
        self.ijk = np.column_stack(([0, 0, 0, 0, 1, 1], [1, 1, 3, 3, 2, 3], [2, 4, 2, 4, 3, 4]))

        # Create unit vectors from X-ray source to beam verticies
        v = ((self.r[1:] - self.r[0, :]).T / np.linalg.norm(self.r[1:] - self.r[0, :], axis=1)).T

        # Create the four normal vectors to the faces of the beam.
        self.N = np.vstack(
            [
                np.cross(v[0, :], v[1, :]),
                np.cross(v[1, :], v[2, :]),
                np.cross(v[2, :], v[3, :]),
                np.cross(v[3, :], v[0, :]),
            ]
        )

        # Create detector corners for with side length 1
        # The first four rows represent the X-ray detector surface, the last
        # four are there to give the detector some depth for 3D visualization.
        det_r = np.array(
            [
                [+0.5, -1.0, +0.5],
                [+0.5, -1.0, -0.5],
                [-0.5, -1.0, -0.5],
                [-0.5, -1.0, +0.5],
                [+0.5, -1.2, +0.5],
                [+0.5, -1.2, -0.5],
                [-0.5, -1.2, -0.5],
                [-0.5, -1.2, +0.5],
            ]
        )

        # Add detector dimensions
        detector_width = data_norm.DSL[0]
        det_r[:, 0] *= detector_width
        det_r[:, 2] *= detector_width
        # Place detector at actual distance
        det_r[:, 1] *= data_norm.DID[event]

        # Transform the detector from the positioner coordinate system to
        # the isocenter coordinate system. Note! The transpose operations
        # are needed to broadcast over all vector in r_det
        det_r = np.matmul(Rz, np.matmul(Ry, np.matmul(Rx, det_r.T))).T

        self.det_r = det_r

        # Manually construct vertex index vector for the X-ray detector
        self.det_ijk = np.column_stack(
            (
                [0, 0, 4, 4, 0, 1, 0, 3, 3, 7, 1, 1],
                [1, 2, 5, 6, 1, 5, 3, 7, 2, 2, 2, 6],
                [2, 3, 6, 7, 4, 4, 4, 4, 7, 6, 6, 5],
            )
        )

    def check_hit(self, patient: Phantom) -> List[bool]:
        """Calculate which patient entrance skin cells are hit by the beam.

        A description of this algoritm is presented in the wiki, please visit
        https://pyskindose.readthedocs.io/en/latest/

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
        # Create vectors from X-ray source to each phantom skin cell
        v = patient.r - self.r[0, :]

        # Check which skin cells lies within the beam
        hits = (np.dot(v, self.N.T) <= 0).all(axis=1)
        # if patient phantom is 3D, remove exit path skin cells
        if patient.phantom_model != "plane":
            temp1 = v[hits]
            temp2 = patient.n[hits]

            bool_entrance = [np.dot(temp1[i], temp2[i]) <= 0 for i in range(len(temp1))]

            hits[np.where(hits)] = bool_entrance

        return hits.tolist()
