from typing import Set
from typing import Tuple


def get_joint_and_disjoint_sets(x: Set, y: Set) -> Tuple[Set, Set, Set]:
    joint = x.intersection(y)
    disjoint_x = x - joint
    disjoint_y = y - joint

    return joint, disjoint_x, disjoint_y
