from mpl_toolkits.mplot3d import axes3d
# import matplotlib.pyplot as plt
from typing import Dict, List
# import matplotlib as mpl
import numpy as np
import pandas as pd
import os


def tempname(pd):
    pd["DSI"] = pd.DistanceSourcetoIsocenter_mm/10
    pd["DSD"] = pd.DistanceSourcetoDetector_mm/10
    pd["DST"] = -pd.TableHeightPosition_mm/10 + 77.5
    pd["DIT"] = pd.DST - pd.DSI
    pd["DID"] = pd.DSD - pd.DSI
    pd["DSIRP"] = pd.DSI/10 - 15
    pd["CFA"] = pd.CollimatedFieldArea_m2*10000
    pd["PPA"] = pd.PositionerPrimaryAngle_deg
    pd["PSA"] = pd.PositionerSecondaryAngle_deg
    pd["T_LAT"] = pd.TableLateralPosition_mm/10
    pd["T_LONG"] = pd.TableLongitudinalPosition_mm/10
    pd["T_VERT"] = pd.TableHeightPosition_mm/10

    return pd


def offset_object(obj, dr_phantom: List[float], dr_table: List[float]):

    obj.r = [[obj.r[ind][0] + dr_phantom[0],
             obj.r[ind][1] + dr_phantom[1],
             obj.r[ind][2] + dr_phantom[2]]
             for ind in range(len(obj.r))]

    obj.table_r = [[obj.table_r[ind][0] + dr_table[0],
                    obj.table_r[ind][1] + dr_table[1],
                    obj.table_r[ind][2] + dr_table[2]]
                   for ind in range(len(obj.table_r))]

    obj.x = [obj.r[ind][0] for ind in range(len(obj.r))]
    obj.y = [obj.r[ind][1] for ind in range(len(obj.r))]
    obj.z = [obj.r[ind][2] for ind in range(len(obj.r))]

    obj.table_x = [obj.table_r[ind][0] for ind in range(len(obj.table_r))]
    obj.table_y = [obj.table_r[ind][1] for ind in range(len(obj.table_r))]
    obj.table_z = [obj.table_r[ind][2] for ind in range(len(obj.table_r))]

    return obj


def rotate_object(obj, rotation: List[float] = [0, 0, 0]):

    rotation = np.deg2rad(rotation)

    x_rot = rotation[0]
    y_rot = rotation[1]
    z_rot = rotation[2]

    Rx = np.array([[+1, +0,             +0],
                   [+0, +np.cos(x_rot), -np.sin(x_rot)],
                   [+0, +np.sin(x_rot), +np.cos(x_rot)]])

    Ry = np.array([[+np.cos(y_rot), +0, +np.sin(y_rot)],
                   [+0,             +1, +0],
                   [-np.sin(y_rot), +0, +np.cos(y_rot)]])

    Rz = np.array([[+np.cos(z_rot), -np.sin(z_rot), +0],
                   [+np.sin(z_rot), +np.cos(z_rot), +0],
                   [+0,             +0,             +1]])

    # rotate phantom and table cells
    obj.r = [np.dot(Rx, np.dot(Ry, np.dot(Rz, obj.r[ind])))
             for ind in range(len(obj.r))]

    obj.table_r = [np.dot(Rx, np.dot(Ry, np.dot(Rz, obj.table_r[ind])))
                   for ind in range(len(obj.table_r))]

    obj.x = [obj.r[ind][0] for ind in range(len(obj.r))]
    obj.y = [obj.r[ind][1] for ind in range(len(obj.r))]
    obj.z = [obj.r[ind][2] for ind in range(len(obj.r))]

    obj.table_x = [obj.r[ind][0] for ind in range(len(obj.table_r))]
    obj.table_y = [obj.r[ind][1] for ind in range(len(obj.table_r))]
    obj.table_z = [obj.r[ind][2] for ind in range(len(obj.table_r))]

    # rotate phantom normal vectors
    obj.normals = [np.dot(Rx, np.dot(Ry, np.dot(Rz, obj.normals[ind])))
                   for ind in range(len(obj.normals))]

    return obj

def position_source(pd, Ra, Rb):

    source = np.array([0, pd.DSI[0], 0])
    source = np.transpose(Rb.dot(Ra)).dot(source)

    source = np.asarray(source)

    return source


