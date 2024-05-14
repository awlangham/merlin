import click

from merlin.cli.decorators import pass_node_name
from merlin.utilities import search_for_stream

@click.command('datasets')
@pass_node_name
def datasets(node) -> None:
    """
    List all event datasets.
    """

    for dataset in search_for_stream(node, 'events'):
        click.echo(dataset)