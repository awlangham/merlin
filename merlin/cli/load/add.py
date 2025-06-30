import click

from merlin.models import GenericLoad
from merlin.api import Installation
from merlin.cli.utilities import _comma_separated_to_strings, _comma_separated_to_floats


@click.command('add')
@click.argument('load_name')
def add(load_name: str) -> None:
    """
    Add a load to the configuration.
    """

    state_names = _comma_separated_to_strings(click.prompt('Enter a comma-separated list of states', default='OFF, ON'))

    states_dict = {}
    for state_name in state_names:
        click.echo(f'\nConfiguring {load_name}::{state_name}')
        P_ss = _comma_separated_to_floats(click.prompt('Enter per-phase real power (PA, PB, PC)'))
        Q_ss = _comma_separated_to_floats(click.prompt('Enter per-phase reactive power (QA, QB, QC)'))

        PQ_ss = [None] * 6
        PQ_ss[::2] = P_ss
        PQ_ss[1::2] = Q_ss

        states_dict[state_name] = PQ_ss

    new_load = GenericLoad(load_name, states_dict)
    Installation(None).add_load(new_load)

    click.echo(f'Added {load_name} to configuration.')
