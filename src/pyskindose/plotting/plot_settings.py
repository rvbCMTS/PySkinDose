from ..constants import (
    COLOR_CANVAS_DARK,
    COLOR_CANVAS_LIGHT,
    COLOR_GRID_DARK,
    COLOR_GRID_LIGHT,
    COLOR_PLOT_TEXT_DARK,
    COLOR_PLOT_TEXT_LIGHT,
    COLOR_SLIDER_BORDER_DARK,
    COLOR_SLIDER_BORDER_LIGHT,
    COLOR_SLIDER_TICK_DARK,
    COLOR_SLIDER_TICK_LIGHT,
    COLOR_ZERO_LINE_DARK,
    COLOR_ZERO_LINE_LIGHT,
    PLOT_HEIGHT,
    PLOT_HEIGHT_NOTEBOOK,
    PLOT_MARGIN,
    PLOT_MARGIN_NOTEBOOK,
    PLOT_SLIDER_PADDING,
    PLOT_SLIDER_PADDING_NOTEBOOK,
    PLOT_WIDTH,
    PLOT_WIDTH_NOTEBOOK,
)


def fetch_plot_colors(dark_mode: bool):
    """Fetch correct colors scheme for plotly plots.

    Parameters
    ----------
    dark_mode : bool
        Specifies whether dark mode should be implemented

    """
    if dark_mode:
        return (
            COLOR_CANVAS_DARK,
            COLOR_PLOT_TEXT_DARK,
            COLOR_GRID_DARK,
            COLOR_ZERO_LINE_DARK,
        )

    return (
        COLOR_CANVAS_LIGHT,
        COLOR_PLOT_TEXT_LIGHT,
        COLOR_GRID_LIGHT,
        COLOR_ZERO_LINE_LIGHT,
    )


def fetch_slider_colors(dark_mode: bool):
    """Fetch correct colors scheme for plotly sliders.

    Parameters
    ----------
    dark_mode : bool
        Specifies whether dark mode should be implemented

    """
    if dark_mode:
        return (
            COLOR_PLOT_TEXT_DARK,
            COLOR_SLIDER_TICK_DARK,
            COLOR_SLIDER_BORDER_DARK,
        )

    return COLOR_PLOT_TEXT_LIGHT, COLOR_SLIDER_TICK_LIGHT, COLOR_SLIDER_BORDER_LIGHT


def fetch_plot_size(notebook_mode: bool):
    """Fetch correct plot size for plotly plots.

    Parameters
    ----------
    notebook_mode : bool
        specifies whether plot size should be optimized for notebooks

    """
    if notebook_mode:
        return PLOT_HEIGHT_NOTEBOOK, PLOT_WIDTH_NOTEBOOK

    return PLOT_HEIGHT, PLOT_WIDTH


def fetch_plot_margin(notebook_mode: bool):
    """Fetch correct margins for plotly plots.

    Parameters
    ----------
    notebook_mode : bool
        Specifies whether plot margins should be optimized for notebooks

    """
    if notebook_mode:
        return PLOT_MARGIN_NOTEBOOK

    return PLOT_MARGIN


def fetch_slider_padding(notebook_mode: bool):
    """Fetch correct slider margins for plot procedure.

    Parameters
    ----------
    notebook_mode : bool
        Specifies whether the slider padding should be optimized for notebooks

    """
    if notebook_mode:
        return PLOT_SLIDER_PADDING_NOTEBOOK

    return PLOT_SLIDER_PADDING
