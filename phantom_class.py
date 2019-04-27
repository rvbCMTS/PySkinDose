from typing import List, Optional
from settings import PhantomDimensions
import plotly.graph_objs as go
import plotly.offline as ply
from stl import mesh
import pandas as pd
import numpy as np
import copy
import os

# valid phantom types
VALID_PHANTOM_TYPES = ["plane", "cylinder", "human", "table", "pad"]

class Phantom:
    """Create and handle phantoms for patient, support table and pad.

    This class creates a phatom of any of the types specified in
    VALID_PHANTOM_TYPES (plane, cylinder or human to represent the patient,
    as well as patient support table and pad). The patient phantoms consists of
    a number of skin cells where the skin dose can be calculated.

    Attributes
    ----------
    type : str
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
    plot_dosemap
        Creates and plots a plotly mesh3D plot, where the intensity in each
        phantom skin cell corresponds to the estimated skin dose.

    """
    def __init__(self,
                 phantom_model: str, phantom_dim: PhantomDimensions,
                 human_model: Optional[str] = None):
        """Create the phantom of choice.

        Parameters
        ----------
        phantom_model : str
            Type of phantom. Valid selections are 'plane', 'cylinder', 'human',
            "table" an "pad".
        phantom_dim : PhantomDimensions
            instance of class PhantomDimensions containing dimensions for
            all phantoms models except human phantoms: Length, width, radius,
            thickness etc.
        human_model : str, optional
            Choose which human phantom to use. Valid selection are names of the
            *.stl-files in the phantom_data folder (The default is none.

        Raises
        ------
        ValueError
            Raises value error if unsupported phantom type are selected,
            or if phantom_model='human' selected, without specifying
            human_model

        """
        phantom_model = phantom_model.lower()

        # Raise error if invalid phantom model selected
        if phantom_model not in VALID_PHANTOM_TYPES:
            raise ValueError(f"Unknown phantom model selected. Valid type:"
                             f"{'.'.join(VALID_PHANTOM_TYPES)}")

        # creates a plane phantom (2D grid)
        if phantom_model == "plane":
            self.type = "plane"

            # Linearly spaced (1 cm) point along the longitudinal direction
            x_range = np.linspace(-0.5 * phantom_dim.plane_width,
                                  +0.5 * phantom_dim.plane_width,
                                  phantom_dim.plane_width + 1)
            # Linearly spaced (1 cm) point along the lateral direction
            y_range = np.linspace(0, phantom_dim.plane_length,
                                  phantom_dim.plane_length + 1)
            # Create phantom in form of rectangular grid
            x, y = np.meshgrid(x_range, y_range)

            t = phantom_dim.plane_width

            # Create index vectors for plotly mesh3d plotting
            i1 = i2 = j1 = j2 = k1 = k2 = list()  # type: List[str]

            for a in range(phantom_dim.plane_length):
                i1 = i1 + list(range
                               (a * t + a, (a + 1) * t + a))
                j1 = j1 + list(range
                               ((a + 1) * t + (a + 1), (a + 2) * t + (a + 1)))
                k1 = k1 + list(range
                               ((a + 1) * t + (a + 2), (2 + a) * t + (a + 2)))
                i2 = i2 + list(range
                               (a * t + a, (a + 1) * t + a))
                j2 = j2 + list(range
                               (a * t + (a + 1), (a + 1) * (t + 1)))
                k2 = k2 + list(range
                               ((a + 1) * t + (a + 2), (a + 2) * t + (a + 2)))

            self.r = np.column_stack((x.ravel(), y.ravel(),
                                      np.zeros(len(x.ravel()))))

            self.ijk = np.column_stack((i1 + i2, j1 + j2, k1 + k2))
            self.dose = np.zeros(len(self.r))

        # creates a cylinder phantom (elliptic)
        elif phantom_model == "cylinder":
            self.type = "cylinder"

            # Creates linearly spaced points along an ellipse
            #  in the lateral direction
            t = np.arange(0, 2 * np.pi, 0.1)
            x = (phantom_dim.cylinder_radii_a * np.cos(t)).tolist()
            z = (phantom_dim.cylinder_radii_b * np.sin(t)).tolist()

            n = [[x[ind], 0.0, z[ind]] for ind in range(len(t))]

            # Store the  coordinates of the cylinder phantom
            output = {"type": "cylinder", "n": [],
                      "x": [], "y": [], "z": []}

            # Extend the ellipse to span the entire length of the phantom,
            # in steps of 1 cm, thus creating an elliptic cylinder
            for index in range(0, phantom_dim.cylinder_length + 2, 1):
                output["x"] = output["x"] + x
                output["y"] = output["y"] + [index] * len(x)
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
            self.type = "human"

            if human_model is None:
                raise ValueError('Human model needs to be specified for'
                'phantom_model = "human"')

            # load selected phantom model from binary .stl file
            phantom_path = os.path.join(os.path.dirname(__file__),
                                        'phantom_data', f"{human_model}.stl")
            phantom_mesh = mesh.Mesh.from_file(phantom_path)

            r = phantom_mesh.vectors
            n = phantom_mesh.normals

            self.r = np.asarray([el for el_list in r
                                 for el in el_list])
            self.n = np.asarray([
                x for pair in zip(n, n, n) for x in pair])

            # Create index vectors for plotly mesh3d plotting
            self.ijk = np.column_stack((
                np.arange(0, len(self.r) - 3, 3),
                np.arange(1, len(self.r) - 2, 3),
                np.arange(2, len(self.r) - 1, 3)))

            self.dose = np.zeros(len(self.r))

        # Creates the vertices of the patient support table
        elif phantom_model == "table":
            self.type = "table"

            # Longitudinal position of the the vertices
            x = [index * phantom_dim.table_width for index in
                 [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                  0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the the vertices
            y = [index * phantom_dim.table_length for index in
                 [0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0,
                  0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0]]

            # Vertical position of the vertices
            z = [index * phantom_dim.table_thickness for index in
                 [0, 0, 0, 0, 0, 0, 0, 0,
                 -1, -1, -1, -1, -1, -1, -1, -1]]

            # Create index vectors for plotly mesh3d plotting
            i = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

            self.r = np.column_stack((x, y, z))
            self.ijk = np.column_stack((i, j, k))

        # Creates the vertices of the patient support table
        elif phantom_model == "pad":
            self.type = "pad"

            # Longitudinal position of the the vertices
            x = [index * phantom_dim.pad_width for index in
                 [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                  0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the the vertices
            y = [index * phantom_dim.pad_length for index in
                 [0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0,
                  0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0]]

            # Vertical position of the vertices
            z = [index * phantom_dim.pad_thickness for index in
                 [0, 0, 0, 0, 0, 0, 0, 0,
                 1, 1, 1, 1, 1, 1, 1, 1]]

            # Create index vectors for plotly mesh3d plotting
            i = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

            self.r = np.column_stack((x, y, z))
            self.ijk = np.column_stack((i, j, k))

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
        for i in range(len(self.r)):
            self.r[i, :] = np.dot(Rx, np.dot(Ry, np.dot(Rz, self.r[i, :])))

        if self.type in ["cylinder", "human"]:
            for i in range(len(self.n)):
                self.n[i, :] = np.dot(Rx, np.dot(Ry, np.dot(Rz, self.n[i, :])))

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

    def position(self, data_norm: pd.DataFrame, i: int) -> None:
        """Position the phantom for a event by adding RDSR table displacement.

        Positions the phantom from reference position to actual position
        according to the table displacement info in data_norm.

        Parameters
        ----------
        data_norm : pd.DataFrame
            Table containing dicom RDSR information from each irradiation event
            See parse_data.py for more information.

        """
        self.r = copy.copy(self.r_ref)

        self.r[:, 0] += data_norm.dLONG[i]
        self.r[:, 1] += data_norm.dVERT[i]
        self.r[:, 2] += data_norm.dLAT[i]

    def plot_dosemap(self):
        """Plot a map of the absorbed skindose upon the patient phantom.

        This function creates and plots an offline plotly graph of the
        skin dose distribution on the phantom. The colorscale is mapped to the
        absorbed skin dose value. Only available for phantom type: "plane",
        "cylinder" or "human"
        """

        hover_text = [f"<b>coordinate:</b><br>LAT: {np.around(self.r[ind, 2])} cm\
                  <br>LON: {np.around(self.r[ind, 0])} cm\
                  <br>VER: {np.around(self.r[ind, 1])} cm\
                      <br><b>skin dose:</b><br>{round(self.dose[ind],2)} mGy"
                      for ind in range(len(self.r))]

        # create mesh object for the phantom
        phantom_mesh = [
            go.Mesh3d(
                x=self.r[:, 0], y=self.r[:, 1], z=self.r[:, 2],
                i=self.ijk[:, 0], j=self.ijk[:, 1], k=self.ijk[:, 2],
                intensity=self.dose, colorscale="Jet", showscale=True,
                hoverinfo='text',
                text=hover_text, name="Human",
                colorbar=dict(tickfont=dict(color="white"),
                              title="Skin dose [mGy]",
                              titlefont=dict(color="white")))]

        # Layout settings
        layout = go.Layout(
            font=dict(family='roboto', color="white", size=18),
            hoverlabel=dict(font=dict(size=16)),
            title='<b>P</b>y<b>S</b>kin<b>D</b>ose[dev]<br>mode: dosemap',
            titlefont=dict(family='Courier New', size=35,
                           color='white'),
            plot_bgcolor='rgb(45,45,45)',
            paper_bgcolor='rgb(45,45,45)',

            scene=dict(aspectmode="data",
                       xaxis=dict(title='',
                                  showgrid=False, showticklabels=False),
                       yaxis=dict(title='',
                                  showgrid=False, showticklabels=False),
                       zaxis=dict(title='',
                                  showgrid=False, showticklabels=False)))

        # create figure
        fig = go.Figure(data=phantom_mesh, layout=layout)
        # Execure plot
        ply.plot(fig, filename='dose_map.html')
