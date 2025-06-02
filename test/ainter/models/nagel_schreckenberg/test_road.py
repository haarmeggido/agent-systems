import json
from datetime import time
from itertools import chain, combinations

import networkx as nx
import numpy as np
import pytest
from mesa import Model
from shapely import LineString

from ainter.configs.env_creation import EnvConfig, PhysicsConfig, VehiclesConfig, MapBoxConfig
from ainter.models.nagel_schreckenberg.environment import Environment
from ainter.models.nagel_schreckenberg.model import NaSchUrbanModel
from ainter.models.nagel_schreckenberg.road import Road
from ainter.models.nagel_schreckenberg.units import get_time_density_strategy, discretize_time, TimeDensity, ROAD_COLOR
from ainter.models.vehicles.vehicle import Vehicle, NULL_VEHICLE_ID
from test.ainter.test_fixtures import seed
from test.ainter.models.vehicles.test_vehicle import agent_type


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

@pytest.fixture(params=['./test/resources/small_graph.json'])
def graph(request):
    with open(request.param, "r", encoding='utf-8') as in_file:
        data = json.load(in_file)

    for edge in data["edges"]:
        edge["geometry"] = LineString(edge["geometry"])

    graph = nx.node_link_graph(data, edges="edges")
    return graph

@pytest.fixture
def env_config(monkeypatch):
    return EnvConfig(physics=PhysicsConfig(start_time=time.fromisoformat('08:00:00'),
                                           end_time=time.fromisoformat('20:00:00')),
                     vehicles=VehiclesConfig(time_density_strategy=get_time_density_strategy("null_dist"),
                                             min_node_path_length=1),
                     map_box=MapBoxConfig(left=0.0,
                                          bottom=0.0,
                                          right=0.0,
                                          top=0.0))


@pytest.fixture
def dummy_model(monkeypatch, graph, env_config, seed):
    def mock_model_init(self, env_config, seed):
        Model.__init__(self, seed=seed)

        self.graph = graph
        self.grid = Environment.from_directed_graph(self.graph)

        self.time = discretize_time(env_config.physics.start_time)
        self.end_time = discretize_time(env_config.physics.end_time)

        self.agent_spawn_probability: TimeDensity = env_config.vehicles.time_density_strategy

        self.min_node_path_length = env_config.vehicles.min_node_path_length

        self.running = True

    monkeypatch.setattr(NaSchUrbanModel, "__init__", mock_model_init)
    model = NaSchUrbanModel(env_config=env_config, seed=seed)

    return model

@pytest.fixture(params=[
    './test/resources/roads/road1.json',
    './test/resources/roads/road2.json',
    './test/resources/roads/road3.json',
    './test/resources/roads/road4.json',
    './test/resources/roads/road5.json',
    './test/resources/roads/road6.json',
    './test/resources/roads/road7.json',
    './test/resources/roads/road8.json',
])
def road_json(request):
    with open(request.param, "r", encoding='utf-8') as in_file:
        data = json.load(in_file)

    data["geometry"] = LineString(data["geometry"])

    road = Road.from_graph_data(dict(x=0.0, y=0.0), dict(x=1.0, y=1.0), data)
    return road

def test_road(dummy_model, agent_type):
    path = list(nx.topological_sort(nx.DiGraph(dummy_model.graph)))
    agent = Vehicle(model=dummy_model,
                    vehicle_type=agent_type,
                    path=path)

    assert agent.is_on_intersection(), "Agent must start at the intersection"
    assert all(map(lambda x: np.all(x.grid == 0), dummy_model.grid.roads.values())), "Road must be empty"
    agent.step()
    road = dummy_model.grid.roads[agent.pos]
    assert agent.is_on_road(), "Agent must be on road"
    assert road.contains_agent(agent.unique_id), "Road must contain agent"


@pytest.mark.parametrize("color", [
    np.array([0, 0, 255], dtype=np.uint8),
    np.array([0, 255, 0], dtype=np.uint8),
    np.array([255, 0, 0], dtype=np.uint8),
])
def test_remove_agent(seed, road_json, color):
    agent_ids = [1, 2, 8, 9, 10, 100, 1000, 765, 4562]
    rng = np.random.RandomState(seed)
    length = 5

    assert np.all(road_json.render_lut == ROAD_COLOR), "Lut should be empty"
    assert np.all(road_json.grid == 0), "Road should be empty"

    for possible_lane_assigment in powerset(range(road_json.lanes)):
        if not possible_lane_assigment:
            continue

        agent_indices = rng.choice(len(agent_ids), size=len(possible_lane_assigment), replace=False)
        selected_agents = [agent_ids[i] for i in agent_indices]

        for agent_id, lane_num in zip(selected_agents, possible_lane_assigment):
            road_json.add_agent(agent_id, color, lane_num, length)
            assert road_json.contains_agent(agent_id), f"Agent {agent_id} should be added"

        for agent_id in selected_agents:
            road_json.remove_agent(agent_id)
            assert not road_json.contains_agent(agent_id), f"Agent {agent_id} should be removed"

        assert np.all(road_json.grid == NULL_VEHICLE_ID), "Road should be empty"

        road_json.render_lut[:] = ROAD_COLOR
        road_json.grid[:] = NULL_VEHICLE_ID
