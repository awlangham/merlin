class GenericLoad:
    """
    Generic load class.
    """

    def __init__(self, name, states, family=None) -> None:
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

    def __init__(self, name, on_ss, family=None) -> None:
        states = {'OFF': [0, 0], 'ON': on_ss.tolist()}
        super().__init__(name, states, family)
