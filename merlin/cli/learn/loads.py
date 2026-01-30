import click
from joule.utilities import human_to_timestamp as h2ts

from merlin.api import get_installation


@click.command('loads')
@click.option('--start', '-s', help='Timestamp or descriptive string', required=True)
@click.option('--end', '-e', help='Timestamp or descriptive string', required=True)
def learn_loads(start, end) -> None:
    try:
        start_ts, end_ts = h2ts(start), h2ts(end)
    except ValueError:
        click.echo('Invalid start/end time.')
        return

    from tabulate import tabulate

    installation = get_installation()
    num_phases = installation.num_phases
    inferred_exemplars, inferred_loads = installation.learn_loads(start_ts, end_ts)
    installation.close()

    table = []
    for load in inferred_loads:
        table.append([load.name, load.family, *load.states['ON']])

    if num_phases == 3:
        headers = ['Load name', 'Family', 'PA_ss (W)', 'QA_ss (Var)', 'PB_ss (W)', 'QB_ss (Var)', 'PC_ss (W)', 'QC_ss (Var)']
    else:
        headers = ['Load name', 'Family', 'P_ss (W)', 'Q_ss (Var)']
    click.echo(tabulate(table, headers=headers))

    if click.confirm('Save configuration?'):
        load_dict = {}
        exemplar_list = []
        for load in inferred_loads:
            load_dict[load.name] = load.to_json()

        for exemplar in inferred_exemplars:
            exemplar_list.append(exemplar.to_json())

        with installation.modify_config() as config:
            config['exemplars'] = exemplar_list
            config['loads'] = load_dict

        click.echo(f'Saved to configuration file.')
