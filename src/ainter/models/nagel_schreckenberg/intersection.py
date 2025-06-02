from dataclasses import dataclass, field
from typing import Self, Any

import numpy as np

from ainter.models.nagel_schreckenberg.units import DiscreteSpeed, ROAD_COLOR, DiscreteLength
from ainter.models.vehicles.vehicle import VehicleId


@dataclass(slots=True)
class Intersection:
    osm_id: int
    grid: np.ndarray
    x: float
    y: float
    render_lut: np.ndarray = field(init=False,
                                   default_factory=lambda: np.full(shape=(2 ** 17 - 1, 3),
                                                                   fill_value=ROAD_COLOR,
                                                                   dtype=np.uint8))

    @classmethod
    def from_graph_data(cls, osm_id: int,
                        edges_info: dict[tuple[int, int], Any],
                        node_info: dict[str, Any]) -> Self:


        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(10, 10), dtype=np.uint16),
                   x=node_info['x'],
                   y=node_info['y'])

    def add_agent(self, agent_id: VehicleId) -> None:
        pass

    def remove_agent(self, agent_id: VehicleId) -> None:
        pass

    def move_agent(self, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        pass

    def is_agent_leaving(self, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        return True

    def render(self) -> np.ndarray:
        return self.render_lut[self.grid.T]

    def contains_agent(self, agent_id: VehicleId) -> bool:
        return True

    def can_accept_agent(self, agent_id: VehicleId, length: DiscreteLength) -> bool:
        return True
