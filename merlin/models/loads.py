import numpy as np

class GenericLoad:
    """
    Generic load class.
    """

    def __init__(self, name, states, family=None) -> None:
        if len(states) == 0:
            raise ValueError('Load states cannot be empty')
        
        if len(name) == 0:
            raise ValueError('Load name cannot be empty')

        self.name = name
        self.family = family
        self.states = states

    def to_json(self) -> dict:
        return {
            'family': self.family,
            'states': self.states
        }


class OnOffLoad(GenericLoad):
    """
    Simple two-state (OFF and ON) load class.
    """

    def __init__(self, name, on_ss: np.ndarray, family=None, num_phases=3) -> None:
        if num_phases not in (1, 3):
            raise ValueError('num_phases must be either 1 or 3')

        if num_phases == 3:
            states = {'OFF': [0, 0, 0, 0, 0, 0], 'ON': on_ss.tolist()}
        else:
            states = {'OFF': [0, 0], 'ON': on_ss.tolist()}
        super().__init__(name, states, family)

    def __repr__(self):
        ss_string = [round(s) for s in self.states['ON']]
        return f'<merlin.models.OnOffLoad name: {self.name} family: {self.family} on_ss: {ss_string} W>'
