import joule
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
    def wrapper():
        return asyncio.run(func())
    return wrapper


@async_run
async def list_event_sources():
    stream_names, path = [], []

    def traverse_folder(folder):
        for child in folder.children:
            path.append(child.name)

            prep_exists, events_exists = False, False

            for data_stream in child.data_streams:
                if data_stream.name == 'prep':
                    prep_exists = True

            for event_stream in child.event_streams:
                if event_stream.name == 'events':
                    events_exists = True

            if prep_exists and events_exists:
                stream_names.append('/' + '/'.join(path))

            traverse_folder(child)
            path.pop()

    async with get_node() as node:
        root = await node.folder_root()
        traverse_folder(root)

    await node.close()

    return stream_names
