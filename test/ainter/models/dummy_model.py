from mesa import Model, Agent

from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.model import VehicleModel
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.nagel_schreckenberg.units import DiscreteSpeed, DiscreteLength
from ainter.models.vehicles.vehicle import Position, VehicleId


class DummyModel(Model, VehicleModel):
    """Fake model for testing only"""

    def __init__(self, seed=None) -> None:
        super().__init__(seed=seed)

        self.running = False

    def spawn_agent(self) -> Agent:
        pass

    def add_agent_to_environment(self, position: Position, agent_id: VehicleId, **kwargs) -> Intersection | Road:
        pass

    def remove_agent_from_environment(self, position: Position, agent_id: VehicleId) -> None:
        pass

    def is_agent_leaving(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        pass

    def move_agent(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        pass

    def get_obstacle_distance(self, position: Position, agent_id: VehicleId) -> DiscreteLength:
        pass
