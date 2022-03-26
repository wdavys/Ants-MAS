import math
import uuid
import numpy as np
from mesa import Model

from src import ant, main

MODEL = Model()

def test_create_ant():
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        sight_distance=20,
        proba_cgt_angle=0.5
    )

def test_go_to_reachable():
    target = main.Point(7, 2)
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        sight_distance=20,
        proba_cgt_angle=0.5
    )
    next_x, next_y = 7., 2.
    reached = True
    
    (predicted_x, predicted_y), predicted_angle, predicted_reach = test_ant.go_to(target)
    
    assert next_x == predicted_x
    assert next_y == predicted_y
    assert reached == predicted_reach

def test_go_to_not_reachable():
    target = main.Point(10, 2)
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        sight_distance=20,
        proba_cgt_angle=0.5
    )
    next_x, next_y = 10., 0.
    next_angle = 0.1973
    reached = False

    (predicted_x, predicted_y), predicted_angle, predicted_reach = test_ant.go_to(target)
    
    assert next_x == predicted_x
    assert next_y == predicted_y
    assert reached == predicted_reach
    assert math.isclose(next_angle, predicted_angle, rel_tol=1e-3)