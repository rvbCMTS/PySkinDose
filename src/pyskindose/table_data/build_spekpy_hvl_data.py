import pandas as pd
import os
from pathlib import Path


file_names = [
    "HVL_AXIOM-Artis_4.1mmAl_SinglePlane_U106_20180328.csv",
    "HVL_AlluraClarity_3.6mmAl_SinglePlane_U601_20180418.csv",
    "HVL_AlluraClarity_4.4mmAl_PlaneA_U104_20180412.csv",
    "HVL_AlluraClarity_3.1mmAl_PlaneB_U104_20180412.csv",
]

data_path = Path(os.path.abspath(__file__)).parent

data = [pd.read_csv(data_path / file_name) for file_name in file_names]
data_combined = pd.concat([dat for dat in data])

data_combined.drop(columns=data_combined.columns[0], axis=1, inplace=True)


data_combined.to_csv(data_path / "HVL_simulated.csv", index=False)


print("Done")
