import asyncio
from .utilities import get_joule_node


def get_events(node_name, stream_name, start=None, end=None) -> list:
    """
    Return a list of all events in the specified stream.
    """

    with get_joule_node(node_name) as node:
        return asyncio.run(node.event_stream_read(stream_name + '/events', start=start, end=end, limit=1000))
