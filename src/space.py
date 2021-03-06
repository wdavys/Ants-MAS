from click import Tuple
import numpy as np


class Point:
    def __init__(self, x: float, y: float):
        self.x, self.y = x, y


def move(x: float, y: float, speed: float, angle: float) -> Tuple:
    return x + speed * np.cos(angle), y + speed * np.sin(angle)


def euclidean(p1, p2) -> float:
    return np.linalg.norm((p1.x - p2.x, p1.y - p2.y), ord=2)
