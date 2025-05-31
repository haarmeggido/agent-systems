from random import choice, choices

from mesa import Model, Agent
from networkx import descendants

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox, bfs_shortest_path
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_time, TimeDensity
from ainter.models.vehicles.vehicle import Vehicle, VehicleType


class NaSchUrbanModel(Model):

    def __init__(self, env_config: EnvConfig, seed=None) -> None:
        super().__init__(seed=seed)

        self.graph = get_data_from_bbox(env_config.map_box)
        self.grid = Environment.from_directed_graph(self.graph)

        self.time = discretize_time(env_config.physics.start_time)
        self.end_time = discretize_time(env_config.physics.end_time)

        self.agent_spawn_probability: TimeDensity = env_config.vehicles.time_density_strategy

        self.running = True
        # self.spawn_agent()

    def step(self) -> None:
        print(self.time)
        if self.random.random() < self.agent_spawn_probability(self.time):
            self.spawn_agent()

        # TODO: remove except
        try:
            self.agents.sort(lambda x: x.unique_id).do("step")
            self.agents.sort(lambda x: x.unique_id).select(lambda x : x.finished()).do("remove")
        except:
            pass

        self.time += 1
        if self.time > self.end_time:
            self.running = False

    def spawn_agent(self) -> Agent:
        types = list(VehicleType)
        graph = self.grid.road_graph

        while True:
            start_node = choice(list(graph.nodes))
            end_node_possibilities = list(descendants(graph, start_node))
            if len(end_node_possibilities) > 0:
                break

        end_node = choice(end_node_possibilities)

        path = bfs_shortest_path(graph, start_node, end_node)

        # Randomly select a vehicle type
        vehicle_type, = choices(types, weights=list(map(lambda x: x.get_pdf(), types)), k=1)
        return Vehicle(model=self,
                       type=vehicle_type,
                       path=path)
