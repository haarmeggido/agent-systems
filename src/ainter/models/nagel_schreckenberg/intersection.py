from dataclasses import dataclass
from typing import Self, Any

import numpy as np


@dataclass(slots=True, frozen=True)
class Intersection:
    osm_id: int
    grid: np.ndarray

    @classmethod
    def from_graph_data(cls, osm_id: int,
                        node_info: dict[str, Any]) -> Self:
        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(10, 10), dtype=np.uint16))
