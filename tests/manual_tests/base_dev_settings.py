from pyskindose import constants as const

DEVELOPMENT_PARAMETERS = dict(
    # modes: 'calculate_dose', 'plot_setup', 'plot_event', 'plot_procedure'
    mode=const.MODE_PLOT_PROCEDURE,
    # RDSR filename
    rdsr_filename='s1.dcm',
    # Irrading event index for mode='plot_event'
    plot_event_index=12,
    # Set True to estimate table correction, or False to use measured k_tab
    estimate_k_tab=False,
    # Numeric value of estimated table correction    
    k_tab_val=0.8,
    # plot settings
plot={
        # dark mode for plots
        const.MODE_DARK_MODE: True,
        # notebook mode
        const.MODE_NOTEBOOK_MODE: False,
        # choose if dosemap should be plotted after dose calculations.
        const.MODE_PLOT_DOSEMAP: True,
        # colorscale for dosemaps
        const.DOSEMAP_COLORSCALE_KEY: const.DOSEMAP_COLORSCALE},
    # Phantom settings:
    phantom=dict(
        # Phantom model, valid selections: 'plane', 'cylinder', or 'human'
        model=const.PHANTOM_MODEL_HUMAN,
        # Human phantom .stl filename, without .stl ending.
        human_mesh=const.PHANTOM_MESH_ADULT_MALE,
        # Patient offset from table isocenter (centered at head end side).
        patient_offset={const.OFFSET_LATERAL_KEY: const.OFFSET_LATERAL,
                        const.OFFSET_VERTICAL_KEY: const.OFFSET_VERTICAL,
                        const.OFFSET_LONGITUDINAL_KEY: const.OFFSET_LONGITUDINAL,
                        const.DIMENSION_UNIT_KEY: const.DIMENSION_UNIT_CM},
        # Dimensions of matematical phantoms (except model='human')
        dimension={
            const.DIMENSION_PLANE_LENGTH: 120,  # Length of plane phantom
            const.DIMENSION_PLANE_WIDTH: 40,  # Width of plane phantom
            const.DIMENSION_PLANE_RESOLUTION: const.RESOLUTION_SPARSE,  # Resolution of plane phantom
            const.DIMENSION_CYLINDER_LENGTH: 150,  # Length of cylinder phantom
            const.DIMENSION_CYLINDER_RADII_A: 20,  # First radii of cylinder phantom
            const.DIMENSION_CYLINDER_RADII_B: 10,  # Second radii of cylinder phantom
            const.DIMENSION_CYLINDER_RESOLUTION: const.RESOLUTION_SPARSE,  # Resolution of cylinder.
            const.DIMENSION_TABLE_LENGTH: 260,  # Support table length
            const.DIMENSION_TABLE_WIDTH: 50,  # Support table width
            const.DIMENSION_TABLE_THICKNESS: 5,  # Support table thickness
            const.DIMENSION_PAD_LENGTH: 260,  # Support pad length
            const.DIMENSION_PAD_WIDTH: 50,  # Support pad width
            const.DIMENSION_PAD_THICKNESS: 4,  # Support pad thickness
            const.DIMENSION_UNIT_KEY: const.DIMENSION_UNIT_CM})  # unit of dimension. Only 'cm' is supported.
    ,
)