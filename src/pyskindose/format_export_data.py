from dataclasses import dataclass
import json
from typing import Dict, Any, Union, Tuple, List

import numpy as np
import pandas as pd

from pyskindose.settings import PyskindoseSettings

from pyskindose import Phantom, Beam
from pyskindose.constants import (
    PHANTOM_MODEL_HUMAN,
    PLOT_TRACE_ORDER_PHANTOM_WIREFRAME,
    PLOT_TRACE_ORDER_BEAM_WIREFRAME,
    PLOT_TRACE_ORDER_DETECTOR_WIREFRAME, KEY_NORMALIZATION_AIR_KERMA, OUTPUT_KEY_HITS,
    OUTPUT_KEY_CORRECTION_BACK_SCATTER, OUTPUT_KEY_CORRECTION_MEDIUM, OUTPUT_KEY_CORRECTION_TABLE,
    OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW, RUN_ARGUMENTS_OUTPUT_DICT, RUN_ARGUMENTS_OUTPUT_JSON, OUTPUT_KEY_DOSE_MAP,
)


@dataclass
class Position:
    """Create and handle the x, y, and z-positions of, e.g., a phantom. When used for a phantom, each combination of an
    element of the same index in the x, y, and z-list represents the position of one skin cell.

    Attributes
    ----------
    x : list[float]
        A list of the x-positions, e.g., representing the x-position of a phantom's skin cells
    y : list[float]
        A list of the y-positions, e.g., representing the y-position of a phantom's skin cells
    z : list[float]
        A list of the z-positions, e.g., representing the x-position of a phantom's skin cells
    """
    x: list[float]
    y: list[float]
    z: list[float]

    def to_dict(self):
        return {
            "x": [float(el) for el in self.x],
            "y": [float(el) for el in self.y],
            "z": [float(el) for el in self.z],
        }


@dataclass
class VertexIndices:
    """Create and handle the x, y, and z-positions of, e.g., a phantom. When used for a phantom, each combination of an
    element of the same index in the x, y, and z-list represents the position of one skin cell.

    Attributes
    ----------
    i : list[float]
        A list of the i-vertex indies, e.g., representing the i-vertex indices of a phantom's skin cells
    j : list[float]
        A list of the j-vertex indices, e.g., representing the j--vertex indices of a phantom's skin cells
    k : list[float]
        A list of the k-vertex indices, e.g., representing the k-vertex indices of a phantom's skin cells
    """
    i: list[float]
    j: list[float]
    k: list[float]

    def to_dict(self):
        return {
            "i": [float(el) for el in self.i],
            "j": [float(el) for el in self.j],
            "k": [float(el) for el in self.k],
        }


