import numpy as np
import json
from importlib.resources import files
from itertools import combinations, product

import merlin
from merlin.supervised.trainola import trainola

config_filename = str(files(merlin) / 'config.json')


# TO DO: Change to get_current_installation() and Installation class
class CurrentInstallation:
    def __init__(self, node) -> None:
        """
        Read JSON configuration and construct installation object.
        """

        with open(config_filename, 'r') as config_file:
            self.config_json = json.load(config_file)

        self.node = node

    def add_exemplar(self, exemplar) -> None:
        self.config_json['exemplars'].append(exemplar.to_json())

        with open(config_filename, 'w') as f:
            json.dump(self.config_json, f, indent=4)

    def get_load_names(self) -> list:
        """
        Return a list of all loads on this installation.
        """

        return list(self.config_json['loads'].keys())

    async def load_exemplar(self, load_name, state1, state2):
        """
        Find the exemplar corresponding to
        the transition load_name::state1->state2
        """

        exemplars = self.config_json['exemplars']
        stream_name = self.config_json['stream_name']

        for exemplar in exemplars:
            if exemplar['transitions'] == [[load_name, state1, state2]]:
                return await self.node.data_read_array(stream_name + '/transients', start=exemplar['start_ts'], end=exemplar['end_ts'], flatten=True)

    async def find_matching_exemplar(self, data, trainola_threshold=0.1):
        """
        Returns the exemplar in the config file that best
        matches the provided transient, or None if no exemplar
        matches the transient below trainola_threshold.
        """

        best_score = np.inf
        matching_exemplar = None

        for exemplar in self.config_json['exemplars']:
            pipe = await self.node.data_read(self.config_json['stream_name'] + '/transients',
                                             start=exemplar['start_ts'],
                                             end=exemplar['end_ts'])
            exemplar_sarray = await pipe.read_all()
            exemplar_PQ = exemplar_sarray['data']
            exemplar_PQ -= np.mean(exemplar_PQ[:5], axis=0)

            observed_data = data - np.mean(data[:5], axis=0)

            trainola_score = trainola(observed_data.T, exemplar_PQ.T)

            if trainola_score < best_score and trainola_score < trainola_threshold:
                best_score = trainola_score
                matching_exemplar = exemplar

        return matching_exemplar, best_score

    async def combinatorial_match(self, P_ss, Q_ss):
        """
        Match the steady-state changes in real and reactive power
        to combinations of two loads in the configuration.
        """

        load_names = list(self.config_json['loads'].keys())

        best_error = np.inf
        best_loads, best_type = None, None

        for load1, load2 in combinations(load_names, 2):
            PA_ss_1, QA_ss_1, PB_ss_1, QB_ss_1, PC_ss_1, QC_ss_1 = self.config_json['loads'][load1]['states']['ON']
            P_ss_1, Q_ss_1 = PA_ss_1 + PB_ss_1 + PC_ss_1, QA_ss_1 + QB_ss_1 + QC_ss_1

            PA_ss_2, QA_ss_2, PB_ss_2, QB_ss_2, PC_ss_2, QC_ss_2 = self.config_json['loads'][load2]['states']['ON']
            P_ss_2, Q_ss_2 = PA_ss_2 + PB_ss_2 + PC_ss_2, QA_ss_2 + QB_ss_2 + QC_ss_2

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
