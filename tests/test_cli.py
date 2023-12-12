from typer.testing import CliRunner

from score_simulator_py.cli import app

runner = CliRunner()


def test_play() -> None:
    result = runner.invoke(app, ["play"])
    assert result.exit_code == 0
    assert "hello" in result.stdout
