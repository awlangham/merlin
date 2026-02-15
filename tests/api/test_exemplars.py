import pytest
from contextlib import contextmanager

from merlin.models import Exemplar
from merlin.api.exemplars import add_exemplar, remove_exemplar


class FakeInstallation:
    def __init__(self):
        self.config = {"exemplars": []}

    @contextmanager
    def modify_config(self):
        yield self.config


def test_add_exemplar():
    installation = FakeInstallation()

    e = Exemplar(0, 10, [["load1", "A", "B"]])
    add_exemplar(installation, e)

    assert installation.config['exemplars'] == [e.to_json()]


def test_remove_exemplar_valid():
    installation = FakeInstallation()

    e = Exemplar(0, 10, [["load1", "A", "B"]])
    add_exemplar(installation, e)

    remove_exemplar(installation, 1)

    assert len(installation.config['exemplars']) == 0

def test_remove_exemplar_invalid():
    installation = FakeInstallation()

    e = Exemplar(0, 10, [["load1", "A", "B"]])
    add_exemplar(installation, e)
    add_exemplar(installation, e)

    with pytest.raises(IndexError):
        remove_exemplar(installation, 3)

    with pytest.raises(IndexError):
        remove_exemplar(installation, 0)

    with pytest.raises(IndexError):
        remove_exemplar(installation, -1)