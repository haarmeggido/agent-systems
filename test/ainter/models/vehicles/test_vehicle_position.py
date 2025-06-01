from typing import Any

import pytest

from ainter.models.vehicles.vehicle import Position, is_intersection_position, is_road_position


@pytest.mark.parametrize("position,expected", [
    (42, True),
    (0, True),
    (-10, True),
    ((1, 2), False),
    ((0, 0), False),
    ((-1, 5), False),
])
def test_is_intersection_position(position: Position, expected: bool):
    result = is_intersection_position(position)
    assert result == expected, f"For position {position} expected {expected}, but got {result}"

@pytest.mark.parametrize("position,expected", [
    ((1, 2), True),
    ((0, 0), True),
    ((-1, 5), True),
    (42, False),
    (0, False),
    (-10, False),
])
def test_is_road_position(position: Position, expected: bool):
    result = is_road_position(position)
    assert result == expected, f"For position {position} expected {expected}, but got {result}"

@pytest.mark.parametrize("invalid_position", [
    "string",
    3.14,
    [1, 2],
    {"u": 1, "v": 2},
    None,
    (0.5,),
    (0.5, 0.5),
    (0.5, 1),
    (1, 0.5),
    ("ABC", 1),
])
def test_position_functions_with_invalid_types(invalid_position: Any):
    assert not is_intersection_position(invalid_position), f"is_intersection_position should return False for {type(invalid_position)}"
    assert not is_road_position(invalid_position), f"is_road_position should return False for {type(invalid_position)}"
