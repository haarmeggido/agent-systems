import pytest

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection


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
