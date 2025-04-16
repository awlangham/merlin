import click
import json

from merlin.installation import config_filename
from merlin.cli.decorators import pass_node_name


@click.command(name='infer')
@click.argument('event_stream')
@pass_node_name
def infer(node, event_stream) -> None:
    """
    Infer loads and exemplars from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    from tabulate import tabulate
    import numpy as np
    from merlin.lib.inference.clustering import cluster_events, infer_loads

    table = []
    clustering = cluster_events(node, event_stream)[1]
    for cluster in clustering:
        table.append([cluster.id_ + 1,
                      len(cluster),
                      *[np.round(m, 1) for m in cluster.exemplar.features_]]
                     )

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']

    click.echo(tabulate(table, headers=headers))

    load_dict = {}
    exemplar_list = []
    for load in infer_loads(clustering):
        load_dict[load.name] = load.to_json()

    for cluster in clustering:
        exemplar_list.append(cluster.to_json())

    config = {}
    config['node'] = node
    config['stream_name'] = event_stream
    config['exemplars'] = exemplar_list
    config['loads'] = load_dict

    with open(config_filename, 'w') as f:
        json.dump(config, f, indent=4)

    click.echo(f'Saved to {config_filename}')
