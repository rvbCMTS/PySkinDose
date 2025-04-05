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

    return json.loads((Path(__file__).parent / "settings_example.json").read_text())


def print_available_human_phantoms():
    from pathlib import Path

    phantom_data_dir = Path(__file__).parent / "phantom_data"
    phantoms = [
        phantom.stem for phantom in phantom_data_dir.glob("*.stl") if not phantom.stem.endswith("reduced_1000t")
    ]

    for phantom in phantoms:
        print(phantom)


def print_example_rdsr_files():
    rdsr_data_dir = get_path_to_example_rdsr_files()
    files = [file.name for file in rdsr_data_dir.glob("*.dcm")]

    print("Available RDSR files:\n")
    for filename in files:
        print(f"\t{filename}")

    print(f"\nFiles located in {rdsr_data_dir.absolute()}")


def get_path_to_example_rdsr_files():
    from pathlib import Path

    return Path(__file__).parent / "example_data" / "RDSR"
