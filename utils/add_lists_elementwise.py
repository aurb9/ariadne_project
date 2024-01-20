from typing import List


def add_lists_elementwise(list1: List[int], list2: List[int]) -> List[int]:
    min_len = min(len(list1), len(list2))
    result = [list1[x] + list2[x] for x in range(min_len)]
    result += list1[min_len:]
    result += list2[min_len:]

    return result
