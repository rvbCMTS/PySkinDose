from pyskindose.helpers.create_attributes_string import create_attributes_string


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
        self.plane_length = ptm_dim["plane_length"]
        self.plane_width = ptm_dim["plane_width"]
        self.plane_resolution = ptm_dim["plane_resolution"]
        self.cylinder_length = ptm_dim["cylinder_length"]
        self.cylinder_radii_a = ptm_dim["cylinder_radii_a"]
        self.cylinder_radii_b = ptm_dim["cylinder_radii_b"]
        self.cylinder_resolution = ptm_dim["cylinder_resolution"]
        self.table_thickness = ptm_dim["table_thickness"]
        self.table_length = ptm_dim["table_length"]
        self.table_width = ptm_dim["table_width"]
        self.pad_thickness = ptm_dim["pad_thickness"]
        self.pad_width = ptm_dim["pad_width"]
        self.pad_length = ptm_dim["pad_length"]

        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="dimensions", indent_level=1)

    def update_attrs_str(self):
        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="dimension", indent_level=1)

    def to_dict_pad(self):
        return {
            "plane_length": self.plane_length,
            "plane_width": self.plane_width,
            "plane_resolution": self.plane_resolution,
            "cylinder_radii_a": self.cylinder_radii_a,
            "cylinder_length": self.cylinder_length,
            "cylinder_radii_b": self.cylinder_radii_b,
            "cylinder_resolution": self.cylinder_resolution,
            "table_thickness": self.table_thickness,
            "table_length": self.table_length,
            "table_width": self.table_width,
            "pad_thickness": self.pad_thickness,
            "pad_width": self.pad_width,
            "pad_length": self.pad_length,
        }

    def to_dict_cylinder(self):
        return {
            "cylinder_length": self.cylinder_length,
            "cylinder_radii_a": self.cylinder_radii_a,
            "cylinder_radii_b": self.cylinder_radii_b,
            "cylinder_resolution": self.cylinder_resolution,
        }
