import copy
from itertools import chain
from pathlib import Path
from tempfile import TemporaryFile
from typing import Dict, List, Optional, Union

import numpy as np
import pandas as pd
from stl import mesh

from pyskindose.plotting.create_ploty_ijk_indices import (
    _create_plotly_ijk_indices_for_cuboid_objects,
)
from pyskindose.settings.phantom_dimensions import PhantomDimensions

# valid phantom types
VALID_PHANTOM_MODELS = ["plane", "cylinder", "human", "table", "pad"]


class Phantom:
    """Create and handle phantoms for patient, support table and pad.

    This class creates a phantom of any of the types specified in
    VALID_PHANTOM_MODELS (plane, cylinder or human to represent the patient,
    as well as patient support table and pad). The patient phantoms consists of
    a number of skin cells where the skin dose can be calculated.

    Attributes
    ----------
    phantom_model : str
        Type of phantom, i.e. "plane", "cylinder", "human", "table" or "pad"
    r : np.ndarray
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


    """

    def __init__(
        self,
        phantom_model: str,
        phantom_dim: PhantomDimensions,
        human_mesh: Optional[Union[str, tuple[str, mesh.Mesh]]] = None,
    ):
        """Create the phantom of choice.

        Parameters
        ----------
        phantom_model : str
            Type of phantom to create. Valid selections are 'plane',
            'cylinder', 'human', "table", and "pad".
        phantom_dim : PhantomDimensions
            instance of class PhantomDimensions containing dimensions for
            all phantoms models except human phantoms: Length, width, radius,
            thickness etc.
        human_mesh : str | tuple[str, mes.Mesh | temp_file], optional
            Choose which human mesh phantom to use. Valid selection are names
            of the *.stl-files in the phantom_data folder or a custom phantom
            sent in as either a mesh object or a svg given as a temp_file object
            (The default is none).

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

        self.human_model = None

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

            # Store the  coordinates of the cylinder phantom, extended to span the entire length of the phantom, thus
            # creating an elliptical cylinder
            tmp_len = int(res_length) * (phantom_dim.cylinder_length + 2)
            output: dict = {
                "n": n * tmp_len,
                "x": x * tmp_len,
                "y": [el - phantom_dim.cylinder_radii_b for el in (y * tmp_len)],
                "z": list(chain(*[[-1 / res_length * ind] * len(x) for ind in range(tmp_len)])),
            }

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
                raise ValueError("Human model needs to be specified for" 'phantom_model = "human"')

            if isinstance(human_mesh, str):
                # load selected phantom model from binary .stl file
                self.human_model = human_mesh
                phantom_path = Path(__file__).parent / f"phantom_data/{human_mesh}.stl"
                phantom_mesh = mesh.Mesh.from_file(str(phantom_path.absolute()))
            elif isinstance(human_mesh, tuple):
                self.human_model, phantom_mesh = self._get_phantom_mesh_from_tuple(human_mesh)
            else:
                raise ValueError("No human model specified while 'phantom_model' is 'human'")

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
            # Longitudinal position of the vertices
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

            # Longitudinal position of the vertices
            x_pad = [index * phantom_dim.pad_width for index in [+0.5, +0.5, -0.5, -0.5, +0.5, +0.5, -0.5, -0.5]]

            # Vertical position of the vertices
            y_pad = [index * phantom_dim.pad_thickness for index in [0, 0, 0, 0, -1, -1, -1, -1]]

            # Lateral position of the vertices
            z_pad = [index * phantom_dim.pad_length for index in [0, -1, -1, 0, 0, -1, -1, 0]]

            # Create index vectors for plotly mesh3d plotting
            i_pad, j_pad, k_pad = _create_plotly_ijk_indices_for_cuboid_objects()

            self.r = np.column_stack((x_pad, y_pad, z_pad))
            self.ijk = np.column_stack((i_pad, j_pad, k_pad))

    @staticmethod
    def _get_phantom_mesh_from_tuple(
        phantom_mesh_tuple: tuple[str, Union[mesh.Mesh, TemporaryFile, str]]
    ) -> tuple[str, mesh.Mesh]:
        if not isinstance(phantom_mesh_tuple[0], str):
            raise TypeError(
                "If human_mesh is specified as a tuple, the first element must be the phantom name as a string"
            )

        if isinstance(phantom_mesh_tuple[1], mesh.Mesh):
            return phantom_mesh_tuple

        return phantom_mesh_tuple[0], mesh.Mesh.from_file(phantom_mesh_tuple[1])

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

        # displace phantom to table rotation center
        self.r[:, 2] += self.table_length / 2

        # Apply table rotation
        self.r = np.matmul(
            data_norm.Rz[event], np.matmul(data_norm.Ry[event], np.matmul(data_norm.Rx[event], self.r.T))
        ).T

        # Replace phantom back to starting position
        self.r[:, 2] -= self.table_length / 2

        # Apply phantom translation
        t = np.array([data_norm.Tx[event], data_norm.Ty[event], data_norm.Tz[event]])

        self.r = self.r + t
