from . import constants as c

DEVELOPMENT_PARAMETERS = dict(
    # modes: 'calculate_dose', 'plot_setup', 'plot_event', 'plot_procedure'
    mode=c.MODE_PLOT_PROCEDURE,
    # RDSR filename
    rdsr_filename="S1.dcm",
    # Set True to estimate table correction, or False to use measured k_tab
    estimate_k_tab=False,
    # Numeric value of estimated table correction
    k_tab_val=0.8,
    # plot settings
    plot={
        # dark mode for plots
        c.MODE_DARK_MODE: True,
        # notebook mode
        c.MODE_NOTEBOOK_MODE: False,
        # choose if dosemap should be plotted after dose calculations.
        c.MODE_PLOT_DOSEMAP: False,
        # colorscale for dosemaps
        c.DOSEMAP_COLORSCALE_KEY: c.DOSEMAP_COLORSCALE,
        # max number of event for inclusion of patient phantom in plot
        # procedure
        c.MAX_EVENT_FOR_PATIENT_INCLUSION_IN_PROCEDURE_KEY: 0,
        # Irrading event index for mode='plot_event'
        c.PLOT_EVENT_INDEX_KEY: 12,
    },
    # Phantom settings:
    phantom=dict(
        # Phantom model, valid selections: 'plane', 'cylinder', or 'human'
        model=c.PHANTOM_MODEL_CYLINDER,
        # Human phantom .stl filename, without .stl ending.
        human_mesh=c.PHANTOM_MESH_ADULT_MALE,
        # Patient offset from table isocenter (centered at head end side).
        patient_offset={c.OFFSET_LONGITUDINAL_KEY: 0, c.OFFSET_VERTICAL_KEY: 0, c.OFFSET_LATERAL_KEY: -35},
        patient_orientation=c.PATIENT_ORIENTATION_HEAD_FIRST_SUPINE,
        dimension={
            # Length of plane phantom
            c.DIMENSION_PLANE_LENGTH: 120,
            # Width of plane phantom
            c.DIMENSION_PLANE_WIDTH: 40,
            # Resolution of plane phantom
            c.DIMENSION_PLANE_RESOLUTION: c.RESOLUTION_SPARSE,
            # Length of cylinder phantom
            c.DIMENSION_CYLINDER_LENGTH: 150,
            # First radii of cylinder phantom
            c.DIMENSION_CYLINDER_RADII_A: 20,
            # Second radii of cylinder phantom
            c.DIMENSION_CYLINDER_RADII_B: 10,
            # Resolution of cylinder.
            c.DIMENSION_CYLINDER_RESOLUTION: c.RESOLUTION_SPARSE,
            # 281.5 Support table length
            c.DIMENSION_TABLE_LENGTH: 281.5,
            # Support table width
            c.DIMENSION_TABLE_WIDTH: 45,
            # Support table thickness
            c.DIMENSION_TABLE_THICKNESS: 5,
            # Support pad length
            c.DIMENSION_PAD_LENGTH: 281.5,
            c.DIMENSION_PAD_WIDTH: 45,  # Support pad width
            c.DIMENSION_PAD_THICKNESS: 4,
        },
    ),  # Support pad thickness
)
