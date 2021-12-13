from pyskindose import constants
from pyskindose.main import main
from pyskindose.settings_pyskindose import PyskindoseSettings

from base_dev_settings import DEVELOPMENT_PARAMETERS

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)
settings.mode = constants.MODE_PLOT_PROCEDURE

settings.rdsr_filename = "beam_collimations.json"

main(settings=settings)
