from click.testing import CliRunner
from merlin.cli.load import add


def test_add_invalid():
    result = CliRunner().invoke(add, [''])
    assert 'Load name cannot be empty' in result.output
    assert result.exit_code == 0
