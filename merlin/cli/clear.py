import click
import asyncio

from merlin.cli.decorators import pass_node_name
from merlin.utilities import get_joule_node


@click.command(name='clear')
@click.argument('event_stream')
@pass_node_name
def cli_clear(node, event_stream: str) -> None:
    """
    Remove all events from EVENT_STREAM.
    """

    asyncio.run(_clear_stream(node, event_stream))


async def _clear_stream(node_name: str, stream_name: str) -> None:
    async with get_joule_node(node_name) as node:
        await node.event_stream_remove(stream_name + '/events')
