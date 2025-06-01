import pytest
import mesa

from ainter.models.vehicles.vehicle import Vehicle, VehicleType

@pytest.mark.parametrize("agent_type", [VehicleType.MOTORCYCLE, VehicleType.CAR, VehicleType.BUS, VehicleType.TRUCK,])
@pytest.mark.parametrize("path", [[0, 1], [0, 1, 2], [0, 1, 2, 3]])
def test_vehicle_finish(agent_type, path):
    dummy_model = mesa.Model()
    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    assert not agent.finished(), "Agent cannot finish if agent is not placed"

    for _ in range(len(path) + len(path) - 1):
        agent.step()
        assert not agent.finished()
