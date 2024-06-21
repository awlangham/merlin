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
