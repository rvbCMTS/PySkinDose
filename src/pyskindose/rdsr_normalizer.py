from typing import Optional, Union
import numpy as np
import pandas as pd
from pathlib import Path
import json

from .settings_normalization import NormalizationSettings
from .geom_calc import calculate_field_size


def rdsr_normalizer(
        data_parsed: pd.DataFrame,
        normalization_settings: Optional[Union[str, dict]] = None
        ) -> pd.DataFrame:
    """Normalize RDSR data for PySkinDose compliance.

    Parameters
    ----------
    data_parsed : pd.DataFrame
        Parsed RDSR data from all irradiation events in the RDSR input file,
        i.e. output of function rdsr_parser

    Returns
    -------
    data_norm : pd.DataFrame
        Dataframe with the following columns:
    model : str
        device model, e.g. 'AXIOM-artis
    DSD : float
        Distance Source to detector (DSD) in cm.
    DSI : float
        Distance Source to Isocenter (DSI) in cm.
    DID : float
        Distance Isocenter to Detector (DID) in cm.
    DSIRP : float
        Distance Source to intercentional reference point (DSIRP) in cm.
    acquisition_type : str
        Type of irradiation event, i.e. 'fluoroscopy, or stationary
        acquisition.
    acquisition_plane : str
        plane used for image acquisition. Either 'single plane', 'plane a', or
        plane b.
    Tx : float
        Table offset in x-direction (longitudinal direction) from the machine
        isocenter. At Tx = 0, the patient support table is centered about the
        isocenter x-axis. With patient lying in head-first supine position
        (default settings), Tx increases in patient left lateral direction.
    Ty : float
        Table offset in y-direction (vertical direction) from the machine
        isocenter. At Ty = 0, the patient support table is centered about the
        isocenter y-axis. Ty is increasing downwards, i.e. along the force
        of gravity.
    Tz : float
        Table offset in z-direction (lateral direction) from the machine
        isocenter. At Tz = 0, the head end of the patient support tables are
        located at the zero coordinate of the z-axis. With patient lying in
        head-first supine position (default settings), Tz increases in the
        patients cranial direction.

        .. image:: user/figures/table/table_translate.svg

    At1 : int
        Rotation angle of the patient support table about the isocenter
        y-axis. The center of rotation is located at the centerpoint
        of the table. Positive direction is determined by the right-hand rule
        for curve orientation about the positive isocenter y-axis.

        .. image:: user/figures/table/table_at1.svg

    At2 : int
        Tilt angel of the patient support table about the isocenter x-axis.
        The center of the tilt is located at the center of the table, with
        positive direction determined by the right-hand rule for curve
        orientations  about the positiove isocenter x-axis.

        .. image:: user/figures/table/table_at2.svg

    At3 : int
        Cradle angle of the patient support table about the isocenter
        z-axis. The center of rotation is located at the centerpoint
        of the table. Positive direction is determined by the right-hand rule
        for curve orientation about the positive isocenter z-axis.

        .. image:: user/figures/table/table_at3.svg

    Ap1 : int
        Rotation angle of the X-ray source about the isocenter z-axis. Positive
        direction is determined by the right-hand rule for curve orientation
        about the positive isocenter z-axis.

        .. image:: user/figures/beam/beam_ap1.svg

    Ap2 : int
        Rotation angle of the X-ray source about the isocenter x-axis. Positive
        direction is determined by the right-hand rule for curve orientation
        about the positive isocenter x-axis.

        .. image:: user/figures/beam/beam_ap2.svg

    Ap3 : int
        Rotation angle of the X-ray detector about the isocenter y-axis.
        Positive direction is determined by the right-hand rule for curve
        orientation about the positive isocenter y-axis.


    DSL : float
        Detector Side Length (DSL) in cm.
    FS_lat : float
        Side length of the X-ray field in the lateral direction at the image
        receptor plane.
    FS_long : float
        Side length of the X-ray field in the longitudinal direction at the
        image receptor plane.
    kVp : float
        Tube voltage in kV
    K_IRP : float
        IRP air kerma at the Interventional Reference Point (IRP).
    filter_thickness_Cu : float
        Aluminum X-ray filter thickness in mm.
    filter_thickness_Al : float
        Copper X-ray filter thickness in mm.
    """
    data_norm = pd.DataFrame()

    norm = _load_normalization_settings(
        data_parsed=data_parsed,
        norm_settings=normalization_settings
    )

    data_norm = _normalize_machine_parameters(
        data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    data_norm = _normalize_table_parameters(
        data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    data_norm = _normalize_beam_parameters(
            data_parsed=data_parsed, data_norm=data_norm, norm=norm)

    return data_norm


def _load_normalization_settings(
        data_parsed: pd.DataFrame,
        norm_settings: Optional[Union[str, dict]] = None
        ) -> NormalizationSettings:

    if norm_settings is None:

        normalization_settings_path = \
            Path(__file__).parent / "normalization_settings.json"

        with normalization_settings_path.open("r") as json_file:
            norm_settings = json.load(json_file)

    if isinstance(norm_settings, str):
        norm_settings = json.load(json_file)

    return NormalizationSettings(
        normalization_settings=norm_settings,
        data_parsed=data_parsed
    )


def _normalize_machine_parameters(
        data_parsed: pd.DataFrame,
        data_norm: pd.DataFrame,
        norm: NormalizationSettings) -> pd.DataFrame:

    data_norm['model'] = data_parsed.ManufacturerModelName

    # Find indices of nans in DistanceSourcetoDetector
    if 'nan' in str(data_parsed['DistanceSourcetoDetector_mm']).lower():
        nan_indices = data_parsed.index[
            data_parsed['DistanceSourcetoDetector_mm'].apply(np.isnan)]
        # Replace those nans with the corresponding value in
        # FinalDistanceSourcetoDetector
        data_parsed.DistanceSourcetoDetector_mm = \
            data_parsed.DistanceSourcetoDetector_mm.fillna(
                data_parsed.FinalDistanceSourcetoDetector_mm[nan_indices])

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
