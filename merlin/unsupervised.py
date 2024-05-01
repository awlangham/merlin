import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import MinMaxScaler
from merlin.utilities import async_run, get_joule_node


@async_run
async def cluster_data(event_stream_name):
    async with get_joule_node() as node:
        events = await node.event_stream_read(event_stream_name + '/events')

    feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']
    features = np.array([
        [
            event.content[name] for name in feature_names]
        for event in events
    ])

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)

    hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid').fit(scaled_features)
    return hdbscan.labels_, scaler.inverse_transform(hdbscan.medoids_)


def list_clusters(event_stream_name):
    cluster_labels, exemplars = cluster_data(event_stream_name)
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
