import numpy as np
from sklearn.cluster import HDBSCAN
from sklearn.preprocessing import MinMaxScaler
from itertools import combinations

from merlin.lib.events import read_events
from merlin.models import Exemplar, Cluster, OnOffLoad


class Clustering:
    """
    Abstraction of a collection of clusters in a Merlin dataset.

    The HDBSCAN clustering procedure is run upon class construction.

    Load inference is performed with Clustering.infer_loads().
    """

    def _get_events(self, node_name, event_stream_name, start = None, end = None):
        return read_events(node_name, event_stream_name, start, end)

    def __init__(self, node_name, event_stream_name, start = None, end = None) -> None:
        # TODO: handle case where there are no events

        feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']

        features, intervals = [], []
        for event in self._get_events(node_name, event_stream_name, start, end):
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

    def infer_loads(self):
        loads = []

        def _best_matching_pair(cluster_list):
            if len(cluster_list) < 2:
                return False

            best_mean_sq_error = np.inf
            best_cluster1, best_cluster2 = None, None
            for cluster1, cluster2 in combinations(cluster_list, 2):
                mean_sq_error = np.linalg.norm(cluster1.exemplar.steady_state_diff + cluster2.exemplar.steady_state_diff)

                if mean_sq_error < best_mean_sq_error:
                    best_mean_sq_error = mean_sq_error
                    best_cluster1 = cluster1
                    best_cluster2 = cluster2

            cluster_list.remove(best_cluster1)
            cluster_list.remove(best_cluster2)

            new_load_name = f'Load {len(loads)}'

            # Figure out which exemplar is ON and which is OFF
            on_exemplar, off_exemplar = (best_cluster1.exemplar, best_cluster2.exemplar) if best_cluster1.exemplar.features_[
                0] > best_cluster2.exemplar.features_[0] else (best_cluster2.exemplar, best_cluster1.exemplar)
            on_exemplar.transitions = [[new_load_name, 'OFF', 'ON']]
            off_exemplar.transitions = [[new_load_name, 'ON', 'OFF']]

            if on_exemplar.features_[1] < 500:
                family = 'Resistive'
            elif on_exemplar.features_[2] > 2 * on_exemplar.features_[0]:
                # TODO: Refactor this into some sort of classifier that's well documented
                family = 'Motor'
            else:
                family = None

            new_load = OnOffLoad(new_load_name, on_exemplar.features_[:2], family)
            loads.append(new_load)

            return True

        cluster_list_copy = self.clusters.copy()
        found_pair = _best_matching_pair(cluster_list_copy)
        while found_pair:
            found_pair = _best_matching_pair(cluster_list_copy)

        return loads
