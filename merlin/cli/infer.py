import click
import json
from joule.utilities import human_to_timestamp as h2ts
import asyncio

from merlin.installation import config_filename
from merlin.cli.decorators import pass_node_name
from merlin.inference import level_zero, level_one, level_two


@click.command(name='infer-zero')
@click.argument('event_stream')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_zero(node, event_stream, start, end) -> None:
    """
    Infer loads and exemplars from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    from tabulate import tabulate

    inferred_exemplars, inferred_loads = level_zero(node, event_stream, h2ts(start), h2ts(end))

    table = []
    for load in inferred_loads:
        table.append([load.name, load.family, *load.states['ON']])

    headers = ['Load name', 'Family', 'PA_ss (W)', 'QA_ss (Var)', 'PB_ss (W)', 'QB_ss (Var)', 'PC_ss (W)', 'QC_ss (Var)']
    click.echo(tabulate(table, headers=headers))

    if click.confirm('Save configuration?'):
        load_dict = {}
        exemplar_list = []
        for load in inferred_loads:
            load_dict[load.name] = load.to_json()

        for exemplar in inferred_exemplars:
            exemplar_list.append(exemplar.to_json())

        config = {}
        config['node'] = node
        config['stream_name'] = event_stream
        config['exemplars'] = exemplar_list
        config['loads'] = load_dict

        with open(config_filename, 'w') as f:
            json.dump(config, f, indent=4)

        click.echo(f'Saved to {config_filename}')


@click.command(name='infer-one')
@click.argument('event_stream')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_one(node, event_stream, start, end) -> None:
    inferred_exemplars = level_one(node, event_stream, h2ts(start), h2ts(end))
    print(inferred_exemplars)

    with open(config_filename, 'r') as f:
        config_json = json.load(f)

    config_json['exemplars'] = [inferred_exemplar.to_json() for inferred_exemplar in inferred_exemplars]

    with open(config_filename, 'w') as f:
        json.dump(config_json, f, indent=4)

    click.echo(f'Saved to {config_filename}')


@click.command(name='infer-two')
@click.argument('event_stream')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_two(node, event_stream, start, end) -> None:
    inferred_exemplar, match_score = asyncio.run(level_two(node, event_stream, h2ts(start), h2ts(end)))

    if inferred_exemplar is None:
        click.echo('No exemplar matched.')
    else:
        click.echo(f'Exemplar match (Score: {match_score}):')
    click.echo(inferred_exemplar)
