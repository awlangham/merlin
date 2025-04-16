import asyncio
from .utilities import get_joule_node


def get_events(node_name: str, stream_name: str, start: int = None, end: int = None) -> list:
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
