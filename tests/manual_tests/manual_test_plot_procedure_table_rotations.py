from base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose import constants
from pyskindose.main import main
from pyskindose.settings_pyskindose import PyskindoseSettings

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)
settings.mode = constants.MODE_PLOT_PROCEDURE

settings.rdsr_filename = 'table_rotations.json'

main(settings=settings)
