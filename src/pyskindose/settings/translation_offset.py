from typing import Dict, Optional


class TranslationOffset:
    """Set translation offset of patient support table.

    Use this class to set the translation offset (in cm) between the machine
    origin (the unit that generated the RDSR) and the machine origin of
    PySkinDose (which is located at (x,y,z) = (0, 0, 0)).

    Attributes
    ----------
    keys of __init__ parameter offset
        Value of each attribute (i.e. key) is a float specifying the offset
        in cm.

    """

    def __init__(self, offset: Optional[Dict[str, float]] = None):
        """Initialize class attributes.

        Parameters
        ----------
        offset : dict
            dictionary with keys 'x', 'y' and 'z'. Each key contains the
            translation offset (in that direction), specified as a float in cm.

        """
        if offset is None:
            offset = dict()

        self.x: float = offset.get("x")
        self.y: float = offset.get("y")
        self.z: float = offset.get("z")

    def update_translation_offset(self, offset: Dict[str, float]):
        self.x = float(offset["x"]) if self.x is None else self.x
        self.y = float(offset["y"]) if self.y is None else self.y
        self.z = float(offset["z"]) if self.z is None else self.z
