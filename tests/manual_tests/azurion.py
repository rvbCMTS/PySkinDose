from base_dev_settings import DEVELOPMENT_PARAMETERS

from pyskindose import constants
from pyskindose.main import main
from pyskindose.settings import PyskindoseSettings

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)
settings.mode = constants.MODE_PLOT_PROCEDURE
settings.plot.interactivity = True
settings.plot.plot_dosemap = False

settings.estimate_k_tab = True
settings.rdsr_filename = 'clinical/AzurionNormalisation2022.dcm'
main(settings=settings)
