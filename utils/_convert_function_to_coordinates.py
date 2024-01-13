from typing import List
from typing import Union

from pyariadne import Function

from utils._coordinate import Coordinate


def convert_function_to_coordinates(n_variables: int, f: Union[str, Function]) -> List[Coordinate]:
    function_str = f if isinstance(f, str) else f.__crepr__()
    function_str = (
        function_str
        .replace("-", "+-")
        .replace("[", "")
        .replace("]", "")
        .replace(" ", "")
    )
    function_split_by_literals = function_str.split("+")
    function_as_coordinate = []
    for x in function_split_by_literals:
        x = x.lstrip("(").rstrip(")")
        coordinate = Coordinate(n_variables=n_variables, expression=x)
        if coordinate:
            function_as_coordinate.append(coordinate)

    return function_as_coordinate
