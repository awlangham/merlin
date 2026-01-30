import click

from merlin.api import get_installation


@click.command('remove')
@click.argument('exemplar_index', type=int)
def remove(exemplar_index: int) -> None:
    """
    Remove an exemplar from the active configuration.
    """

    try:
        get_installation().remove_exemplar(exemplar_index)
    except IndexError:
        click.echo(f'No exemplar with index {exemplar_index} exists.')
