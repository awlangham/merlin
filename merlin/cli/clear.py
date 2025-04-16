import click

from merlin.cli.decorators import pass_node_name
from merlin.lib.events import clear_event_stream


@click.command(name='clear')
@click.argument('event_stream')
@pass_node_name
def cli_clear(node, event_stream) -> None:
    """
    Remove all events from EVENT_STREAM.
    """

    clear_event_stream(node, event_stream)
