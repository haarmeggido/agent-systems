import json
from copy import deepcopy
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
from ainter.models.nagel_schreckenberg.units import get_time_density_strategy, discretize_time, TimeDensity, ROAD_COLOR, \
    discretize_length
from ainter.models.vehicles.vehicle import Vehicle, NULL_VEHICLE_ID
from test.ainter.test_fixtures import seed
from test.ainter.models.vehicles.test_vehicle import agent_type


def powerset(iterable):
    s = list(iterable)
    return chain.from_iterable(combinations(s, r) for r in range(len(s) + 1))

@pytest.fixture(params=['./test/resources/models/small_graph.json'])
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
                     vehicles=VehiclesConfig(time_density_strategy=get_time_density_strategy('null_dist'),
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

@pytest.mark.parametrize("agent_id", [1111, 1, 2, 987, 1223,])
@pytest.mark.parametrize("speed", [0, 1, 2, 5, 7, 10,])
def test_move_agent(road_json, agent_type, agent_id, speed):
    length = agent_type.get_characteristic().length
    assert not road_json.contains_agent(agent_id), "Road must be empty"

    for lane in range(road_json.lanes):
        color = np.zeros((3,), dtype=np.uint8)
        road_json.add_agent(agent_id, color, lane, length)

        assert road_json.contains_agent(agent_id), "Agent should be added"

        initial_positions = np.where(road_json.grid == agent_id)
        initial_start = initial_positions[0][0]
        initial_end = initial_start + length

        if initial_end + speed > road_json.grid.shape[0]:
            road_json.grid[:] = 0
            road_json.render_lut[:] = ROAD_COLOR
            continue

        road_json.move_agent(agent_id, speed)

        moved_positions = np.where(road_json.grid == agent_id)
        moved_start = moved_positions[0][0]
        moved_end = moved_start + length

        assert moved_start == initial_start + speed, f"Agent should move by {speed} cells"
        assert moved_end == initial_end + speed, f"End position should also move by {speed} cells"
        assert moved_end - moved_start == length, "Agent should have the same length"
        assert moved_positions[1][0] == lane, f"Lane should not change"

        road_json.grid[:] = NULL_VEHICLE_ID
        road_json.render_lut[:] = ROAD_COLOR

@pytest.mark.parametrize("road_grid,lane,agent_id,color,length,speed,expected", [
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
        0,
        7,
        np.array([0, 255, 0], dtype=np.uint8),
        4,
        0,
        np.array([[7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
        0,
        7,
        np.array([0, 255, 0], dtype=np.uint8),
        5,
        6,
        np.array([[0, 0, 0, 0, 0, 0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
        0,
        7,
        np.array([0, 255, 0], dtype=np.uint8),
        5,
        4,
        np.array([[0, 0, 0, 0, 7, 7, 7, 7, 7, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 0],], dtype=np.uint16).T,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        1,
        np.array([0, 255, 0], dtype=np.uint8),
        5,
        9,
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 3, 3, 3, 3, 3, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
    ),
])
def test_movement_from_start(road_json, road_grid, lane, agent_id, color, length, speed, expected):
    road_json.grid = deepcopy(road_grid)
    road_json.lanes = road_grid.shape[1]

    assert not road_json.contains_agent(agent_id), "Road must be empty"
    road_json.add_agent(agent_id, color, lane, length)

    assert road_json.contains_agent(agent_id), "Road must contain added agent"
    road_json.move_agent(agent_id, speed)

    assert np.all(road_json.grid == expected), "Grid must match expectations"

@pytest.mark.parametrize("road_grid,lane,agent_id,speed,expected", [
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        3,
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 2, 2, 2, 2, 0, 0],], dtype=np.uint16).T,
        0,
        2,
        2,
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 2, 2, 2, 2, 0, 0],], dtype=np.uint16).T,
        0,
        2,
        3,
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
    ),

])
def test_movement_any_start(road_json, road_grid, lane, agent_id, speed, expected):
    road_json.grid = deepcopy(road_grid)
    road_json.lanes = road_grid.shape[1]

    assert road_json.contains_agent(agent_id), "Road must contain added agent"
    road_json.move_agent(agent_id, speed)

    assert np.all(road_json.grid == expected), "Grid must match expectations"

@pytest.mark.parametrize("road_grid,lane,agent_id,expected", [
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 2, 2, 2, 2, 0, 0, 0],], dtype=np.uint16).T,
        0,
        2,
        3,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 2, 2, 2, 2, 0, 0],], dtype=np.uint16).T,
        0,
        2,
        2,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 2, 2, 2, 2, 0],], dtype=np.uint16).T,
        0,
        2,
        1,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        2,
        0,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        4,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        3,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        2,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 0, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        1,
    ),
    (
        np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 3, 3, 3, 3, 3, 2, 2, 2, 2],], dtype=np.uint16).T,
        0,
        3,
        0,
    ),
])
def test_get_agent_distance(road_json, road_grid, lane, agent_id, expected):
    road_json.grid = deepcopy(road_grid)
    road_json.lanes = road_grid.shape[1]

    assert road_json.contains_agent(agent_id), "Road must contain added agent"
    result = road_json.get_length_to_obstacle(agent_id)

    assert result == expected, "Distance must match"
