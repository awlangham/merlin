import click


from merlin.config import config_file, filename
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
    from merlin.unsupervised.clustering import Clustering

    table = []
    clustering = Clustering(node, event_stream)
    for cluster in clustering:
        table.append([cluster.id_ + 1,
                      len(cluster),
                      *[np.round(m, 1) for m in cluster.exemplar.features_]]
                     )

    headers = ['Index', 'Size', 'P_ss', 'Q_ss', 'P_pk', 'Q_pk']

    click.echo(tabulate(table, headers=headers))

    load_dict = {}
    exemplar_list = []
    for load in clustering.infer_loads():
        load_dict[load.name] = load.to_json()

    for cluster in clustering:
        exemplar_list.append(cluster.to_json())

    with config_file() as config:
        config['exemplars'] = exemplar_list
        config['loads'] = load_dict

    click.echo(f'Saved to {filename}')
