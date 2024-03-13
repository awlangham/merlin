import click
from merlin import list_event_sources

@click.group()
@click.version_option()
def main():
    pass


@main.command(name='sources')
def sources():
    for source in list_event_sources():
        click.echo(source)