import enum


class MarkerPurpose(enum.Enum):
    DANGER = enum.auto()
    FOOD = enum.auto()


class Marker:  # La classe pour les balises
    def __init__(self, x, y, purpose, directions):
        self.x = x
        self.y = y
        self.purpose = purpose
        if purpose == MarkerPurpose.FOOD:
            self.directions = directions

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Layer": 2,
            "Color": "red" if self.purpose == MarkerPurpose.DANGER else "green",
            "r": 2,
        }
        return portrayal
