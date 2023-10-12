import os
from pathlib import Path

import pandas as pd

file_names = [
    "hvl_tables/hvl_allura_filters_11deg.csv",
    "hvl_tables/hvl_axiom_filters_8deg.csv",
]

data_path = Path(os.path.abspath(__file__)).parent

data = [pd.read_csv(data_path / file_name) for file_name in file_names]
data_combined = pd.concat([dat for dat in data])

data_combined.to_csv(data_path / "hvl_tables/hvl_combined.csv", index=False)
