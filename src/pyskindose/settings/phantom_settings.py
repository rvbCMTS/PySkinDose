from pyskindose.constants import KEY_PARAM_PHANTOM_MODEL, KEY_PARAM_HUMAN_MESH
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
