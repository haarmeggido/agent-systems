from dataclasses import dataclass, field
from typing import Self, Any

import numpy as np

from ainter.models.autonomous_intersection.intersection_directions import IntersectionEntranceDirection, \
    IntersectionDirection
from ainter.models.autonomous_intersection.traffic_lights import SimpleTrafficLight, TrafficLight
from ainter.models.nagel_schreckenberg.units import DiscreteSpeed, ROAD_COLOR, DiscreteLength, discretize_length, \
    DiscreteTime, LINE_WIDTH
from ainter.models.vehicles.vehicle import VehicleId
from ainter.models.autonomous_intersection.lane_directions import LaneDirections

RED_LIGHT_COLOR = np.array([255, 0, 0], dtype=np.uint8)
GREEN_LIGHT_COLOR = np.array([0, 255, 0], dtype=np.uint8)
POSSIBLE_LIGHTS_TIMESTEPS: list[DiscreteTime] = [30, 35, 40]

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
                                                               action_slice = None,
                                                               name=edge_data['name'],
                                                               lanes=edge_data['lanes'])
        elif 45 <= angle_deg < 135:
            assert (IntersectionEntranceDirection.NORTH, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.NORTH, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.NORTH,
                                                               action_slice=None,
                                                               name=edge_data['name'],
                                                               lanes=edge_data['lanes'])
        elif 135 <= angle_deg or -135 > angle_deg:
            assert (IntersectionEntranceDirection.WEST, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.WEST, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.WEST,
                                                               action_slice=None,
                                                               name=edge_data['name'],
                                                               lanes=edge_data['lanes'])
        else:
            assert (IntersectionEntranceDirection.SOUTH, is_in) not in used_directions, "Two many one way directions"
            used_directions.add((IntersectionEntranceDirection.SOUTH, is_in))
            edge_directions[edge_info] = IntersectionDirection(direction=IntersectionEntranceDirection.SOUTH,
                                                               action_slice=None,
                                                               name=edge_data['name'],
                                                               lanes=edge_data['lanes'])

    return edge_directions, used_directions

def calculate_slice(direction: IntersectionEntranceDirection, is_in: bool, lanes: int) -> tuple[slice, slice]:
    grid_length = int(lanes * LINE_WIDTH)
    match (direction, is_in):
        case (IntersectionEntranceDirection.NORTH, True):
            return slice(0, grid_length), slice(0, 1)

        case (IntersectionEntranceDirection.NORTH, False):
            return slice(-grid_length, None), slice(0, 1)

        case (IntersectionEntranceDirection.WEST, True):
            return slice(0, 1), slice(-grid_length, None)

        case (IntersectionEntranceDirection.WEST, False):
            return slice(0, 1), slice(0, grid_length)

        case (IntersectionEntranceDirection.SOUTH, True):
            return slice(-grid_length, None), slice(-1, None)

        case (IntersectionEntranceDirection.SOUTH, False):
            return slice(0, grid_length), slice(-1, None)

        case (IntersectionEntranceDirection.EAST, True):
            return slice(-1, None), slice(0, grid_length)

        case (IntersectionEntranceDirection.EAST, False):
            return slice(-1, None), slice(-grid_length, None)

    raise ValueError("Unknown direction + entrance type provided")


