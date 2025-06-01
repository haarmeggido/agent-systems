from dataclasses import dataclass, field
from typing import Self, Any, Optional

import numpy as np
from shapely import LineString

from ainter.models.nagel_schreckenberg.units import discretize_length, PhysicalLength, DEFAULT_ROAD_MAX_SPEED, \
    PhysicalSpeed, DiscreteSpeed, DiscreteLength, ROAD_COLOR, convert_km_h_to_m_s
from ainter.models.vehicles.vehicle import VehicleId


@dataclass(slots=True)
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
    render_lut: np.ndarray = field(init=False,
                                   default_factory=lambda: np.full(shape=(2 ** 17 - 1, 3),
                                                                   fill_value=ROAD_COLOR,
                                                                   dtype=np.uint8))

    @classmethod
    def from_graph_data(cls,
                        start_node_info: dict[str, Any],
                        end_node_info: dict[str, Any],
                        edge_info: dict[str, Any]) -> Self:

        osm_id = edge_info['osmid']
        lanes = int(edge_info.get('lanes', '1'))
        length = edge_info['length']
        cells_num = discretize_length(length.astype(np.float32))
        max_speed = convert_km_h_to_m_s(float(edge_info.get('max_speed', DEFAULT_ROAD_MAX_SPEED)))
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

    def add_agent(self, agent_id: VehicleId, color: np.ndarray, lane: int, length: DiscreteLength) -> None:
        self.render_lut[agent_id] = color

        if lane < 0 or lane > self.lanes:
            raise ValueError("Incorrect lane number provided")

        if length < 0 or length > discretize_length(self.length):
            raise ValueError("Length isd either negative or the agent des not fit into the road")

        if np.any(self.grid == agent_id):
            raise ValueError("Cannot add the agent twice to a road")

        # TODO: Check if line is occupied
        self.grid[:length, lane] = agent_id

    def remove_agent(self, agent_id: VehicleId) -> None:
        self.render_lut[agent_id] = ROAD_COLOR
        self.grid = np.where(self.grid == agent_id, ROAD_COLOR, self.grid)

    def move_agent(self, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        if speed < 0 or speed > self.grid.shape[0]:
            raise ValueError("Incorrect speed provided")

        agent_start = np.where(self.grid == agent_id)[0][0]
        agent_lane = np.where(self.grid == agent_id)[1][0]
        agent_length = np.sum(self.grid == agent_id)
        self.grid[agent_start:agent_start + agent_length, agent_lane] = ROAD_COLOR
        self.grid[agent_start + speed:agent_start + agent_length + speed, agent_lane] = agent_id

    def get_length_to_obstacle(self, agent_id: VehicleId) -> DiscreteLength:
        agent_start = np.where(self.grid == agent_id)[0][0]
        agent_lane = np.where(self.grid == agent_id)[1][0]
        road_length = self.grid.shape[0]

        if agent_start + 1 >= road_length:
            return 0

        for i in range(agent_start + 1, road_length):
            if self.grid[i, agent_lane] != ROAD_COLOR:
                return i - agent_start

        return road_length - agent_start

    def is_agent_leaving(self, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        return (self.grid[-(speed + 1):, :] == agent_id).any()

    def render(self) -> np.ndarray:
        return self.render_lut[self.grid.T]

    def contains_agent(self, agent_id) -> bool:
        return np.any(self.grid == agent_id)

