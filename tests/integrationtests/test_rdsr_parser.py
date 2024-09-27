from pyskindose.rdsr_parser import rdsr_parser


def test_that_all_rdsr_events_are_extracted_during_parsing(phantom_dataset):
    # Arrange
    expected = 24

    # act
    data_parsed = rdsr_parser(data_raw=phantom_dataset)

    actual = len(data_parsed)

    # Assert
    assert actual == expected
