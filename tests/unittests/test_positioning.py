from pathlib import Path
import sys
import os
from pyskindose.phantom_class import Phantom
import pyskindose.constants as c

test_path = Path(__file__).parent.parent
sys.path.insert(1, str(test_path.absolute()))

phantom_path = Path(__file__).parent.parent.parent / \
    'src' / 'pyskindose' / 'phantom_data'

from pyskindose.settings_pyskindose import PyskindoseSettings
from manual_tests.base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose.geom_calc import position_patient_phantom_on_table

param = PyskindoseSettings(DEVELOPMENT_PARAMETERS)


def test_mathematical_phantom_positioning_in_z_direction():
    # the patient phantom origin is located at the top of its head. Therefore,
    # all points on the phantom should have negative z value when loaded.

    # expect 0 skin cell have positiv z-directions, for all mathematical
    # phantoms
    expected = [0, 0]

    test = []

    for phantom_model in [c.PHANTOM_MODEL_PLANE, c.PHANTOM_MODEL_CYLINDER]:

        patient_phantom = Phantom(
            phantom_model=phantom_model,
            phantom_dim=param.phantom.dimension,
            human_mesh=c.PHANTOM_MESH_ADULT_MALE)

        test.append(sum(patient_phantom.r[:, 2] > 0))

    assert expected == test


def test_stl_phantom_positioning_in_z_direction():
    # the patient phantom origin is located at the top its head. Therefore,
    # all points on the phantom should have negative z value when loaded.
    nr_phantoms = 0

    # calculate numer of stl phantoms
    for phantom in os.listdir(phantom_path):
        if '.stl' in phantom:
            nr_phantoms += 1

    # expect that none of the phantoms have any skin cell in +z dir
    expected = nr_phantoms * [0]
    test = []

    # for each ...
    for phantom in os.listdir(phantom_path):
        # ... stl phantom
        if '.stl' in phantom:
            # fetch phantom name
            phantom_name = phantom.replace('.stl', '')

            # create human phantom, with each mesh
            test_phantom = Phantom(
                phantom_model=c.PHANTOM_MODEL_HUMAN,
                phantom_dim=param.phantom.dimension,
                human_mesh=phantom_name)
            # calculate number of skin cells in +z dir
            test.append(sum(test_phantom.r[:, 2] > 0))

    assert expected == test
