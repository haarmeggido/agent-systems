import itertools

import pytest

from ainter.models.nagel_schreckenberg.units import discretize_length
from ainter.models.vehicles.vehicle import Vehicle, VehicleType, is_intersection_position
from test.ainter.models.dummy_model import DummyModel
from test.ainter.test_fixtures import seed


def mock_is_agent_leaving_false(position, agent_id, speed):
    return False

def mock_is_agent_leaving_true(position, agent_id, speed):
    return True

def mock_get_obstacle_distance(self, position, agent_id):
    return discretize_length(5.)

@pytest.fixture(params=[VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
def agent_type(request):
    return request.param

@pytest.fixture(params=[[0, 1], [0, 1, 2], [0, 1, 2, 3], [1, 2, 3]])
def path(request):
    return request.param

def test_vehicle_creation(seed, agent_type, path):
    dummy_model = DummyModel(seed=seed)
    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    assert is_intersection_position(agent.pos), "Agent must be spawned on the intersection"
    assert agent.from_node == path[0], "Agent must start from a first intersection"
    assert agent.from_node == agent.pos, "Agent must have correct position"
    assert agent.from_node != agent.to_node, "Agent cannot start at the finishing node"
    assert agent.to_node == path[-1], "Agent must finish on the end"
    assert agent.finished() == False, "Agent cannot be finishing"

def test_vehicle_iterates_over_path(monkeypatch, seed, agent_type, path):
    dummy_model = DummyModel(seed=seed)
    monkeypatch.setattr(dummy_model, "is_agent_leaving", mock_is_agent_leaving_true)
    monkeypatch.setattr(DummyModel, "get_obstacle_distance", mock_get_obstacle_distance)

    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    nodes = path
    edges = itertools.pairwise(path)

    def interleave(iterable1, iterable2):
        for item1, item2 in itertools.zip_longest(iterable1, iterable2, fillvalue=None):
            if item1 is not None:
                yield item1
            if item2 is not None:
                yield item2

    for element in interleave(nodes, edges):
        assert agent.pos == element, "Agent must follow the entre path"
        if element == nodes[-1]:
            assert agent.finished() == True, "Agent must finish when the path is finished"
        else:
            assert agent.finished() == False, "Agent cannot finish when traversing the path"
            agent.step()

    with pytest.raises(ValueError) as exc_info:
        agent.step()

    assert exc_info.type is ValueError, "Agent cannot traverse after end of the path (exception type)"
    assert str(exc_info.value) == "Agent should be removed", "Correct string of exception"

@pytest.mark.parametrize("intersection", [0, 1, 2, 3, 4])
@pytest.mark.parametrize("road", [(0, 1), (1, 0), (1, 2), (2, 3), (2, 0)])
@pytest.mark.parametrize("num_steps", [1, 10, 50, 100])
def test_vehicle_stays_at_position(monkeypatch, seed, agent_type, intersection, road, num_steps):
    dummy_model = DummyModel(seed=seed)
    monkeypatch.setattr(dummy_model, "is_agent_leaving", mock_is_agent_leaving_false)
    monkeypatch.setattr(DummyModel, "get_obstacle_distance", mock_get_obstacle_distance)

    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=[-9999, 9999])

    agent.pos = intersection
    assert not agent.finished(), "Agent cannot finish"
    for _ in range(num_steps):
        agent.step()
        assert not agent.finished(), "Agent cannot finish"
        assert agent.pos == intersection, "Agent must stay at the intersection"
    assert not agent.finished(), "Agent cannot finish"

    agent.pos = road
    assert not agent.finished(), "Agent cannot finish"
    for _ in range(num_steps):
        agent.step()
        assert not agent.finished(), "Agent cannot finish"
        assert agent.pos == road, "Agent must stay at the road"
    assert not agent.finished(), "Agent cannot finish"
