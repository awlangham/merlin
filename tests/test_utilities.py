import numpy as np
from merlin.utilities import trainola


def test_trainola_same():
    a = np.ones((1, 30))
    a[:, :15] = 0
    assert np.isclose(trainola(a, a), 0)

    a = np.ones((24, 30))
    a[:, :15] = 0
    assert np.isclose(trainola(a, a), 0)


def test_trainola_uncorrelated():
    a = np.ones((1, 30))
    a[:, :15] = 0
    b = np.zeros((1, 30))
    assert np.isclose(trainola(a, b), 1)

    a = np.ones((24, 30))
    a[:, :15] = 0
    b = np.zeros((24, 30))
    assert np.isclose(trainola(a, b), 1)
