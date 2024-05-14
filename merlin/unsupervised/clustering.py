import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import MinMaxScaler

from merlin.utilities import get_joule_node

async def cluster_data(node_name, event_stream_name):
    async with get_joule_node(node_name) as node:
        events = await node.event_stream_read(event_stream_name + '/events')

    if len(events) == 0:
        return [], []

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