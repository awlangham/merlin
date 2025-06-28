import click

from merlin.api import Installation


@click.command('remove')
@click.argument('exemplar_index', type=int)
def remove(exemplar_index: int) -> None:
    """
    Remove an exemplar from the active configuration.
    """

    with Installation(None).config() as cf:
        try:
            del cf['exemplars'][exemplar_index - 1]
            click.echo(f'Removed exemplar {exemplar_index} from configuration.')
        except IndexError:
            click.echo(f'No exemplar with index {exemplar_index} exists.')
