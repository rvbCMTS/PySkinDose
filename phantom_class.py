from typing import List, Dict, Optional
import plotly.graph_objs as go
import plotly.offline as ply
from geom_calc import *
from stl import mesh
import numpy as np
import os

# valid phantom types
VALID_PHANTOM_TYPES = ["plane", "cylinder", "human", "table", "pad"]
# default phantom type
DEFAULT_PHANTOM_TYPE = "human"
# default human model (choose from phantom_data) folder
DEFAULT_HUMAN_MODEL = "adult_male"

# default phantom dimensions for plane- and cylinder phantom
DEFAULT_PHANTOM_DIM = {"plane_length": 180,
                       "plane_width": 50,
                       "cylinder_length": 160,
                       "cylinder_radii_a": 20,
                       "cylinder_radii_b": 10,
                       "table_width": 50,
                       "table_length": 210,
                       "table_thickness": 5,
                       "pad_width": 45,
                       "pad_length": 200,
                       "pad_thickness": 4,
                       "units": "cm"}


class Phantom:
    """This class creates a phatom of any of the types specified in
       VALID_PHANTOM_TYPES and plots the phantom in a plotly 3D mesh for
       radiation skin dose visualization."""

    # REMOVE OPTIONAL?
    def __init__(self,
                 phantom_type: Optional[str] = DEFAULT_PHANTOM_TYPE,
                 phantom_dim: Optional[dict] = DEFAULT_PHANTOM_DIM,
                 human_model: Optional[str] = DEFAULT_HUMAN_MODEL):
        """
        :param phantom_type:    Type of phantom. Valid selections are
                                'plane', 'cylinder', 'human' and "table".

        :param phantom_dim:     Dimensions of the mathematical phantoms (plane
                                or cylinder) given as {"plane_length": <int>,
                                "plane_width": <int>, "cylinder_length":
                                <float>, "cylinder_radii_a": <float>,
                                "cylinder_radii_b": <float>} where radii "a"
                                and "b" are the radii of an eliptical cylinder,
                                i.e., if a and b are equal, it will be a
                                perfect cylinder. EXPAND THIS

        :param human_model:     Choose which human phantom to use. Valid
                                selection are names of the *.stl-files in the
                                phantom_data folder."""

        # Raise error if invalid phantom type selected
        if phantom_type.lower() not in VALID_PHANTOM_TYPES:
            raise ValueError(f"Unknown phantom type selected. Valid type:"
                             "{'.'.join(VALID_PHANTOM_TYPES)}")

        # [multiple statements on one line (colon) [E701]]
        self.x: np.ndarray = None
        self.y: np.ndarray = None
        self.z: np.ndarray = None
        self.r: List[List[float]] = None

        self.i: Optional[np.ndarray] = None
        self.j: Optional[np.ndarray] = None
        self.k: Optional[np.ndarray] = None
        self.r_t: List[List[float]] = None

        self.normals: np.ndarray = None
        # trinagles
        self.type: str = phantom_type.lower()
        self.dose: Optional[List[float]] = None

        # creates a plane phantom (2D grid)
        if phantom_type.lower() == "plane":

            # Linearly spaced (1 cm) point along the longitudinal direction
            x_range = np.linspace(-0.5 * phantom_dim["plane_width"],
                                  +0.5 * phantom_dim["plane_width"],
                                  phantom_dim["plane_width"] + 1)

            # Linearly spaced (1 cm) point along the lateral direction
            y_range = np.linspace(0, phantom_dim["plane_length"],
                                  phantom_dim["plane_length"] + 1)

            # Create phantom in form of rectangular grid
            x, y = np.meshgrid(x_range, y_range)

            t = phantom_dim["plane_width"]

            i1 = i2 = j1 = j2 = k1 = k2 = []

            for i in range(phantom_dim["plane_length"]):
                i1 = i1 + list(range
                               (i * t + i, (i + 1) * t + i))
                j1 = j1 + list(range
                               ((i + 1) * t + (i + 1), (i + 2) * t + (i + 1)))
                k1 = k1 + list(range
                               ((i + 1) * t + (i + 2), (2 + i) * t + (i + 2)))
                i2 = i2 + list(range
                               (i * t + i, (i + 1) * t + i))
                j2 = j2 + list(range
                               (i * t + (i + 1), (i + 1) * (t + 1)))
                k2 = k2 + list(range
                               ((i + 1) * t + (i + 2), (i + 2) * t + (i + 2)))

            self.type = "plane"
            self.x = x.ravel().tolist()
            self.y = y.ravel().tolist()
            self.z = [0] * len(self.x)
            self.i = i1 + i2
            self.j = j1 + j2
            self.k = k1 + k2
            self.triangles = [[i[s], j[s], k[s]] for s in range(len(i))]
            self.dose = [0] * len(self.x)
            self.r = [[self.x[ind], self.y[ind], self.z[ind]]
                      for ind in range(len(self.x))]

        # creates a cylinder phantom (elliptic)
        elif phantom_type.lower() == "cylinder":

            # Creates linearly spaced points along an ellipse
            #  in the lateral direction
            t = np.arange(0, 2 * np.pi, 0.1)
            x = (phantom_dim["cylinder_radii_a"] * np.cos(t)).tolist()
            z = (phantom_dim["cylinder_radii_b"] * np.sin(t)).tolist()

            # issue: list input
            n = [[x[ind], 0.0, z[ind]] for ind in range(len(t))]

            # Store the  coordinates of the cylinder phantom
            output = {"type": "cylinder", "normals": [],
                      "x": [], "y": [], "z": []}

            # Extend the ellipse to span the entire length of the phantom,
            # in steps ofFFFF 10 cm, thus creating an elliptic cylinder
            for index in range(0, phantom_dim["cylinder_length"] + 1, 1):
                output["x"] = output["x"] + x
                output["z"] = output["z"] + z
                output["normals"] = output["normals"] + n
                output["y"] = output["y"] + [index] * len(x)

            i1 = list(range(0, len(output["x"]) - len(t)))
            j1 = list(range(1, len(output["x"]) - len(t) + 1))
            k1 = list(range(len(t), len(output["x"])))

            i2 = list(range(0, len(output["x"]) - len(t)))
            k2 = list(range(len(t) - 1, len(output["x"]) - 1))
            j2 = list(range(len(t), len(output["x"])))

            self.type = "cylinder"
            self.x = output["x"]
            self.y = output["y"]
            self.z = output["z"]
            self.i = i1 + i2
            self.j = j1 + j2
            self.k = k1 + k2
            self.dose = [0] * len(output['x'])
            self.normals = output["normals"]
            self.triangles = [[self.i[ind], self.j[ind], self.k[ind]]
                              for ind in range(len(self.i))]
            self.r = [[self.x[ind], self.y[ind], self.z[ind]]
                      for ind in range(len(self.x))]

        # creates a human phantom
        elif phantom_type.lower() == "human":

            # load selected phantom model from binary .stl file
            phantom_path = os.path.join(os.path.dirname(__file__),
                                        'phantom_data', f"{human_model}.stl")

            phantom_mesh = mesh.Mesh.from_file(phantom_path)

            self.type = "human"
            self.r = [el for el_list in phantom_mesh.vectors for el in el_list]
            self.x = [self.r[ind][0] for ind in range(len(self.r))]
            self.y = [self.r[ind][1] for ind in range(len(self.r))]
            self.z = [self.r[ind][2] for ind in range(len(self.r))]
            
            self.i = np.arange(0, len(self.r) - 3, 3)
            self.j = np.arange(1, len(self.r) - 2, 3)
            self.k = np.arange(2, len(self.r) - 1, 3)
            self.triangles = [[self.i[ind], self.j[ind], self.k[ind]]
                              for ind in range(len(self.i))]

            n = phantom_mesh.normals
            self.normals = [x for pair in zip(n, n, n) for x in pair]

            # Preallocate memory for skin dose mapping
            self.dose = [0] * len(self.r)
            self.type = "human"

        # Creates the vertices of the patient support table
        elif phantom_type.lower() == "table":

            # Longitudinal position of the the vertices
            x = [index * phantom_dim["table_width"] for index in
                 [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                  0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the the vertices
            y = [index * phantom_dim["table_length"] for index in
                 [0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0,
                  0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0]]

            # Vertical position of the vertices
            z = [index * phantom_dim["table_thickness"] for index in
                                    [0, 0, 0, 0, 0, 0, 0, 0,
                                     -1, -1, -1, -1, -1, -1, -1, -1]]

            r = [[x[ind], y[ind], z[ind]] for ind in range(len(x))]

            i = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

            self.type = "table"
            self.x = x
            self.y = y
            self.z = z
            self.i = i
            self.j = j
            self.k = k
            self.r = [[x[ind], y[ind], z[ind]] for ind in range(len(x))]
            self.triangles = [[i[ind], j[ind], k[ind]]
                              for ind in range(len(i))]
            self.dose = [0] * len(self.x)

        # Creates the vertices of the patient support table
        elif phantom_type.lower() == "pad":

            # Longitudinal position of the the vertices
            x = [index * phantom_dim["pad_width"] for index in
                 [0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5,
                  0.5, 0.25, 0.25, -0.25, -0.25, -0.5, -0.5, 0.5]]

            # Lateral position of the the vertices
            y = [index * phantom_dim["pad_length"] for index in
                 [0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0,
                  0.9, 0.9, 1, 1, 0.9, 0.9, 0, 0]]

            # Vertical position of the vertices
            z = [index * phantom_dim["pad_thickness"] for index in
                                  [0, 0, 0, 0, 0, 0, 0, 0,
                                   1, 1, 1, 1, 1, 1, 1, 1]]

            r = [[x[ind], y[ind], z[ind]] for ind in range(len(x))]

            i = [0, 0, 1, 1, 8, 8, 9, 9, 0, 7, 0, 1,
                 1, 2, 2, 3, 3, 4, 4, 5, 5, 6, 6, 7]

            j = [5, 6, 2, 3, 13, 14, 10, 11, 7, 15, 1, 9,
                 2, 10, 3, 11, 4, 12, 5, 13, 6, 14, 7, 15]

            k = [6, 7, 3, 4, 14, 15, 11, 12, 8, 8, 8, 8,
                 9, 9, 10, 10, 11, 11, 12, 12, 13, 13, 14, 14]

            self.type = "pad"
            self.x = x
            self.x = x
            self.y = y
            self.z = z
            self.i = i
            self.j = j
            self.k = k
            self.r = [[x[ind], y[ind], z[ind]] for ind in range(len(x))]
            self.triangles = [[i[ind], j[ind], k[ind]]
                              for ind in range(len(i))]
            self.dose = [0] * len(self.x)

    def _rotate(self, rotation):

        rotation = np.deg2rad(rotation)

        x_rot = rotation[0]
        y_rot = rotation[1]
        z_rot = rotation[2]

        Rx = np.array([[+1, +0, +0],
                       [+0, +np.cos(x_rot), -np.sin(x_rot)],
                       [+0, +np.sin(x_rot), +np.cos(x_rot)]])

        Ry = np.array([[+np.cos(y_rot), +0, +np.sin(y_rot)],
                       [+0, +1, +0],
                       [-np.sin(y_rot), +0, +np.cos(y_rot)]])

        Rz = np.array([[+np.cos(z_rot), -np.sin(z_rot), +0],
                       [+np.sin(z_rot), +np.cos(z_rot), +0],
                       [+0, +0, +1]])

        self.r = [np.dot(Rx, np.dot(Ry, np.dot(Rz, self.r[ind])))
                  for ind in range(len(self.r))]

        self.x = [self.r[ind][0] for ind in range(len(self.r))]
        self.y = [self.r[ind][1] for ind in range(len(self.r))]
        self.z = [self.r[ind][2] for ind in range(len(self.r))]

        # Rotate normal vectors if available
        if self.normals is not None:
            self.normals = [np.dot(Rx, np.dot(Ry, np.dot(Rz, self.normals[ind])))
                            for ind in range(len(self.normals))]

    def _translate(self, dr):

        dx = dr[0]
        dy = dr[1]
        dz = dr[2]

        self.r = [[self.x[ind] + dx, self.y[ind] + dy, self.z[ind] + dz]
                  for ind in range(len(self.r))]

        self.x = [self.r[ind][0] for ind in range(len(self.r))]
        self.y = [self.r[ind][1] for ind in range(len(self.r))]
        self.z = [self.r[ind][2] for ind in range(len(self.r))]

    def _save_position(self):

        x_ref = self.x
        y_ref = self.y
        z_ref = self.z
        r_ref = self.r

        self.x_ref = np.asarray(x_ref)
        self.y_ref = np.asarray(y_ref)
        self.z_ref = np.asarray(z_ref)
        self.r_ref = np.asarray(r_ref)

    def plot(self):
        """ This function creates and plots an offline plotly graph of the
        phantom. The colorscale is mapped to the absorbed skin dose value for
        skin dose mapping"""

        # create mesh object for phantom
        phantom_mesh = [
            go.Mesh3d(
                x=self.x, y=self.y, z=self.z, i=self.i, j=self.j, k=self.k,
                intensity=self.dose, colorscale="Jet", showscale=True,
                text=[f"{round(self.dose[ind],2)} mGy"
                      for ind in range(len(self.dose))], name="Human",
                colorbar=dict(tickfont=dict(color="white"),
                              title="Skin dose [mGy]",
                              titlefont=dict(color="white")))]

        # set plot settings
        layout = go.Layout(
            title='<b>P</b>y<b>S</b>kin<b>D</b>ose[dev]',
            titlefont=dict(family='Courier New, monospace', size=35,
                           color='white'),
            plot_bgcolor='rgb(45,45,45)',
            paper_bgcolor='rgb(45,45,45)',

            scene=dict(aspectmode="data",

                       xaxis=dict(title='LONGITUDINAL [cm]',
                                  zerolinecolor='rgb(45,45,45)',
                                  showgrid=False,
                                  titlefont=dict(color="white"),
                                  tickfont=dict(color="white")),

                       yaxis=dict(title="LATERAL [cm]",
                                  zerolinecolor='rgb(45,45,45)',
                                  showgrid=False,
                                  titlefont=dict(color="white"),
                                  tickfont=dict(color="white")),

                       zaxis=dict(title='',
                                  showline=False,
                                  zeroline=False,
                                  showgrid=False,
                                  showticklabels=False,
                                  titlefont=dict(color="white"),
                                  tickfont=dict(color="white"))))

        # create figure
        fig = go.Figure(data=phantom_mesh, layout=layout)
        # open plot
        ply.plot(fig, filename='PySkinDose.html')



# # EXAMPLE USAGE
# patient = Phantom(phantom_type="cylinder")
# Phantom.plot(patient)
