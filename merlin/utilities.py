import numpy as np
import joule
from joule.api import EventStream
from joule.errors import ApiError
from contextlib import asynccontextmanager
import asyncio
from async_lru import alru_cache


@asynccontextmanager
async def get_joule_node(node_name: str):
    """
    Context manager for a Joule node handle.
    Automatically handles closing network resources.
    """

    node = joule.api.get_node(node_name)
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
async def create_event_stream(node_name: str, path: str) -> bool:
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


@async_run
async def get_events(node_name: str, stream_name: str, start: int = None, end: int = None) -> list:
    """
    Return a list of all events in the specified stream.
    """

    async with get_joule_node(node_name) as node:
        return await node.event_stream_read_list(stream_name + '/events', start=start, end=end, limit=1000)


@async_run
async def search_for_stream(node_name: str, stream_name: str) -> list:
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

    async with get_joule_node(node_name) as node:
        root = await node.folder_root()
        traverse_folder(root)

    await node.close()

    return stream_names


@async_run
async def clear_stream(node_name: str, stream_name: str) -> None:
    """
    Remove all events from the specified stream.
    """

    async with get_joule_node(node_name) as node:
        await node.event_stream_remove(stream_name + '/events')


@alru_cache(maxsize=8192)
async def read_interval(node_name: str, stream_name: str, interval_start: int, interval_end: int):
    """
    Cache recently-viewed transients in the back-end program.
    """

    async with get_joule_node(node_name) as node:
        pipe = await node.data_read(stream_name + '/transients', start=interval_start, end=interval_end)
        sarray = await pipe.read_all(flatten=True)
    return sarray


async def get_transients(node_name: str, stream_name: str, intervals: list[list[int]]) -> list:
    """
    Return a list of the transients corresponding
    to the specified intervals in the provided stream.
    """

    transients = []
    for interval in intervals:
        sarray = await read_interval(node_name, stream_name, interval[0], interval[1])
        transients.append(sarray.T)

    return transients


async def label_data(node_name: str, stream_name: str, intervals: list[list[int]], label_name: str) -> None:
    """
    Apply the specified label to the events in the
    provided stream that correspond to the specified
    time intervals.
    """

    starts = [interval[0] for interval in intervals]
    min_start_ts = min(starts)
    max_end_ts = max([interval[1] for interval in intervals])

    new_events = []
    async with get_joule_node(node_name) as node:
        events = await node.event_stream_read_list(stream_name + '/events', start=min_start_ts, end=max_end_ts)

        for event in events:
            if event.start_time in starts:
                event.content['label'] = label_name
                new_events.append(event)

        await node.event_stream_write(stream_name + '/events', new_events)


def trainola(a, b):
    """
    Compute trainola score for two waveforms a and b.

    a and b are 2-D arrays with the same number of rows,
    but they do not need to have the same number of columns.

    Returns a score within [0, infinity] such that
    0 indicates a match, 1 indicates no correlation,
    and infinity indicates negative correlation
    """

    # Remove mean of first 5 samples
    a = (a.T - np.mean(a[:, :5], axis=1)).T
    b = (b.T - np.mean(b[:, :5], axis=1)).T

    max_length = max(a.shape[-1], b.shape[-1])

    # Find the next power of 2 from max_length
    # since FFT works best with n as a power of 2.
    max_length_base_2 = int(2**np.ceil(np.log2(max_length)))

    A = np.fft.fft(a, n=max_length_base_2)
    B = np.fft.fft(b, n=max_length_base_2)

    circular_corr = np.fft.ifft(A * B.conj()).real
    corr_scores = np.sum(circular_corr / (max(np.linalg.norm(a), np.linalg.norm(b)) ** 2), axis=0)
    mapped_scores = mapping(corr_scores)

    return max(min(mapped_scores), 0)


def mapping(x):
    """
    Mapping function to turn correlation scores into
    trainola scores.

    0 is good, 1 is neutral, inf is bad
    """

    # fix for floating point
    x_shifted = x + 1
    close_to_zero = np.isclose(x_shifted, 0)
    x_shifted[close_to_zero] = 0

    with np.errstate(divide='ignore'):
        return np.divide(2, x_shifted) - 1
