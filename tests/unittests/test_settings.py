import sys
from pathlib import Path

P = Path(__file__).parent.parent
sys.path.insert(1, str(P.absolute()))

from manual_tests.base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose.settings import PyskindoseSettings

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)


def test_that_print_parameters_function_updates_output_after_settings_change():

    print_string = settings.print_parameters(return_as_string=True)

    settings.mode = "some_other_mode"

    print_string_updated = settings.print_parameters(return_as_string=True)

    assert print_string != print_string_updated


def test_that_file_output_directory_is_set_to_a_subdirectory_to_cwd_if_not_specified():
    expected = Path.cwd() / "PlotOutputs"

    assert settings.file_result_output_path.absolute() == expected.absolute()


def test_that_file_output_directory_is_set_to_specified_directory():
    expected = Path(__file__).parent.parent

    actual = PyskindoseSettings(
        settings=DEVELOPMENT_PARAMETERS, file_result_output_path=expected
    ).file_result_output_path

    assert actual == expected
