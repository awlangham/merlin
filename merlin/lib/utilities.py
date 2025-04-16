import joule
from contextlib import contextmanager
import asyncio


@contextmanager
def get_joule_node(node_name: str):
    """
    Context manager for a Joule node handle.
    Automatically handles closing network resources.
    """

    node = joule.api.get_node(node_name)
    try:
        yield node
    finally:
        asyncio.run(node.close())


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
