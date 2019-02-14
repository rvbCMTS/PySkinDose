import numpy as np
from mayavi import mlab
from mayavi.mlab import *


def plot_phantom(obj):

    if obj.type is "human":
        color = (0.85, 0.75, 0.75)

    elif obj.type is "table":
        color = (0.2, 0.2, 0.2)

    elif obj.type is "pad":
        color = (0.2, 0.2, 0.8)

    else:
        color = (0.5, 0.5, 0.5)

    return mlab.triangular_mesh(obj.x, obj.y, obj.z,
                                obj.triangles, color=color)


def plot_detector(beam):

    return triangular_mesh(beam.r_det[:, 0],
                           beam.r_det[:, 1],
                           beam.r_det[:, 2], beam.r_det_triangles,
                           color=(1, 1, 1))


def plot_beam(beam, plot_type="volume"):

    if plot_type is "volume":
        return triangular_mesh(np.append(beam.source[0], beam.x_edge),
                               np.append(beam.source[1], beam.y_edge),
                               np.append(beam.source[2], beam.z_edge),
                               beam.r_edge_triangles, color=(1, 0, 0),
                               opacity=0.2)
    elif plot_type is "wireframe":
        return triangular_mesh(np.append(beam.source[0], beam.x_edge),
                               np.append(beam.source[1], beam.y_edge),
                               np.append(beam.source[2], beam.z_edge),
                               beam.r_edge_triangles, color=(0, 0, 0),
                               representation="wireframe")


def plot_source(beam):

    return points3d(beam.source[0], beam.source[1], beam.source[2],
                    scale_factor=4)
