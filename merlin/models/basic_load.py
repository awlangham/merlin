class BasicLoad:
    def __init__(self, name, on_ss) -> None:
        self.name = name
        self.states = {'OFF': [0, 0], 'ON': on_ss.tolist()}

    def to_json(self):
        return {
            'states': self.states
        }
