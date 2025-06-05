class Exemplar:
    """
    Exemplar class for the transient signature of a load state change.
    """

    def __init__(self):
        self.start_ts = None
        self.end_ts = None
        self.transitions = []

    def to_json(self) -> dict:
        return {
            'start_ts': self.start_ts,
            'end_ts': self.end_ts,
            'transitions': self.transitions
        }
