import asyncio
from functools import lru_cache
from .utilities import get_joule_node

import numpy as np


@lru_cache(maxsize=8192)
def read_single_transient(node_name: str, stream_name: str, interval_start: int, interval_end: int) -> np.array:
    """
    Read a single transient with across time interval [interval_start, interval_end].

    Recently viewed transients are cached in the back-end program with an LRU cache.
    """

    async def _read_from_pipe():
        pipe = await node.data_read(stream_name + '/transients', start=interval_start, end=interval_end)
        return await pipe.read_all(flatten=True)

    with get_joule_node(node_name) as node:
        sarray = asyncio.run(_read_from_pipe())
    return sarray


def read_multiple_transients(node_name: str, stream_name: str, intervals: list[tuple[int, int]]) -> list:
    """
    Return a list of the transients corresponding
    to the specified intervals in the provided stream.
    """

    transients = []
    for interval in intervals:
        sarray = read_single_transient(node_name, stream_name, interval[0], interval[1])
        transients.append(sarray.T)

    return transients
