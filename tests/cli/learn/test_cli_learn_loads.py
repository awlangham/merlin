import pytest
from click.testing import CliRunner
from merlin.cli.learn import learn_loads


@pytest.mark.parametrize(
    "start,end",
    [
        ("abc", "def"),
        (10, 5),
        (10, 10)
    ])
def test_learn_loads_invalid(start, end):
    result = CliRunner().invoke(learn_loads, ['--start', start, '--end', end])
    assert 'Invalid start/end time.' in result.output
    assert result.exit_code == 0
