import pytest
from merlin.api.learn_loads import learn_loads

class FakeInstallation:
    pass

def test_learn_loads_invalid():
    with pytest.raises(ValueError):
        learn_loads(FakeInstallation(), 20, 10)

    with pytest.raises(ValueError):
        learn_loads(FakeInstallation(), 20, 20)

    with pytest.raises(ValueError):
        learn_loads(FakeInstallation(), 10, 20, max_ss_error=-100)