@dataclass(slots=True)
class Intersection:
    osm_id: int
    grid: np.ndarray
    x: float
    y: float
    in_edge_directions: dict[int, IntersectionDirection]
    out_edge_directions: dict[int, IntersectionDirection]
    traffic_lights: TrafficLight
    render_lut: np.ndarray = field(init=False,
                                   default_factory=lambda: np.full(shape=(2 ** 16, 3),
                                                                   fill_value=ROAD_COLOR,
                                                                   dtype=np.uint8))

    @classmethod
    def from_graph_data(cls, osm_id: int,
                        edges_info: dict[tuple[int, int], Any],
                        node_info: dict[str, Any],
                        global_time: DiscreteTime,
                        rng) -> Self:
        x = node_info['x']
        y = node_info['y']

        edge_directions, used_directions = create_edge_directions(osm_id, x, y, edges_info)

        traffic_lights = SimpleTrafficLight(global_time, rng.choice(POSSIBLE_LIGHTS_TIMESTEPS))
        for direction, is_in in used_directions:
            if is_in:
                traffic_lights.add_direction(direction)

        in_edge_directions: dict[int, IntersectionDirection] = dict()
        out_edge_directions: dict[int, IntersectionDirection] = dict()

        for edge_direction_k, edge_direction_v in edge_directions.items():
            if edge_direction_k[0] != osm_id:
                in_edge_directions[edge_direction_k[0]] = edge_direction_v
            else:
                out_edge_directions[edge_direction_k[1]] = edge_direction_v

                    #N, E, S, W
        size_list = [0, 0, 0, 0]

        # TODO: Consider moving calculate_slice(...) inside create_edge_directions(...)
        for in_direction in in_edge_directions.values():
            size_list[in_direction.direction.value] += in_direction.lanes
            in_direction.action_slice = calculate_slice(in_direction.direction, True, in_direction.lanes)

        for out_direction in out_edge_directions.values():
            size_list[out_direction.direction.value] += out_direction.lanes
            out_direction.action_slice = calculate_slice(out_direction.direction, False, out_direction.lanes)

        x_int_size = int(max(size_list[0], size_list[2]) * LINE_WIDTH)
        y_int_size = int(max(size_list[1], size_list[3]) * LINE_WIDTH)

        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(x_int_size, y_int_size), dtype=np.uint16),
                   x=x,
                   y=y,
                   in_edge_directions=in_edge_directions,
                   out_edge_directions=out_edge_directions,
                   traffic_lights=traffic_lights)

    def add_agent(self, agent_id: VehicleId) -> None:
        if self.is_end_of_the_road():
            return

    def remove_agent(self, agent_id: VehicleId) -> None:
        if self.is_end_of_the_road():
            return

    def move_agent(self, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        if self.is_end_of_the_road():
            return

    def is_agent_leaving(self, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        if self.is_end_of_the_road():
            return True
        return True

    def step(self) -> None:
        self.traffic_lights.step()

    def render(self) -> np.ndarray:
        base_render = self.render_lut[self.grid]

        padded_render = np.full(
            shape=(base_render.shape[0] + 2,
                   base_render.shape[1] + 2,
                   3),
            fill_value=ROAD_COLOR,
            dtype=np.uint8
        )

        padded_render[1:-1, 1:-1] = base_render

        for incoming_edge in self.in_edge_directions.values():
            has_right_of_way = self.traffic_lights.has_right_of_way(incoming_edge.direction)
            light_color = GREEN_LIGHT_COLOR if has_right_of_way else RED_LIGHT_COLOR
            data_slice_x, data_slice_y = incoming_edge.action_slice

            match incoming_edge.direction:
                case IntersectionEntranceDirection.NORTH:
                    padded_render[slice(data_slice_x.start + 1, data_slice_x.stop + 1), data_slice_y] = light_color

                case IntersectionEntranceDirection.EAST:
                    padded_render[data_slice_x, slice(data_slice_y.start + 1, data_slice_y.stop + 1)] = light_color

                case IntersectionEntranceDirection.SOUTH:
                    data_slice_x_not_null = data_slice_y.stop - 1 if data_slice_y.stop is not None else -1
                    padded_render[slice(data_slice_x.start - 1, data_slice_x_not_null), data_slice_y] = light_color

                case IntersectionEntranceDirection.WEST:
                    data_slice_y_not_null = data_slice_y.stop - 1 if data_slice_y.stop is not None else -1
                    padded_render[data_slice_x, slice(data_slice_y.start - 1, data_slice_y_not_null)] = light_color

        return padded_render.transpose(1, 0, 2)

    def contains_agent(self, agent_id: VehicleId) -> bool:
        if self.is_end_of_the_road():
            return True
        return True

    def can_accept_agent(self, agent_id: VehicleId, length: DiscreteLength) -> bool:
        if self.is_end_of_the_road():
            return True
        return True

    def get_obstacle_distance(self, agent_id: VehicleId) -> DiscreteLength:
        if self.is_end_of_the_road():
            return discretize_length(1.)
        return discretize_length(1.)

    def is_end_of_the_road(self) -> bool:
        return self.grid.shape[0] == 0 or self.grid.shape[1] == 0

    def get_direction_to(self, start_node: int, end_node: int) -> LaneDirections:
        pass