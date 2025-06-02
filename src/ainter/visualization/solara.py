import math
from typing import Optional, Any

import matplotlib.pyplot as plt
import networkx as nx
import osmnx as ox
import solara
from mesa.visualization import SolaraViz
from mesa.visualization.utils import update_counter

from ainter.configs.env_creation import EnvConfig, VehiclesConfig
from ainter.models.nagel_schreckenberg.model import NaSchUrbanModel

plt.rcParams['axes.facecolor'] = 'none'
plt.rcParams['figure.facecolor'] = 'none'

shared_env_config: Optional[dict[str, Any]] = None

def set_environment_config(env_config: EnvConfig) -> None:
    global shared_env_config
    shared_env_config = {
        "seed": {
            "type": "InputText",
            "value": 69,
            "label": "Random Seed",
        },
        "time_density_strategy": {
            "type": "Select",
            "value": env_config.vehicles.time_density_strategy_code,
            "label": "Time Density Strategy",
            "values": ["normal_dist", "uniform_dist", "null_dist"],
        },
        "env_config": env_config,
        # "n": {
        #     "type": "SliderInt",
        #     "value": 50,
        #     "label": "Number of agents:",
        #     "min": 10,
        #     "max": 100,
        #     "step": 1,
        # },
    }

@solara.component
def network_portrayal(model):
    update_counter.get()
    fig, axis = ox.plot_graph(nx.MultiDiGraph(model.grid.road_graph),
                              figsize=(10, 4),
                              save=True,
                              show=False,
                              bgcolor='none',
                              node_color='blue',
                              edge_color='black',
                              node_size=65)

    for edge_data in model.grid.roads.values():
        text = edge_data.name
        c = edge_data.geometry.centroid
        axis.annotate(text, (c.x, c.y), c="blue", ha='center', va='center')

    for node_id, node_data in model.grid.intersections.items():
        text = str(node_id)
        axis.annotate(text, (node_data.x, node_data.y), c="orange", ha='center', va='center')

    fig.tight_layout()
    solara.FigureMatplotlib(fig)

@solara.component
def intersections_portrayal(model) -> None:
    update_counter.get()

    intersections_dict = model.grid.intersections
    roads_dict = model.grid.roads
    road_graph = model.grid.road_graph

    num_intersections = len(intersections_dict)
    cols = 3
    rows = math.ceil(num_intersections / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten()

    for i, (intersection_id, intersection_data) in enumerate(intersections_dict.items()):
        if i >= len(axes):
            break

        ax = axes[i]
        ax.imshow(intersection_data.render(), cmap="viridis", interpolation='nearest')
        ax.set_title(f"{','.join(map(lambda x: str(roads_dict[intersection_id, x].name), road_graph.adj[intersection_id].keys()))}\n({intersection_id})",
                     fontsize=11)
        ax.axis('off')

    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    plt.tight_layout()
    solara.FigureMatplotlib(fig)

@solara.component
def roads_portrayal(model) -> None:
    update_counter.get()
    roads_dict = model.grid.roads

    num_roads = len(roads_dict)
    cols = 1
    rows = math.ceil(num_roads / cols)
    max_x_length = 0
    max_x_len_id = 0
    max_y_length = 0
    max_y_len_id = 0

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 12, rows * 1))
    axes = axes.flatten()

    for i, ((road_start_id, road_end_id), road_data) in enumerate(roads_dict.items()):
        if i >= len(axes):
            break

        if max_x_length < road_data.length:
            max_x_length = road_data.length
            max_x_len_id = i

        if max_y_length < road_data.lanes:
            max_y_length = road_data.lanes
            max_y_len_id = i

        ax = axes[i]
        ax.imshow(road_data.render(), cmap="viridis", interpolation='nearest')
        ax.set_title(f"{road_data.name}, {float(road_data.length):.1f}m ({road_start_id} -> {road_end_id})",
                     fontsize=11)
        ax.axis('off')


    for j in range(i + 1, len(axes)):
        fig.delaxes(axes[j])

    for axi in axes:
        ax_max_x = axes[max_x_len_id]
        ax_max_y = axes[max_y_len_id]
        axi.set_ylim(ax_max_y.get_ylim())
        axi.set_xlim(ax_max_x.get_xlim())

    plt.tight_layout()
    solara.FigureMatplotlib(fig)

@solara.component
def page() -> None:
    if shared_env_config is None:
        raise ValueError("Environment config not set. Please call `set_environment_config(...)` first.")

    seed = int(shared_env_config["seed"]["value"])
    strategy_code = shared_env_config["time_density_strategy"]["value"]

    env_config: EnvConfig = shared_env_config["env_config"]
    updated_vehicles_config = VehiclesConfig(
        time_density_strategy_code=strategy_code,
        min_node_path_length=env_config.vehicles.min_node_path_length
    )
    updated_env_config = EnvConfig(
        physics=env_config.physics,
        map_box=env_config.map_box,
        vehicles=updated_vehicles_config
    )

    model = NaSchUrbanModel(updated_env_config, seed=seed)

    SolaraViz(
        model,
        components=[
            network_portrayal,
            roads_portrayal,
            intersections_portrayal,
        ],
        model_params = {
            "seed": {
                "type": "InputText",
                "value": seed,
                "label": "Random Seed"
            },
            "time_density_strategy": {
                "type": "Select",
                "value": strategy_code,
                "label": "Time Density Strategy",
                "values": ["normal_dist", "uniform_dist", "null_dist"]
            },
            "env_config": updated_env_config
        },
        name="Autonomous Intersection Model",
    )

    # plt.close('all')

routes = [
    solara.Route(path="/", component=page, label="Agent Model"),
]
