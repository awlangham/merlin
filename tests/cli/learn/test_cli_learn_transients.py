import pytest
from click.testing import CliRunner
from merlin.cli.learn import learn_transients


@pytest.mark.parametrize(
    "start,end",
    [
        ("abc", "def"),
        (10, 5),
        (10, 10)
    ])
def test_learn_transients_invalid(start, end):
    result = CliRunner().invoke(learn_transients, ['--start', start, '--end', end, '/test1/test', '-l', '300'], obj={'NODE': 'test_node'})
    assert 'Invalid start/end time.' in result.output
    assert result.exit_code == 0
