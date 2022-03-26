import math
import uuid
import numpy as np

from src import ant, space, environnement

MODEL = environnement.Ground(
    n_colony=2,
    n_ants_per_colony=2,
    color_ants="black",
    color_colonies="green",
    n_obstacles=5,
    n_food=2,
    speed=20,
)
COLONY = environnement.Colony(x=0, y=0, r=10, ants=10)


def test_create_ant():
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        colony=COLONY,
        color="black",
        sight_distance=20,
        proba_cgt_angle=0.5,
    )


def test_go_to_reachable():
    target = space.Point(7, 2)
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        colony=COLONY,
        color="black",
        sight_distance=20,
        proba_cgt_angle=0.5,
    )
    next_x, next_y = 7.0, 2.0
    reached = True

    (predicted_x, predicted_y), predicted_angle, predicted_reach = test_ant.go_to(
        target
    )

    assert next_x == predicted_x
    assert next_y == predicted_y
    assert reached == predicted_reach


def test_go_to_not_reachable():
    target = space.Point(10, 2)
    test_ant = ant.Ant(
        unique_id=uuid.uuid1(),
        model=MODEL,
        x=0,
        y=0,
        speed=10,
        angle=0,
        colony=COLONY,
        color="black",
        sight_distance=20,
        proba_cgt_angle=0.5,
    )
    next_x, next_y = 10.0, 0.0
    next_angle = 0.1973
    reached = False

    (predicted_x, predicted_y), predicted_angle, predicted_reach = test_ant.go_to(
        target
    )

    assert next_x == predicted_x
    assert next_y == predicted_y
    assert reached == predicted_reach
    assert math.isclose(next_angle, predicted_angle, rel_tol=1e-3)
