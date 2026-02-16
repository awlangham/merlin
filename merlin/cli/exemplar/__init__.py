import click

from merlin.cli.exemplar.add import add
from merlin.cli.exemplar.remove import remove


@click.group()
def exemplar() -> None:  # pragma: no cover
    """
    Manage exemplars.
    """
    pass


exemplar.add_command(add)
exemplar.add_command(remove)
