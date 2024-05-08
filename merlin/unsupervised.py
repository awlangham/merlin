from itertools import combinations
import numpy as np
import asyncio
from sklearn.cluster import HDBSCAN
from sklearn.manifold import MDS
from sklearn.preprocessing import MinMaxScaler
from merlin.utilities import get_joule_node, trainola


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
    cluster_labels, exemplars = asyncio.run(cluster_data(event_stream_name))
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


async def mds_data(stream_name, intervals):
    async with get_joule_node() as node:
        mds_events = []
        for interval in intervals:
            sarray = await node.data_read_array(stream_name + '/transients', start=interval[0], end=interval[1], flatten=True)
            mds_events.append(sarray.T)

    num_events = len(mds_events)
    trainola_distances = np.zeros((num_events, num_events))

    for t1, t2 in combinations(range(num_events), 2):
        pair_distance = trainola(mds_events[t1][1:], mds_events[t2][1:])
        trainola_distances[t1, t2] = pair_distance
        trainola_distances[t2, t1] = pair_distance

    # # transformed = UMAP(metric='precomputed', min_dist=0, n_neighbors=4).fit_transform(trainola_distances)

    transformed = MDS(dissimilarity='precomputed', normalized_stress='auto').fit_transform(trainola_distances)
    # # embedding_distances = cdist(transformed, transformed)
    # # error_matrix = embedding_distances - trainola_distances
    # # print(f'RMSE: {np.sqrt(np.mean(error_matrix ** 2))}')

    return transformed
