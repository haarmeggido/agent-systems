import itertools
from abc import abstractmethod, ABC

from mesa import Model, Agent
from mesa.datacollection import DataCollector
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


class VehicleModel(ABC):

    @abstractmethod
    def spawn_agent(self) -> Agent:
        pass

    @abstractmethod
    def add_agent_to_environment(self, position: Position, agent_id: VehicleId, **kwargs) -> Intersection | Road:
        pass

    @abstractmethod
    def remove_agent_from_environment(self, position: Position, agent_id: VehicleId) -> None:
        pass

    @abstractmethod
    def is_agent_leaving(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> bool:
        pass

    @abstractmethod
    def move_agent(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> None:
        pass

    @abstractmethod
    def get_obstacle_distance(self, position: Position, agent_id: VehicleId) -> DiscreteLength:
        pass


class NaSchUrbanModel(Model, VehicleModel):

    def __init__(self, env_config: EnvConfig, seed=None) -> None:
        super().__init__(seed=seed)

        self.start_time = discretize_time(env_config.physics.start_time)
        self.time = discretize_time(env_config.physics.start_time)
        self.end_time = discretize_time(env_config.physics.end_time)

        self.graph = get_data_from_bbox(env_config.map_box)
        self.grid = Environment.from_directed_graph(self.graph, self.time, self.random)

        self.agent_spawn_probability: TimeDensity = env_config.vehicles.time_density_strategy

        self.min_node_path_length = env_config.vehicles.min_node_path_length

        self.datacollector = DataCollector(
            model_reporters={
            "AgentCount": lambda m: m.num_agents,
            },
            agent_reporters={
            "Speed": lambda a: getattr(a, "speed", None) * 3.6 if getattr(a, "speed", None) is not None else None,
            "VehicleType": lambda a: {1: "Car", 2: "Bus", 3: "Truck", 4: "Motorcycle"}.get(getattr(a, "type", None), None),
            "Position": lambda a: getattr(a, "pos", None),
            }
        )

        

        self.running = True

    @property
    def num_agents(self):
        return len(self.agents)

    def step(self) -> None:
        hours = self.time // 3600
        minutes = (self.time % 3600) // 60
        seconds = self.time % 60
        print(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
        if self.random.random() < self.agent_spawn_probability(self.time):
            _ = self.spawn_agent()

        self.agents.sort(lambda x: x.unique_id).do("step")
        self.agents.sort(lambda x: x.unique_id).select(lambda x: x.finished()).do("remove")

        self.grid.step()
        self.datacollector.collect(self)
        # self.datacollector.collect_agent_vars(self.agents)

        self.time += 1
        if self.time > self.end_time:
            self.running = False

            df_model = self.datacollector.get_model_vars_dataframe()
            df_agents = self.datacollector.get_agent_vars_dataframe()

            df_model.to_csv("src/ainter/data/model_results.csv")
            df_agents.to_csv("src/ainter/data/agent_results.csv")


    def spawn_agent(self) -> Agent:
        types = list(VehicleType)
        graph = self.grid.road_graph
        vehicle_type: VehicleType = self.random.choices(types, weights=[x.get_pdf() for x in types], k=1)[0]
        vehicle_minimum_road_length = vehicle_type.get_characteristic().length + discretize_length(2.)

        while True:
            start_node = self.random.choice(list(graph.nodes))
            end_node_possibilities = list(descendants(graph, start_node))
            if len(end_node_possibilities) == 0:
                continue

            end_node = self.random.choice(end_node_possibilities)
            path = bfs_shortest_path(graph, start_node, end_node)
            if len(path) < self.min_node_path_length:
                continue

            if any(map(lambda x: discretize_length(self.grid.roads[x].length) < vehicle_minimum_road_length,
                       itertools.pairwise(path))):
                continue

            break


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
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Cannot add agent nonexistent intersection"
            intersection = self.grid.intersections[position]
            assert intersection.contains_agent(agent_id=agent_id), "Agent is not on this intersection"
            intersection.remove_agent(agent_id=agent_id)

        elif is_road_position(position):
            assert position in self.grid.roads, "Cannot add agent to nonexistent road"
            road = self.grid.roads[position]
            assert road.contains_agent(agent_id=agent_id), "Agent is not on this road"
            road.remove_agent(agent_id=agent_id)

        else:
            raise ValueError("Position cannot be decoded")

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

    def move_agent(self, position: Position, agent_id: VehicleId, speed: DiscreteSpeed) -> DiscreteSpeed:
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Agent cannot move on a nonexistent intersection"
            intersection = self.grid.intersections[position]
            assert intersection.contains_agent(agent_id=agent_id), "Agent is not on this intersection"
            return intersection.move_agent(agent_id=agent_id,
                                           speed=speed)

        elif is_road_position(position):
            assert position in self.grid.roads, "Agent cannot move on a nonexistent road"
            road = self.grid.roads[position]
            assert road.contains_agent(agent_id=agent_id), "Agent is not on this road"
            return road.move_agent(agent_id=agent_id, speed=speed)

        raise ValueError("Position cannot be decoded")

    def get_obstacle_distance(self, position: Position, agent_id: VehicleId) -> DiscreteLength:
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Cannot check if agent is leaving on a nonexistent intersection"
            intersection = self.grid.intersections[position]
            assert intersection.contains_agent(agent_id=agent_id), "Agent is not on this intersection"
            return intersection.get_obstacle_distance(agent_id=agent_id)

        if is_road_position(position):
            assert position in self.grid.roads, "Cannot check if agent is leaving on a nonexistent road"
            road = self.grid.roads[position]
            assert road.contains_agent(agent_id=agent_id), "Agent is not on this road" # not working at the moment
            return road.get_obstacle_distance(agent_id=agent_id)

        raise ValueError("Position cannot be decoded")

    def can_accept_agent(self, position: Position, agent_id: VehicleId, length: DiscreteLength) -> bool:
        if is_intersection_position(position):
            assert position in self.grid.intersections, "Cannot check if agent is leaving on a nonexistent intersection"
            intersection = self.grid.intersections[position]
            # assert not intersection.contains_agent(agent_id=agent_id), "Agent is on this intersection"
            return intersection.can_accept_agent(agent_id=agent_id, length=length)

        if is_road_position(position):
            assert position in self.grid.roads, "Cannot check if agent is leaving on a nonexistent road"
            road = self.grid.roads[position]
            assert not road.contains_agent(agent_id=agent_id), "Agent is on this road"
            return road.can_accept_agent(agent_id=agent_id, length=length)

        raise ValueError("Position cannot be decoded")
