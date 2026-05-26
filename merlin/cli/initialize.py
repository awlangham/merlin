import click
import configparser
import asyncio

from merlin.cli.decorators import pass_node_name
from merlin.api import new_installation


@click.command(name='initialize')
@pass_node_name
def initialize(node) -> None:
    """
    Set up a Merlin event processor on a given transient stream.

    The user is prompted to choose a transient source, a supervision
    level, and to supply any initial load information.
    """

    from merlin.utilities import search_for_stream, create_event_stream

    num_phases = int(click.prompt('Enter number of power system phases', type=click.Choice(['1', '3']), default='3'))

    click.echo('Select a transient source:')

    sources_list = asyncio.run(search_for_stream(node, 'prep'))
    for index, source in enumerate(sources_list):
        click.echo(f'  {index + 1}) {source}')

    value = click.prompt(f'Selection [1-{len(sources_list)}]', type=int)

    selected_folder = sources_list[value - 1]
    click.echo(f'\nTransient source stream: [{selected_folder}/transients]')

    if asyncio.run(create_event_stream(node, selected_folder)):
        click.echo(f'Created event stream [{selected_folder}/events]')
    else:
        click.echo(f'Event stream [{selected_folder}/events] already exists')

    # click.echo('\nSelect a learning method:')
    # learning_methods = ['Unsupervised', 'Supervised']
    # for index, method in enumerate(learning_methods):
    #     click.echo(f'  {index + 1}) {method}')

    # value = click.prompt(f'Selection [1-{len(learning_methods)}]', type=int)
    # if learning_methods[value - 1] == 'Supervised':
        # _supervised_setup(selected_folder, node)

    min_window_length = click.prompt(f'Enter the minimum flat window length', type=int)
    threshold = click.prompt('Enter transient threshold', type=float)
    median_length = click.prompt('Enter median filter length', type=int)

    module_config = configparser.ConfigParser()
    module_config['Main'] = {
        'exec_cmd': 'merlin-sparsify',
        'name': 'Merlin sparsifier'
    }
    module_config['Arguments'] = {
        'output': f'{selected_folder}/events',
        # 'method': learning_methods[value - 1].lower(),
        'min_window_length': min_window_length,
        'threshold': threshold,
        'median_window_length': median_length
    }
    module_config['Inputs'] = {
        'prep': f'{selected_folder}/prep'
    }
    module_config['Outputs'] = {
        'transients': f'{selected_folder}/transients'
    }

    module_config_filename = f'{selected_folder[1:].replace('/', '_').replace(' ', '_')}_sparsify.conf'
    with open(module_config_filename, 'w') as module_config_file:
        module_config.write(module_config_file)

    stream_config_filename = f'{selected_folder[1:].replace('/', '_').replace(' ', '_')}_transients.conf'
    stream_config = configparser.ConfigParser()
    stream_config['Main'] = {
        'name': 'transients',
        'path': selected_folder,
        'datatype': 'float32'
    }

    phases = ['A', 'B', 'C'] if num_phases == 3 else ['A']
    element_number = 1
    for phase in phases:
        for harm in [1, 3, 5, 7]:
            stream_config[f'Element{element_number}'] = {
                'name': f'P{harm}{phase}'
            }
            element_number += 1

            stream_config[f'Element{element_number}'] = {
                'name': f'Q{harm}{phase}'
            }
            element_number += 1

    with open(stream_config_filename, 'w') as stream_config_file:
        stream_config.write(stream_config_file)

    click.echo(f'\nCreated {module_config_filename}')

    new_installation(selected_folder, num_phases, node)
    click.echo('Created new configuration.')

    click.echo('Complete installation by either adding loads/exemplars or running merlin learn loads')


# def _supervised_setup(selected_folder, node_name) -> None:
#     from merlin.models import GenericLoad
#     from merlin.api import Installation

#     click.echo('\n~~~ Load Configuration ~~~')

#     load_names = _comma_separated_to_strings(click.prompt('Enter a comma-separated list of loads'))

#     load_dict = {}
#     for load_name in load_names:
#         click.echo(f'\nConfiguring {load_name}:')
#         state_names = _comma_separated_to_strings(click.prompt('Enter a comma-separated list of states', default='OFF, ON'))

#         states_dict = {}
#         for state_name in state_names:
#             click.echo(f'\nConfiguring {load_name}::{state_name}')
#             P_ss = click.prompt('Enter steady-state real power', type=float)
#             Q_ss = click.prompt('Enter steady-state reactive power', type=float)

#             states_dict[state_name] = [P_ss, Q_ss]

#         new_load = GenericLoad(load_name, states_dict)

#         load_dict[load_name] = new_load.to_json()

#     click.echo('\n~~~ Exemplar Configuration ~~~')
#     exemplar_list = []
#     create_new_exemplar = True
#     while create_new_exemplar:
#         click.echo('\nCreating new exemplar')
#         # TODO: Implement Click ParamType for comma-separated stuff
#         timestamps = _comma_separated_to_ints(click.prompt('Exemplar timestamp interval'))

#         transitions = _comma_separated_to_strings(click.prompt('Associated state transitions'))

#         exemplar_list.append({
#             'start_ts': timestamps[0],
#             'end_ts': timestamps[1],
#             'transitions': [_parse_transition(t) for t in transitions]
#         })

#         create_new_exemplar = click.confirm('Continue adding exemplars')


#     joule_node = get_node(node_name)
#     installation = Installation(joule_node)
#     with installation.modify_config() as config:
#         config = {}
#         config['stream_name'] = selected_folder
#         config['exemplars'] = exemplar_list
#         config['loads'] = load_dict
#     asyncio.run(joule_node.close())


#     click.echo(f'Saved to {installation.config_filename}')


# def _comma_separated_to_strings(string) -> list[str]:
#     return [substring.strip() for substring in string.split(',')]


# def _comma_separated_to_ints(string) -> list[int]:
#     return [int(substring.strip()) for substring in string.split(',')]


# def _parse_transition(string) -> tuple[str, str, str]:
#     substrings = string.split('::')
#     load_name = substrings[0]

#     substrings = substrings[1].split('->')
#     state1 = substrings[0]
#     state2 = substrings[1]

#     return load_name, state1, state2
