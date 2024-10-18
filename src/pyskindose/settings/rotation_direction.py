from typing import Dict, Optional, Union


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
        self.Ap1 = (
            self._get_direction_as_value(directions["Ap1"])
            if self.Ap1 is None
            else self._get_direction_as_value(self.Ap1)
        )
        self.Ap2 = (
            self._get_direction_as_value(directions["Ap2"])
            if self.Ap2 is None
            else self._get_direction_as_value(self.Ap2)
        )
        self.Ap3 = (
            self._get_direction_as_value(directions["Ap3"])
            if self.Ap3 is None
            else self._get_direction_as_value(self.Ap3)
        )
        self.At1 = (
            self._get_direction_as_value(directions["At1"])
            if self.At1 is None
            else self._get_direction_as_value(self.At1)
        )
        self.At2 = (
            self._get_direction_as_value(directions["At2"])
            if self.At2 is None
            else self._get_direction_as_value(self.At2)
        )
        self.At3 = (
            self._get_direction_as_value(directions["At3"])
            if self.At3 is None
            else self._get_direction_as_value(self.At3)
        )

    @staticmethod
    def _get_direction_as_value(direction: Union[str, int]):

        if direction in (-1, +1):
            return direction

        if direction in ("+", "-"):
            return 1 if direction == "+" else -1

        raise ValueError(f"The direction must be given as '+', '-', 1, or -1, but was given as {direction}")
