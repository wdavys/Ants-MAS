import math
from click import Tuple
import numpy as np


class Point:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y

    def get_position(self) -> Tuple:
        return self.x, self.y


def move(x: float, y: float, speed: float, angle: float) -> Tuple:
    return x + speed * math.cos(angle), y + speed * math.sin(angle)


def euclidean(p1: Point, p2: Point) -> float:
    return np.linalg.norm((p1.x - p2.x, p1.y - p2.y), ord=2)
