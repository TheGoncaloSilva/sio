import pytest
import sys
from unittest.mock import Mock
from unittest.mock import MagicMock

from common.communication import *
from common.state import State

def test_init():
    # Test valid input
    s = State(['A', 'B', 'C'], {'A': ['B'], 'B': ['C'], 'C': ['A']}, 'A')

    # Test invalid initial state
    with pytest.raises(ValueError):
        s = State(['A', 'B', 'C'], {'A': ['B'], 'B': ['C'], 'C': ['A']}, 'D')


def test_get_state():
    s = State(['A', 'B', 'C'], {'A': ['B'], 'B': ['C'], 'C': ['A']}, 'B')
    assert s.getState() == 'B'

def test_apply():
    s = State(['A', 'B', 'C'], {'A': ['B'], 'B': ['C'], 'C': ['A']}, 'A')

    # Test valid transition
    s.apply('B')
    assert s.getState() == 'B'

    # Test invalid transition
    with pytest.raises(ValueError):
        s.apply('A')

    # Test invalid state
    with pytest.raises(ValueError):
        s.apply('D')

def test_apply_multiple():
    s = State(['A', 'B', 'C'], {'A': ['B'], 'B': ['C'], 'C': ['A']}, 'A')
    s.apply('B')
    s.apply('C')
    assert s.getState() == 'C'