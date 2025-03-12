from mesa import Model
from mesa.space import MultiGrid
from mesa.time import SimultaneousActivation
from models.intersection_manager import IntersectionManager
from models.vehicle import VehicleAgent
import random

class IntersectionModel(Model):
    def __init__(self, width=10, height=10, num_vehicles=4):
        super().__init__()
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = SimultaneousActivation(self)

        # Define intersection (4 middle squares)
        self.intersection_center = (5, 5)
        self.intersection_area = {(5, 5), (5, 6), (6, 5), (6, 6)}

        # Entry points for vehicles (fixed locations for clarity)
        self.entry_points = {
            "N": (5, 0),
            "S": (6, 9),
            "E": (9, 5),
            "W": (0, 6),
        }

        # Create Intersection Manager
        self.intersection_manager = IntersectionManager(99, self)
        self.schedule.add(self.intersection_manager)

        # Spawn vehicles at correct starting positions
        for i, (direction, pos) in enumerate(self.entry_points.items()):
            agent = VehicleAgent(i, self, direction)
            self.grid.place_agent(agent, pos)
            self.schedule.add(agent)

    def step(self):
        self.schedule.step()
