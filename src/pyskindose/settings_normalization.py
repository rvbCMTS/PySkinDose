from pyskindose.constants import (
    KEY_NORMALIZATION_DETECTOR_SIDE_LENGTH,
    KEY_NORMALIZATION_FIELD_SIZE_MODE,
    KEY_NORMALIZATION_MANUFACTURER,
    KEY_NORMALIZATION_MODELS,
    KEY_RDSR_MANUFACTURER,
    KEY_RDSR_MANUFACTURER_MODEL_NAME,
)


class NormalizationSettings:
    """A class to normalize RDSR for PySkinDose compliance.

    Attributes
    ----------
    trans_offset : _TranslationOffset
        See class variables of _TranslationOffset
    trans_dir : _TranslationDirection
        See class variables of _TranslationDirection
    rot_dir : _RotationDirection
        See class variables of _RotationDirection
    field_size_mode : str
        method for calculating field size at image receptor plane.
        Choose either "CFA" (collimated field area) or "ACD" (actual shutter
        distance). For more info, see calculate_field_size in geom_calc.py.
    detector_side_length : str
        side length of active image receptor area in cm.

    """

    def __init__(self, normalization_settings, data_parsed):
        """Initialize class attributes."""
        manufacturer = data_parsed[KEY_RDSR_MANUFACTURER][0]
        model = data_parsed[KEY_RDSR_MANUFACTURER_MODEL_NAME][0]

        # Select correct normalization settings
        for setting in normalization_settings["normalization_settings"]:

            if not (
                manufacturer.lower() == setting[KEY_NORMALIZATION_MANUFACTURER.lower()].lower()
                and model in setting[KEY_NORMALIZATION_MODELS]
            ):
                continue

            self.trans_offset = _TranslationOffset(offset=setting["translation_offset"])

            self.trans_dir = _TranslationDirection(directions=setting["translation_direction"])

            self.rot_dir = _RotationDirection(directions=setting["rotation_direction"])

            self.field_size_mode = setting[KEY_NORMALIZATION_FIELD_SIZE_MODE]
            self.detector_side_length = setting[KEY_NORMALIZATION_DETECTOR_SIDE_LENGTH]
            return

        raise NotImplementedError


class _RotationDirection:
    """Switch pos/neg direction of beam- and table angles.

    Attributes
    ----------
    keys of __init__ parameter directions
        Value of each attribute (i.e. key) is integers of either +1 or -1 to be
        used as a multiplicative correction factor to switch pos/neg direction
        in each angle. PySkinDose default angles are all +1.

    """

    def __init__(self, directions):
        """Initialize class attributes.

        Parameters
        ----------
        directions : dict
            dictionary with keys 'Ap1', 'Ap2', 'Ap3', 'At1', 'At2' and 'At3'.
            Each key contains either '+' or '-'.

        """
        pos_dir = +1
        neg_dir = -1

        for dimension in directions:

            if directions[dimension] == "+":
                setattr(self, dimension, pos_dir)
                continue

            elif directions[dimension] == "-":
                setattr(self, dimension, neg_dir)

            else:
                raise ValueError(f"direction {directions[dimension]} not understood. choose" "either  + or -")

        return


class _TranslationDirection:
    """Switch pos/neg direction of table translations.

    Attributes
    ----------
    keys of __init__ parameter directions
        Value of each attribute (i.e. key) is integers of either +1 or -1 to be
        used as a multiplicative correction factor to switch pos/neg direction
        in each direction. PySkinDose default angles are all +1.

    """

    def __init__(self, directions):
        """Initialize class attributes.

        Parameters
        ----------
        directions : dict
            dictionary with keys 'x', 'y' and 'z'.
            Each key contains either '+' or '-'.

        """
        pos_dir = +1
        neg_dir = -1

        for dimension in directions:

            if directions[dimension] == "+":
                setattr(self, dimension, pos_dir)
                continue

            elif directions[dimension] == "-":
                setattr(self, dimension, neg_dir)

            else:
                raise ValueError(f"direction {directions[dimension]} not understood. choose" "either  + or -")

        return


class _TranslationOffset:
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

    def __init__(self, offset):
        """Initialize class attributes.

        Parameters
        ----------
        offset : dict
            dictionary with keys 'x', 'y' and 'z'. Each key contains the
            translation offset (in that direction), specified as a float in cm.

        """
        for dimension in offset:
            setattr(self, dimension, offset[dimension])

        return
