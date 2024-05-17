import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import MinMaxScaler

from merlin.utilities import get_events


class Exemplar:
    def __init__(self, features, ts_interval) -> None:
        self.features_ = features
        self.ts_interval_ = ts_interval

    def __repr__(self) -> str:
        return f'Exemplar({self.features_})'


class Cluster:
    def __init__(self, cluster_id, indices, exemplar) -> None:
        self.id_ = cluster_id
        self.indices_ = indices
        self.size_ = len(indices)
        self.exemplar = exemplar

    def __len__(self) -> int:
        return self.size_

    def to_json(self) -> dict:
        return {'ss': self.exemplar.features_.tolist(), 'timestamps': self.exemplar.ts_interval_}


class Clustering:
    def __init__(self, node_name, event_stream_name) -> None:
        # TODO: handle case where there are no events

        feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']

        features, intervals = [], []
        for event in get_events(node_name, event_stream_name):
            features.append([event.content[name] for name in feature_names])
            intervals.append((event.start_time, event.end_time))

        features = np.array(features)

        scaler = MinMaxScaler()
        scaled_features = scaler.fit_transform(features)

        hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid').fit(scaled_features)

        self.cluster_assignments = hdbscan.labels_
        self.medoids_values = scaler.inverse_transform(hdbscan.medoids_)

        distinct_ids = list(set(self.cluster_assignments))
        self.clusters = []
        for cluster_id in distinct_ids:
            if cluster_id < 0:
                continue

            medoid_index = np.where(np.all(scaled_features == hdbscan.medoids_[cluster_id], axis=1))[0][0]

            cluster_indices = np.where(self.cluster_assignments == cluster_id)[0]
            cluster_exemplar = Exemplar(self.medoids_values[cluster_id], intervals[medoid_index])
            self.clusters.append(Cluster(cluster_id, cluster_indices, cluster_exemplar))

    def __iter__(self):
        yield from self.clusters
