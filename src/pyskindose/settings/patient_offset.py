from pyskindose.constants import (
    OFFSET_LATERAL_KEY,
    OFFSET_LONGITUDINAL_KEY,
    OFFSET_VERTICAL_KEY,
)
from pyskindose.helpers.create_attributes_string import create_attributes_string


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

        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="patient offset", indent_level=1)

    def update_attrs_str(self):
        self.attrs_str = create_attributes_string(attrs_parent=self, object_name="patient offset", indent_level=1)
