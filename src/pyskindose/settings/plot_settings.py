from pyskindose.helpers.create_attributes_string import create_attributes_string


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
        self.interactivity = plt_dict.get("interactivity", True)
        self.dark_mode = plt_dict.get("dark_mode", True)
        self.notebook_mode = plt_dict.get("notebook_mode", False)
        self.plot_dosemap = plt_dict.get("plot_dosemap", True)
        self.max_events_for_patient_inclusion = plt_dict.get("max_events_for_patient_inclusion", 10)
        self.plot_event_index = plt_dict.get("plot_event_index", 0)

        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="plot", indent_level=0)

    def update_attrs_str(self):
        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="plot", indent_level=0)

    def to_printable_string(self, color: str = "blue"):
        return (
            f"[bold {color}]Plot settings[/bold {color}]\n"
            f"\t[{color}]interactivity: {'True' if self.interactivity else 'False'}[/{color}]\n"
            f"\t[{color}]dark_mode: {'True' if self.dark_mode else 'False'}[/{color}]\n"
            f"\t[{color}]notebook_mode: {'True' if self.notebook_mode else 'False'}[/{color}]\n"
            f"\t[{color}]plot_dosemap: {'True' if self.plot_dosemap else 'False'}[/{color}]\n"
            f"\t[{color}]max_events_for_patient_inclusion: {self.max_events_for_patient_inclusion}[/{color}]\n"
            f"\t[{color}]plot_event_index: {self.plot_event_index}[/{color}]\n"
        )
