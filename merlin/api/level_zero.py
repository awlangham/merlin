from itertools import combinations
import numpy as np
from sklearn.cluster import HDBSCAN
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from merlin.models import Exemplar, OnOffLoad
from merlin.utilities import trainola


async def level_zero(self, start_ts: int, end_ts: int, max_ss_error=500):
    feature_names = ['PA_ss', 'QA_ss',
                     'PB_ss', 'QB_ss',
                     'PC_ss', 'QC_ss',
                     'PA_pk', 'QA_pk',
                     'PB_pk', 'QB_pk',
                     'PC_pk', 'QC_pk'
                     ]

    transient_pipe = await self.node.data_read(self.stream_name + '/transients', start=start_ts, end=end_ts)
    transient_data = await transient_pipe.read_all(flatten=True, error_on_overflow=True, maxrows=10000000)

    features, intervals, transients = [], [], []
    events = await self.node.event_stream_read_list(self.stream_name + '/events', start=start_ts, end=end_ts, limit=5000)
    for event in events:
        features.append([event.content[name] for name in feature_names])
        intervals.append((event.start_time, event.end_time))

        start_idx = np.searchsorted(transient_data[:, 0], event.start_time)
        end_idx = np.searchsorted(transient_data[:, 0], event.end_time) + 1

        transients.append(transient_data[start_idx:end_idx].T)

    features = np.array(features)
    print(f'Processing {len(transients)} events...')

    num_events = len(transients)
    distance_matrix = np.zeros((num_events, num_events))

    for t1, t2 in combinations(range(num_events), 2):
        pair_distance = trainola(transients[t1][1:], transients[t2][1:])
        distance_matrix[t1, t2] = pair_distance
        distance_matrix[t2, t1] = pair_distance

    hdbscan = HDBSCAN(min_cluster_size=5, metric='precomputed', cluster_selection_epsilon=0.01).fit(distance_matrix)

    cluster_assignments = hdbscan.labels_

    distinct_ids = list(set(cluster_assignments))
    exemplar_event_indices = []
    for cluster_id in distinct_ids:
        if cluster_id < 0:
            # Skip anything unlabeled
            continue

        this_cluster_indices = np.where(cluster_assignments == cluster_id)[0]
        this_cluster_pair_distances = distance_matrix[this_cluster_indices][:, this_cluster_indices]
        medoid_index = this_cluster_indices[np.argmin(np.sum(this_cluster_pair_distances, axis=0))]

        # Find index of representative event for this cluster
        exemplar_event_indices.append(medoid_index)

    # Load inference
    exemplars, loads = [], []

    load_indices = np.zeros(len(hdbscan.labels_))
    load_index = 1

    def _best_matching_pair(cluster_list):
        nonlocal load_index

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

        ss_error = features[best_cluster1, :6] + features[best_cluster2, :6]
        if np.any(np.abs(ss_error) > max_ss_error):
            return False

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

        load_indices[np.where(hdbscan.labels_ == hdbscan.labels_[best_cluster1])] = load_index
        load_indices[np.where(hdbscan.labels_ == hdbscan.labels_[best_cluster2])] = load_index

        load_index += 1

        on_exemplar = Exemplar(on_start_ts, on_end_ts, [[new_load_name, 'OFF', 'ON']])
        off_exemplar = Exemplar(off_start_ts, off_end_ts, [[new_load_name, 'ON', 'OFF']])

        exemplars.append(on_exemplar)
        exemplars.append(off_exemplar)

        return True

    exemplar_event_indices_backup = exemplar_event_indices.copy()

    found_pair = _best_matching_pair(exemplar_event_indices)
    while found_pair:
        found_pair = _best_matching_pair(exemplar_event_indices)

    plt.figure(tight_layout=True)
    tab10 = plt.get_cmap('tab10')
    colors = [(0, 0, 0, 1)] + [tab10(i) for i in range(10)]
    custom_cmap = ListedColormap(colors)
    plt.scatter(features[:, 0] + features[:, 2] + features[:, 4], features[:, 1] + features[:, 3] + features[:, 5], c=load_indices, cmap=custom_cmap, s=100, alpha=0.5)
    for exemplar_event_index in exemplar_event_indices_backup:
        plt.scatter(features[exemplar_event_index, 0] + features[exemplar_event_index, 2] + features[exemplar_event_index, 4],
                    features[exemplar_event_index, 1] + features[exemplar_event_index, 3] + features[exemplar_event_index, 5], marker='x', color='red')
    plt.xlabel('Total Steady-State P')
    plt.ylabel('Total Steady-State Q')
    plt.grid()
    plt.show()

    return exemplars, loads
