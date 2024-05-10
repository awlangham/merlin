import numpy as np
import joule
from joule.api import EventStream
from joule.errors import ApiError
from contextlib import asynccontextmanager
import asyncio


@asynccontextmanager
async def get_joule_node():
    """
    Context manager for a Joule node handle.
    Automatically handles closing network resources.
    """

    node = joule.api.get_node()
    try:
        yield node
    finally:
        await node.close()


def async_run(func):
    """
    Decorator to run a coroutine and block until done.
    """

    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))
    return wrapper


@async_run
async def create_event_stream(path):
    """
    Create new event stream at [path]/events and return True.
    If one already exists, do nothing and return False.
    """

    async with get_joule_node() as node:
        try:
            await node.event_stream_get(f'{path}/events')
            return False
        except ApiError:
            new_stream = EventStream(name='events')
            await node.event_stream_create(new_stream, path)
            return True


@async_run
async def search_for_stream(stream_name) -> list:
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

    async with get_joule_node() as node:
        root = await node.folder_root()
        traverse_folder(root)

    await node.close()

    return stream_names


@async_run
async def clear_stream(stream_name) -> None:
    async with get_joule_node() as node:
        await node.event_stream_remove(stream_name + '/events')


def mapping(x):
    # 0 is good, 1 is neutral, inf is bad

    # fix for floating point
    x_shifted = x + 1
    close_to_zero = np.isclose(x_shifted, 0)
    x_shifted[close_to_zero] = 0

    with np.errstate(divide='ignore'):
        return np.divide(2, x_shifted) - 1


def trainola(a, b):
    # Compute trainola score for two waveforms a and b.

    # a and b are 2-D arrays with the same number of rows,
    # but they do not need to have the same number of columns.

    # Returns a score within [0, infinity] such that
    # 0 indicates a match, 1 indicates no correlation,
    # and infinity indicates negative correlation

    a = a.reshape((-1, a.shape[-1]))
    b = b.reshape((-1, b.shape[-1]))

    max_length = max(a.shape[-1], b.shape[-1])

    # Probably can cache these somehow (outside of the function)
    max_length_2 = int(2**np.ceil(np.log2(max_length)))
    A = np.fft.fft(a, n=max_length_2)
    B = np.fft.fft(b, n=max_length_2)
    circular_corr = np.fft.ifft(A * B.conj()).real
    corr_scores = np.sum(circular_corr / (max(np.linalg.norm(a), np.linalg.norm(b)) ** 2), axis=0)
    mapped_scores = mapping(corr_scores)
    return max(min(mapped_scores), 0)


async def get_transients(stream_name, intervals):
    async with get_joule_node() as node:
        events = []
        for interval in intervals:
            sarray = await node.data_read_array(stream_name + '/transients', start=interval[0], end=interval[1], flatten=True)
            events.append(sarray.T)

    return events


async def label_data(stream_name, intervals, label_name):
    new_events = []
    async with get_joule_node() as node:
        for interval in intervals:
            old_events = await node.event_stream_read(stream_name + '/events', start=interval[0], end=interval[1])
            new_event = old_events[0]
            new_event.content['label'] = label_name
            new_events.append(new_event)
            # await node.event_stream_remove(stream_name + '/events', start=interval[0], end=interval[1])

        await node.event_stream_write(stream_name + '/events', new_events)
