import click

from merlin.api import Installation


@click.command('remove')
@click.argument('load_name')
def remove(load_name: str) -> None:
    with Installation(None).config() as cf:
        try:
            del cf['loads'][load_name]
            click.echo(f'Removed {load_name} from configuration.')
        except KeyError:
            click.echo(f'No load found named {load_name}.')
