import pandas as pd
from pathlib import Path
import json
from .settings_normalization import NormalizationSettings
from .geom_calc import calculate_field_size


def rdsr_normalizer(data_parsed: pd.DataFrame) -> pd.DataFrame:

    data_norm = pd.DataFrame()
    normalization_settings_path = \
        Path(__file__).parent / "normalization_settings.json"

    with normalization_settings_path.open("r") as json_file:
        normalization_settings = json.load(json_file)

    norm = NormalizationSettings(
        normalization_settings=normalization_settings,
        data_parsed=data_parsed)

    data_norm = _normalize_machine_parameters(
        data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    data_norm = _normalize_table_parameters(
        data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    data_norm = _normalize_beam_parameters(
            data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    return data_norm


def _normalize_machine_parameters(
        data_parsed: pd.DataFrame,
        data_norm: pd.DataFrame,
        norm: NormalizationSettings) -> pd.DataFrame:

    data_norm['model'] = data_parsed.ManufacturerModelName
    data_norm['DSD'] = data_parsed.DistanceSourcetoDetector_mm / 10
    data_norm['DSI'] = data_parsed.DistanceSourcetoIsocenter_mm / 10
    data_norm['DID'] = data_norm.DSD - data_norm.DSI
    data_norm["DSIRP"] = data_norm.DSI - 15
    data_norm["acquisition_type"] = data_parsed.IrradiationEventType
    data_norm["acquisition_plane"] = data_parsed.AcquisitionPlane

    return data_norm


def _normalize_table_parameters(
        data_parsed: pd.DataFrame,
        data_norm: pd.DataFrame,
        norm: NormalizationSettings) -> pd.DataFrame:

    # Table translations
    data_norm['Tx'] = norm.trans_offset.x + \
        norm.trans_dir.x * data_parsed.TableLongitudinalPosition_mm / 10

    data_norm['Ty'] = norm.trans_offset.y + \
        norm.trans_dir.y * data_parsed.TableHeightPosition_mm / 10

    data_norm['Tz'] = norm.trans_offset.z + \
        norm.trans_dir.z * data_parsed.TableLateralPosition_mm / 10

    # Table rotations
    data_norm["At1"] = norm.rot_dir.At1 * [0] * len(data_norm)
    data_norm["At2"] = norm.rot_dir.At2 * [0] * len(data_norm)
    data_norm["At3"] = norm.rot_dir.At3 * [0] * len(data_norm)

    return data_norm


def _normalize_beam_parameters(
        data_parsed: pd.DataFrame,
        data_norm: pd.DataFrame,
        norm: NormalizationSettings) -> pd.DataFrame:

    # beam angulation
    data_norm["Ap1"] = norm.rot_dir.Ap1 * \
            data_parsed.PositionerPrimaryAngle_deg
    data_norm["Ap2"] = norm.rot_dir.Ap2 * \
        data_parsed.PositionerSecondaryAngle_deg
    # temp set to zero
    data_norm["Ap3"] = norm.rot_dir.Ap3 * [0] * len(data_norm)

    # detector side length
    data_norm['DSL'] = norm.detector_side_length

    FS_lat, FS_long = calculate_field_size(
        field_size_mode=norm.field_size_mode,
        data_parsed=data_parsed,
        data_norm=data_norm)

    data_norm['FS_lat'] = FS_lat
    data_norm['FS_long'] = FS_long

    data_norm['kVp'] = data_parsed.KVP_kV
    data_norm['K_IRP'] = data_parsed.DoseRP_Gy * 1000

    data_norm["filter_thickness_Cu"] = \
        (data_parsed.XRayFilterThicknessMaximum_mm)

    data_norm.filter_thickness_Cu = (data_norm.filter_thickness_Cu.fillna(0.0))

    data_norm["filter_thickness_Al"] = (
        [0.0] * len(data_parsed.XRayFilterThicknessMaximum_mm))

    return data_norm