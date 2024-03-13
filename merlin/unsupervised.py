import numpy as np
from sklearn.cluster import DBSCAN, HDBSCAN
from sklearn.preprocessing import MinMaxScaler
from merlin import async_run, get_node


@async_run
async def get_clusters(event_stream_name):
    async with get_node() as node:
        events = await node.event_stream_read(event_stream_name)

    feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']
    features = np.array([
        [
            event.content[name] for name in feature_names]
        for event in events
    ])

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)

    # dbscan = DBSCAN(eps=0.01).fit(scaled_features)
    hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid').fit(scaled_features)
    cluster_labels = list(set(hdbscan.labels_))
    exemplars = scaler.inverse_transform(hdbscan.medoids_)

    output = []
    for index, cluster_label in enumerate(cluster_labels):
        if cluster_label < 0:
            continue

        cluster_indices = np.where(hdbscan.labels_ == cluster_label)[0]
        cluster_data = features[cluster_indices]

        # cluster_mean = np.mean(cluster_data, axis=0)
        output.append({
            'index': cluster_label,
            'size': len(cluster_data),
            'exemplar': exemplars[index].tolist()
        })

    return output
