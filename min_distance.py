import numpy as np
from numpy.linalg import norm
from numpy.lib.stride_tricks import sliding_window_view
import asyncio
from itertools import combinations
from sklearn.manifold import MDS
from joule.utilities import human_to_timestamp as h2ts
import matplotlib.pyplot as plt

from merlin.utilities import get_events, read_interval


def transverse_distance(a, b):
    a = (a.T - np.mean(a[:, :5], axis=1)).T
    b = (b.T - np.mean(b[:, :5], axis=1)).T

    long_array, short_array = (a, b) if a.shape[1] > b.shape[1] else (b, a)
    long_array_slices = sliding_window_view(long_array, short_array.shape)[0]
    # distances = [norm(long_array_slice - short_array) / max(norm(long_array_slice), norm(short_array)) for long_array_slice in long_array_slices]

    distances = []
    for long_array_slice in long_array_slices:
        # print(np.max(np.abs(long_array_slice - short_array)))
        # print(norm(long_array_slice), norm(short_array), norm(long_array_slice - short_array))
        # plt.plot(long_array_slice.T)
        # plt.plot(short_array.T)
        # plt.figure()
        # plt.plot(long_array_slice.T - short_array.T)
        # plt.show()
        distances.append(norm(long_array_slice - short_array) / min(norm(long_array_slice), norm(short_array)))
        # print(distances[-1])
    return min(distances)

if __name__ == '__main__':
    node_name = 'nilm-dev'
    dataset_name = '/USCG Sturgeon/Port'
    events = get_events(node_name, dataset_name)
    # event1 = get_events('nilm-dev', '/sparcs/39BayStateRd', start=99629766666, end=99630283333)
    # event2 = get_events('nilm-dev', '/sparcs/39BayStateRd', start=114959766666, end=114960283333)
    # events = event1 + event2
    # print(events)

    transients = []
    for event in events:
        print(event)
        transient = asyncio.run(read_interval(node_name, dataset_name, event.start_time, event.end_time))
        transients.append(transient.T)


    num_events = len(transients)
    distance_matrix = np.zeros((num_events, num_events))

    for t1, t2 in combinations(range(num_events), 2):
        pair_distance = transverse_distance(transients[t1][1:], transients[t2][1:])
        distance_matrix[t1, t2] = pair_distance
        distance_matrix[t2, t1] = pair_distance

    print(distance_matrix)

    transformed = MDS(dissimilarity='precomputed', normalized_stress='auto').fit_transform(distance_matrix)

    plt.scatter(transformed[:, 0], transformed[:, 1], alpha=0.3)
    plt.show()