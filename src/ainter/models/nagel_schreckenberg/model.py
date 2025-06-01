from typing import Optional

import numpy as np
from mesa import Model, Agent
from networkx import descendants

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox, bfs_shortest_path
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.nagel_schreckenberg.units import discretize_time, TimeDensity, DiscreteLength, DiscreteSpeed, \
    discretize_length
from ainter.models.vehicles.vehicle import Vehicle, VehicleType, VehicleId, Position, is_intersection_position, \
    is_road_position


class NaSchUrbanModel(Model):

    def __init__(self, env_config: EnvConfig, seed=None) -> None:
        super().__init__(seed=seed)

        self.graph = get_data_from_bbox(env_config.map_box)
        self.grid = Environment.from_directed_graph(self.graph)

        self.time = discretize_time(env_config.physics.start_time)
        self.end_time = discretize_time(env_config.physics.end_time)

        self.agent_spawn_probability: TimeDensity = env_config.vehicles.time_density_strategy

        self.min_node_path_length = env_config.vehicles.min_node_path_length

        self.running = True

    def step(self) -> None:
        print(self.time)
        if self.random.random() < self.agent_spawn_probability(self.time):
            _ = self.spawn_agent()

        self.agents.sort(lambda x: x.unique_id).do("step")
        self.agents.sort(lambda x: x.unique_id).select(lambda x: x.finished()).do("remove")

        self.time += 1
        if self.time > self.end_time:
            self.running = False

    def spawn_agent(self) -> Agent:
        types = list(VehicleType)
        graph = self.grid.road_graph

        while True:
            start_node = self.random.choice(list(graph.nodes))
            end_node_possibilities = list(descendants(graph, start_node))
            if len(end_node_possibilities) == 0:
                continue
                
            end_node = self.random.choice(end_node_possibilities)
            path = bfs_shortest_path(graph, start_node, end_node)
            if len(path) >= self.min_node_path_length:
                break

        # Randomly select a vehicle type
        vehicle_type = self.random.choices(types, weights=[x.get_pdf() for x in types], k=1)[0]
        return Vehicle(model=self,
                       vehicle_type=vehicle_type,
                       path=path)

    def add_agent_to_environment(self, position: Position, agent_id: VehicleId, **kwargs) -> Intersection | Road:
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Cannot add agent nonexistent intersection"

            intersection = self.grid.intersections[position]
            intersection.add_agent(agent_id=agent_id)
            return intersection

        if is_road_position(position):
            assert position in self.grid.roads, "Cannot add agent to nonexistent road"

            road = self.grid.roads[position]
            kwargs |= {'lane': self.random.randint(0, road.lanes - 1)}
            road.add_agent(agent_id=agent_id, **kwargs)
            return road

        raise ValueError("Position cannot be decoded")

    def remove_agent_from_environment(self, position: Position, agent_id: VehicleId) -> None:
        pass

    def is_agent_leaving(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Cannot check if agent is leaving on a nonexistent intersection"
            intersection = self.grid.intersections[position]
            assert intersection.contains_agent(agent_id=agent_id), "Agent is not on this intersection"
            return intersection.is_agent_leaving(agent_id=agent_id, speed=speed)

        if is_road_position(position):
            assert position in self.grid.roads, "Cannot check if agent is leaving on a nonexistent road"
            road = self.grid.roads[position]
            assert road.contains_agent(agent_id=agent_id), "Agent is not on this road"
            return road.is_agent_leaving(agent_id=agent_id, speed=speed)

        raise ValueError("Position cannot be decoded")

    def move_agent(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        # Agents Obey the speed limit of the road
        # TODO: Check if an agent would collide
        #self.speed = self.decide_speed(road)
        #print("Agent", self.unique_id, "speed", self.speed)
        #road.move_agent(agent_id=self.unique_id,
        #                speed=self.speed)
        pass

    def get_obstacle_distance(self, position: Position, agent_id: VehicleId) -> DiscreteLength:
        return discretize_length(1.)


class DummyModel(Model):
    def __init__(self, seed=None) -> None:
        super().__init__(seed=seed)

        self.running = False

    def add_to_intersection(self, node_id: int, agent_id: int) -> None:
        pass

    def add_to_road(self,
                    road_id: tuple[int, int],
                    agent_id: int,
                    color: np.ndarray,
                    length: DiscreteLength) -> None:
        pass

    def is_agent_leaving_intersection(self, node_id: int, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        return False

    def is_agent_leaving_road(self, road_id: tuple[int, int], agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        return False
