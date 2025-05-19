from random import randint, random

from mesa import Model
from mesa.space import NetworkGrid

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_time, TimeDensity
from ainter.models.vehicles.vehicle import generate_vehicles


class NaSchUrbanModel(Model):

    def __init__(self, env_config: EnvConfig, seed=None) -> None:
        super().__init__(seed=seed)

        self.graph = get_data_from_bbox(env_config.map_box)
        self.grid = Environment.from_directed_graph(self.graph)
        #self.agents = generate_vehicles(self.environment.road_graph,
        #                               discretize_time(env_config.physics.start_time),
        #                               discretize_time(env_config.physics.end_time),
        #                               config.vehicles.time_density_strategy)

        self.active_agent_indexes = []
        self.last_index = 0
        self.time = discretize_time(env_config.physics.start_time)
        self.end_time = discretize_time(env_config.physics.end_time)

        self.agent_spawn_probability: TimeDensity = env_config.vehicles.time_density_strategy

        self.running = True

    def step(self) -> None:
        if random() < self.agent_spawn_probability(self.time):
            # TODO: Add agent
            pass
        # For now, ignore intersections

        # Add all agents spawned at this timestep
        # while self.agents[self.last_index].start_time <= self.time:
        #     self.active_agent_indexes.append(self.last_index)
        #     self.last_index += 1
        #
        # for agent in map(lambda agent_index: self.agents[agent_index], self.active_agent_indexes):
        #
        #     match agent:
        #         case _ if agent.is_on_intersection():   # Immediately teleport agent to the next road segment
        #             intersection = self.environment.intersections[agent.location]
        #
        #             if intersection.is_agent_leaving(age, speed):
        #                 current_journey_index = agent.path.index(agent.location)
        #                 agent.location = (agent.path[current_journey_index], agent.path[current_journey_index + 1])
        #                 road = self.environment.roads[agent.location]
        #                 road.add_agent(agent_id=agent.id,
        #                                lane=randint(0, road.lanes),
        #                                length=agent.type.get_characteristic().length)
        #
        #         case _ if agent.is_on_road():  # Immediately teleport agent to the next road segment
        #             road = self.environment.roads[agent.location]
        #             road.move_agent()
        #
        #         case _:
        #             agent.location = agent.from_node
        print(self.time)
        self.time += 1

        if self.time > self.end_time:
            self.running = False
