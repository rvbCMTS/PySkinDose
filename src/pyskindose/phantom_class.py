import copy
import os
from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from stl import mesh
from tqdm import tqdm

from pyskindose.plotting.create_ploty_ijk_indices import (
    _create_plotly_ijk_indices_for_cuboid_objects,
)

from .settings_pyskindose import PhantomDimensions

# valid phantom types
VALID_PHANTOM_MODELS = ["plane", "cylinder", "human", "table", "pad"]


class Phantom:
    """Create and handle phantoms for patient, support table and pad.

    This class creates a phatom of any of the types specified in
    VALID_PHANTOM_MODELS (plane, cylinder or human to represent the patient,
    as well as patient support table and pad). The patient phantoms consists of
    a number of skin cells where the skin dose can be calculated.

    Attributes
    ----------
    phantom_model : str
        Type of phantom, i.e. "plane", "cylinder", "human", "table" or "pad"
    r : np.array
        n*3 array where n are the number of phantom skin cells. Each row
        contains the xyz coordinate of one of the phantom skin cells
    ijk : np.array
        A matrix containing vertex indices. This is required in order to
        plot the phantom using plotly Mesh3D. For more info, see "i", "j", and
        "k" at https://plot.ly/python/reference/#mesh3d
    dose : np.array
        An empty 1d array to store skin dose calculation for each of the n
        phantom cells. Only for patient phantom types (plane, cylinder, human)
    n : np.array
        normal vectors to each of the n phantom skin cells. (only for 3D
        patient phantoms, i.e. "cylinder" and "human")
    r_ref : np.array
        Empty array to store of reference position of the phantom cells after
        the phantom has been aligned in the geometry with the
        position_patient_phantom_on_table function in geom_calc.py
    table_length : float
        length of patient support table. The is needed for all phantom object
        to select correct rotation origin for At1, At2, and At3.

    Methods
    -------
    rotate(rotation)
        Rotating the phantom about any of the x, y, or z axis
    translate(dr)
        Translates the phantom along the x, y or z direction
    save_position
        Saves the reference position after the phantom has been properly
        positioned in the irradiation geometry. This method is called in the
        position_patient_phantom_on_table function
    position(data_norm)
        Positions the phantom from reference position to actual position
        according to the table displacement info in data_norm
    """

    def __init__(self, phantom_model: str, phantom_dim: PhantomDimensions, human_mesh: Optional[str] = None):
        """Create the phantom of choice.

        Parameters
        ----------
        phantom_model : str
            Type of phantom to create. Valid selections are 'plane',
            'cylinder', 'human', "table" an "pad".
        phantom_dim : PhantomDimensions
            instance of class PhantomDimensions containing dimensions for
            all phantoms models except human phantoms: Length, width, radius,
            thickness etc.
        human_mesh : str, optional
            Choose which human mesh phantom to use. Valid selection are names
            of the *.stl-files in the phantom_data folder (The default is none.

        Raises
        ------
        ValueError
            Raises value error if unsupported phantom type are selected,
            or if phantom_model='human' selected, without specifying
            human_mesh

        """
        self.phantom_model = phantom_model.lower()
        # Raise error if invalid phantom model selected
        if self.phantom_model not in VALID_PHANTOM_MODELS:
            raise ValueError(f"Unknown phantom model selected. Valid type:" f"{'.'.join(VALID_PHANTOM_MODELS)}")

        self.r_ref: np.array

        # Save table length for all phantom in order to choose correct rotation
        # origin when applying At1, At2, and At3
        self.table_length = phantom_dim.table_length

        # creates a plane phantom (2D grid)
        if phantom_model == "plane":

            # Use a dense grid if specified by user
            if phantom_dim.plane_resolution.lower() == "dense":
                res_length = res_width = 2.0

            elif phantom_dim.plane_resolution.lower() == "sparse":
                res_length = res_width = 1.0

            # Linearly spaced points along the longitudinal direction
            x = np.linspace(
                -phantom_dim.plane_width / 2, +phantom_dim.plane_width / 2, int(res_width * phantom_dim.plane_width + 1)
            )
            # Linearly spaced points along the lateral direction
            z = np.linspace(0, -phantom_dim.plane_length, int(res_length * phantom_dim.plane_length))

            # Create phantom in form of rectangular grid
            x_plane, z_plane = np.meshgrid(x, z)

            t = phantom_dim.plane_width

            # Create index vectors for plotly mesh3d plotting
            i2: List[int] = []
            i1 = j1 = k1 = i2

            for i in range(len(x) - 1):
                for j in range(len(z) - 1):
                    i1 = i1 + [j * len(x) + i]
                    j1 = j1 + [j * len(x) + i + 1]
                    k1 = k1 + [j * len(x) + i + len(x)]
                    i2 = i2 + [j * len(x) + i + len(x) + 1]

            self.r = np.column_stack((x_plane.ravel(), np.zeros(len(x_plane.ravel())), z_plane.ravel()))

            self.ijk = np.column_stack((i1 + i2, j1 + k1, k1 + j1))
            self.dose = np.zeros(len(self.r))

        # creates a cylinder phantom (elliptic)
        elif phantom_model == "cylinder":

            # Use a dense grid if specified by user
            if phantom_dim.cylinder_resolution.lower() == "dense":
                res_length = 4
                res_width = 0.05

            elif phantom_dim.cylinder_resolution.lower() == "sparse":
                res_length = 1.0
                res_width = 0.1

            # Creates linearly spaced points along an ellipse
            #  in the lateral direction
            t = np.arange(0 * np.pi, 2 * np.pi, res_width)
            x = (phantom_dim.cylinder_radii_a * np.cos(t)).tolist()
            y = (phantom_dim.cylinder_radii_b * np.sin(t)).tolist()

            # calculate normal vectors of a cylinder (pointing outwards)
            nx = np.cos(t) / (np.sqrt(np.square(np.cos(t) + 4 * np.square(np.sin(t)))))

            nz = np.zeros(len(t))

            ny = 2 * np.sin(t) / (np.sqrt(np.square(np.cos(t) + 4 * np.square(np.sin(t)))))

            nx = nx.tolist()
            ny = ny.tolist()
            nz = nz.tolist()

            n = [[nx[ind], ny[ind], nz[ind]] for ind in range(len(t))]

            # Store the  coordinates of the cylinder phantom
            output: Dict = dict(n=[], x=[], y=[], z=[])

            # Extend the ellipse to span the entire length of the phantom,
            # thus creating an elliptic cylinder
            for index in range(0, int(res_length) * (phantom_dim.cylinder_length + 2), 1):

                output["x"] = output["x"] + x
                output["z"] = output["z"] + [-1 / res_length * index] * len(x)
                output["y"] = output["y"] + y
                output["n"] = output["n"] + n

            # Create index vectors for plotly mesh3d plotting
            i1 = list(range(0, len(output["x"]) - len(t)))
            j1 = list(range(1, len(output["x"]) - len(t) + 1))
            k1 = list(range(len(t), len(output["x"])))
            i2 = list(range(0, len(output["x"]) - len(t)))
            k2 = list(range(len(t) - 1, len(output["x"]) - 1))
            j2 = list(range(len(t), len(output["x"])))

            for i in range(len(output["y"])):
                output["y"][i] -= phantom_dim.cylinder_radii_b

            self.r = np.column_stack((output["x"], output["y"], output["z"]))
            self.ijk = np.column_stack((i1 + i2, j1 + j2, k1 + k2))
            self.dose = np.zeros(len(self.r))
            self.n = np.asarray(output["n"])

        # creates a human phantom
        elif phantom_model == "human":

            if human_mesh is None:
                raise ValueError("Human model needs to be specified for" 'phantom_model = "human"')

            # load selected phantom model from binary .stl file
            phantom_path = os.path.join(os.path.dirname(__file__), "phantom_data", f"{human_mesh}.stl")
            phantom_mesh = mesh.Mesh.from_file(phantom_path)

            r = phantom_mesh.vectors
            n = phantom_mesh.normals

            self.r = np.asarray([el for el_list in r for el in el_list])
            self.n = np.asarray([x for pair in zip(n, n, n) for x in pair])

            # Create index vectors for plotly mesh3d plotting
            self.ijk = np.column_stack(
                (np.arange(0, len(self.r) - 3, 3), np.arange(1, len(self.r) - 2, 3), np.arange(2, len(self.r) - 1, 3))
            )
            self.dose = np.zeros(len(self.r))

        # Creates the vertices of the patient support table
        elif phantom_model == "table":
            # Longitudinal position of the the vertices
            x_tab = [index * phantom_dim.table_width for index in [+0.5, +0.5, -0.5, -0.5, +0.5, +0.5, -0.5, -0.5]]

            # Vertical position of the vertices
            y_tab = [index * phantom_dim.table_thickness for index in [0, 0, 0, 0, +1, +1, +1, +1]]

            # Lateral position of the vertices
            z_tab = [index * phantom_dim.table_length for index in [0, -1, -1, 0, 0, -1, -1, 0]]

            # Create index vectors for plotly mesh3d plotting
            i_tab, j_tab, k_tab = _create_plotly_ijk_indices_for_cuboid_objects()

            self.r = np.column_stack((x_tab, y_tab, z_tab))
            self.ijk = np.column_stack((i_tab, j_tab, k_tab))

        # Creates the vertices of the patient support table
        elif phantom_model == "pad":

            # Longitudinal position of the the vertices
            x_pad = [index * phantom_dim.pad_width for index in [+0.5, +0.5, -0.5, -0.5, +0.5, +0.5, -0.5, -0.5]]

            # Vertical position of the vertices
            y_pad = [index * phantom_dim.pad_thickness for index in [0, 0, 0, 0, -1, -1, -1, -1]]

            # Lateral position of the the vertices
            z_pad = [index * phantom_dim.pad_length for index in [0, -1, -1, 0, 0, -1, -1, 0]]

            # Create index vectors for plotly mesh3d plotting
            i_pad, j_pad, k_pad = _create_plotly_ijk_indices_for_cuboid_objects()

            self.r = np.column_stack((x_pad, y_pad, z_pad))
            self.ijk = np.column_stack((i_pad, j_pad, k_pad))

    def rotate(self, angles: List[int]) -> None:
        """Rotate the phantom about the angles specified in rotation.

        Parameters
        ----------
        angles: List[int]
            list of angles in degrees the phantom should be rotated about,
            given as [x_rot: <int>, y_rot: <int>, z_rot: <int>]. E.g.
            rotation = [0, 90, 0] will rotate the phantom 90 degrees about the
            y-axis.

        """
        # convert degrees to radians
        angles = np.deg2rad(angles)

        x_rot = angles[0]
        y_rot = angles[1]
        z_rot = angles[2]

        # Define rotation matricies about the x, y and z axis
        Rx = np.array([[+1, +0, +0], [+0, +np.cos(x_rot), -np.sin(x_rot)], [+0, +np.sin(x_rot), +np.cos(x_rot)]])
        Ry = np.array([[+np.cos(y_rot), +0, +np.sin(y_rot)], [+0, +1, +0], [-np.sin(y_rot), +0, +np.cos(y_rot)]])
        Rz = np.array([[+np.cos(z_rot), -np.sin(z_rot), +0], [+np.sin(z_rot), +np.cos(z_rot), +0], [+0, +0, +1]])

        # Rotate position vectors to the phantom cells

        self.r = np.matmul(Rx, np.matmul(Ry, np.matmul(Rz, self.r.T))).T

        if self.phantom_model in ["cylinder", "human"]:

            self.n = np.matmul(Rx, np.matmul(Ry, np.matmul(Rz, self.n.T))).T

    def translate(self, dr: List[int]) -> None:
        """Translate the phantom in the x, y or z direction.

        Parameters
        ----------
        dr : List[int]
            list of distances the phantom should be translated, given in cm.
            Specified as dr = [dx: <int>, dy: <int>, dz: <int>]. E.g.
            dr = [0, 0, 10] will translate the phantom 10 cm in the z direction

        """
        self.r[:, 0] += dr[0]
        self.r[:, 1] += dr[1]
        self.r[:, 2] += dr[2]

    def save_position(self) -> None:
        """Store a reference position of the phantom.

        This function is supposed to be used to store the patient fixation
        conducted in the function position_patient_phantom_on_table

        """
        r_ref = copy.copy(self.r)
        self.r_ref = r_ref

    def position(self, data_norm: pd.DataFrame, event: int) -> None:
        """Position the phantom for a event by adding RDSR table displacement.

        Positions the phantom from reference position to actual position
        according to the table displacement info in data_norm.

        Parameters
        ----------
        data_norm : pd.DataFrame
            Table containing dicom RDSR information from each irradiation event
            See rdsr_normalizer.py for more information.
        event : int
            Irradiation event index

        """
        self.r = copy.copy(self.r_ref)

        # Fetch rotation angles of the patient, table, and pad

        # Table Horizontal Rotation Angle (At1)
        # i.e. rotation of the table about the positive y axis (VERT),
        # with rotation axis in the center of the table.
        at1 = np.deg2rad(data_norm["At1"][event])
        # Table Head Tilt Angle (At2)
        # i.e. rotation of the table about the positive x axis (LON)
        # with rotation axis in the center of the table.
        at2 = np.deg2rad(data_norm["At2"][event])
        # Table Cradle Tilt Angle (At3)
        # i.e. rotation of the table about the z axis (LAT)
        at3 = np.deg2rad(data_norm["At3"][event])

        # displace phantom to table rotation center
        self.r[:, 2] += self.table_length / 2

        # calculate rotation about x axis
        angle = at2
        Rx = np.array([[+1, +0, +0], [+0, +np.cos(angle), -np.sin(angle)], [+0, +np.sin(angle), +np.cos(angle)]])

        # calculate rotation about y axis
        angle = at1
        Ry = np.array([[+np.cos(angle), +0, +np.sin(angle)], [+0, +1, +0], [-np.sin(angle), +0, +np.cos(angle)]])

        # calculate rotation about z axis
        angle = at3
        Rz = np.array([[+np.cos(angle), -np.sin(angle), +0], [+np.sin(angle), +np.cos(angle), +0], [+0, +0, +1]])

        # Apply table rotation
        self.r = np.matmul(Rz, np.matmul(Ry, np.matmul(Rx, self.r.T))).T

        # Replace phantom back to starting position
        self.r[:, 2] -= self.table_length / 2

        # Apply phantom translation
        t = np.array([data_norm.Tx[event], data_norm.Ty[event], data_norm.Tz[event]])

        self.r = self.r + t
