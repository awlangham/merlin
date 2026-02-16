import asyncio
import click

from merlin.cli.decorators import pass_node_name


@click.command('datasets')
@pass_node_name
def datasets(node) -> None:
    """
    List all event datasets.
    """

    from merlin.utilities import search_for_stream

    for dataset in asyncio.run(search_for_stream(node, 'events')):
        click.echo(dataset)
