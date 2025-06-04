from dataclasses import dataclass
from typing import Self, Any

import networkx as nx
from networkx.classes import MultiDiGraph, DiGraph
from shapely import LineString

from ainter.models.nagel_schreckenberg.intersection import Intersection
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.nagel_schreckenberg.units import DEFAULT_ROAD_MAX_SPEED, DiscreteTime
from ainter.models.vehicles.vehicle import RoadPosition, IntersectionPosition


def enrich_edge_data(edge_data: dict[str, Any], start_node_data: dict[str, Any], end_node_data: dict[str, Any])-> None:
    if 'geometry' not in edge_data:
        edge_data['geometry'] = LineString(coordinates=[[start_node_data['x'], start_node_data['y']],
                                                        [end_node_data['x'], end_node_data['y']]])
    edge_data['lanes'] = int(edge_data.get('lanes', '1'))
    edge_data['name'] = edge_data.get('name', '')
    edge_data['name'] = 'Unnamed Street' if edge_data['name'] == '' else edge_data['name']
    edge_data['max_speed'] = float(edge_data.get('max_speed', DEFAULT_ROAD_MAX_SPEED))

def enrich_with_defaults(graph: nx.DiGraph) -> nx.DiGraph:
    for start_id, end_id in graph.edges:
        start_node_data = graph.nodes[start_id]
        end_node_data = graph.nodes[end_id]
        edge_data = graph.edges[start_id, end_id]
        enrich_edge_data(edge_data, start_node_data, end_node_data)

    return graph

def create_roads_from_graph(graph: MultiDiGraph, graph_di: DiGraph) -> dict[tuple[int, int], Road]:
    roads = dict()
    for start_id, end_id in graph_di.edges:
        start_data = graph.nodes[start_id]
        end_data = graph.nodes[end_id]
        edge_data = graph_di.edges[start_id, end_id]
        new_road = Road.from_graph_data(start_node_info=start_data,
                                        end_node_info=end_data,
                                        edge_info=edge_data)
        roads.update({(start_id, end_id): new_road})
    return roads

def create_intersections_from_graph(graph_di: DiGraph, global_time: DiscreteTime) -> dict[int, Intersection]:
    intersections = dict()
    for node_id in graph_di.nodes:
        node_data = graph_di.nodes[node_id]
        edges_data = {edge: graph_di.edges[edge]
                      for edge in set(graph_di.in_edges(node_id)) | set(graph_di.out_edges(node_id))}

        new_intersection = Intersection.from_graph_data(osm_id=node_id,
                                                        edges_info=edges_data,
                                                        node_info=node_data,
                                                        global_time=global_time)
        intersections.update({node_id: new_intersection})
    return intersections


@dataclass(slots=True)
class Environment:
    road_graph: DiGraph
    intersections: dict[IntersectionPosition, Intersection]
    roads: dict[RoadPosition, Road]

    @classmethod
    def from_directed_graph(cls, graph: MultiDiGraph, global_time: DiscreteTime) -> Self:
        assert all(map(lambda x: x[2] == 0, graph.edges)), 'The convertion to DiGraph would result in information loss'

        graph_di = DiGraph(graph)
        graph_di = enrich_with_defaults(graph_di)

        roads = create_roads_from_graph(graph, graph_di)
        intersections = create_intersections_from_graph(graph_di, global_time)

        return cls(road_graph=graph_di,
                   roads=roads,
                   intersections=intersections)
