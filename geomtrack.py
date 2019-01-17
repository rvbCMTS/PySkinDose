from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
import matplotlib as mpl
import numpy as np
from typing import Dict, List


def tempname(pd):
    pd["DSI"] = pd.DistanceSourcetoIsocenter_mm/10
    pd["DSD"] = pd.DistanceSourcetoDetector_mm/10
    pd["DST"] = -pd.TableHeightPosition_mm/10 + 77.5
    pd["DIT"] = pd.DST - pd.DSI
    pd["DID"] = pd.DSD - pd.DSI
    pd["CFA"] = pd.CollimatedFieldArea_m2*10000
    pd["PPA"] = pd.PositionerPrimaryAngle_deg
    pd["PSA"] = pd.PositionerSecondaryAngle_deg
    pd["TLaP"] = pd.TableLateralPosition_mm/10
    pd["TLoP"] = pd.TableLongitudinalPosition_mm/10

    return pd


def FetchRotation(Ap1, Ap2):

    # Convert from degrees to radians
    Ap1 = np.deg2rad(Ap1)
    Ap2 = np.deg2rad(Ap2)
    # Ap3 = np.deg2rad(Ap3)

    # Define rotation about primary angle (alpha/Ap1)
    Ra = np.array([[+np.cos(Ap1), +np.sin(Ap1), +0],
                   [-np.sin(Ap1), +np.cos(Ap1), +0],
                   [+0,           +0,           +1]])

    # Define rotation about secondary angle (beta/Ap2)
    Rb = np.array([[+1, +0,           +0],
                   [+0, +np.cos(Ap2), -np.sin(Ap2)],
                   [+0, +np.sin(Ap2), +np.cos(Ap2)]])

    # Define rotation about ? angle (Ap3)
    # Rc = np.array([[+np.cos(Ap3), -np.sin(Ap3), +0],
    #                [+np.sin(Ap3), +np.cos(Ap3), +0],
    #                [+0,           +0,           +1]])

    return Ra, Rb


# Ra, Rb, Rc = FetchRotation(Ap1, Ap2, Ap3)

def CreateDetector(DD, pd, Ra, Rb, i):

    detector = np.array([[+0.5*DD, -pd.DID[i], +0.5*DD],
                         [+0.5*DD, -pd.DID[i], -0.5*DD],
                         [-0.5*DD, -pd.DID[i], -0.5*DD],
                         [-0.5*DD, -pd.DID[i], +0.5*DD],
                         [+0.5*DD, -pd.DID[i], +0.5*DD]])

    for index in range(0, len(detector)):
        detector[index, :] = np.transpose(Rb.dot(Ra)).dot(detector[index, :])

    return detector


def CreateRay(pd, Ra, Rb, i):

    ray = np.array([[+0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], +0.5*np.sqrt(pd.CFA[i])],
                    [+0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], -0.5*np.sqrt(pd.CFA[i])],
                    [-0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], -0.5*np.sqrt(pd.CFA[i])],
                    [-0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], +0.5*np.sqrt(pd.CFA[i])],
                    [+0.5*np.sqrt(pd.CFA[i]), -pd.DID[i], +0.5*np.sqrt(pd.CFA[i])]])

    for index in range(0, len(ray)):
        ray[index, :] = np.transpose(Rb.dot(Ra)).dot(ray[index, :])

    return ray


def CreateTable(TL=200, TW=50):
    table = np.array([[+0.50*TW, 0, +0.4*TL],
                      [+0.25*TW, 0, +0.4*TL],
                      [+0.25*TW, 0, +0.5*TL],
                      [-0.25*TW, 0, +0.5*TL],
                      [-0.25*TW, 0, +0.4*TL],
                      [-0.50*TW, 0, +0.4*TL],
                      [-0.50*TW, 0, -0.5*TL],
                      [+0.50*TW, 0, -0.5*TL]])
    return table


def PositionSource(source, Ra, Rb):
    source = np.transpose(Rb.dot(Ra)).dot(source)
    return source


def PositionTable(phantom, pd, i):
    phantom2 = np.zeros([len(phantom), 3])
    phantom2[:, 0] = phantom[:, 0] + pd.TLoP[i]
    phantom2[:, 1] = phantom[:, 1] - pd.DIT[i]
    phantom2[:, 2] = phantom[:, 2] + pd.TLaP[i]
    phantom2[:, 2] = phantom2[:, 2] - pd.TLaP[0]
    return phantom2


def PositionPhantom(ptm, pd, i):
    phantom = {}
    phantom["x"] = ptm["x"] + pd.TLoP[i]
    phantom["y"] = ptm["y"] - pd.DIT[i]
    phantom["z"] = ptm["z"] + pd.TLaP[i]
    phantom["z"] = phantom["z"] - pd.TLaP[0]

    return phantom


def PositionPatient(ptm, ang, table):
    ang = np.deg2rad(ang)
    Rx = np.array([[+1, +0,           +0],
                   [+0, +np.cos(ang), -np.sin(ang)],
                   [+0, +np.sin(ang), +np.cos(ang)]])

    for i in range(0, len(ptm["x"])):
        temp = Rx.dot(np.array([ptm["x"][i], ptm["y"][i], ptm["z"][i]]))
        ptm["x"][i] = temp[0]
        ptm["y"][i] = temp[1]
        ptm["z"][i] = temp[2]
        ptm["normals"][i] = Rx.dot(np.array([ptm["normals"][i][0],
                                             ptm["normals"][i][1],
                                             ptm["normals"][i][2]]))
    # Fix vertically at zero
    ptm["y"] = ptm["y"] - max(ptm["y"])

    ptm["z"] = ptm["z"] - abs(min(table[:, 2])-min(ptm["z"]))

    return ptm


def CheckHit(source, ray, points: List[List[float]]):
    v1 = Vector(source, ray[0, :], "unit")
    v2 = Vector(source, ray[1, :], "unit")
    v3 = Vector(source, ray[2, :], "unit")
    v4 = Vector(source, ray[3, :], "unit")

    N1 = np.cross(v1, v2)
    N2 = np.cross(v2, v3)
    N3 = np.cross(v3, v4)
    N4 = np.cross(v4, v1)

    point_vectors = [Vector(source, point) for point in points]
    #v = Vector(source, point)

    hits = [1 if np.dot(v, N1) <= 0 and np.dot(v, N2) <= 0 and np.dot(v, N3) <= 0 and np.dot(v, N4) <= 0 else 0
            for v in point_vectors]
    return hits

    #if np.dot(v, N1) <= 0 and np.dot(v, N2) <= 0 and np.dot(v, N3) <= 0 and np.dot(v, N4) <= 0:
    #    hit = 1
    #else:
    #    hit = 0

    return hit


def Vector(start, stop, normalization=0):

    # Calculate vector from start to stop
    v = stop - start

    # If unit vector
    if normalization == "unit":
        # Normalize vector
        mag = np.sqrt(v.dot(v))
        v = v/mag

    return v
