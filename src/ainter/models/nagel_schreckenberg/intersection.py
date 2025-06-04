from dataclasses import dataclass, field
from typing import Self, Any

import numpy as np

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection, \
    IntersectionDirection
from ainter.models.autonomous_intersection.traffic_lights import SimpleTrafficLight, TrafficLight
from ainter.models.nagel_schreckenberg.units import DiscreteSpeed, ROAD_COLOR, DiscreteLength, discretize_length, \
    DiscreteTime
from ainter.models.vehicles.vehicle import VehicleId

def create_edge_directions(
        osm_id, inter_x, inter_y, edges_info
    ) -> tuple[dict[tuple[int, int], IntersectionDirection], set[tuple[IntersectionEntranceDirection, bool]]]:
    edge_directions = dict()
    used_directions = set()

    for edge_info, edge_data in edges_info.items():
        geom_points_x, geom_points_y = edge_data['geometry'].xy
        is_in = edge_info[0] != osm_id
        if is_in:
            shifted_geom_x = geom_points_x[-2] - inter_x
            shifted_geom_y = geom_points_y[-2] - inter_y
        else:
            shifted_geom_x = geom_points_x[1] - inter_x
            shifted_geom_y = geom_points_y[1] - inter_y


        angle_rad = np.arctan2(shifted_geom_y, shifted_geom_x)
        angle_deg = np.degrees(angle_rad)
        if -45 <= angle_deg < 45:
            assert (IntersectionEntranceDirection.EAST, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.EAST, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.EAST,
                                                               lanes=edge_data['lanes'])
        elif 45 <= angle_deg < 135:
            assert (IntersectionEntranceDirection.NORTH, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.NORTH, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.NORTH,
                                                               lanes=edge_data['lanes'])
        elif 135 <= angle_deg or -135 > angle_deg:
            assert (IntersectionEntranceDirection.WEST, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.WEST, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.WEST,
                                                               lanes=edge_data['lanes'])
        else:
            assert (IntersectionEntranceDirection.SOUTH, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.SOUTH, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.SOUTH,
                                                               lanes=edge_data['lanes'])

    return edge_directions, used_directions


@dataclass(slots=True)
class Intersection:
    osm_id: int
    grid: np.ndarray
    x: float
    y: float
    edge_directions: dict[tuple[int, int], IntersectionDirection]
    traffic_lights: TrafficLight
    render_lut: np.ndarray = field(init=False,
                                   default_factory=lambda: np.full(shape=(2 ** 16, 3),
                                                                   fill_value=ROAD_COLOR,
                                                                   dtype=np.uint8))

    @classmethod
    def from_graph_data(cls, osm_id: int,
                        edges_info: dict[tuple[int, int], Any],
                        node_info: dict[str, Any],
                        global_time: DiscreteTime) -> Self:
        x = node_info['x']
        y = node_info['y']

        edge_directions, used_directions = create_edge_directions(osm_id, x, y, edges_info)

        traffic_lights = SimpleTrafficLight(global_time, 40)
        for direction, is_in in used_directions:
            if is_in:
                traffic_lights.add_direction(direction)

        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(10, 10), dtype=np.uint16),
                   x=x,
                   y=y,
                   edge_directions=edge_directions,
                   traffic_lights=traffic_lights)

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

    def get_obstacle_distance(self, agent_id: VehicleId) -> DiscreteLength:
        return discretize_length(1.)
