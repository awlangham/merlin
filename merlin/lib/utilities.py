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


def create_event_stream(node_name, path) -> bool:
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

    return stream_names


def clear_stream(node_name, stream_name) -> None:
    """
    Remove all events from the specified stream.
    """

    with get_joule_node(node_name) as node:
        asyncio.run(node.event_stream_remove(stream_name + '/events'))
