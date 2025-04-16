import joule
from joule.api import EventStream
from joule.errors import ApiError
from contextlib import contextmanager
import asyncio


@contextmanager
def get_joule_node(node_name):
    """
    Context manager for a Joule node handle.
    Automatically handles closing network resources.
    """

    node = joule.api.get_node(node_name)
    try:
        yield node
    finally:
        asyncio.run(node.close())


def async_run(func):
    """
    Decorator to run a coroutine and block until done.
    """

    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@async_run
async def create_event_stream(node_name, path) -> bool:
    """
    Create new event stream at [path]/events and return True.
    If one already exists, do nothing and return False.
    """

    async with get_joule_node(node_name) as node:
        try:
            await node.event_stream_get(f'{path}/events')
            return False
        except ApiError:
            new_stream = EventStream(name='events')
            await node.event_stream_create(new_stream, path)
            return True


def search_for_stream(node_name, stream_name) -> list:
    """
    Return list of Joule folder paths that include a stream named [stream_name].
    Checks both data streams and event streams.
    """

    stream_names, path = [], []

    def traverse_folder(folder):
        for child in folder.children:
            path.append(child.name)

            for stream in child.event_streams + child.data_streams:
                if stream.name == stream_name:
                    stream_names.append('/' + '/'.join(path))

            traverse_folder(child)
            path.pop()

    with get_joule_node(node_name) as node:
        root = asyncio.run(node.folder_root())
        traverse_folder(root)

    # await node.close()

    return stream_names


@async_run
async def clear_stream(node_name, stream_name) -> None:
    """
    Remove all events from the specified stream.
    """

    async with get_joule_node(node_name) as node:
        await node.event_stream_remove(stream_name + '/events')


def label_data(node_name, stream_name, intervals, label_name) -> None:
    """
    Apply the specified label to the events in the
    provided stream that correspond to the specified
    time intervals.
    """

    new_events = []
    with get_joule_node(node_name) as node:
        for interval in intervals:
            old_events = asyncio.run(node.event_stream_read(stream_name + '/events', start=interval[0], end=interval[1]))
            new_event = old_events[0]
            new_event.content['label'] = label_name
            new_events.append(new_event)
            # await node.event_stream_remove(stream_name + '/events', start=interval[0], end=interval[1])

        asyncio.run(node.event_stream_write(stream_name + '/events', new_events))
