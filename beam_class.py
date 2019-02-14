import numpy as np
from mayavi import mlab


class Beam:

    def __init__(self, data_parsed, i):

        self.source: np.array = None
        self.Ra: np.array = None
        self.Rb: np.array = None

        self.r_det: np.array = None
        self.x_det: np.array = None
        self.y_det: np.array = None
        self.z_det: np.array = None

        self.r_edge: np.array = None
        self.x_edge: np.array = None
        self.y_edge: np.array = None
        self.z_edge: np.array = None

        self.r_det_triangles: List[tuple] = None
        self.r_det_triangles: List[tuple] = None

        # fetch rotation
        Ap1 = np.deg2rad(data_parsed.PPA[i])
        Ap2 = np.deg2rad(data_parsed.PSA[i])

        # Define rotation about primary angle (alpha/Ap1)
        Ra = np.array([[+np.cos(Ap1), +np.sin(Ap1), +0],
                       [-np.sin(Ap1), +np.cos(Ap1), +0],
                       [+0,           +0,           +1]])

        # Define rotation about secondary angle (beta/Ap2)
        Rb = np.array([[+1, +0,           +0],
                       [+0, +np.cos(Ap2), -np.sin(Ap2)],
                       [+0, +np.sin(Ap2), +np.cos(Ap2)]])

        self.Ra = Ra
        self.Rb = Rb

        # sources
        source = np.array([0, data_parsed.DSI[i], 0])
        source = np.dot(np.dot(self.Rb, self.Ra), source)
        self.source = source

        detector_width = 40  # Fetch this from parsed data later on

        # detector
        points1 = np.array([[+0.5, -1.0, +0.5],
                           [+0.5, -1.0, -0.5],
                           [-0.5, -1.0, -0.5],
                           [-0.5, -1.0, +0.5],
                           [+0.5, -1.2, +0.5],
                           [+0.5, -1.2, -0.5],
                           [-0.5, -1.2, -0.5],
                           [-0.5, -1.2, +0.5]])

        r_det = points1
        r_det[:, 0] = detector_width * r_det[:, 0]
        r_det[:, 1] = data_parsed.DID[i] * r_det[:, 1]
        r_det[:, 2] = detector_width * r_det[:, 2]

        for ind in range(8):
            r_det[ind, :] = np.dot(np.dot(self.Rb, self.Ra), r_det[ind, :])

        self.r_det = r_det
        self.x_det = r_det[:, 0]
        self.y_det = r_det[:, 1]
        self.z_det = r_det[:, 2]
        self.r_det_triangles = [(0, 1, 2), (0, 3, 2), (4, 5, 6), (4, 7, 6),
                                (0, 1, 4), (1, 4, 5), (2, 3, 7), (2, 7, 6),
                                (1, 2, 6), (1, 6, 5), (0, 3, 4), (3, 4, 7)]

        # field
        points2 = np.array([[+0.5, -1.0, +0.5],
                            [+0.5, -1.0, -0.5],
                            [-0.5, -1.0, -0.5],
                            [-0.5, -1.0, +0.5]])

        r_edge = points2
        r_edge[:, 0] = np.sqrt(data_parsed.CFA[i]) * r_edge[:, 0]
        r_edge[:, 1] = data_parsed.DID[i] * r_edge[:, 1]
        r_edge[:, 2] = np.sqrt(data_parsed.CFA[i]) * r_edge[:, 2]

        for ind in range(4):
            r_edge[ind, :] = np.dot(np.dot(self.Rb, self.Ra), r_edge[ind, :])

        self.r_edge = r_edge
        self.x_edge = r_edge[:, 0]
        self.y_edge = r_edge[:, 1]
        self.z_edge = r_edge[:, 2]
        self.r_edge_triangles = [(0, 1, 2), (0, 1, 4), (0, 3, 2), (0, 3, 4)]
