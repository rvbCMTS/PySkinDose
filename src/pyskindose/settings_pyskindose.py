import json
from typing import Union

from pyskindose.constants import (
    KEY_PARAM_ESTIMATE_K_TAB,
    KEY_PARAM_HUMAN_MESH,
    KEY_PARAM_K_TAB_VAL,
    KEY_PARAM_MODE,
    KEY_PARAM_PHANTOM_MODEL,
    KEY_PARAM_RDSR_FILENAME,
    OFFSET_LATERAL_KEY,
    OFFSET_LONGITUDINAL_KEY,
    OFFSET_VERTICAL_KEY,
)


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
    phantom : PhantomSettings
        Instance of class PhantomSettings containing all phantom related
        settings.
    plot : Plotsettings
        Instace of class Plottsettings containing all plot related settings

    """

    def __init__(self, settings: Union[str, dict]):
        """Initialize settings class.

        Parameters
        ----------
        settings : Union[str, dict]
            settings : Union[str, dict]
            Either a .json string or a dictionary containing all the settings
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

        main_attrs_str = create_attrs_str(attrs_parent=self, object_name="general", indent_level=0)

        if return_as_string:
            return main_attrs_str

        return print(main_attrs_str)


class PhantomSettings:
    """A class for setting all the phantom related settings required.

    Attributes
    ----------
    model : str
        Select which model to represent the skin surface for skindose
        calculations. Valid selections: "plane" (2D planar surface),
        "cylinder" (cylinder with elliptical cross section) or "human" (phantom
        in the shape of a human, created with MakeHuman.)
    human_mesh: str
        Select which MakeHuman phantom to represent the patient when
        model = "human" is selected. Valid selections: Any of the .stl files
        in the folder phantom_data. Enter as a string without the .stl file
        ending.
    patient_offset : PhantomOffset
        Instance of class PhantomOffset containing patient - table isocenter
        offset.
    patient_orientation : str
        patient orientation on table. Choose between 'head_first_supine' and
        'feet_first_supine'.
    dimension : PhantomDimensions
        Instance of class PhantomDimensions containing all dimensions required
        to create any of the mathematical phantoms, which is all but human.

    """

    def __init__(self, ptm_dim: dict):
        """Initialize phantom settings class.

        Parameters
        ----------
        ptm_dim : PhantomDimensions
            Instance of class PhantomDimensions containing all dimensions for
            the mathematical phantoms. See attributes of PhantomDimensions.

        """
        self.model = ptm_dim[KEY_PARAM_PHANTOM_MODEL]
        self.human_mesh = ptm_dim[KEY_PARAM_HUMAN_MESH]
        self.patient_orientation = ptm_dim["patient_orientation"]
        self.patient_offset = PatientOffset(offset=ptm_dim["patient_offset"])
        self.dimension = PhantomDimensions(ptm_dim=ptm_dim["dimension"])

        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="phantom", indent_level=0)
        return

    def update_attrs_str(self):
        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="phantom", indent_level=0)


class PhantomDimensions:
    """A class for setting the phantom dimensions for mathematical phantoms.

    Attributes
    ----------
    plane_length : int
        Lenth of plane phantom.
    plane_width : int
        Width of plane phantom.
    plane_resolution: str
        Select either 'sparse' or 'dense' resolution of the skin cell grid
        on the surface of the plane phantom. Note: dense is more computational
        expensive.
    cylinder_length : int
        Length of cylider phantom.
    cylinder_radii_a : float
        First radii of the cylindrical cross section of the cylindrical
        phantom, which lies in the "width" direction.
    cylinder_radii_b : float
        Second radii of the cylindrical cross section of the cylindrical
        phantom, which lies in the "thickness" direction. radii a should
        be greater than radii b.
    cylinder_resolution: str
        Select either 'sparse' or 'dense' resolution of the skin cell grid
        on the surface of the elliptical cylinder. Note: dense is more
        computational expensive.
    table_thickness : int
        Thickness of the support table phantom.
    table_length : int
        Length of the support table phantom.
    table_width : int
        Width of the support table phantom.
    pad_thickness : int
        Thickness of the patient support table phantom.
    pad_width : int
        Width of the patient support table phantom.
    pad_length : int
        Length of the patient support table phantom.

    """

    def __init__(self, ptm_dim: dict):
        """Initialize phantom dimension class.

        Parameters
        ----------
        ptm_dim : dict
            Dictionary containing all of the phantom dimensions that are
            appended as attributes to this class, see class attributes.

        """
        for dimension in ptm_dim.keys():
            setattr(self, dimension, ptm_dim[dimension])

        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="dimensions", indent_level=1)

    def update_attrs_str(self):
        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="dimension", indent_level=1)


