from pathlib import Path
from typing import List

import pandas as pd
import spekpy as sp  # Note: Not included in PySkinDose,
from tqdm import tqdm


def generate_hvl_data(
    kvp_range: List[float],
    filtration_inherent_mmal: List[float],
    filtration_added_mmal: List[float],
    filtration_added_mmcu: List[float],
    anode_angle_deg: int,
    path_results: Path,
    filter_name: str,
):
    """Generate HVL data with SpekPy for k_bs and k_med selection.

    Parameters
    ----------
    kvp_range : List[float]
        list with range of kvp vals (in kV)
    filtration_inherent_mmal : float
        list of range of X-ray tube inherent filtration (in mmAl)
    filtration_added_mmal : List[float]
        X-ray tube added Al filtration. E.g. [0] for AXIOM-Artis
        or [0, 1] for Allura Clarity
    filtration_added_mmcu : List[float]
        X-ray tube added Cu filtration for spekpy spectrum generation. E.g. [0, 0.1, 0.2, 0.3, 0.6, 0.9] for AXIOM-Artis
        or [0, 0.1, 0.4, 0.9] for Allura Clarity
    anode_angle_deg : int
        Anode angle for spekpy spectrum generation. E.g. 8 for "AXIOM-Artis" or 11 for "Allura Clarity"
    path_results : Path
        The path to store results
    filter_name : str
        tag in filename for filter alternative, e.g. "allura" or "artis".

    """
    index = [
        "kvp_kv",
        "filtration_inherent_mmal",
        "filtration_added_mmal",
        "filtration_added_mmcu",
        "anode_angle_deg",
        "hvl_mmal",
    ]

    res = dict()
    for i in index:
        res[i] = []

    for kvp in tqdm(kvp_range):
        for inherent_mmal in filtration_inherent_mmal:
            for added_mmal in filtration_added_mmal:
                for added_mmcu in filtration_added_mmcu:
                    s = sp.Spek(kvp=kvp, th=anode_angle_deg, dk=1)
                    filters = [("Al", inherent_mmal + added_mmal), ("Cu", added_mmcu)]
                    s.multi_filter(filters)

                    res["kvp_kv"].append(kvp)
                    res["filtration_inherent_mmal"].append(inherent_mmal)
                    res["filtration_added_mmal"].append(added_mmal)
                    res["filtration_added_mmcu"].append(added_mmcu)
                    res["anode_angle_deg"].append(anode_angle_deg)
                    res["hvl_mmal"].append(s.get_hvl())

    file_name = f"hvl_{filter_name}_{anode_angle_deg}deg.csv"
    file_name = file_name.replace(" ", "")

    pd.DataFrame(res).to_csv(path_results / file_name, index=False)
