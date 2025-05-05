from itertools import combinations
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import HDBSCAN

from merlin.utilities import get_events
from merlin.models import Exemplar, Cluster, OnOffLoad


def level_zero(node_name, dataset, start, end):
    feature_names = ['P_ss', 'Q_ss', 'P_pk', 'Q_pk']

    features, intervals = [], []
    for event in get_events(node_name, dataset, start, end):
        features.append([event.content[name] for name in feature_names])
        intervals.append((event.start_time, event.end_time))

    features = np.array(features)

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)

    hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid').fit(scaled_features)

    cluster_assignments = hdbscan.labels_
    medoids_values = scaler.inverse_transform(hdbscan.medoids_)

    distinct_ids = list(set(cluster_assignments))
    clusters = []
    for cluster_id in distinct_ids:
        if cluster_id < 0:
            continue

        medoid_index = np.where(np.all(scaled_features == hdbscan.medoids_[cluster_id], axis=1))[0][0]

        cluster_indices = np.where(cluster_assignments == cluster_id)[0]
        cluster_exemplar = Exemplar(medoids_values[cluster_id], intervals[medoid_index])
        clusters.append(Cluster(cluster_id, cluster_indices, cluster_exemplar))

    # Load inference
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

    cluster_list_copy = clusters.copy()
    found_pair = _best_matching_pair(cluster_list_copy)
    while found_pair:
        found_pair = _best_matching_pair(cluster_list_copy)

    return clusters, loads
