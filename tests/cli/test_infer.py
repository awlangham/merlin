import pytest
from click.testing import CliRunner
from merlin.cli import infer


@pytest.mark.parametrize(
    "start,end",
    [
        ("", ""),
        ("abc", "def"),
        ("", "2026-01-01"),
        ("2026-01-01", "")
    ])
def test_infer_invalid(start, end):
    result = CliRunner().invoke(infer, ['--start', start, '--end', end])
    assert 'Invalid start/end time.' in result.output
    assert result.exit_code == 0
