from mesa import Agent

class VehicleAgent(Agent):
    def __init__(self, unique_id, model, direction, speed=1):
        super().__init__(unique_id, model)
        self.direction = direction
        self.speed = speed
        self.state = "approaching"  # States: approaching, waiting, crossing, exited

    def move(self):
        x, y = self.pos
        new_pos = self.get_next_pos(x, y)

        # If still approaching, keep moving toward the intersection
        if self.state == "approaching":
            if new_pos not in self.model.intersection_area:
                self.model.grid.move_agent(self, new_pos)
            else:
                self.state = "waiting"
                self.model.intersection_manager.request_entry(self)

        # If crossing, keep moving and check when it exits the intersection
        elif self.state == "crossing":
            if new_pos not in self.model.intersection_area:
                self.state = "exited"
            self.model.grid.move_agent(self, new_pos)

        # If exited, continue moving until out of bounds
        elif self.state == "exited":
            if self.is_out_of_bounds(new_pos):
                self.model.grid.remove_agent(self)
                self.model.schedule.remove(self)
            else:
                self.model.grid.move_agent(self, new_pos)

    def get_next_pos(self, x, y):
        """ Move in the correct lane and follow right-side traffic. """
        if self.direction == "N":
            return (x, y + self.speed)  # Move up
        elif self.direction == "S":
            return (x, y - self.speed)  # Move down
        elif self.direction == "E":
            return (x - self.speed, y)  # Move left 
        elif self.direction == "W":
            return (x + self.speed, y)  # Move right 
        return (x, y)

    def is_out_of_bounds(self, pos):
        """ Check if position is outside the grid. """
        x, y = pos
        return x < 0 or x >= self.model.grid.width or y < 0 or y >= self.model.grid.height

    def step(self):
        self.move()
