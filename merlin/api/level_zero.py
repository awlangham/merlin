from itertools import combinations
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import HDBSCAN

from merlin.models import Exemplar, OnOffLoad


def level_zero(self, start_ts: int, end_ts: int):
    feature_names = ['PA_ss', 'QA_ss',
                     'PB_ss', 'QB_ss',
                     'PC_ss', 'QC_ss',
                     'PA_pk', 'QA_pk',
                     'PB_pk', 'QB_pk',
                     'PC_pk', 'QC_pk'
                     ]

    features, intervals = [], []
    for event in self.get_events(start_ts, end_ts):
        features.append([event.content[name] for name in feature_names])
        intervals.append((event.start_time, event.end_time))

    features = np.array(features)

    scaler = MinMaxScaler()
    scaled_features = scaler.fit_transform(features)

    hdbscan = HDBSCAN(min_cluster_size=25, store_centers='medoid', cluster_selection_epsilon=0.1).fit(scaled_features)

    cluster_assignments = hdbscan.labels_

    distinct_ids = list(set(cluster_assignments))
    exemplar_event_indices = []
    for cluster_id in distinct_ids:
        if cluster_id < 0:
            # Skip anything unlabeled
            continue

        # Find index of representative event for this cluster
        medoid_index = np.where(np.all(scaled_features == hdbscan.medoids_[cluster_id], axis=1))[0][0]
        exemplar_event_indices.append(medoid_index)

    # Load inference
    exemplars, loads = [], []

    def _best_matching_pair(cluster_list):
        if len(cluster_list) < 2:
            return False

        best_mean_sq_error = np.inf
        best_cluster1, best_cluster2 = None, None
        for cluster1, cluster2 in combinations(cluster_list, 2):
            ss_1, ss_2 = features[cluster1, :6], features[cluster2, :6]
            mean_sq_error = np.linalg.norm(ss_1 + ss_2)

            if mean_sq_error < best_mean_sq_error:
                best_mean_sq_error = mean_sq_error
                best_cluster1 = cluster1
                best_cluster2 = cluster2

        cluster_list.remove(best_cluster1)
        cluster_list.remove(best_cluster2)

        new_load_name = f'Load {len(loads) + 1}'

        # Figure out which exemplar is ON and which is OFF
        if np.sum(features[best_cluster1, (0, 2, 4)]) > np.sum(features[best_cluster2, (0, 2, 4)]):
            # best_cluster1 is ON, best_cluster2 is OFF
            on_start_ts = intervals[best_cluster1][0]
            on_end_ts = intervals[best_cluster1][1]

            off_start_ts = intervals[best_cluster2][0]
            off_end_ts = intervals[best_cluster2][1]

            on_ss = features[best_cluster1, :6]
            on_pk = features[best_cluster1, 6:]
        else:
            # best_cluster2 is ON, best_cluster1 is OFF
            on_start_ts = intervals[best_cluster2][0]
            on_end_ts = intervals[best_cluster2][1]

            off_start_ts = intervals[best_cluster1][0]
            off_end_ts = intervals[best_cluster1][1]

            on_ss = features[best_cluster2, :6]
            on_pk = features[best_cluster2, 6:]

        if (on_ss[1] + on_ss[3] + on_ss[5]) < 0.1 * (on_ss[0] + on_ss[2] + on_ss[4]):
            family = 'Resistive'
        elif (on_pk[0] + on_pk[2] + on_pk[4]) > 2 * (on_ss[0] + on_ss[2] + on_ss[4]):
            # TODO: Refactor this into some sort of classifier that's well documented
            family = 'Motor'
        else:
            family = None

        new_load = OnOffLoad(new_load_name, on_ss, family)
        loads.append(new_load)

        on_exemplar = Exemplar(on_start_ts, on_end_ts, [[new_load_name, 'OFF', 'ON']])
        off_exemplar = Exemplar(off_start_ts, off_end_ts, [[new_load_name, 'ON', 'OFF']])

        exemplars.append(on_exemplar)
        exemplars.append(off_exemplar)

        return True

    found_pair = _best_matching_pair(exemplar_event_indices)
    while found_pair:
        found_pair = _best_matching_pair(exemplar_event_indices)

    return exemplars, loads
