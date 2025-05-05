from dataclasses import dataclass, field
from random import randint
from typing import Self

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_time, DiscreteTime
from ainter.models.vehicles.vehicle import Vehicle, generate_vehicles


@dataclass(slots=True)
class Model:
    environment: Environment
    agents: list[Vehicle]
    active_agent_indexes: list[int] = field(init=False)
    last_index: int = field(init=False)
    time: DiscreteTime

    def __post_init__(self) -> None:
        self.active_agent_indexes = []
        self.last_index = 0

    @classmethod
    def from_config(cls, config: EnvConfig) -> Self:
        graph = get_data_from_bbox(config.map_box)
        env = Environment.from_directed_graph(graph)
        vehicles = generate_vehicles(env.road_graph,
                                     discretize_time(config.physics.start_time),
                                     discretize_time(config.physics.end_time),
                                     config.vehicles.time_density_strategy)
        return cls(environment=env,
                   agents=vehicles,
                   time=discretize_time(config.physics.start_time))

    def step(self) -> None:
        # For now, ignore intersections

        # Add all agents spawned at this timestep
        while self.agents[self.last_index].start_time <= self.time:
            self.active_agent_indexes.append(self.last_index)
            self.last_index += 1

        for agent_id in self.active_agent_indexes:
            agent = self.agents[agent_id]

            if agent.is_on_intersection():  # Immediately teleport agent to the next road segment
                current_journey_index = agent.path.index(agent.location)
                agent.location = (agent.path[current_journey_index], agent.path[current_journey_index + 1])
                road = self.environment.roads[agent.location]
                road.add_agent(agent_id=agent.id,
                               lane=randint(0, road.lanes),
                               length=agent.type.get_characteristic().length)

            elif agent.is_on_road():  # Check if on the next timestep the agent will touch the end of the road line
                road = self.environment.roads[agent.location]
                road.move_agent()
            else:
                agent.location = agent.from_node

        self.time += 1