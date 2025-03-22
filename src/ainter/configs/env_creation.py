from dataclasses import dataclass
from typing import Any, Self


@dataclass(slots=True, frozen=True)
class EnvConfig:
    left: float
    bottom: float
    right: float
    top: float

    @classmethod
    def from_json(cls, json_data: dict[str, Any]) -> Self:
        return cls(left=float(json_data['left']),
                   bottom=float(json_data['bottom']),
                   right=float(json_data['right']),
                   top=float(json_data['top']))
