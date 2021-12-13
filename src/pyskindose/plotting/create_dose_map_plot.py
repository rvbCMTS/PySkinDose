import logging

import numpy as np
import plotly.graph_objects as go
from PIL import Image

from pyskindose.phantom_class import Phantom
from pyskindose.plotting.create_layout_for_dose_map_plots import (
    create_layout_for_dose_map_plots,
)
from pyskindose.plotting.create_notebook_dose_map_plot import (
    create_notebook_dose_map_plot,
)
from pyskindose.settings_pyskindose import PyskindoseSettings

from ..constants import (
    DOSEMAP_COLORSCALE,
    PHANTOM_MODEL_PLANE,
    PLOT_EYE_BACK,
    PLOT_EYE_FRONT,
    PLOT_EYE_LEFT,
    PLOT_EYE_RIGHT,
    PLOT_FILE_TYPE_STATIC,
    PLOT_FONT_FAMILY,
    PLOT_ORDER_STATIC,
)
from .plot_settings import fetch_plot_colors, fetch_plot_margin, fetch_plot_size

logger = logging.getLogger(__name__)


def create_dose_map_plot(patient: Phantom, settings: PyskindoseSettings, dose_map: np.ndarray) -> None:
    """Plot a map of the absorbed skindose upon the patient phantom.

    This function creates and plots an offline plotly graph of the skin dose
    distribution on the phantom. The colorscale is mapped to the absorbed skin dose
    value. Only available for phantom type: "plane", "cylinder" or "human."

    Parameters
    ----------
    patient : Phantom
        patient phantom
    settings : PyskindoseSettings
        Settings class for PySkinDose
    dose_map : np.ndarray
        array with dose matrix, where each element is to be mapped to the corresponding
        skin cell of the patient.

    """
    if not settings.plot.plot_dosemap:
        logger.debug("Mode not set to plot dosemap. Returning without doing anything")
        return

    if dose_map is None:
        logger.debug(
            """Cannot plot dosemap since dose calculation has not been conducted.
            Returning without doing anything."""
        )
        raise ValueError(
            """Dosemap is None. Mode must be set to calculate dose in order to plot
            dosemap"""
        )

    # Fix error with plotly layout for 2D plane patient.
    if patient.phantom_model == PHANTOM_MODEL_PLANE:
        patient = Phantom(phantom_model=settings.phantom.model, phantom_dim=settings.phantom.dimension)

    # append dosemap to patient
    patient.dose = dose_map

    COLOR_CANVAS, COLOR_PLOT_TEXT, COLOR_GRID, COLOR_ZERO_LINE = fetch_plot_colors(dark_mode=settings.plot.dark_mode)

    PLOT_HEIGHT, PLOT_WIDTH = fetch_plot_size(notebook_mode=settings.plot.notebook_mode)

    PLOT_MARGINS = fetch_plot_margin(notebook_mode=settings.plot.notebook_mode)

    lat_text = [(f"<b>lat:</b> {np.around(patient.r[ind, 2],2)} cm<br>") for ind in range(len(patient.r))]

    lon_text = [f"<b>lon:</b> {np.around(patient.r[ind, 0],2)} cm<br>" for ind in range(len(patient.r))]

    ver_text = [f"<b>ver:</b> {np.around(patient.r[ind, 1],2)} cm<br>" for ind in range(len(patient.r))]

    dose_text = [f"<b>skin dose:</b> {round(patient.dose[ind],2)} mGy" for ind in range(len(patient.r))]

    hover_text = [lat_text[cell] + lon_text[cell] + ver_text[cell] + dose_text[cell] for cell in range(len(patient.r))]

    # create mesh object for the phantom
    phantom_mesh = [
        go.Mesh3d(
            x=patient.r[:, 0],
            y=patient.r[:, 1],
            z=patient.r[:, 2],
            i=patient.ijk[:, 0],
            j=patient.ijk[:, 1],
            k=patient.ijk[:, 2],
            intensity=patient.dose,
            colorscale=DOSEMAP_COLORSCALE,
            showscale=True,
            hoverinfo="text",
            text=hover_text,
            name="Human",
            colorbar=dict(
                tickfont=dict(color=COLOR_PLOT_TEXT),
                title="Skin dose [mGy]",
                titlefont=dict(family=PLOT_FONT_FAMILY, color=COLOR_PLOT_TEXT),
            ),
        )
    ]

    layout = create_layout_for_dose_map_plots(
        PLOT_MARGINS=PLOT_MARGINS,
        PLOT_HEIGHT=PLOT_HEIGHT,
        PLOT_WIDTH=PLOT_WIDTH,
        COLOR_PLOT_TEXT=COLOR_PLOT_TEXT,
        COLOR_CANVAS=COLOR_CANVAS,
    )

    # create figure
    fig = go.Figure(data=phantom_mesh, layout=layout)

    if settings.plot.interactivity:
        fig.show()
        return

    # proceed with creating static dose map

    eyes = [PLOT_EYE_RIGHT, PLOT_EYE_BACK, PLOT_EYE_LEFT, PLOT_EYE_FRONT]

    names = PLOT_ORDER_STATIC
    file_type_static = PLOT_FILE_TYPE_STATIC

    if settings.plot.notebook_mode:
        from tqdm import tqdm_notebook as pbar

    else:
        from tqdm import tqdm as pbar

    # create static dose map plots
    for i in pbar(range(len(eyes)), desc=f"saving static dosemaps: "):
        fig["layout"]["scene"]["camera"] = eyes[i]
        fig.write_image(f"{names[i]}.png")

    # show dose map plot with PIL if not in notebook mode
    if not settings.plot.notebook_mode:
        for image_file_name in [name + file_type_static for name in names]:
            im = Image.open(image_file_name)
            im.show()
        return

    # proceed with showing the dose map plot in notebook mode
    create_notebook_dose_map_plot(
        names=names,
        file_type_static=file_type_static,
    )
