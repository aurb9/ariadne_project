from typing import Any


_allowed_scalars = [int, float]


def is_scalar(x: Any) -> bool:
    return type(x) in _allowed_scalars
