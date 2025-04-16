class Cluster:
    """
    Cluster class for a collection of transients with a representative exemplar.
    """

    def __init__(self, cluster_id, indices, exemplar) -> None:
        self.id_ = cluster_id
        self.indices_ = indices
        self.size_ = len(indices)
        self.exemplar = exemplar

    def __len__(self) -> int:
        return self.size_

    def to_json(self) -> dict:
        return {
            'start_ts': self.exemplar.ts_interval_[0],
            'end_ts': self.exemplar.ts_interval_[1],
            'transitions': self.exemplar.transitions
        }
