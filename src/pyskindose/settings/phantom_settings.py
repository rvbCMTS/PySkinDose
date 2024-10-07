from pyskindose.constants import KEY_PARAM_HUMAN_MESH, KEY_PARAM_PHANTOM_MODEL
from pyskindose.helpers.create_attributes_string import create_attributes_string
from pyskindose.settings.patient_offset import PatientOffset
from pyskindose.settings.phantom_dimensions import PhantomDimensions


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

        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="phantom", indent_level=0)

    def update_attrs_str(self):
        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="phantom", indent_level=0)

    def to_printable_string(self, color: str = "light_slate_blue"):
        return (
            f"[bold {color}]Phantom settings[/bold {color}]\n"
            f"\t[{color}]model: {self.model}[/{color}]\n"
            f"\t[{color}]patient_offset:[/{color}]\n"
            f"\t\t[{color}]d_lat: {self.patient_offset.d_lat}[/{color}]\n"
            f"\t\t[{color}]d_ver: {self.patient_offset.d_ver}[/{color}]\n"
            f"\t\t[{color}]d_lon: {self.patient_offset.d_lon}[/{color}]\n"
            f"\t[{color}]patient_orientation: {self.patient_orientation}[/{color}]\n"
            f"\t[{color}]dimension:[/{color}]\n"
            f"\t\t[{color}]plane_length: {self.dimension.plane_length}[/{color}]\n"
            f"\t\t[{color}]plane_width: {self.dimension.plane_width}[/{color}]\n"
            f"\t\t[{color}]plane_resolution: {self.dimension.plane_resolution}[/{color}]\n"
            f"\t\t[{color}]cylinder_length: {self.dimension.cylinder_length}[/{color}]\n"
            f"\t\t[{color}]cylinder_radii_a: {self.dimension.cylinder_radii_a}[/{color}]\n"
            f"\t\t[{color}]cylinder_radii_b: {self.dimension.cylinder_radii_b}[/{color}]\n"
            f"\t\t[{color}]cylinder_resolution: {self.dimension.cylinder_resolution}[/{color}]\n"
            f"\t\t[{color}]table_thickness: {self.dimension.table_thickness}[/{color}]\n"
            f"\t\t[{color}]table_length: {self.dimension.table_length}[/{color}]\n"
            f"\t\t[{color}]table_width: {self.dimension.table_width}[/{color}]\n"
            f"\t\t[{color}]pad_thickness: {self.dimension.pad_thickness}[/{color}]\n"
            f"\t\t[{color}]pad_width: {self.dimension.pad_width}[/{color}]\n"
            f"\t\t[{color}]pad_length: {self.dimension.pad_length}[/{color}]\n"
        )
