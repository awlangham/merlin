import click

from merlin.api import config_filename


@click.command('rename')
@click.argument('old_name')
@click.argument('new_name')
def rename(old_name: str, new_name: str) -> None:
    """
    Rename a load.
    """

    with open(config_filename, 'r') as file:
        config_text = file.read()

    config_text = config_text.replace(f'"{old_name}"', f'"{new_name}"')

    with open(config_filename, 'w') as file:
        file.write(config_text)

    click.echo(f'Renamed {old_name} to {new_name}.')