class PatientOffset:
    """A class for setting patient - table offset.

    In PyskinDose, the table isocenter is located centered at the head end
    of the support table. The attributes in this class is used to offset the
    patient phantom from this isocenter, in order to get correct patient
    positioning.

    Attributes
    ----------
    d_lat : int
        latertal offset from table isocenter
    d_ver : int
        Vertical offset from table isocenter
    d_lon : int
        longitudianl offset from table isocenter

    Raises
    ------
    NotImplementedError
            Raises error if other units then cm are used.

    """

    def __init__(self, offset: dict):
        """Initialize patient-table offset class.

        Parameters
        ----------
        offset : dict
            offset in cm from the table isocenter in the lateral, vertical and
            longitudinal direction.

        """
        self.d_lat = offset[OFFSET_LATERAL_KEY]
        self.d_ver = offset[OFFSET_VERTICAL_KEY]
        self.d_lon = offset[OFFSET_LONGITUDINAL_KEY]

        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="patient offset", indent_level=1)

    def update_attrs_str(self):
        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="patient offset", indent_level=1)


class Plotsettings:
    """A class for setting plot settings.

    Attributes
    ----------
    interactivity : bool
        Toggle for interactive mode when plotting dosemaps. If True,
        the dosemap will be plotted in a .html file with full interactivity.
        If False, the dosemap will be saved as static images. Static mode is
        provided to enable PySkinDose to run smooth on machines with limited
        RAM.
    dark_mode : bool
        dark mode boolean
    notebook_mode : bool
        Set true if main is called from within a notebook.
        This optimizes plot sizing for notebook output cells.
    plot_dosemap : bool, default is True
        Whether dosemap should be plotted after dose calculation
    max_events_for_patient_inclusion : int
        maximum number of irradiation event for patient inclusion in
        plot_procedure. If the SR file contains more events than this number,
        the patient phantom is not shown in plot_procedure to avoid memory
        error.
    plot_event_index : int
        Index for the event that should be plotted when mode="plot_event" is
        chosen.

    """

    def __init__(self, plt_dict):
        """Initialize plot settings class.

        Parameters
        ----------
        plt_dict : dict
            Dictionary containing all of the plot setting that are
            appended as attributes to this class, see class attributes.
        """
        for key in plt_dict.keys():
            setattr(self, key, plt_dict[key])

        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="plot", indent_level=0)

    def update_attrs_str(self):
        self.attrs_str = create_attrs_str(attrs_parent=self, object_name="plot", indent_level=0)


def create_attrs_str(attrs_parent, object_name, indent_level, indent_size=4, indent_sign=" "):

    attrs_dict = vars(attrs_parent)

    indent_marker_title = (indent_level) * indent_size * indent_sign
    indent_marker_objs = indent_marker_title + indent_size * indent_sign

    attrs_str = indent_marker_title + object_name + "\n"

    for key, val in attrs_dict.items():
        if type(val) in [str, float, bool, int]:
            if not key == "attrs_str":
                attrs_str = attrs_str + indent_marker_objs + str(key) + " : " + str(val) + "\n"
        else:
            attrs_str = attrs_str + "\n" + getattr(attrs_parent, key).attrs_str

    return attrs_str


def initialize_settings(settings: Union[str, dict, PyskindoseSettings]) -> PyskindoseSettings:
    valid_input_settings = settings is not None and isinstance(settings, (str, dict, PyskindoseSettings))

    if not valid_input_settings:
        raise ValueError("Settings must be given as a str or dict")

    if isinstance(settings, PyskindoseSettings):
        return settings

    return PyskindoseSettings(settings=settings)
