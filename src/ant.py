import random
import numpy as np
from typing import Tuple
from mesa import Agent, Model
from space import Point, euclidean, move
from marker import Marker, MarkerPurpose

PROBA_CHGT_ANGLE = 0.3
MAX_MARKERS = np.inf
MAX_ITERATIONS = 100

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
        epsilon: float,
        proba_cgt_angle=PROBA_CHGT_ANGLE,
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
        self.color = color
        self.colony = colony
        self.epsilon = epsilon

    def next_pos(self) -> Tuple:
        next_x, next_y = move(self.x, self.y, self.speed, self.angle)
        return next_x, next_y

    def look_for_food(self):
        if foods_at_sight := [
            food
            for food in self.model.foods
            if euclidean(self, food) < self.sight_distance
        ]:
            nearest_food = foods_at_sight[
                np.argmin([euclidean(self, food) for food in foods_at_sight])
            ]

            return nearest_food

    def look_for_food_marker(self, back_to_colony=False):
        if back_to_colony:
            if food_markers_at_sight := [
                marker for marker in self.model.markers_dict[str(self.colony.id_colony)]
                if marker.purpose == MarkerPurpose.FOOD and \
                    np.array([self.x-self.colony.x, self.y-self.colony.y]) @ np.array([self.x-marker.x, self.y-marker.y])> 0
            ]:
                nearest_food_marker = food_markers_at_sight[
                    np.argmin([euclidean(self, marker) for marker in food_markers_at_sight])
                ]
                
                return nearest_food_marker
            
        else:
            if food_markers_at_sight := [
                marker for marker in self.model.markers_dict[str(self.colony.id_colony)]
                if marker.purpose == MarkerPurpose.FOOD
            ]:
                nearest_food_marker = food_markers_at_sight[
                    np.argmin([euclidean(self, marker) for marker in food_markers_at_sight])
                ]
                
                return nearest_food_marker
     
    def go_to(self, destination) -> Tuple:
        dist_to_destination = euclidean(self, destination)
        reached = False
        entering = dist_to_destination < destination.r if destination.__class__.__name__ in ["Food", "Colony"] else False
    
        if dist_to_destination < self.speed or entering:
            next_x, next_y = destination.x, destination.y
            next_angle = np.pi * (random.random()*2-1)
            reached = True
            return next_x, next_y, next_angle, reached
        
        else:
            next_angle = np.arccos((destination.x - self.x) / dist_to_destination)
            if destination.y < self.y:
                next_angle = -next_angle
            return *self.next_pos(), next_angle, reached
    
    def go_back_to_colony(self) -> Tuple:
        next_x, next_y, next_angle, reached = self.go_to(self.colony)

        if reached:
            self.colony.food_picked += 1
            self.is_carrying = False

        return next_x, next_y, next_angle

    def will_crash_with(self, object):
        '''
            Check if the ant will crash with ``object``.
            ``object`` is either an obstacle or another ant.
        '''
        pf = Point(*move(self.x, self.y, self.speed, self.angle))
        p0pf = np.array([pf.x - self.x, pf.y - self.y])
        p0pc = np.array([object.x - self.x, object.y - self.y])
        norm_p0pf = euclidean(self, pf)
        norm_p0pc = euclidean(self, object)
        prod = p0pf @ p0pc
        norm_p0ph = abs(prod/norm_p0pf)
        radius = object.speed if isinstance(object, Ant) else object.r

        if norm_p0ph>norm_p0pf:
            dist = euclidean(pf, object)
        elif prod<0:
            dist=np.inf
        #     dist = euclidean(p0, pc)
        else:
            dist = np.sqrt(norm_p0pc**2 - norm_p0ph**2)

        return dist<=radius

    def will_crash(self, objects):
        '''
            Check if the ant will crash with an element of ``objects``
        '''
        for obj in objects:
            if self.will_crash_with(obj):
                return True
        return False
    
    def step(self):
        ants = [ant for ant in self.model.schedule.agents if self != ant
                            and euclidean(self, ant) < self.sight_distance]
        obstacles = [obstacle for obstacle in self.model.obstacles
                        if euclidean(self, obstacle) < self.sight_distance]

        crash = self.model.space.out_of_bounds(self.next_pos())
        if not crash:
            crash = self.will_crash(ants) or self.will_crash(obstacles)
        
        iter = 0
        initial_angle = self.angle
        while crash and iter<MAX_ITERATIONS:
            # ---- Priority X.X ----
            # We try to avoid a crash with either any ant or any obstacle
            if iter%2:
                self.angle = initial_angle + (iter//2+1)*random.random()*2*np.pi
            else:
                self.angle = initial_angle - (iter//2+1)*random.random()*2*np.pi

            crash = self.model.space.out_of_bounds(self.next_pos())
            if not crash:
                crash = self.will_crash(ants) or self.will_crash(obstacles)
            iter += 1

        if crash:
            # The ant couldn't avoid a crash with an obstacle or an ant
            iter = 0
            while crash and iter<MAX_ITERATIONS:
                # ---- Priority X.X ----
                # At least it 
                if iter%2:
                    self.angle = initial_angle + (iter//2+1)*random.random()*2*np.pi
                else:
                    self.angle = initial_angle - (iter//2+1)*random.random()*2*np.pi

                crash = self.will_crash(obstacles)
                iter += 1

        if crash:
            # The ant didn't succeed in finding a convenient angle, it maintain its initial trajectory

            self.angle = initial_angle

        next_x, next_y, next_angle = *self.next_pos(), self.angle

        if self.is_carrying:
            # The ant is carrying food, it wants to go back to the colony
            # if False:#self.is_on_food_marker:
            #     if self.ignore_markers_counts == 0 and \
            #             (nearest_food_marker := self.look_for_food_marker(False)) is not None and random.random() < EPS:
            #             # The ant is aware of markers and saw one

            #         next_x, next_y, next_angle, marker_reached = self.go_to(nearest_food_marker)
            
            # else:
                # next_x, next_y, next_angle = self.go_back_to_colony()
                # if len(self.model.markers_dict[str(self.colony.id_colony)]) < MAX_MARKERS:
                #     food_marker = Marker(
                #         x=self.x,
                #         y=self.y,
                #         colony_id=self.colony.id_colony,
                #         purpose=MarkerPurpose.FOOD,
                #         direction=next_angle,
                #         color=self.colony.markers_colors[0],
                #     )
                #     self.model.markers_dict[str(self.colony.id_colony)].append(food_marker)
                #     self.ignore_markers_counts += self.ignore_steps_after_marker
            next_x, next_y, next_angle = self.go_back_to_colony()
            
            if len(self.model.markers_dict[str(self.colony.id_colony)]) < MAX_MARKERS:
                food_marker = Marker(
                    x=self.x,
                    y=self.y,
                    colony_id=self.colony.id_colony,
                    purpose=MarkerPurpose.FOOD,
                    direction=next_angle,
                    color=self.colony.markers_colors[self.colony.id_colony][0],
                )
                self.model.markers_dict[str(self.colony.id_colony)].append(food_marker)
                self.ignore_markers_counts += self.ignore_steps_after_marker

        else:
            # The ant is looking for either food or markers

            if (nearest_food := self.look_for_food()) is not None and random.random() < self.epsilon:
                # The ant saw some food and eager

                next_x, next_y, next_angle, food_reached = self.go_to(nearest_food)

                # The ant can already leave a food marker
                if len(self.model.markers_dict[str(self.colony.id_colony)]) < MAX_MARKERS:
                    food_marker = Marker(
                        x=self.x,
                        y=self.y,
                        colony_id=self.colony.id_colony,
                        purpose=MarkerPurpose.FOOD,
                        direction=next_angle,
                        color=self.colony.markers_colors[self.colony.id_colony][0]
                    )
                    self.model.markers_dict[str(self.colony.id_colony)].append(food_marker)
                    self.ignore_markers_counts += self.ignore_steps_after_marker

                if food_reached:
                    # The ant reached food, it take one piece and now try to go back to the colony

                    nearest_food.get_one_piece()
                    self.is_carrying = True

            else:
                # The ant did not see any food
                
                if self.ignore_markers_counts == 0 and \
                    (nearest_food_marker := self.look_for_food_marker()) is not None and random.random() < self.epsilon:
                    # The ant is aware of markers and saw one

                    next_x, next_y, next_angle, marker_reached = self.go_to(nearest_food_marker)

                    if marker_reached:
                        self.is_on_food_marker = True

                else:
                    # The ant did not see any food nor markers, it explores the environement

                    next_x, next_y = self.next_pos()
                    next_angle = np.pi * (random.random()*2-1)

        # Update ant states
        self.x, self.y, self.angle = next_x, next_y, next_angle
        self.ignore_markers_counts = max(0, self.ignore_markers_counts - 1)

    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Color": self.color,
            "Layer": 3,
            "r": 3
            #"Shape": "arrowHead"
            #"heading_x": np.cos(self.angle),
            #"heading_y": np.sin(self.angle),
            #"scale": .5
            # Bizarrement ça ne fonctionne pas avec arrowHead et j'ai pris du temps pour m'en rendre compte...
        }
        return portrayal

class Warrior(Ant):
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
        lifespan: int, 
        proba_cgt_angle=PROBA_CHGT_ANGLE, 
        ignore_steps_after_marker=2):
        
        super().__init__(unique_id, model, x, y, speed, angle, sight_distance, colony, color, proba_cgt_angle, ignore_steps_after_marker)
        self.lifespan = lifespan
 
    def next_pos(self) -> Tuple:
        return super().next_pos()
    
    def go_to(self, destination) -> Tuple:
        return super().go_to(destination)
    
    def go_back_to_colony(self) -> Tuple:
        return super().go_back_to_colony()
    
    def will_crash(self, objects):
        return super().will_crash(objects)
    
    def look_for_ant(self):
        if ants_at_sight := [
            ant
            for ant in self.model.schedule.agents
            if ant.__class__.__name__ == "Ant" and ant.colony.id_colony != self.colony.id_colony and euclidean(self, ant) < self.sight_distance
        ]:
            nearest_ant = ants_at_sight[
                np.argmin([euclidean(self, ant) for ant in ants_at_sight])
            ]

            return nearest_ant

    def step(self):
        obstacles = [obstacle for obstacle in self.model.obstacles
                        if euclidean(self, obstacle)<self.sight_distance]

        crash = self.model.space.out_of_bounds(self.next_pos())
        if not crash:
            crash = self.will_crash(obstacles)
        
        iter = 0
        initial_angle = self.angle
        while crash and iter<MAX_ITERATIONS:
            # ---- Priority X.X ----
            # We try to avoid a crash with any obstacle
            if iter%2:
                self.angle = initial_angle + (iter//2+1)*random.random()*2*np.pi
            else:
                self.angle = initial_angle - (iter//2+1)*random.random()*2*np.pi

            crash = self.model.space.out_of_bounds(self.next_pos())
            if not crash:
                crash = self.will_crash(obstacles)
            iter += 1

        if crash:
            # The ant didn't succeed in finding a convenient angle, it maintain its initial trajectory

            self.angle = initial_angle

        next_x, next_y, next_angle = *self.next_pos(), self.angle
        
        if (nearest_ant := self.look_for_ant()) is not None:
            next_x, next_y, next_angle, reached = self.go_to(nearest_ant)

            if reached:
                if len(self.model.markers_dict[str(nearest_ant.colony.id_colony)]) < MAX_MARKERS:
                    danger_marker = Marker(
                        x=nearest_ant.x,
                        y=nearest_ant.y,
                        colony_id=nearest_ant.colony.id_colony,
                        purpose=MarkerPurpose.DANGER,
                        direction=nearest_ant.angle,
                        color=nearest_ant.colony.markers_colors[nearest_ant.colony.id_colony][1]
                    )
                    self.model.markers_dict[str(nearest_ant.colony.id_colony)].append(danger_marker)
                    self.ignore_markers_counts += self.ignore_steps_after_marker
                    
                self.model.schedule.remove(nearest_ant)
                self.model.colonies[nearest_ant.colony.id_colony].ants.remove(nearest_ant)
                self.lifespan -= 1
                self.go_back_to_colony()

        else:
            next_x, next_y = self.next_pos()
            next_angle = np.pi * (random.random()*2-1)
            
        self.x, self.y, self.angle = next_x, next_y, next_angle
       
    def portrayal_method(self):
        portrayal = {
            "Shape": "circle",
            "Filled": "true",
            "Color": self.color,
            "Layer": 3,
            "r": 5
            #"Shape": "arrowHead"
            #"heading_x": np.cos(self.angle),
            #"heading_y": np.sin(self.angle),
            #"scale": .5
            # Bizarrement ça ne fonctionne pas avec arrowHead et j'ai pris du temps pour m'en rendre compte...
        }
        return portrayal