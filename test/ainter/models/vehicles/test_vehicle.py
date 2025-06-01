import pytest

from ainter.models.nagel_schreckenberg.model import DummyModel
from ainter.models.vehicles.vehicle import Vehicle, VehicleType, is_intersection_position


@pytest.mark.parametrize("seed", [0, 111, 222, 333, 444, 555, 666, 777, 888, 999])
@pytest.mark.parametrize("agent_type", [VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
@pytest.mark.parametrize("path", [[0, 1], [0, 1, 2], [0, 1, 2, 3]])
def test_vehicle_creation(seed, agent_type, path):
    dummy_model = DummyModel(seed=seed)
    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    assert is_intersection_position(agent.pos), "Agent must be spawned on the intersection"

@pytest.mark.parametrize("seed", [0, 111, 222, 333, 444, 555, 666, 777, 888, 999])
@pytest.mark.parametrize("agent_type", [VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
@pytest.mark.parametrize("path", [[0, 1], [0, 1, 2], [0, 1, 2, 3]])
def test_vehicle_finish(seed, agent_type, path):
    dummy_model = DummyModel(seed=seed)
    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    #assert not agent.finished(), "Agent cannot finish if agent is not placed"

    #for _ in range(len(path) + len(path) - 1):
    #    agent.step()
    #    assert not agent.finished()
