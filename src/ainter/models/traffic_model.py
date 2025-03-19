from mesa import Model
from mesa.space import MultiGrid
from mesa.time import RandomActivation
from ainter.models.vehicle import VehicleAgent
from ainter.models.intersection_manager import IntersectionManager

class TrafficModel(Model):
    def __init__(self, width=10, height=10, num_vehicles=4):
        self.grid = MultiGrid(width, height, torus=False)
        self.schedule = RandomActivation(self)

        self.intersection_area = {(5, 5), (5, 6), (6, 5), (6, 6)}
        self.intersection_center = (5, 5)

        # Define entry points
        self.entry_points = {
            "N": (5, 0),
            "S": (6, 9),
            "E": (9, 5),
            "W": (0, 6),
        }

        # Add vehicles at predefined locations
        for i, (dir, pos) in enumerate(self.entry_points.items()):
            vehicle = VehicleAgent(i, self, dir)
            self.schedule.add(vehicle)
            self.grid.place_agent(vehicle, pos)

        self.intersection_manager = IntersectionManager(99, self)
        self.schedule.add(self.intersection_manager)

    def step(self):
        self.schedule.step()