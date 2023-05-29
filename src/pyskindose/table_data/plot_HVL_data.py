import pandas as pd
from pathlib import Path
import os
import plotly.graph_objects as go


data_path = Path(os.path.abspath(__file__)).parent
file_name = "HVL_simulated.csv"

data = pd.read_csv(data_path / file_name)

data_axiom_single = []
data_allura_single = []

filtration_axiom = [0, 0.1, 0.2, 0.3, 0.6, 0.9]


filtration_allura_al = [0, 1, 1, 1]
filtration_allura_cu = [0, 0.1, 0.4, 0.9]

for i in range(len(filtration_allura_al)):
    data_allura_single.append(
        data.loc[
            (data["DeviceModel"] == "Allura Clarity")
            & (data["AcquisitionPlane"] == "Single Plane")
            & (data["AddedFiltration_mmCu"] == filtration_allura_cu[i])
            & (data["AddedFiltration_mmAl"] == filtration_allura_al[i])
        ]
    )

for filtration_cu in filtration_axiom:
    data_axiom_single.append(
        data.loc[
            (data["DeviceModel"] == "AXIOM-Artis")
            & (data["AcquisitionPlane"] == "Single Plane")
            & (data["AddedFiltration_mmCu"] == filtration_cu)
        ]
    )

fig = go.Figure()

for i in range(len(data_axiom_single)):
    fig.add_trace(
        go.Scatter(
            x=data_axiom_single[i]["kVp_kV"],
            y=data_axiom_single[i]["HVL_mmAl"],
            mode="lines",
            name=f"{filtration_axiom[i]} mmCu",
            marker=dict(color="red"),
        )
    )

for i in range(len(data_allura_single)):
    fig.add_trace(
        go.Scatter(
            x=data_allura_single[i]["kVp_kV"],
            y=data_allura_single[i]["HVL_mmAl"],
            mode="lines",
            name=f"{filtration_allura_al[i]} mmAl, {filtration_allura_cu[i]} mmCu",
            marker=dict(color="blue"),
        )
    )

fig.show()
