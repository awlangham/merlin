import numpy as np
import asyncio
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import MinMaxScaler

from merlin.utilities import get_joule_node


class Exemplar:
    def __init__(self, features) -> None:
        self.features_ = features

    def __repr__(self) -> str:
        return f'Exemplar({self.features_})'


class Cluster:
    def __init__(self, label, indices, size, exemplar) -> None:
        self.label_ = label
        self.indices_ = indices
        self.size_ = size
        self.exemplar = exemplar

    def __len__(self) -> int:
        return self.size_

    def to_json(self) -> dict:
        return {'ss': self.exemplar.features_.tolist()}


class Clustering:
    def __init__(self, node_name, event_stream_name) -> None:
        async def _get_events():
            async with get_joule_node(node_name) as node:
                return await node.event_stream_read(event_stream_name + '/events')

        events = asyncio.run(_get_events())

        # TODO: handle empty case
        # if len(events) == 0:
        #     return [], []

        feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']
        features = np.array([
            [
                event.content[name] for name in feature_names]
            for event in events
        ])

        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid').fit(scaled_features)

        self.labels = hdbscan.labels_
        self.medoids_values = scaler.inverse_transform(hdbscan.medoids_)

        self.medoids_indices = []
        for m in hdbscan.medoids_:
            medoid_index = np.where(np.all(scaled_features == m, axis=1))[0][0]
            self.medoids_indices.append(medoid_index)

        distinct_labels = list(set(self.labels))
        self.clusters = []
        for cluster_label in distinct_labels:
            if cluster_label < 0:
                continue

            cluster_indices = np.where(self.labels == cluster_label)[0]
            cluster_size = len(cluster_indices)

            cluster_exemplar = Exemplar(self.medoids_values[cluster_label])

            self.clusters.append(Cluster(cluster_label, cluster_indices, cluster_size, cluster_exemplar))

    def __iter__(self):
        yield from self.clusters
