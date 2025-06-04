import pytest

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection
from ainter.models.autonomous_intersection.lane_directions import LaneDirections


@pytest.mark.parametrize("start,expected", [
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.WEST),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.NORTH),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.EAST),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.SOUTH),
])
def test_left(start, expected):
    assert start.get_left_of() == expected, "Directions must be correct"

@pytest.mark.parametrize("start,expected", [
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.EAST),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.SOUTH),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.WEST),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.NORTH),
])
def test_right(start, expected):
    assert start.get_right_of() == expected, "Directions must be correct"

@pytest.mark.parametrize("start,expected", [
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.SOUTH),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.WEST),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.NORTH),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.EAST),
])
def test_straight(start, expected):
    assert start.get_straight() == expected, "Directions must be correct"

@pytest.mark.parametrize("start,end,expected", [
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.WEST, LaneDirections.RIGHT),
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.EAST, LaneDirections.LEFT),
    (IntersectionEntranceDirection.NORTH, IntersectionEntranceDirection.SOUTH, LaneDirections.STRAIGHT),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.NORTH, LaneDirections.STRAIGHT),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.WEST, LaneDirections.LEFT),
    (IntersectionEntranceDirection.SOUTH, IntersectionEntranceDirection.EAST, LaneDirections.RIGHT),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.NORTH, LaneDirections.LEFT),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.SOUTH, LaneDirections.RIGHT),
    (IntersectionEntranceDirection.WEST, IntersectionEntranceDirection.EAST, LaneDirections.STRAIGHT),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.NORTH, LaneDirections.RIGHT),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.SOUTH, LaneDirections.LEFT),
    (IntersectionEntranceDirection.EAST, IntersectionEntranceDirection.WEST, LaneDirections.STRAIGHT),
])
def test_direction_calculation(start, end, expected):
    assert start.get_direction(end) == expected, "The difference should be correct"
