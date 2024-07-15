import click
from treelib import Tree
from joule.utilities import timestamp_to_human as ts2h


@click.command('configuration')
def configuration() -> None:
    """
    Show current Merlin configuration.
    """

    from merlin.installation import CurrentInstallation

    config_valid = False

    exemplar_tree = Tree()
    exemplar_tree.create_node(click.style('Exemplars', bold=True), 'exemplars')

    load_tree = Tree()
    load_tree.create_node(click.style('Loads', bold=True), 'loads')

    current_installation = CurrentInstallation()
    cf = current_installation.config_json

    try:
        for i, exemplar in enumerate(cf['exemplars']):
            exemplar_tree.create_node(f'[ {ts2h(exemplar["start_ts"])}, {ts2h(exemplar["end_ts"])}]', i, parent='exemplars')
            for transition in exemplar['transitions']:
                exemplar_tree.create_node(f'{transition[0]}::{transition[1]}->{transition[2]}', parent=i)

        for i, load_name in enumerate(cf['loads']):
            load_dict = cf['loads'][load_name]
            if load_dict['family'] is None:
                load_tree.create_node(f'{load_name}', i, parent='loads')
            else:
                load_tree.create_node(f'{load_name} ({load_dict["family"]})', i, parent='loads')

            for state_name in load_dict['states']:
                P, Q = load_dict['states'][state_name]
                load_tree.create_node(f'{state_name}: {round(P, 2)} W, {round(Q, 2)} Var', parent=i)

        config_valid = True
    except KeyError:
        click.echo('Invalid configuration file.')

    if config_valid:
        click.echo(click.style('Node:', bold=True) + f' {cf['node']}')
        click.echo(click.style('Input:', bold=True) + f' {cf['stream_name']}/transients')
        click.echo(click.style('Output:', bold=True) + f' {cf['stream_name']}/events\n')
        click.echo(exemplar_tree.show(stdout=False))
        click.echo(load_tree.show(stdout=False))
