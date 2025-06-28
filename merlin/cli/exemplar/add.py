import click

from merlin.api import Installation
from merlin.cli.utilities import _comma_separated_to_ints, _comma_separated_to_strings, _parse_transition


@click.command('add')
def add() -> None:
    """
    Add an exemplar to the configuration.
    """

    timestamps = _comma_separated_to_ints(click.prompt('Exemplar timestamp interval'))
    transitions = _comma_separated_to_strings(click.prompt('Associated state transitions'))

    new_exemplar = {
        'start_ts': timestamps[0],
        'end_ts': timestamps[1],
        'transitions': [_parse_transition(t) for t in transitions]
    }

    with Installation(None).config() as cf:
        cf['exemplars'].append(new_exemplar)

    click.echo('Added exemplar to configuration.')