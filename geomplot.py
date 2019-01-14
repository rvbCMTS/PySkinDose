from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np


def PlotRay(ray, source, ax, color):

    ax.plot(ray[:, 0], ray[:, 2], ray[:, 1], color=color)

    # source to detector edges (make field edges insted)
    ax.plot([source[0], ray[0, 0]], [source[2], ray[0, 2]],
            [source[1], ray[0, 1]], color=color, linewidth=1)
    ax.plot([source[0], ray[1, 0]], [source[2], ray[1, 2]],
            [source[1], ray[1, 1]], color=color, linewidth=1)
    ax.plot([source[0], ray[2, 0]], [source[2], ray[2, 2]],
            [source[1], ray[2, 1]], color=color, linewidth=1)
    ax.plot([source[0], ray[3, 0]], [source[2], ray[3, 2]],
            [source[1], ray[3, 1]], color=color, linewidth=1)

    return


def PlotObject(obj, ax, color):
    ax.plot(obj[:, 0], obj[:, 2], obj[:, 1], color=color)
    ax.plot([obj[-1, 0], obj[0, 0]],
            [obj[-1, 2], obj[0, 2]],
            [obj[-1, 1], obj[0, 1]], color=color)
    return


def PlotPoint(point, ax, color):
    ax.scatter(point[0], point[2], point[1], color=color)
    return


def PlotPhantom(phantom, ax, color):
    # ax.scatter(phantom["x"], phantom["z"], phantom["y"],
    #            color=color, s=1, alpha=0.5)
    ax.plot(phantom["x"], phantom["z"], phantom["y"], linewidth=0.5)

    return
