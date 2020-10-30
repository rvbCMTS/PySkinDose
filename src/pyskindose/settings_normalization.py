class _NormalizationSettings:

    def __init__(self, normalization_settings, data_parsed):

        manufacturer = data_parsed['Manufacturer'][0]
        model = data_parsed['ManufacturerModelName'][0]

        # Select correct normalization settings
        for setting in normalization_settings['normalization_settings']:
            if not (manufacturer == setting['manufacturer'] and model in setting['models']):
                continue

            self.trans_offset = _TranslationOffset(offset=setting['translation_offset'])

            self.trans_dir = _TranslationDirection(
                directions=setting['translation_direction'])

            self.rot_dir = _RotationDirection(
                directions=setting['rotation_direction'])

            self.field_size_mode = setting['field_size_mode']
            self.detector_side_length = setting['detector_side_length']
            return

        raise NotImplementedError


class _RotationDirection:
    def __init__(self, directions):

        pos_dir = +1
        neg_dir = -1

        for dimension in directions:

            if directions[dimension] == '+':
                setattr(self, dimension, pos_dir)

            elif directions[dimension] == '-':
                setattr(self, dimension, neg_dir)

            else:
                assert False

        return


class _TranslationDirection:
    def __init__(self, directions):

        pos_dir = +1
        neg_dir = -1

        for dimension in directions:

            if directions[dimension] == '+':
                setattr(self, dimension, pos_dir)

            elif directions[dimension] == '-':
                setattr(self, dimension, neg_dir)
            
            else:
                assert False

        return 


class _TranslationOffset:
    def __init__(self, offset):
        for dimension in offset:
            setattr(self, dimension, offset[dimension])

        return
