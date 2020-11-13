import json
from typing import Union


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
        with the function "position_geometry".

        mode = "plot_event" plots the geometry for a specific irradiation event
        with index = event.

        mode = "plot_procedure" plots geometry of the entire sequence of RDSR
        events provided in the RDSR file. The patient phantom is omitted for
        calculation speed in human phantom is used.

    rdsr_filename : str
        filename of the RDSR file, without the .dcm file ending.
    plot_event_index : int
        Index for the event that should be plotted when mode="plot_event" is
        chosen.
    phantom : PhantomSettings
        Instance of class PhantomSettings containing all phantom related
        settings.
    plot : Plotsettings.
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

        self.mode = tmp['mode']
        self.rdsr_filename = tmp['rdsr_filename']
        self.plot_event_index = tmp['plot_event_index']
        self.estimate_k_tab = tmp['estimate_k_tab']
        self.k_tab_val = tmp['k_tab_val']
        self.phantom = PhantomSettings(ptm_dim=tmp['phantom'])
        self.plot = Plotsettings(plt_dict=tmp['plot'])


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
            the mathematical phantoms.

        """
        self.model = ptm_dim["model"]
        self.human_mesh = ptm_dim["human_mesh"]
        self.patient_offset = PatientOffset(offset=ptm_dim["patient_offset"])
        self.patient_orientation = ptm_dim["patient_orientation"]
        self.dimension = PhantomDimensions(ptm_dim=ptm_dim['dimension'])


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
    units : float
        Units of the all attributes in this class. Only "cm" are currently
        implemented.

    Raises
    ------
    NotImplementedError
        Raises error if other units then cm are used.

    """

    def __init__(self, ptm_dim: dict):
        """Initialize phantom dimension class.

        Parameters
        ----------
        ptm_dim : dict
            Dictionary containing all of the phantom dimensions that are
            appended as attributes to this class, see class attributes.

        Raises
        ------
        NotImplementedError
            Raises error if other units then cm are used.

        """
        self.plane_length = ptm_dim['plane_length']
        self.plane_width = ptm_dim['plane_width']
        self.plane_resolution = ptm_dim['plane_resolution']
        self.cylinder_length = ptm_dim['cylinder_length']
        self.cylinder_radii_a = ptm_dim['cylinder_radii_a']
        self.cylinder_radii_b = ptm_dim['cylinder_radii_b']
        self.cylinder_resolution = ptm_dim['cylinder_resolution']
        self.table_thickness = ptm_dim['table_thickness']
        self.table_length = ptm_dim['table_length']
        self.table_width = ptm_dim['table_width']
        self.pad_thickness = ptm_dim['pad_thickness']
        self.pad_width = ptm_dim['pad_width']
        self.pad_length = ptm_dim['pad_length']
        self.unit = ptm_dim['unit']

        if self.unit != "cm":
            raise NotImplementedError('Units must be given in cm.')


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

        Raises
        ------
        NotImplementedError
            Raises error if other units then cm are used.

        """
        self.d_lat = offset["d_lat"]
        self.d_ver = offset["d_ver"]
        self.d_lon = offset["d_lon"]
        self.units = offset["unit"]

        if self.units != "cm":
            raise NotImplementedError('Units must be given in cm.')


class Plotsettings:
    """A class for setting plot settings.

    Attributes
    ----------
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

