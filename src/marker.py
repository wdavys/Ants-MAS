import enum

LIFETIME = 50
class MarkerPurpose(enum.Enum):
    DANGER = enum.auto()
    FOOD = enum.auto()


class Marker:
    def __init__(self, x, y, colony_id, purpose, direction, color):
        self.x = x
        self.y = y
        self.colony_id = colony_id
        self.purpose = purpose
        self.color = color
        self.lifetime = LIFETIME
        if purpose == MarkerPurpose.FOOD:
            self.direction = direction
    
    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 2,
            "Color": self.color,
            "r": 1,
        }
        return portrayal
