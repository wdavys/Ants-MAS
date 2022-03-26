import math
import random
import numpy as np
from mesa import Agent, Model

from .main import Point
from .marker import MarkerPurpose


def move(x, y, speed, angle):
    return x + speed * math.cos(angle), y + speed * math.sin(angle)


def euclidean(p1: Point, p2: Point):
    return np.linalg.norm((p1.x - p2.x, p1.y - p2.y), ord=2)


class Ant(Agent):
    def __init__(
        self,
        unique_id: int,
        model: Model,
        x: float,
        y: float,
        speed: float,
        angle: float,
        sight_distance: float,
        proba_cgt_angle=0.03,
    ):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.sight_distance = sight_distance
        self.proba_cgt_angle = proba_cgt_angle
        self.angle = angle
        self.is_carrying = False
        self.is_on_food_marker = False

    def next_pos(self):
        next_x, next_y = move(self.x, self.y, self.speed, self.angle)
        return next_x, next_y

    def go_to(self, destination: Point):
        x = self.x
        y = self.y
        speed = self.speed
        dist_to_destination = euclidean(self, destination)
        reached = False

        if dist_to_destination < speed:
            next_x, next_y = destination.x, destination.y
            next_angle = 2 * math.pi * random.random()
            reached = True
            return (next_x, next_y), next_angle, reached

        else:
            next_angle = math.acos((destination.x - x) / dist_to_destination)
            if destination.y < y:
                next_angle = -next_angle
            return self.next_pos(), next_angle, reached

    def step(self):
        foods = [
            food
            for food in self.model.foods
            if euclidean(food, self) < self.sight_distance
        ]
        food_markers = [
            marker
            for marker in self.model.markers
            if marker.purpose == MarkerPurpose.FOOD
        ]
        if foods:
            nearest_food = foods[np.argmin([euclidean(self, food) for food in foods])]
            next_x, next_y, next_angle, reached = self.go_to(nearest_food)
        elif food_markers:
            nearest_food_marker = food_markers[
                np.argmin([euclidean(self, marker) for marker in food_markers])
            ]
            next_x, next_y, next_angle, reached = self.go_to(nearest_food_marker)
            if reached:
                self.is_on_food_marker = True

        self.x, self.y, self.angle = next_x, next_y, next_angle

    def portrayal_method(self):
        portrayal = {
            "Shape": "arrowHead",
            "s": 1,
            "Filled": "true",
            "Color": "Red",
            "Layer": 3,
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
        }
        return portrayal
