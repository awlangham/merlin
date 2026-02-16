import click

from merlin.cli.load.add import add
from merlin.cli.load.remove import remove
from merlin.cli.load.rename import rename


@click.group()
def load() -> None:  # pragma: no cover
    """
    Manage loads.
    """
    pass


load.add_command(add)
load.add_command(remove)
load.add_command(rename)
