import pytest

from ainter.models.autonomous_intersection.traffic_lights import SimpleTrafficLight
from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection
from ainter.models.nagel_schreckenberg.units import DiscreteTime


@pytest.fixture
def traffic_light():
    return SimpleTrafficLight(global_time_ref=0, green_duration=10)

@pytest.fixture
def traffic_light_with_directions(traffic_light):
    traffic_light.add_direction(IntersectionEntranceDirection.NORTH)
    traffic_light.add_direction(IntersectionEntranceDirection.EAST)
    traffic_light.add_direction(IntersectionEntranceDirection.SOUTH)
    traffic_light.add_direction(IntersectionEntranceDirection.WEST)
    return traffic_light

def test_initialization(traffic_light):
    assert traffic_light.time == 0
    assert traffic_light.green_duration == 10
    assert len(traffic_light.directions) == 0

def test_add_direction(traffic_light):
    traffic_light.add_direction(IntersectionEntranceDirection.NORTH)
    assert len(traffic_light.directions) == 1
    assert IntersectionEntranceDirection.NORTH in traffic_light.directions

    traffic_light.add_direction(IntersectionEntranceDirection.EAST)
    assert len(traffic_light.directions) == 2
    assert IntersectionEntranceDirection.EAST in traffic_light.directions

    traffic_light.add_direction(IntersectionEntranceDirection.WEST)
    assert len(traffic_light.directions) == 3
    assert IntersectionEntranceDirection.WEST in traffic_light.directions

    traffic_light.add_direction(IntersectionEntranceDirection.SOUTH)
    assert len(traffic_light.directions) == 4
    assert IntersectionEntranceDirection.SOUTH in traffic_light.directions

@pytest.mark.parametrize("direction", [
    IntersectionEntranceDirection.NORTH,
    IntersectionEntranceDirection.EAST,
    IntersectionEntranceDirection.SOUTH,
    IntersectionEntranceDirection.WEST,
])
def test_add_duplicate_direction(traffic_light, direction):
    traffic_light.add_direction(direction)
    with pytest.raises(AssertionError, match="Cannot add an direction twice"):
        traffic_light.add_direction(direction)

@pytest.mark.parametrize("direction", [
    IntersectionEntranceDirection.NORTH,
    IntersectionEntranceDirection.EAST,
    IntersectionEntranceDirection.SOUTH,
    IntersectionEntranceDirection.WEST,
])
def test_has_right_of_way_unknown_direction(traffic_light, direction):
    with pytest.raises(AssertionError, match="Cannot ask for unknow direction"):
        traffic_light.has_right_of_way(direction)

def test_has_right_of_way_cycle(traffic_light_with_directions):
    light = traffic_light_with_directions

    for _ in range(10):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is True
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.SOUTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.WEST) is False
        light.step()

    for _ in range(10):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is True
        assert light.has_right_of_way(IntersectionEntranceDirection.SOUTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.WEST) is False
        light.step()

    for _ in range(10):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.SOUTH) is True
        assert light.has_right_of_way(IntersectionEntranceDirection.WEST) is False
        light.step()

    for _ in range(10):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.SOUTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.WEST) is True
        light.step()

    assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is True
    assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is False
    assert light.has_right_of_way(IntersectionEntranceDirection.SOUTH) is False
    assert light.has_right_of_way(IntersectionEntranceDirection.WEST) is False

def test_step_increments_time(traffic_light):
    initial_time = traffic_light.time
    traffic_light.step()
    assert traffic_light.time == initial_time + 1

    for _ in range(5):
        traffic_light.step()
    assert traffic_light.time == initial_time + 6

def test_traffic_light_with_custom_time_ref():
    light = SimpleTrafficLight(global_time_ref=5, green_duration=10)
    light.add_direction(IntersectionEntranceDirection.NORTH)
    light.add_direction(IntersectionEntranceDirection.EAST)

    for _ in range(5):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is True
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is False
        light.step()

    for _ in range(5):
        assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is False
        assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is True
        light.step()

    assert light.has_right_of_way(IntersectionEntranceDirection.NORTH) is False
    assert light.has_right_of_way(IntersectionEntranceDirection.EAST) is True
