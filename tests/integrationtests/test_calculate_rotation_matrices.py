from pyskindose.helpers.calculate_rotation_matrices import calculate_rotation_matrices


def test_calculate_rotation_matrices_returns_the_same_dataframe_with_new_columns_for_rotation_matrices(
    axiom_artis_normalized,
):
    # Arrange
    expected = list(axiom_artis_normalized.columns) + ["Rx", "Ry", "Rz"]

    # Act
    result = calculate_rotation_matrices(axiom_artis_normalized)
    actual = list(result.columns)

    # Assert
    assert actual == expected


def test_calculate_rotation_matrices_returns_correctly_calculates_the_rotation_matrices(axiom_artis_normalized):
    # Arrange
    expected_Rx = [[1, 0, 0], [0, 1.0, -0.0], [0, 0.0, 1.0]]
    expected_Ry = [
        [1.0, 0, 0.0],
        [0, 1.0, 0],
        [-0.0, 0, 1.0],
    ]
    expected_Rz = [[1.0, -0.0, 0], [0.0, 1.0, 0], [0, 0, 1]]

    # Act
    result = calculate_rotation_matrices(axiom_artis_normalized)

    # Assert
    assert result.Rx[0] == expected_Rx
    assert result.Ry[0] == expected_Ry
    assert result.Rz[0] == expected_Rz
