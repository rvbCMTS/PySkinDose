from pyskindose import constants
from pyskindose.main import main
from pyskindose.settings_pyskindose import PyskindoseSettings

from base_dev_settings import DEVELOPMENT_PARAMETERS

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)
settings.mode = constants.MODE_PLOT_EVENT
settings.plot_event_index = 12

main(settings=settings)
