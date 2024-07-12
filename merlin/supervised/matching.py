import numpy as np
from itertools import combinations, product

from merlin.config import config_file
from merlin.supervised.trainola import trainola


async def find_matching_exemplar(P, Q, joule_node, transients_stream, trainola_threshold=0.15):
    """
    Returns the exemplar in the config file that best
    matches the provided transient, or None if no exemplar
    matches the transient below trainola_threshold.
    """

    with config_file() as config:
        best_score = np.inf
        matching_exemplar = None

        for exemplar in config['exemplars']:
            exemplar_sarray = await joule_node.data_read_array(transients_stream,
                                                               start=exemplar['start_ts'],
                                                               end=exemplar['end_ts'])
            exemplar_PQ = exemplar_sarray['data']
            exemplar_PQ -= np.mean(exemplar_PQ[:5], axis=0)

            detected_PQ = np.column_stack((P, Q))
            detected_PQ -= np.mean(detected_PQ[:5], axis=0)

            trainola_score = trainola(detected_PQ.T, exemplar_PQ.T)

            if trainola_score < best_score and trainola_score < trainola_threshold:
                best_score = trainola_score
                matching_exemplar = exemplar

        return matching_exemplar, best_score


async def combinatorial_match(P_ss, Q_ss):
    with config_file() as config:
        load_names = list(config['loads'].keys())

        best_error = np.inf
        best_loads, best_type = None, None

        for load1, load2 in combinations(load_names, 2):
            P_ss_1, Q_ss_1 = config['loads'][load1]['states']['ON']
            P_ss_2, Q_ss_2 = config['loads'][load2]['states']['ON']

            for a, b in product([1, -1], repeat=2):
                P_ss_combo = a * P_ss_1 + b * P_ss_2
                Q_ss_combo = a * Q_ss_1 + b * Q_ss_2

                error = (P_ss - P_ss_combo) ** 2 + (Q_ss - Q_ss_combo) ** 2
                error /= P_ss_combo ** 2 + Q_ss_combo ** 2
                if error < best_error:
                    best_error = error
                    best_loads = f'{load1},{load2}'

                    type1 = 'OFF to ON' if a == 1 else 'ON to OFF'
                    type2 = 'OFF to ON' if b == 1 else 'ON to OFF'

                    best_type = f'{type1},{type2}'

        if best_error < 0.1:
            return best_loads, best_type
        else:
            return None
