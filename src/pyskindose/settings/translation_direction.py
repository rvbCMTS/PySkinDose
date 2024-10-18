from typing import Dict, Optional


class TranslationDirection:
    """Switch pos/neg direction of table translations.

    Attributes
    ----------
    keys of __init__ parameter directions
        Value of each attribute (i.e. key) is integers of either +1 or -1 to be
        used as a multiplicative correction factor to switch pos/neg direction
        in each direction. PySkinDose default angles are all +1.

    """

    x: Optional[int]
    y: Optional[int]
    z: Optional[int]

    def __init__(self, directions: Optional[Dict[str, str]] = None):
        """Initialize class attributes.

        Parameters
        ----------
        directions : dict
            dictionary with keys 'x', 'y' and 'z'.
            Each key contains either '+' or '-'.

        """
        self.x = None if directions is None else self._get_direction_as_value(directions["x"])
        self.y = None if directions is None else self._get_direction_as_value(directions["y"])
        self.z = None if directions is None else self._get_direction_as_value(directions["z"])

    def update_translation_direction(self, directions: Dict[str, str]):
        self.x = self._get_direction_as_value(directions["x"]) if self.x is None else self.x
        self.y = self._get_direction_as_value(directions["y"]) if self.y is None else self.y
        self.z = self._get_direction_as_value(directions["z"]) if self.z is None else self.z

    @staticmethod
    def _get_direction_as_value(direction: str):
        if direction not in ("+", "-"):
            raise ValueError(f"The direction must be given as '+' or '-' but was given as {direction}")

        return 1 if direction == "+" else -1
