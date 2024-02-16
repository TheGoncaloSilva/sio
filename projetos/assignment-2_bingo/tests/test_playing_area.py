import pytest
import sys

from playing_area.playing_area import truncate_dict

def test_invalid_arguments():
    with pytest.raises(ValueError):
        truncate_dict({} , -10)

def test_valid_arguments():
    d = {'key1': 12345, 'key2': 67890, 'key3': 111111}
    truncated_d = truncate_dict(d, max_length=5)
    assert truncated_d == {'key1': 12345, 'key2': 67890, 'key3': '11...'}