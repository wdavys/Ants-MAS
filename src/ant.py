import math
import random
import numpy as np
from typing import Tuple, Union
from mesa import Agent, Model

from space import Point, euclidean, move
from marker import Marker, MarkerPurpose
import space


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
        colony,
        color: str,
        proba_cgt_angle=0.03,
        ignore_steps_after_marker=2,
    ):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.speed = speed
        self.angle = angle
        self.sight_distance = sight_distance
        self.proba_cgt_angle = proba_cgt_angle
        self.is_carrying = False
        self.is_on_food_marker = False
        self.ignore_markers_counts = 0
        self.ignore_steps_after_marker = ignore_steps_after_marker

    def next_pos(self) -> Tuple:
        next_x, next_y = move(self.x, self.y, self.speed, self.angle)
        return next_x, next_y

    def go_to(self, destination: Point) -> Tuple:
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

    def go_back_to_colony(self) -> Tuple:
        next_x, next_y, next_angle, reached = self.go_to(self.colony)

        if reached:
            self.colony.food_picked += 1
            self.is_carrying = False

        return next_x, next_y, next_angle

    def look_for_food(self):
        foods_at_sight = [
            food
            for food in self.model.foods
            if euclidean(food, self) < self.sight_distance
        ]
        if foods_at_sight:
            nearest_food = foods_at_sight[
                np.argmin([euclidean(self, food) for food in foods_at_sight])
            ]

            return nearest_food

    def look_for_food_marker(self) -> Union[Marker, None]:
        food_markers_at_sight = [
            marker
            for marker in self.model.markers
            if marker.purpose == MarkerPurpose.FOOD
        ]
        if food_markers_at_sight:
            nearest_food_marker = food_markers_at_sight[
                np.argmin([euclidean(self, marker) for marker in food_markers_at_sight])
            ]
            return nearest_food_marker

    def step(self):
        if self.is_carrying:
            # The ant is carrying food, it wants to go to the colony

            next_x, next_y, next_angle = self.go_back_to_colony()

        else:
            # The ant is looking for either food or markers

            if nearest_food := self.look_for_food() is not None:
                # The ant saw some food

                next_x, next_y, next_angle, food_reached = self.go_to(nearest_food)

                # The ant can already leave a food marker
                food_marker = Marker(
                    x=self.x,
                    y=self.y,
                    purpose=MarkerPurpose.FOOD,
                    directions=next_angle,
                )
                self.model.markers.append(food_marker)
                self.ignore_markers_counts += self.ignore_steps_after_marker

                if food_reached:
                    # The ant reached food, it take one piece and now try to go back to the colony

                    nearest_food.get_one_piece()
                    self.is_carrying = True

            else:
                # The ant did not see any food

                if self.ignore_markers_counts == 0 and (
                    nearest_food_marker := self.look_for_food_marker() is not None
                ):
                    # The ant is aware of markers and saw one

                    next_x, next_y, next_angle, marker_reached = self.go_to(
                        nearest_food_marker
                    )

                    if marker_reached:
                        self.is_on_food_marker = True  # TODO a quoi ça sert ?

                else:
                    # The ant did not see any food nor markers, it explores the environement

                    next_x, next_y = space.move(
                        x=self.x, y=self.y, speed=self.speed, angle=self.angle
                    )
                    next_angle = 2 * np.pi * random.random()

        # Update ant states
        self.x, self.y, self.angle = next_x, next_y, next_angle
        self.ignore_markers_counts = max(0, self.ignore_markers_counts - 1)

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
