from dataclasses import dataclass
from typing import Self, Any, Optional

import numpy as np
from shapely import LineString

from ainter.models.nagel_schreckenberg.units import discretize_length, PhysicalLength, DEFAULT_ROAD_MAX_SPEED, \
    PhysicalSpeed


@dataclass(slots=True, frozen=True)
class Road:
    osm_id: int
    grid: np.ndarray
    lanes: int
    max_speed: PhysicalSpeed
    name: Optional[str]
    oneway: bool
    reversed: bool
    length: PhysicalLength
    geometry: LineString

    @classmethod
    def from_graph_data(cls,
                        start_node_info: dict[str, Any],
                        end_node_info: dict[str, Any],
                        edge_info: dict[str, Any]) -> Self:

        osm_id = edge_info['osmid']
        lanes = int(edge_info.get('lanes', '1'))
        length = edge_info['length']
        cells_num = discretize_length(length.astype(np.float32))
        max_speed = float(edge_info.get('max_speed', DEFAULT_ROAD_MAX_SPEED))
        name = edge_info.get('name', None)
        is_oneway = edge_info['oneway']
        is_reversed = edge_info['reversed']
        geometry = edge_info.get('geometry', LineString(coordinates=[[start_node_info['x'], start_node_info['y']],
                                                                     [end_node_info['x'], end_node_info['y']]]))

        return cls(osm_id=osm_id,
                   grid=np.zeros(shape=(cells_num, lanes), dtype=np.uint8),
                   lanes=lanes,
                   max_speed=max_speed,
                   name=name,
                   oneway=is_oneway,
                   reversed=is_reversed,
                   length=length,
                   geometry=geometry)
