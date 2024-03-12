from itertools import combinations
from fastapi import APIRouter, Request
import numpy as np
from sklearn.manifold import MDS

from nilmevents import get_connection
from nilmevents.utilities import trainola

router = APIRouter()


@router.post('/{event_set_name}/mds')
async def mds(event_set_name: str, request: Request):
    eventDB = get_connection(event_set_name)
    ids = (await request.json())['ids']

    mds_events = eventDB.get_multiple_transients(ids)
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

    return {
        'data0': transformed[:, 0].tolist(),
        'data1': transformed[:, 1].tolist()
    }
