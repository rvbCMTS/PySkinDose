import numpy as np
import spekpy as sp  # Note: Not included in PySkinDose,
import pandas as pd
import os
from pathlib import Path


def generate_spekpy_data(
    kvpRange_kV,
    InherentFiltration_mmAl,
    AddedFiltrationRange_mmAl,
    AddedFiltrationRange_mmCu,
    AddedFiltration_mmAir,
    DeviceModel,
    AcquisitionPlane,
    AnodeAngle_deg,
    ResultsPath,
    LabName,
    FileName,
    MeasurementDate,
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

    for kvp in kvpRange_kV:
        print(kvp)
        for AddedFiltration_mmAl in AddedFiltrationRange_mmAl:
            for AddedFiltration_mmCu in AddedFiltrationRange_mmCu:

                filters = [("Al", InherentFiltration_mmAl + AddedFiltration_mmAl), ("Cu", AddedFiltration_mmCu)]
                s = sp.Spek(kvp=kvp, th=AnodeAngle_deg, dk=1, z=AddedFiltration_mmAir / 10)
                s.multi_filter(filters)

                res["kVp_kV"].append(kvp)
                res["InherentFiltration_mmAl"].append(InherentFiltration_mmAl)
                res["AddedFiltration_mmCu"].append(AddedFiltration_mmCu)
                res["AddedFiltration_mmAl"].append(AddedFiltration_mmAl)
                res["AddedFiltration_mmAir"].append(AddedFiltration_mmAir)
                res["DeviceModel"].append(DeviceModel)
                res["AcquisitionPlane"].append(AcquisitionPlane)
                res["AnodeAngle_deg"].append(AnodeAngle_deg)
                res["HVL_mmAl"].append(s.get_hvl())
                res["LabName"].append(LabName)
                res["MeasurementDate"].append(MeasurementDate)

    pd.DataFrame(res).to_csv(ResultsPath / FileName)




# variables to enter
kvp_min = None
kvp_max = None
InherentFiltration_mmAl = None
AddedFiltrationRange_mmAl = None
AddedFiltrationRange_mmCu = None
AddedFiltration_mmAir = None
DeviceModel = None
AcquisitionPlane = None
AnodeAngle_deg = None
LabName = None
MeasurementDate = None
ResultsPath = Path(os.path.abspath(__file__)).parent
FileName = None
FileName = FileName.replace(" ", "")

res = generate_spekpy_data(
    kvpRange_kV=np.linspace(kvp_min, kvp_max, kvp_max - kvp_min + 1),
    InherentFiltration_mmAl=InherentFiltration_mmAl,
    AddedFiltrationRange_mmAl=AddedFiltrationRange_mmAl,
    AddedFiltrationRange_mmCu=AddedFiltrationRange_mmCu,
    AddedFiltration_mmAir=AddedFiltration_mmAir,
    DeviceModel=DeviceModel,
    AcquisitionPlane=AcquisitionPlane,
    AnodeAngle_deg=AnodeAngle_deg,
    ResultsPath=ResultsPath,
    LabName=LabName,
    MeasurementDate=MeasurementDate,
    FileName=FileName,
)