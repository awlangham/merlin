import click
import numpy as np
import configparser
from tabulate import tabulate
from merlin.utilities import search_for_stream, create_event_stream, clear_stream
from merlin.unsupervised import list_clusters


@click.group()
@click.version_option()
def main() -> None:
    pass


@main.command(name='datasets')
def datasets() -> None:
    """
    List all event datasets.
    """

    for dataset in search_for_stream('events'):
        click.echo(dataset)


@main.command(name='init')
def init() -> None:
    """
    Set up a Merlin event processor on a given transient stream.
    """

    click.echo('Select a transient source:')

    sources_list = search_for_stream('transients')
    for index, source in enumerate(sources_list):
        click.echo(f'  {index + 1}) {source}')

    value = click.prompt(f'Selection [1-{len(sources_list)}]', type=int)

    selected_folder = sources_list[value - 1]
    click.echo(f'\nTransient source stream: [{selected_folder}/transients]')

    if create_event_stream(selected_folder):
        click.echo(f'Created event stream [{selected_folder}/events]')
    else:
        click.echo(f'Event stream [{selected_folder}/events] already exists')

    click.echo('\nSelect a learning method:')
    learning_methods = ['Unsupervised', 'Semi-supervised', 'Supervised']
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


@main.command(name='clusters')
@click.argument('event_stream')
def cli_clusters(event_stream) -> None:
    """
    Extract significant clusters from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    clusters = list_clusters(event_stream)

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']
    table = [
        [cluster['index'] + 1, cluster['size'], *[np.round(m, 1) for m in cluster['exemplar']]]
        for cluster in clusters if cluster['index'] != -1]
    click.echo(tabulate(table, headers=headers))


@main.command(name='clear')
@click.argument('event_stream')
def cli_clear(event_stream) -> None:
    """
    Remove all events from EVENT_STREAM.
    """

    clear_stream(event_stream)
