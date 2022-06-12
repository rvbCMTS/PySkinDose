from typing import Dict, Any, Union, Tuple, List

import numpy as np
from pyskindose.settings import PyskindoseSettings

from pyskindose import Phantom
from pyskindose.constants import PHANTOM_MODEL_HUMAN, PHANTOM_MODEL_TABLE


def format_analysis_result_for_export(analysis_result: Dict[str, Any], settings: Union[str, dict, PyskindoseSettings]):
    """

    Parameters
    ----------
    analysis_result
    settings

    Returns
    -------

    """


class PySkinDoseOutput:
    def __init__(self, dose_map: np.array):
        self.PSD: float = None
        self.PSD_angles_accounted: float = dose_map.max()
        self.Kerma: float = 0
        self.DoseMap: List[float] = dose_map.to_list()
        self.BackscatterCorrection: float = 1.0
        self.InverseSquareLawCorrection: float = 1.0
        self.MediumCorrection: float = 1.0
        self.TableCorrection: float = 1.0

    def to_dict(self):
        return {
            "psd": self.PSD,
            "psd_angles_accounted": self.PSD_angles_accounted,
            "kerma": self.Kerma,
            "dose_map": self.DoseMap,
            "backscatter_correction": self.BackscatterCorrection,
            "inverse_square_law_correction": self.InverseSquareLawCorrection,
            "medium_correction": self.MediumCorrection,
            "table_correction": self.TableCorrection
        }


class TableOutput:
    def __init__(self, table: Phantom):
        if table.phantom_model != PHANTOM_MODEL_TABLE:
            raise TypeError("The specified table is not a table phantom")

        self.r: np.array = table.r,
        self.ijk: np.array = table.ijk
        self.table_length: float = table.table_length


class NonHumanPhantomOutput:
    def __init__(self, phantom: Phantom):
        self.human_model = None
        self.r = phantom.r
        self.ijk = phantom.ijk
        self.r_ref = phantom.r_ref


class HumanPhantomOutput:
    def __init__(self, phantom: Phantom):
        self.human_model = phantom.human_model
        self.r = phantom.r
        self.ijk = phantom.ijk
        self.r_ref = phantom.r_ref


class DoseMapOutput:
    def __init__(
            self,
            patient_base_translation: Tuple[int, int, int],
            patient_base_rotation: Tuple[int, int, int],
            table: Phantom,
            pad: Phantom,
            patient: Phantom,
            dosemap: np.array
    ):
        self.patient_base_rotation: Tuple[int, int, int] = patient_base_rotation
        self.patient_base_translation: Tuple[int, int, int] = patient_base_translation
        self.table: TableOutput = TableOutput(table)
        self.pad: TableOutput = TableOutput(pad)
        self.patient_type: str = patient.phantom_model
        self.patient: Union[HumanPhantomOutput, NonHumanPhantomOutput] = (
            HumanPhantomOutput(patient)
            if patient.phantom_model == PHANTOM_MODEL_HUMAN else
            NonHumanPhantomOutput(patient)
        )
        self.dose_map: np.array = dosemap

    def to_dict(self):
        return {
            "table": {
                "r": self.table.r.tolist(),
                "ijk": self.table.ijk.tolist(),
                "tableLength": self.table.table_length
            },
            "pad": {
                "r": self.pad.r.tolist(),
                "ijk": self.pad.ijk.tolist()
            },
            "patient": {
                "type": self.patient_type,
                "human_phantom": self.patient.human_model,
                "r_ref": self.patient.r_ref.tolist(),
                "r": self.patient.r.tolist(),
                "ijk": self.pad.ijk.tolist()
            },
            "dosemap": self.dose_map.tolist(),
            "corrections": {
                "backscatter": [],
                "medium": [],
                "table": []
            }
        }
