import click

from merlin.api import get_installation


@click.command(name='method')
@click.argument('selected_method', type=click.Choice(['unsupervised', 'supervised']))
def method(selected_method):
    """
    Set learning method.
    """

    installation = get_installation()
    with installation.modify_config() as cf:
        cf['method'] = selected_method

    click.echo(f'Set to {selected_method}. Restart Joule to change any running modules.')
