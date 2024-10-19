import numpy as np
import pandas as pd


def calculate_rotation_matrices(normalized_data: pd.DataFrame) -> pd.DataFrame:
    at = normalized_data.loc[:, ["At1", "At2", "At3"]]
    at.At1 = [np.deg2rad(val) for val in at["At1"]]  # Table Horizontal Rotation Angle, rotation axis: center of table
    at.At2 = [np.deg2rad(val) for val in at["At2"]]  # Table Head Tilt Angle, rotation axis: center of table
    at.At3 = [np.deg2rad(val) for val in at["At3"]]  # Table Cradle Tilt Angle

    return normalized_data.join(
        pd.DataFrame(
            [
                (
                    [
                        [+1, +0, +0],
                        [+0, +float(np.cos(row.At2)), -float(np.sin(row.At2))],
                        [+0, +float(np.sin(row.At2)), +float(np.cos(row.At2))],
                    ],
                    [
                        [+float(np.cos(row.At1)), +0, +float(np.sin(row.At1))],
                        [+0, +1, +0],
                        [-float(np.sin(row.At1)), +0, +float(np.cos(row.At1))],
                    ],
                    [
                        [+float(np.cos(row.At3)), -float(np.sin(row.At3)), +0],
                        [+float(np.sin(row.At3)), +float(np.cos(row.At3)), +0],
                        [+0, +0, +1],
                    ],
                )
                for row in at.itertuples()
            ],
            columns=["Rx", "Ry", "Rz"],
        )
    )
