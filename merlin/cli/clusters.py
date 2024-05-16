import click
from tabulate import tabulate
import numpy as np
import asyncio
from merlin.loads import load_file

from merlin.cli.decorators import pass_node_name
from merlin.unsupervised.clustering import cluster_data


def list_clusters(node_name, event_stream_name):
    cluster_labels, exemplars = asyncio.run(cluster_data(node_name, event_stream_name))
    distinct_labels = list(set(cluster_labels))

    output = []
    for index, cluster_label in enumerate(distinct_labels):
        if cluster_label < 0:
            continue

        cluster_indices = np.where(cluster_labels == cluster_label)[0]

        output.append({
            'index': cluster_label,
            'size': len(cluster_indices),
            'exemplar': exemplars[index].tolist()
        })

    return output


@click.command(name='clusters')
@click.argument('event_stream')
@click.option('--export', '-e', is_flag=True, default=False, help='Export clusters to load configuration')
@pass_node_name
def cli_clusters(node, event_stream, export) -> None:
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

    if export:
        with load_file() as loads_json:
            for cluster in clusters:
                if cluster['index'] != -1:
                    index = str(cluster['index'])
                    loads_json[index] = {'ss': cluster['exemplar']}
