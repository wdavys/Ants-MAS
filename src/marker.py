import enum


class MarkerPurpose(enum.Enum):
    DANGER = enum.auto()
    FOOD = enum.auto()


class Marker:
    def __init__(self, x, y, purpose, directions, color):
        self.x = x
        self.y = y
        self.purpose = purpose
        self.color = color
        if purpose == MarkerPurpose.FOOD:
            self.directions = directions

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 2,
            "Color": self.color,
            "r": 2,
        }
        return portrayal
