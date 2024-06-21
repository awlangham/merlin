from itertools import combinations
import numpy as np
from sklearn.manifold import MDS

from merlin.utilities import get_joule_node
from merlin.supervised.trainola import trainola

async def mds_data(node_name, stream_name, intervals):
    """
    Transform specified time-series data into a compressed 2-D
    space via multidimensional scaling and using trainola scores
    as the distance metric.
    """

    async with get_joule_node(node_name) as node:
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
