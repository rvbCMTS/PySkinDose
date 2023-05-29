import numpy as np
import spekpy as sp  # Note: Not included in PySkinDose,
import pandas as pd
import os
from pathlib import Path


def generate_spekpy_data(
    kvp_range_kv,
    Inherent_filtration_mmal,
    added_filtration_range_mmal,
    added_filtration_range_mmcu,
    added_filtration_mmair,
    device_model,
    acquisition_plane,
    anode_angle_deg,
    results_path,
    lab_name,
    file_name,
    measurement_date,
):

    index = [
        "kVp_kV",
        "InherentFiltration_mmAl",
        "AddedFiltration_mmCu",
        "AddedFiltration_mmAl",
        "AddedFiltration_mmAir",
        "DeviceModel",
        "AcquisitionPlane",
        "AnodeAngle_deg",
        "HVL_mmAl",
        "LabName",
        "MeasurementDate",
    ]

    res = dict()
    for i in index:
        res[i] = []

    for kvp in kvp_range_kv:
        print(kvp)
        for added_filtration_mmal in added_filtration_range_mmal:
            for added_filtration_mmcu in added_filtration_range_mmcu:

                filters = [("Al", Inherent_filtration_mmal + added_filtration_mmal), ("Cu", added_filtration_mmcu)]
                s = sp.Spek(kvp=kvp, th=anode_angle_deg, dk=1, z=added_filtration_mmair / 10)
                s.multi_filter(filters)

                res["kVp_kV"].append(kvp)
                res["InherentFiltration_mmAl"].append(Inherent_filtration_mmal)
                res["AddedFiltration_mmCu"].append(added_filtration_mmcu)
                res["AddedFiltration_mmAl"].append(added_filtration_mmal)
                res["AddedFiltration_mmAir"].append(added_filtration_mmair)
                res["DeviceModel"].append(device_model)
                res["AcquisitionPlane"].append(acquisition_plane)
                res["AnodeAngle_deg"].append(anode_angle_deg)
                res["HVL_mmAl"].append(s.get_hvl())
                res["LabName"].append(lab_name)
                res["MeasurementDate"].append(measurement_date)

    pd.DataFrame(res).to_csv(results_path / file_name)

# variables to enter
kvp_min = None
kvp_max = None

res = generate_spekpy_data(
    kvp_range_kv=np.linspace(kvp_min, kvp_max, kvp_max - kvp_min + 1),
    Inherent_filtration_mmal=None,
    added_filtration_range_mmal=None,
    added_filtration_range_mmcu=None,
    added_filtration_mmair=None,
    device_model=None,
    acquisition_plane=None,
    anode_angle_deg=None,
    results_path=Path(os.path.abspath(__file__)).parent,
    lab_name=None,
    measurement_date=None,
    file_name=None,
)