import numpy as np
import json
from itertools import combinations, product
from contextlib import contextmanager
import asyncio

from merlin.api import config_filename
from merlin.utilities import trainola
from merlin.models import Exemplar


class Installation:
    def __init__(self, node=None) -> None:
        self.node = node

        with self.config() as cf:
            self.stream_name = cf['stream_name']

    @contextmanager
    def config(self):
        with open(config_filename, 'r') as config_file:
            config_json = json.load(config_file)

        try:
            yield config_json
        finally:
            with open(config_filename, 'w') as config_file:
                json.dump(config_json, config_file, indent=4)

    def get_events(self, start: int = None, end: int = None) -> list:
        """
        Return a list of all events in the specified stream.
        """

        return asyncio.run(self.node.event_stream_read_list(self.stream_name + '/events', start=start, end=end, limit=1000))

    def add_exemplar(self, exemplar: Exemplar) -> None:
        with self.config() as cf:
            cf['exemplars'].append(exemplar.to_json())

    async def load_exemplar(self, load_name: str, state1: str, state2: str):
        """
        Find the exemplar corresponding to
        the transition load_name::state1->state2
        """

        with self.config() as cf:
            exemplars = cf['exemplars']

        for exemplar in exemplars:
            if exemplar['transitions'] == [[load_name, state1, state2]]:
                return await self.get_transient(exemplar['start_ts'], exemplar['end_ts'])

    async def find_matching_exemplar(self, data, trainola_threshold: float = 0.1):
        """
        Returns the exemplar in the config file that best
        matches the provided transient, or None if no exemplar
        matches the transient below trainola_threshold.
        """

        best_score = np.inf
        matching_exemplar = None

        with self.config() as cf:
            exemplars = cf['exemplars']
            stream_name = cf['stream_name']

        for exemplar in exemplars:
            pipe = await self.node.data_read(stream_name + '/transients',
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

    async def combinatorial_match(self, P_ss: float, Q_ss: float):
        """
        Match the steady-state changes in real and reactive power
        to combinations of two loads in the configuration.
        """

        with self.config() as cf:
            load_names = list(cf['loads'].keys())

            best_error = np.inf
            best_loads, best_type = None, None

            for load1, load2 in combinations(load_names, 2):
                PA_ss_1, QA_ss_1, PB_ss_1, QB_ss_1, PC_ss_1, QC_ss_1 = cf['loads'][load1]['states']['ON']
                P_ss_1, Q_ss_1 = PA_ss_1 + PB_ss_1 + PC_ss_1, QA_ss_1 + QB_ss_1 + QC_ss_1

                PA_ss_2, QA_ss_2, PB_ss_2, QB_ss_2, PC_ss_2, QC_ss_2 = cf['loads'][load2]['states']['ON']
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

    async def get_transient(self, start_ts: int, end_ts: int):
        pipe = await self.node.data_read(self.stream_name + '/transients', start=start_ts, end=end_ts)
        sarray = await pipe.read_all(flatten=True)
        return sarray

    from merlin.api.level_zero import level_zero
    from merlin.api.level_one import level_one
    from merlin.api.level_two import level_two
    from merlin.api.level_three import level_three
