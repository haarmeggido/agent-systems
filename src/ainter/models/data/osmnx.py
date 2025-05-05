import networkx as nx
import osmnx as ox
from networkx.classes import DiGraph

from ainter.configs.env_creation import MapBoxConfig


def get_data_from_bbox(config: MapBoxConfig) -> nx.MultiDiGraph:
    return ox.graph.graph_from_bbox(bbox=config.get_bbox(),
                                    network_type='drive')

def bfs_shortest_path(graph: DiGraph, source: int, target: int) -> list[int]:
    return nx.shortest_path(graph, source=source, target=target, weight='length')
