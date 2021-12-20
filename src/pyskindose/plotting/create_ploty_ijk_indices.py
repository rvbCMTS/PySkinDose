def _create_plotly_ijk_indices_for_cuboid_objects():

    # create list for storing indices order
    i_tab = []
    j_tab = []
    k_tab = []

    # append triangles to fill cuboid top side
    i_tab.append(0)
    j_tab.append(1)
    k_tab.append(2)

    i_tab.append(2)
    j_tab.append(3)
    k_tab.append(0)

    # append triangles to fill cuboid bottom side
    i_tab.append(0 + 4)
    j_tab.append(1 + 4)
    k_tab.append(2 + 4)

    i_tab.append(2 + 4)
    j_tab.append(3 + 4)
    k_tab.append(0 + 4)

    # append triangles to fill cuboid right side
    i_tab.append(0)
    j_tab.append(1)
    k_tab.append(4)

    i_tab.append(1)
    j_tab.append(5)
    k_tab.append(4)

    # append triangles to fill cuboid left side
    i_tab.append(2)
    j_tab.append(3)
    k_tab.append(6)

    i_tab.append(3)
    j_tab.append(7)
    k_tab.append(6)

    # append triangles to fill cuboid head side
    i_tab.append(0)
    j_tab.append(3)
    k_tab.append(4)

    i_tab.append(3)
    j_tab.append(7)
    k_tab.append(4)

    # append triangles to fill cuboid feet side
    i_tab.append(1)
    j_tab.append(2)
    k_tab.append(5)

    i_tab.append(2)
    j_tab.append(6)
    k_tab.append(5)

    return i_tab, j_tab, k_tab
