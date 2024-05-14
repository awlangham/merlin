import click
from tabulate import tabulate
import numpy as np

from merlin.cli.decorators import pass_node_name
from merlin.unsupervised import list_clusters

@click.command(name='clusters')
@click.argument('event_stream')
@pass_node_name
def cli_clusters(node, event_stream) -> None:
    """
    Extract significant clusters from EVENT_STREAM.

    Clusters with fewer than 25 data points are excluded.
    """

    clusters = list_clusters(node, event_stream)

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']
    table = [
        [cluster['index'] + 1, cluster['size'], *[np.round(m, 1) for m in cluster['exemplar']]]
        for cluster in clusters if cluster['index'] != -1]
    click.echo(tabulate(table, headers=headers))