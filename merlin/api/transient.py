import numpy as np
from joule.utilities import timestamp_to_human as ts2h


def load_transient_file(filename: str) -> list:
    """
    Helper function to open a npz transients file.
    """
    
    npz_data = np.load(filename)
    return [Transient(array) for array in npz_data.values()]


class Transient:
    """
    API transient class to simplify data parsing.
    """

    def __init__(self, array):
        self.timestamps = array[0]
        self.P = array[1]
        self.Q = array[2]

    def __len__(self):
        return len(self.timestamps)

    def __repr__(self):
        start_time = ts2h(self.timestamps[0]).strip()
        dP = round(self.P[-1] - self.P[0])
        dQ = round(self.Q[-1] - self.Q[0])
        return f'<merlin.api.Transient start_time: {start_time}, dP = {dP} W, dQ = {dQ} var>'
