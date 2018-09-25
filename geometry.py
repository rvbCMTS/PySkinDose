import numpy as np
import plotly.graph_objs as go
import plotly.offline as ply


# Create patient support table

# ILI, given av uses stated or from machine protocol in db. 40/150/2 are from openSkin
table_width = 40
table_length = 150
table_thickness = 2

##########
# Creates 2D surface for table representation{}

x = np.linspace(-0.5*table_length, 0.5*table_length, 50)
y = np.linspace(-0.5*table_width, 0.5*table_width, 50)
x, y = np.meshgrid(x, y)
z_level = 0.0  # plot a z-plane at height 0

z = z_level * np.ones(x.shape)
single_color = [[0.0, 'rgb(200,200,200)'], [1.0, 'rgb(200,200,200)']]
z_plane = dict(type='surface', x=x, y=y, z=z, colorscale=single_color, showscale=False)
##########

# Step 1: Create data
x1 = [0, 50, 0, 0, -50, 0, 0]
y1 = [0, 0, 50, 0, 0, -50, 0]
z1 = [10, 10, 10, 50, 10, 10, -50]

# Step 2: Create traces - data collections

trace1 = go.Scatter3d(
    x=x1,
    y=y1,
    z=z1,
    mode='markers',
    marker=dict(
        size=5,
        # line=dict(
        #    color='rgba(217, 217, 217, 0.14)',
        #    width=0.5
        ), opacity=0.8
    )


data = [trace1, z_plane]


layout = go.Layout(
    scene=dict(
        # axis range specified from table dimensions.
        xaxis=dict(
            title='LONG [cm]',
            range=[-0.75*table_length, 0.75*table_length]),
        yaxis=dict(
            title='LAT [cm]',
            range=[-0.75*table_length, 0.75*table_length]),
        zaxis=dict(
            title='VERT [cm]',
            range=[-100, 100]),
        )
)

# Create figure
fig = go.Figure(data=data, layout=layout)

# Plot figure
ply.plot(fig, filename='simple-3d-scatter.html')

