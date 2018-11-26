from stl import mesh
import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np
from typing import List, Dict, Optional


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


def create_phantom(phantom_type: str, human_model: Optional[str] = None, phantom_dim: Optional[dict] = None) -> dict:
    """creates skin dose calculation phantom.
    :param phantom_type: Type of phantom to create: "plane" (1D slab), "cylinder", "human" (MakeHuman binary .stl)
    :type phantom_type: str
    :param human_model: Type of human phantom. Current available options:
    'adult male', 'adult_female', 'senior_male', 'senior_female', 'junior_male', 'junior_female'
    :type human_model: str
    :param phantom_dim: size of the phantom for phantom_type: "plane" (width, length) and "cylinder" (a, b, length)
    For a circular cylinder, set a = b
    :type phantom_dim: Dict[str, int]
    :return: (x,y,z) coordinates for all point on the phantom. Also, (i,j,k) interpolation order for MakeHuman phantom
    :rtype: Dict[str, str]
    """

    # Raise error if plane/cylinder dimensions are missing for plane/cylinder phantom representation
    if phantom_type in ["plane", "cylinder"]:
        if phantom_dim is None:
            raise ValueError("Phantom dimensions are needed to create a plane or cylinder phantom.")

    # Raise error if human model are not specified for human phantom representation
    elif phantom_type == "human":
        if human_model is None:
            raise ValueError("Human model are needed to create a human phantom.")

    # Creates a coordinate grid on a 2D plane for plane phantom representation
    if phantom_type == "plane":

        # Linearly spaced point along the longitudinal direction, in steps of 1 cm
        x_range = np.linspace(-0.5*phantom_dim["width"], 0.5*phantom_dim["width"], phantom_dim["width"] + 1)
        # Linearly spaced point along the lateral direction, in steps of 1 cm
        y_range = np.linspace(0, phantom_dim["length"], phantom_dim["length"] + 1)
        # Create phantom in form of rectangular grid
        x, y = np.meshgrid(x_range, y_range)

        x = x.ravel().tolist()
        y = y.ravel().tolist()

        # Preallocate memory for skin dose mapping
        z = [0] * len(x)
        dose = [0] * len(x)

        # Store the  coordinates of the plane phantom, and preallocate memory for skin dose mapping at each point
        output = {"type": "plane", 'x': x, 'y': y, 'z': z, "dose": dose}

    # Creates a coordinate grid along an elliptic cylinder for elliptic cylinder phantom representation
    elif phantom_type == "cylinder":

        # Creates linearly spaced points along an ellipse in the lateral direction
        t = np.arange(0, 2 * np.pi, 0.15)
        x = (phantom_dim["a"] * np.cos(t)).tolist()
        z = (phantom_dim["b"] * np.sin(t)).tolist()

        # Store the  coordinates of the cylinder phantom
        output = {"type": "cylinder", "x": [], "y": [], "z": []}

        # Extend the ellipse to span the entire length of the phantom, in steps of 10 cm,
        # thus creating a phantom in form of an elliptic cylinder
        for index in range(0, phantom_dim["length"], 10):
            output["x"] = output["x"] + x
            output["z"] = output["z"] + z
            output["y"] = output["y"] + [index] * len(x)

        output['dose'] = [0] * len(output['x'])

    # Creates a coordinate grid on a 3D human model for human phantom representation
    elif phantom_type == "human":

        # load selected phantom model from binary .stl file
        phantom_mesh = mesh.Mesh.from_file('phantom_data/'+human_model+'.stl')
        x = [el for el_list in phantom_mesh.x for el in el_list]
        y = [el for el_list in phantom_mesh.y for el in el_list]
        z = [el for el_list in phantom_mesh.z for el in el_list]
        i = np.arange(0, len(x) - 3, 3)
        j = np.arange(1, len(y) - 2, 3)
        k = np.arange(2, len(z) - 1, 3)

        # Store the coordinates of the human phantom
        output = {"type": "human", 'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k}
        # Preallocate memory for skin dose mapping
        output['dose'] = [0] * len(output['x'])

    # Raise error if invalid phantom type selected
    else:
        raise ValueError("Unknown phantom type selected. Valid type: plane, cylinder, human")

    return output


def plot_phantom(phantom_dict: dict, include_table: bool, table_dict: Optional[dict] = None):
    """creates and plots an (offline) plotly graph of the phantom and support table (optional)

    :param phantom_dict: (x,y,z) coordinates for all point on the phantom.
    Also, (i,j,k) interpolation order for MakeHuman phantom.
    :type phantom_dict: Dict[str, str]
    :param include_table: choose if the support table should be included in the plot.
    :type include_table: bool
    :param table_dict: (x,y,z) coordinates of the vertices of the patient support table
    :type table_dict: Dict[str, str]
    """
    # Raise error if table dimensions are missing when table presentation are selected
    if include_table:
        if table_dict is None:
            raise ValueError('Table measurements must be given when include_table is True')

    # Create Plotly 3D mesh object for plane phantom representation
    if phantom_dict["type"] == "plane":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                alphahull=-1, colorscale='Jet', name='plane phantom', showscale=True)]

    # Create Plotly 3D mesh object for elliptic cylinder phantom representation
    elif phantom_dict["type"] == "cylinder":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                alphahull=1, colorscale='Jet', name='Cylinder phantom', showscale=True)]

    # Create Plotly 3D mesh object for human phantom representation
    elif phantom_dict["type"] == "human":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                i=phantom_dict["i"], j=phantom_dict["j"], k=phantom_dict["k"],
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
                x=table_dict["x"], y=table_dict["y"], z=[x + np.amin(phantom_dict["z"]) for x in table_dict["z"]],
                intensity=phantom_dict["dose"], alphahull=1, color='gray', opacity=0.8, name='Table', showscale=False)]

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

# user commands


# Define table dimensions in the longitudinal (width), lateral (length) and vertical (thickness) direction
table_measurements = {'width': 70, 'length': 200, 'thickness': 5}


# Define width (of the plane phantom), length (of the plane/elliptic cylinder),
# foci a and b (elliptic cylinder) in the lateral and longitudinal direction
phantom_measurements = {'width': 60, 'length': 180, "a": 20, "b": 10}

# create phantom
phantom = create_phantom(phantom_type='human',
                         human_model='adult_male',
                         phantom_dim=phantom_measurements)

# create table
table = create_table(table_measurements)

# plot phantom
plot_phantom(phantom_dict=phantom,
             include_table=True,
             table_dict=table)
