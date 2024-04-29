from base_dev_settings import DEVELOPMENT_PARAMETERS

from pyskindose import constants
from pyskindose.main import main
from pyskindose.settings import PyskindoseSettings

settings = PyskindoseSettings(settings=DEVELOPMENT_PARAMETERS)
settings.plot.max_events_for_patient_inclusion = 1000
settings.mode = constants.MODE_PLOT_PROCEDURE

settings.rdsr_filename = "check_table_correction.json"

settings.estimate_k_tab = True
settings.k_tab_val = 0.5

main(settings=settings)


settings.mode = constants.MODE_CALCULATE_DOSE
settings.plot.plot_dosemap = True
main(settings=settings)
