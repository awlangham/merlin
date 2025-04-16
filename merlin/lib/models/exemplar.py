class Exemplar:
    """
    Exemplar class for the transient signature of a load state change.
    """

    def __init__(self, features, ts_interval) -> None:
        self.features_ = features
        self.ts_interval_ = ts_interval
        self.steady_state_diff = features[:2]
        self.transitions = None
