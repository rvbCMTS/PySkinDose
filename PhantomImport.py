from stl import mesh
import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np
from typing import List, Dict, Optional


def _create_table(table_measurements: dict, phantom: dict) -> dict:
    # TABLE ILLUSTRATION, improve this please
    x_tab = np.linspace(-0.5 * table_measurements["width"], 0.5 * table_measurements["width"], 50)
    y_tab = np.linspace(-50, table_measurements["length"], 50)

    x_tab, y_tab = np.meshgrid(x_tab, y_tab)

    z_level = np.amin(phantom["z"])

    z_tab = z_level * np.ones(x_tab.shape)
    single_color = [[0.0, 'rgb(200,200,200)'], [1.0, 'rgb(200,200,200)']]
    output = dict(type='surface', x=x_tab, y=y_tab, z=z_tab,
                  colorscale=single_color, showscale=False)

    return output


def import_phantom(phantom_type: str) -> dict:

    # works fine
    if phantom_type == "human":
        phantom_mesh = mesh.Mesh.from_file('standard_bin.stl')
        x = [el for el_list in phantom_mesh.x for el in el_list]
        y = [el for el_list in phantom_mesh.y for el in el_list]
        z = [el for el_list in phantom_mesh.z for el in el_list]
        i = np.arange(0, len(x) - 3, 3)
        j = np.arange(1, len(y) - 2, 3)
        k = np.arange(2, len(z) - 1, 3)

        output = {"type": "human", 'x': x, 'y': y, 'z': z, 'i': i, 'j': j, 'k': k}
        output['dose'] = [0] * len(output['x'])

    elif phantom_type == "cylinder":

        radius = 20

        t = np.arange(0, 2 * np.pi, 0.3)
        x = (radius * np.cos(t)).tolist()
        z = (radius * np.sin(t)).tolist()

        output = {"type": "cylinder", "x": [], "y": [], "z": []}

        for index in range(0, 180, 10):
            output["x"] = output["x"] + x
            output["z"] = output["z"] + z
            output["y"] = output["y"] + [index] * len(x)

        output['dose'] = [0] * len(output['x'])

    return output


# works fine
def plot_phantom(phantom_dict: dict) -> List[go.Mesh3d]:
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
                name='phantom',
                showscale=True)]

    elif phantom_dict["type"] == "cylinder":
        phantom_mesh = [
            go.Mesh3d(
                x=phantom_dict["x"], y=phantom_dict["y"], z=phantom_dict["z"],
                alphahull=1,
                intensity=phantom_dict["dose"],
                colorscale='Jet',
                name='phantom',
                showscale=True)]

    layout = go.Layout(
        scene=dict(
            aspectmode="data",
            xaxis=dict(
                title='LONG [cm])'),
            yaxis=dict(
                title='LAT [cm])'),
            zaxis=dict(
                title='VERT [cm])'),
        )
    )

    fig = go.Figure(data=phantom_mesh, layout=layout)
    ply.plot(fig, filename='PhantomImport.html')


table_measurements = {'width': 70, 'length': 250, 'thickness': 2}

phantom = import_phantom(phantom_type='human')

plot_phantom(phantom)








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