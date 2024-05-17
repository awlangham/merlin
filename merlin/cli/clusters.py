import click
from tabulate import tabulate
import numpy as np
from merlin.loads import load_file

from merlin.cli.decorators import pass_node_name
from merlin.unsupervised.clustering import Clustering


@click.command(name='clusters')
@click.argument('event_stream')
@click.option('--export', '-e', is_flag=True, default=False, help='Export clusters to load configuration')
@pass_node_name
def cli_clusters(node, event_stream, export) -> None:
    """
    Extract significant clusters from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    table = []
    for cluster in Clustering(node, event_stream):
        table.append([cluster.label_ + 1,
                      len(cluster),
                      *[np.round(m, 1) for m in cluster.exemplar.features_]]
                     )

        if export:
            with load_file() as loads_json:
                loads_json[str(cluster.label_)] = cluster.to_json()

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']

    click.echo(tabulate(table, headers=headers))
