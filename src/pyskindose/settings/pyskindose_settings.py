import json
from pathlib import Path
from typing import Union, Optional

from pyskindose.constants import (
    KEY_PARAM_ESTIMATE_K_TAB,
    KEY_PARAM_K_TAB_VAL,
    KEY_PARAM_MODE,
    KEY_PARAM_RDSR_FILENAME,
)
from .phantom_settings import PhantomSettings
from .plot_settings import Plotsettings
from .normalization_settings import NormalizationSettings
from ..helpers.create_attributes_string import create_attributes_string


class PyskindoseSettings:
    """A class to store all settings required to run PySkinDose.

    Attributes
    ----------
    mode : str
        Select which mode to execute PySkinDose with. There are three
        different modes:

        mode = "calculate_dose" calculates the skindose from the RDSR data and
        presents the result in a skindose map.

        mode = "plot_setup" plots the geometry (patient, table, pad and beam
        in starting position, i.e., before any RDSR data has been added.) This
        is useful for debugging and when manually fixating the patient phantom
        with the function "position_patient_phantom_on_table".

        mode = "plot_event" plots the geometry for a specific irradiation event
        with index = event.

        mode = "plot_procedure" plots geometry of the entire sequence of RDSR
        events provided in the RDSR file. The patient phantom is omitted for
        calculation speed in human phantom is used.

    rdsr_filename : str
        filename of the RDSR file, without the .dcm file ending.
    estimate_k_tab : bool
        Wheter k_tab should be approximated or not. You this if have not
        conducted table attenatuion measurements.
    k_tab_val : float
        Value of k_tab, in range 0.0 -> 1.0.
    phantom : pyskindose.settings.phantom_settings.PhantomSettings
        Instance of class PhantomSettings containing all phantom related
        settings.
    plot : pyskindose.settings.plot_settings.Plotsettings
        Instace of class Plottsettings containing all plot related settings

    """

    def __init__(
        self,
        settings: Union[str, dict],
        normalization_settings: Optional[Union[Path, str, dict, NormalizationSettings]] = None,
    ):
        """Initialize settings class.

        Parameters
        ----------
        settings : Union[str, dict]
            Either a JSON-string or a dictionary containing all the settings
            parameters required to run PySkinDose. See setting_example.json
            in /settings/ for example.

        """
        if isinstance(settings, str):
            tmp = json.loads(settings)
        else:
            tmp = settings

        self.mode = tmp[KEY_PARAM_MODE]
        self.k_tab_val = tmp[KEY_PARAM_K_TAB_VAL]
        self.rdsr_filename = tmp[KEY_PARAM_RDSR_FILENAME]
        self.estimate_k_tab = tmp[KEY_PARAM_ESTIMATE_K_TAB]

        self.phantom = PhantomSettings(ptm_dim=tmp["phantom"])
        self.plot = Plotsettings(plt_dict=tmp["plot"])

        self.normalization_settings = self._initialize_normalization_settings(normalization_settings)

    @staticmethod
    def _initialize_normalization_settings(
        normalization_settings: Optional[Union[Path, str, dict, NormalizationSettings]]
    ) -> NormalizationSettings:
        if normalization_settings is None:
            normalization_settings = Path(__file__).parent.parent / "normalization_settings.json"

        if isinstance(normalization_settings, Path):
            normalization_settings = normalization_settings.read_text()

        if isinstance(normalization_settings, str):
            normalization_settings = json.loads(normalization_settings)

        if isinstance(normalization_settings, dict):
            if "normalization_settings" in normalization_settings:
                normalization_settings = normalization_settings["normalization_settings"]
            normalization_settings = NormalizationSettings(normalization_settings)

        if isinstance(normalization_settings, NormalizationSettings):
            return normalization_settings

        raise TypeError(f"Invalid type {type(normalization_settings)} given for normalization_settings")

    def print_parameters(self, return_as_string: bool = False):
        """Print entire parameter class to terminal.

        Parameters
        ----------
        return_as_string : bool, optional
            Return the print statement as a string, instead of printing it
            to the terminal. The default is False.

        """
        self.phantom.patient_offset.update_attrs_str()
        self.phantom.dimension.update_attrs_str()
        self.phantom.update_attrs_str()
        self.plot.update_attrs_str()
        self.normalization_settings.update_attrs_str()

        main_attrs_str = create_attributes_string(attrs_parent=self, object_name="general", indent_level=0)

        if return_as_string:
            return main_attrs_str

        return print(main_attrs_str)


def initialize_settings(settings: Union[str, dict, PyskindoseSettings]) -> PyskindoseSettings:
    valid_input_settings = settings is not None and isinstance(settings, (str, dict, PyskindoseSettings))

    if not valid_input_settings:
        raise ValueError("Settings must be given as a str or dict")

    if isinstance(settings, PyskindoseSettings):
        return settings

    return PyskindoseSettings(settings=settings)
