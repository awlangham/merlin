from itertools import combinations
import numpy as np
from sklearn.manifold import MDS

from merlin.lib.transients import read_multiple_transients
from merlin.lib.inference.trainola import trainola


def mds_data(node_name: str, stream_name: str, intervals: list[tuple[int, int]]) -> np.array:
    """
    Transform specified time-series data into a compressed 2-D
    space via multidimensional scaling and using trainola scores
    as the distance metric.
    """

    mds_events = read_multiple_transients(node_name, stream_name, intervals)

    num_events = len(mds_events)
    trainola_distances = np.zeros((num_events, num_events))

    for t1, t2 in combinations(range(num_events), 2):
        pair_distance = trainola(mds_events[t1][1:], mds_events[t2][1:])
        trainola_distances[t1, t2] = pair_distance
        trainola_distances[t2, t1] = pair_distance

    # transformed = UMAP(metric='precomputed', min_dist=0, n_neighbors=4).fit_transform(trainola_distances)

    transformed = MDS(dissimilarity='precomputed', normalized_stress='auto').fit_transform(trainola_distances)
    # embedding_distances = cdist(transformed, transformed)
    # error_matrix = embedding_distances - trainola_distances
    # print(f'RMSE: {np.sqrt(np.mean(error_matrix ** 2))}')

    return transformed
