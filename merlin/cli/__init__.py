import click

from merlin.cli.datasets import datasets
from merlin.cli.initialize import initialize
from merlin.cli.clusters import cli_clusters
from merlin.cli.clear import cli_clear
from merlin.cli.configure import configure


@click.group()
@click.version_option()
@click.option('--node', '-n', default='', help='Joule node to use (uses default if unspecified)')
@click.pass_context
def main(context, node) -> None:
    context.ensure_object(dict)
    context.obj['NODE'] = node


main.add_command(datasets)
main.add_command(initialize)
main.add_command(cli_clusters)
main.add_command(cli_clear)
main.add_command(configure)
