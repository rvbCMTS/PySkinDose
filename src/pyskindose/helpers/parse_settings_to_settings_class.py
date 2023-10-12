import logging
from pathlib import Path
from typing import Optional

from pyskindose.settings import PyskindoseSettings, initialize_settings

logger = logging.getLogger(__name__)


def parse_settings_to_settings_class(settings: Optional[str] = None):
    try:
        return initialize_settings(settings)
    except ValueError:
        logger.debug("Tried initializing settings without any settings")

    settings_path = Path(__file__).parent.parent / "settings.json"

    if not settings_path.exists():
        logger.warning("Settings path not specified. Using example settings.")
        settings_path = settings_path.parent / "settings_example.json"

    return PyskindoseSettings(settings_path.read_text())
