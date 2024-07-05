import numpy as np

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
