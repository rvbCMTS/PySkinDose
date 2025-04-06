import json
from pathlib import Path
from typing import Optional, Union

from rich import print

from pyskindose.constants import (
    KEY_PARAM_ESTIMATE_K_TAB,
    KEY_PARAM_INHERENT_FILTRATION,
    KEY_PARAM_K_TAB_VAL,
    KEY_PARAM_MODE,
    KEY_PARAM_RDSR_FILENAME,
    KEY_PARAM_REMOVE_INVALID_ROWS,
    KEY_PARAM_SILENCE_PYDICOM_WARNINGS,
    RUN_ARGUMENTS_OUTPUT_DICT,
    RUN_ARGUMENTS_OUTPUT_HTML,
    RUN_ARGUMENTS_OUTPUT_JSON,
    RUN_ARGUMENTS_VALID_OUTPUT_FORMATS,
)

from .normalization_settings import NormalizationSettings
from .phantom_settings import PhantomSettings
from .plot_settings import Plotsettings


class PyskindoseSettings:
    """A class to store all settings required to run PySkinDose.

    Attributes
    ----------
    mode : str
        Select which mode to execute PySkinDose with. There are three
        different modes:

        mode = "calculate_dose" calculates the skin dose from the RDSR data and
        presents the result in a skin dose map.

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
        Whether k_tab should be approximated or not. You should set this to true if you
        have not conducted table attenuation measurements.
    k_tab_val : float
        Value of k_tab, in range 0.0 -> 1.0.
    inherent_filtration : float
        X-ray tube inherent filtration, for backscatter and medium correction.
    phantom : pyskindose.settings.phantom_settings.PhantomSettings
        Instance of class PhantomSettings containing all phantom related
        settings.
    plot : pyskindose.settings.plot_settings.Plotsettings
        Instance of class Plotsettings containing all plot related settings

    """

    def __init__(
        self,
        settings: Union[str, dict],
        normalization_settings: Optional[Union[Path, str, dict, NormalizationSettings]] = None,
        file_result_output_path: Optional[Union[str, Path]] = None,
        output_format: str = RUN_ARGUMENTS_OUTPUT_HTML,
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

        if (output_format := output_format.lower()) not in RUN_ARGUMENTS_VALID_OUTPUT_FORMATS:
            raise ValueError(
                f"The output format must be specified as one of {', '.join(RUN_ARGUMENTS_VALID_OUTPUT_FORMATS)}"
            )

        self.mode = tmp[KEY_PARAM_MODE]
        self.output_format = output_format
        self.file_result_output_path: Path = self._initialize_output_path(
            output_path=file_result_output_path, output_format=output_format
        )
        self.k_tab_val = tmp[KEY_PARAM_K_TAB_VAL]
        self.inherent_filtration = tmp[KEY_PARAM_INHERENT_FILTRATION]
        self.silence_pydicom_warnings = tmp[KEY_PARAM_SILENCE_PYDICOM_WARNINGS]
        self.rdsr_filename = tmp[KEY_PARAM_RDSR_FILENAME]
        self.estimate_k_tab = tmp[KEY_PARAM_ESTIMATE_K_TAB]
        self.phantom = PhantomSettings(ptm_dim=tmp["phantom"])
        self.plot = Plotsettings(plt_dict=tmp["plot"])
        self.corrections_db_path = tmp.get("corrections_db_path", "corrections.db")

        self.normalization_settings = self._initialize_normalization_settings(normalization_settings)

        self.remove_invalid_rows: bool = True if tmp.get(KEY_PARAM_REMOVE_INVALID_ROWS) else None

    @staticmethod
    def _initialize_output_path(output_path: Optional[Union[str, Path]], output_format: str) -> Path:
        if output_path is None:
            output = Path.cwd() / "PlotOutputs"

            if output_format in (RUN_ARGUMENTS_OUTPUT_DICT, RUN_ARGUMENTS_OUTPUT_JSON):
                return output  # Return without creating the output directory as it won't be used

            output.mkdir(exist_ok=True)
            return output

        if isinstance(output_path, str):
            output_path = Path(output_path)

        if not isinstance(output_path, Path):
            raise TypeError("file_result_output_path must be a string or a Path object")

        if output_path.is_dir():
            return output_path

        raise ValueError("file_result_output_path must be a path to a directory")

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
        phantom_settings_string = self.phantom.to_printable_string(color="bright_magenta")
        plot_settings_string = self.plot.to_printable_string(color="steel_blue1")
        normalization_settings_string = self.normalization_settings.to_printable_string(color="bright_green")

        color = "bright_cyan"

        output_str = (
            f"[b u {color}]General settings[/b u {color}]\n"
            f"\t[{color}]mode:\t{self.mode}[/{color}]\n"
            f"\t[{color}]rdsr_filename:\t{self.rdsr_filename}[/{color}]\n"
            f"\t[{color}]estimate_k_tab:\t{'True' if self.estimate_k_tab else 'False'}[/{color}]\n"
            f"\t[{color}]silence_pydicom_warnings:\t{'True' if self.silence_pydicom_warnings else 'False'}[/{color}]\n"
            f"\n{phantom_settings_string}"
            f"\n{plot_settings_string}"
            f"\n{normalization_settings_string}"
        )

        if return_as_string:
            return output_str

        return print(output_str)


def initialize_settings(settings: Union[str, dict, PyskindoseSettings]) -> PyskindoseSettings:
    valid_input_settings = settings is not None and isinstance(settings, (str, dict, PyskindoseSettings))

    if not valid_input_settings:
        raise ValueError("Settings must be given as a str or dict")

    if isinstance(settings, PyskindoseSettings):
        return settings

    return PyskindoseSettings(settings=settings)
