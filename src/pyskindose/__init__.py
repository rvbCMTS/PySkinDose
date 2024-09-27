from .beam_class import Beam
from .geom_calc import position_patient_phantom_on_table, scale_field_area, fetch_and_append_hvl, check_new_geometry
from .rdsr_parser import rdsr_parser
from .rdsr_normalizer import rdsr_normalizer
from .phantom_class import Phantom
from pyskindose.plotting import plot_geometry
from .analyze_data import analyze_data
from .settings import PyskindoseSettings


def load_settings_example_json() -> dict:
    import json
    from pathlib import Path

    return json.loads((Path(__file__).parent / 'settings_example.json').read_text())
 

def print_available_human_phantoms():
    from pathlib import Path
    phantom_data_dir = Path(__file__).parent / 'phantom_data'
    phantoms = [phantom.stem for phantom in phantom_data_dir.glob('*.stl') if not phantom.stem.endswith('reduced_1000t')]

    for phantom in phantoms:
        print(phantom)

