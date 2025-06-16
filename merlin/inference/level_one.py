import json
from itertools import permutations
import numpy as np

from merlin.installation import CurrentInstallation
from merlin.utilities import get_events
from merlin.models import Exemplar


def level_one(node_name, dataset, start, end):
    """
    Given a configuration file with loads filled in,
    identify exemplars that correspond with state changes.
    """

    with CurrentInstallation().config() as cf:
        cf['exemplars'] = []

        events = get_events(node_name, dataset, start, end)

        exemplars = []
        for load in cf['loads'].keys():
            states = cf['loads'][load]['states']

            for state1, state2 in permutations(states.keys(), 2):
                print(f'Searching for {load}::{state1}->{state2}')

                target_ss_diff = np.array(states[state2]) - np.array(states[state1])

                best_event_match = None
                best_sse = np.inf
                for event in events:
                    PA_ss = event.content['PA_ss']
                    QA_ss = event.content['QA_ss']
                    PB_ss = event.content['PB_ss']
                    QB_ss = event.content['QB_ss']
                    PC_ss = event.content['PC_ss']
                    QC_ss = event.content['QC_ss']

                    observed_ss_diff = np.array([PA_ss, QA_ss, PB_ss, QB_ss, PC_ss, QC_ss])

                    sse = np.sum((observed_ss_diff - target_ss_diff) ** 2)

                    if sse < best_sse:
                        best_sse = sse
                        best_event_match = event

                # Create exemplar for best match
                new_exemplar = Exemplar()
                new_exemplar.start_ts = best_event_match.start_time
                new_exemplar.end_ts = best_event_match.end_time
                new_exemplar.transitions.append([load, state1, state2])
                exemplars.append(new_exemplar)

    return exemplars
