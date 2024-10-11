from typing import Any, Dict, List, Optional

import pandas as pd

from pyskindose.constants import (
    KEY_NORMALIZATION_DETECTOR_SIDE_LENGTH,
    KEY_NORMALIZATION_FIELD_SIZE_MODE,
    KEY_NORMALIZATION_MANUFACTURER,
    KEY_NORMALIZATION_MODELS,
    KEY_RDSR_MANUFACTURER,
    KEY_RDSR_MANUFACTURER_MODEL_NAME,
)
from pyskindose.helpers.create_attributes_string import create_attributes_string
from pyskindose.settings.rotation_direction import RotationDirection
from pyskindose.settings.translation_direction import TranslationDirection
from pyskindose.settings.translation_offset import TranslationOffset


class NormalizationSettings:
    """A class to normalize RDSR for PySkinDose compliance.

    Attributes
    ----------
    trans_offset : pyskindose.settings.translation_offset.TranslationOffset
        See class variables of _TranslationOffset
    trans_dir : pyskindose.settings.translation_direction.TranslationDirection
        See class variables of _TranslationDirection
    rot_dir : pyskindose.settings.rotation_direction.RotationDirection
        See class variables of _RotationDirection
    field_size_mode : str
        method for calculating field size at image receptor plane.
        Choose either "CFA" (collimated field area) or "ACD" (actual shutter
        distance). For more info, see calculate_field_size in geom_calc.py.
    detector_side_length : str
        side length of active image receptor area in cm.

    """

    def __init__(self, normalization_settings: List[Dict[str, Any]]):
        """Initialize class attributes."""
        self.normalization_settings_list: List[Dict[str, Any]] = normalization_settings
        self.trans_offset: TranslationOffset = TranslationOffset()
        self.trans_dir: TranslationDirection = TranslationDirection()
        self.rot_dir: RotationDirection = RotationDirection()
        self.field_size_mode: Optional[str] = None
        self.detector_side_length: Optional[str] = None

        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="normalization", indent_level=0)

    def update_used_settings(self, data_parsed: pd.DataFrame):
        manufacturer = data_parsed[KEY_RDSR_MANUFACTURER][0].casefold()
        model = data_parsed[KEY_RDSR_MANUFACTURER_MODEL_NAME][0].casefold()

        setting = [
            setting
            for setting in self.normalization_settings_list
            if manufacturer == setting[KEY_NORMALIZATION_MANUFACTURER].casefold()
            and model in [mod.casefold() for mod in setting[KEY_NORMALIZATION_MODELS]]
        ]

        if not setting:
            raise NotImplementedError(
                f"Could not find settings for the given manufacturer and model ({manufacturer=}, {model=})"
            )

        setting = setting[0]

        self.trans_offset.update_translation_offset(offset=setting.get("translation_offset"))
        self.trans_dir.update_translation_direction(directions=setting.get("translation_direction"))
        self.rot_dir.update_rotation_direction(directions=setting.get("rotation_direction"))
        self.field_size_mode = setting[KEY_NORMALIZATION_FIELD_SIZE_MODE]
        self.detector_side_length = setting[KEY_NORMALIZATION_DETECTOR_SIDE_LENGTH]

        self.update_attrs_str()

    def update_attrs_str(self):
        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="normalization", indent_level=0)

    def to_printable_string(self, color: str = "blue"):
        return (
            f"[bold {color}]Normalization settings[/bold {color}]\n"
            f"\t[{color}]trans_offset:[/{color}]\n"
            f"\t\t[{color}]x:{self.trans_offset.x}[/{color}]\n"
            f"\t\t[{color}]y:{self.trans_offset.y}[/{color}]\n"
            f"\t\t[{color}]z:{self.trans_offset.z}[/{color}]\n"
            f"\t[{color}]trans_dir:[/{color}]\n"
            f"\t\t[{color}]x:{self.trans_dir.x}[/{color}]\n"
            f"\t\t[{color}]y:{self.trans_dir.y}[/{color}]\n"
            f"\t\t[{color}]z:{self.trans_dir.z}[/{color}]\n"
            f"\t[{color}]rot_dir:[/{color}]\n"
            f"\t\t[{color}]Ap1:{self.rot_dir.Ap1}[/{color}]\n"
            f"\t\t[{color}]Ap2:{self.rot_dir.Ap2}[/{color}]\n"
            f"\t\t[{color}]Ap3:{self.rot_dir.Ap3}[/{color}]\n"
            f"\t\t[{color}]At1:{self.rot_dir.At1}[/{color}]\n"
            f"\t\t[{color}]At2:{self.rot_dir.At2}[/{color}]\n"
            f"\t\t[{color}]At3:{self.rot_dir.At3}[/{color}]\n"
            f"\t[{color}]field_size_mode: {self.field_size_mode}[/{color}]\n"
            f"\t[{color}]detector_side_length: {self.detector_side_length}[/{color}]\n"
        )