def position_source2(a, Ra, Rb):

    a.source = np.transpose(Rb.dot(Ra)).dot(a.source)


def position_detector2(data_parsed, Ra, Rb, i):

    x_det = detector_width * np.array([+0.5, +0.5, -0.5, -0.5])
    z_det = detector_width * np.array([+0.5, -0.5, -0.5, +0.5])
    y_det = data_parsed.DID[i] * np.array([-1, -1, -1, -1])

    r_det = [[x_det[ind], y_det[ind], z_det[ind]]
             for ind in range(len(x_det))]

    r = [np.dot(np.transpose(np.dot(Rb, Ra)), r[ind]) for ind in range(len(x))]


def position_ray(pd, Ra, Rb, i):

    ray = np.array([[+0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], +0.5*np.sqrt(pd.CFA[i])],
                    [+0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], -0.5*np.sqrt(pd.CFA[i])],
                    [-0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], -0.5*np.sqrt(pd.CFA[i])],
                    [-0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], +0.5*np.sqrt(pd.CFA[i])]])

    for index in range(0, len(ray)):
        ray[index, :] = np.transpose(Rb.dot(Ra)).dot(ray[index, :])

    return ray


def position_phantom(ptm, parsed_data, i):

    x = ptm.x_ref - parsed_data.T_LONG[i]
    y = ptm.y_ref + parsed_data.T_VERT[i]
    z = ptm.z_ref + parsed_data.T_LAT[i]

    ptm.x = x
    ptm.y = y
    ptm.z = z


def position_phantom2(ptm, parsed_data, i):

    x = ptm.x_ref - parsed_data.T_LONG[i]
    y = ptm.y_ref + parsed_data.T_VERT[i]
    z = ptm.z_ref + parsed_data.T_LAT[i]

    r = [[x[ind], y[ind], z[ind]] for ind in range(len(x))]

    ptm.x = x
    ptm.y = y
    ptm.z = z
    ptm.r = r


def CheckHit(source, ray, cell_location: List[List[float]],
             cell_normals: List[List[float]]=None):

    v1 = Vector(source, ray[0, :], "unit")
    v2 = Vector(source, ray[1, :], "unit")
    v3 = Vector(source, ray[2, :], "unit")
    v4 = Vector(source, ray[3, :], "unit")

    N1 = np.cross(v1, v2)
    N2 = np.cross(v2, v3)
    N3 = np.cross(v3, v4)
    N4 = np.cross(v4, v1)

    cells_vectors = [Vector(source, cell) for cell in cell_location]

    if cell_normals is not None:

        hits = [True if
                np.dot(cells_vectors[ind], N1) <= 0 and
                np.dot(cells_vectors[ind], N2) <= 0 and
                np.dot(cells_vectors[ind], N3) <= 0 and
                np.dot(cells_vectors[ind], N4) <= 0 and
                np.dot(cells_vectors[ind], cell_normals[ind]) <= 0
                else False
                for ind in range(len(cells_vectors))]

    else:

        hits = [True if
                np.dot(cells_vectors[ind], N1) <= 0 and
                np.dot(cells_vectors[ind], N2) <= 0 and
                np.dot(cells_vectors[ind], N3) <= 0 and
                np.dot(cells_vectors[ind], N4) <= 0
                else False
                for ind in range(len(cells_vectors))]

    return hits


def addKerma(pd, hits, i):

    eventKerma = pd.DoseRP_Gy[i]

    kerma = [eventKerma if hits[ind] is True
             else 0 for ind in range(len(hits))]

    kerma = np.asarray(kerma)

    return kerma


def Vector(start, stop, normalization=0):

    # Calculate vector from start to stop
    v = stop - start

    # If unit vector
    if normalization == "unit":
        # Normalize vector
        mag = np.sqrt(v.dot(v))
        v = v/mag

    return v


def FluenceCorrection(source, phantom, hits, pd, i):

    r = [[Vector(source, phantom.r[ind])] for ind in range(len(phantom.r))]

    d = [np.sqrt(np.dot(x, x)) for x in r]
    d_ref = pd.DSIRP

    k_isq = [np.sqrt(x/d_dref) for x in d]

    return k_isq
