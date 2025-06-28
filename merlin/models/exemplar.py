class Exemplar:
    """
    Exemplar class for the transient signature of a load state change.
    """

    def __init__(self, start_ts: int, end_ts: int, transitions: list) -> None:
        self.start_ts = start_ts
        self.end_ts = end_ts
        self.transitions = transitions

    def to_json(self) -> dict:
        return {
            'start_ts': self.start_ts,
            'end_ts': self.end_ts,
            'transitions': self.transitions
        }

    def __repr__(self):
        return f'<merlin.models.Exemplar start_ts: {self.start_ts} end_ts: {self.end_ts} transitions: {self.transitions}>'
