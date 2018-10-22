from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import plotly.plotly as py

import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np

# ILI, given av uses stated or from machine protocol in db. 40/150/2 are from openSkin
table_width = 70
table_length = 250
table_thickness = 2


mesh = mesh.Mesh.from_file('standard_bin.stl')

intensity = np.random.rand(mesh.x.size)
# intensity = np.arange(0, len(xlist), 1)


# TABLE ILLUSTRATION
x_tab = np.linspace(-0.5*table_width, 0.5*table_width, 50)
y_tab = np.linspace(-50, 200, 50)

x_tab, y_tab = np.meshgrid(x_tab, y_tab)

z_level = np.amin(mesh.z)

z_tab=z_level*np.ones(x_tab.shape)
single_color=[[0.0, 'rgb(200,200,200)'], [1.0, 'rgb(200,200,200)']]
z_plane=dict(type='surface', x=x_tab, y=y_tab, z=z_tab,
                     colorscale=single_color, showscale=False)

phantom = [
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
        i=np.arange(0, mesh.x.size -3, 3),
        j=np.arange(1, mesh.y.size -2, 3),
        k=np.arange(2, mesh.z.size -1, 3),

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

fig_temp = go.Figure(data=phantom)
fig = dict(data=[fig_temp.data[0], z_plane], layout=layout)


ply.plot(fig, filename='OnTable.html')


