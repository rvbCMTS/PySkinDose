import os
import copy

from tqdm import tqdm
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from stl import mesh
from typing import Dict, List, Optional

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
        the phantom has been aligned in the geometry with the position_geometry
        function in geom_calc.py
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
        position_geometry function
    position(data_norm)
        Positions the phantom from reference position to actual position
        according to the table displacement info in data_norm
    """

    def __init__(self,
                 phantom_model: str, phantom_dim: PhantomDimensions,
                 human_mesh: Optional[str] = None):
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
            raise ValueError(f"Unknown phantom model selected. Valid type:"
                             f"{'.'.join(VALID_PHANTOM_MODELS)}")

        self.r_ref: np.array

        # Save table length for all phantom in order to choose correct rotation
        # origin when applying At1, At2, and At3
        self.table_length = phantom_dim.table_length

        # creates a plane phantom (2D grid)
        if phantom_model == "plane":

            # Use a dense grid if specified by user
            if phantom_dim.plane_resolution.lower() == 'dense':
                res_length = res_width = 2.0

            elif phantom_dim.plane_resolution.lower() == 'sparse':
                res_length = res_width = 1.0

            # Linearly spaced points along the longitudinal direction
            x = np.linspace(-phantom_dim.plane_width / 2,
                            +phantom_dim.plane_width / 2,
                            int(res_width * phantom_dim.plane_width + 1))
            # Linearly spaced points along the lateral direction
            y = np.linspace(0, phantom_dim.plane_length,
                            int(res_length * phantom_dim.plane_length))

            # Create phantom in form of rectangular grid
            x_plane, y_plane = np.meshgrid(x, y)

            t = phantom_dim.plane_width

            # Create index vectors for plotly mesh3d plotting
            i2: List[int] = []
            i1 = j1 = k1 = i2

            for i in range(len(x) - 1):
                for j in range(len(y) - 1):
                    i1 = i1 + [j * len(x) + i]
                    j1 = j1 + [j * len(x) + i + 1]
                    k1 = k1 + [j * len(x) + i + len(x)]
                    i2 = i2 + [j * len(x) + i + len(x) + 1]

            self.r = np.column_stack((x_plane.ravel(),
                                      y_plane.ravel(),
                                      np.zeros(len(x_plane.ravel()))))

            self.ijk = np.column_stack((i1 + i2, j1 + k1, k1 + j1))
            self.dose = np.zeros(len(self.r))

        # creates a cylinder phantom (elliptic)
        elif phantom_model == "cylinder":

            # Use a dense grid if specified by user
            if phantom_dim.cylinder_resolution.lower() == 'dense':
                res_length = 4
                res_width = 0.05

            elif phantom_dim.cylinder_resolution.lower() == 'sparse':
                res_length = 1.0
                res_width = 0.1

            # Creates linearly spaced points along an ellipse
            #  in the lateral direction
            t = np.arange(0 * np.pi, 2 * np.pi, res_width)
            x = (phantom_dim.cylinder_radii_a * np.cos(t)).tolist()
            z = (phantom_dim.cylinder_radii_b * np.sin(t)).tolist()

            # calculate normal vectors of a cylinder (pointing outwards)
            nx = np.cos(t) / (
                np.sqrt(np.square(np.cos(t) + 4 * np.square(np.sin(t)))))

            ny = np.zeros(len(t))

            nz = 2 * np.sin(t) / (
                np.sqrt(np.square(np.cos(t) + 4 * np.square(np.sin(t)))))

            nx = nx.tolist()
            ny = ny.tolist()
            nz = nz.tolist()

            n = [[nx[ind], ny[ind], nz[ind]] for ind in range(len(t))]

            # Store the  coordinates of the cylinder phantom
            output: Dict = dict(n=[], x=[], y=[], z=[])

            # Extend the ellipse to span the entire length of the phantom,
            # thus creating an elliptic cylinder
            for index in range(
                    0, int(res_length) * (phantom_dim.cylinder_length + 2), 1):

                output["x"] = output["x"] + x
                output["y"] = output["y"] + [1 / res_length * index] * len(x)
                output["z"] = output["z"] + z
                output["n"] = output["n"] + n

            # Create index vectors for plotly mesh3d plotting
            i1 = list(range(0, len(output["x"]) - len(t)))
            j1 = list(range(1, len(output["x"]) - len(t) + 1))
            k1 = list(range(len(t), len(output["x"])))
            i2 = list(range(0, len(output["x"]) - len(t)))
            k2 = list(range(len(t) - 1, len(output["x"]) - 1))
            j2 = list(range(len(t), len(output["x"])))

            self.r = np.column_stack((output["x"], output["y"], output["z"]))
            self.ijk = np.column_stack((i1 + i2, j1 + j2, k1 + k2))
            self.dose = np.zeros(len(self.r))
            self.n = np.asarray(output["n"])

        # creates a human phantom
        elif phantom_model == "human":

            if human_mesh is None:
                raise ValueError('Human model needs to be specified for'
                                 'phantom_model = "human"')

            # load selected phantom model from binary .stl file
            phantom_path = os.path.join(os.path.dirname(__file__),
                                        'phantom_data', f"{human_mesh}.stl")
            phantom_mesh = mesh.Mesh.from_file(phantom_path)

            r = phantom_mesh.vectors
            n = phantom_mesh.normals

            self.r = np.asarray([el for el_list in r for el in el_list])
            self.n = np.asarray([x for pair in zip(n, n, n) for x in pair])

            # Create index vectors for plotly mesh3d plotting
            self.ijk = np.column_stack((
                np.arange(0, len(self.r) - 3, 3),
                np.arange(1, len(self.r) - 2, 3),
                np.arange(2, len(self.r) - 1, 3)))
            self.dose = np.zeros(len(self.r))

        # Creates the vertices of the patient support table
        elif phantom_model == "table":
            # Longitudinal position of the the vertices
            x_tab = [index * phantom_dim.table_width for index in
                     [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                      0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the vertices. Replace the list y below with
            # y_pad = [index * phantom_dim.table_length for index in
            #          [0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0,
            #           0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0]]
            # in order to clearly visualize the head-end of the table. Note
            # that this extra segment is not included in table correction
            # calculations (k_tab).

            y_tab = [index * phantom_dim.table_length for index in
                     [1.0, 1.0, 1, 1, 1.0, 1.0, 0, 0,
                      1.0, 1.0, 1, 1, 1.0, 1.0, 0, 0]]

            # Vertical position of the vertices
            z_tab = [index * phantom_dim.table_thickness for index in
                     [0, 0, 0, 0, 0, 0, 0, 0,
                      -1, -1, -1, -1, -1, -1, -1, -1]]

            # Create index vectors for plotly mesh3d plotting
            i_tab = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                     1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j_tab = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                     2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k_tab = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                     9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

            self.r = np.column_stack((x_tab, y_tab, z_tab))
            self.ijk = np.column_stack((i_tab, j_tab, k_tab))

        # Creates the vertices of the patient support table
        elif phantom_model == "pad":

            # Longitudinal position of the the vertices
            x_pad = [index * phantom_dim.pad_width for index in
                     [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                      0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the the vertices
            y_pad = [index * phantom_dim.pad_length for index in
                     [1.0, 1.0, 1, 1, 1.0, 1.0, 0, 0,
                      1.0, 1.0, 1, 1, 1.0, 1.0, 0, 0]]

            # Vertical position of the vertices
            z_pad = [index * phantom_dim.pad_thickness for index in
                     [0, 0, 0, 0, 0, 0, 0, 0,
                      1, 1, 1, 1, 1, 1, 1, 1]]

            # Create index vectors for plotly mesh3d plotting
            i_pad = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                     1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j_pad = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                     2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k_pad = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                     9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

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
        Rx = np.array([[+1, +0, +0],
                       [+0, +np.cos(x_rot), -np.sin(x_rot)],
                       [+0, +np.sin(x_rot), +np.cos(x_rot)]])
        Ry = np.array([[+np.cos(y_rot), +0, +np.sin(y_rot)],
                       [+0, +1, +0],
                       [-np.sin(y_rot), +0, +np.cos(y_rot)]])
        Rz = np.array([[+np.cos(z_rot), -np.sin(z_rot), +0],
                       [+np.sin(z_rot), +np.cos(z_rot), +0],
                       [+0, +0, +1]])

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
        conducted in the function position_geometry

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

        # position phantom centered about isocenter
        self.r[:, 2] += self.table_length / 2

        # Fetch At1, At2, and At3
        rot = np.deg2rad(data_norm['At1'][event])
        tilt = np.deg2rad(data_norm['At2'][event])
        cradle = np.deg2rad(data_norm['At3'][event])

        R1 = np.array([[+np.cos(rot),   0,  +np.sin(rot)],
                      [0,              1,   0],
                      [-np.sin(rot), 0, +np.cos(rot)]])

        R2 = np.array([[+1, +0, +0],
                       [+0, +np.cos(tilt), -np.sin(tilt)],
                       [+0, +np.sin(tilt), +np.cos(tilt)]])

        R3 = np.array([[+np.cos(cradle), -np.sin(cradle), 0],
                       [+np.sin(cradle), +np.cos(cradle), +0],
                       [+0, +0, +1]])

        # Apply table rotation
        self.r = np.matmul(np.matmul(R3, np.matmul(R2, R1)), (self.r).T).T

        # Replace phantom to stanting position
        self.r[:, 2] -= self.table_length/2

        # Apply phantom translation
        t = np.array(
            [data_norm.Tx[event], data_norm.Ty[event], data_norm.Tz[event]]
            )

        self.r = self.r + t
