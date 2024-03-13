import joule
from joule.api import EventStream
from joule.errors import ApiError
from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def get_node():
    node = joule.api.get_node()
    try:
        yield node
    finally:
        await node.close()


def async_run(func):
    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@async_run
async def search_for_stream(stream_name) -> list:
    stream_names, path = [], []

    def traverse_folder(folder):
        for child in folder.children:
            path.append(child.name)

            for stream in child.event_streams + child.data_streams:
                if stream.name == stream_name:
                    stream_names.append('/' + '/'.join(path))

            traverse_folder(child)
            path.pop()

    async with get_node() as node:
        root = await node.folder_root()
        traverse_folder(root)

    await node.close()

    return stream_names


def list_event_sources():
    return search_for_stream('events')


def list_transient_sources():
    return search_for_stream('transients')


@async_run
async def create_event_stream(path):
    async with get_node() as node:
        try:
            await node.event_stream_get(f'{path}/events')
            return False
        except ApiError:
            new_stream = EventStream(name='events')
            await node.event_stream_create(new_stream, path)
            return True
