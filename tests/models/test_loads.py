import pytest
import numpy as np
from merlin.models import GenericLoad, OnOffLoad


def test_generic_load_valid():
    states = {'OFF': [0, 0, 0, 0, 0, 0], 'ON': [1, 1, 1, 1, 1, 1]}
    load = GenericLoad(name="load1", states=states, family="Resistive")

    assert load.name == "load1"
    assert load.family == "Resistive"
    assert load.states == states


def test_generic_load_invalid():
    with pytest.raises(ValueError):
        GenericLoad(name="load1", states={}, family="Resistive")

    valid_states = {'OFF': [0, 0, 0, 0, 0, 0], 'ON': [1, 1, 1, 1, 1, 1]}
    with pytest.raises(ValueError):
        GenericLoad(name="", states=valid_states, family="Resistive")


def test_generic_load_to_json():
    states = {'OFF': [0, 0, 0, 0, 0, 0], 'ON': [1, 1, 1, 1, 1, 1]}
    load = GenericLoad(name="load1", states=states, family=None)

    expected_json = {
        "family": None,
        "states": {'OFF': [0, 0, 0, 0, 0, 0], 'ON': [1, 1, 1, 1, 1, 1]},
    }

    assert load.to_json() == expected_json


def test_on_off_load_valid():
    on_ss = np.array([1, 1, 1, 1, 1, 1])
    load = OnOffLoad(name="load1", on_ss=on_ss,
                     family="Resistive", num_phases=3)

    assert load.name == "load1"
    assert load.family == "Resistive"
    assert load.states == {'OFF': [0, 0, 0, 0, 0, 0], 'ON': [1, 1, 1, 1, 1, 1]}


def test_on_off_load_invalid():
    with pytest.raises(ValueError):
        OnOffLoad(name="load1", on_ss=np.array([1, 1, 1, 1]), family=None, num_phases=2)

    with pytest.raises(ValueError):
        OnOffLoad(name="", on_ss=np.array([1, 1]), family=None, num_phases=1)


def test_on_off_load_repr_rounds_correctly():
    on_ss = np.array([10.1, 20.7, 30.4, 40.9, 50.2, 60.6])
    load = OnOffLoad(name="load1", on_ss=on_ss, family="Machine", num_phases=3)

    expected_repr = "<merlin.models.OnOffLoad name: load1 family: Machine on_ss: [10, 21, 30, 41, 50, 61] W>"
    assert repr(load) == expected_repr
