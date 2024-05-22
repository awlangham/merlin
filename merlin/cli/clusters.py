import click
from tabulate import tabulate
import numpy as np
from merlin.loads import load_file

from merlin.cli.decorators import pass_node_name
from merlin.unsupervised.clustering import Clustering


@click.command(name='clusters')
@click.argument('event_stream')
@click.option('--infer', '-i', is_flag=True, default=False)
@pass_node_name
def cli_clusters(node, event_stream, infer) -> None:
    """
    Extract significant clusters from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    table = []
    clustering = Clustering(node, event_stream)
    for cluster in clustering:
        table.append([cluster.id_ + 1,
                      len(cluster),
                      *[np.round(m, 1) for m in cluster.exemplar.features_]]
                     )

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']

    click.echo(tabulate(table, headers=headers))

    if infer:
        load_dict = {}
        exemplar_list = []
        for load in clustering.infer_loads():
            load_dict[load.name] = load.to_json()

        for cluster in clustering:
            exemplar_list.append(cluster.to_json())

        with load_file() as loads_json:
            loads_json['exemplars'] = exemplar_list
            loads_json['loads'] = load_dict

        click.echo('Saved to loads.json')
