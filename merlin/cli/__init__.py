import click
from joule.api import get_node

from merlin.cli.datasets import datasets
from merlin.cli.initialize import initialize
from merlin.cli.infer import infer_zero, infer_one
from merlin.cli.clear import cli_clear
from merlin.cli.docs import docs
from merlin.cli.configuration import configuration


@click.group()
@click.version_option()
@click.option('--node', '-n', default='', help='Joule node to use (uses the default node if unspecified).')
@click.pass_context
def main(context, node) -> None:
    context.ensure_object(dict)
    if node != '':
        context.obj['NODE'] = node
    else:
        context.obj['NODE'] = get_node(node).name


main.add_command(datasets)
main.add_command(initialize)
main.add_command(infer_zero)
main.add_command(infer_one)
main.add_command(cli_clear)
main.add_command(docs)
main.add_command(configuration)
