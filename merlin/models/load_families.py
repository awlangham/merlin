class BasicLoad:
    def __init__(self, name, on_ss, family=None) -> None:
        self.name = name
        self.family = family
        self.states = {'OFF': [0, 0], 'ON': on_ss.tolist()}

    def to_json(self):
        return {
            'family': self.family,
            'states': self.states
        }
