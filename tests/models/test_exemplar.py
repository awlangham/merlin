import pytest
from merlin.models import Exemplar


def test_exemplar_valid():
    e = Exemplar(start_ts=0, end_ts=10, transitions=["Load1::A->B"])
    assert e.start_ts == 0
    assert e.end_ts == 10
    assert e.transitions == ["Load1::A->B"]
    assert isinstance(e.to_json(), dict)
    assert "<merlin.models.Exemplar" in repr(e)


def test_exemplar_invalid_timestamps():
    with pytest.raises(ValueError):
        Exemplar(start_ts=10, end_ts=5, transitions=["Load1::A->B"])

    with pytest.raises(ValueError):
        Exemplar(start_ts=5, end_ts=5, transitions=["Load1::A->B"])


def test_exemplar_empty_transitions():
    with pytest.raises(ValueError):
        Exemplar(start_ts=0, end_ts=10, transitions=[])
