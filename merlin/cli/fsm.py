import click
import graphviz

from merlin.cli.decorators import pass_node_name
from merlin.installation import CurrentInstallation

@click.command('fsm')
@click.argument('load_name')
@pass_node_name
def fsm(node, load_name) -> None:
    click.echo(load_name)
    
    current_installation = CurrentInstallation(node)

    # Get load states
    load_json = current_installation.config_json['loads'][load_name]
    states = [state_name for state_name in load_json['states']]

    f = graphviz.Digraph()
    # f.attr(rankdir='LR')

    for state in states:
        f.node(state)
    
    exemplars = current_installation.config_json['exemplars']
    for exemplar in exemplars:
        for transition in exemplar['transitions']:
            if transition[0] == load_name:
                f.edge(transition[1], transition[2])

    f.attr(label=load_name)
    f.view(cleanup=True)