from base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose import constants
from pyskindose.main import main

DEVELOPMENT_PARAMETERS['mode'] = constants.MODE_PLOT_EVENT



main(settings=DEVELOPMENT_PARAMETERS)
