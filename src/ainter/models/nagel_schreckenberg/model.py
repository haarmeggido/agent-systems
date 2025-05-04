from dataclasses import dataclass
from typing import Self

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.units import discretize_time
from ainter.models.vehicles.vehicle import Vehicle, generate_vehicles


@dataclass(slots=True)
class Model:
    environment: Environment
    agents: list[Vehicle]

    @classmethod
    def from_config(cls, config: EnvConfig) -> Self:
        graph = get_data_from_bbox(config.map_box)
        env = Environment.from_directed_graph(graph)
        vehicles = generate_vehicles(graph,
                                     discretize_time(config.physics.start_time),
                                     discretize_time(config.physics.end_time),
                                     config.vehicles.time_density_strategy)
        return cls(environment=env,
                   agents=vehicles)

    def update_simulation(self) -> None:
        pass
