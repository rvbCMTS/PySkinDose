import sys
from pathlib import Path

import numpy as np

from pyskindose.geom_calc import Triangle, convert_from_m_to_cm, convert_from_mm_to_cm

P = Path(__file__).parent.parent.parent
sys.path.insert(1, str(P.absolute()))


def test_triangle_check_intersection():
    """Test of intersection algoritm.

    Test if the intersection algoritm returns the expected output for different
    cell segment combinations.
    """
    expected = [True, True, True, True, False, False, [True, False]]

    test = [0] * len(expected)

    center = np.array([0, 0, 0])
    vertex_1 = np.array([1, 0, 0])
    vertex_2 = np.array([0, 0, 1])

    triangle = Triangle(center, vertex_1, vertex_2)

    # straight through central vertex. (Expected = True)
    beam = np.array([+0.0, +1.0, +0.0])
    cell = np.array([+0.0, -1.0, +0.0])
    test[0] = triangle.check_intersection(beam, cell)

    # straight through first vertex. (Expected = True)
    beam = np.array([+1.0, +1.0, +0.0])
    cell = np.array([+1.0, -1.0, +0.0])
    test[1] = triangle.check_intersection(beam, cell)

    # straight through second vertex (Expected = True)
    beam = np.array([+0.0, +1.0, +1.0])
    cell = np.array([+0.0, -1.0, +1.0])
    test[2] = triangle.check_intersection(beam, cell)

    # straight through triangle (Expected = True)
    beam = np.array([+0.2, +1.0, +0.2])
    cell = np.array([+0.2, -1.0, +0.2])
    test[3] = triangle.check_intersection(beam, cell)

    # outside p1 (Expected = False)
    beam = np.array([+0.5, +1.0, -0.1])
    cell = np.array([+0.5, -1.0, -0.1])
    test[4] = triangle.check_intersection(beam, cell)

    # outside p2 (Expected = False)
    beam = np.array([-0.1, +1.0, +0.5])
    cell = np.array([-0.1, -1.0, +0.5])
    test[5] = triangle.check_intersection(beam, cell)

    # through triangle and outside of hypotenuse (Expected = [True, False])
    beam = np.array([+0.3, +1.0, +0.3])
    cell = np.array([[+0.3, -1.0, +0.3], [+0.9, -1.0, +0.9]])
    test[6] = triangle.check_intersection(beam, cell)

    assert expected == test


def test_convert_measurements_from_mm_to_cm():
    """Test that the mm to cm convertion scales correctly."""
    measurement_in_mm = 1000
    same_measurement_in_cm = 100

    expected = same_measurement_in_cm
    test = convert_from_mm_to_cm(measurement_in_mm)

    assert expected == test


def test_convert_measurements_from_m_to_cm():
    """Test that the m to cm convertion scales correctly."""
    measurement_in_m = 2
    same_measurement_in_cm = 200

    expected = same_measurement_in_cm
    test = convert_from_m_to_cm(measurement_in_m)

    assert expected == test
