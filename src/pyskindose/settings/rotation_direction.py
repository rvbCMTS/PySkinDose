from typing import Dict, Optional


class RotationDirection:
    """Switch pos/neg direction of beam- and table angles.

    Attributes
    ----------
    keys of __init__ parameter directions
        Value of each attribute (i.e. key) is integers of either +1 or -1 to be
        used as a multiplicative correction factor to switch pos/neg direction
        in each angle. PySkinDose default angles are all +1.

    """

    def __init__(self, directions: Optional[Dict[str, str]] = None):
        """Initialize class attributes.

        Parameters
        ----------
        directions : dict
            dictionary with keys 'Ap1', 'Ap2', 'Ap3', 'At1', 'At2' and 'At3'.
            Each key contains either '+' or '-'.

        """
        self.Ap1: Optional[int] = None if directions is None else self._get_direction_as_value(directions["Ap1"])
        self.Ap2: Optional[int] = None if directions is None else self._get_direction_as_value(directions["Ap2"])
        self.Ap3: Optional[int] = None if directions is None else self._get_direction_as_value(directions["Ap3"])
        self.At1: Optional[int] = None if directions is None else self._get_direction_as_value(directions["At1"])
        self.At2: Optional[int] = None if directions is None else self._get_direction_as_value(directions["At2"])
        self.At3: Optional[int] = None if directions is None else self._get_direction_as_value(directions["At3"])

    def update_rotation_direction(self, directions: Dict[str, str]):
        self.Ap1 = self._get_direction_as_value(directions["Ap1"])
        self.Ap2 = self._get_direction_as_value(directions["Ap2"])
        self.Ap3 = self._get_direction_as_value(directions["Ap3"])
        self.At1 = self._get_direction_as_value(directions["At1"])
        self.At2 = self._get_direction_as_value(directions["At2"])
        self.At3 = self._get_direction_as_value(directions["At3"])

    @staticmethod
    def _get_direction_as_value(direction: str):
        if direction not in ("+", "-"):
            raise ValueError(f"The direction must be given as '+' or '-' but was given as {direction}")

        return 1 if direction == "+" else -1
