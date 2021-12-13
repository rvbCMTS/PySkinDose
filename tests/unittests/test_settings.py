import sys
from pathlib import Path

P = Path(__file__).parent.parent
sys.path.insert(1, str(P.absolute()))

from manual_tests.base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose.settings_pyskindose import PyskindoseSettings

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)


def test_print_parameters_with_updated_settings():

    # Expect that the print statement will change if parameters in the settings are
    # changed
    expected = False

    # print parameters
    print_string = settings.print_parameters(return_as_string=True)
    # update something
    settings.mode = "some_other_mode"
    # print parameters again
    print_string_updated = settings.print_parameters(return_as_string=True)

    # test if the printing has been updated
    test = print_string == print_string_updated

    assert expected == test
