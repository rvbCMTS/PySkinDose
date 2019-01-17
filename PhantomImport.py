from stl import mesh
import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np
import os
from typing import List, Dict, Optional


VALID_PHANTOM_TYPES = ['plane', 'cylinder', 'human']


def create_table(table_dim: dict) -> dict:
    """Creates the eight vertices of the patient support table.

    :param table_dim: Patient support table dimensions (width, length, thickness)
    :type table_dim: Dict[str, int]
    :return: (x,y,z) coordinates of the vertices of the patient support table
    :rtype: Dict[str, str]
    """
    # Longitudinal position of the the vertices
    x = [index * 0.5*table_dim["width"] for index in [-1, 1, 1, -1, -1, 1, 1, -1]]
    # Lateral position of the the vertices
    y = [index * table_dim["length"] for index in [0, 0, 1, 1, 0, 0, 1, 1]]
    # Vertical position of the vertices
    z = [index * -table_dim["thickness"] for index in [0, 0, 0, 0, 1, 1, 1, 1]]

    output = {"type": "table", "x": x, "y": y, "z": z}

    return output


class Phantom:
    """This class creates a phatom of any of the types specified in VALID_PHANTOM_TYPES.
    and plots the phantom in a plotly 3D mesh for radiation skin dose visualization."""
    
    def __init__(self, phantom_type: str, human_model: Optional[str] = None, phantom_dim: Optional[dict] = None):
        # Raise error if plane/cylinder dimensions are missing for plane/cylinder phantom representation
        if phantom_type.lower() in ["plane", "cylinder"]:
            if phantom_dim is None:
                raise ValueError("Phantom dimensions are needed to create a plane or cylinder phantom.")

        # Raise error if human model are not specified for human phantom representation
        elif phantom_type.lower() == "human":
            if human_model is None:
                raise ValueError("Human model are needed to create a human phantom.")

                # Raise error if invalid phantom type selected
        if phantom_type.lower() not in VALID_PHANTOM_TYPES:
            raise ValueError(f"Unknown phantom type selected. Valid type: {'.'.join(VALID_PHANTOM_TYPES)}")

        self.x: np.ndarray = None
        self.y: np.ndarray = None
        self.z: np.ndarray = None
        self.r: List[List[float]] = None

        self.i: Optional[np.ndarray] = None
        self.j: Optional[np.ndarray] = None
        self.k: Optional[np.ndarray] = None

        self.normals: np.ndarray = None

        self.type: str = phantom_type.lower()
        self.dose: Optional[List[float]] = None

        if phantom_type.lower() == "plane":

            # Linearly spaced point along the longitudinal direction, in steps of 1 cm
            x_range = np.linspace(-0.5 * phantom_dim["width"], 0.5 * phantom_dim["width"], phantom_dim["width"] + 1)
            # Linearly spaced point along the lateral direction, in steps of 1 cm
            z_range = np.linspace(-0.5 * phantom_dim["length"], 0.5 * phantom_dim["length"], phantom_dim["length"] + 1)
            # Create phantom in form of rectangular grid
            x, z = np.meshgrid(x_range, z_range)

            self.x = x.ravel().tolist()
            self.z = z.ravel().tolist()

            # Preallocate memory for skin dose mapping
            self.y = [0] * len(x)
            self.dose = [0] * len(x)

        # Creates a coordinate grid along an elliptic cylinder for elliptic cylinder phantom representation
        elif phantom_type.lower() == "cylinder":
            # Creates linearly spaced points along an ellipse in the lateral direction
            t = np.arange(0, 2 * np.pi, 0.25)
            x = (phantom_dim["a"] * np.cos(t)).tolist()
            y = (phantom_dim["b"] * np.sin(t)).tolist()

            # Store the  coordinates of the cylinder phantom
            output = {"type": "cylinder", "x": [], "y": [], "z": []}

            # Extend the ellipse to span the entire length of the phantom, in steps of 10 cm,
            # thus creating a phantom in form of an elliptic cylinder
            for index in range(0, phantom_dim["length"], 5):
                output["x"] = output["x"] + x
                output["y"] = output["y"] + y
                output["z"] = output["z"] + [index] * len(x)

            self.x = output["x"]
            # center in z direction
            self.z = [x - 0.5 * phantom_dim["length"] for x in output["z"]]
            self.y = [x - phantom_dim["b"] for x in output["y"]]

            # Preallocate memory for skin dose mapping
            self.dose = [0] * len(output['x'])

        # Creates a coordinate grid on a 3D human model for human phantom representation
        elif phantom_type.lower() == "human":

            # load selected phantom model from binary .stl file
            phantom_path = os.path.join(os.path.dirname(__file__), 'phantom_data', f"{human_model}.stl")
            phantom_mesh = mesh.Mesh.from_file(phantom_path)
            self.x = [el for el_list in phantom_mesh.x for el in el_list]
            self.y = [el for el_list in phantom_mesh.y for el in el_list]
            self.z = [el for el_list in phantom_mesh.z for el in el_list]
            self.r = [
                [[self.x[ind], self.z[ind], self.y[ind]] for ind in range(len(self.x))]
            ]
            n = phantom_mesh.normals
            self.normals = [x for pair in zip(n, n, n) for x in pair]
            self.i = np.arange(0, len(self.x) - 3, 3)
            self.j = np.arange(1, len(self.y) - 2, 3)
            self.k = np.arange(2, len(self.z) - 1, 3)

            # Preallocate memory for skin dose mapping
            self.dose = [0] * len(self.x)

    def plot(self, include_table: bool, table: Optional[object] = None):
        """creates and plots an (offline) plotly graph of the phantom and support table (optional)

            :param include_table: choose if the support table should be included in the plot.
            :param table_dict: (x,y,z) coordinates of the vertices of the patient support table
            :type table_dict: Dict[str, str]
            """
        # Raise error if table dimensions are missing when table presentation are selected
        if include_table:
            if table is None:
                raise ValueError('Table measurements must be given when include_table is True')

        # Create Plotly 3D mesh object for plane phantom representation
        if self.type == "plane":
            phantom_mesh = [
                go.Mesh3d(
                    x=self.x, y=self.y, z=self.z, intensity=self.dose,
                    alphahull=-1, colorscale='Jet', name='plane phantom', showscale=True)]

        # Create Plotly 3D mesh object for elliptic cylinder phantom representation
        elif self.type == "cylinder":
            phantom_mesh = [
                go.Mesh3d(
                    x=self.x, y=self.y, z=self.z, intensity=self.dose,
                    alphahull=1, colorscale='Jet', name='Cylinder phantom', showscale=True)]

        # Create Plotly 3D mesh object for human phantom representation
        elif self.type == "human":
            phantom_mesh = [
                go.Mesh3d(
                    x=self.x, y=self.y, z=self.z, intensity=self.dose,
                    i=self.i, j=self.j, k=self.k,
                    colorscale='Jet', name='Human phantom', showscale=True)]

        # Raise error if invalid phantom type selected
        else:
            raise ValueError("Unsupported phantom type selected. Valid selections: plane, cylinder, human")

        # Plot settings
        layout = go.Layout(
            scene=dict(
                aspectmode="data",
                xaxis=dict(
                    title='LONG [cm])'),
                yaxis=dict(
                    title='LAT [cm])'),
                zaxis=dict(
                    title='VERT [cm])')))

        # If the patient support table are to be visualized in the figure
        if include_table:
            # Create Plotly 3D mesh object for the patient support table.
            table_mesh = [
                go.Mesh3d(
                    x=table.x, y=table.y, z=[x + np.amin(self.z) for x in table.z],
                    intensity=self.dose, alphahull=1, color='gray', opacity=0.8, name='Table',
                    showscale=False)]

            # Fixing problem with plotting several Plotly 3D mesh object in the same figure (both table and phantom)
            phantom_temp = go.Figure(data=phantom_mesh)
            table_temp = go.Figure(data=table_mesh)

            fig = dict(data=[table_temp.data[0], phantom_temp.data[0]], layout=layout)
            # Plot the result locally (No Plotly login required)
            ply.plot(fig, filename='PhantomImport.html')

        # If only the patient phantom should be visualized (without patient support table
        else:
            fig = go.Figure(data=phantom_mesh, layout=layout)
            # Plot the result locally (No Plotly login required)
            ply.plot(fig, filename='plot_phantom.html')



# example output

# Define width (of the plane phantom), length (of the plane/elliptic cylinder),
# foci a and b (elliptic cylinder) in the lateral and longitudinal direction
phantom_measurements = {'width': 60, 'length': 180, "a": 20, "b": 10}

# Table measurements
table_measurements = {'width': 70, 'length': 200, 'thickness': 5}

table = create_table(table_dim=table_measurements)
TestPhantom = Phantom(phantom_type="human", human_model="adult_male", phantom_dim=phantom_measurements)

TestPhantom.plot(include_table=True,)






































# Define table dimensions in the longitudinal (width), lateral (length) and vertical (thickness) direction
# table_measurements = {'width': 70, 'length': 200, 'thickness': 5}



# create phantom
# phantom = create_phantom(phantom_type='human',
#                          human_model='adult_male',
#                          phantom_dim=phantom_measurements)

# create table
# table = create_table(table_measurements)

# plot phantom
# plot_phantom(phantom_dict=phantom,
#              include_table=True,
#              table_dict=table)