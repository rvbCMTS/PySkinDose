import numpy as np
import pandas as pd


def calculate_rotation_matrices(normalized_data: pd.DataFrame) -> pd.DataFrame:

    at1_ind = normalized_data.columns.get_loc("At1")  # Table Horizontal Rotation Angle, rotation axis: center of table
    at2_ind = normalized_data.columns.get_loc("At2")  # Table Head Tilt Angle, rotation axis: center of table
    at3_ind = normalized_data.columns.get_loc("At3")  # Table Cradle Tilt Angle

    return normalized_data.join(
        pd.DataFrame(
            [
                (
                    [
                        [+1, +0, +0],
                        [+0, +float(np.cos(np.deg2rad(row[at2_ind]))), -float(np.sin(np.deg2rad(row[at2_ind])))],
                        [+0, +float(np.sin(np.deg2rad(row[at2_ind]))), +float(np.cos(np.deg2rad(row[at2_ind])))],
                    ],
                    [
                        [+float(np.cos(np.deg2rad(row[at1_ind]))), +0, +float(np.sin(np.deg2rad(row[at1_ind])))],
                        [+0, +1, +0],
                        [-float(np.sin(np.deg2rad(row[at1_ind]))), +0, +float(np.cos(np.deg2rad(row[at1_ind])))],
                    ],
                    [
                        [+float(np.cos(np.deg2rad(row[at3_ind]))), -float(np.sin(np.deg2rad(row[at3_ind]))), +0],
                        [+float(np.sin(np.deg2rad(row[at3_ind]))), +float(np.cos(np.deg2rad(row[at3_ind]))), +0],
                        [+0, +0, +1],
                    ],
                )
                for row in normalized_data.itertuples()
            ],
            columns=["Rx", "Ry", "Rz"],
        )
    )
