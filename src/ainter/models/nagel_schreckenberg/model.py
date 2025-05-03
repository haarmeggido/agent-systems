from dataclasses import dataclass
from typing import Self

from ainter.configs.env_creation import EnvConfig
from ainter.models.data.osmnx import get_data_from_bbox
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.vehicles.vehicle import Vehicle


@dataclass(slots=True)
class Model:
    environment: Environment
    agents: list[Vehicle]

    @classmethod
    def from_config(cls, config: EnvConfig) -> Self:
        graph = get_data_from_bbox(config.map_box)
        env = Environment.from_directed_graph(graph)
        vehicles = [Vehicle.from_random() for _ in range(config.vehicles.max_count)]
        return cls(environment=env,
                   agents=vehicles)
