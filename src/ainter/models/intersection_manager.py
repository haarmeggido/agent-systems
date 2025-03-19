from mesa import Agent

class IntersectionManager(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.queue = []
        self.current_vehicle = None

    def request_entry(self, vehicle):
        """ Vehicles request to cross; only one allowed at a time. """
        if vehicle not in self.queue:
            self.queue.append(vehicle)

    def can_enter(self, vehicle):
        """ Check if intersection is clear for a new vehicle. """
        return self.current_vehicle is None  # Only one vehicle at a time

    def step(self):
        """ Manage intersection crossing. """
        if self.current_vehicle and self.current_vehicle.state == "exited":
            self.current_vehicle = None

        if not self.current_vehicle and self.queue:
            self.current_vehicle = self.queue.pop(0)
            self.current_vehicle.state = "crossing"
