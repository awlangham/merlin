import click
import configparser

from merlin.cli.decorators import pass_node_name


@click.command(name='initialize')
@pass_node_name
def initialize(node) -> None:
    """
    Set up a Merlin event processor on a given transient stream.
    """

    from merlin.utilities import search_for_stream, create_event_stream

    click.echo('Select a transient source:')

    sources_list = search_for_stream(node, 'transients')
    for index, source in enumerate(sources_list):
        click.echo(f'  {index + 1}) {source}')

    value = click.prompt(f'Selection [1-{len(sources_list)}]', type=int)

    selected_folder = sources_list[value - 1]
    click.echo(f'\nTransient source stream: [{selected_folder}/transients]')

    if create_event_stream(node, selected_folder):
        click.echo(f'Created event stream [{selected_folder}/events]')
    else:
        click.echo(f'Event stream [{selected_folder}/events] already exists')

    click.echo('\nSelect a learning method:')
    learning_methods = ['Unsupervised', 'Supervised']
    for index, method in enumerate(learning_methods):
        click.echo(f'  {index + 1}) {method}')

    value = click.prompt(f'Selection [1-{len(learning_methods)}]', type=int)
    if learning_methods[value - 1] == 'Supervised':
        _supervised_setup(selected_folder)

    config = configparser.ConfigParser()
    config['Main'] = {
        'exec_cmd': 'merlin-process-events',
        'name': 'Merlin event processor'
    }
    config['Arguments'] = {
        'output': f'{selected_folder}/events',
        'method': learning_methods[value - 1].lower()
    }
    config['Inputs'] = {
        'transients': f'{selected_folder}/transients'
    }

    filename = 'merlin.conf'
    with open(filename, 'w') as configfile:
        config.write(configfile)

    click.echo(f'\nCreated {filename}')


def _supervised_setup(selected_folder):
    from merlin.models import GenericLoad
    from merlin.config import config_file, filename

    click.echo('\n~~~ Load Configuration ~~~')

    load_names = _comma_separated_to_strings(click.prompt('Enter a comma-separated list of loads'))

    load_dict = {}
    for load_name in load_names:
        click.echo(f'\nConfiguring {load_name}:')
        state_names = _comma_separated_to_strings(click.prompt('Enter a comma-separated list of states', default='OFF, ON'))

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
        timestamps = _comma_separated_to_ints(click.prompt('Exemplar timestamp interval'))

        transitions = _comma_separated_to_strings(click.prompt('Associated state transitions'))

        exemplar_list.append({
            'start_ts': timestamps[0],
            'end_ts': timestamps[1],
            'transitions': [_parse_transition(t) for t in transitions]
        })

        create_new_exemplar = click.confirm('Continue adding exemplars')

    with config_file(write=True) as config:
        config['stream_name'] = selected_folder
        config['exemplars'] = exemplar_list
        config['loads'] = load_dict

    click.echo(f'Saved to {filename}')


def _comma_separated_to_strings(string):
    return [substring.strip() for substring in string.split(',')]


def _comma_separated_to_ints(string):
    return [int(substring.strip()) for substring in string.split(',')]


def _parse_transition(string):
    substrings = string.split('::')
    load_name = substrings[0]

    substrings = substrings[1].split('->')
    state1 = substrings[0]
    state2 = substrings[1]

    return load_name, state1, state2
