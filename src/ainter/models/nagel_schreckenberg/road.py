from dataclasses import dataclass, field
from typing import Self, Any, Optional

import numpy as np
from shapely import LineString

from ainter.models.nagel_schreckenberg.units import discretize_length, PhysicalLength, PhysicalSpeed, DiscreteSpeed, \
    DiscreteLength, ROAD_COLOR, convert_km_h_to_m_s
from ainter.models.vehicles.vehicle import VehicleId, NULL_VEHICLE_ID
from ainter.models.autonomous_intersection.lane_directions import LaneDirections


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
                                   default_factory=lambda: np.full(shape=(2 ** 16, 3),
                                                                   fill_value=ROAD_COLOR,
                                                                   dtype=np.uint8))

    @classmethod
    def from_graph_data(cls,
                        start_node_info: dict[str, Any],
                        end_node_info: dict[str, Any],
                        edge_info: dict[str, Any]) -> Self:

        osm_id = edge_info['osmid']
        lanes = edge_info['lanes']
        length = edge_info['length']
        cells_num = discretize_length(length)
        max_speed = convert_km_h_to_m_s(edge_info['max_speed'])
        name = edge_info['name']
        is_oneway = edge_info['oneway']
        is_reversed = edge_info['reversed']
        geometry = edge_info['geometry']

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
        if lane < 0 or lane > self.lanes:
            raise ValueError("Incorrect lane number provided")

        if length < 0 or length > discretize_length(self.length):
            raise ValueError("Length isd either negative or the agent des not fit into the road")

        if np.any(self.grid == agent_id):
            raise ValueError("Cannot add the agent twice to a road")

        # TODO: Check if line is occupied
        self.grid[:length, lane] = agent_id
        self.render_lut[agent_id] = color

    def remove_agent(self, agent_id: VehicleId) -> None:
        self.render_lut[agent_id] = ROAD_COLOR
        self.grid = np.where(self.grid == agent_id, NULL_VEHICLE_ID, self.grid)

    def move_agent(self, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        assert self.contains_agent(agent_id), "Road must contain this agent"

        if speed < 0 or speed > self.grid.shape[0]:
            raise ValueError("Incorrect speed provided")

        agent_start = np.where(self.grid == agent_id)[0][0]
        agent_lane = np.where(self.grid == agent_id)[1][0]
        agent_length = np.sum(self.grid == agent_id)

        self.grid[agent_start:agent_start + agent_length, agent_lane] = NULL_VEHICLE_ID
        if agent_start + agent_length + speed > self.grid.shape[0]:
            assert np.all(self.grid[-agent_length:, agent_lane] != agent_id), 'Cannot put two agent at the same place'
            self.grid[-agent_length:, agent_lane] = agent_id
        else:
            assert np.all( self.grid[agent_start + speed:agent_start + agent_length + speed, agent_lane] != agent_id), 'Cannot put two agent at the same place'
            self.grid[agent_start + speed:agent_start + agent_length + speed, agent_lane] = agent_id

        assert self.contains_agent(agent_id), "Road must contain this agent"

    def get_length_to_obstacle(self, agent_id: VehicleId) -> DiscreteLength:
        agent_start = np.where(self.grid == agent_id)[0][0]
        agent_lane = np.where(self.grid == agent_id)[1][0]
        agent_length = np.sum(self.grid == agent_id)
        agent_end = agent_start + agent_length - 1
        road_length = self.grid.shape[0]

        for i in range(agent_end + 1, road_length):
            if self.grid[i, agent_lane] != agent_id and self.grid[i, agent_lane] != NULL_VEHICLE_ID:
                return i - agent_end - 1

        return road_length - agent_end - 1

    def is_agent_leaving(self, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        return np.any(self.grid[-(speed + 1):, :] == agent_id)

    def render(self) -> np.ndarray:
        return self.render_lut[self.grid.T]

    def contains_agent(self, agent_id: VehicleId) -> bool:
        return np.any(self.grid == agent_id)

    def can_accept_agent(self, agent_id: VehicleId, length: DiscreteLength) -> bool:
        return (not self.contains_agent(agent_id)) and np.all(self.grid[:length, :] == NULL_VEHICLE_ID)

    def get_obstacle_distance(self, agent_id: VehicleId) -> DiscreteLength:
        agent_indices = np.where(self.grid == agent_id)
        if len(agent_indices[0]) == 0:
            raise ValueError("Agent not found on road")

        agent_start = agent_indices[0][0]
        agent_lane = agent_indices[1][0]
        agent_length = np.sum(self.grid[:, agent_lane] == agent_id)
        agent_end = agent_start + agent_length - 1
        assert self.grid[agent_end, agent_lane] == agent_id, "Agent must be traced"
        road_length = self.grid.shape[0]

        if agent_end >= road_length - 1:
            return discretize_length(0.)

        distance_to_obstacle = road_length - agent_end - 1

        for i in range(agent_end + 1, road_length):
            if self.grid[i, agent_lane] != NULL_VEHICLE_ID:
                distance_to_obstacle = i - agent_end - 1
                break

        return distance_to_obstacle

    def get_possible_lanes(self, direction: LaneDirections) -> set[int]:
        assert self.lanes > 0, 'Lanes number cannot bne negative'
        if self.lanes == 1:
            return {0}

        if self.lanes == 2:
            if direction == LaneDirections.LEFT:
                return {0}
            if direction == LaneDirections.RIGHT:
                return {1}
            if direction == LaneDirections.STRAIGHT:
                return {0, 1}

        if self.lanes == 3:
            if direction == LaneDirections.LEFT:
                return {0}
            if direction == LaneDirections.RIGHT:
                return {2}
            if direction == LaneDirections.STRAIGHT:
                return {0, 1}

        raise ValueError("Too many lanes")
