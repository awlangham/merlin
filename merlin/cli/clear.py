import click
import asyncio

from merlin.cli.decorators import pass_node_name
from merlin.utilities import clear_stream


@click.command(name='clear')
@click.argument('event_stream')
@pass_node_name
def cli_clear(node, event_stream: str) -> None:
    """
    Remove all events from EVENT_STREAM.
    """

    asyncio.run(clear_stream(node, event_stream))
