from joule.api import EventStream
from joule.errors import ApiError
import asyncio
from .utilities import get_joule_node


def read_events(node_name: str, stream_name: str, start: int = None, end: int = None) -> list:
    """
    Return a list of all events in the specified stream in the interval [start, end].

    A maximum of 1000 events are returned. If start is None, the last 1000 are returned.
    If end is None, the first 1000 are returned.
    """

    with get_joule_node(node_name) as node:
        return asyncio.run(node.event_stream_read(stream_name + '/events', start=start, end=end, limit=1000))


def label_events(node_name: str, stream_name: str, intervals: list[tuple[int, int]], label_name: str) -> None:
    """
    Apply the specified label to the events in the
    provided stream that correspond to the specified
    time intervals.
    """

    async def _apply_labels():
        new_events = []
        for interval in intervals:
            old_events = await node.event_stream_read(stream_name + '/events', start=interval[0], end=interval[1])
            new_event = old_events[0]
            new_event.content['label'] = label_name
            new_events.append(new_event)
            # await node.event_stream_remove(stream_name + '/events', start=interval[0], end=interval[1])

        await node.event_stream_write(stream_name + '/events', new_events)

    with get_joule_node(node_name) as node:
        asyncio.run(_apply_labels())


def create_event_stream(node_name: str, path: str) -> bool:
    """
    Create new event stream at [path]/events and return True.
    If one already exists, do nothing and return False.
    """

    with get_joule_node(node_name) as node:
        try:
            asyncio.run(node.event_stream_get(f'{path}/events'))
            return False
        except ApiError:
            new_stream = EventStream(name='events')
            asyncio.run(node.event_stream_create(new_stream, path))
            return True


def clear_event_stream(node_name: str, stream_name: str) -> None:
    """
    Remove all events from the specified stream.
    """

    with get_joule_node(node_name) as node:
        asyncio.run(node.event_stream_remove(stream_name + '/events'))
