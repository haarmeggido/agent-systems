import json
from dataclasses import dataclass
from typing import Any, Self
from datetime import time

from ainter.models.nagel_schreckenberg.units import TimeDensity, get_time_density_strategy


@dataclass(slots=True, frozen=True)
class PhysicsConfig:
    start_time: time
    end_time: time

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self | str:
        if not ('start_time' in json_data and 'end_time' in json_data):
            return json_data

        return cls(start_time=time.fromisoformat(json_data['start_time']),
                   end_time=time.fromisoformat(json_data['end_time']))


@dataclass(slots=True, frozen=True)
class MapBoxConfig:
    left: float
    bottom: float
    right: float
    top: float

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self | dict[str, Any]:
        if not ('left' in json_data and 'bottom' in json_data and 'right' in json_data and 'top' in json_data):
            return json_data

        return cls(left=float(json_data['left']),
                   bottom=float(json_data['bottom']),
                   right=float(json_data['right']),
                   top=float(json_data['top']))

    def get_bbox(self) -> tuple[float, float, float, float]:
        return self.left, self.bottom, self.right, self.top


@dataclass(slots=True, frozen=True)
class VehiclesConfig:
    time_density_strategy: TimeDensity
    min_node_path_length: int

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self | dict[str, Any]:
        if not ('time_density_strategy' in json_data and 'min_node_path_length' in json_data):
            return json_data

        min_node_path_length = json_data['min_node_path_length']
        if min_node_path_length < 1:
            raise ValueError(f"{min_node_path_length=} cannot be zero-like or negative")

        return cls(time_density_strategy=get_time_density_strategy(json_data['time_density_strategy']),
                   min_node_path_length=min_node_path_length)


@dataclass(slots=True, frozen=True)
class EnvConfig:
    physics: PhysicsConfig
    map_box: MapBoxConfig
    vehicles: VehiclesConfig

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self | dict[str, Any]:
        if not ('physics' in json_data and 'map_box' in json_data and 'vehicles' in json_data):
            return json_data

        return cls(physics=PhysicsConfig.from_json(json_data['physics']),
                   map_box=MapBoxConfig.from_json(json_data['map_box']),
                   vehicles=VehiclesConfig.from_json(json_data['vehicles']))

def get_env_config_from_json(input_file) -> EnvConfig:
    data = json.load(input_file, object_hook=EnvConfig.from_json)
    assert isinstance(data, EnvConfig), 'Invalid data structure provided'

    return data
