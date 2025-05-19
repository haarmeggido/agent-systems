from dataclasses import dataclass
from typing import Self, Any, Optional

import numpy as np
from shapely import LineString

from ainter.models.nagel_schreckenberg.units import discretize_length, PhysicalLength, DEFAULT_ROAD_MAX_SPEED, \
    PhysicalSpeed, DiscreteSpeed, discretize_speed, DiscreteLength
from ainter.models.vehicles.vehicle import VehicleId


@dataclass(slots=True, frozen=True)
class Road:
    osm_id: int
    grid: np.ndarray
    lanes: int
    max_speed: PhysicalSpeed
    name: Optional[str]
    oneway: bool
    reversed: bool
    length: PhysicalLength
    geometry: LineString

    @classmethod
    def from_graph_data(cls,
                        start_node_info: dict[str, Any],
                        end_node_info: dict[str, Any],
                        edge_info: dict[str, Any]) -> Self:

        osm_id = edge_info['osmid']
        lanes = int(edge_info.get('lanes', '1'))
        length = edge_info['length']
        cells_num = discretize_length(length.astype(np.float32))
        max_speed = float(edge_info.get('max_speed', DEFAULT_ROAD_MAX_SPEED))
        name = edge_info.get('name', None)
        name = name if name != '' else None
        is_oneway = edge_info['oneway']
        is_reversed = edge_info['reversed']
        geometry = edge_info.get('geometry', LineString(coordinates=[[start_node_info['x'], start_node_info['y']],
                                                                     [end_node_info['x'], end_node_info['y']]]))

        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(cells_num, lanes), dtype=np.uint16),
                   lanes=lanes,
                   max_speed=max_speed,
                   name=name,
                   oneway=is_oneway,
                   reversed=is_reversed,
                   length=length,
                   geometry=geometry)

    def add_agent(self, agent_id: VehicleId, lane: int, length: DiscreteLength) -> None:
        if lane < 0 or lane > self.lanes:
            raise ValueError("Incorrect lane number provided")

        if length < 0 or length > discretize_length(self.length):
            raise ValueError("Length isd either negative or the agent des not fit into the road")

        if np.any(self.grid == agent_id):
            raise ValueError("Cannot add the agent twice to a road")

    def is_agent_leaving(self, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        pass

    def move_agents(self, id: VehicleId, speed: DiscreteSpeed) -> None:
        if speed > discretize_speed(self.max_speed):
            raise ValueError("Too big speed reached")

    def render(self) -> np.ndarray:
        return self.grid.T
