class Exemplar:
    """
    Exemplar class for the transient signature of a load state change.
    """

    def __init__(self, start_ts: int, end_ts: int, transitions: list) -> None:
        if start_ts >= end_ts:
            raise ValueError(f'Exemplar start time must be less than end time: ({start_ts}, {end_ts})')

        if len(transitions) == 0:
            raise ValueError(f'Exemplar transitions cannot be empty')

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