class HumanPhantomOutput:
    """Create and handle a patient phantom data for output into a dict or JSON-string."""
    def __init__(self, phantom: Phantom):
        self.human_model = phantom.human_model
        self.phantom_skin_cells = Position(
            x=phantom.r[:, 0].tolist(),
            y=phantom.r[:, 1].tolist(),
            z=phantom.r[:, 2].tolist()
        )
        self.triangle_vertex_indices = VertexIndices(
            i=phantom.ijk[:, 0].tolist(),
            j=phantom.ijk[:, 1].tolist(),
            k=phantom.ijk[:, 2].tolist()
        )
        self.r_ref = phantom.r_ref

    def to_dict(self) -> dict:
        return {
            "human_phantom": self.human_model,
            "r_ref": self.r_ref.tolist(),
            "patient_skin_cells": self.phantom_skin_cells.to_dict(),
            "triangle_vertex_indices": self.triangle_vertex_indices.to_dict(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())


class NonHumanPhantomOutput(HumanPhantomOutput):
    """Create and handle non-human phantoms, that is all phantoms that are not using a human model from, e.g., an
    stl-file.

    Attributes
    ----------
    phantom_skin_cells : Position
        The positions of all the phantom skin cells
    triangle_vertex_indices : VertexIndices
        The vertex indices of all the phantom skin cells
    """
    def __init__(self, phantom: Phantom):
        super().__init__(phantom)
        self.human_model = None


class EventOutput:
    def __init__(self, patient: Phantom, table: Phantom, pad: Phantom, data_norm: pd.DataFrame):
        self.events = len(data_norm)

        self.patient = self._extract_position_list(phantom=patient, data_norm=data_norm)
        self.table = self._extract_position_list(phantom=table, data_norm=data_norm)
        self.pad = self._extract_position_list(phantom=pad, data_norm=data_norm)
        self.beam_positions, self.beam_vertex_indices, self.detector_positions, self.detector_vertex_indices = (
            [self._extract_beam_data_list(data_norm=data_norm, event=event) for event in range(len(data_norm))]
        )
        self.phantom_object_trace_order = PLOT_TRACE_ORDER_PHANTOM_WIREFRAME
        self.beam_wireframe_trace_order = PLOT_TRACE_ORDER_BEAM_WIREFRAME
        self.detector_wireframe_trace_order = PLOT_TRACE_ORDER_DETECTOR_WIREFRAME

    def _extract_position_list(self, phantom: Phantom, data_norm: pd.DataFrame) -> list[Position]:
        return [
            self._get_position_dict(phantom=phantom, data_norm=data_norm, event=ind)
            for ind in range(len(data_norm))
        ]

    @staticmethod
    def _get_position_dict(phantom: Phantom, data_norm: pd.DataFrame, event: int) -> Position:
        phantom.position(data_norm=data_norm, event=event)
        return Position(
            x=phantom.r[:, 0].tolist(),
            y=phantom.r[:, 1].tolist(),
            z=phantom.r[:, 2].tolist(),
        )

    @staticmethod
    def _extract_beam_data_list(data_norm: pd.DataFrame, event: int) -> tuple[Position, VertexIndices, Position, VertexIndices]:
        beam = Beam(data_norm, event=event, plot_setup=False)
        beam_position = Position(x=beam.r[:, 0].tolist(), y=beam.r[:, 1].tolist(), z=beam.r[:, 2].tolist())
        beam_vertex_indices = VertexIndices(
            i=beam.ijk[:, 0].tolist(),
            j=beam.ijk[:, 1].tolist(),
            k=beam.ijk[:, 2].tolist()
        )
        detector_position = Position(
            x=beam.det_r[:, 0].tolist(),
            y=beam.det_r[:, 1].tolist(),
            z=beam.det_r[:, 2].tolist()
        )
        detector_vertex_indices = VertexIndices(
            i=beam.det_ijk[:, 0].tolist(),
            j=beam.det_ijk[:, 1].tolist(),
            k=beam.det_ijk[:, 2].tolist()
        )

        return beam_position, beam_vertex_indices, detector_position, detector_vertex_indices

    def to_dict(self):
        return {
            "number_of_events": self.events,
            "patient": {
                "positions": [pos.to_dict() for pos in self.patient],
                "trace_order": self.phantom_object_trace_order
            },
            "table": {
                "positions": [pos.to_dict() for pos in self.table],
                "trace_order": self.phantom_object_trace_order
            },
            "pad": {
                "positions": [pos.to_dict() for pos in self.pad],
                "trace_order": self.phantom_object_trace_order
            },
            "beam": {
                "positions": [pos.to_dict() for pos in self.beam_positions],
                "vertex_indices": [pos.to_dict() for pos in self.beam_vertex_indices],
                "trace_order": self.beam_wireframe_trace_order,
            },
            "detector": {
                "positions": [pos.to_dict() for pos in self.beam_positions],
                "vertex_indices": [pos.to_dict() for pos in self.beam_vertex_indices],
                "trace_order": self.detector_wireframe_trace_order
            },
        }


class PySkinDoseOutput:
    """

    Attributes
    __________

    PSD : float
        The peak skin dose found in the dose map
    AirKerma : float
        The total air KERMAof the
    """
    def __init__(
            self,
            patient: Phantom,
            table: Phantom,
            pad: Phantom,
            dose_map: np.array,
            hits: list[list[float]],
            backscatter_correction: list[list[float]],
            inverse_square_law_correction: list[list[float]],
            medium_correction: list[list[float]],
            table_correction: list[list[float]],
            settings: PyskindoseSettings,
            data_norm: pd.DataFrame,
    ):
        """Create a PySkinDose output instance based on data from the PySKinDose run

        Parameters
        ----------
        patient : Phantom
            An instance of the Phantom class that represents the patient
        table : Phantom
            An instance of the Phantom class that represents the treatment table
        pad : Phantom
            An instance of the Phantom class that represents the pad
        dose_map : np.array
            A numpy array containing the calculated dose map
        hits : list[np.array]
            The numpy arrays containing information on which of the phantom cells are hit by the beam at each
            irradiation event
        backscatter_correction : list[np.array]
            A list with a numpy array for each irradiation event containing the backscatter correction determined for
            each phantom cell
        inverse_square_law_correction : list[np.array]
            A list with a numpy array for each irradiation event containing the inverse square law correction determined
            for each phantom cell
        medium_correction : list[np.array]
            A list with a numpy array for each irradiation event containing the medium correction determined for
            each phantom cell
        table_correction : list[np.array]
            A list with a numpy array for each irradiation event containing the table correction determined for
            each phantom cell
        settings : PyskindoseSettings
            The instance of the settings class used in the PySKinDose run for the current data
        data_norm : pd.DataFrame
            The RDSR data, normalized for compliance with PySkinDose's use of units etc.
        """
        self.PSD: float = dose_map.max()
        self.AirKerma: float = data_norm[KEY_NORMALIZATION_AIR_KERMA].sum()
        self.Events: EventOutput = EventOutput(
            patient=patient,
            table=table,
            pad=pad,
            data_norm=data_norm
        )
        self.PatientOffsets: dict = {
            "long": settings.phantom.patient_offset.d_lon,
            "vert": settings.phantom.patient_offset.d_ver,
            "lat": settings.phantom.patient_offset.d_lat
        }
        self.Patient: dict = {
            "patient_type": patient.phantom_model,
            "patient": (
                HumanPhantomOutput(patient)
                if patient.phantom_model == PHANTOM_MODEL_HUMAN else
                NonHumanPhantomOutput(patient)
            ),
            "orientation": settings.phantom.patient_orientation,
        }
        self.Table: Phantom = table
        self.Pad: Phantom = pad
        self.PadThickness: float = settings.phantom.dimension.pad_thickness
        self.DoseMap: np.array = dose_map
        (
            self.Hits,
            self.BackscatterCorrection,
            self.InverseSquareLawCorrection,
            self.MediumCorrection,
            self.TableCorrection
        ) = zip(*[
            ((event, ind),
             backscatter_correction[event][ind],
             inverse_square_law_correction[event][ind],
             medium_correction[event][ind],
             table_correction[event][ind],
             )
            for event, event_hits in enumerate(hits)
            for ind, hit in event_hits
            if hit
        ])

    def to_dict(self) -> dict[str, float | list[float | int]]:
        """Converts the output data into a dict

        Returns
        -------
        Dict[str, Any]
            A dict containing the output data for the PySKinDose analysis where the lists of hits and corrections have
            been made sparse in order to save space.
        """
        return {
            "psd": self.PSD,
            "air_kerma": self.AirKerma,
            "patient": {
                "patient_type": self.Patient["patient_type"],
                "patient": self.Patient["patient"].to_dict(),
                "orientation": self.Patient["orientation"],
                "offsets": self.PatientOffsets
            },
            "table": {
                "table_surface": {
                    "x": self.Table.r[:, 0],
                    "y": self.Table.r[:, 1],
                    "z": self.Table.r[:, 2],
                },
                "triangle_vertex_indices": {
                    "i": self.Table.ijk[:, 0].tolist(),
                    "j": self.Table.ijk[:, 1].tolist(),
                    "k": self.Table.ijk[:, 2].tolist(),
                },
                "table_length": self.Table.table_length
            },
            "pad": {
                "pad_surface": {
                    "x": self.Pad.r[:, 0],
                    "y": self.Pad.r[:, 1],
                    "z": self.Pad.r[:, 2],
                },
                "triangle_vertex_indices": {
                    "i": self.Pad.ijk[:, 0].tolist(),
                    "j": self.Pad.ijk[:, 1].tolist(),
                    "k": self.Pad.ijk[:, 2].tolist(),
                },
            },
            "dose_map": self.DoseMap.tolist(),
            "corrections": {
                "correction_value_index": self.Hits,
                "backscatter": self.BackscatterCorrection,
                "medium": self.MediumCorrection,
                "table": self.TableCorrection,
                "inverse_square_law": self.InverseSquareLawCorrection
            },
            "events": self.Events.to_dict(),
        }

    def to_json(self) -> str:
        """Converts the output data into a JSON string

        Returns
        -------
        str
            A JSON formatted string containing the output data
        """
        return json.dumps(self.to_dict())


def format_analysis_result_for_export(
        analysis_result: Dict[str, Any],
        data_norm: pd.DataFrame,
        patient: Phantom,
        table: Phantom,
        pad: Phantom,
        settings: PyskindoseSettings
) -> Union[PySkinDoseOutput, dict[str, Any], str]:
    """Formats the result of the PySkinDose analysis into a PySkinDoseOutput class instance that has a methods for
    converting the result to either a dict or a JSON string to facilitate building custom visualizations and for other
    custom implementations of the PySkinDose calculated data.

    Parameters
    ----------
    analysis_result : dict[str, Any]
        The dict resulting from the call to pyskindose.calculate_dose.calculate_dose.calculate_dose
    data_norm : pd.DataFrame
        The RDSR data, normalized for compliance with PySkinDose's use of units etc.
    patient : Phantom
        An instance of the Phantom class that represents the patient
    table : Phantom
        An instance of the Phantom class that represents the treatment table
    pad : Phantom
        An instance of the Phantom class that represents the pad
    settings : PyskindoseSettings
        The instance of the settings class used in the PySKinDose run for the current data

    Returns
    -------
    Union[PySkinDoseOutput, dict[str, Any], str]
        The PySKinDose formatted output as either a PySKinDoseOutput class instance, a dict or a JSON-formatted string
        depending on the output format specified in the settings
    """
    pyskindose_output = PySkinDoseOutput(
        patient=patient,
        table=table,
        pad=pad,
        dose_map=analysis_result[OUTPUT_KEY_DOSE_MAP],
        hits=[event.tolist() for event in analysis_result[OUTPUT_KEY_HITS]],
        backscatter_correction=[event.tolist() for event in analysis_result[OUTPUT_KEY_CORRECTION_BACK_SCATTER]],
        inverse_square_law_correction=[event.tolist() for event in analysis_result[OUTPUT_KEY_CORRECTION_INVERSE_SQUARE_LAW]],
        medium_correction=[event.tolist() for event in analysis_result[OUTPUT_KEY_CORRECTION_MEDIUM]],
        table_correction=[event.tolist() for event in analysis_result[OUTPUT_KEY_CORRECTION_TABLE]],
        settings=settings,
        data_norm=data_norm,
    )

    if settings.output_format == RUN_ARGUMENTS_OUTPUT_DICT:
        return pyskindose_output.to_dict()

    if settings.output_format == RUN_ARGUMENTS_OUTPUT_JSON:
        return pyskindose_output.to_json()

    return pyskindose_output
