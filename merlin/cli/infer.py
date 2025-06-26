import click
from joule.utilities import human_to_timestamp as h2ts
from joule.api import get_node
import asyncio

from merlin.installation import config_filename, CurrentInstallation, new_installation
from merlin.cli.decorators import pass_node_name


@click.command(name='infer-zero')
@click.argument('event_stream')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_zero(node, event_stream, start, end) -> None:
    """
    Infer loads and exemplars from EVENT_STREAM. All loads are assumed to be two-state (ON, OFF).

    Clusters with fewer than 25 data points are excluded.
    """

    from tabulate import tabulate

    joule_node = get_node(node)
    installation = new_installation(joule_node, event_stream)
    inferred_exemplars, inferred_loads = installation.level_zero(h2ts(start), h2ts(end))
    asyncio.run(joule_node.close())

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

        with installation.config() as config:
            config['exemplars'] = exemplar_list
            config['loads'] = load_dict

        click.echo(f'Saved to {config_filename}')


@click.command(name='infer-one')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_one(node, start, end) -> None:
    """
    Find exemplars in EVENT_STREAM over the specified period that match load state changes in the config file.
    """

    joule_node = get_node(node)
    current_installation = CurrentInstallation(joule_node)
    inferred_exemplars = current_installation.level_one(h2ts(start), h2ts(end))
    asyncio.run(joule_node.close())

    with CurrentInstallation().config() as cf:
        cf['exemplars'] = [inferred_exemplar.to_json() for inferred_exemplar in inferred_exemplars]

    click.echo(f'Saved to {config_filename}')


@click.command(name='infer-two')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_two(node, start, end) -> None:
    """
    Find the exemplar in the config file that matches the specified data in EVENT_STREAM.
    """

    joule_node = get_node(node)
    current_installation = CurrentInstallation(joule_node)
    inferred_exemplar, match_score = current_installation.level_two(h2ts(start), h2ts(end))
    asyncio.run(joule_node.close())

    if inferred_exemplar is None:
        click.echo(f'No exemplar matched (Best score: {match_score})')
    else:
        click.echo(f'Exemplar match (Score: {match_score}):')
        click.echo(inferred_exemplar)


@click.command(name='infer-three')
@click.argument('load_name')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
@pass_node_name
def infer_three(node, load_name, start, end) -> None:
    """
    Infer a the statistical behavior of a load.
    """

    joule_node = get_node(node)
    current_installation = CurrentInstallation(joule_node)
    current_installation.level_three(load_name, h2ts(start), h2ts(end))
    asyncio.run(joule_node.close())
