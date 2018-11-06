from stl import mesh
import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np
from typing import List, Dict, Optional


def _create_table(table_size: dict) -> dict:

    x = [-0.5*table_size["width"], 0.5*table_size["width"], 0.5*table_size["width"], -0.5*table_size["width"]]
    y = [0, 0, table_size["length"], table_size["length"]]
    z = [0, 0, 0, 0]
    x = x + x
    y = y + y
    z = z + [-table_size["thickness"]] * len(z)

    output = {"type": "table", "x": x, "y": y, "z": z}

    return output


def create_phantom(phantom_type: str, table_size: dict, cylinder_radius: int = 20) -> dict:

    if phantom_type == "plane":

        x_range = np.linspace(-0.5*table_size["width"], 0.5*table_size["width"], table_size["width"] + 1)
        y_range = np.linspace(0, table_size["length"], table_size["length"] + 1)
        x, y = np.meshgrid(x_range, y_range)

        x = x.ravel().tolist()
        y = y.ravel().tolist()
        z = [0] * len(x)
        dose = [0] * len(x)

        output = {"type": "plane", 'x': x, 'y': y, 'z': z, "dose": dose}

    elif phantom_type == "cylinder":

        t = np.arange(0, 2 * np.pi, 0.15)
        x = (cylinder_radius * np.cos(t)).tolist()
        z = (cylinder_radius * np.sin(t)).tolist()

        output = {"type": "cylinder", "x": [], "y": [], "z": []}

        for index in range(0, table_size["length"], 10 + 1):
            output["x"] = output["x"] + x
            output["z"] = output["z"] + z
            output["y"] = output["y"] + [index] * len(x)

        output['dose'] = [0] * len(output['x'])

    elif phantom_type == "human":
        phantom_mesh = mesh.Mesh.from_file('standard_bin.stl')
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


# works fine
def plot_phantom(phantom_dict: dict, include_table: bool, table_dict: Optional[dict] = None) -> List[go.Mesh3d]:
    # if include_table:
        # if table_measurements is None:
            # raise ValueError('Table measurements must be given when include_table is True')

        # z_plane = _create_table(table_width=table_measurements['width'],
                                # table_length=table_measurements['length'],
                                # table_thickness=table_measurements['thickness'])

    if phantom_dict["type"] == "human":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"],
                i=phantom_dict["i"], j=phantom_dict["j"], k=phantom_dict["k"],
                intensity=phantom_dict["dose"],
                colorscale='Jet',
                name='Phantom',
                showscale=True)]

    elif phantom_dict["type"] == "cylinder":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"],
                alphahull=1,
                intensity=phantom_dict["dose"],
                colorscale='Jet',
                name='Phantom',
                showscale=True)]

    elif phantom_dict["type"] == "plane":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"],
                alphahull=-1,
                intensity=phantom_dict["dose"],
                colorscale='Jet',
                name='Phantom',
                showscale=True)]

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
                alphahull=1,
                intensity=phantom_dict["dose"],
                color='gray',
                opacity=0.5,
                name='Table')]

        phantom_temp = go.Figure(data=phantom_mesh)
        table_temp = go.Figure(data=table_mesh)

        fig = dict(data=[phantom_temp.data[0], table_temp.data[0]], layout=layout)
        ply.plot(fig, filename='PhantomImport.html')

    else:
        fig = go.Figure(data=phantom_mesh, layout=layout)
        ply.plot(fig, filename='plot_phantom.html')


# user commands
table_measurements = {'width': 70, 'length': 250, 'thickness': 2}

# create phantom
phantom = create_phantom(phantom_type='human',
                         table_size=table_measurements,
                         cylinder_radius=20)

# create table
table = _create_table(table_measurements)

# plot phantom
plot_phantom(phantom_dict=phantom,
             include_table=True,
             table_dict=table)










# intensity = np.random.rand(mesh.x.size)
# intensity = np.arange(0, len(xlist), 1)

# intensity = [el for el_list in mesh.z for el in el_list],
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import plotly.plotly as py
#def plot_phantom(phantom_dict: dict, include_table: bool, table_measurements: Optional[dict] = None,
                           #  show_colourscale: Optional[bool] = True) -> List[go.Mesh3d]:

# fig_temp = go.Figure(data=phantom_mesh)
# fig = dict(data=[fig_temp.data[0]], layout=layout)
# single_color = [[0.0, 'rgb(200,200,200)'], [1.0, 'rgb(200,200,200)']]
# output = dict(type='surface', x=x_tab, y=y_tab, z=z_tab,
#              colorscale=single_color, showscale=False)
