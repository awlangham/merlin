import click

from merlin.models import GenericLoad
from merlin.config import config_file, filename


def comma_separated_to_strings(string):
    return [substring.strip() for substring in string.split(',')]


def comma_separated_to_ints(string):
    return [int(substring.strip()) for substring in string.split(',')]


def parse_transition(string):
    substrings = string.split('::')
    load_name = substrings[0]

    substrings = substrings[1].split('->')
    state1 = substrings[0]
    state2 = substrings[1]

    return load_name, state1, state2


@click.command('configure')
def configure() -> None:
    """
    Configure Merlin with a set of known loads and exemplars.
    """

    click.echo('\n~~~ Load Configuration ~~~')

    load_names = comma_separated_to_strings(click.prompt('Enter a comma-separated list of loads'))

    load_dict = {}
    for load_name in load_names:
        click.echo(f'\nConfiguring {load_name}:')
        state_names = comma_separated_to_strings(click.prompt('Enter a comma-separated list of states', default='OFF, ON'))

        states_dict = {}
        for state_name in state_names:
            click.echo(f'\nConfiguring {load_name}::{state_name}')
            P_ss = click.prompt('Enter steady-state real power', type=float)
            Q_ss = click.prompt('Enter steady-state reactive power', type=float)

            states_dict[state_name] = [P_ss, Q_ss]

        new_load = GenericLoad(load_name, states_dict)

        load_dict[load_name] = new_load.to_json()

    click.echo('\n~~~ Exemplar Configuration ~~~')
    exemplar_list = []
    create_new_exemplar = True
    while create_new_exemplar:
        click.echo('\nCreating new exemplar')
        # TODO: Implement Click ParamType for comma-separated stuff
        timestamps = comma_separated_to_ints(click.prompt('Exemplar timestamp interval'))

        transitions = comma_separated_to_strings(click.prompt('Associated state transitions'))

        exemplar_list.append({
            'start_ts': timestamps[0],
            'end_ts': timestamps[1],
            'transitions': [parse_transition(t) for t in transitions]
        })

        create_new_exemplar = click.confirm('Continue adding exemplars')

    with config_file() as config:
        config['exemplars'] = exemplar_list
        config['loads'] = load_dict

    click.echo(f'Saved to {filename}')
