from base_dev_settings import DEVELOPMENT_PARAMETERS
from pyskindose import constants
from pyskindose.main import main

DEVELOPMENT_PARAMETERS['mode'] = constants.MODE_CALCULATE_DOSE
DEVELOPMENT_PARAMETERS['plot']['plot_dosemap'] = constants.MODE_PLOT_DOSEMAP

main(settings=DEVELOPMENT_PARAMETERS)
