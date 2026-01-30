import click

from merlin.api import get_installation
from merlin.models import Exemplar
from merlin.cli.utilities import _comma_separated_to_ints, _comma_separated_to_strings, _parse_transition


@click.command('add')
def add() -> None:
    """
    Add an exemplar to the configuration.
    """

    timestamps = _comma_separated_to_ints(click.prompt('Exemplar timestamp interval'))
    transitions = _comma_separated_to_strings(click.prompt('Associated state transitions'))

    new_exemplar = Exemplar(timestamps[0], timestamps[1], [_parse_transition(t) for t in transitions])
    get_installation().add_exemplar(new_exemplar)

    click.echo('Added exemplar to configuration.')
