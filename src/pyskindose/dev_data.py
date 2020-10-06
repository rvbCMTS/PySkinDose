from . import constants as const

DEVELOPMENT_PARAMETERS = dict(
    # modes: 'calculate_dose', 'plot_setup', 'plot_event', 'plot_procedure'
    mode=const.MODE_PLOT_SETUP,
    # RDSR filename
    rdsr_filename='S1.dcm',
    # Irrading event index for mode='plot_event'
    plot_event_index=12,
    # Set True to estimate table correction, or False to use measured k_tab
    # from /table_data/table_transmission.csv
    estimate_k_tab=False,
    # Numeric value of estimated table correction
    k_tab_val=0.8,
    # Phantom settings:
    phantom=dict(
        # Phantom model, valid selections: 'plane', 'cylinder', or 'human'
        model=const.PHANTOM_MODEL_HUMAN,
        # Human phantom .stl filename, without .stl ending.
        human_mesh=const.PHANTOM_MESH_ADULT_MALE,
        # Patient offset from table isocenter (centered at head end side).
        patient_offset={'d_lat': 0,
                        'd_ver': 0,
                        'd_lon': -35,
                        'units': 'cm'},
        # Dimensions of matematical phantoms (except model='human')
        dimension={
            const.DIMENSION_PLANE_LENGTH: 120,  # Length of plane phantom
            const.DIMENSION_PLANE_WIDTH: 40,  # Width of plane phantom
            const.DIMENSION_PLANE_RESOLUTION: const.RESOLUTION_SPARSE,  # Resolution of plane phantom
            'cylinder_length': 150,  # Length of cylinder phantom
            'cylinder_radii_a': 20,  # First radii of cylinder phantom
            'cylinder_radii_b': 10,  # Second radii of cylinder phantom
            'cylinder_resolution': 'sparse',  # Resolution of cylinder.
            'table_thickness': 5,  # Support table thickness
            'table_length': 210,  # Support table length
            'table_width': 50,  # Support table width
            'pad_thickness': 4,  # Support pad thickness
            'pad_length': 210,  # Support pad length
            'pad_width': 50,  # Support pad width
            'units': 'cm'}))  # unit of dimension. Only 'cm' is supported.