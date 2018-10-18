from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import plotly.plotly as py

import plotly.graph_objs as go
import plotly.offline as ply
import numpy as np



mesh = mesh.Mesh.from_file('standard_bin.stl')




xlist = [el for el_list in mesh.x for el in el_list]
ylist = [el for el_list in mesh.y for el in el_list]
zlist = [el for el_list in mesh.z for el in el_list]

# range (start, stop, descriminator)
ilist = np.arange(0, len(xlist)-3, 3)
jlist = np.arange(1, len(ylist)-2, 3)
klist = np.arange(2, len(zlist)-1, 3)

print(len(ilist))
print(len(jlist))
print(len(klist))


test=1

intensity = np.random.rand(len(xlist))

data = [
    go.Mesh3d(
        x = xlist,
        y = ylist,
        z = zlist,
        colorbar = go.ColorBar(
            title='z'
        ),
        colorscale = [[0, 'rgb(255, 0, 255)'],
                    [   0.5, 'rgb(0, 255, 0)'],
                      [1, 'rgb(0, 0, 255)']],
        intensity = intensity,
        # intensity = [0, 0.142857142857143, 0.285714285714286,
        #              0.428571428571429, 0.571428571428571,
        #              0.714285714285714, 0.857142857142857, 1],
        i = ilist,
        j = jlist,
        k = klist,
        name='y',
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
            range=[-100, 100])
        )
)
fig = go.Figure(data=data, layout=layout)
ply.plot(fig, filename='3d-mesh-cube-python.html')

