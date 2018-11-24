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
    x = [index * 0.5*table_dim["width"] for index in [-1, 1, 1, -1, -1, 1, 1, -1]]
    y = [index * table_dim["length"] for index in [0, 0, 1, 1, 0, 0, 1, 1]]
    z = [index * -table_dim["thickness"] for index in [0, 0, 0, 0, 1, 1, 1, 1]]

    output = {"type": "table", "x": x, "y": y, "z": z}

    return output


def create_phantom(phantom_type: str, human_model: Optional[str] = None, phantom_dim: Optional[dict] = None) -> dict:
    """creates skin dose calculation phantom.
    :param phantom_type: Type of phantom to create: "plane" (1D slab), "cylinder", "human" (MakeHuman binary stl)
    :type phantom_type: str
    :param human_model: Type of human phantom. Current available options:
    'adult male', 'adult_female', 'senior_male', 'senior_female', 'junior_male', 'junior_female'
    :type human_model: str
    :param phantom_dim: size of the phantom for phantom_type: "plane" (width, length) and "cylinder" (radius, length)
    :type phantom_dim: Dict[str, int]
    :return: (x,y,z) coordinates for all point on the phantom. Also, (i,j,k) interpolation order for MakeHuman phantom
    :rtype: Dict[str, str]
    """

    if phantom_type in ["plane", "cylinder"]:
        if phantom_dim is None:
            raise ValueError("Phantom dimensions are needed to create a plane or cylinder phantom.")

    elif phantom_type == "human":
        if human_model is None:
            raise ValueError("Human model are needed to create a human phantom.")

    if phantom_type == "plane":

        x_range = np.linspace(-0.5*phantom_dim["width"], 0.5*phantom_dim["width"], phantom_dim["width"] + 1)
        y_range = np.linspace(0, phantom_dim["length"], phantom_dim["length"] + 1)
        x, y = np.meshgrid(x_range, y_range)

        x = x.ravel().tolist()
        y = y.ravel().tolist()
        z = [0] * len(x)
        dose = [0] * len(x)

        output = {"type": "plane", 'x': x, 'y': y, 'z': z, "dose": dose}

    elif phantom_type == "cylinder":

        t = np.arange(0, 2 * np.pi, 0.15)
        x = (phantom_dim["a"] * np.cos(t)).tolist()
        z = (phantom_dim["b"] * np.sin(t)).tolist()

        output = {"type": "cylinder", "x": [], "y": [], "z": []}

        for index in range(0, phantom_dim["length"], 10 + 1):
            output["x"] = output["x"] + x
            output["z"] = output["z"] + z
            output["y"] = output["y"] + [index] * len(x)

        output['dose'] = [0] * len(output['x'])

    elif phantom_type == "human":

        phantom_mesh = mesh.Mesh.from_file('phantom_data/'+human_model+'.stl')
        x = [el for el_list in phantom_mesh.x for el in el_list]
        y = [el for el_list in phantom_mesh.y for el in el_list]
        z = [el for el_list in phantom_mesh.z for el in el_list]
        i = np.arange(0, len(x) - 3, 3)
        j = np.arange(1, len(y) - 2, 3)
        k = np.arange(2, len(z) - 1, 3)

        output = {"type": "human", 'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k}
        output['dose'] = [0] * len(output['x'])

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

    if include_table:
        if table_dict is None:
            raise ValueError('Table measurements must be given when include_table is True')

    if phantom_dict["type"] == "plane":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                alphahull=-1, colorscale='Jet', name='plane phantom', showscale=True)]

    elif phantom_dict["type"] == "cylinder":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                alphahull=1, colorscale='Jet', name='Cylinder phantom', showscale=True)]

    elif phantom_dict["type"] == "human":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"], intensity=phantom_dict["dose"],
                i=phantom_dict["i"], j=phantom_dict["j"], k=phantom_dict["k"],
                colorscale='Jet', name='Human phantom', showscale=True)]

    else:
        raise ValueError("Unsupported phantom type selected. Valid selections: plane, cylinder, human")

    layout = go.Layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(
                title='LONG [cm])'),
            yaxis=dict(
                title='LAT [cm])'),
            zaxis=dict(
                title='VERT [cm])')))

    if include_table:
        table_mesh = [
            go.Mesh3d(
                x=table_dict["x"], y=table_dict["y"], z=[x + np.amin(phantom_dict["z"]) for x in table_dict["z"]],
                intensity=phantom_dict["dose"], alphahull=1, color='gray', opacity=0.8, name='Table', showscale=False)]

        phantom_temp = go.Figure(data=phantom_mesh)
        table_temp = go.Figure(data=table_mesh)

        fig = dict(data=[table_temp.data[0], phantom_temp.data[0]], layout=layout)
        ply.plot(fig, filename='PhantomImport.html')

    else:
        fig = go.Figure(data=phantom_mesh, layout=layout)
        ply.plot(fig, filename='plot_phantom.html')


# user commands
table_measurements = {'width': 70, 'length': 200, 'thickness': 5}

phantom_measurements = {'width': 60, 'length': 180, 'radius': 20, "a": 20, "b": 10}

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