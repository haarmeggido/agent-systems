import itertools

import pytest

from ainter.models.nagel_schreckenberg.model import DummyModel
from ainter.models.vehicles.vehicle import Vehicle, VehicleType, is_intersection_position


@pytest.mark.parametrize("seed", [0, 111, 222, 333, 444, 555, 666, 777, 888, 999])
@pytest.mark.parametrize("agent_type", [VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
@pytest.mark.parametrize("path", [[0, 1], [0, 1, 2], [0, 1, 2, 3], [1, 2, 3]])
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

@pytest.mark.parametrize("seed", [0, 111, 222, 333, 444, 555, 666, 777, 888, 999])
@pytest.mark.parametrize("agent_type", [VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
@pytest.mark.parametrize("path", [[0, 1], [0, 1, 2], [0, 1, 2, 3], [1, 2, 3]])
def test_vehicle_iterates_over_path(seed, agent_type, path):
    dummy_model = DummyModel(seed=seed)
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
