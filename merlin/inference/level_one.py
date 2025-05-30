import json
from itertools import permutations
import numpy as np

from merlin.installation import config_filename
from merlin.utilities import get_events

def level_one(node_name, dataset, start, end):
    """
    Given a configuration file with loads filled in,
    identify exemplars that correspond with state changes.
    """
    
    with open(config_filename, 'r') as f:
        config_json = json.load(f)

    config_json['exemplars'] = []
    
    events = get_events(node_name, dataset, start, end)
    
    for load in config_json['loads'].keys():
        states = config_json['loads'][load]['states']
        
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
            
            print(best_event_match.content['type'], best_event_match.content['label'])

        print('---')