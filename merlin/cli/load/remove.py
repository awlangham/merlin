import click

from merlin.api import get_installation


@click.command('remove')
@click.argument('load_name')
def remove(load_name: str) -> None:
    """
    Remove a load from the active configuration.
    """

    try:
        get_installation().remove_load(load_name)
        click.echo(f'Removed {load_name} from configuration.')

        get_installation().remove_exemplar_by_load(load_name)
        click.echo(f'Removed all {load_name} exemplars.')
    except KeyError:
        click.echo(f'No load found named {load_name}.')
