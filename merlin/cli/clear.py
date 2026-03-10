import click
import asyncio
from joule.utilities import human_to_timestamp as h2ts

from merlin.cli.decorators import pass_node_name
from merlin.utilities import get_joule_node


@click.command(name='clear')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@click.argument('event_stream')
@pass_node_name
def cli_clear(node, start: str, end: str, event_stream: str) -> None:
    """
    Remove all events from EVENT_STREAM.
    """

    asyncio.run(_clear_stream(node, h2ts(start), h2ts(end), event_stream))


async def _clear_stream(node_name: str, start_ts: int, end_ts: int, stream_name: str) -> None:
    async with get_joule_node(node_name) as node:
        await node.data_delete(stream_name + '/transients', start=start_ts, end=end_ts)
        await node.event_stream_remove(stream_name + '/events', start=start_ts, end=end_ts)
