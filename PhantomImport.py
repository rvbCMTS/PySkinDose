from stl import mesh
import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np
from typing import List, Dict, Optional
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import plotly.plotly as py


def import_phantom(phantom_type: str) -> dict:

    phantom_mesh = mesh.Mesh.from_file(phantom_type)

    output = {
        # extract x,y,z coordinates from phantom .stl file
        'x': [el for el_list in phantom_mesh.x for el in el_list],
        'y': [el for el_list in phantom_mesh.y for el in el_list],
        'z': [el for el_list in phantom_mesh.z for el in el_list],
        # Fixes order of interpolation between calculation point (x,y,z)
        'i': np.arange(0, phantom_mesh.x.size - 3, 3),
        'j': np.arange(1, phantom_mesh.y.size - 2, 3),
        'k': np.arange(2, phantom_mesh.z.size - 1, 3)
    }

    output['intensities'] = [0] * len(output['x'])

    return output


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


def create_phantom_dose_plot(phantom_dict: dict, include_table: bool, table_measurements: Optional[dict] = None,
                             show_colourscale: Optional[bool] = True) -> List[go.Mesh3d]:
    if include_table:
        if table_measurements is None:
            raise ValueError('Table measurements must be given when include_table is True')

        z_plane = _create_table(table_width=table_measurements['width'],
                                table_length=table_measurements['length'],
                                table_thickness=table_measurements['thickness'])
    phantom_plot = [
        go.Mesh3d(
            # extract x,y,z coordinates from phantom .stl file
            x=[el for el_list in mesh.x for el in el_list],
            y=[el for el_list in mesh.y for el in el_list],
            z=[el for el_list in mesh.z for el in el_list],

            # Jet seems reasonable. Perhaps fix couture lines for dose limits?
            colorscale='Jet',

            # intensity variable shall hold calculated absorbed dose for each point.
            # Right now, it just holds a gradient for visualization of output in plot window.
            # intensity=intensity,
            intensity=[el for el_list in mesh.z for el in el_list],

            # Fixes order of interpolation between calculation point (x,y,z)
            i=np.arange(0, mesh.x.size - 3, 3),
            j=np.arange(1, mesh.y.size - 2, 3),
            k=np.arange(2, mesh.z.size - 1, 3),

            name='phantom',
            showscale=True
        )
    ]

    layout = go.Layout(
        scene=dict(
            # axis range specified from table dimensions.
            xaxis=dict(
                title='LONG [cm]',
                range=[-100, 100]),
            yaxis=dict(
                title='LAT [cm]',
                range=[-50, 200]),
            zaxis=dict(
                title='VERT [cm])',
                range=[-100, 100]),
        )
    )

    fig_temp = go.Figure(data=phantom_plot)
    fig = dict(data=[fig_temp.data[0], z_plane], layout=layout)

    ply.plot(fig, filename='PhantomImport.html')


table_measurements = {
    'width': 70,
    'length': 250,
    'thickness': 2
}

# works
phantom = import_phantom(phantom_type='standard_bin.stl')
#

table = _create_table(table_measurements, phantom)


# intensity = np.random.rand(mesh.x.size)
# intensity = np.arange(0, len(xlist), 1)

# intensity = [el for el_list in mesh.z for el in el_list],
